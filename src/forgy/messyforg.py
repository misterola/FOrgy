# main
from pathlib import Path
import shutil
import os
import time
import random
import textwrap
import os

import requests

from .isbn_regex import (
    isbn_pattern,
    format_isbn,
    is_isbn_in_db,
)
from .text_extraction import extract_text
from .metadata_search import (
    headers,
    get_metadata_google,
    get_metadata_openlibrary,
    get_metadata_from_api,
    modify_title,
)
from .database import (
    create_table,
    create_library_db,
    add_metadata_to_table,
    view_database_table,
    # delete_table,
    titles_in_db,
)
from .process_stats import (
    number_of_dir_files,
    number_of_processed_files,
    total_time_remaining,
    number_of_database_files,
    percent_api_utilization,
    file_processing_efficiency,
)
from .filesystem_utils import (
    count_files_in_directory,
    delete_files_in_directory,
    get_files_from_directories,
    get_files_from_tree,
)
from .logger import configure_logger


logger = configure_logger('forgy')

def check_internet_connection():
    """Check user internet connection."""
    try:
        response = requests.get("https://www.google.com", timeout=5)

        if response.status_code == 200:
            print("Internet connection is active")
            # logger.info("Internet connection is active")
            return True
    except requests.ConnectionError:
        print("No internet connection")
        return False

# Create data directory and subdirectories. Create directories before the first instance of calling logger
def create_directories(
    data="data",
    pdfs="pdfs",
    missing_isbn="missing_isbn",
    missing_metadata="missing_metadata",
    book_metadata="book_metadata",
    extracted_texts="extracted_texts",
    book_covers="book_covers",
    delete_content=True):
    """Create data directory and its subdirectories"""

    # get the parent directory for data/
    current_directory = Path(os.getcwd())
    # data_parent_directory = current_directory.parent.parent  # if you run this module
    data_parent_directory = current_directory.parent  # if you run from main
    print(f"Data parent directory: {data_parent_directory}")

    # Path to data directory
    data_path = data_parent_directory/data

    # Create the paths to all directories in data/
    pdfs_path = data_path/pdfs
    missing_isbn_path = data_path/missing_isbn
    missing_metadata_path = data_path/missing_metadata
    book_metadata_path = data_path/book_metadata

    # Create paths to subdirectories (missing_isbn/extracted_texts and book_metadata/covers) in data/
    extracted_texts_path = missing_isbn_path/extracted_texts
    cover_pics_path = book_metadata_path/book_covers

    directories = [
##        logs_path,
        data_path,
        pdfs_path,
        missing_isbn_path,
        missing_metadata_path,
        book_metadata_path,
        extracted_texts_path,
        cover_pics_path,
    ]

    for directory in directories:
        if directory.exists() and delete_content:
            delete_files_in_directory(directory)
            print(f"Files in existing {directory} directory deleted")
            continue
        try:
            directory.mkdir(exist_ok=True)
            print(f"{directory} directory created")
        except FileExistsError:
            # Delete all files inside directory
            delete_files_in_directory(directory)
            print(f"Content of {directory} directory cleared")
            continue
    # unpack all links to those paths when this function is called      
    return directories


def get_src_and_dst(src, dst, directory_list_src=False, directory_tree_src=False):
    """Function to properly get sources and destinaton folder. dst destination directory must be empty"""
    
    # clear content of destination directory if it exists
    if Path(dst).exists():
        """Delete directory"""
        #shutil.rmtree(dst)
        delete_files_in_directory(dst)
        logger.info(f"Existing '{dst}' directory deleted") 
        # print(f"Existing '{dst}' directory deleted")

    # Copy pdf files from source directories
    if directory_list_src and isinstance(src, list):
        get_files_from_directories(src, dst)
        print(f"Files in {src} directories moved to {dst}")
        return
    else:
        print(f"Validate directory paths in {src} and ensure that it is a list")
        return

    # Copy pdf files from a source directory tree
    if directory_tree_src:
        get_files_from_tree(src, dst)
        print(f"Files in {src} tree moved to {dst}")
        return
    return None
        

def create_db_and_table(database, table_name="Books", library_db_name="library.db", delete_db_table=True):
    """Create database and Books table in database. Existing table delete in database by default.
       Same is the case in underlying functions.

    Database can be a directory or .db file path.
    """

    # Create Books table in database and specify all metadata columns
    create_table(database, table_name="Books", library_name='library.db', delete_table=delete_db_table)
    return None


# Copy destination directory into forgy pdfs_path
def copy_destination_directory(pdfs_source, new_pdfs_path):
    pdfs_source = Path(pdfs_source)
    new_pdfs_path = Path(new_pdfs_path)

    if not pdfs_source.is_dir():
        print(f"{dst} is not a directory")
        return
    if not new_pdfs_path.is_dir():
        print(f"{new_pdfs_path} is not a directory")
        return
    try:
        # Copy directory even if it exists. FileExistsError will not be raised
        shutil.copytree(pdfs_source, new_pdfs_path, dirs_exist_ok=True)
        logger.info("Source directory copied successfully")
        #print("Source directory copied successfully")
    except Exception as e:
        logger.exception(f"Exception {e} raised")
        # print(f"Exception {e} raised")
        pass



def process_duration(start_time):
    """Function to calculate duration of operation for each file.

    Start time is predefined at the start of the loop that goes
    through file.
    """
    # start_time = start_time
    end_time = time.time()
    duration = end_time - start_time
    return f"{duration:.5f}"


def save_process_duration(file_name,
                          process_duration,
                          duration_dictionary):
    """Function adds the operation time for file to dictionary.

    This ie eventually used in estimating total time taken in the
    process_statistics module."""
    duration_dictionary[file_name] = process_duration
    return duration_dictionary


def return_dict_key(dictionary):
    """Function to get key in a dictionary of 1 item."""
    for key, _ in dictionary.items():
        key = key
    return key


def choose_random_api(api_list):
    """Function to choose an api(key) and its associated calling
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


def format_filename(filename):
    width = 36
    wraped_filename = textwrap.fill(filename, width)
    lines = wraped_filename.split('\n')
    # print(f"Current file: {current_file}")
    first_line = f"{lines[0]}"

    # print subsequent lines
    # subsequent_lines = f"'                {line}' for line in lines[1:]"
    subsequent_lines = '\n'.join([f"                   {line}" for line in lines[1:]])

    return f'{first_line}\n{subsequent_lines}'.rstrip('\n')


def format_time_remaining(time):
    if time < 60:
        time = f"{time:.2f} minutes"
    else:
        time = f"{time:.2f} hours"
    return time


def show_statistics(
        filename,
        original_source,
        src,
        database,
        table,
        missing_isbn_dir,
        missing_metadata,
        duration_dictionary):
    # Define header and footer for table
    table_header = """
=========================================================
                FOrgy Process Statistics
=========================================================
"""

    footer = """
=========================================================
"""
    # Get and format filename
    filename = format_filename(filename)

    total_no_of_files = count_files_in_directory(original_source)

    no_of_processed = number_of_processed_files(
        src,
        database,
        table,
        missing_isbn_dir,
        missing_metadata
    )
    percentage_completion = no_of_processed/total_no_of_files*100
    no_of_database_files = number_of_database_files(database, table)

    time_remaining = total_time_remaining(
        duration_dictionary,
        original_source,
        database,
        table,
        no_of_database_files,
        missing_isbn_dir,
        missing_metadata
    )
    time_remaining = format_time_remaining(time_remaining)

    (percent_google_api,
     percent_openlibrary_api) = percent_api_utilization(database, table)

    process_efficiency = file_processing_efficiency(src, database, table, missing_isbn_dir)
    n_missing_isbn = number_of_dir_files(missing_isbn_dir)
    n_missing_metadata = number_of_dir_files(missing_metadata)

    updated_stats = f"""
    Progress: file {no_of_processed} of {total_no_of_files}
    Current file: {format_filename(filename)}
    Percentage completion: {percentage_completion:.1f}% DONE
    Time remaining: {time_remaining}
    API utilization: {percent_google_api:.1f}% Google, {percent_openlibrary_api:.1f}% Openlibrary
    Process efficiency: {process_efficiency:.1f}%"
    Process summary: {no_of_database_files} files renamed or added to DB,
                     {n_missing_isbn} files with missing ISBN,
                     {n_missing_metadata} files with missing metadata"""

    # Clear screen (gives the values changing effect)
    os.system('cls' if os.name == 'nt' else 'clear')
    print(table_header, end='')
    print(updated_stats)
    print(footer)
    

# Iterate through each file in the new 'ubooks_copy' directory
# and extract text in first 20 pages of each file

def fetch_book_metadata(pdfs_source,
                        original_source,
                        database,
                        missing_isbn_dir,
                        missing_metadata_dir,
                        extracted_texts_path,
                        table_name="Books"):
    
    """Database here is the path to the .db file"""
    # Initialize raw_files_set to store path to raw files iterated over and initialize
    # renamed_files_set to store path to renamed file. This ensures that no file is
    # iterated over twice and metadata is not fetched twice.
    raw_files_set = set()
    renamed_files_set = set()
    title_set = set()

    print(f"pdfs_source: {pdfs_source}")

    # Duration dictionary stores how long it takes for operation on
    # each file.
    # This will help in estimating total time required to complete file
    # organizing in the process_statistics module
    duration_dictionary = {}

    
    with os.scandir(pdfs_source) as entries:    
        for file in entries:    # noqa: C901 # A complex loop_McCabe 30
            # Get and format filename
            file_name = file.name
            show_statistics(
                file_name,
                original_source,
                pdfs_source,
                database,
                "Books",
                missing_isbn_dir,
                missing_metadata_dir,
                duration_dictionary
            )
            start_time = time.time()

            # get file path
            file_src = Path(file.path)

            # If file has been iterated over or renamed, skip to next iteration
            if (file_name in raw_files_set) or (file_name in renamed_files_set):
                continue

            # Initialize values of metadata parameters and assign to values

            values = ""

            # Initialize list of valid isbns
            valid_isbn = []

            # Extract text from file in file_src as a string
            if not file_name.startswith(".") and Path(file_src).is_file():
                extracted_text = extract_text(file_src)

                # Use regex to match isbn in extracted text, into matched_isbn list
                matched_isbn = []
                matched_regex = isbn_pattern.findall(extracted_text)
                matched_isbn.append(matched_regex)
                valid_isbn = format_isbn(matched_isbn)

                # Add all in valid_isbn list to a set of valid isbns
                # add_isbn_to_set(valid_isbn, valid_isbn_set)
                print(valid_isbn)

                # Extracted_text_list = extracted_text.split(' ')

                # For files with missing isbn, save extracted text into file,
                # and move file to missing_isbn directory
                if (missing_isbn_dir.exists() and (not valid_isbn)):
                    try:
                        shutil.move(file_src, missing_isbn_dir)
                        print(f"File {file_name} moved to {missing_isbn_dir} directory")
                    except FileExistsError:
                        print(f"File {file_name} already exists in destination {missing_isbn_dir}")
                    except Exception as e:
                        print(f"Exception {e} raised")
                        pass
                    # For files with missing isbn, generate (empty) text files
                    # to ascertain problem
                    with open(f"{missing_isbn_dir}/{extracted_texts_path.name}/{file_src.stem}.txt", "a") as page_new:
                        try:
                            page_new.write(extracted_text)
                        except (FileNotFoundError, UnicodeEncodeError):
                            process_duration_sec = process_duration(start_time)
                            save_process_duration(file_name,
                                                  process_duration_sec,
                                                  duration_dictionary)
                            print(duration_dictionary)
                            continue
                # Move to next book if its isbn has been previously extracted
                # (compare with ref_isbn_set)
                if is_isbn_in_db(database, table_name, valid_isbn):
                    process_duration_sec = process_duration(start_time)
                    save_process_duration(file_name,
                                          process_duration_sec,
                                          duration_dictionary)
                    print(duration_dictionary)
                    continue

                # Use each isbn in int_isbn_list to search on openlibrary api
                # and googlebookapi for book metadata and download in json
                # Repeat same for every isbn in list. If metadata not found,
                # print error message.
                for isbn in valid_isbn:

                    try:
                        # Select api randomly to avoid overworking any of the apis
                        api_list = [
                            {"google": get_metadata_google},
                            {"openlibrary": get_metadata_openlibrary},
                        ]

                        (api1_dict,
                         api1_dict_key,
                         api2_dict,
                         api2_dict_key) = choose_random_api(api_list)

                        if api1_dict_key == "google":
                            # Assign retrieved metadata to tuple value for easy
                            # addition to database. This updates the initialized values
                            values = get_metadata_from_api(
                                api1_dict,
                                api1_dict_key,
                                api2_dict,
                                api2_dict_key,
                                isbn,
                                file,
                                headers,
                                file_src,
                                missing_metadata_dir
                            )
                            raw_files_set.add(file)
                            time.sleep(5)
                            process_duration_sec = process_duration(start_time)
                            save_process_duration(file_name,
                                                  process_duration_sec,
                                                  duration_dictionary)
                            print(duration_dictionary)
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
                                file_src,
                                missing_metadata_dir
                            )
                            raw_files_set.add(file)
                            time.sleep(5)
                            process_duration_sec = process_duration(start_time)
                            save_process_duration(file_name,
                                                  process_duration_sec,
                                                  duration_dictionary)
                            print(duration_dictionary)
                            continue

                    except ConnectionError:
                        print("Connection Error")
                        continue
                    except TimeoutError:
                        print("Timeout Error")
                        continue
                    except requests.exceptions.ConnectTimeout:
                        print("Request ConnectTimeoutError")
                        continue
                    except requests.exceptions.HTTPError:
                        print("Request HTTPError")
                        continue
                    except requests.exceptions.ConnectionError:
                        print(
                            "Request ConnectionError. Check your internet connection",
                            end="\n"
                        )
                        continue
                    except requests.ReadTimeout:  # noqa: F821
                        print("ReadTimeoutError")
                        continue
                    except requests.RequestException as e:
                        print(f"Error '{e}' occured")

            print(values)

            # Extract all titles contained in database as a set 'db_titles'
            db_titles = titles_in_db(database, table_name)

            # Check if the metadata tuple (i.e. values) is not empty
            # and title is already in database. If that is the case,
            # skip to next iteration
            # if values and f"{values[0]}.pdf" in db_titles:
            if values and f"{values[0]}" in db_titles:
                process_duration_sec = process_duration(start_time)
                save_process_duration(file_name,
                                      process_duration_sec,
                                      duration_dictionary)
                print(duration_dictionary)
                continue

            # ........#
            # For file with retrieved metadata, rename and do not move
            if (
                missing_metadata_dir.exists()
                and valid_isbn
                and values != ""
                and len(list(set(values[0:6]))) >= 2
            ):

                # Default is 4 out of 6
                # Rename file in its original ubooks directory
                old_file_name = file_src
                dst_dir = pdfs_source
                new_file_name = f"{values[0]}.pdf"
                # new_file_path = os.path.join(dst_dir, new_file_name)
                new_file_path = Path(dst_dir)/new_file_name

                try:
                    os.rename(file_src, new_file_path)
                except FileNotFoundError:
                    pass
                # Device how to handle duplicates by attacching time to file name
                except FileExistsError:
                    pass

                # Add retrieved metadata to database
                add_metadata_to_table(database, table_name, values)

                # Add the name of renamed book to renamed_files_set
                # Add the title of book to title_set...both defined earlier
                renamed_files_set.add(new_file_name)
                title_set.add(values[0])

                view_database_table(database, table_name)

            # For files with missing missing_metadata, move file to
            # missing_isbn directory
            else:
                try:
                    shutil.move(file_src, missing_metadata_dir)
                    # FileNotFoundError raised if file has a missing ISBN and is already
                    # moved to missing_isbn directory. skip this whole process for file
                    # that raises this error
                except shutil.Error as e:
                    print(f"Error {e} encountered")
                    pass
                except FileNotFoundError as e:
                    print(f"Error {e} encountered")
                    pass
                # if there is no internet connection, don't move file
                except OSError as e:
                    print(f"Error {e} encountered")
                    pass
                except requests.exceptions.ConnectionError:
                    print("Request ConnectionError. Check your internet connection")
                    pass


# OBSERVED REASONS FOR MISSING ISBN IN EXTRACTED TEXT
# isbn pattern not matching: read isbn standard and write a better regex
# text not having any isbn: follow instruction above 'with statement'
# text cannot be extracted: use OCR
# incomplete isbn digit (e.g. 9 digits): follow instruction above

# APIs
# googlebooks api: https://www.googleapis.com/books/v1/volumes?q=isbn:0-444-82409-x
# openlibrary api: https://openlibrary.org/isbn/9781119284239.json
