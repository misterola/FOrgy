<p align="center">
    <img alt="forgy_logo" src="https://github.com/misterola/forgy/blob/dev/forgy_logo.png">
</p>

------------------------

# forgy
**forgy** is a powerful file organizer and e-book manager with a Command-Line Interface that enables users to retrieve e-book metadata, and rename PDF e-books with ease. 

Forgy can automatically extract valid ISBNs from many e-books, rename 'unknown' books using retrieved metadata (including cover thumbnails!), organize a messy file collection into folders according to their formats, and much more. This project arose due to the perceived need to reliably rename e-books with their correct titles while keeping them organized on a computer, without installing and depending on heavy software with a busy interface. 

The goal is to easily create and maintain a decent personal PDF e-book library, especially when identifying PDF e-books by their names becomes difficult. The name Forgy is from the project's roots as a file(f) organizer (org) in Python (y).
<br/>
<br/>
## Table of Contents
- [Setting up forgy (Windows)](#setting-up-forgy-windows-10)
- [Usage](#usage)
- [Example](#example)
- [License](#license)
- [Dependencies](#dependencies)
<br/>

## Setting up forgy (Windows 10)
1. Verify that you have python installed on your computer.
   
   Open windows command prompt (windows button + cmd + enter) and check python version using ```python --version```+ enter. You should see
   your python version, which in this case is 3.12.4.

   If you don't have python installed, you can download it [here](https://www.python.org/downloads)
   <br/>
   <br/>
2. Navigate to directory where you want to keep the cloned forgy that you are about to download.

   To download into desktop directory, use the change directory command as shown below.
   ```cmd
   cd desktop
   ```
   Alternatively, you can create a directory to contain cloned forgy using ```mkdir new_directory_name``` at the command prompt.
   <br/>
   <br/>
3. Clone the repository.
   
   You need git installed to clone a repo on Windows. If you don't already use git on your computer, download git for windows [here](https://git-scm.com/downloads/win) ,
   open the downloaded git bash, navigate to the destination directory for the cloned forgy repo (desktop in this case) and clone repository using the clone command as shown below.
   ```bash
   cd desktop
   ```

   ```
   git clone https://github.com/misterola/forgy.git
   ```
   <br/>
4. Re-open Windows command prompt and navigate to the project root directory (desktop/forgy).
   You use the command prompt for the rest of the process.
   ```cmd
   cd forgy
   ```
   <br/>
5. Create virtual environment
   
   ```cmd
   python -m venv venv
   ```
   <br/>
6. Activate virtual environment.
   
   You should see '(venv)' in front of your current path in command prompt after activating virtual environment.
    ```cmd
    venv\Scripts\activate
    ```
    <br/>
7. Install dependencies
    
   ```cmd
   python -m pip install -r requirements.txt
   ```
   <br/>
8. You can leave virtual environment at any point using ```deactivate``` command prompt
   <br/>
   <br/>
## Usage
Sub-commands in forgy can be currently accessed via the CLI.
1. Navigate to source directory which contains the CLI app
   ```cmd
   cd src
   ```
   
   <br/>
2. To view help page to understand all subcommands available
   ```cmd
   python -m forgy-app -h
   ```
   Sample output:
   ```
   usage: forgy-app [-h] [--version]
                 {get_metadata,get_isbns_from_texts,get_single_metadata,organize_extension,get_files_from_dir,copy_directory_contents,move_directories,delete_files_directories}
                 ...

    A powerful file organizer, ebook manager, and book metadata extractor in
    python
	
    options:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
	
    forgy Operations:
	Valid subcommands
	
	{get_metadata,get_isbns_from_texts,get_single_metadata,organize_extension,get_files_from_dir,copy_directory_contents,move_directories,delete_files_directories}
	    get_metadata        retrieve PDF e-book metadata and rename several PDF
	                        e-books with it
	    get_isbns_from_texts
	                        extract isbns from several PDF e-books contained in
	                        source_directory
	    get_single_metadata
	                        get metatada for a single book using file path and
	                        title or isbn
	    organize_extension  organize files by extension or format
	    get_files_from_dir  aggregate pdf files from various directories/sources
	    copy_directory_contents
	                        copy contents of source directory into destination
	                        directory (files and directories included)
	    move_directories    move directories to another destination
	    delete_files_directories
	                        delete files or directo- ries in source directory.
	                        WARNING: permanent operation!
	
   Welcome to forgy-app v0.1.0!
   ```
   <br/>

From the above, there are eight major subcommands you can use to carryout various operations on your files. These include:
<br/>
- get_metadata
- get_isbns_from_texts
- get_single_metadata
- organize_extension
- get_files_from_dir
- copy_directory_contents
- move_directories
- delete_files_directories
<br/>

The functions of sub-commands are as stated in the CLI help shown earlier. You can always view usage of sub-commands using: ```python -m forgy-app sub-command-name --help```.
<br/>

Note that the get_metadata sub-command requires an optional GoogleBooks API key. The get_metadata sub-command in **forgy** is built on two major books API (Google and Openlibrary) which are freely available. 

Openlibrary API is available for free with some API request per sec limit to enforce responsible usage. Google BooksAPI has a default quota of about 1000 API calls
per month which can theoretically be increased. 

To avoid overwhelming a single API and provide access to more book metadata, providing Google BooksAPI key is important and forgy
randomly selects between these two APIs for metadata retrieval.

Google BooksAPI key can be obtained via [Google Cloud Console](https://console.cloud.google.com/) . 

```text
On the home page:
Select a project if existing or Create new (right beside Google Console Logo) > New Project > Create > Left hand menu > APIs and Services > Credentials >
> Create Credentials > API Key (API key created and displayed in dialog box. Copy it and use) > Close dialog > API key (optional) > API Restrictions >
> Restrict key > Google Cloud APIs > OK
```

## Example
Task: extracting valid isbns from all PDF books in a directory

Here, we want to extract ISBNs from books located in a particular directory. First, we view CLI help to locate a subcommand to do that. Looking at the sample output above (see usage section), the get_isbns_from_texts subparser is the one that does this. For the sake of simplicity, we keep all PDF ebooks inside one folder and then we view help page for get_isbns_from_texts subcommand to understand how to use it.
```cmd
python -m forgy-app get_isbns_from_texts -h
```
Sample output:

```
usage: forgy-app get_isbns_from_texts [-h]
                                      [--isbn_text_filename ISBN_TEXT_FILENAME]
                                      source_directory destination_directory

Extract valid ISBNs from PDF files as a dictionary with filenames as keys and
valid ISBNs as a list of values

positional arguments:
  source_directory      provide source directory for input pdf files
  destination_directory
                        provide destination for text file containing book
                        titles and extracted isbns

options:
  -h, --help            show this help message and exit
  --isbn_text_filename ISBN_TEXT_FILENAME
                        provide name of text file containing extracted e-book
```

The usage of the subcommand is shown on the first line in the help screen above. Only two postional arguments (source_directory and destination_directory) are compulsory here, while the
the name of the text file to contain extracted valid ISBNs is optional (the default name is 'extracted_isbns.txt'). 

The source_directory contains PDF files to extract ISBNs from and the destination_directory is the location on your computer where the file containing extracted ISBNs is saved. The format of the output is a text file containing file names as keys and extracted valid ISBNs as a list of values and the ISBN text file is found in destination directory defined.

The command to extract ISBNs from texts, contained in source-directory into a text file located in destination-directory with both source-directory and destination directory located in the user desktop directory:
```cmd
python -m forgy-app get_isbns_from_texts C:\Users\User-name\Desktop\source-directory C:\Users\User-name\Desktop\destination-directory
```
Once you press the enter key, ISBN extraction takes place on all PDF files in C:\Users\User-name\Desktop\source-directory
<br/>
<br/>
<br/>

## License
**forgy** is available under [AGPL3](https://www.gnu.org/licenses/agpl-3.0.txt) open-source license

## Dependencies
- [requests - make HTTP request](https://github.com/psf/requests)
- [pypdf - extract text from PDF ebook](https://github.com/py-pdf/pypdf)
- [dotenv - manage user Google BooksAPI key-value pairs as environment variables](https://github.com/theskumar/python-dotenv)
- [reportlab - to create pdf file in some test](https://pypi.org/project/reportlab)
- [flake8 - format code](https://flake8.pycqa.org/en/latest/)

## TODO
- Package and release version 0.1.0 of FOrgy version (with a CLI and/or GUI)
