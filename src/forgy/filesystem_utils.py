"""
This module contains functions to carryout basic
filesystem operations on files and directories in
all modules
"""

import os
from pathlib import Path
import shutil

from .logger import create_logger


logger = create_logger("filesystem_utils")


def count_files_in_directory(directory):
    """
    This function counts the files within a directory.

    Files contained in sub-folders in directory are not
    counted.
    """
    file_count = sum(
        1 for entry in os.scandir(directory) if entry.is_file()
    )

    return file_count


def count_files_in_tree(directory):
    """
    Function to count files in a directory containing other
    directories.

    This will serve if the folder containing PDF books contain
    many other sub-folders and files. The count_files_in_tree
    function will help set the progress stats while a separate
    function will help with transversing directory tree

    This function returns total number of files and directories
    contained in a specified directory (excluding the supplied
    directory).
    """
    n_directories = 0
    n_files = 0

    # Discard the root
    for _, directories, files in os.walk(directory):

        n_directories = n_directories + len(directories)

        n_files = n_files + len(files)

    return n_directories, n_files


def move_folders(source_dir, destination_dir):

    """
    This program takes a source folder and moves every
    sub_folder into another directory.

    The non_directory files in the source_dir is not moved.
    However, files in subdirectories are moved with their
    parents.
    """

    src_dir = Path(source_dir)

    dst_dir = Path(destination_dir)

    if not src_dir.exists():
        logger.warning(
            f"Source directory '{src_dir}' does not exist."
        )
        return

    if not dst_dir.exists():
        logger.warning(
            f"Destination directory '{dst_dir}' does not exist."
        )
        return

    with os.scandir(src_dir) as entries:
        for entry in entries:
            if entry.is_dir():
                src_path = entry.path
                dst_path = dst_dir/f"{entry.name}"
                try:
                    shutil.move(src_path, dst_path)
                    logger.info(
                        f"Moved directory: {src_path} to {dst_path}"
                    )
                except shutil.Error as e:
                    logger.exception(f"Error '{e}' occured")
                    pass
                except Exception as e:
                    logger.exception(f"Error moving {src_path}: {e}")
            else:
                logger.info(f"Skipped non-directory item: {entry.path}")
    return None


def copy_directory_contents(user_pdfs_source, forgy_pdfs_copy):
    """
    Function to copy content of user_pdfs_source directory
    into forgy_pdfs_copy
    """

    user_pdfs_source = Path(user_pdfs_source)
    forgy_pdfs_copy = Path(forgy_pdfs_copy)

    if not user_pdfs_source.is_dir():
        logger.warning(f"{user_pdfs_source} is not a directory")
        return
    if not forgy_pdfs_copy.is_dir():
        logger.warning(f"{forgy_pdfs_copy} is not a directory")
        return
    try:
        # FileExistsError will not be raised if content exists
        shutil.copytree(
            user_pdfs_source,
            forgy_pdfs_copy,
            dirs_exist_ok=True
        )
        logger.info("Source directory copied successfully")
    except Exception as e:
        logger.exception(f"Exception {e} raised")
        pass


def get_files_from_directory(  # noqa:C901
    source_directory,
    destination_directory,
    move=False,
    extension='pdf'
):
    """
    Function to copy or move files from source directory to
    destination directory.

    Does not copy or move if file already exists in destination.
    """

    if not Path(source_directory).is_dir():
        logger.warning(
            f"{source_directory} is not a valid directory"
        )
        return None

    if not Path(destination_directory).is_dir():
        logger.warning(
            f"{destination_directory} is not a valid directory"
        )
        return None

    source_directory = Path(source_directory)
    destination_directory = Path(destination_directory)

    with os.scandir(source_directory) as entries:
        for entry in entries:
            entry_name = entry.name
            source_path = entry.path
            if entry_name.endswith(f".{extension}"):
                if not move:
                    destination_path = destination_directory/entry_name
                    if destination_path.exists():
                        logger.info(
                            f"File {entry_name} already exists in \
destination {destination_directory}"
                        )
                        continue
                    try:
                        shutil.copy(source_path, destination_path)
                    except Exception as e:
                        logger.exception(f"Exception {e} encountered")
                        continue
                else:
                    destination_path = destination_directory/entry_name
                    if destination_path.exists():
                        logger.info(
                            f"File {entry_name} already exists in\
destination {destination_directory}"
                        )
                        continue
                    try:
                        shutil.move(source_path, destination_path)
                    except Exception as e:
                        logger.exception(f"Exception {e} encountered")
                        continue
            else:
                continue
    return None


def get_files_from_tree(
    source_directory,
    destination_directory,
    extension='pdf',
    move=False
):
    """
    Function copies or moves all files in a directory which
    containing other sub-directories and files into a
    different directory.

    In this case, the directories are left behind with empty files
    as all files within them are moved to a new destination.
    Existing files in destination are not copied

    If move=False, files are copied from sources to destination,
    else files are moved. copy is the default behavior
    """

    src_dir = Path(source_directory)
    dst_dir = Path(destination_directory)

    if not src_dir.exists():
        logger.warning(
            f"Source directory '{src_dir}' does not exist."
        )
        return None

    if not dst_dir.exists():
        logger.warning(
            f"Destination directory '{dst_dir}' does not exist."
        )
        return None

    for root, directories, files in os.walk(src_dir):
        root = Path(root)

        for file in files:
            file_path = root/file
            if file_path.suffix == f".{extension}":
                src_file = root/file
                dst_file = dst_dir/file

                if dst_file.exists():
                    logger.info(
                        f"File {file} already exists in destination \
{dst_dir}.")
                    continue
                try:
                    if not move:
                        shutil.copy(src_file, dst_file)
                    else:
                        shutil.move(src_file, dst_file)
                    logger.info(
                        f"{file} moved from {src_file} to {dst_file}"
                    )
                except Exception as e:
                    logger.exception(
                        f"Encountered error {e} while moving file {file}"
                    )
                    continue
            else:
                logger.info(
                    f"File '{file_path.name}' is not a .{extension} file"
                )
                continue
    return None


def get_files_from_directories(  # noqa: C901
    directory_list,
    destination,
    extension='pdf',
    move=False
):
    """
    Function to copy or move .pdf files in a list of directories
    to a destination.

    The default is copy, when move=False.
    """
    directory_list = [Path(directory) for directory in directory_list]

    for directory in directory_list:
        if not Path(directory).is_dir():
            logger.warning(
                f"{directory} in directory_list is not a directory"
            )
            return None

    if not Path(destination).is_dir():
        logger.warning(f"{destination} is not a directory")
        return None

    for directory in directory_list:
        dir_path = Path(directory)
        files_moved = False
        files_copied = False

        for file in dir_path.iterdir():
            extension_match = extension.lower()

            # Validity of file is established when its name ending
            # is same as the extension name
            if (
                file.is_file()
                and file.name.lower().endswith(f".{extension_match}")
            ):
                src = dir_path/file.name
                dst = Path(destination)/file.name
                try:
                    if not move:
                        if dst.exists():
                            logger.info(
                                f"File {src} already exists in \
destination {Path(destination)}"
                            )
                            continue
                        shutil.copy(src, dst)
                        logger.info(f"File '{src}' copied to '{dst}'")
                        files_copied = True
                    else:
                        if dst.exists():
                            logger.info(f"File {src} already exists\
in destination {Path(destination)}"
                            )
                            continue
                        shutil.move(src, dst)
                        logger.info(f"File '{src}' moved to '{dst}'")
                        files_moved = True
                except Exception as e:
                    logger.exception(
                        f"Error {e} encountered when {src} was being moved"
                    )
                    continue

        if files_moved:
            logger.info(
                f"All .{extension} files in {directory} moved to \
{destination} successfully."
            )
        elif files_copied:
            logger.info(
                f"All .{extension} files in {directory} \
copied to {destination} successfully."
            )
        else:
            logger.info(
                f"No .{extension} files in directory {directory}."
            )

    return None


def log_copy_or_move(source=None, destination=None, move=False):
    """Function to customize logged message"""

    if not move:
        logger(
            f"Files in {source} directory copied into {destination}"
        )
    else:
        print(f"Files in {source} directory moved to {destination}")


def get_files_from_sources(
    src, dst,
    directory_src=False,
    directory_list_src=False,
    directory_tree_src=False,
    move_file=False
):
    """
    Function to properly fetch pdf files from various sources to
    destination directory.

    Default operation is copy (when move_file=False). Files that already
    exist in destination are not copied or moved
    """

    # necessary directory existence checks are in the three underlying
    # function. The conversion of src and dst to path objects is done
    # by the underlying funtions

    # The default: copy pdfs from a single source directory
    if directory_src and isinstance(src, str):
        get_files_from_directory(src, dst, move=move_file)
        log_copy_or_move(source=src, destination=dst, move=move_file)

    # Copy pdf files from source directories (paths) in a list
    elif directory_list_src and isinstance(src, list):
        get_files_from_directories(src, dst, move=move_file)
        return None

    # Copy pdf files from a source directory tree. A case of
    # directory_tree_src
    # TODO: add checks
    else:
        get_files_from_tree(src, dst, move=move_file)
        return None

    return None


def organize_files_in_directory(  # noqa:C901
    source_directory,
    destination_directory,
    move=False
):
    """
    This function organizes files in a directory using file extension
    The default in this case is .pdf.

    The function takes a directory (without a subdir) and creates a set
    containing all unique file extensions in folder. All files of the same
    unique filetype or extension and are moved into the same directory.
    This content of source directory into an 'organized_files' directory(
    inside destination_directory.

    Of all the unique file types, the pdf directory is a good target source
    directory for FOrgy get_metadata subcommand since it only contains PDF
    files.


    TODO: Allow user to specify walk or scan to properly handle children
    files in folders.
    """

    src_dir = Path(source_directory)
    dst_dir = Path(destination_directory)

    if not src_dir.exists():
        logger.warning("The given source directory does not exist")
        return None

    if not dst_dir.exists():
        logger.warning("The given destination directory does not exist")
        return None

    # Create organized_directory folder and its parent(if it doesn't
    # yet exist) to house all organized file-typed folders
    organized_path = dst_dir/"organized_directory"
    if not organized_path.exists():
        os.makedirs(organized_path)

    # Initialize an extension set to contain all unique file extensions
    # in the directory
    extension_set = set()

    # Obtain all unique extensions by iterating over directory entries
    for file in os.scandir(src_dir):

        # First get file extension
        if file.is_file():
            _, extensn = os.path.splitext(file.name)
            extension_set.add(extensn)
    logger.info(extension_set)

    # Create folders to contain each unique file extension
    for ext in extension_set:
        # eliminate the leading dot in extension name
        folder_name = ext.lstrip(".")
        folder_path = organized_path / folder_name

        # Make extension directory and its parent
        if not folder_path.exists():
            os.makedirs(folder_path)

        # Move files with each unique extension to the created
        # extension directory. A future modification of this may
        # be to set walk=False|True to touch subfolders or not
        for file in os.scandir(src_dir):
            # file_path = src_dir/f"{file.name}"
            files_moved = False
            files_copied = False

            if file.is_file():

                # Get the file extension
                _, extension = os.path.splitext(file.name)

                # Move file to directories matching file's extension name
                if extension.lstrip(".") == folder_name:
                    try:
                        if not move:
                            shutil.copy(file.path, folder_path/file.name)
                            logger.info(
                                f"File '{file.path}' copied to '{folder_path/file.name}'"
                            )
                            files_copied = True
                        else:
                            shutil.move(file.path, folder_path/file.name)
                            logger.info(
                                f"File '{file.path}' moved to '{folder_path/file.name}'"
                            )
                            files_moved = True
                    except OSError as e:
                        logger.exception(
                            f"Error {e} encountered when {file.name} was being moved"
                        )
                        continue
                    except Exception as e:
                        logger.exception(f"Error '{e}' occured on {file.name}")
                        continue
        # Print success message whenever all files in one directory have been
        # moved/copied to destination (or it already exists there)
        if files_moved:
            logger.info(
                f"All {ext} files in {src_dir.name} moved to {dst_dir.absolute()} \
successfully."
            )
        elif files_copied:
            logger.info(
                f"All {ext} files in {src_dir.name} copied to {dst_dir.absolute()} \
successfully."
            )
        else:
            logger.info(f"No {ext} files in directory {src_dir.name}.")

    return extension_set


def delete_files_in_directory(directory, files=True, directories=False):
    """
    Delete only files (default), directories or both from directory.

    The shutil.rmtree(directory) deletes all content of directory which
    is not needed here

    NOTE: Delete is expected to be permanent. So use this carefully.
    """
    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if files:
                    if entry.is_file():
                        os.unlink(entry.path)
                        logger.info(
                            f"File {entry.name} in {entry.path} deleted successfully")
                if directories:
                    if entry.is_dir():
                        shutil.rmtree(entry.path)
                        logger.info(f"Directory {entry.name} in {entry.path} deleted successfully")
        logger.info(f"Files in {directory} deleted successfully")
    except OSError as e:
        logger.exception(f"Error {e} occured")
    except Exception as e:
        logger.exception(f"An unexpected error {e} encountered")


def move_file_or_directory(source, destination):
    """
    Function to move a file or directory from
    source to destination directory.
    """
    source = Path(source)
    destination = Path(destination)
    try:
        shutil.move(source, destination)

        # FileNotFoundError raised if file has a missing ISBN
        # and is already moved to missing_isbn directory.
        print(f"File {source.name} moved to {destination} directory")
    except FileNotFoundError:
        # This is a case where file has already been moved
        # to missing_isbn directory
        logger.exception(f"File not found: {source}")
        pass
    except (PermissionError, IsADirectoryError, OSError) as e:
        logger.exception(f"Error encountered: {e}")
        pass
    except shutil.Error as e:
        logger.exception(f"Shutil error encountered: {e}")
        pass
    except Exception as e:
        logger.exception(f"An unexpected error occured: {e}")
        pass


def rename_file_or_directory(source, destination):
    """Rename a file or a directory"""
    source = Path(source)
    destination = Path(destination)
    try:
        os.rename(source, destination)
        # Device how to handle duplicates by attacching time to file name
        logger.exception(
            f"File {source.name} renamed to {destination.name} directory"
        )
    except FileExistsError:
        logger.exception(
            f"File already exists at the destination: {source.name}"
        )
        pass
    except FileNotFoundError:
        logger.exception(f"Source file {source.name} not found in {source}")
        pass
    except (PermissionError, IsADirectoryError, OSError) as e:
        logger.exception(f"Error encountered: {e}")
        pass
    except Exception as e:
        logger.exception(f"An unexpected error occured: {e}")
        pass
