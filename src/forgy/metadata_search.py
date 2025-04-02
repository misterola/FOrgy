"""
The metadata_search module contains functions to get
book metadata from Google BooksAPI and OpenlibraryAPI.
"""
# import sys
# sys.path.append(r'C:\Users\Ola\Desktop\Projects\Forgy\src')
import json
import os
import re
from datetime import datetime
from pathlib import Path
import time

import requests
from dotenv import load_dotenv

from .database import get_database_columns
from .isbn_regex import is_valid_isbn
from .filesystem_utils import (
    count_files_in_directory,
    move_file_or_directory,
)

from .logger import create_logger


logger = create_logger('metadata_search')
logger.info('logger created successfully')

headers={  # noqa: E225
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\
 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

# Load BookAPI key from .env file
load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')
logger.info("Google API key added")


def merge_list_items(given_list):
    """Convert elements in a list into a single string of the
    list of values neatly separated by a comma.

    Function format the authors field in json metadata which may be
    a list containing author names.

    Note: function may be modified to include 'et. al.' where
    the number of authors is more than three.
    """
    if isinstance(given_list, list):
        appended_values = ", ".join(given_list)
        return appended_values
    else:
        logger.info(
            f"{given_list} is of type {type(given_list)}, not list"
        )
        pass


def get_cover_url_google(dictionary):
    """Function to get book cover thumbnail (medium-sized)
        from googlebooks api.

    ImageLinks come with returned json_metadata

    The format of imageLinks dictionary retrieved from google:

    "imageLinks": {
          "smallThumbnail": "http://books.google.com/...",
          "thumbnail": "http://books.google.com/..."
    }
    Note: Indexing the ImageLinks from returned metadata:
    json_metadata["items"][0]["volumeInfo"]["imageLinks"]
    """
    if "thumbnail" in dictionary.copy().keys():
        cover_url = dictionary["thumbnail"]
    elif "smallThumbnail" in dictionary.copy().keys():
        cover_url = dictionary["smallThumbnail"]
    else:
        cover_url = "NA"

    return cover_url


def get_cover_url_openlibrary(cover_id, isbn):
    """Funtion to get cover image from openlibrary api.

    The api may return cover_id or not (doesn't in most cases).
    The cover_id can be converted into the cover_url from covers
    API. In the absence of cover_id, the Cover API is queried
    using book's ISBN

    Cover API documentation can be found here:
    https://openlibrary.org/dev/docs/api/covers
    Rate-limit for openlib = 100 covers per 5 minutes per user IP

    Note: May modify function later to include thumbnail-size param
    """
    if cover_id != "NA":
        image_link = (
            'https://covers.openlibrary.org/b/id/' + cover_id + '-M.jpg'
        )
    else:
        image_link = (
            'https://covers.openlibrary.org/b/isbn/' + isbn + '-M.jpg'
        )

    return image_link


def get_image_url_google(
    isbn_of_book=None,
    headers=headers,
    title_of_book=None
):
    """Function to get imageLinks for a book from Google BooksAPI using
        Book ISBN or title.

    Function filters out just the imageLinks dictionary from JSON metadata.
    """
    # initialize dictionary containing imageLinks key
    # This is same key of imageLinks url in json from api source
    dict_of_interest = {
        "imageLinks": ""
    }

    if isbn_of_book:
        metadata_dict = google_metadata_dict(isbn=isbn_of_book)
    elif title_of_book:
        metadata_dict = google_metadata_dict(title=title_of_book)
    else:
        logger.warning("Please provide a valid book identifier")

    # Populate dict_of_interest with metadata value with key imageLinks
    available_metadata = metadata_handler(dict_of_interest, metadata_dict)
    dict_of_interest = get_dictionary(available_metadata)

    if len(dict_of_interest) == 0:
        return None
    else:
        pass

    image_link = dict_of_interest.get("imageLinks", "NA")

    return image_link


def metadata_handler(dict_of_interest, metadata_dict):
    """Function to extract keys and values of interest from API's
        JSON metadata_dict into FOrgy's dict_of_interest.

    metadata_dict: a dictionary extracted from JSON API metadata
                    which contains all metadata values present in
                    JSON data returned by API call. Extracting
                    metadata_dict is different for each API. It's
                    much simpler for openlibrary.
                    For Openlibrary API, metadata_dict:
                        json_metadata
                    For Google BooksAPI, metadata_dict:
                        json_metadata["items"][0]["volumeInfo"]


    dict_of_interest: a dictionary with keys matching keys of data
                      to be extracted from API's JSON metadata and
                      values intialized to empty strings. The keys
                      are also different for each API.
                      The dict_of_interest is populated with available
                      values whose keys match those in API.

    Function handles metadata_dict keys and values of different types,
    including missing keys and values of type str, list, dict and
    extracts them accordingly. If key in defined empty-valued dict_of_interest
    also exist in metadata_dict from api (this means data is available).
    This data is carefully extracted by this function.
    """
    logger.info(
        f"dict_of_interest: {dict_of_interest}"
    )
    logger.info(
        f"metadata_dict: {metadata_dict}"
    )

    for key in dict_of_interest.keys():
        if key in metadata_dict.keys():
            # CASE 1:
            # If retrieved value from metadata_dict is a list containing a
            # single element, extract that element using its index, zero,
            # and update the defined empty_valued (dict_of_interest)
            # dictionary with it.
            if (
                isinstance(metadata_dict[key], list)
                and len(metadata_dict[key]) == 1
            ):
                try:
                    dict_of_interest[key] = (
                        dict_of_interest[key]
                        + metadata_dict[key][0]
                    )
                except TypeError:
                    # TypeError can be encountered in the case of cover_id
                    # in Openlibrary API which is a list containing one integer
                    # Type conversion becomes necessary in this case
                    logger.exception(
                        f"{metadata_dict[key][0]} is a {type(metadata_dict[key][0])}"
                    )
                    dict_of_interest[key] = (
                        dict_of_interest[key]
                        + str(metadata_dict[key][0])
                    )

            # CASE 2:
            # If value in retrieved dict is a list containing more than one
            # str elements, extract that element by merging joining listed
            # items on a comma(','). Update dict_of_interest accordingly
            elif (
                isinstance(metadata_dict[key], list)
                and len(metadata_dict[key]) > 1
            ):
                dict_of_interest[key] = (
                    dict_of_interest[key]
                    + merge_list_items(metadata_dict[key])
                )

            # CASE: 3
            # If a dictionary is returned (containing two elements like the
            # case of book thumbnail urls in googleapi), get_cover_url function
            # is used to fetch medium thumbnail 'thumbnail' and if not available
            # a small thumbnail is used. If value is not available, it defaults
            # to "NA"
            elif (
                isinstance(metadata_dict[key], dict)
                and len(metadata_dict[key]) >= 1
            ):
                dict_of_interest[key] = get_cover_url_google(metadata_dict[key])

            # CASE 4:
            else:
                # If value in retrieved metadata_dict is a single value (str or int),
                # simply save the value to dict_of_interest using matching key from
                # metadata_dict
                dict_of_interest[key] = metadata_dict[key]
        else:
            # If key in dict_of_interest is not in API returned_metadata_dict,
            # assign it a value "NA".
            dict_of_interest[key] = "NA"

    return dict_of_interest


def get_subtitle_full_title(metadata_dict, dict_of_interest):
    """Function to get books's subtitle, and full_title
        from metadata_dict and save to dict_of_interest.

    This is needed to handle the inconsistencies in data returned
    by API. Some may contain title but not subtitle, and some may
    contain full title and no title or subtitle.
    """
    if (
        "title" in metadata_dict.keys()
        and "subtitle" not in metadata_dict.keys()
    ):
        subtitle = "NA"
        full_title = dict_of_interest["title"]

    elif (
        "title" in metadata_dict.keys()
        and "subtitle" in metadata_dict.keys()
    ):
        subtitle = dict_of_interest["subtitle"]
        full_title = (
            dict_of_interest["title"]
            + ": "
            + dict_of_interest["subtitle"]
        )
    else:
        subtitle = "NA"
        full_title = "NA"
    return full_title, subtitle


def get_isbns_google(metadata_dict):  # noqa: C901
    """Function to get isbn10 and isbn13 from metadata_dict from
        Google BooksAPI.
    Function returns 'NA' if isbn value is not available. The ISBN
    result from metadata_dict is a list of two dictionaries with each
    dict having two key:value pairs representing ISBN_10 and ISBN_13.
    (e.g. [{'type':ISBN_10, 'identifier':'2382932220'},
        {'type': ISBN_13, 'identifier':'9784525242123'}])
    """
    if "industryIdentifiers" in metadata_dict.keys():
        # If index 0 in list is for ISBN_10 dictionary and index1 in list
        # is for ISBN_13 dictionary
        if (
            metadata_dict["industryIdentifiers"][0]["type"] == "ISBN_10"
            and ("ISBN_10" in metadata_dict["industryIdentifiers"][0].values())
            and metadata_dict["industryIdentifiers"][1]["type"] == "ISBN_13"
            and ("ISBN_13" in metadata_dict["industryIdentifiers"][1].values())
        ):
            try:
                isbn_10 = metadata_dict["industryIdentifiers"][0]["identifier"]
            except (UnboundLocalError, IndexError):
                isbn_10 = "NA"
            try:
                isbn_13 = metadata_dict["industryIdentifiers"][1]["identifier"]
            except (UnboundLocalError, IndexError):
                isbn_13 = "NA"

        # If index 0 in list is for ISBN_13 dictionary and index1 in list
        # is for ISBN_10 dictionary
        elif (
            metadata_dict["industryIdentifiers"][0]["type"] == "ISBN_13"
            and ("ISBN_13" in metadata_dict["industryIdentifiers"][0].values())
            and metadata_dict["industryIdentifiers"][1]["type"] == "ISBN_10"
            and ("ISBN_10" in metadata_dict["industryIdentifiers"][1].values())
        ):
            try:
                isbn_13 = metadata_dict["industryIdentifiers"][0]["identifier"]
            except (UnboundLocalError, IndexError):
                isbn_13 = "NA"
            try:
                isbn_10 = metadata_dict["industryIdentifiers"][1]["identifier"]
            except (UnboundLocalError, IndexError):
                isbn_10 = "NA"
        else:
            # metadata_dict["industryIdentifiers"][0]["type"]== "OTHER"
            # and len(metadata_dict["industryIdentifiers"]==1)
            # to handle cases like this:'industryIdentifiers':
            # [{'type': 'OTHER', 'identifier': 'UOM:39015058578744'}]
            isbn_10 = "NA"
            isbn_13 = "NA"
    else:
        # if error is returned by database or metadata retrieve unsuccessful
        isbn_10 = "NA"
        isbn_13 = "NA"
    return isbn_10, isbn_13


def get_isbns_openlibrary(metadata_dict):
    """Fetches ISBNS from openlibrary sourced
    metadata"""
    if "isbn_10" in metadata_dict.keys():
        isbn_10 = metadata_dict["isbn_10"][0]
    else:
        isbn_10 = "NA"

    if "isbn_13" in metadata_dict.keys():
        isbn_13 = metadata_dict["isbn_13"][0]
    else:
        isbn_13 = "NA"
    return isbn_10, isbn_13


def get_file_size(file_path):
    """Function to get file size in MB.

    File_size in bytes (obtained from st_size
    is converted into MB by dividing by 1024**2.
    """
    file_stats = os.stat(file_path)
    file_size_bytes = file_stats.st_size
    file_size_MB = file_size_bytes / (1024 * 1024)
    return f"{file_size_MB:.2f}"


def get_google_metadata_json(API_KEY, isbn=None, title=None):  # noqa: C901
    """Function to fetch raw metadata from Google Books API"""
    if isbn:
        googleapi_metadata = (
            "https://www.googleapis.com/books/v1/volumes?q=isbn:"
            + isbn
            + "&key="
            + API_KEY
        )
    else:
        googleapi_metadata = (
            "https://www.googleapis.com/books/v1/volumes?q=intitle:"
            + title
            + "&key="
            + API_KEY
        )
    try:
        response = requests.get(
            googleapi_metadata,
            headers=headers,
            timeout=60
        )
        response.raise_for_status()
        logger.info(f"Status code: {response.status_code}")
        json_metadata = json.loads(response.text)
        return json_metadata
    except requests.exceptions.HTTPError as e:
        logger.exception(f"Request HTTP error occurred: {e}")
        return
    except requests.exceptions.RequestException as e:
        logger.exception(f"Request error occurred: {e}")
        return

    except requests.exceptions.ConnectTimeout:
        logger.exception("Request ConnectTimeoutError")
        return
    except requests.exceptions.ConnectionError:
        logger.exception(
            "Request ConnectionError. Check your internet connection",
            end="\n",
        )
        return
    except requests.ReadTimeout:  # noqa: F821
        logger.exception("ReadTimeoutError")
        return
    except ConnectionError:
        logger.exception("Connection Error")
        return
    except TimeoutError:
        logger.exception("Timeout Error")
        return
    except Exception as e:
        logger.exception(f"An unexpected error occured: {e}")
        return


# For use in main script
def get_openlibrary_metadata_json(isbn):
    """Function to fetch raw metadata from Google Books API"""

    try:
        olibapi_metadata = (
            "https://openlibrary.org/isbn/"
            + isbn
            + ".json"
        )
        response = requests.get(
                        olibapi_metadata,
                        headers=headers,
                        timeout=60
                    )
        response.raise_for_status()
        logger.info(f"Status code: {response.status_code}")
        json_metadata = json.loads(response.text)
        return json_metadata
    except requests.exceptions.HTTPError as e:
        logger.exception(f"Request HTTP error occurred: {e}")
        return
    except requests.exceptions.RequestException as e:
        logger.exception(f"Request error occurred: {e}")
        return

    except requests.exceptions.ConnectTimeout:
        logger.exception("Request ConnectTimeoutError")
        return
    except requests.exceptions.ConnectionError:
        logger.exception(
            "Request ConnectionError. Check your internet connection",
            end="\n",
        )
        return
    except requests.ReadTimeout:  # noqa: F821
        logger.exception("ReadTimeoutError")
        return
    except ConnectionError:
        logger.exception("Connection Error")
        return
    except TimeoutError:
        logger.exception("Timeout Error")
        return
    except Exception as e:
        logger.exception(f"An unexpected error occured: {e}")
        return


def google_metadata_dict(isbn=None, title=None):
    """Function to extract metadata_dict from json_metadata"""

    if isbn:
        json_metadata = get_google_metadata_json(API_KEY, isbn=isbn)
    else:
        json_metadata = get_google_metadata_json(API_KEY, title=title)

    try:
        metadata_dict = json_metadata["items"][0]["volumeInfo"]
    except KeyError:
        metadata_dict = {"kind": "books#volumes", "totalItems": 0}
    return metadata_dict


def openlibrary_metadata_dict(isbn):
    """Function to extract metadata_dict from json_metadata.

    The metadata_dict is directly avvailable in json_metadata.
    Thefore, we assign the extracted json_metadata to metadata_dict
    """
    json_metadata = get_openlibrary_metadata_json(isbn)

    try:
        metadata_dict = json_metadata
    except KeyError:
        #
        metadata_dict = {
            "error": "notfound",
            "key": f"/{isbn}",
        }
    return metadata_dict


def get_dictionary(dictionary):
    """A function that formats dict_of_interest by converting
    a dictionary with all values as "NA" into an empty dictionary.

    If there is an error fetching a data from api, the corresponding
    value of the key in dict_of_interest is "NA". This function ensures
    that at least one non-"NA" value is present in dict_of_interest.

    This function deletes all values in dict_of_interest If all values
    in dict_of_interest are "NA", converting it into an empty dict.
    The goal is to ensure that some values in dict_of_interest can be missing,
    but not all. A book must have a title.
    """

    empty_dict = {}
    final_dict = {}
    for key, value in dictionary.copy().items():
        # if value == "NA", delete from dict_of_interest
        if dictionary[key] == "NA":
            dictionary.pop(key)
        else:
            final_dict[key] = value

    # If book does not have at least a title, final_dict will be empty
    # else, dictionary contains other key:value pairs
    if len(final_dict) == 0:
        return empty_dict
    else:
        return final_dict


def modify_title(title):
    """Function to format title to eliminate characters
        not allowed in windows os file naming.

    Note that there are other reserved filenames
    e.g. "CON", "PRN"
    """
    # remove leading and trailing white spaces
    title = title.strip()

    # replace invalid characters with underscore
    title = re.sub(r'[<>:"/\\|?*!]', "_", title)

    # replace hyphen with underscore
    title = title.replace("-", "_")

    # remove trailing periods (at end of filename)
    title = title.rstrip(".")

    # Keep filename within 255 character limits
    if len(title) > 255:
        title = title[:255]

    return title


def get_metadata_google(
    file,
    isbn_of_book=None,
    title_of_book=None,
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    },
):
    """Function to get book metadata using extracted book isbn (or title),
        and file (to estimate size). The source here is Google BooksAPI only.
    """

    # initialize dictionary dict_of_interest with keys representing the
    # names of keys in json_metadata from Google Books API for values we
    # are interested in. All values are set to empty string.
    dict_of_interest = {
        "title": "",
        "subtitle": "",
        "publishedDate": "",
        "publisher": "",
        "authors": "",
        "pageCount": "",
        "imageLinks": ""
    }

    # Get metadata_dict
    if isbn_of_book:
        metadata_dict = google_metadata_dict(isbn=isbn_of_book)
    else:
        metadata_dict = google_metadata_dict(title=title_of_book)

    # Populate dict_of_interest with metadata values
    available_metadata = metadata_handler(dict_of_interest, metadata_dict)
    dict_of_interest = get_dictionary(available_metadata)

    if len(dict_of_interest) == 0:
        return None
    else:
        pass

    # assign title to variable
    title = dict_of_interest.get("title", "NA")

    # fetch sub_title and full title
    full_title, subtitle = get_subtitle_full_title(
                               metadata_dict,
                               dict_of_interest
                           )

    # assign values in dict_of_interest to respective variables
    date_of_publication = dict_of_interest.get("publishedDate", "NA")
    publisher = dict_of_interest.get("publisher", "NA")
    authors = dict_of_interest.get("authors", "NA")
    page_count = str(dict_of_interest.get("pageCount", "NA"))

    image_link = dict_of_interest.get("imageLinks", "NA")

    isbn_10, isbn_13 = get_isbns_google(metadata_dict)

    # get reference isbn (ref_isbn), the one used to retrieve
    # the metadata. This will later serve in getting book covers
    ref_isbn = isbn_of_book

    source = "www.google.com"

    # get file size
    file_size = get_file_size(file)

    # Get date created
    date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Update dict_of_interest to include all the other values
    dict_of_interest["full_title"] = full_title
    dict_of_interest["isbn_10"] = isbn_10
    dict_of_interest["isbn_13"] = isbn_13
    dict_of_interest["ref_isbn"] = isbn_of_book
    dict_of_interest["source"] = source
    dict_of_interest["filesizes"] = file_size

    logger.info(f"dict_of_interest: {dict_of_interest}")

    return (
        modify_title(title),
        subtitle,
        full_title,
        date_of_publication,
        publisher,
        authors,
        f"{str(page_count)}",
        isbn_10,
        isbn_13,
        ref_isbn,
        source,
        float(file_size),
        image_link,
        date_created,
    )


def get_metadata_openlibrary(
    file,
    isbn,
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\
 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    },
):

    """Function to get book metadata using extracted book isbn,
        and file (to estimate size). The source here is Openlibrary API only.
    """

    # The cover ID is expected and this can be converterted into image_url
    # this to image link by get_cover_url_openlibrary function
    dict_of_interest = {
        "title": "",
        "subtitle": "",
        "publish_date": "",
        "publishers": "",
        "by_statement": "",
        "number_of_pages": "",
        "covers": "",
    }

    # Get metadata_dict using book ISBN
    metadata_dict = openlibrary_metadata_dict(isbn)

    # Populate dict_of_interest with metadata values
    # whose keys are initialized to empty strings
    dict_of_interest = metadata_handler(dict_of_interest, metadata_dict)

    # Fetch title: the nested exception handles cases of
    # inconsistencies in openlibrary json where title may
    # be missing but full_title or subtitle only may be
    # present in the json metadata
    try:
        title = dict_of_interest["title"]
    except KeyError:
        try:
            title = dict_of_interest["subtitle"]
        except KeyError:
            title = dict_of_interest.get("full_title", "NA")

    full_title, subtitle = get_subtitle_full_title(
                                metadata_dict,
                                dict_of_interest
                           )

    # Assign values in dict_of_interest to respective variables
    date_of_publication = dict_of_interest.get("publish_date", "NA")
    publisher = dict_of_interest.get("publishers", "NA")
    authors = dict_of_interest.get("by_statement", "NA")
    page_count = str(dict_of_interest.get("number_of_pages", "NA"))

    # image link
    image_id = dict_of_interest.get("covers", "NA")

    image_link = get_cover_url_openlibrary(image_id, isbn)

    # Get the remaining values
    isbn_10, isbn_13 = get_isbns_openlibrary(metadata_dict)

    # get reference isbn (ref_isbn), the one used to
    # retrieve the metadata
    ref_isbn = isbn

    source = "www.openlibrary.org"

    # get file size
    file_size = get_file_size(file)

    # get creation date
    date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # update dict_of_interest
    dict_of_interest["full_title"] = full_title
    dict_of_interest["isbn_10"] = isbn_10
    dict_of_interest["isbn_13"] = isbn_13
    dict_of_interest["ref_isbn"] = isbn
    dict_of_interest["source"] = source
    dict_of_interest["filesizes"] = file_size

    logger.info(f"dict_of_interest: {dict_of_interest}")

    return (
        modify_title(title),
        subtitle,
        full_title,
        date_of_publication,
        publisher,
        authors,
        f"{str(page_count)}",
        isbn_10,
        isbn_13,
        ref_isbn,
        source,
        float(file_size),
        image_link,
        date_created,
    )


def move_to_missing_metadata(file_src, missing_metadata):
    """Function to move file to missing_metadata directory if its
    metadata is not recovered from both google and openlibrary
    apis.
    """
    move_file_or_directory(file_src, missing_metadata)

    return


def get_metadata_from_api(
    api1_dict,
    api1_dict_key,
    api2_dict,
    api2_dict_key,
    isbn,
    file,
    headers,
    file_src,
    missing_metadata
):
    """Function to search metadata using both openlibrary and
        Google BooksAPI.

        If first API is selected and API returns valid metadata
        function returns metadata else it tries the second API
        and does the same. If all else fail, None is returned.

        The two API sources are selected randomly in practice.
        See main forgy package (messyforg.py).

        The format of api_dicts are as shown:
        {"google": get_metadata_google},
        {"openlibrary": get_metadata_openlibrary}

        Keys are names of api source (google, and open library),
        and values are functions to retrieve data from each API.
    """

    # Check API_1 for metadata (can be any of google or openlibrary)
    # and selection is random
    file_metadata = api1_dict[api1_dict_key](
                        file,
                        isbn,
                        headers=headers
                    )
    # time.sleep(5)

    # If metadata from API_1 is not empty, unpack tuple file_metadata
    # into the various variables
    if file_metadata is not None:
        return file_metadata

    else:
        file_metadata = api2_dict[api2_dict_key](
                            file,
                            isbn,
                            headers=headers
                        )
        # time.sleep(5)

        if file_metadata is not None:
            return file_metadata

        else:
            logger.warning(
                f"ISBN metadata not found for {Path(file).stem}"
            )
            move_to_missing_metadata(file_src, missing_metadata)

            return None


def get_single_book_metadata(
    file,
    book_isbn=None,
    book_title=None
):
    """Function to fetch metadata of a single book from Google
        Books API using title or isbn."""

    values = ""

    if book_title:
        values = get_metadata_google(
                        file,
                        title=book_title,
                     )
    elif book_isbn:
        if is_valid_isbn(book_isbn):
            values = get_metadata_google(
                        file,
                        isbn=book_isbn,
                     )
        else:
            logger.error(f"Invalid ISBN: {book_isbn}")
    else:
        logger.warning("Please provide a valid title or isbn")

    return values


def download_image_bytes(
    image_url,
    no_of_retries=3,
    time_delay_before_retries=1.5
):
    """Function to download image byte object using image_url
        from either Google or Openlibrary API.
    """
    for trial in range(no_of_retries):
        try:
            # Get image bytes object (in streams for memory
            # efficiency) and handle errors

            response = requests.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            logger.info(f"Status code {response.status_code}")
        except requests.exceptions.Timeout:
            logger.exception(
                "The request timed out. Attempting trial {trial + 1}..."
            )
            time.sleep(time_delay_before_retries)
            time_delay_before_retries *= 1.5
            continue
        except requests.exceptions.ReadTimeout:
            logger.exception(
                f"ReadTimeout Error. Attempting trial {trial + 1}..."
            )
            time.sleep(time_delay_before_retries)
            time_delay_before_retries *= 1.5
            continue
        except requests.exceptions.HTTPError:
            logger.exception(
                f"HTTP error occurred. Attempting trial {trial + 1}..."
            )
            time.sleep(time_delay_before_retries)
            time_delay_before_retries *= 1.5
            continue
        except requests.exceptions.RequestException as e:
            logger.exception(
                f"Error '{e}' occured. Attempting trial {trial + 1}..."
            )
            time.sleep(time_delay_before_retries)
            time_delay_before_retries *= 1.5
            continue
        else:
            # if no exception is raised
            logger.info("Request was successful")
            return response


def process_image_bytes(response, image_file):
    """Function process image byte objects and write to file"""

    logger.info(f"Status response: {response}")
    if not response.ok:
        logger.info(response)
        # return
    else:
        # Retrieve Content-Length header from HTTP request
        content_length = response.headers.get('content-length')
        logger.info(f"Content length: {content_length}")

        # If server does not provide content length (size of content
        # in bytes), download the tne entire image at once and write
        # to file.
        if content_length is None:
            image_file.write(response.content)
            logger.info(f"{image_file} downloaded successfully")
        else:
            # if server provides content length, download file size
            # in 3 kilobytes chunks.
            downloaded_bytes = 0
            content_length = int(content_length)

            try:
                for chunk in response.iter_content(chunk_size=3072):
                    # If no chunk if received (such as when all chunks
                    # are fully downloaded, break the loop and move to
                    # next file
                    if not chunk:
                        break

                    # Write each chunk to file as it is downloaded
                    image_file.write(chunk)
                    logger.info(f"Successfully downloaded {image_file}")

                    # Update total length of downloaded chunks
                    downloaded_bytes += len(chunk)

                    logger.info(
                        f"Progress: {(downloaded_bytes/content_length)*100:.2f}%"
                    )
            except requests.exceptions.ChunkedEncodingError:
                logger.exception("Chunked Encoding Error occured")
            except Exception as e:
                logger.exception(f"An unexpected exception occured: {e}")


def get_book_covers(cover_dir, database, table):
    """Function to extract cover page for all books in library.db. These books
        have all their metadata successfully downloaded.

    Ref_isbn in database is used to fetch cover image from google or openlibrary.
    Openlib has covers api while google returns cover with metadata json.
    """

    # Confirm if cover_dir is a valid directory
    if not Path(cover_dir).is_dir():
        logger.warning(f"Cover directory {cover_dir} is not a directory")
        return None

    cover_dir_path = Path(cover_dir)

    # get book_metadata from database. The format is:
    # [(title, ref_isbn, source, image_url),...(title, image_url...)]
    book_metadata = get_database_columns(
                        database,
                        table,
                        columns=["Title", "RefISBN", "Source", "ImageLink"]
    )

    for val in book_metadata:
        # Enable matching of order of columns
        title, ref_isbn, source, image_url = val

        image_file_path = f"{cover_dir_path}/{title}.jpg"

        if image_url == "NA":

            if source == "www.google.com":

                # New source = "www.openlibrary.org"
                image_url = get_cover_url_openlibrary("NA", ref_isbn)
                logger.info(f"New image_url extracted from OpenlibraryAPI: {image_url}")
            elif source == "www.openlibrary.org":

                # New_source = "www.google.com"
                # Since we do not need to extract the whole metadata in this case,
                # We simple extract the imageLinks from json_metadata using the
                # get_image_url_google function
                image_url = get_image_url_google(
                    isbn_of_book=ref_isbn,
                )
                logger.info(f"New image_url extracted from Google BooksAPI: {image_url}")
            else:
                logger.error(f"Invalid image url in database: {image_url}")
                pass

        with open(image_file_path, 'wb') as image_file:

            # set number of api call requests before skipping iteration
            response = download_image_bytes(image_url)
            process_image_bytes(response, image_file)

        # sleep for 5 seconds after each operation to stay within the 20 request
        # per minute api limit by openlibrary
        time.sleep(5)

        print()

    # Take statistics of book cover downloads
    successful_image_downloads = 0
    unsuccessful_image_downloads = 0

    with os.scandir(cover_dir_path) as entries:
        for entry in entries:

            if entry.is_file():
                file_size_bytes = entry.stat().st_size

                if file_size_bytes <= 1000:
                    logger.error(f"Invalid image: {image_file_path}")
                    unsuccessful_image_downloads += 1

                elif file_size_bytes > 1000:
                    successful_image_downloads += 1
                    logger.error(f"Image file is valid: {image_file_path}")

                else:
                    pass

            else:
                logger.error(f"Entry is not a file {entry}")

    print(
        f"""
    FOrgy Cover Image Download Statistics:
    Total no of images: {count_files_in_directory(cover_dir_path)}
    Successful image downloads: {successful_image_downloads}
    Unsuccessful image downloads: {unsuccessful_image_downloads}"""
    )

    return None
