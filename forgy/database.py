import sqlite3
from pathlib import Path

home = Path.home()


# Create 'Books' table in 'library.db' database
def create_table(destination, table_name):
    with sqlite3.connect(destination) as connection:
        cursor = connection.cursor()
        cursor.executescript(
            f"""CREATE TABLE {table_name}(
                Title TEXT, Subtitle TEXT, FullTitle TEXT,
                Date_of_publication TEXT, Publisher TEXT, Authors TEXT,
                PageCount TEXT, ISBN10 TEXT, ISBN13 TEXT,
                RefISBN TEXT, Source TEXT, Filesize REAL
                );"""
        )
        print("Book database table created successfully")


# Create a 'library.db' database
def create_library_db(destination):
    with sqlite3.connect(destination) as connection:
        cursor = connection.cursor()  # noqa: F841  # no use for cursor variable
        print("Database connection established")


# Add metadata to 'Book' table
def add_metadata_to_table(destination, table_name, values):
    with sqlite3.connect(destination) as connection:
        cursor = connection.cursor()
        print("Database connection successful")
        cursor.execute(
            f"INSERT INTO {table_name} VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
            values,
        )
        print("Book details added successfully")


# Check content of database
def view_database_table(source, table_name):
    with sqlite3.connect(source) as connection:
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
        cursor.execute(f"SELECT Title FROM {table};")
        existing_db_titles = cursor.fetchall()  # Has the form [('title1',), ('title2',)]
        ref_title_set = set()
        for titl in existing_db_titles:
            ref_title_set.add(titl[0])
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
# tests: all_funcs    

# Test module
# Create_library_db(home/'Desktop'/'library.db')
# Create_table(home/'Desktop'/'library.db', 'Trial')
