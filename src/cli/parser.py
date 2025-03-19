# The CLI parser
# Commands (positional_arguments, --optional_argument, choices, default_values, type:
#Get book metadata or organize your files",

#NOTE: Add sufficient help messages
import argparse

parser = argparse.ArgumentParser(
            prog="FOrgy",
            description="A powerful file organizer, ebook manager, and book metadata extractor in python",  
            epilog="Welcome to %(prog)s v0.1.0!",
        )

subparsers = parser.add_subparsers(
                    title="FOrgy Operations",
                    description="Valid subcommands",
                    dest="subcommands"
            )


# 1. dir_operations_parser
# to delete files or organize by extension
dir_operations_parser = subparsers.add_parser("dir_operation")
dir_operations_parser.add_argument(
    "operation",
    choices=[
        "organize_files_ext",
        "delete_files",
    ],
)

# add all options to cover for each operation under organize files
# organize_files_in_directory(source_directory, destination_directory)--organizes files according to extension



# 2. get_files_parser
get_files_parser = subparsers.add_parser("get_files")
get_files_parser.add_argument(
    "source",
    choices=[
        "from_dir",
        "from_dir_list",
        "from_tree",
    ],                                   
    default="from_dir",
)
# add get files arguments for all functions



# 3. get_book_metadata parser
get_metadata_parser = subparsers.add_parser("get_metadata")
get_metadata_parser.add_argument("source", type=str)
get_metadata_parser.add_argument("--book_covers", action="store_true")
get_metadata_parser.add_argument("--metadata_dict", action="store_true")
# add other arguments


# 4. single file_metadata parser (has no cover)
single_metadata_parser = subparsers.add_parser("get_single_metadata")
single_metadata_parser.add_argument("operation", choices=["from_api", "from_file"])
# add other arguments

# some testing
args = parser.parse_args(['dir_operation', 'organize_files_ext'])
##args = parser.parse_args(['dir_operation', 'delete_files'])
##args = parser.parse_args(['get_files', 'from_dir'])
##args = parser.parse_args(['get_files', 'from_dir_list'])
##args = parser.parse_args(['get_files', 'from_tree'])
##args = parser.parse_args(['get_metadata', 'www.google.com'])
##args = parser.parse_args(['get_metadata', 'www.openlibrary.org', '--book_covers'])
##args = parser.parse_args(['get_metadata', 'www.ab.org', '--metadata_dict'])
##args = parser.parse_args(['get_metadata', 'www.zzz.org', '--book_covers', '--metadata_dict'])

print(args)


# some useful options
# --original_source (list_of_dir, tree, dir)
# --compiled_source
# --directory_list_src (F,T)
# --directory_tree_src (F,T)
# --table_name
# --library_db_name
# --delete_db_table
# --get_cover_pics
# --get_metadata_txt
# --googlebooks api key
# --move_or_copy
# --get argument from text document
# --file to enable user to add arguments as file
# --quit
#--version action="version", version="%(prog)s 0.1.0"
# --data (folder to store all forgy files) the internal directory is the default if not provided



# subparsers: organize_files, get_metadata

#organize_files
# arguments: operation: choices[get_files_from_dir, get_files_from directory_list, get_files_from_tree,
            # move_folders_to_dir (folders in tree), organize_files_in_directory, delete_files_in_directory]

#get_metadata
# arguments: operation: get_book_metadata/rename_files (options: download_book_covers, get_metadata_dict_text),
            # single_file_operations: get_single_book_metadata, fetch_metadata_from_file




