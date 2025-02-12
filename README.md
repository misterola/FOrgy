## FOrgy
FOrgy is a powerful file organizer that automatically detects ISBN from your PDF ebooks, use the detected ISBN to retrieve book metadata, automatically rename these files (if you so desire), and create for you a decent personal  library of your ebooks. FOrgy essentially helps you manage your messy PDF e-book collection, including when the "by their names we shall know them" principle does not strictly apply to your ebooks.

The name FOrgy is from its capabilities as a File(F)-Organizer-(Org)-in-Python (y).
<br/>
<br/>
<br/>
    
## How it works
You provide links to directories containing your ebooks and FOrgy creates its own local copy of those books, extracts ISBN from each book, retrieves metadata from Google's BookAPI or Openlibrary API, checks file for size, rename files, creates a database of books in your library which you can easily search through to locate your books. FOrgy also organizes books without metadata or isbn into separate folder and further helps you locate metadata for those otherwise.
<br/>
<br/>
<br/>


## Project status
This project is under active development. All modules work perfectly fine albeit not yet packageds.
<br/>
<br/>
<br/>

## TODOs

- Add timestamps to book metadata (or database), and if file already exists, move duplicated to
  duplicate_files directory.

- Organize program, add more modules: isbn_api, pdf_to_text, messyforgs, regex, tests, stats
  file_system_utils (file mgt - save, rename, delete, copy), database, single_metadata_search,
  header & api key, logging, cache, temp, archive, usage stats, documentation, examples,
  CLI, Tkinter GUI, tests, CI/CD, no_isbn_metadata_search, parallel operation
  (threading/concurrency/multiprocessing/async)

- Enable user to supply list of directories containing PDF files to be operated upon and '*.pdf'
  extension is matched to autogenerate local copy for messyforg

- Enable user to add book details (isbn, title, author) manually and automatically fetch book metadata
  from api (perhaps another module named single_isbn_api)

- Enable metadata extraction from book using the current pdf text extractor

- Design beautiful and intuitive interfaces with Agparse and Tkinter

- Add more metadata sources (Amazon, goodreads, worldcat, library of congress, librarything, thrift books, ebay)

- Test the APIs and user internet connection before beginning operation, and automatically get header
  settings for user browser from reliable source and parse into format needed by Forgy

- Automatically cache .json() downloaded by API into a redis database as a first search point
  before online API bandwith

- Extract firstpage of book, save as jpg, standardize size for thumbnail, and treat as cover image

- Add journal article DOI metadata search

- Add OCR engine e.g. pytesseract (dependency difficult to install on windows),
  EasyOCR, PyOCR, Textract for text extraction if empty text extracted by pypdf

- Configure and package FOrgy

- Release version 0.1.0 of FOrgy version (with a gui with cli)