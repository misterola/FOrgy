# This module contains functions to carryout operations on files and directories
import os
from pathlib import Path
import shutil


def count_files_in_directory(directory):
    """This function takes a directory and counts the files within the directory.

    The counting will be done using the os.scandir method which tend to be more efficient.

    """
    file_count = sum(1 for entry in os.scandir(directory) if entry.is_file())
    return file_count


def count_files_in_tree(directory):
    """Function to count files in a directory containing other directories.
    This will be helpful if the folder containing PDF books contain many other
    folders and files. This function will help set the progress stats while
    a separate function will help with transversing directory tree

    This function returns total number of files and directories contained in a
    specified root directory.
    """
    # Initialize directory, sub_directory, and files counters
    n_directories = 0
    n_files = 0
    for root, directories, files in os.walk(directory):
        n_directories = n_directories + len(directories)
        n_files = n_files + len(files)
##        print(f"""
##        Root: {root}
##        Dirs: {directories}
##        Files:
##        {files}""")
    return n_directories, n_files

# print(count_files_in_directory(r"C:\Users\Ola\Desktop\ubooks_mod"))        

def organize_files_in_directory(src_directory, dest_directory):
    """This function takes a directory (without a subdir) and create a folder for each unique filetype.

    A set containing unique file extensions in folder will first be created,
    and a folder with the extension name is created. The extension containing FOrgy
    files will be the source directory for FOrgy.
    """

    #Confirm if the source (src_directory) and destination(dest_directory) exist
    if (
        not os.path.exists(src_directory)
        or (not os.path.exists(dest_directory))
    ):
        print("The given source or destination directories do not exist")
        return None

    
    # Initialize an extension set to contain all unique file extensions in directory
    extension_set = set()

    # Create organized_directory folder (if it doesn't yet exist)
    # to house all organized folders
    organized_path = os.path.join(dest_directory, "organized_directory")
    if not os.path.exists(organized_path):
        os.makedirs(organized_path)

    # Obtain all unique extensions by iterating over directory entries
    for file in os.scandir(src_directory):
        _, extensn = os.path.splitext(file)
        extension_set.add(extensn)
    # print(extension_set)

    # Create folders to contain each unique file extension
    for ext in extension_set:
        folder_name = ext.replace(".", "")
        folder_path = os.path.join(organized_path, folder_name)

        # Confirm if exension folder exist and if it doesn't, make a new one
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        

        # Move files with each extension to the created extension folder
        for file in os.scandir(src_directory):
            file_path = os.path.join(src_directory, file)

            # Exclude directories from this operation
            if os.path.isdir(file_path):
                continue

            # Get the extension for file
            _, extension = os.path.splitext(file)
            
            if extension.replace(".", "") == folder_name:
                try:
                    shutil.move(file_path, folder_path)
                except OSError as e:
                    print(f"Error {e} encountered")
                    continue
            
    return extension_set

print(organize_files_in_directory(r"C:\Users\Ola\Desktop\ubooks", r"C:\Users\Ola\Desktop"))
    
        
##        
##    file_set = set()
##    for _, _, files in os.walk(dir):
##        for file in files:
##            file_set.append(file)
##        
        

    # pass
    




if 'name' == '__main__':
    print(count_files_in_directory(r"C:\Users\Ola\Desktop\ubooks"))
    
