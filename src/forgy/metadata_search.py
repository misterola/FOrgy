# metadata search on google and openlib apis
import json
import os
import re
import shutil
from datetime import datetime
import sqlite3
from pathlib import Path
import time

# from .user_requirements import headers, API_KEY
import requests
from dotenv import load_dotenv

from .database import get_database_columns

# Load BookAPI key from dotenv file
load_dotenv()

# Get BooksAPI key from .env
API_KEY = os.getenv('GOOGLE_API_KEY')
print(f"Google API Key is: {API_KEY}")

headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }


def merge_list_items(
    given_list,
):  # format can be first author et al if list contains more than two et al
    """convert content of
    list into a single string of the
    list of values neatly separated
    by a comma"""
    if isinstance(given_list, list):
        appended_values = ", ".join(given_list)
        return appended_values
    else:
        print(f"parameter is of type {type(given_list)}, not of type:list")
        pass

    
def get_cover_url(dictionary):
    """Function to get book cover thumbnail (medium-sized) from googlebooks api.

    The format of imageLinks dictionary retrieved from json metadata

    "imageLinks": {
          "smallThumbnail": "http://books.google.com/books/content?id=mC-4CwAAQBAJ&printsec=frontcover&img=1&zoom=5&edge=curl&source=gbs_api",
          "thumbnail": "http://books.google.com/books/content?id=mC-4CwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api"
    }
    """
    #cover_info = dictionary["items"][0]["volumeInfo"]["imageLinks"]
    print(f"SUPPLIED DICT: {dictionary}")
    if "thumbnail" in dictionary.copy().keys():
        cover_url = dictionary["thumbnail"]
    elif "smallThumbnail" in dictionary.copy().keys():
        cover_url = dictionary["smallThumbnail"]
    else:
        cover_url = "NA"
    return cover_url


def get_cover_url2(cover_id, isbn):
    """Funtion to get cover image from openlibrary api.

    Cover API documentation can be found here:
    https://openlibrary.org/dev/docs/api/covers
    Rate-limit for openlib = 100 covers per 5 minutes per user IP

    Modify function later to have thumbnail-size parameter
    """
    if cover_id != "NA":
        image_link = 'https://covers.openlibrary.org/b/id/' + cover_id + '-M.jpg'
    else:
        image_link = 'https://covers.openlibrary.org/b/isbn/' + isbn + '-M.jpg'
    return image_link
        

# a function to handle keys and values of different types, including missing keys and values of type str, list
# dict of interest is populated with available values whose keys match those in API
def metadata_handler(dict_of_interest, metadata_dict):
    """dict of interest is empty_valued while metadata_dict is from json data from api"""
    print(f"dict_of_interest: {dict_of_interest}, metadata_dict: {metadata_dict}")
    for key in dict_of_interest.keys():
        # if key in defined empty-valued book dictionary also exist
        # in metadata keys from api (this means data is available)
        if key in metadata_dict.keys():
            # if value in retrieved dict is a list containing single element, extract that element using zero index
            # and update the defined empty_valued dictionary (dict_of_interest)
            if isinstance(metadata_dict[key], list) and len(metadata_dict[key]) == 1:
                try:
                    dict_of_interest[key] = dict_of_interest[key] + metadata_dict[key][0]
                except TypeError:
                    #this can occur in the case of cover_id in openlib api which is a list containing one integer
                    print(f"{metadata_dict[key][0]} is of type {type(metadata_dict[key][0])}")
                    dict_of_interest[key] = dict_of_interest[key] + str(metadata_dict[key][0])
                    

            # if value in retrieved dict is a list containing multiple elements, extract that element using zero index
            # and update the defined empty_valued dictionary (dict_of_interest)
            elif isinstance(metadata_dict[key], list) and len(metadata_dict[key]) > 1:
                dict_of_interest[key] = dict_of_interest[key] + merge_list_items(
                    metadata_dict[key]
                )
            # if a dictionary if returned (containing two elements like the case of book thumbnail urls in googleapi)
            elif isinstance(metadata_dict[key], dict) and len(metadata_dict[key]) >= 1:
                dict_of_interest[key] = get_cover_url(metadata_dict[key])
                print(f"DICT OF INTEREST: {dict_of_interest[key]}")
            else:
                # If value is a single value (string), simply assign the value to
                # corresponding key in empty-valued dictionary
                dict_of_interest[key] = metadata_dict[
                    key
                ]  # If the value is a str or int
        else:
            # absent values are market 'NA'
            dict_of_interest[key] = "NA"  # if key not in metadata

    return dict_of_interest


# handle title, subtitle and derive subtitle from the former
def get_title_subtitle(metadata_dict, dict_of_interest):
    if ("title" in metadata_dict.keys()) and ("subtitle" not in metadata_dict.keys()):
        subtitle = "NA"
        full_title = dict_of_interest["title"]
    else:  # ("title" in metadata_dict.keys()) and ("subtitle" in metadata_dict.keys())
        subtitle = dict_of_interest["subtitle"]
        full_title = dict_of_interest["title"] + ": " + dict_of_interest["subtitle"]
    return full_title, subtitle


def get_isbns(metadee):  # noqa: C901
    """fetches isbn10 and isbn13 from metadata via google and
    returns 'NA' if isbn value is not available the result
    is a list of two dictionaries each dict has two key:value
    pairs (e.g. {'type':ISBN_10, 'identifier':'2382932220'})"""
    if "industryIdentifiers" in metadee.keys():
        # if index 0 in list is for ISBN_10 dictionary and index1 in list is for ISBN_13 dictionary
        if (
            metadee["industryIdentifiers"][0]["type"] == "ISBN_10"
            and ("ISBN_10" in metadee["industryIdentifiers"][0].values())
            and metadee["industryIdentifiers"][1]["type"] == "ISBN_13"
            and ("ISBN_13" in metadee["industryIdentifiers"][1].values())
        ):
            try:
                isbn_10 = metadee["industryIdentifiers"][0]["identifier"]
            except (UnboundLocalError, IndexError):
                isbn_10 = "NA"
            try:
                isbn_13 = metadee["industryIdentifiers"][1]["identifier"]
            except (UnboundLocalError, IndexError):
                isbn_13 = "NA"

        # if index 0 in list is for ISBN_13 dictionary and index1 in list is for ISBN_10 dictionary
        elif (
            metadee["industryIdentifiers"][0]["type"] == "ISBN_13"
            and ("ISBN_13" in metadee["industryIdentifiers"][0].values())
            and metadee["industryIdentifiers"][1]["type"] == "ISBN_10"
            and ("ISBN_10" in metadee["industryIdentifiers"][1].values())
        ):
            try:
                isbn_13 = metadee["industryIdentifiers"][0]["identifier"]
            except (UnboundLocalError, IndexError):
                isbn_13 = "NA"
            try:
                isbn_10 = metadee["industryIdentifiers"][1]["identifier"]
            except (UnboundLocalError, IndexError):
                isbn_10 = "NA"
        else:
            # (metadee["industryIdentifiers"][0]["type"]== "OTHER") and len(metadee["industryIdentifiers"]==1)
            # to handle cases like this:'industryIdentifiers': [{'type': 'OTHER', 'identifier': 'UOM:39015058578744'}]
            isbn_10 = "NA"
            isbn_13 = "NA"
    else:
        # if error is returned by database or metadata retrieve unsuccessful
        isbn_10 = "NA"
        isbn_13 = "NA"
    return isbn_10, isbn_13


def get_isbns2(metadata_dict):
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
    # uses file path to obtain file size
    file_stats = os.stat(file_path)
    # print(file_stats): returns an os.stat_result object(st_size in object is the filesize in bytes)
    file_size_bytes = file_stats.st_size
    # print(file_size_bytes) returns size of file in bytes
    file_size_MB = file_size_bytes / (1024 * 1024)
    return f"{file_size_MB:.2f}"
    # returns file_size in megabytes: 9.493844985961914
    # .st_size returns filesize in bytes and this is divided
    # by 1024 twice to get value in MB
    # filesize = os.stat(file_src).st_size/(1024*1024


# for use in main script
def google_api(API_KEY, isbn=None, title=None):
    print(f"For google_api, Title:{title} and ISBN={isbn}")
    if isbn:
        googleapi_metadata = (
            "https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn + "&key=" + API_KEY
        )
    else:
        googleapi_metadata = (
            'https://www.googleapis.com/books/v1/volumes?q=intitle:'+ title
        )
    print(f"GoogleAPI metadata url: {googleapi_metadata}, ISBN: {isbn}, Title: {title}")
    # define function load metadata for both google and openlibrary api to return json_metadata
    # check google api for book metadata
    book_metadata = requests.get(
    googleapi_metadata, headers=headers, timeout=60
    )  # 300 works
    book_metadata.raise_for_status()
    json_metadata = json.loads(book_metadata.text)
    return json_metadata


# For use in main script
def openlibrary_api(isbn):
    olibapi_metadata = "https://openlibrary.org/isbn/" + isbn + ".json"
    book_metadata = requests.get(olibapi_metadata, headers=headers, timeout=60)
    book_metadata.raise_for_status()
    json_metadata = json.loads(book_metadata.text)
    return json_metadata


# Assign dict from extracted metadata to metadata_dict
def google_metadata_dict(isbn=None, title=None):
    print(f"google_metadata_dict, Title:{title}, ISBN: {isbn}")
    if isbn:
        json_metadata = google_api(API_KEY, isbn=isbn)
    else:
        json_metadata = google_api(API_KEY, title=title)

    try:
        metadata_dict = json_metadata["items"][0]["volumeInfo"]
    except KeyError:
        metadata_dict = {"kind": "books#volumes", "totalItems": 0}
    return metadata_dict


def openlibrary_metadata_dict(isbn):
    json_metadata = openlibrary_api(isbn)
    # values are directly avvailable in json_metadata without nesting, so we assign the extracted json to metadata_dict
    try:
        openlibrary_metadata_dict = json_metadata
    except KeyError:
        openlibrary_metadata_dict = {
            "error": "notfound",
            "key": "/044482409x",
        }  # this dict is that returned by openlib when metadata not available
    return openlibrary_metadata_dict


# if there is an error fetching data from api, a dictionary with all values as 'NA' is returned.
# the function below converts this into an empty dictionary
def get_dictionary(dictionary):
    # checks if all values in a dictionary are 'NA' and returns an empty dictionary in that case.
    # some values in dict can be missing but not all!
    empty_dict = {}
    final_dict = {}
    for key, value in dictionary.copy().items():
        # if key == 'NA':
        if dictionary[key] == "NA":
            dictionary.pop(key)
        else:
            final_dict[key] = value
        # else append value to null_dict (of no use)
    if len(final_dict) == 0:
        return empty_dict
    else:
        return final_dict

# Function to format title to format allowed by windows os
# Note that there are other reserved filenames e.g. "CON", "PRN"
def modify_title(title):
    # remove leading and trailing white spaces
    title = title.strip()

    # replace invalid characters with underscore
    title = re.sub(r'[<>:"/\\|?*!]', "_", title)

    # remove hyphen
    title = title.replace("-", "_")

    # remove trailing periods (at end of filename)
    title = title.rstrip(".")

    # Keep filename within 255 character limits
    if len(title) > 255:
        title = title[:255]

    return title


# prev: isbn, api, headers as input
def get_metadata_google(
    file,
    isbn=None,
    title=None,
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    },
):
    print(f"For get_metadata_google, title={title}, isbn={isbn}")
    """Supply extracted isbn to fetch book metadata as a json from either google.com api or openlibrary.org api"""
    # gets file metadata from google or openlibrary apis
    # json_metadata = google_api(isbn)
    # initialize dictionary with most important keys also present in json and values initialized to empty string
    # keys are named according to keys in json from api source
    dict_of_interest = {
        "title": "",
        "subtitle": "",
        "publishedDate": "",
        "publisher": "",
        "authors": "",
        "pageCount": "",
        "imageLinks": ""   
    }

    # dictionary["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
    # Assign dict from extracted metadata to metadata_dict
    if isbn:
        metadata_dict = google_metadata_dict(isbn=isbn)
    else:
        metadata_dict = google_metadata_dict(title=title)
    

    # populate dictionary with metadata values whose keys are initialized with empty_values are automatically added)
    available_metadata = metadata_handler(dict_of_interest, metadata_dict)
    dict_of_interest = get_dictionary(available_metadata)

    if len(dict_of_interest) == 0:
        return None
    else:
        pass

    # assign title to variable
    title = dict_of_interest.get("title", "NA")

    # fetch sub_title and full title
    # full_title, subtitle = get_title_subtitle(metadata_dict, metadata_dict)
    full_title, subtitle = get_title_subtitle(metadata_dict, dict_of_interest)

    # assign values populated in dict_of_interest to variables
    # (keys are: title, publishedDate, publisher, authors, pageCount)
    date_of_publication = dict_of_interest.get("publishedDate", "NA")
    publisher = dict_of_interest.get("publisher", "NA")
    authors = dict_of_interest.get("authors", "NA")
    page_count = str(dict_of_interest.get("pageCount", "NA"))

    image_link = dict_of_interest.get("imageLinks", "NA")

    # GET OTHER VALUES
    # get isbns from metadata

    isbn_10, isbn_13 = get_isbns(metadata_dict)

    # get reference isbn (ref_isbn), the one used to retrieve the metadata
    ref_isbn = isbn

    source = "www.google.com"

    # get file size
    file_size = get_file_size(file)

    # get date created
    date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # update dict_of_interest
    dict_of_interest["full_title"] = full_title
    dict_of_interest["isbn_10"] = isbn_10
    dict_of_interest["isbn_13"] = isbn_13
    dict_of_interest["ref_isbn"] = isbn
    dict_of_interest["source"] = source
    dict_of_interest["filesizes"] = file_size

    # print(dict_of_interest)

    # print(f"""
    # title = {title},
    # subtitle = {subtitle},
    # full_title = {full_title},
    # date_of_publication = {date_of_publication},
    # publisher = {publisher},
    # authors = {authors},
    # page_count = {str(page_count)},
    # isbn_10 = {isbn_10},
    # isbn_13 = {isbn_13},
    # ref_isbn = isbn,
    # source = {source},
    # filesize = {filesize:.2f} MB""")
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
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    },
):
    """Supply extracted isbn to fetch book metadata as a json from either google.com api or openlibrary.org api"""
    # json_metadata = openlibrary_api(isbn)
    # Initialize dictionary with most important keys also present in json and values initialized to empty string
    dict_of_interest = {
        "title": "",
        "subtitle": "",
        "publish_date": "",
        "publishers": "",
        "by_statement": "",
        "number_of_pages": "",
        "covers": "", # cover ID expected and function converts this to image link
    }  # str by_statement rep authors in openlib api
    # openlib also has "full_title" key in json

    # Values are directly available in json_metadata without nesting,
    # so we assign the extracted json to metadata_dict
    metadata_dict = openlibrary_metadata_dict(isbn)

    # populate dictionary with metadata values whose keys are initialized with empty_values are automatically added)
    dict_of_interest = metadata_handler(dict_of_interest, metadata_dict)

    # Fetch title: the nested exception handles cases of inconsistencies in openlibrary json where
    # title may be missing but full_title or subtitle only may be present in the json metadata
    try:
        title = dict_of_interest["title"]
    except KeyError:
        try:
            title = dict_of_interest["subtitle"]
        except KeyError:
            title = dict_of_interest.get("full_title", "NA")

    # fetch sub_title and full title
    full_title, subtitle = get_title_subtitle(metadata_dict, dict_of_interest)

    # assign values populated in dict_of_interest to variables (keys are:
    # title, publishedDate, publisher, authors, pageCount)
    date_of_publication = dict_of_interest.get("publish_date", "NA")
    publisher = dict_of_interest.get("publishers", "NA")
    authors = dict_of_interest.get("by_statement", "NA")
    page_count = str(dict_of_interest.get("number_of_pages", "NA"))

    # image link
    image_id = dict_of_interest.get("covers", "NA")
    image_link = get_cover_url2(image_id, isbn)

    
    # GET OTHER VALUES
    # get isbns from metadata

    isbn_10, isbn_13 = get_isbns2(metadata_dict)

    # get reference isbn (ref_isbn), the one used to retrieve the metadata
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

    # print(dict_of_interest)

    # print(f"""
    # title = {title},
    # subtitle = {subtitle},
    # full_title = {full_title},
    # date_of_publication = {date_of_publication},
    # publisher = {publisher},
    # authors = {authors},
    # page_count = {str(page_count)},
    # isbn_10 = {isbn_10},
    # isbn_13 = {isbn_13},
    # ref_isbn = "isbn",
    # source = {source},
    # file_size = {file_size:.2f} MB"""
    #       )
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


# If metadata not recovered from both google and openlibrary apis,
# Print file_name not found and move file to missing_metadata directory

def move_to_missing_metadata(file_src, missing_metadata):
    try:
        shutil.move(file_src, missing_metadata)
    # FileNotFoundError raised if file has a missing ISBN and is already moved to
    # Missing_isbn directory. skip this whole process for file that raises this error
    except FileNotFoundError:
        # This is a case where file has already been moved to missing_isbn directory
        pass
        # continue


def get_metadata_from_api(api1_dict,
                          api1_dict_key,
                          api2_dict,
                          api2_dict_key,
                          isbn,
                          file,
                          headers,
                          file_src,
                          missing_metadata):
    # call get_metadata_google or get_metadata_openlibrary
    file_metadata = api1_dict[api1_dict_key](file, isbn, headers=headers)
    # time.sleep(5)

    # If metadata from google is not empty, unpack tuple file_metadata into the various variables
    if file_metadata is not None:
        return file_metadata
        
    else:
        file_metadata = api2_dict[api2_dict_key](file, isbn, headers=headers)
        # time.sleep(5)

        # If metadata from google is not empty, unpack tuple file_metadata into the various variables
        if file_metadata is not None:
            return file_metadata

        else:
            print(f"ISBN metadata not found for {pdf_path.stem}")
            move_to_missing_metadata(file_src, missing_metadata)
            return None                            


def download_book_covers(isbns):
    """use ref isbn to fetch thumbnail cover image or medium cover image from google or openlibrary respectively.

    Getting cover_page is only to be applied to books with successfully extracted metadata (those in database).
    Search details in google api followed by openlibrary_api.

    Openlib has covers api while google returns cover with metadata json.
    1. If metadata found, download cover image using image link, save to book_covers folder and rename to book title
    

    In both cases, update database to include link to coverpage on pc
    """
    pass


def get_single_book_metadata(file, isbn=None, title=None):
    """Function to fetch metadata of one book by title or isbn from google bookapi."""

    values=""
    # If title is supplied, in all function calls, title is assigned to supplied title
    # while isbn is None. The converse is also true.
    if title:
            values = get_metadata_google(
                        file,
                        title=title,
                     )
    elif isbn:
        values = get_metadata_google(
                    file,
                    isbn=isbn,
                 )
    else:
        print("Please provide a valid title or isbn")

    print(f"""
            Title: {title}
            ISBN: {isbn}"""
    )
        
    return values


def get_book_covers(cover_dir, database, table):
    """Function to extract cover page for all books in library.db(those with successfully obtained metadata."""
    
    # Confirm if cover_dir is a valid directory
    if not Path(cover_dir).is_dir():
        print(f"Cover directory {cover_dir} is not a directory")
        return None

    cover_dir_path = Path(cover_dir)

    # get book_metadata from database. The format is [(title, image_url),...(title, image_url)]
    book_metadata = get_database_columns(database, table)

    # Iterate through "title, image_url" in book_metadata and download file
     
    for val in book_metadata:
        #enable matching of order of columns
        title, image_url = val
        # print(f"Title: {title}\nImage_url: {image_url}")

        # enable skipping already downloaded cover pages
        
        with open(f"{cover_dir_path}/{title}.jpg", 'wb') as image_file:
            # set number of api call requests before skipping iteration
            retries = 3
            delay_before_retries = 1.5
            
            try:
                for trial in range(retries):
                    # get image bytes object (in streams for memory efficiency downloading large files or many files) and handle errors
                    # Send get request to image url
                    response = requests.get(image_url, timeout=30, stream=True)

                    #Check if request is successful. raise HTTPError if any
                    response.raise_for_status()
            except requests.exceptions.Timeout:
                print("The request timed out.")
                print(f"Attempt {trial + 1}")
                continue
            #handle raised exception/HTTPError by raise_for_status
            except requests.exceptions.HTTPError as error:
                print(f"HTTP error occurred: {error}")
                print(f"Attempt {trial + 1}: HTTP error occurred: {error}")
                print(f"Status code: {response.status_code}")
                continue
            except requests.RequestException as e:
                print(f"Error '{e}' occured")
                print(f"Attempt {trial + 1}: An error occurred: {e}")
                continue
            else:
                # if no exception is raised
                print("Request was successful")
                print(f"Status code: {response.status_code}")
            time.sleep(delay_before_retries)
            delay_before_retries *= 1.5

            # Check if the response was successful. response.ok returns True if success status code (2xx) or False otherwise(4xx, 5xx)
            if not response.ok:
                print(response)
            else:
                #retrieve Content-Length header from HTTP request
                content_length = response.headers.get('content-length')
                #print(response.headers)
                #print(content_length)

                # if server does not provide content length (size of content in bytes),
                # download the tne entire image at once. Load the entire image into memory and write to file at once without monitoring progress
                if content_length is None:
                    image_file.write(response.content)    # response.content is the raw binary content of response body (image)
                    print(f"{title} downloaded successfully")
                else:
                    # if server provides content length, download file size in 1kilobyte chunks.
                    downloaded_bytes = 0
                    content_length = int(content_length)
                    print(f"{title}")
                    for chunk in response.iter_content(chunk_size=1024):
                        # If no chunk if received (such as when all chunks are fully downloaded, break the loop and move to next file
                        if not chunk:
                            break
                        #write each chunk to file as it is downloaded
                        image_file.write(chunk)
                        #update total length of downloaded chunks
                        downloaded_bytes += len(chunk)
                        print(f"Download Progress: {downloaded_bytes}/{content_length} bytes, ({(downloaded_bytes / content_length) * 100:.2f}% DONE)")
        # sleep for 3 seconds after each operation to meet the 20 request per minute api requirement by openlibrary
        time.sleep(5)

    print()
    return None
   

# www.openlibrary.org/search/inside.json?q="what is life"

# Search with title
# https://www.googleapis.com/books/v1/volumes?q=intitle:"To Kill a Mockingbird"

# if api = google and json values returned, use google api,
# else: we use openlibrary api
# case 1. api = openlibrary and json values returned; retrieve values
# case 2. api = openlibrary  and json values not returned; set api as
# google api and if values not returned,,, print values not found

# Define a function to enable user check individual book for ISBN and automatically apply metadata to book
