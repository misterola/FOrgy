## FOrgy
FOrgy is a powerful file organizer that automatically detects ISBN from your PDF ebooks, use the detected ISBN to retrieve book metadata, automatically rename these files (if you so desire), and create for you a decent personal  library of your ebooks. FOrgy essentially helps you manage your messy PDF e-book collection, including when the "by their names we shall know them" principle does not strictly apply to your ebooks. You can also organize your collection of files (such as those in downloads folder) into folders containing unique file types

The name FOrgy is from its capabilities as a File(F) Organizer (Org) in Python (y).
<br/>
<br/>
<br/>
    
## How it works
You provide paths to directories containing your PDF ebooks and FOrgy creates a copy of those books on your laptop or PC, extracts ISBN from each book, retrieves metadata from Google's BookAPI or Openlibrary API, checks file for size, rename files, and creates a database of books in your library which you can easily search through to locate your books. FOrgy also organizes books without metadata or isbn into separate folder and further helps you locate metadata for those using other features. FOrgy can also organize contents of messy folders based on filetype. 
<br/>
<br/>
<br/>


## Project status
This project is under active development. All modules work perfectly fine albeit not yet packaged.
<br/>
<br/>
<br/>

## TODOs

- Add timestamps to book metadata (or database)

- Organize program, add more modules: isbn_api, pdf_to_text, messyforgs, regex, tests, stats
  file_system_utils (file mgt - save, rename, delete, copy), database, single_metadata_search,
  header & api key, logging, cache, temp, archive, usage stats, documentation, examples,
  CLI, Tkinter GUI, tests, CI/CD, no_isbn_metadata_search, parallel operation
  (threading/concurrency/multiprocessing/async)

- Enable user to supply list of directories containing PDF files to be operated upon and '*.pdf'
  extension is matched to autogenerate local copy for messyforg

- Enable metadata extraction from book using the current pdf text extractor

- Enable metadata download as a dictionary for all books

- Test the APIs and user internet connection before beginning operation, and automatically get header
  settings for user browser from reliable source and parse into format needed by Forgy

- Extract firstpage of book, save as jpg, standardize size for thumbnail, and treat as cover image

- Package and release version 0.1.0 of FOrgy version (with a gui with cli)