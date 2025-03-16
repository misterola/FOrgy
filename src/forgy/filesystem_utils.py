# This module contains functions to carryout operations on files and directories
import os
from pathlib import Path
import shutil


def count_files_in_directory(directory):
    """This function takes a directory and counts the files within the directory.

    The counting will be done using the os.scandir method which tend to be more efficient.
    Files contained in folders in the entered directory are not counted.

    """
    file_count = sum(1 for entry in os.scandir(directory) if entry.is_file())
    return file_count


def count_files_in_tree(directory):
    """Function to count files in a directory containing other directories.
    This will be helpful if the folder containing PDF books contain many other
    folders and files. This function will help set the progress stats while
    a separate function will help with transversing directory tree

    This function returns total number of files and directories contained in a
    specified directory (excluding the supplied directory).
    """
    # Initialize directory, sub_directory, and files counters
    n_directories = 0
    n_files = 0
    for root, directories, files in os.walk(directory):
        n_directories = n_directories + len(directories)
        n_files = n_files + len(files)
        print(f"""
        Root: {root}
        Dirs: {directories}
        Files:
        {files}""")
    return n_directories, n_files

# print(count_files_in_directory(r"C:\Users\Ola\Desktop\ubooks_mod"))


def move_folders(source_dir, destination_dir):

    """This program takes a source folder and moves every sub_folder into
    another directory.

    The non_directory files in the destination_dir is not moved.
    However, files in subdirectories are moved with their parents
    """
    # Check if source and destination directories exist
    src_dir = Path(source_dir)
    dst_dir = Path(destination_dir)
    if not src_dir.exists():
        print(f"Source directory '{src_dir}' does not exist.")
        return

    if not dst_dir.exists():
        print(f"Destination directory '{dst_dir}' does not exist.")
        return

    # Loop through the source directory using os.scandir()
    with os.scandir(src_dir) as entries:
        for entry in entries:
            if entry.is_dir():  # Check if the entry is a directory
                src_path = entry.path
                # dst_path = os.path.join(dst_dir, entry.name)
                dst_path = dst_dir/f"{entry.name}"
                try:
                    # Move the directory to the destination
                    shutil.move(src_path, dst_path)
                    print(f"Moved directory: {src_path} to {dst_path}")
                except shutil.Error as e:
                    print(f"Error '{e}' occured")
                    pass
                except Exception as e:
                    print(f"Error moving {src_path}: {e}")
            else:
                print(f"Skipped non-directory item: {entry.path}")
    return None


def get_files_from_tree(source_directory, destination_directory, extension='pdf', move=False):
    """Function moves all files in a directory which containing other directories and files into another directory.

    In this case, the directories are left behind with empty files as all files are moved to new destination.

    If move=False, files are copied from sources to destination, else files are moved. copy is the default behavior
    """
    # Check if source and destination directories exist
    src_dir = Path(source_directory)
    dst_dir = Path(destination_directory)

    if not src_dir.exists():
        print(f"Source directory '{src_dir}' does not exist.")
        return None

    if not dst_dir.exists():
        print(f"Destination directory '{dst_dir}' does not exist.")
        return None

    for root, directories, files in os.walk(src_dir):
        root = Path(root)
        print(f"""
        root: {root}
        directories: {directories}
        files: {files}""")

        for file in files:
            file_path = root/file
            if file_path.suffix == f".{extension}":
                src_file = root/file
                dst_file = dst_dir/file

                # Check destination for presence of file
                if dst_file.exists():
                    print(f"File {file} already exists in destination directory.")
                    continue
                try:
                    if not move:
                        shutil.copy(src_file, dst_file)
                    else:
                        shutil.move(src_file, dst_file)
                    print(f"{file} moved from {src_file} to {dst_file}")
                except Exception as e:
                    print(f"Encountered error {e} while moving file {file}")
                    continue
            else:
                print(f"File '{file_path.name}' is not a .{extension} file")
                continue
    return None


def get_files_from_directories(directory_list, destination, extension='pdf', move=False):
    """Function to copy or move .pdf files in a list of directories to a destination. copy is the default"""
    # Check if every directory in list is valid
    for directory in directory_list:
        if not Path(directory).is_dir():
            print(f"{directory} in directory_list is not a directory")
            return None

    # Check if the provided destination is a valid directory
    if not Path(destination).is_dir():
        print(f"{destination} is not a directory")
        return None
    
    # Iterate through directories in list
    for directory in directory_list:    
        dir_path = Path(directory)
        files_moved = False
        files_copied = False

        # Iterate through files inside directory
        for file in dir_path.iterdir():
            extension_match = extension.lower()
            # Ensure file is a valid file and it ends with extension name
            if file.is_file() and file.name.lower().endswith(f".{extension_match}"):
                src = dir_path/file.name
                dst = Path(destination)/file.name
                try:
                    if not move:
                        shutil.copy(src, dst)
                        print(f"File '{src}' copied to '{dst}'")
                        files_copied = True
                    else:    
                        shutil.move(src, dst)
                        print(f"File '{src}' moved to '{dst}'")
                        files_moved = True
                except OSError as e:
                    print(f"Error {e} encountered when {src} was being moved")
                    continue
        # Print success message whenever all files in one directory have been moved/copied to destination
        if files_moved:
            print(f"All files in {directory} moved to {destination} successfully.")
        elif files_copied:
            print(f"All files in {directory} copied to {destination} successfully.")
        else:
            print(f"No .{extension} files in directory {directory}.")

    return None
    
    
            

def organize_files_in_directory(source_directory, destination_directory):
    """This function takes a directory (without a subdir) and create a folder for each unique filetype.

    A set containing unique file extensions in folder will first be created,
    and a folder with the extension name is created. The extension containing FOrgy
    files will be the source directory for FOrgy.


    Enable user to specify a folder or list of folders containing messy files to be organized
    and a new organized folder is created in a folder of choice. This util creates a
    separate folder   for each unique file type. The folder
    containing PDF files can be used as input for FOrgy   isbn_metadata utils.

    Future modification: allow user to specify walk or scan to properly handle children files in folders.
    """

    #Confirm if the source (source_directory) and destination(destination_directory) exist
    src_dir = Path(source_directory)
    dst_dir = Path(destination_directory)
    
    if not src_dir.exists():
        print("The given source directory does not exist")
        return None

    if not dst_dir.exists():
        print("The given destination directory does not exist")
        return None

    # Create organized_directory folder and its parent(if it doesn't yet exist)
    # to house all organized folders
    organized_path = dst_dir/"organized_directory"
    if not organized_path.exists():
        os.makedirs(organized_path)

    # Initialize an extension set to contain all unique file extensions in the directory
    extension_set = set()

    # Obtain all unique extensions by iterating over directory entries
    for file in os.scandir(src_dir):
        # the .name attribute accesses the file name
        # First get file extension
        if file.is_file():
            _, extensn = os.path.splitext(file.name)
            extension_set.add(extensn)
    # print(extension_set)

    # Create folders to contain each unique file extension
    for ext in extension_set:
        # eliminate the leading dot in extension name
        folder_name = ext.lstrip(".")
        folder_path = organized_path / folder_name

        # Confirm if exension folder exist and if it doesn't, make a new one
        if not folder_path.exists():
            os.makedirs(folder_path)
        

        # Move files with each unique extension to the created extension folder
        # Enable modification of this part using walk=False|True to touch subfolders or not
        for file in os.scandir(src_dir):
            #file_path = src_dir/f"{file.name}"

            # Only consider files in this operation
            if file.is_file():

                # Get the file extension
                _, extension = os.path.splitext(file.name)

                # Move file to directories matching file's extension name
                if extension.lstrip(".") == folder_name:
                    try:
                        shutil.move(file.path, folder_path / file.name)
                    except OSError as e:
                        print(f"Error {e} occured on {file.name}")
                        continue
                    except Exception as e:
                        print(f"Error '{e}' occured on {file.name}")
                        continue
    return extension_set


def delete_files_in_directory(directory):
    """Delete only files from directory.

    shutil.rmtree(directory) deletes all content of directory which is not needed here
    """
    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file():
                    os.unlink(entry.path)
        print(f"Files in {directory} deleted successfully")
    except OSError as e:
        print(f"Error {e} occured")

# To test
# print(organize_files_in_directory(r"C:\Users\Ola\Desktop\ubooks_keji", r"C:\Users\Ola\Desktop"))
    

if 'name' == '__main__':
    print(count_files_in_directory(r"C:\Users\Ola\Desktop\ubooks"))
    
