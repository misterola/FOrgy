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
        cursor = connection.cursor()
        print("Database connection established")


# Add metadata to 'Book' table
def add_metadata_to_table(destination, table_name, values):
    with sqlite3.connect(destination) as connection:
        cursor = connection.cursor()
        print('Database connection successful')
        cursor.execute(f"INSERT INTO {table_name} VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", values)
        print('Book details added successfully')

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
        cursor.executescript(
            f"DROP TABLE IF EXISTS {table_name};"
        )
        print(f"Database table {table_name} deleted successfully")
        

# Test module
##create_library_db(home/'Desktop'/'library.db')
##create_table(home/'Desktop'/'library.db', 'Trial')



