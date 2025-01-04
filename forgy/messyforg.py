# main
from pathlib import Path
import shutil
import os
import time
##from pypdf import PdfReader
##import re
##import json
import requests
import time
import sqlite3
import random

from isbn_regex import isbn_pattern, is_valid_isbn, format_isbn
from text_extraction import extract_text
from metadata_search import (
    headers, get_metadata_google, google_api,
    google_metadata_dict, get_metadata_openlibrary,
    openlibrary_api,  openlibrary_metadata_dict
)
from database import (
    create_table, create_library_db,
    add_metadata_to_table, view_database_table,
    delete_table
)

home = Path.home()
#enable user to add more sources (up to 5) and make user specify location
#for messyforg folder
src = home/"Desktop"/"Projects"/"Forgy"/"ubooks"

dst = home/"Desktop"/"Projects"/"Forgy"/"ubooks_copy"

# copy source directory and rename as 'ubooks_copy'
try:
    shutil.copytree(src, dst)
    print('Source directory copied successfully')
except FileExistsError:
    print("Directory copied already!")

### create library database and create table "Books" in database
##with sqlite3.connect(home/'Desktop'/'Forgy'/"forgy"/'library.db') as connection:
##    cursor = connection.cursor()
##    print("Database connection established")
##    cursor.executescript(
##        """DROP TABLE IF EXISTS Books;
##            CREATE TABLE Books(Title TEXT, Subtitle TEXT, FullTitle TEXT,
##            Date_of_publication TEXT, Publisher TEXT, Authors TEXT, PageCount TEXT,
##            ISBN10 TEXT, ISBN13 TEXT, RefISBN TEXT, Source TEXT, Filesize REAL
##            );"""
##    )
##    print("Book database table created successfully")

# Create 'library.db' or connect to it if it already exists
create_library_db(home/'Desktop'/'Projects'/'Forgy'/'forgy'/'library.db')

# Delete Books table if it exists in database
delete_table(home/'Desktop'/'Projects'/'Forgy'/'forgy'/'library.db', 'Books')

# Create table 'Books' in library.db
create_table(home/'Desktop'/'Projects'/'Forgy'/'forgy'/'library.db', 'Books')


missing_metadata = home/'Desktop'/'Projects'/'Forgy'/'missing_metadata'
missing_metadata.mkdir(exist_ok=True)

##title, subtitle, full_title, date_of_publication, publisher, authors, page_count, isbn_10, isbn_13, ref_isbn, source, filesize

# iterate through each file in the new 'ubooks_copy' directory
# and extract text in first 20 pages of each file
for file in os.scandir(dst):
    #initialize dictionary with most important keys also present in json and values initialized to empty string
    #keys are named according to keys in json from api source
##    dict_of_interest = {"title":'', "subtitle":'', "publishedDate":'', "publisher":'', "authors":'', "pageCount":''}
    title=''
    subtitle=''
    full_title=''
    date_of_publication=''
    publisher=''
    authors=''
    page_count=''
    isbn_10=''
    isbn_13=''
    ref_isbn=''
    source=''
    file_size=0.0

    #initialize list of valid isbns
    valid_isbn = []
  
    values = (
        title, subtitle, full_title,
        date_of_publication, publisher, authors,
        page_count, isbn_10, isbn_13,
        ref_isbn, source, file_size
    )
    ##    values = (f'{title}', f'{date_of_publication}', f'{ISBN}', f'{source}')
    #subtitle, publisher, authors, and page_count removed due to lack of consistency
    
    if not file.name.startswith('.') and file.is_file():
        pdf_path = dst/file
        extracted_text = extract_text(pdf_path)

        # use regex to match isbn in extracted text, into matched_isbn list
        matched_isbn = []
        matched_regex = isbn_pattern.findall(extracted_text)
        matched_isbn.append(matched_regex)
        valid_isbn = format_isbn(matched_isbn)
        print(valid_isbn)
        
##        extracted_text_list = extracted_text.split(' ')
        m_dir = home/'Desktop'/'Projects'/'Forgy'/"missing_isbn"
        m_dir.mkdir(exist_ok=True)
        m_src = home/'Desktop'/'Projects'/'Forgy'/"ubooks_copy"/file

        # for files with missing isbn, save extracted text into file, and move file to missing_isbn directory
        if (m_dir.exists()==True) and (valid_isbn==[]):
            shutil.move(m_src, m_dir)
            # For files with missing isbn, generate (empty) text files to ascertain problem
            # Note on handling files in missing_isbn folder: use another set of text extractors (e.g.PyMupdf),
            # use OCR engine (e.g. tesseract) to extract text, fetch metadata from book using the current
            # pdf extractor, or generate error messages/logs if all else fails.
##            with open(f"home/'Desktop'/'Forgy'/'{pdf_path.stem}.txt'", 'a') as page_new:
            with open(f"{pdf_path.stem}.txt", 'a') as page_new:
                try:
                    page_new.write(extracted_text)
                except (FileNotFoundError,UnicodeEncodeError):
                    continue
            


##
        # use each isbn in int_isbn_list to search on openlibrary api and googlebookapi for book metadata and download in json
        # repeat same for every isbn in list. If metadata not found, print error message.
        for isbn in valid_isbn:
            try:
                # Select api randomly to avoid overworking any of the apis
                random_api = ['google', 'openlibrary']
                api = random.choice(random_api)
##                print(f'api_1 = {api}')

                if api == 'google':
                    print(f'api_1 = {api}')
                    # file metadata is either None or a tuple:(title, subtitle, full_title, date_of_publication, publisher, authors,\
                        #page_count, isbn_10, isbn_13, ref_isbn, source, filesize)
                    file_metadata = get_metadata_google(isbn, file, headers)
##                    time.sleep(5)

                    #if metadata from google is not empty, unpack tuple file_metadata into the various variables
                    if file_metadata is not None:
                        title, subtitle, full_title, date_of_publication, publisher, authors, page_count, isbn_10, isbn_13, ref_isbn, source, file_size = file_metadata
                        time.sleep(5)
                    #if metadata not available on google api, None is returned. In this case, check openlibrary api for metadata
                    else:
                        print(f'api_1a = {api}')
                        file_metadata = get_metadata_openlibrary(isbn, file, headers)
##                        time.sleep(6)
                        
                        #if metadata from openlibrary is not empty, unpack tuple file_metadata into the various variables
                        if file_metadata is not None:
                            title, subtitle, full_title, date_of_publication, publisher, authors, page_count, isbn_10, isbn_13, ref_isbn, source, file_size = get_metadata_openlibrary(isbn, file, headers)
                            time.sleep(5)
                        else:
                            #if metadata not recovered from both google and openlibrary apis, \
                            #print file_name not found and move file to missing_metadata directory
                            print(f'ISBN metadata not found for {pdf_path.stem}')
                            try:
                                m_src = home/'Desktop'/'Projects'/'Forgy'/"ubooks_copy"/file
                                shutil.move(m_src, missing_metadata) 
                                #FileNotFoundError raised if file has a missing ISBN and is already moved to
                                #missing_isbn directory. skip this whole process for file that raises this error
                            except FileNotFoundError:
                                #this is a case where file has already been moved to missing_isbn directory
                                continue
##                            except requests.exceptions.ConnectionError:
##                                #if there is no internet connection, skip the movement of file to missing isbn_directory
##                                print("Request ConnectionError. Check your internet connection")
##                                pass     #continue to relocate files (into missing_isbn and missing_metadata directories) if internet connection is poor
                else:
                    print(f'api_2 = {api}')
                    #if the randomly-selected api is openlibrary
                    file_metadata = get_metadata_openlibrary(isbn, file, headers)
##                    time.sleep(6)

                    #if metadata from openlibrary is not empty, unpack tuple file_metadata into the various variables
                    if file_metadata is not None:
                        title, subtitle, full_title, date_of_publication, publisher, authors, page_count, isbn_10, isbn_13, ref_isbn, source, file_size = get_metadata_openlibrary(isbn, file, headers)
                        time.sleep(5)
                    else:
                        print(f'api_2a = {api}')
                        #if metadata not on openlibrary api, check google api
                        file_metadata = get_metadata_google(isbn, file, headers)
##                        time.sleep(5)

                        #if metadata is recovered from googleapi, unpack tuple file_metadata into the various variables
                        if file_metadata is not None:
                            (title, subtitle, full_title,
                             date_of_publication, publisher, authors,
                             page_count, isbn_10, isbn_13,
                             ref_isbn, source, file_size) = file_metadata
                            time.sleep(5)
                        else:
                            #if metadata not recovered from both apis, extract important file data from pdf_reader extracted metadata
                            print(f'ISBN metadata not found for {pdf_path.stem}')
                            try:
                                m_src = home/'Desktop'/'Projects'/'Forgy'/"ubooks_copy"/file
                                shutil.move(m_src, missing_metadata)
                                #FileNotFoundError raised if file has a missing ISBN and is already moved to
                                #missing_isbn directory. skip this whole process for file that raises this error
                            except FileNotFoundError:
                                continue
            except ConnectionError:
                print("Connection Error")
                continue
            except TimeoutError:
                print("Timeout Error")
                continue
            except requests.exceptions.ConnectTimeout:
                print("Request ConnectTimeoutError")
                continue
            except requests.exceptions.HTTPError:
                print("Request HTTPError")
                continue
            except requests.exceptions.ConnectionError:
                print("Request ConnectionError. Check your internet connection", end='\n')
                continue
            except urllib3.exceptions.ReadTimeoutError:
                print("ReadTimeoutError")
                continue
            

    #assign retrieved metadata to tuple value for easy addition to database. this updates the initialized values
    values = (f'{title}', f'{subtitle}', f'{full_title}', f'{date_of_publication}', f'{publisher}',
          f'{authors}', f'{str(page_count)}', f'{isbn_10}', f'{isbn_13}', f'{ref_isbn}', f'{source}', f'{float(file_size):.2f}')

    print(values)

#........#
#create a function in fileutils to change each variable used in naming into standard format acceptable to MS and Linux OS.
# This new variable is then used in naming file        
    # for file with retrieved metadata, rename and do not move
    if (missing_metadata.exists()==True) and (valid_isbn!=[]) and values != ('', '', '', '', '', '', '', '', '', '', '', '0.00') and len(list(set(values[0:6])))>=3: #default is 4 out of 6
        #rename file in its original ubooks directory
        old_file_name = pdf_path
        dst_dir = dst
        new_file_name = fr'{title}.pdf'
        new_file_path = os.path.join(dst_dir, new_file_name)

        try:
            os.rename(pdf_path,new_file_path)
        except FileNotFoundError:
            pass
        except FileExistsError: #device how to handle duplicates by attacching time to file name
            pass
        
        # add retrieved metadata to database
##        with sqlite3.connect(home/'Desktop'/'Forgy'/'forgy'/'library.db') as connection:
##            cursor = connection.cursor()
##            print('Database connection successful')
##            cursor.execute("INSERT INTO Books VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", values)
##            print('Book details added successfully')
##
##            #check content of database
##            for row in cursor.execute("SELECT Title FROM Books;").fetchall():
##                print(row)

        add_metadata_to_table(home/'Desktop'/'Projects'/'Forgy'/'forgy'/'library.db', 'Books', values)
        view_database_table(home/'Desktop'/'Projects'/'Forgy'/'forgy'/'library.db', 'Books')

    # for files with missing missing_metadata, move file to missing_isbn directory
    else:
        ##    missing_metadata = home/"Desktop"/"MessyFOrg"/"missing_metadata"
        ##    missing_metadata.mkdir(exist_ok=True)
        m_src = home/'Desktop'/'Projects'/'Forgy'/"ubooks_copy"/file
        try:
            shutil.move(m_src, missing_metadata) 
            #FileNotFoundError raised if file has a missing ISBN and is already moved to
            #missing_isbn directory. skip this whole process for file that raises this error
        except FileNotFoundError:
            pass
        #if there is no internet connection, don't move file
        except requests.exceptions.ConnectionError:
            print("Request ConnectionError. Check your internet connection")
            pass


#.......#
#TODO: rename book with format here
##    new_dst = dst/f"{full_title}, {authors} {date_of_publication}.{publisher}.pdf"

        #TODO: Separate out my user key and browser header and import them
                #into the program and set .gitignore for them
                #DONE

        #TODO: Enable user to specify if to delete content of database or not DONE

        #TODO: For every extracted isbn, check database ref_isbn to ensure that is isn't there.

        #TODO: Redesign project structure, set-up GitHub repo and select license (AGPL) ONGOING
        
        #TODO: rename book using name from metadata if metadata retrieval
            #from ISBN is successful

        #TODO: Lint code with Flake8, Pylint, and/or ruff. Configure and package

        #TODO: organize program, add more modules: isbn_api, pdf_to_text, messyforgs, regex, tests,
            #file_system_utils (file mgt - save, rename, delete, copy), database, single_metadata_search,
            #header & api key, logging, cache, temp, archive, usage stats, documentation, example,
            #CLI, Tkinter GUI, tests, CI/CD, no_isbn_metadata_search, examples, database, multiprocessing
            #via asynchronous performance, threading, or concurrency in the most efficient way

        #TODO: Enable user to supply list of directories containing PDF files to be operated upon and '*.pdf'
            #extension is matched to autogenerate local copy for messyforg

        #TODO: Enable user to specify a folder or list of folders containing messy files to be organized and a new
            #organized folder is created in a folder of choice. This util creates a separate folder for each unique file
            #type. The folder containing PDF files can be used as input for FOrgy isbn_metadata utils.

        #TODO: Design a beautiful and intuitive GUI interface for app (commandline interface should also be embedded)

        #TODO: Design beautiful and intuitive CLI for app

        #TODO: Add grouping files in given directory based on format before carying out operation
            #on the pdfs of journal articles and books

        #TODO: For books with missing ISBN in preliminary pages, check last ten pages. This should
            #be done on individual book (publishers like pack publisher advert books in last pages
            #of their books and this means there are unrelated isbns at back of the books.

        #TODO: Create a directory of 10 creative commons-licensed ebooks and place in tests folder for the tests

        #TODO: Enable user to add book details manually or by supplying some title and isbn to aid to aid search
            #(perhaps another module named single_isbn_api)

        #TODO: Test the APIs and user internet connection before beginning operation, and automatically get header
            # settings for user browser from reliable source and parse into format needed by Forgy

        #TODO: Download 10 open source ebooks and place in a folder so users can practice with and test API with

        #TODO: Automatically cache .json() downloaded by API into a redis database as a first search point
            #before online API bandwith 

        #TODO: If file already exists, ensure timestamp is added to a filename before adding to database

        #TODO: Extract firstpage of book, save as jpg, standardize size for thumbnail, and treat as cover image

        #TODO: Add timestamp to book metadata (or database)

        #TODO: Check database for book ref_isbn before going online to search for it. This will ensure program can
            #continue from where it stops without cache

        #TODO: Create the first full-featured GUI with Tkinter

        #TODO: Enable user to enter title and author and automatically fetch book metadata online

        #TODO: add OCR engine e.g. pytesseract (dependency difficult to install),
            #EasyOCR, PyOCR, Textract for text extraction if empty text extracted by pypdf

        #TODO: Add journal article DOI tools
        
                

#OBSERVED REASONS FOR MISSING ISBN IN EXTRACTED TEXT
#isbn pattern not matching: read isbn standard and write a better regex
#text not having any isbn: follow instruction above 'with statement'
#text cannot be extracted: use OCR
#incomplete isbn digit (e.g. 9 digits): follow instruction above

#APIs
#googlebooks api: https://www.googleapis.com/books/v1/volumes?q=isbn:0-444-82409-x
#openlibrary api: https://openlibrary.org/isbn/9781119284239.json



                

            

        
            
