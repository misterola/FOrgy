"""
A module to carryout various operations on
db using sqlite3 in the python standard library
"""


import sqlite3
from pathlib import Path

from .logger import create_logger
from .isbn_regex import add_to_ref_isbn_set, isbns_in_set


logger = create_logger("database")


def create_library_db(destination, library_name='library.db'):
    """
    Create a library.db file to contain retrieved book metadata.

    A database (existing .db file path) or a directory path must
    be specified and both must exist at the provided path. If a
    directory path is provided, the database(.db file) is created
    inside it and if it is a database, a connection is made to it
    to ascertain it's suitability. The database is then closed.
    """
    if (
        not Path(destination).is_dir()
        and not Path(destination).name.endswith('.db')
    ):
        logger.error(
            f"{destination} is not a valid directory or database\
path. Database connection unsuccessful"
        )
        return None

    # If destination is a directory and not a database file,
    # create database file in directory
    if (
        not Path(destination).name.endswith('.db')
        and Path(destination).is_dir()
    ):
        logger.info("A parent directory for database is provided")
        database_path = Path(destination)/f"{library_name}"

        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()  # noqa: F841  # no use for cursor
            logger.info(f"New database created at {database_path})")
            return None

    # if .db path provided and it already exists, try to establish
    # connection with it
    if (
        Path(destination).name.endswith('.db')
        and Path(destination).exists()
    ):
        logger.info(
            f"Database file already exists at destination {destination}"
        )

        try:
            with sqlite3.connect(destination) as connection:
                cursor = connection.cursor()  # noqa: F841  # no use for cursor
                logger.info("Database connection established")
                return None
        except Exception as e:
            logger.exception(
                f"""
                Error {e} occured during operation.
                Database connection not successful
                """
            )
            return None

    # if db path provided but it doesn't exist
    else:
        logger.exception(
            f"The specified database {destination} does not exist"
        )
    return None


def create_db_and_table(
    destination,
    table_name="Books",
    db_name='library.db',
    delete_table=True  # deletes table if it exist
):

    """
    Create a database (library.db), and 'Books' table within it,
    inside a valid directory

    The database can be a directory or .db file path. If a directory
    is provided, the create_library_db is used to create library.db
    file in destination directory, and 'Books' table is created within
    the library.db database.
    """
    if not Path(destination).name.endswith('.db'):
        logger.error("The given destination is not a database")

        if not Path(destination).is_dir():
            logger.error(
                "The given destination is not a valid directory path"
            )
            return None

    # If the database already exists, verify if it contains Books database
    if Path(destination).is_dir() and not Path(destination).name.endswith('.db'):
        create_library_db(destination)

    db_path = Path(destination)/f"{db_name}"
    logger.info(f"The databaese path: {db_path}")

    if Path(destination).exists() and db_path.name.endswith('.db'):
        logger.info("Database already exists")

        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()

            # To check if database contains "Books" table, we use parametric query
            # to select tables from database.
            query = (
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
            )
            cursor.execute(query, (table_name,))

            # returns a tuple containing one element (the name of the table)
            # format: ("Books",)
            table_in_db = cursor.fetchone()

            logger.info(f"Table {table_name} value retrieved: {table_in_db}")

            # Check if a table is in database (the returned tuple is not empty)
            if table_in_db and delete_table:
                logger.info(f"{table_name} table already exists in database")
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                logger.info(f"Existing {table_name} database deleted successfully")
            elif table_in_db and not delete_table:
                logger.info(
                    f"{table_name} table already exists in database and will be adopted"
                )
                return None

            # Cases:
            # not table_in_db and delete_table,
            # not table_in_db and not delete_table
            else:
                pass

            # Create a new "Books" table
            cursor.execute(
                # primary key and/or unique constraints may be necessary
                # to prevent duplication of title and date_of_publication
                f"""CREATE TABLE {table_name}(
                        Title TEXT,
                        Subtitle TEXT,
                        FullTitle TEXT,
                        Date_of_publication TEXT,
                        Publisher TEXT,
                        Authors TEXT,
                        PageCount TEXT,
                        ISBN10 TEXT,
                        ISBN13 TEXT,
                        RefISBN TEXT,
                        Source TEXT,
                        Filesize REAL,
                        ImageLink TEXT,
                        Date_created TEXT
                    );"""
               )
            logger.info(
                f"New {table_name} database table created successfully"
            )
    else:
        # If destination path does not exist
        logger.info(
            """
            Database table creation unsuccessfull. Use the
            create_library_db function to create .db file
            """
        )
        return None


def add_metadata_to_table(destination, table_name, values):
    """Add retrieved metadata values to 'Book' table in database"""
    with sqlite3.connect(destination) as connection:
        cursor = connection.cursor()
        logger.info("Database connection successful")
        cursor.execute(
            f"INSERT INTO {table_name} VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
            values,
        )
        logger.info("Book details added successfully")


def view_database_table(source, table_name):
    """Function to view titles of all books in database"""
    with sqlite3.connect(source) as connection:
        # connection.isolation_level = None
        cursor = connection.cursor()
        for row in cursor.execute("SELECT Title FROM Books;").fetchall():
            print(row)


def delete_table(source, table_name):
    """Delete table from database"""
    with sqlite3.connect(source) as connection:
        cursor = connection.cursor()
        cursor.executescript(f"DROP TABLE IF EXISTS {table_name};")
        logger.info(f"Database table {table_name} deleted successfully")


def titles_in_db(database, table):
    """
    Check database for existence of a given title in Title
    column of database.
    """
    # Extract title from database as a set. Number of items in set
    # is number of items added to database
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(f"SELECT Title FROM {table};")

            # Titles in db is extracted as a list of tuples
            # The format: [('title1',), ('title2',)]
            existing_db_titles = cursor.fetchall()

            ref_title_set = set()

            for titl in existing_db_titles:
                ref_title_set.add(titl[0])

            # connection.commit() to ensure changes are saved before
            # closing db in all cases of return within a context manager
            return ref_title_set

        except sqlite3.OperationalError:
            ref_title_set = set()
            # return ref_title_set

    return ref_title_set


def api_utilization(database, table):
    """
    Function to extract all API sources on Sources column
    of Books table as a list.
    """
    # Extract 'Source' column from database as a list.
    # Sources are either openlibrary or google domain name
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT Source FROM {table};")

        # A list of tuples is returned: the format: [('api1',), ('api2',)]
        api_sources = cursor.fetchall()
        api_sources_list = []
        for source in api_sources:
            api_sources_list.append(source[0])

    return api_sources_list


def get_all_metadata(database, table):
    """
    Function makes book title key and book metadata value
    in all_metadata dictionary.
    """
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table};")
        book_metadata = cursor.fetchall()
        all_metadata = {}
        for entry in book_metadata:
            all_metadata[entry[0]] = entry

    return all_metadata


def show_all_database_content(database, table):
    """Function to get all metadata values from database."""
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table};")
        book_metadata = cursor.fetchall()
        for val in book_metadata:
            print()


def get_database_columns(database, table, columns=["Title", "ImageLink"]):
    """
    Function to fetch all book metadata from database.

    Book metadata format: [(title, image_url),...(title, image_url)]
    """
    database_columns = ", ".join(columns)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT {database_columns} FROM {table};")
        # Get book metadata. The format is
        book_metadata = cursor.fetchall()

    return book_metadata


def is_isbn_in_db(database, table, isbn_list):
    """
    Check database for existence of isbns in isbn_list in
    the RefISBN column.
    """
    # Extract isbn from database as a set (for better performance)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT RefISBN FROM {table};")

        # existing_db_refisbns has the format:
        # [('9780873897365',), ('9781636940274',)]
        existing_db_refisbns = cursor.fetchall()
        ref_isbn_set = set()
        for isbn in existing_db_refisbns:
            add_to_ref_isbn_set(isbn[0], ref_isbn_set)

    # Are extracted values in list present in set of db ref_isbns
    return isbns_in_set(isbn_list, ref_isbn_set)
