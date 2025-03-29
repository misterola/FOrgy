# The CLI parser

import argparse
from pathlib import Path


def get_parser():
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
    delete_files_parser = subparsers.add_parser(
                            "delete_files",
                            help="delete files (default) or directories in source directory. \
    WARNING: permanent operation!",
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
    copy_directory_parser = subparsers.add_parser(
                                "copy_directory_contents",
                                help="copy contents of source directory into destination directory (files and directories included)",
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
    get_files_from_dir_parser = subparsers.add_parser(
                                    "get_files_from_dir",
                                    help="aggregate pdf files from various directories/sources",
                                )
    get_files_group = get_files_from_dir_parser.add_argument_group(
                          title='get files options',
                          description='Specify origin of source files (pick among directory_src, \
    directory_list_src, and directory_tree_src)',
                      )
    get_files_mutually_excl = get_files_group.add_mutually_exclusive_group(required=True)
    get_files_mutually_excl.add_argument(
        '--directory_src',
        action='store_true',
        help="get pdf files from a single directory. source_directory is a raw string of\
    path to a single directory",
    )
    get_files_mutually_excl.add_argument(
        '--directory_list_src',
        action='store_true',
        help="get pdf files from several directory paths. source_directory is a list of raw \
    strings of paths to directories containing pdf files",
    )
    get_files_mutually_excl.add_argument(
        '--directory_tree_src',
        action='store_true',
        help="get pdf files from a single directory which contain other subdirectories with pdf files. \
    source_directory is raw string of path to a single directory tree containing other directories",
    )

    get_files_from_dir_parser.add_argument(
        "--source_directory",
        help="provide source directory. The source can be a list of paths to different directories,\
a directory containing only files, or a directory containing other directories any or all of which\
contain pdf files",
        type=str,
    )

    get_files_from_dir_parser.add_argument(
        "--source_directory2",
        help="provide source directory. The source can be a list of paths to different directories,\
a directory containing only files, or a directory containing other directories any or all of which\
contain pdf files",
        # action='append',
        nargs='+',
        type=Path,
    )

    get_files_from_dir_parser.add_argument(
        "--destination_directory",
        help="provide destination directory for copied or moved files",
        required=True,
        type=Path,
    )
    get_files_from_dir_parser.add_argument(
        "--move",
        action='store_true',
        help="move files from directory (default is copy, when move_file=False)",
    )



    # 3. get_book_metadata parser
    get_metadata_parser = subparsers.add_parser(
                            "get_metadata",
                            help="get pdf metadata and rename file",
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
        "--file",
        help="enable user to supply arguments as a text file one line for each argument\
    (do not specify other arguments in the commandline",
    )
    get_metadata_parser.add_argument(
        "--GOOGLE_API_KEY",
        help="provide Google BooksAPI KEY",
    )
    get_metadata_parser.add_argument(
        "--database",
        default="library.db",
        help="provide link to .db file",
    )
    get_metadata_parser.add_argument(
        "--db_table",
        default="Books",
        help="provide name of book table in .db file",
    )
    get_metadata_parser.add_argument(
        "--user_pdfs_source",
        type=str,
        help="provide source of pdf files to operate upon",
    )
    get_metadata_parser.add_argument(
        "--user_pdfs_destination",
        type=str,
        help="provide destination for extracted book metadata",
    )

    # 4. single file_metadata parser (has no cover)
    single_metadata_parser = subparsers.add_parser(
                                 "get_single_metadata",
                                 help="get metatada for a single book using title, isbn or file path",
                             )
    # file is needed for filesize estimation not isbn or text extraction
    single_metadata_parser.add_argument(
        "file",
        help="provide path to pdf file",
    )

    single_metadata_group = single_metadata_parser.add_argument_group(title="get single metadata")
    single_metadata_mutually_excl = single_metadata_group.add_mutually_exclusive_group(required=True)
    single_metadata_mutually_excl.add_argument(
        "--isbn",
        type=str,
        help="provide book isbn as int",
    )
    single_metadata_mutually_excl.add_argument(
        "--title",
        help="provide book title",
    )

    # Add last parser subcommand which takes a folder containing books and return a
    # text file of a dictionary whose key is filename and isbn_list as value of extracted ISBN
    # enable user to rename files with joined isbns
    # Positional args: source, isbn_file_path
    get_isbns_from_texts_parser = subparsers.add_parser(
                                  "get_isbns_from_texts",
                                  help="Extract isbns from source_directory pdf files into a text file (isbn_text_filename)",
                              )
    get_isbns_from_texts_parser.add_argument(
        'source_directory',
        help="provide source directory for pdf files",
    )
    get_isbns_from_texts_parser.add_argument(
        'destination_directory',
        help="provide destination for text file containing isbns",
    )
    get_isbns_from_texts_parser.add_argument(
        '--isbn_text_filename',
        default="extracted_book_isbns.txt",
        help="provide destination for text file containing isbns",
    )
    

    

    return parser

##
##if args.quit:
##    # print("Exiting...")
##    parser.exit(0, "Quit command entered...Goodbye!")
##




