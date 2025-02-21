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

from process_stats import (
    number_of_dir_files,
    number_of_processed_files,
    total_time_remaining,
    number_of_database_files,
    percent_api_utilization,
    file_processing_efficiency,
)

from filesystem_utils import count_files_in_directory

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

database = (
    home
    / "Desktop"
    / "Projects"
    / "Forgy"
    / "forgy"
    / "library.db"
)
create_library_db(database)

# Delete Books table if it exists in database
delete_table(database, "Books")

# Create table 'Books' in library.db
create_table(database, "Books")

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

# Duration dictionary stores how long it takes for operation on
# each file.
# This will help in estimating total time required to complete file
# organizing in the process_statistics module
duration_dictionary = {}


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
    duration_dictionary[file_name.name] = process_duration
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


# Iterate through each file in the new 'ubooks_copy' directory
# and extract text in first 20 pages of each file
for file in os.scandir(dst):    # noqa: C901 # A complex loop_McCabe 30

    # Take process statistics
    current_file = modify_title(file.name)
    print(f"Current file: {current_file}")

    total_no_of_files = count_files_in_directory(src)

    no_of_processed = number_of_processed_files(
        src,
        database,
        "Books",
        missing_isbn_dir,
        missing_metadata
    )
    print(f"Progress: file {no_of_processed} of {total_no_of_files}")

    percentage_completion = no_of_processed/total_no_of_files*100
    print(f"Percentage completion: {percentage_completion:.2f}% DONE")

    no_of_database_files = number_of_database_files(database, "Books")

    time_remaining = total_time_remaining(
        duration_dictionary,
        src,
        database,
        "Books",
        no_of_database_files,
        missing_isbn_dir,
        missing_metadata
    )
    if time_remaining < 60:
        print(f"Total time remaining: {time_remaining:.2f} minutes")
    else:
        print(f"Total time remaining: {time_remaining:.2f} hours")
    (percent_google_api,
     percent_openlibrary_api) = percent_api_utilization(database, "Books")
    print(f"API utilization: {percent_google_api:.2f}% Google, {percent_openlibrary_api:.2f}% Openlibrary")

    process_efficiency = file_processing_efficiency(src, database, "Books", missing_isbn_dir)
    print(f"Process efficiency: {process_efficiency:.2f}%")

    n_missing_isbn = number_of_dir_files(missing_isbn_dir)
    n_missing_metadata = number_of_dir_files(missing_metadata)
    print(
        f"""Process summary: {no_of_database_files} files renamed or added to DB, \
{n_missing_isbn} files with missing ISBN, {n_missing_metadata} files with missing metadata"""
    )

    start_time = time.time()

    file_src = (
        home
        / "Desktop"
        / "Projects"
        / "Forgy"
        / "ubooks_copy"
        / file
    )

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

        # For files with missing isbn, save extracted text into file,
        # and move file to missing_isbn directory
        if (missing_isbn_dir.exists() and (not valid_isbn)):
            shutil.move(file_src, missing_isbn_dir)
            # For files with missing isbn, generate (empty) text files
            # to ascertain problem
            # with open(
            # f"home/'Desktop'/'Forgy'/'{pdf_path.stem}.txt'", 'a'
            # ) as page_new:
            with open(f"{pdf_path.stem}.txt", "a") as page_new:
                try:
                    page_new.write(extracted_text)
                except (FileNotFoundError, UnicodeEncodeError):
                    process_duration_sec = process_duration(start_time)
                    save_process_duration(file,
                                          process_duration_sec,
                                          duration_dictionary)
                    print(duration_dictionary)
                    continue
        # Move to next book if its isbn has been previously extracted
        # (compare with ref_isbn_set)
        if is_isbn_in_db(
            home
            / "Desktop"
            / "Projects"
            / "Forgy"
            / "forgy"
            / "library.db",
            "Books",
            valid_isbn,
        ):
            process_duration_sec = process_duration(start_time)
            save_process_duration(file,
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
                    process_duration_sec = process_duration(start_time)
                    save_process_duration(file,
                                          process_duration_sec,
                                          duration_dictionary)
                    print(duration_dictionary)
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
                    process_duration_sec = process_duration(start_time)
                    save_process_duration(file,
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
    db_titles = titles_in_db(
        home
        / "Desktop"
        / "Projects"
        / "Forgy"
        / "forgy"
        / "library.db",
        "Books"
    )

    # Check if the metadata tuple (i.e. values) is not empty
    # and title is already in database. If that is the case,
    # skip to next iteration
    if values and modify_title(f"{values[0]}.pdf") in db_titles:
        process_duration_sec = process_duration(start_time)
        save_process_duration(file,
                              process_duration_sec,
                              duration_dictionary)
        print(duration_dictionary)
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
            home
            / "Desktop"
            / "Projects"
            / "Forgy"
            / "forgy"
            / "library.db",
            "Books",
            values,
        )

        # Add the name of renamed book to renamed_files_set
        # Add the title of book to title_set...both defined earlier
        renamed_files_set.add(new_file_name)
        title_set.add(values[0])

        view_database_table(
            home
            / "Desktop"
            / "Projects"
            / "Forgy"
            / "forgy"
            / "library.db", "Books"
        )

    # For files with missing missing_metadata, move file to
    # missing_isbn directory
    else:
        try:
            shutil.move(file_src, missing_metadata)
            # FileNotFoundError raised if file has a missing ISBN and is already
            # moved to missing_isbn directory. skip this whole process for file
            # that raises this error
        except FileNotFoundError:
            pass
        # if there is no internet connection, don't move file
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
