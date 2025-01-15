# Track: Total number of files, number of files with missing isbn,
# number of files with missing metadata, number of files renamed,
# number of files added to database (metadata found), no of files remaining,
# api utilization (%google, %openlibrary), efficiency of conversion
# equals sno of saved books/total no of files
# time remaining estmated base on average time per file so far
# % done and % remaining
# format to have a pretty display

"""
=====================================================\n
                FOrgy Process Statistics\n
=====================================================\n
Total number of files: {total_no_of_ubook_files}\n
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


print(f"""
====================================================
              FOrgy Process Statistics        
====================================================
 Progress: file {n} of {m}  # n is no_of_processed_file+1, m is total_number_of_files

 Total number of files: {total_no_of_ubook_files}

 Number of processed files: {no_of_processed_files}

 Number of files added to database/renamed: {no_of_files_added_to_database}

 API utilization (%): {percent_api_utilization}                             
                                                     
 Process efficiency: {efficiency_of_file_processing} 

 Number of files remaining(unprocessed): {total_number_of_unprocessed_files}
                                                      
 Time remaining: {time_remaining}                     
                                                                                                        
 Number of file with missing ISBN: {no_of_files_with_missing_isbn}   
                                                    
 Number of file with missing metadata: {no_of_files_with_missing_metadata}                                             
=====================================================
""")


# no_of_files_processed = no_of_database_files + no_of_missing_isbn +\
# + no_of_missing_metadata


def number_of_dir_files(directory):
    """Function to count the number of files in a directory.

    The function is used to estimate total number of files,
    no of files with missing isbn, number of files with missing
    metadata, number of files renamed (metadata found)
    """
    pass


def number_of_database_files(database, table):
    """Function to count number of books added to database.

    This represents the number of books whose metadata was
    successfully retrieved from the API.
    """
    pass


def number_of_files_remaining(dir):
    """"Function to count the number of unprocessed files in directory.

    This equals (Initial total no of ubooks files - no of files processed)

    """
    pass


def percent_api_utilization(database, table, column):
    """Function to estimate the percentage of metadata retrieved from each
    source.

    The estimate is done by counting data from Books database source column.
    And estimating %google and %openlibraryapi.
    """
    pass


def efficiency_of_file_processing(number_of_processed_files, total_number_of_files):
    """Estimates what percentage of total number of books, excluding those with missing ISBN

    This equals [number_of_database_files]/[total_number_of_files - n_files_with_missing_isbn]
    """
    pass


def percent_completion(foo):
    """Shows how many percent of files have been processes vs how many remaining.
    
    number_of_files_processed/initial_ubooks_total_number_of_files

    """
    pass


def average_time_per_file():
    """Measures average time it takes to process a file.

    Checks time at the beginning of process for a file and at the end of a process for file.
    Time per file = start time - end time
    average time per file = (total time taken so far/total no of files processed)
    pass
    """


 def total_time_remaining(foo):
    """Estimates how many hours left for operating on all files.

    Estimate using: number of file remaining*average processing time per file
    This is estimated using

    time_rem = (initial_no_of_ubook_files-no_of_processed_files)*average_time_per_file
    """
    pass

