# This module tracks or estimates process statistics, especially:
# total number of files,
# number of files with missing isbn,
# number of files with missing metadata,
# number of files renamed or added to database(metadata found),
# number of files remaining,
# api utilization (%google, %openlibrary),
# efficiency of process (successful operations as % of total no of files,
# excl. those files with missing ISBN)
# time remaining estmated base on average time per file so far
# format to have a pretty display
import textwrap
import os
from .filesystem_utils import (
    count_files_in_directory,
)

from .database import (
    titles_in_db,
    api_utilization,
)


def number_of_dir_files(directory):
    """Function to count the number of files  in a directory.

    The function is used to estimate total number of files,
    no of files with missing isbn, number of files with missing
    metadata, number of files renamed (metadata found)
    """

    return count_files_in_directory(directory)


def number_of_database_files(database, table):
    """Function to count number of books added to database.

    This represents the number of books whose metadata was
    successfully retrieved from the API.
    """
    return len(titles_in_db(database, table))


def number_of_processed_files(source_dir,
                              database,
                              table,
                              missing_isbn_dir,
                              missing_metadata_dir):
    # initial_file_count = number_of_dir_files(source_dir)

    no_of_files_in_database = number_of_database_files(database, table)

    no_of_missing_isbn = number_of_dir_files(missing_isbn_dir)

    no_of_missing_metadata = number_of_dir_files(missing_metadata_dir)

    no_of_processed_files = (no_of_files_in_database
                             + no_of_missing_isbn
                             + no_of_missing_metadata)

    return no_of_processed_files


def _number_of_files_remaining(source_dir,
                               database,
                               table,
                               no_of_database_files,
                               missing_isbn_dir,
                               missing_metadata_dir):
    """"Function to count the number of unprocessed files in directory.

    This equals (Initial total no of ubooks files - no of files processed)

    """
    initial_file_count = number_of_dir_files(source_dir)

    no_of_processed_files = number_of_processed_files(source_dir,
                                                      database,
                                                      table,
                                                      missing_isbn_dir,
                                                      missing_metadata_dir)

    no_of_files_remaining = initial_file_count - no_of_processed_files

    return no_of_files_remaining


def percent_api_utilization(database, table):
    """Function to estimate the percentage of metadata retrieved from each
    source.

    The estimate is done by counting data from Books database source column.
    And estimating %google and %openlibraryapi.
    """
    api_list = api_utilization(database, table)

    # n_successful_api_calls = len(api_list)

    google_list = []

    openlibrary_list = []

    for num in range(len(api_list)):
        if api_list[num] == 'www.google.com':
            google_list.append('g')
        else:
            openlibrary_list.append('o')
    try:
        percent_google_api = len(google_list)/len(api_list)*100
    except ZeroDivisionError:
        percent_google_api = 0

    try:
        percent_openlibrary_api = len(openlibrary_list)/len(api_list)*100
    except ZeroDivisionError:
        percent_openlibrary_api = 0

    return (percent_google_api, percent_openlibrary_api)


def file_processing_efficiency(source_dir,
                               database,
                               table, missing_isbn_dir):
    """Estimates what percentage of total number of books, excluding those with missing ISBN,
    whose metadata have been added to the Books table in database.

    This equals [number_of_database_files]/[total_number_of_files - n_files_with_missing_isbn]
    """
    no_of_database_files = number_of_database_files(database, table)

    initial_file_count = number_of_dir_files(source_dir)

    no_of_missing_isbn = number_of_dir_files(missing_isbn_dir)

    try:
        process_efficiency = no_of_database_files/(initial_file_count - no_of_missing_isbn)*100
    except ZeroDivisionError:
        process_efficiency = 0

    return process_efficiency


def _average_time_per_file(duration_dict):
    """Measures average time it takes to process a file.

    Checks time at the beginning of process for a file and at the end of a process for file.
    Time per file = start time - end time
    average time per file = (total time taken so far/total no of files processed)

    pass
    """
    total_time_taken = 0

    for _, value in duration_dict.items():
        total_time_taken += float(value)

    try:
        avg_time_per_file = total_time_taken/len(duration_dict)
    except ZeroDivisionError:
        avg_time_per_file = 0

    return avg_time_per_file


def total_time_remaining(duration_dict,
                         source_dir,
                         database,
                         table,
                         no_of_database_files,
                         missing_isbn_dir,
                         missing_metadata_dir):
    """Estimates how many hours left for operating on all files.

    Estimate using: number of file remaining*average processing time per file
    This is estimated using

    time_rem = (initial_no_of_ubook_files-no_of_processed_files)*average_time_per_file
    """
    avg_time_per_file = _average_time_per_file(duration_dict)

    no_of_files_remaining = _number_of_files_remaining(source_dir,
                                                       database,
                                                       table,
                                                       no_of_database_files,
                                                       missing_isbn_dir,
                                                       missing_metadata_dir)

    time_remaining = avg_time_per_file * no_of_files_remaining/60

    # return time remaining in hours if it's greater than 60 minutes or in minutes if less
    if time_remaining < 60:
        return time_remaining
    else:
        return time_remaining/60


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
        user_pdfs_source,
        forgy_pdfs_copy,
        database_path,
        table,
        missing_isbn_path,
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

    total_no_of_files = count_files_in_directory(user_pdfs_source)

    no_of_processed = number_of_processed_files(
        user_pdfs_source,
        database_path,
        table,
        missing_isbn_path,
        missing_metadata
    )
    percentage_completion = no_of_processed/total_no_of_files*100
    no_of_database_files = number_of_database_files(database_path, table)

    time_remaining = total_time_remaining(
        duration_dictionary,
        user_pdfs_source,
        database_path,
        table,
        no_of_database_files,
        missing_isbn_path,
        missing_metadata
    )
    time_remaining = format_time_remaining(time_remaining)
    print(f"DB_TABLEEE: {table}")
    (percent_google_api,
     percent_openlibrary_api) = percent_api_utilization(database_path, table)

    process_efficiency = file_processing_efficiency(user_pdfs_source, database_path, table, missing_isbn_path)
    n_missing_isbn = number_of_dir_files(missing_isbn_path)
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


# Preferred format of process stats

"""
=====================================================
                FOrgy Process Statistics
=====================================================
Progress: file {n} of {m}  # n is no_of_processed_file+1, m is total_number_of_files
Current file: {file}
Total number of files: {total_no_of_ubook_files}
Time remaining: {time_remaining}\n
Number of processed files: {no_of_processed_files}\n
Number of files added to database/renamed: {no_of_files_added_to_database}\n
Number of file with missing ISBN: {no_of_files_with_missing_isbn}\n
Number of file with missing metadata: {no_of_files_with_missing_metadata}\n
Total number of files remaining(unprocessed): {total_number_of_unprocessed_files}\n
API utilization (%): {percent_api_utilization}\n
Process efficiency: {efficiency_of_file_processing}\n
=======================================================\n
"""
