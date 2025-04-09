"""
The main module of the forgy package.
"""


from pathlib import Path
import os
import time
import random

import requests
import pypdf

from .isbn_regex import (
    extract_valid_isbns,
)
from .text_extraction import extract_text
from .metadata_search import (
    headers,
    get_metadata_google,
    get_metadata_openlibrary,
    get_metadata_from_api,
)
from .database import (
    add_metadata_to_table,
    titles_in_db,
    is_isbn_in_db,
)
from .process_stats import show_statistics
from .filesystem_utils import (
    delete_files_in_directory,
    move_file_or_directory,
    rename_file_or_directory,
)
from .logger import create_logger

# Both console and rotating file handlers are created
# They log ERROR and INFO levels respectively
logger = create_logger('forgy')
logger.info("Logger created successfully")


def check_internet_connection():
    """
    Check user internet connection.

    Return True if user is connected
    and False otherwise.
    """
    try:
        response = requests.get(
            "https://www.google.com",
            timeout=5
        )

        if response.status_code == 200:
            logger.info("Internet connection is active")
            return True
    except requests.exceptions.ConnectionError:
        logger.error("No internet connection")
        return False


def create_directories(
    data="data",
    forgy_pdfs_copy="pdfs",
    missing_isbn="missing_isbn",
    missing_metadata="missing_metadata",
    book_metadata="book_metadata",
    extracted_texts="extracted_texts",
    book_covers="book_covers",
    delete_content=True
):

    """
    Create data directory and its subdirectories.

    These are needed to contain diffenrent categories of files
    and directories handled by FOrgy during operations of
    get_metadata subcommand or while fetch_book_metadata
    function is working
    """

    current_directory = Path(os.getcwd())

    # Get the parent directory for the data/ directory.
    # If this module is run from main.py, the parent is
    # one level above current directory in the directory
    # tree. If this module runs on its own, the parent is
    # even one steps further above.
    data_parent_directory = current_directory.parent
    logger.info(f"Data parent directory: {data_parent_directory}")

    # Create path to data directory
    data_path = data_parent_directory/data

    # Create the paths to all sub_directories in data/
    forgy_pdfs_copy_path = data_path/forgy_pdfs_copy
    missing_isbn_path = data_path/missing_isbn
    missing_metadata_path = data_path/missing_metadata
    book_metadata_path = data_path/book_metadata

    # Create paths to subdirectories of some directories in data/
    # (i.e. missing_isbn/extracted_texts and book_metadata/covers)
    extracted_texts_path = missing_isbn_path/extracted_texts
    cover_pics_path = book_metadata_path/book_covers

    directories = [
        data_path,
        forgy_pdfs_copy_path,
        missing_isbn_path,
        missing_metadata_path,
        book_metadata_path,
        extracted_texts_path,
        cover_pics_path,
    ]

    for directory in directories:
        if directory.exists() and delete_content:
            delete_files_in_directory(directory)
            logger.warning(
                f"Files in existing {directory} directory deleted"
            )
            continue
        try:
            directory.mkdir(exist_ok=True)
            logger.info(f"{directory} directory created successfully")
        except FileExistsError:
            # Delete all files inside directory
            delete_files_in_directory(directory)
            logger.exception(f"Content of {directory} directory cleared")
            continue
    return directories


def estimate_process_duration(start_time):
    """
    Function to estimate duration of get_metadata operation
    on each file.

    Start time is predefined at the start of the loop that goes
    through file.

    Timing for unsuccessful get_metadata operation is taken right
    before the operation is carried out on the next file in loop.
    """
    end_time = time.time()
    duration = end_time - start_time
    return f"{duration:.5f}"


def save_process_duration(file_name,
                          process_duration,
                          duration_dictionary):
    """
    Function adds the operation time for file to dictionary.

    This ie eventually used in estimating total time taken in the
    process_statistics module.
    """
    duration_dictionary[file_name] = process_duration
    return duration_dictionary


def estimate_and_save_process_duration(
    start_time,
    file_name,
    duration_dictionary
):
    """
    Function to save duration of operation on each file to a
    duration_dictionary which is maintained for the session.

    The key:alue pairs in duration dictionary represent
    file_name:process_duration.
    """
    process_duration_sec = estimate_process_duration(start_time)
    save_process_duration(
        file_name,
        process_duration_sec,
        duration_dictionary
    )


def return_dict_key(dictionary):
    """Function to get key in a dictionary of 1 item."""
    for key, _ in dictionary.items():
        key = key
    return key


def choose_random_api(api_list):
    """
    Function to choose an api(key) and its associated calling
    function (value) from a list of dictionaries containing two apis.

    The format of the api_list containing dictionaries is:
    # [{"google":get_metadata_google},
       {"openlibrary": get_metadata_openlibrary}]
    """
    # Randomly select api1_dictionary containing one item.
    api1_dict = random.choice(api_list)

    # Get the dictionary for api2
    api_list_copy = api_list.copy()
    api1_index = api_list.index(api1_dict)
    del api_list_copy[api1_index]
    api2_dict = api_list_copy[0]

    # Get key of each api dictionary
    api1_dict_key = return_dict_key(api1_dict)
    api2_dict_key = return_dict_key(api2_dict)

    return (api1_dict, api1_dict_key, api2_dict, api2_dict_key)


def fetch_book_metadata(  # noqa: C901
    user_pdfs_source,
    pdfs_path,
    user_pdfs_destination,
    database_path,
    missing_isbn_path,
    missing_metadata_path,
    extracted_texts_path,
    table_name,
    database_name
):
    """
    Function to get book metadata from google BooksAPI and openlibrary
    APIs, rename books using title from fetched metadata, save book
    metadata to database, and move files without isbn or with
    unsuccessful metadata request to missing_isbn and missing_metadata
    directories respectively.

    user_pdfs_source: source directory containing pdf files provided
                      by user
    user_pdfs_path: the path within the data directory where FOrgy's
                    copy of user_pdfs_source is stored
    user_pdfs_destination: where the extracted and organized
                           data is stored on user pc
    database_path: a path within the data/ directory where database .db
                   file is stored
    missing_isbn_path: directory within data/ directory which contains
                       files which do not contain isbns or text extraction
                       from them failed
    missing_metadata_path: directory within data/ directory where files
                            whose metadata are not provided by the two
                            APIs are moved into
    extracted_text_path: path containing extracted texts from a file with
                         missing_isbn for manual confirmation
    database_name: name of the database (.db) file

    table_name: name of the table within database containing all extracted
                book metadata
    """

    # Initialize raw_files_set to store path to raw files iterated
    # over and initialize renamed_files_set to store path to renamed file
    # This ensures that no file is iterated over twice and metadata is not
    # fetched twice. Title set contains new names of renamed files and it
    # serves a similar purpose with the other two sets mentioned
    raw_files_set = set()
    renamed_files_set = set()
    title_set = set()

    # Duration dictionary stores how long it takes for successful or
    # unsuccessful fetch_metadata operation on a file
    # This will help in estimating total time required to complete file
    # organizing in the process_statistics module
    duration_dictionary = {}

    with os.scandir(pdfs_path) as entries:
        for file in entries:
            file_name = file.name

            # Keep process statistics table display active
            # while the fetch_book_metadata function runs
            show_statistics(
                file_name,
                user_pdfs_source,
                pdfs_path,
                database_path,
                table_name,
                missing_isbn_path,
                missing_metadata_path,
                duration_dictionary
            )

            # start time will be used to estimate process
            # duration before the next file is iterated over
            start_time = time.time()

            # The path attribute of DirEntry object contains
            # file path (file_path)
            file_path = Path(file.path)

            # If file has been iterated over or renamed, skip to next iteration
            if (file_name in raw_files_set) or (file_name in renamed_files_set):
                continue

            # Initialize values, an empty tuple containing metadata parameters
            values = ()

            # Initialize list of valid isbns regex_matched from text
            valid_isbn_list = []

            # Extract text from file in file_path as a long string
            if not file_name.startswith(".") and Path(file_path).is_file():
                try:
                    extracted_text = extract_text(file_path)
                except pypdf.errors.PdfStreamError as e:
                    logger.exception(
                        f"Error encountered while extracting texts from {file_name}: {e}"
                    )
                    continue
                except Exception as f:
                    logger.exception(f"Error encountered: {f}")
                    continue

                # Use regex to match isbn in extracted text, into matched_isbn list
                valid_isbn_list = extract_valid_isbns(extracted_text)


                # For files with missing isbn, save extracted text into file,
                # and move file to missing_isbn directory
                if (missing_isbn_path.exists() and (not valid_isbn_list)):
                    move_file_or_directory(file_path, missing_isbn_path)

                    # For files with missing isbn, generate (empty) text files
                    # and save in extracted_texts_path directory in data/

                    try:
                        with open(
                            f"{missing_isbn_path}/{extracted_texts_path.name}/{file_path.stem}.txt", "a"
                        ) as page_new:
                            page_new.write(extracted_text)
                    except (FileNotFoundError, UnicodeEncodeError) as e:
                        logger.exception(f"Error encountered: {e}")
                        estimate_and_save_process_duration(
                            start_time,
                            file_name,
                            duration_dictionary
                        )
                        continue

                # Compare extracted valid_isbn_list with those in ref_isbn_set
                # from from db RefISBN column. Skip iteration if file is already
                # worked on
                if is_isbn_in_db(database_path, table_name, valid_isbn_list):
                    estimate_and_save_process_duration(
                        start_time,
                        file_name,
                        duration_dictionary
                    )
                    continue
                
                # Use each isbn in int_isbn_list to search on openlibrary api
                # and googlebookapi for book metadata and download in json
                # Repeat same for every isbn in list. If metadata not found,
                # move file to missing_metadata directory and continue to next isbn.
                for isbn in valid_isbn_list:
                        # Select api randomly to avoid overworking any of the apis
                        # The other api will only be checked if the first returns
                        # no metadata
                    api_list = [
                        {"google": get_metadata_google},
                        {"openlibrary": get_metadata_openlibrary},
                    ]

                    (api1_dict,
                     api1_dict_key,
                     api2_dict,
                     api2_dict_key) = choose_random_api(api_list)

                    # Case 1: The selected API = google and valid json_metadata values returned,
                    # extract book metadata from Google API. If returned json metatada from
                    # Google BooksAPI is invalid, set API = openlibary. Return value if valid
                    # or return a NoneType if not.
                    # Case 2: The selected API = openlibrary and valid json_metadata returned,
                    # extract book metadata from Openlibrary API. if returned json metadata from
                    # Openlibrary is invalid, set API = google. Return values from Google API
                    # if valid, otherwise, return a NoneType.
                    if api1_dict_key == "google":

                        # Update initialized empty tuple with the values from API
                        values = get_metadata_from_api(
                                api1_dict,
                                api1_dict_key,
                                api2_dict,
                                api2_dict_key,
                                isbn,
                                file,
                                headers,
                                file_path,
                                missing_metadata_path
                                )
                        # add the filename to raw_files_set to mark it as
                        # processed
                        raw_files_set.add(file_name)
                        time.sleep(5)
                        estimate_and_save_process_duration(
                            start_time,
                            file_name,
                            duration_dictionary
                        )
                        continue

                    else:
                        values = get_metadata_from_api(
                                    api2_dict,
                                    api2_dict_key,
                                    api1_dict,
                                    api1_dict_key,
                                    isbn,
                                    file,
                                    headers,
                                    file_path,
                                    missing_metadata_path
                                 )
                        raw_files_set.add(file_name)
                        time.sleep(5)
                        estimate_and_save_process_duration(
                            start_time,
                            file_name,
                            duration_dictionary
                        )
                        continue
            # Back to os.scandir() ops
            logger.info(f"Extracted metadata for {file_name}: {values}")

            # Extract all titles contained in database as a set 'db_titles'
            db_titles = titles_in_db(database_path, table_name)

            # If the current book title is in database and values metadata tuple
            # is not empty, continue to next iteration
            if values and f"{values[0]}" in db_titles:
                estimate_and_save_process_duration(
                    start_time,
                    file_name,
                    duration_dictionary
                )
                continue

            # For file with retrieved metadata, rename and keep in
            # current directory. A valid metadata must have minimum
            # of two values (title and subtitle). A book without title
            # is almost nonexistent
            if (
                missing_metadata_path.exists()
                and valid_isbn_list
                and values != ""
                and len(list(set(values[0:6]))) >= 2
            ):

                # Rename file using title from API metadata that is formatted
                # to 255 character limit. For successful metadata retrieval
                # parent directory of file is not changed
                dst_dir = pdfs_path
                new_file_name = f"{values[0]}.pdf"
                new_file_path = Path(dst_dir)/new_file_name

                rename_file_or_directory(file_path, new_file_path)

                # Add retrieved metadata to database
                add_metadata_to_table(database_path, table_name, values)

                # Add the name of renamed book to renamed_files_set
                # Add the title of book to title_set...both sets defined earlier
                renamed_files_set.add(new_file_name)
                title_set.add(values[0])

            # For files with missing missing_metadata, move file to
            # missing_isbn directory
            else:
                move_file_or_directory(file_path, missing_metadata_path)

    logger.info(f"duration_dictionary: {duration_dictionary}")


def get_isbns_from_texts(
    source_directory,
    txt_destination_dir,
    text_filename="extracted_book_isbns.txt"
):
    """
    Function to extract isbns for every book in a directory.

    The result is a .txt file containing filenames as keys and
    extracted isbns as a list (containing valid isbn values).
    """
    source_directory = Path(source_directory)
    txt_destination_dir = Path(txt_destination_dir)

    if not source_directory.is_dir():
        logger.warning(
            f"The provided source is not a directory: {source_directory}"
        )
        return

    if not txt_destination_dir.is_dir():
        logger.warning(
            f"The provided isbn text destination is not a directory: {txt_destination_dir}"
        )
        return

    with os.scandir(source_directory) as entries:
        isbn_dict = {}
        for file in entries:
            file_path = file.path
            file_name = file.name

            if not file_name.startswith(".") and Path(file_path).is_file():
                try:
                    # Extract text in first 20 pages of book as a long string
                    extracted_text = extract_text(file_path)
                except pypdf.errors.PdfStreamError as e:
                    logger.exception(
                        f"Error encountered while extracting texts from {file_name}: {e}"
                    )
                    continue
                except Exception as e:
                    logger.exception(f"Error encountered: {e}")
                    continue

                valid_isbn_list = get_valid_isbns(extracted_text)
                logger.info(
                    f"Valid isbn(s) extracted from {file_name} successfully: {valid_isbn_list}"
                )
                isbn_dict[f"{file_name}"] = valid_isbn_list

                isbns_file_path = f"{txt_destination_dir}/{text_filename}.txt"

        with open(isbns_file_path, 'a') as isbn_file:
            isbn_file.write(str(isbn_dict))
            logger.exception(
                f"ISBNs from {file_name} saved to {isbns_file_path}: {valid_isbn_list}"
            )

    return isbn_dict


# APIs
# googlebooks api: https://www.googleapis.com/books/v1/volumes?q=isbn:0-444-82409-x
# openlibrary api: https://openlibrary.org/isbn/9781119284239.json
