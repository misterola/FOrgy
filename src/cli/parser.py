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
dir_operations_parser = subparsers.add_parser("dir_operation")
dir_operations_parser.add_argument(
    "operation",
    choices=[
        "organize_files_ext",
        "delete_files",
        "copy_dir",
        "move_dirs",  
    ],
)
# If only one directory is provided, it's the source directory
dir_operations_parser.add_argument('--source_directory')
dir_operations_parser.add_argument('--destination_directory')
dir_operations_parser.add_argument('--move', action='store_true')
dir_operations_parser.add_argument('--files', action='store_true')
dir_operations_parser.add_argument('--directories', action='store_true')


# 2. get_files_parser
# functions:
# get_files_from_dir(directory, copy=True, move=False)  get_files_from_dir
# get_files_from_directories(directory_list, destination, extension='pdf', move=False) for get_files_from directory_list
# get_files_from_tree(source_directory, destination_directory, extension='pdf', move=False) for get_files_from_tree
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
# functions:
# pdfs_source is also compiled_source
# fetch_book_metadata(pdfs_source,
                        # original_source,
                        # database,
                        # missing_isbn_dir,
                        # missing_metadata_dir,
                        # extracted_texts_path,
                        # table_name="Books")  get_metadata
# get_book_covers(cover_dir, database, table) --covers
# get_all_metadata(database, table) --metadata_dict
get_metadata_parser = subparsers.add_parser("get_metadata") # and rename
get_metadata_parser.add_argument("source", type=str)
get_metadata_parser.add_argument("--book_covers", action="store_true")
get_metadata_parser.add_argument("--metadata_dict", action="store_true")
# add other arguments
# --googlebooks api key
# --file to enable user to supply arguments as a text file
# --data (folder to store all forgy files) the internal directory is the default if not provided



# 4. single file_metadata parser (has no cover)
# functions:
# get_single_book_metadata(file, isbn=None, title=None) from_api
# fetch_metadata_from_file(file) from_file

single_metadata_parser = subparsers.add_parser("get_single_metadata")
single_metadata_parser.add_argument("operation", choices=["from_api", "from_file"])
# add other arguments

# parser tests
args = parser.parse_args(['dir_operation', 'organize_files_ext'])
print(args)
args = parser.parse_args(['dir_operation', 'delete_files'])
print(args)
args = parser.parse_args(['get_files', 'from_dir'])
print(args)
args = parser.parse_args(['get_files', 'from_dir_list'])
print(args)
args = parser.parse_args(['get_files', 'from_tree'])
print(args)
args = parser.parse_args(['get_metadata', 'www.google.com'])
print(args)
args = parser.parse_args(['get_metadata', 'www.openlibrary.org', '--book_covers'])
print(args)
args = parser.parse_args(['get_metadata', 'www.ab.org', '--metadata_dict'])
print(args)
args = parser.parse_args(['get_metadata', 'www.zzz.org', '--book_covers', '--metadata_dict'])
print(args)

args = parser.parse_args(['-h'])
print(args)

args = parser.parse_args(['--quit'])
print(args)

if args.quit:
    # print("Exiting...")
    parser.exit(0, "Quit command entered...Goodbye!")

args = parser.parse_args(['--version'])
print(args)




