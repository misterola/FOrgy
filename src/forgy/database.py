import sqlite3
from pathlib import Path

home = Path.home()

# Create a 'library.db' database
def create_library_db(destination, library_name = 'library.db'):
    """Create a library.db file to store retrieved book metadata in.

        If you are specifying a database or directory, it must exist at destionation.
        You can provide a destination only or a destination with preferred library name.
        if both are provided and same, database connection established and closed.
    """
    # Check if destionation is a directory   
    if not Path(destination).is_dir() and not Path(destination).name.endswith('.db'):
        print(f"{destination} is not a valid directory or database path. Database connection unsuccessful")
        return None
    # if destination is a directory and not a database file, create database file in directory
    if not Path(destination).name.endswith('.db') and Path(destination).is_dir():
        # print(f"Invalid database path {destination} provided")
        print(f"A parent directory for database is provided")
        database_path = Path(destination)/f"{library_name}"
        # return None
        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()  # noqa: F841  # no use for cursor variable
            print(f"New database created at {database_path})")
            return None
    # if .db path provided and it already exists, try to establish connection with it
    if Path(destination).name.endswith('.db') and Path(destination).exists():
        print(f"Database file already exists at destination {destination})")
        try:
            with sqlite3.connect(destination) as connection:
                cursor = connection.cursor()  # noqa: F841  # no use for cursor variable
                print("Database connection established")
                return None
        except Exception as e:
            print(f"Error {e} occured during operation. Database connection not successful")
            return None
    # if db path provided but it doesn't exist
    else:
        print(f"The specified database {destination} does not exist")
    return None


# Create 'Books' table in 'library.db' database
def create_db_and_table(destination, table_name="Books", db_name='library.db', delete_table=True):  # deletes table if it exists
    """.db file must first be created by just establishing connection once. call create_library_db once with the correct path

    Create database and Books table in database. Existing table delete in database by default.
    Same is the case in underlying functions.

    Database can be a directory or .db file path.
    """
    # correct inconsistent naming on columns
    print(f"DESTINATION: {destination}")
    if not Path(destination).name.endswith('.db'):
        print("The given destination is not a database")

        if not Path(destination).is_dir():
            print("The given destination is not a valid directory path")
            return None
    print(f"The DESTINATION CHECK: {Path(destination).exists()}")
    # If the database already exists, check if it contains Books database
    if Path(destination).is_dir() and not Path(destination).name.endswith('.db'):
        create_library_db(destination)

    db_path = Path(destination)/f"{db_name}"
    print(db_path)
    
    if Path(destination).exists() and db_path.name.endswith('.db'):
        print("Database already exists")
        # Check if table_name is in database and possibly delete
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            # Parametric query to select table from database. 
            query = f"SELECT name FROM sqlite_master WHERE type='table' AND name=?;"""
            cursor.execute(query, (table_name,))
            table_in_db = cursor.fetchone()  # returns a tuple containing one element (the name of the table) format: ("Books",)
            print(f"Table {table_name} value retrieved: {table_in_db}")

            if table_in_db and delete_table:
                print(f"{table_name} table already exists in database")
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                print(f"Existing {table_name} database deleted successfully")
            elif table_in_db and not delete_table:
                print(f"{table_name} table already exists in database and will be adopted")
                return None
            # Cases: not table_in_db and delete_table, not table_in_db and not delete_table
            else:
                pass
            # Create a fresh "Books" table
            cursor.execute(
                # primary key and/or unique constraints may be necessary to prevent duplication of title and date_of_publication
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
            print(f"New {table_name} database table created successfully")
    else:
        # If destination path does not exist
        print("Database table creation unsuccessfull. Use the create_library_db function to create .db file")
        return None      


# Add metadata to 'Book' table
def add_metadata_to_table(destination, table_name, values):
    with sqlite3.connect(destination) as connection:
        cursor = connection.cursor()
        print("Database connection successful")
        cursor.execute(
            f"INSERT INTO {table_name} VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
            values,
        )
        print("Book details added successfully")


# Check content of database
def view_database_table(source, table_name):
    with sqlite3.connect(source) as connection:
        # connection.isolation_level = None
        cursor = connection.cursor()
        for row in cursor.execute("SELECT Title FROM Books;").fetchall():
            print(row)
        


# Delete table from database
def delete_table(source, table_name):
    with sqlite3.connect(source) as connection:
        cursor = connection.cursor()
        cursor.executescript(f"DROP TABLE IF EXISTS {table_name};")
        print(f"Database table {table_name} deleted successfully")


# Check database for existence of title in Title
def titles_in_db(database, table):
    # Extract title from database as a set. Number of items in set is number of items added to database
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(f"SELECT Title FROM {table};")
            existing_db_titles = cursor.fetchall()  # Has the form [('title1',), ('title2',)]
            ref_title_set = set()
            for titl in existing_db_titles:
                ref_title_set.add(titl[0])
            #return ref_title_set
        except sqlite3.OperationalError:
            ref_title_set = set()
            # re
    return ref_title_set


def api_utilization(database, table):
        # Extract 'Source from database as a list. Sources are either openlibrary or google
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT Source FROM {table};")
        api_sources = cursor.fetchall()  # Has the form [('api1',), ('api2',)]
        api_sources_list = []
        for source in api_sources:
            api_sources_list.append(source[0])
    return api_sources_list

def get_all_metadata(database, table):
    """Function makes book title key and book metadata value in all_metadata dictionary"""
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table};")
        book_metadata = cursor.fetchall()
        all_metadata = {}
        for entry in book_metadata:
            all_metadata[entry[0]] = entry
    return all_metadata


def get_database_columns(database, table, columns=["Title", "ImageLink"]):
    """Function to get values of columns in database table.

    This is used to retrieve book titles/isbns and correspoding image_url
    """
    database_columns = ", ".join(columns)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT {database_columns} FROM {table};")
        # Get book metadata. The format is [(title, image_url),...(title, image_url)]
        book_metadata = cursor.fetchall()
##        for val in book_metadata:
##            title = val[0]
##            image_url = val[1]
##            print(f"Title: {title}\nImage_url: {image_url}")
    return book_metadata



# tests: all_funcs    

# Test module
# Create_library_db(home/'Desktop'/'library.db')
# Create_table(home/'Desktop'/'library.db', 'Trial')
