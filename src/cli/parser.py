# The CLI parser

import argparse
from pathlib import Path

 
parser = argparse.ArgumentParser(
            prog="FOrgy",
            description="A powerful file organizer, ebook manager, and book metadata extractor in python",  
            epilog="Welcome to %(prog)s v0.1.0!",
        )
parser.add_argument(
    "--version",
    action="version",
    version="%(prog)s v0.1.0",
)

subparsers = parser.add_subparsers(
                title="FOrgy Operations",
                description="Valid subcommands",
                dest="subcommands",
            )

# 1. organize_extension_parser
# organize_files_in_directory(source_directory, destination_directory, move=False) for organize_files_ext
organize_extension_parser = subparsers.add_parser(
                                "organize_extension",
                                help="organize files by extension",
                            )
organize_extension_parser.add_argument(
    '--source_directory',
    help="provide source directory for several file types",
)
organize_extension_parser.add_argument(
    '--destination_directory',
    help="provide destination directory for organized files",
)
organize_extension_parser.add_argument(
    '--move',
    action='store_true',
    help="move or copy file from source directory(default copy)",
)


# 2. delete_files_parser
# delete_files_in_directory(directory, files=True, directories=False) for delete_files. delete is permanent
delete_files_parser = subparsers.add_parser(
                        "delete_files",
                        help="delete files (default) or directories in source directory. WARNING: permanent operation!",
                      )
delete_files_parser.add_argument(
    'source_directory',
    help="provide source directory containing files or directories to be deleted",
)
delete_files_parser.add_argument(
    '--files',
    action='store_true',
    help="delete files in source directory",
)
delete_files_parser.add_argument(
    '--directories',
    action='store_true',
    help="delete sub-directories in source directory",
)


# 3. copy_directory
# copy_destination_directory(pdfs_source, new_pdfs_path) copy_dir
copy_directory_parser = subparsers.add_parser(
                            "copy_directory",
                            help="copy contents of source directory into destination directory",
                        )
copy_directory_parser.add_argument(
    'source_directory',
    help="provide source directory",
)
copy_directory_parser.add_argument(
    'destination_directory',
    help="provide destination directory",
)


# 4. move_directories
# move_folders(source_dir, destination_dir)  # function moves all sub-directories in a path into another directory
move_directories_parser = subparsers.add_parser(
                              "move_directories",
                              help="move directories to another destination",
                          )
move_directories_parser.add_argument(
    'source_directory',
    help="provide source directory for sub-directories",
)
move_directories_parser.add_argument(
    'destination_directory',
    help="provide destination for sub-directories moved",
)


# 5. get_files_from_dir_parser
# get_files_from_dir(directory, copy=True, move=False)  get_files_from_dir
# get_files_from_sources(src, dst, directory_src=False, directory_list_src=False, directory_tree_src=False, move_file=False)
get_files_from_dir_parser = subparsers.add_parser(
                                "get_files_from_dir",
                                help="aggregate pdf files from various directories/sources",
                            )
get_files_group = get_files_from_dir_parser.add_argument_group(
                      title='get files options',
                      description='Specify origin of source files (pick among directory_src, directory_list_src, and directory_tree_src)',
                  )
get_files_mutually_excl = get_files_group.add_mutually_exclusive_group(required=True)
get_files_mutually_excl.add_argument(
    '--directory_src',
    default=False,
    help="get pdf files from a single directory. source_directory is a raw string of path to a single directory",
)
get_files_mutually_excl.add_argument(
    '--directory_list_src',
    default=False,
    help="get pdf files from several directory paths. source_directory is a list of raw strings of paths to directories containing pdf files",
)
get_files_mutually_excl.add_argument(
    '--directory_tree_src',
    default=False,
    help="get pdf files from a single directory which contain other subdirectories with pdf files. \
source_directory is raw string of path to a single directory tree containing other directories",
)
# get_files_from_dir_parser.add_argument("source_directory", help="provide source directory or directories to fetch pdfs from")
get_files_from_dir_parser.add_argument(
    "destination_directory",
    help="provide destination directory for copied or moved files"
)
get_files_from_dir_parser.add_argument(
    "--move",
    action='store_true',
    help="move files from directory (default is copy, when move_file=False)",
)



# 3. get_book_metadata parser
# functions:
# pdfs_source is also compiled_source
# fetch_book_metadata(user_pdfs_source,
                        # forgy_pdfs_copy,
                        # user_pdfs_destination, #NEW where to copy or move data directory to
                        # database,
                        # missing_isbn_dir,
                        # missing_metadata_dir,
                        # extracted_texts_path,
                        # table_name="Books")
# get_book_covers(cover_dir, database, table) --covers
# get_all_metadata(database, table) --metadata_dict
get_metadata_parser = subparsers.add_parser(
                        "get_metadata",
                        help="get pdf metadata and rename file",
                      )

get_metadata_parser.add_argument(
    "--file",
    action="store_true",
    help="enable user to supply arguments as a text file one line for each argument(do not specify other arguments in the commandline",
)
get_metadata_parser.add_argument(
    "user_pdfs_source",
    type=str,
    help="provide source of pdf files to operate upon",
)
get_metadata_parser.add_argument(
    "user_pdfs_destination",
    type=str,
    help="provide destination for extracted book metadata",
)
get_metadata_parser.add_argument(
    "--book_covers",
    action="store_true",
    help="get book covers or not",
)
get_metadata_parser.add_argument(
    "--metadata_dict",
    action="store_true",
    help="save extracted metadata dictionary as text file",
)
# add other arguments
get_metadata_parser.add_argument(
    "--move_metadata",
    action="store_true",
    help="move metadata from FOrgy to user_pdfs_destination. It's copied by default",
) # don't specify for now
get_metadata_parser.add_argument(
    "--GOOGLE_API_KEY",
    help="provide Google BooksAPI KEY",
)
get_metadata_parser.add_argument(
    "--database",
    help="provide link to .db file",
)
get_metadata_parser.add_argument(
    "--db_table",
    help="provide name of book table in .db file",
)

# --file to enable user to supply arguments as a text file
# --data (folder to store all forgy files) the internal directory is the default if not provided


# 4. single file_metadata parser (has no cover)
single_metadata_parser = subparsers.add_parser(
                             "get_single_metadata",
                             help="get metatada for a single book using title, isbn or file path",
                         )
# single_metadata_parser.add_argument("operation", choices=["from_api", "from_file", "from_title"], help="provide source you want to fetch metadata from")
single_metadata_group = single_metadata_parser.add_argument_group(title="get single metadata")
single_metadata_mutually_excl = single_metadata_group.add_mutually_exclusive_group(required=True)
single_metadata_mutually_excl.add_argument(
    "--file",
    help="provide path to pdf file",
)
single_metadata_mutually_excl.add_argument(
    "-isbn",
    help="provide book isbn",
)
single_metadata_mutually_excl.add_argument(
    "--title",
    help="provide book title",
)


##
##if args.quit:
##    # print("Exiting...")
##    parser.exit(0, "Quit command entered...Goodbye!")
##




