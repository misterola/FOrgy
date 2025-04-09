from pathlib import Path
import os
import shutil
# import pypdf

# from dotenv import load_dotenv

from forgy.messyforg import (
    check_internet_connection,
    fetch_book_metadata,
    create_directories,
    get_isbns_from_texts,
)
from forgy.database import (
    create_db_and_table,
    get_all_metadata,
    view_database_table,
)
from forgy.logger import create_logger
from cli.parser import get_parser
from forgy.filesystem_utils import (
    delete_files_in_directory,
    organize_files_in_directory,
    copy_directory_contents,
    get_files_from_sources,
    move_folders,
)
from forgy.metadata_search import (
    get_book_covers,
    get_single_book_metadata,
)


logger = create_logger('main')

logger.info("Logger started in main module")


def fetch_arguments_from_file(file_path):
    """Function to read commandline arguments from file"""
    with open(file_path, 'r') as arguments:
        argument_list = arguments.read().splitlines()
        print(argument_list)
        return argument_list


def save_api_key_to_env(api_key):
    """Handle API_KEY as an environment variable"""

    dotenv_file = f'{Path(os.getcwd()).parent}/.env'

    if not os.path.exists(dotenv_file):
        with open(dotenv_file, 'w') as env_file:
            env_file.write(f"GOOGLE_API_KEY={api_key}\n")
    else:
        # If the .env file exists, overwrite existing API_KEY in it
        # whenever user specify it in get_metadata subcommand
        with open(dotenv_file, 'w') as env_file:
            env_file.write(f"GOOGLE_API_KEY={api_key}\n")

    logger.info(f"Google BooksAPI Key saved to {dotenv_file}")


def main():  # noqa: C901
    """Function to run FOrgy"""

    parser = get_parser()

    args = parser.parse_args()

    print(args)

    if args.subcommands == 'organize_extension':
        source_directory = args.source_directory
        destination_directory = args.destination_directory
        move_files = args.move
        organize_files_in_directory(
            source_directory,
            destination_directory,
            move=move_files
        )

    elif args.subcommands == 'delete_files':
        source_directory = args.source_directory
        files = args.files
        directories = args.directories
        delete_files_in_directory(
            source_directory,
            files=files,
            directories=directories
        )

    elif args.subcommands == 'copy_directory_contents':
        source_directory = args.source_directory
        destination_directory = args.destination_directory
        copy_directory_contents(
            source_directory,
            destination_directory
        )

    elif args.subcommands == 'move_directories':
        source_directory = args.source_directory
        destination_directory = args.destination_directory
        move_folders(source_directory, destination_directory)

    elif args.subcommands == 'get_files_from_dir':
        if args.directory_src:
            source_directory = args.source_directory
            destination_directory = args.destination_directory
            directory_src = args.directory_src
            move = args.move

            # directory_list_src=False, directory_tree_src=False
            get_files_from_sources(
                source_directory,
                destination_directory,
                directory_src=directory_src,
                move_file=move,
            )

        elif args.directory_list_src:
            source_directory2 = args.source_directory2
            destination_directory = args.destination_directory
            directory_list_src = args.directory_list_src
            move = args.move

            # directory_src=False, directory_tree_src=False,
            get_files_from_sources(
                source_directory2,
                destination_directory,
                directory_list_src=directory_list_src,
                move_file=move,
            )

        elif args.directory_tree_src:
            source_directory = args.source_directory
            destination_directory = args.destination_directory
            directory_tree_src = args.directory_tree_src
            move = args.move

            #  directory_src=False, directory_list_src=False,
            get_files_from_sources(
                source_directory,
                destination_directory,
                directory_tree_src=directory_tree_src,
                move_file=move,
            )

        else:
            logger.info("Please provide a valid directory list, directory_tree, or directory")

    elif args.subcommands == 'get_metadata':
        # if user is not connected to internet exit
        if check_internet_connection():
            print("Internet connection is available")
        else:
            print("Internet is unavailable")
            return

        # Set-up internal directories (in parent of current
        # directory...FOrgy directory)
        [
            data_path,
            pdfs_path,
            missing_isbn_path,
            missing_metadata_path,
            book_metadata_path,
            extracted_texts_path,
            cover_pics_path
        ] = create_directories(
                                data="data",
                                forgy_pdfs_copy="pdfs",
                                missing_isbn="missing_isbn",
                                missing_metadata="missing_metadata",
                                book_metadata="book_metadata",
                                extracted_texts="extracted_texts",
                                book_covers="book_covers",
                            )

        cli_options_in_file = [
            args.GOOGLE_API_KEY,
            args.database,
            args.db_table,
            args.user_pdfs_source,
            args.user_pdfs_destination,
        ]

        # cli_options = [args.book_covers, args.metadata_dict,
        # args.move_metadata, args.file]

        # Specify options supplied from cli
        book_covers = args.book_covers
        metadata_dict = args.metadata_dict
        move_metadata = args.move_metadata
        file = args.file

        if file:
            if not Path(file).is_file():
                logger.info(
                    f"The provided file does not exist: {file}"
                )
                return

            logger.info(f"Processing arguments in {args.file}")

            # Elements in argument_list represent consecutive ones
            # on each line of .txt file. We use fetch_arguments...
            # function to extract arguments from file.
            # We can unpack arguments from file into variables for
            # use in get_metadata execution
            # NOTE: each member of the argument_list must be specified
            # on one line each in the file.txt
            argument_list = fetch_arguments_from_file(file)

            logger.info(f"Argument list: {argument_list}")

            # Incomplete arguments will not be processed
            # (google_api_key should not be added to text file)
            if len(argument_list) < 8:
                print(
                    "Please add all arguments, excluding --book_covers, \
--metadata_dict, move_metadata, and --file FILEPATH"
                )
                pass

            # Fetch arguments from file
            try:
                [_,
                 GOOGLE_API_KEY,
                 _,
                 database,
                 _,
                 db_table,
                 user_pdfs_source,
                 user_pdfs_destination] = argument_list
            except ValueError:
                print(
                    """
                    All the 5 arguments required inside commands
                    text file must be provided. These include:
                    GOOGLE_API_KEY, database (path), db_table,
                    user_pdfs_source, user_pdfs_destination.
                    """
                )
                return

            if user_pdfs_source is None:
                logger.error(
                    f"Error, user_pdfs_source value is invalid: {user_pdfs_source}"
                )
                return

            if user_pdfs_destination is None:
                logger.errors(
                    f"Error, user_pdfs_destination value is invalid: {user_pdfs_source}"
                )
                return

            db_path = f"{book_metadata_path}/{database}"

            create_db_and_table(
                book_metadata_path,
                table_name=db_table,
                db_name=database,
                delete_table=True,
            )

            # store GOOGLE_API_KEY as an environment variable
            save_api_key_to_env(GOOGLE_API_KEY)

            # copy pdf files into FOrgy's pdfs_path
            copy_directory_contents(user_pdfs_source, pdfs_path)

            # get metadata function
            fetch_book_metadata(
                user_pdfs_source,
                pdfs_path,
                user_pdfs_destination,
                db_path,
                missing_isbn_path,
                missing_metadata_path,
                extracted_texts_path,
                db_table,
                database,
            )

            print(f"Files added to {db_table}:")
            view_database_table(db_path, db_table)

            if book_covers:
                #  #db_table is table_name, db_path is full path
                get_book_covers(cover_pics_path, db_path, db_table)

            if metadata_dict:
                # metadata_dictionary coverted to str to enable
                # .write() work on it
                metadata_dictionary = str(
                    get_all_metadata(
                        db_path,
                        db_table,
                    )
                )
                with open(
                    f"{Path(book_metadata_path)}/metadata_dictionary.txt", 'w'
                ) as metadata_dict_text:
                    metadata_dict_text.write(metadata_dictionary)
                    logger.info("metadata_dictionary text created successfully")

            if not move_metadata:
                try:
                    shutil.copytree(
                        data_path,
                        user_pdfs_destination,
                        dirs_exist_ok=True,
                    )
                    logger.info(
                        f"Source directory {data_path} copied to \
{user_pdfs_destination} successfully"
                    )
                except Exception as e:
                    logger.exception(f"Exception {e} raised")
                    pass
            else:
                # TODO: debug: move_metadata=True
                try:
                    shutil.copytree(
                        data_path,
                        user_pdfs_destination,
                        dirs_exist_ok=True
                    )
                    os.rmdir(data_path)
                    logger.info(
                        f"Source directory {data_path} moved to \
{user_pdfs_destination} successfully"
                    )
                except Exception as e:
                    logger.exception(f"Exception {e} raised")
                    pass

        elif not file and any(cli_options_in_file):
            book_covers = args.book_covers
            metadata_dict = args.metadata_dict
            move_metadata = args.move_metadata
            GOOGLE_API_KEY = args.GOOGLE_API_KEY
            database = args.database
            db_table = args.db_table
            user_pdfs_source = args.user_pdfs_source
            user_pdfs_destination = args.user_pdfs_destination

            if user_pdfs_source is None:
                logger.error(
                    f"Error, user_pdfs_source value is invalid: {user_pdfs_source}"
                )
                return

            if user_pdfs_destination is None:
                logger.error(
                    f"Error, user_pdfs_destination value is invalid: {user_pdfs_source}"
                )
                return

            # Store GOOGLE_API_KEY as an environment variable
            save_api_key_to_env(GOOGLE_API_KEY)

            db_path = f"{book_metadata_path}/{database}"

            create_db_and_table(
                book_metadata_path,
                table_name=db_table,
                db_name=database,
                delete_table=True,
            )

            copy_directory_contents(user_pdfs_source, pdfs_path)

            fetch_book_metadata(
                user_pdfs_source,
                pdfs_path,
                user_pdfs_destination,
                db_path,
                missing_isbn_path,
                missing_metadata_path,
                extracted_texts_path,
                db_table,
                database,
            )
            logger.info(f"Files added to {db_table}:")

            view_database_table(db_path, db_table)

            if book_covers:
                get_book_covers(cover_pics_path, db_path, db_table)

            if metadata_dict:
                # metadata_dictionary coverted to str to enable
                # .write() work on it

                metadata_dictionary = str(get_all_metadata(db_path, db_table))

                with open(
                    f"{Path(book_metadata_path)}/metadata_dictionary.txt", 'w'
                ) as metadata_dict_text:
                    metadata_dict_text.write(metadata_dictionary)
                    print("metadata_dictionary text created successfully")

            if not move_metadata:
                try:
                    shutil.copytree(
                        data_path,
                        user_pdfs_destination,
                        dirs_exist_ok=True
                    )
                    logger.info(
                        f"Source directory {data_path} copied to \
{user_pdfs_destination} successfully"
                    )
                except Exception as e:
                    logger.exception(f"Exception {e} raised")
                    # print(f"Exception {e} raised")
                    pass
            else:
                # TODO: debug: move_metadata=True
                try:
                    shutil.copytree(
                        data_path,
                        user_pdfs_destination,
                        dirs_exist_ok=True
                    )
                    os.rmdir(data_path)
                    logger.info(f"Source directory {data_path} moved \
to {user_pdfs_destination} successfully"
                    )
                except Exception as e:
                    logger.exception(f"Exception {e} raised")
                    pass

        elif file and all(cli_options_in_file):
            print(
                """
                Error: please provide either '--book_covers
                --metadata_dict --move_metadata --file'
                or the other options
                """
            )
            pass

        else:
            print("I'M PASSING")
            pass

    elif args.subcommands == 'get_single_metadata':
        # if user is not connected to internet exit
        if check_internet_connection():
            print("Internet connection is available")
        else:
            print("Internet is unavailable")
            return None

        title_query = args.title
        isbn_query = args.isbn
        file = args.file
        if title_query:
            # title_query=args.title
            # isbn=None
            get_single_book_metadata(
                file,
                book_title=title_query
            )
        elif isbn_query:
            # isbn_query = args.isbn
            # title=None
            get_single_book_metadata(
                file,
                book_isbn=isbn_query,
            )

        else:
            print("please enter a valid argument")
            return None

    elif args.subcommands == 'get_isbns_from_texts':
        source_directory = args.source_directory
        destination_directory = args.destination_directory
        isbn_text_filename = args.isbn_text_filename

        get_isbns_from_texts(
            source_directory,
            destination_directory,
            text_filename=isbn_text_filename,
        )

    else:
        print("Please provide a valid subcommand")


if __name__ == '__main__':
    main()

