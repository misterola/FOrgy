## FOrgy
FOrgy is a powerful file organizer that automatically detects ISBN from your PDF ebooks, use the detected ISBN to retrieve book metadata, automatically rename these files (if you so desire), and create for you a decent personal  library of your ebooks. FOrgy essentially helps you manage your messy PDF e-book collection, including when the "by their names we shall know them" principle does not strictly apply to your ebooks.

The name FOrgy is from its capabilities as a File(F)-Organizer-(Org)-built-using-Python (y).
<br/>
<br/>
<br/>
    
## How it works
You provide links to directories containing your ebooks and FOrgy creates its own local copy of those books, extracts ISBN from each book, retrieves metadata from Google's BookAPI or Openlibrary API, checks file for size, rename files, creates a database of books in your library which you can easily search through to locate your books. FOrgy also organizes books without metadata or isbn into separate folder and further helps you locate metadata for those otherwise.

<br/>
## Project status
This project is under active development. All modules work perfectly fine albeit not yet packaged.

<br/>
# TODOs

- TODO: rename book with format here new_dst = dst/f"{full_title}, {authors} {date_of_publication}.{publisher}.pdf"

- TODO: Separate out my user key and browser header and import them into the program and set .gitignore for them. DONE

- TODO: Enable user to specify if to delete content of database or not DONE

- TODO: For every extracted isbn, check database ref_isbn to ensure that is isn't there. DONE

- TODO: Redesign project structure, set-up GitHub repo and select license (AGPL) DONE

- TODO: rename book using name from metadata if metadata retrieval from ISBN is successful DONE

- TODO: Lint code with Flake8, Pylint, and/or ruff. DONE

- TODO: Configure and package FOrgy

- TODO: Add metadata retrieval date to database columnss

- TODO: organize program, add more modules: isbn_api, pdf_to_text, messyforgs, regex, tests, stats
  file_system_utils (file mgt - save, rename, delete, copy), database, single_metadata_search,
  header & api key, logging, cache, temp, archive, usage stats, documentation, example,
  CLI, Tkinter GUI, tests, CI/CD, no_isbn_metadata_search, examples, database, multiprocessing
  via asynchronous performance, threading, or concurrency in the most efficient way

- TODO: Enable user to supply list of directories containing PDF files to be operated upon and   '*.pdf'
  extension is matched to autogenerate local copy for messyforg

- TODO: Enable user to specify a folder or list of folders containing messy files to be organized and   a new organized folder is created in a folder of choice. This util creates a separate folder   for each unique file type. The folder containing PDF files can be used as input for FOrgy   isbn_metadata utils.

- TODO: Design a beautiful and intuitive GUI interface for app (commandline interface should also be   embedded)


- TODO: Design beautiful and intuitive CLI for app

- TODO: Add more metadata sources (Amazon, goodreads, worldcat, library of congress, librarything,   thrift books, ebay)

- TODO: Add grouping files in given directory based on format before carying out operation
  on the pdfs of journal articles and books

- TODO: For books with missing ISBN in preliminary pages, check last ten pages. This should
  be done on individual book (publishers like pack publisher advert books in last pages
  of their books and this means there are unrelated isbns at back of the books.

- TODO: Create a directory of 10 creative commons-licensed ebooks and place in tests folder for the   tests

- TODO: Enable user to add book details manually or by supplying some title and isbn to aid to aid     search (perhaps another module named single_isbn_api)

- TODO: Test the APIs and user internet connection before beginning operation, and automatically get    header settings for user browser from reliable source and parse into format needed by Forgy

- TODO: Download 10 open source ebooks and place in a folder so users can practice with and test API   with

- TODO: Automatically cache .json() downloaded by API into a redis database as a first search point
  before online API bandwith

- TODO: If file already exists, ensure timestamp is added to a filename before adding to database

- TODO: Extract firstpage of book, save as jpg, standardize size for thumbnail, and treat as cover   image

- TODO: Add timestamp to book metadata (or database)

- TODO: Check database for book ref_isbn before going online to search for it. This will ensure     program can continue from where it stops without cache DONE

- TODO: Create the first full-featured GUI with Tkinter

- TODO: Enable user to enter title and author and automatically fetch book metadata online 

- TODO: add OCR engine e.g. pytesseract (dependency difficult to install),
  EasyOCR, PyOCR, Textract for text extraction if empty text extracted by pypdf

- TODO: release version 0.1.0 of FOrgy version (has a gui with cli but not the journal article doi   search)

- TODO: Add journal article DOI tools



