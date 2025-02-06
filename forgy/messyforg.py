# main
from pathlib import Path
import shutil
import os
import time
import requests
import random

from isbn_regex import (
    isbn_pattern,
    format_isbn,
    is_isbn_in_db,
)
from text_extraction import extract_text
from metadata_search import (
    headers,
    get_metadata_google,
    get_metadata_openlibrary,
    get_metadata_from_api,
    modify_title,
)
from database import (
    create_table,
    create_library_db,
    add_metadata_to_table,
    view_database_table,
    delete_table,
    titles_in_db,
)

home = Path.home()
# Enable user to add more sources (up to 5) and make user specify location
# for messyforg folder
src = home / "Desktop" / "Projects" / "Forgy" / "ubooks"

dst = home / "Desktop" / "Projects" / "Forgy" / "ubooks_copy"

# Copy source directory and rename as 'ubooks_copy'
try:
    shutil.copytree(src, dst)
    print("Source directory copied successfully")
except FileExistsError:
    print("Directory copied already!")


# Create 'library.db' or connect to it if it already exists
create_library_db(
    home / "Desktop" / "Projects" / "Forgy" / "forgy" / "library.db"
)

# Delete Books table if it exists in database
delete_table(
    home / "Desktop" / "Projects" / "Forgy" / "forgy" / "library.db", "Books"
)

# Create table 'Books' in library.db
create_table(
    home / "Desktop" / "Projects" / "Forgy" / "forgy" / "library.db", "Books"
)


missing_metadata = home / "Desktop" / "Projects" / "Forgy" / "missing_metadata"
missing_metadata.mkdir(exist_ok=True)

missing_isbn_dir = home / "Desktop" / "Projects" / "Forgy" / "missing_isbn"
missing_isbn_dir.mkdir(exist_ok=True)

# Initialize raw_files_set to store path to raw files iterated over and initialize
# renamed_files_set to store path to renamed file. This ensures that no file is
# iterated over twice and metadata is not fetched twice.
raw_files_set = set()
renamed_files_set = set()
title_set = set()

# Duration dictionary stores how long it takes for operation on each file
# This will help in estimating total time required to complete file organizing
# in the process_statistics module
duration_dictionary = {}

def process_duration(start_time):
    """Function to calculate duration of operation for each file.

    Start time is predefined at the start of the loop that goes through file.
    """
    start_time = start_time
    end_time = time.time()
    duration = end_time - start_time
    return f"{duration:.3f}"

def save_process_duration(file_name, process_duration, duration_dictionary):
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
    """Function to choose an api(key) and its associated calling function
    (value) from a list of dictionaries containing two apis.
    
    The format of the api_list containing dictionaries is:
    # [{"google":get_metadata_google}, {"openlibrary": get_metadata_openlibrary}]
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


# Iterate through each file in the new 'ubooks_copy' directory
# and extract text in first 20 pages of each file
for file in os.scandir(dst):    # noqa: C901 # A complex loop_McCabe 30
    start_time = time.time()
    
    file_src = home / "Desktop" / "Projects" / "Forgy" / "ubooks_copy" / file

    # If file has been iterated over or renamed, skip to next iteration
    if (file in raw_files_set) or (file in renamed_files_set):
        continue

    # Initialize values of metadata parameters and assign to values

    values = ""
    
    # Initialize list of valid isbns
    valid_isbn = []

    if not file.name.startswith(".") and file.is_file():
        pdf_path = dst / file
        extracted_text = extract_text(pdf_path)

        # Use regex to match isbn in extracted text, into matched_isbn list
        matched_isbn = []
        matched_regex = isbn_pattern.findall(extracted_text)
        matched_isbn.append(matched_regex)
        valid_isbn = format_isbn(matched_isbn)

        # Add all in valid_isbn list to a set of valid isbns
        # add_isbn_to_set(valid_isbn, valid_isbn_set)
        print(valid_isbn)

        # Extracted_text_list = extracted_text.split(' ')

        # for files with missing isbn, save extracted text into file, and move file to missing_isbn directory
        if (missing_isbn_dir.exists() and (not valid_isbn)):
            shutil.move(file_src, missing_isbn_dir)
            # For files with missing isbn, generate (empty) text files to ascertain problem
            # Note on handling files in missing_isbn folder: use another set of text extractors (e.g.PyMupdf),
            # use OCR engine (e.g. tesseract) to extract text, fetch metadata from book using the current
            # pdf extractor, or generate error messages/logs if all else fails.
            # with open(f"home/'Desktop'/'Forgy'/'{pdf_path.stem}.txt'", 'a') as page_new:
            with open(f"{pdf_path.stem}.txt", "a") as page_new:
                try:
                    page_new.write(extracted_text)
                except (FileNotFoundError, UnicodeEncodeError):
                    process_duration(start_time)
                    continue
        # Move to next book if its isbn has been previously extracted (compare with ref_isbn_set)
        if is_isbn_in_db(
            home / "Desktop" / "Projects" / "Forgy" / "forgy" / "library.db",
            "Books",
            valid_isbn,
        ):
            process_duration(start_time)
            continue

        # Use each isbn in int_isbn_list to search on openlibrary api and googlebookapi
        # for book metadata and download in json
        # Repeat same for every isbn in list. If metadata not found, print error message.
        for isbn in valid_isbn:

            try:
                # Select api randomly to avoid overworking any of the apis
                api_list = [
                    {"google":get_metadata_google},
                    {"openlibrary": get_metadata_openlibrary},
                ]

                (api1_dict,
                 api1_dict_key,
                 api2_dict,
                 api2_dict_key)  = choose_random_api(api_list)

                if api1_dict_key == "google":
                    values = get_metadata_from_api(api1_dict,
                                                   api1_dict_key,
                                                   api2_dict,
                                                   api2_dict_key,
                                                   isbn,
                                                   file,
                                                   headers,
                                                   file_src,
                                                   missing_metadata)
                    raw_files_set.add(file)
                    time.sleep(5)
                    process_duration(start_time)
                    continue

                else:
                    values = get_metadata_from_api(api2_dict,
                                                   api2_dict_key,
                                                   api1_dict,
                                                   api1_dict_key,
                                                   isbn,
                                                   file,
                                                   headers,
                                                   file_src,
                                                   missing_metadata)
                    raw_files_set.add(file)
                    time.sleep(5)
                    process_duration(start_time)
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
                    "Request ConnectionError. Check your internet connection", end="\n"
                )
                continue
            except requests.ReadTimeout:  # noqa: F821
                print("ReadTimeoutError")
                continue
            except requests.RequestException as e:
                print(f"Error '{e}' occured")

    # Assign retrieved metadata to tuple value for easy addition to database.
    # This updates the initialized values
##    values = (
##        f"{title}",
##        f"{subtitle}",
##        f"{full_title}",
##        f"{date_of_publication}",
##        f"{publisher}",
##        f"{authors}",
##        f"{str(page_count)}",
##        f"{isbn_10}",
##        f"{isbn_13}",
##        f"{ref_isbn}",
##        f"{source}",
##        f"{float(file_size):.2f}",
##    )

    print(values)

    db_titles = titles_in_db (
        home / "Desktop" / "Projects" / "Forgy" / "forgy" / "library.db", "Books"
    )

    if values and modify_title(f"{values[0]}.pdf") in db_titles:
        process_duration(start_time)
        continue
            

    # ........#
    # For file with retrieved metadata, rename and do not move
    if (
        missing_metadata.exists()
        and valid_isbn
        and values != ""
        and len(list(set(values[0:6]))) >= 2
    ):

        # Default is 4 out of 6
        # Rename file in its original ubooks directory
        old_file_name = pdf_path
        dst_dir = dst
        new_file_name = modify_title(f"{values[0]}.pdf")
        new_file_path = os.path.join(dst_dir, new_file_name)

        try:
            os.rename(pdf_path, new_file_path)
        except FileNotFoundError:
            pass
        # Device how to handle duplicates by attacching time to file name
        except FileExistsError:
            pass

        # Add retrieved metadata to database
        add_metadata_to_table(
            home / "Desktop" / "Projects" / "Forgy" / "forgy" / "library.db",
            "Books",
            values,
        )

        renamed_files_set.add(new_file_name)
        title_set.add(values[0])

        view_database_table(
            home / "Desktop" / "Projects" / "Forgy" / "forgy" / "library.db", "Books"
        )

        # print(f'raw_files_set\n_____________________\n{raw_files_set}')
        # print(f'renamed_files_set\n_____________________\n{raw_files_set}')

    # For files with missing missing_metadata, move file to missing_isbn directory
    else:
        # missing_metadata = home/"Desktop"/"MessyFOrg"/"missing_metadata"
        # missing_metadata.mkdir(exist_ok=True)
        # file_src = home / "Desktop" / "Projects" / "Forgy" / "ubooks_copy" / file
        try:
            shutil.move(file_src, missing_metadata)
            # FileNotFoundError raised if file has a missing ISBN and is already moved to
            # missing_isbn directory. skip this whole process for file that raises this error
        except FileNotFoundError:
            pass
        # if there is no internet connection, don't move file
        except requests.exceptions.ConnectionError:
            print("Request ConnectionError. Check your internet connection")
            pass


# .......#
# TODO: rename book with format here
# new_dst = dst/f"{full_title}, {authors} {date_of_publication}.{publisher}.pdf"

# TODO: Separate out my user key and browser header and import them
# into the program and set .gitignore for them
# DONE

# TODO: Enable user to specify if to delete content of database or not DONE

# TODO: For every extracted isbn, check database ref_isbn to ensure that is isn't there. DONE

# TODO: Redesign project structure, set-up GitHub repo and select license (AGPL) DONE

# TODO: rename book using name from metadata if metadata retrieval DONE
# from ISBN is successful

# TODO: Lint code with Flake8, Pylint, and/or ruff. DONE

# TODO: Configure and package FOrgy

# TODO: Add metadata retrieval date to database columnss

# TODO: organize program, add more modules: isbn_api, pdf_to_text, messyforgs, regex, tests, stats
# file_system_utils (file mgt - save, rename, delete, copy), database, single_metadata_search,
# header & api key, logging, cache, temp, archive, usage stats, documentation, example,
# CLI, Tkinter GUI, tests, CI/CD, no_isbn_metadata_search, examples, database, multiprocessing
# via asynchronous performance, threading, or concurrency in the most efficient way

# TODO: Enable user to supply list of directories containing PDF files to be operated upon and '*.pdf'
# extension is matched to autogenerate local copy for messyforg

# TODO: Enable user to specify a folder or list of folders containing messy files to be organized and a new
# organized folder is created in a folder of choice. This util creates a separate folder for each unique file
# type. The folder containing PDF files can be used as input for FOrgy isbn_metadata utils.

# TODO: Design a beautiful and intuitive GUI interface for app (commandline interface should also be embedded)

# TODO: Design beautiful and intuitive CLI for app

# TODO: Add more metadata sources (Amazon, goodreads, worldcat, library of congress, librarything, thrift books, ebay)

# TODO: Add grouping files in given directory based on format before carying out operation
# on the pdfs of journal articles and books

# TODO: For books with missing ISBN in preliminary pages, check last ten pages. This should
# be done on individual book (publishers like pack publisher advert books in last pages
# of their books and this means there are unrelated isbns at back of the books.

# TODO: Create a directory of 10 creative commons-licensed ebooks and place in tests folder for the tests

# TODO: Enable user to add book details manually or by supplying some title and isbn to aid to aid search
# (perhaps another module named single_isbn_api)

# TODO: Test the APIs and user internet connection before beginning operation, and automatically get header
# settings for user browser from reliable source and parse into format needed by Forgy

# TODO: Download 10 open source ebooks and place in a folder so users can practice with and test API with

# TODO: Automatically cache .json() downloaded by API into a redis database as a first search point
# before online API bandwith

# TODO: If file already exists, ensure timestamp is added to a filename before adding to database

# TODO: Extract firstpage of book, save as jpg, standardize size for thumbnail, and treat as cover image

# TODO: Add timestamp to book metadata (or database)

# TODO: Check database for book ref_isbn before going online to search for it. This will ensure program can
# continue from where it stops without cache DONE

# TODO: Create the first full-featured GUI with Tkinter

# TODO: Enable user to enter title and author and automatically fetch book metadata online 

# TODO: add OCR engine e.g. pytesseract (dependency difficult to install),
# EasyOCR, PyOCR, Textract for text extraction if empty text extracted by pypdf

# TODO: release version 0.1.0 of FOrgy version (has a gui with cli but not the journal article doi search)

# TODO: Add journal article DOI tools


# OBSERVED REASONS FOR MISSING ISBN IN EXTRACTED TEXT
# isbn pattern not matching: read isbn standard and write a better regex
# text not having any isbn: follow instruction above 'with statement'
# text cannot be extracted: use OCR
# incomplete isbn digit (e.g. 9 digits): follow instruction above

# APIs
# googlebooks api: https://www.googleapis.com/books/v1/volumes?q=isbn:0-444-82409-x
# openlibrary api: https://openlibrary.org/isbn/9781119284239.json
