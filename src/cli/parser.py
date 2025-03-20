# The CLI parser
# Commands (positional_arguments, --optional_argument, choices, default_values, type:

import argparse
from pathlib import Path

 
parser = argparse.ArgumentParser(
            prog="FOrgy",
            description="A powerful file organizer, ebook manager, and book metadata extractor in python",  
            epilog="Welcome to %(prog)s v0.1.0!",
        )
parser.add_argument("--version", action="version", version="%(prog)s v0.1.0")
parser.add_argument("--quit", dest="quit", action="store_true")

subparsers = parser.add_subparsers(
                    title="FOrgy Operations",
                    description="Valid subcommands",
                    dest="subcommands"
            )

# 1. dir_operations_parser
# organize_files_in_directory(source_directory, destination_directory, move=False) for organize_files_ext
# delete_files_in_directory(directory, files=True, directories=False) for delete_files. delete is permanent
# copy_destination_directory(pdfs_source, new_pdfs_path) copy_dir
# move_folders(source_dir, destination_dir)  # function move directories in a path to another directory
dir_operations_parser = subparsers.add_parser("dir_operation", help="organize your files")
dir_operations_parser.add_argument(
    "operation",
    choices=[
        "organize_files_ext",
        "delete_files",
        "copy_dir",
        "move_dirs",  
    ],
    help="specify directory operation to perform"
)
# If only one directory is provided, it's the source directory
dir_operations_parser.add_argument('--source_directory', help="provide source directory")
dir_operations_parser.add_argument('--destination_directory', help="provide destination directory(does not apply to delete_files)")
dir_operations_parser.add_argument('--move', action='store_true', help="move or copy file from source directory(default copy)")
dir_operations_parser.add_argument('--files', action='store_true', help="delete files in source directory(only apply to delete_files)")
dir_operations_parser.add_argument('--directories', action='store_true', help="delete directories in source directory(only apply to delete_files")


# 2. get_files_parser
# functions:
# get_files_from_dir(directory, copy=True, move=False)  get_files_from_dir
# get_files_from_directories(directory_list, destination, extension='pdf', move=False) for get_files_from directory_list
# get_files_from_tree(source_directory, destination_directory, extension='pdf', move=False) for get_files_from_tree
get_files_parser = subparsers.add_parser("get_files",help="aggregate pdf files from various directories")
get_files_parser.add_argument(
    "source",
    choices=[
        "from_dir", # leave default as copy
        "from_dir_list",
        "from_tree",
    ],                                   
    default="from_dir",
    help="provide source to fetch pdfs from"
)
get_files_parser.add_argument("--source_directory", help="provide source directory containing pdf files")
get_files_parser.add_argument("--directory_list", help="provide list of directories(paths) containing pdf files")
get_files_parser.add_argument("--move", help="move or copy files") #only use this on 'from_dir_list' and 'from_tree'
get_files_parser.add_argument("--destination_directory", help="provide destination directory for copied or moved files")




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
get_metadata_parser = subparsers.add_parser("get_metadata", help="get pdf metadata and rename file")
get_metadata_parser.add_argument("user_pdfs_source", type=str, help="provide source of pdf files to operate upon")
get_metadata_parser.add_argument("user_pdfs_destination", type=str, help="provide destination for extracted book metadata")
get_metadata_parser.add_argument("--book_covers", action="store_true", help="get book covers or not")
get_metadata_parser.add_argument("--metadata_dict", action="store_true", help="save extracted metadata dictionary as text file")
# add other arguments
get_metadata_parser.add_argument("--move_metadata", action="store_true", help="move metadata from FOrgy to user_pdfs_destination. It's copied by default") # don't specify for now
get_metadata_parser.add_argument("--GOOGLE_API_KEY", help="provide Google BooksAPI KEY")
get_metadata_parser.add_argument("--file", help="enable user to supply arguments as a text file one line for each")
get_metadata_parser.add_argument("--database", help="provide link to .db file")
get_metadata_parser.add_argument("--db_table", help="provide name of book table in .db file")

# --file to enable user to supply arguments as a text file
# --data (folder to store all forgy files) the internal directory is the default if not provided


# 4. single file_metadata parser (has no cover)
# functions:
# get_single_book_metadata(file, isbn=None, title=None) from_api
# fetch_metadata_from_file(file) from_file

single_metadata_parser = subparsers.add_parser("get_single_metadata", help="get metatada for a single file only (from either file or api)")
single_metadata_parser.add_argument("operation", choices=["from_api", "from_file", "from_title"], help="provide source you want to fetch metadata from")
single_metadata_parser.add_argument("--file", help="provide path to pdf file")
single_metadata_parser.add_argument("--isbn", help="provide book isbn")
single_metadata_parser.add_argument("--title", help="provide book title")


##
##args = parser.parse_args(['--quit'])
##print(args)
##
##if args.quit:
##    # print("Exiting...")
##    parser.exit(0, "Quit command entered...Goodbye!")
##




