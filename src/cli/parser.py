"""
The CLI parser for FOrgy
"""

import argparse
from pathlib import Path


def get_parser():
    """Function to get command-line interface parser

    The parser consists of various subparsers that
    provide the following subcommands:
    - organize_extension: to organize files in a directory
                          by type/extension.
    - delete_files: to delete files and/or directories
                    within a source directory
    - copy_directory_contents: copy contents of source directory
                                into destination directory includig
                                files and directories
    - move_directories: to move a directory from its current to
                        another directory. Files in current directory
                        are not moved but directories therein and their
                        contents are moved
    - get_files_from_dir: to copy files into FOrgy from various sources
                          sources may be:
                          > a directory tree (directory_tree_src)
                          > a directory list (directory_list_src)
                          > a path to a single directory (directory_src)
    - get_metadata: enable user to download several metadata for various
                    books including their covers and metadata saved
                    into a text file
    - get_single_metadata: to get metadata for a single book. This
                            excludes the book covers
    """
    parser = argparse.ArgumentParser(
                prog="forgy",
                description="""A powerful file organizer, ebook manager,
                                and book metadata extractor in python
                                """,
                epilog="Welcome to %(prog)s v0.1.0!",
            )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s v0.1.0",
    )

    subparsers = parser.add_subparsers(
                    title="forgy Operations",
                    description="Valid subcommands",
                    dest="subcommands",
                )

    # 1. get_book_metadata parser
    get_metadata_parser = subparsers.add_parser(
                            "get_metadata",
                            description="""Get PDF e-book metadata and rename
                            several files using valid titles from retrieved
                            metadata. Source and destination directories
                            must be provided.
                            """,
                            help="""retrieve PDF e-book metadata and rename
                            several PDF e-books with it"""
                          )

    get_metadata_parser.add_argument(
        "--book_covers",
        action="store_true",
        help="retrieve book covers? False(default)"
    )
    get_metadata_parser.add_argument(
        "--metadata_dict",
        action="store_true",
        help="save extracted metadata as dictionary written to text file? False(default)",
    )
    # add other arguments
    get_metadata_parser.add_argument(
        "--move_metadata",
        action="store_true",
        help="""move extracted metadata from forgy internals to user_pdfs_destination?
        directory? False(default)"""
    )

    get_metadata_parser.add_argument(
        "--GOOGLE_API_KEY",
        help="provide Google BooksAPI key",
        default=""  # doesn't affect string concatenation of api url
    )

    get_metadata_parser.add_argument(
        "--file",
        help="""enable user to provide some arguments in a text file one
              line for each argument. only --book_covers, --metadata_dict,
              --move_metadata, --GOOGLE_API_KEY, should be provided at
              the commandline. The other arguments will be contained inside
              the text file whose path is specified after the --file argument.
              """
    )

    get_metadata_parser.add_argument(
        "--database",
        default="library.db",
        help="provide link to .db file"
    )
    get_metadata_parser.add_argument(
        "--db_table",
        default="Books",
        help="provide name of book table in .db file"
    )
    get_metadata_parser.add_argument(
        "--user_pdfs_source",
        type=str,
        help="provide source directory of pdf files to fetch metadata for and rename",
    )
    get_metadata_parser.add_argument(
        "--user_pdfs_destination",
        type=str,
        help="""provide destination directory to move or copy extracted book metadata
        and renamed books to."""
    )

    2.
    # get_isbns_from_texts parser enables user to fetch
    # isbns in many pdf files text file of a dictionary
    # whose key is filename and isbn_list as value of
    # extracted ISBN
    # TODO: Enable user to rename file with ref_isbn
    get_isbns_from_texts_parser = subparsers.add_parser(
                                  "get_isbns_from_texts",
                                  description="""Extract valid ISBNs from PDF files
                                  as a dictionary with filenames as keys and
                                  valid ISBNs as a list of values""",
                                  help="""extract isbns from several PDF e-books contained
                                  in source_directory"""
                                  )
    get_isbns_from_texts_parser.add_argument(
        'source_directory',
        help="provide source directory for input pdf files",
    )
    get_isbns_from_texts_parser.add_argument(
        'destination_directory',
        help="provide destination for text file containing book titles and extracted isbns"
    )
    get_isbns_from_texts_parser.add_argument(
        '--isbn_text_filename',
        default="extracted_isbns.txt",
        help="provide name of text file containing extracted e-book isbns"
    )

    # 3. single file_metadata parser (has no cover)
    single_metadata_parser = subparsers.add_parser(
                                 "get_single_metadata",
                                 description="""Extract metadata for a
                                 single PDF e-book using its ISBN (or
                                 title) and file path""",
                                 help="""get metatada for a single
                                 book using file path and title or isbn""",
                             )
    # file is needed for filesize estimation not isbn or text
    # extraction
    single_metadata_parser.add_argument(
        "file",
        type=Path,
        help="provide path to input PDF e-book"
    )

    single_metadata_group = (
        single_metadata_parser.add_argument_group(
            title="optional arguments (provide only one)"
        )
    )
    single_metadata_mutually_excl = (
        single_metadata_group.add_mutually_exclusive_group(required=True)
    )
    single_metadata_mutually_excl.add_argument(
        "--isbn",
        type=str,
        help="provide book isbn as int",
    )
    single_metadata_mutually_excl.add_argument(
        "--title",
        help="provide book title",
    )

    # 4. organize_extension_parser
    organize_extension_parser = subparsers.add_parser(
                                    "organize_extension",
                                    help="organize files by extension or format",
                                    description="""Organize files in a directory
                                    into folders each containing files of the same
                                    format."""
                                )
    organize_extension_parser.add_argument(
        '--source_directory',
        help="provide source directory containing files in various formats",
    )
    organize_extension_parser.add_argument(
        '--destination_directory',
        help="provide destination directory for organized files",
    )
    organize_extension_parser.add_argument(
        '--move',
        action='store_true',
        help="""move or copy file from source directory? Copy(default)
        when --move is not provided"""
    )

    # 5. get_files_from_dir_parser
    get_files_from_dir_parser = subparsers.add_parser(
                                    "get_files_from_dir",
                                    help="""aggregate pdf files from various
                                            directories/sources""",
                                    description="""Copy or move (copy default) PDF files
                                    from a directory (directory_src), a list of directories(
                                    directory_list_src), or a directory containing other
                                    directories (directory_tree_src) into a destination
                                    directory."""
                                )
    get_files_group = get_files_from_dir_parser.add_argument_group(
                          title='optional arguments for get_files_from_dir',
                          description="""Specify origin of source files (specify one of
                                          directory_src, directory_list_src,
                                          and directory_tree_src)""",
                      )
    get_files_mutually_excl = (
        get_files_group.add_mutually_exclusive_group(required=True)
    )
    get_files_mutually_excl.add_argument(
        '--directory_src',
        action='store_true',
        help="""get PDF files from a single directory. source_directory
                is a raw string of path to a single directory""",
    )
    get_files_mutually_excl.add_argument(
        '--directory_list_src',
        action='store_true',
        help="""get PDF files from several directory paths.
                source_directory is a list of raw strings of
                paths to directories containing pdf files""",
    )
    get_files_mutually_excl.add_argument(
        '--directory_tree_src',
        action='store_true',
        help="""get pdf files from a single directory which contain
              other subdirectories with pdf files. source_directory
              is a path to a single directory containing other
              directories (a directory tree)""",
    )

    get_files_from_dir_parser.add_argument(
        "--source_directory",
        help="""provide source directory for PDF files. The source
                can be a list of path to a directory containing only
                PDF files or a directory containing other directories
                any or all of which may contain pdf files""",
        type=str,
    )

    get_files_from_dir_parser.add_argument(
        "--source_directory2",
        help="""provide path to source directories for directory_list_src.
                The sources are directories (at least one) containing
                PDF e-book files to be copied (default) or moved""",
        nargs='+',
        type=Path,
    )

    get_files_from_dir_parser.add_argument(
        "--destination_directory",
        help="provide destination directory for copied or moved PDF files",
        required=True,
        type=Path,
    )
    get_files_from_dir_parser.add_argument(
        "--move",
        action='store_true',
        help="""move files from source to destination directory?
        Copy (default) when --move is not specified)""",
    )

    # 6. copy_directory_contents
    copy_directory_parser = subparsers.add_parser(
                                "copy_directory_contents",
                                help="""copy contents of source directory
                                        into destination directory (files
                                        and directories included)""",
                                description="""Copy PDF e-books in source directory
                                into destination directory. Function is also used by
                                forgy to create its own internal copies of PDF files to
                                fetch metadata for and rename."""
                            )
    copy_directory_parser.add_argument(
        'source_directory',
        help="provide source directory of PDF ebooks",
    )
    copy_directory_parser.add_argument(
        'destination_directory',
        help="provide destination directory for PDF ebooks",
    )

    # 7. move_directories
    move_directories_parser = subparsers.add_parser(
                                  "move_directories",
                                  help="move directories to another destination",
                                  description="""Move all directories in source directory
                                  into destination directory"""
                              )
    move_directories_parser.add_argument(
        'source_directory',
        help="provide source directory containing sub-directories to be moved",
    )
    move_directories_parser.add_argument(
        'destination_directory',
        help="provide destination for sub-directories about to be moved",
    )

    # 8. delete_files_parser
    delete_files_parser = subparsers.add_parser(
                            "delete_files_directories",
                            help="""delete files or directo-
                                    ries in source directory. WARNING:
                                    permanent operation!
                                    """,
                            description="Permanently delete files and/or directories"
                          )
    delete_files_parser.add_argument(
        'source_directory',
        help="""provide source directory containing files
                or directories to be deleted""",
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

    return parser
