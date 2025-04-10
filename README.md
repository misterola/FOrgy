<p align="center">
    <img alt="forgy_logo" src="https://github.com/misterola/forgy/blob/dev/forgy_logo.png">
</p>

------------------------

# forgy
**forgy** is a powerful file organizer and ebook manager with a Command-Line Interface that enables you to retrieve e-book metadata, and rename or organize your pdf e-books with ease. 
It can automatically extract valid ISBNs from a large number of e-books, automatically rename books using retrieved reliable metadata (including cover thumbnails!), organize your
messy file collection into folders according to their formats, and much more. This project arose as a result of the need to reliably rename my ebooks with their correct names while
keeping them organized on my computer without installing and depending on heavy software with busy interface. The goal is to easily create and maintain a decent personal PDF e-book 
library for messy PDF e-book collection with ease, especially when the "by their names we shall know them" principle does not strictly apply. The name forgy is from its roots as a 
file(f) organizer (org) in python (y).
<br/>
<br/>
## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)
- [License](#license)
- [Dependencies](#dependencies)

## Installation (Windows 10)

1. Verify that you have python installed
   Open windows command prompt (windows button + cmd + enter) and check python version. The version used here is  3.12.x.
   ```cmd
   python --version
   ```
   If you don't have python installed, you can download [here](https://www.python.org/downloads)
   <br/>
2. Navigate to directory where you want to download forgy into. To download into desktop (for example)
   ```cmd
   cd desktop
   ```
   Alternatively, you can create a directory to contain forgy download using command prompt using ```mkdir new_directory_name```
   <br/>
3. Clone the repository
   You need git installed to achieve this on Windows. Download git for windows [here](https://git-scm.com/downloads/win) ,  Open the downloaded git bash,
   navigate to the directory that will contain your forgy download (we use desktop in this case) and clone repository.
   ```bash
   cd desktop
   git clone https://github.com/misterola/forgy.git
   ```
   <br/>
5. Open Windows command prompt (windows button + cmd + enter) and navigate into the project root directory (desktop/forgy). You use the commandline henceforth
   ```cmd
   cd forgy
   ```
   <br/>
6. Create virtual environment
   ```cmd
   python -m venv venv
   ```
   <br/>
7. Activate virtual environment (You should see '(venv)' in front of your current path in command prompt after using this)
    ```cmd
    venv\Scripts\activate
    ```
    <br/>
8. Install dependencies
   ```cmd
   python -m pip install -r requirements.txt
   ```
   <br/>
9. You can leave virtual environment at any point using ```deactivate``` command prompt
    <br/>
   

## Usage
The use of forgy is currently via its CLI.

1. Navigate to source directory which contains the CLI app
   ```cmd
   cd src
   ```
   
   <br/>
2. To view help page to understand all subcommands available
   ```cmd
   python -m app -h
   ```
   Sample output:
   ```
   usage: forgy-app [-h] [--version]
   {organize_extension,delete_files,copy_directory_contents,move_directories,get_files_from_dir,get_metadata,get_single_metadata,get_isbns_from_texts}
   ...

   A powerful file organizer, ebook manager, and book metadata extractor in python
        
   options:
    -h, --help            show this help message and exit
   --version             show program's version number and exit
        
   FOrgy Operations:
   Valid subcommands
        
   {organize_extension,delete_files,copy_directory_contents,move_directories,get_files_from_dir,get_metadata,get_single_metadata,get_isbns_from_texts}
   organize_extension  Organize files by extension
   delete_files        Delete files (default) or directo- ries in source directory. WARNING: permanent operation!
   copy_directory_contents
                            Copy contents of source directory into destination directory (files and directories included)
   move_directories    Move directories to another destination
   get_files_from_dir  Aggregate pdf files from various directories/sources
   get_metadata        Get pdf metadata and rename file
   get_single_metadata
                        Get metatada for a single book using title, isbn or file path
   get_isbns_from_texts
                        Extract isbns from source_directory pdf files into a text file (isbn_text_filename)
        
   Welcome to forgy v0.1.0!
   ```
   <br/>

From the above, there are eight major subcommands you can use to organize your files and these include:
<br/>
- organize_extension
- delete_files
- copy_directory_contents
- move_directories
- get_files_from_dir
- get_metadata
- get_single_metadata
- get_isbns_from_texts
<br/>

The functions of each are as listed and you can always view usage of sub-command using: ```python -m forgy-app sub-command-name --help```.
The get_metadata requires an optional GoogleBooks API key. **forgy** is built on two major books API (Google and Openlibrary) which are
freely available. The Openlibrary API is fully free without restrictions while Google BooksAPI has a default Quota of about 1000 api calls
per month which can theoretically be increased. To avoid overwhelming a single API and provide access to more book metadata, providing 
Google BooksAPI key is important.

Google BooksAPI key can be obtained via [Google Cloud Console](https://console.cloud.google.com/) . On the home page:

```text
Select a project(if existing) or Create new (right beside Google Logo) > New Project > Create > Left hand menu > APIs and Services > Credentials
> Create Credentials > API Key (API key created and displayed in dialog box. Copy it and use) > Close dialog > API key (optional) > API Restrictions> Restrict key
> Google Cloud APIs > Ok
```


## Example
Task: extracting valid isbns from all PDF books in a directory
Here, we want to extract ISBNs from books located in a particular directory. First, we view CLI help to locate a subcommandS to do that.
And looking at the sample output above (see usage), the get_isbns_from_texts subparser is the one that does this. For the sake of simplicity, we keep all
PDF ebooks inside one folder and then we view help page for get_isbns_from_texts subcommand to understand how to use it.
```cmd
python -m forgy-app get_isbns_from_texts -h
```
Sample output:

	```
	usage: forgy-app get_isbns_from_texts [-h] [--isbn_text_filename ISBN_TEXT_FILENAME] source_directory destination_directory

	Extract ISBNs from PDF files as a dictionary with filename as key and valid ISBNs extracted as a list of values

	positional arguments:
  	source_directory      Provide source directory for pdf files
  	destination_directory
                        Provide destination for text file containing isbns

	options:
  	-h, --help            show this help message and exit
  	--isbn_text_filename ISBN_TEXT_FILENAME
                        	Provide name of text file containing isbns
	```

The usage of the subcommand is shown on the first line in the help screen above. Only two (postional) arguments are compulsory here while the
the name of the text file containing extracted ISBNs is optional (the default is 'extracted_isbns.txt'). Therefore, to use the get_isbns_from_texts
command, you need a source_directory containing the PDF files to extract ISBNs from, a destination_directory where you save file containing extracted isbns
into and, if you like, an optional isbn_text_filename argument which will be the name of text file containing the extracted valid ISBNs and located in destination directory.
The format of the output is a text file containing file names as keys and extracted valid ISBNs as a list of values and this is found in destination directory defined.

The command to extract ISBNs from texts:
```cmd
python -m forgy-app get_isbns_from_texts C:\Users\User-name\Desktop\source-directory C:\Users\User-name\Desktop\destination-directory
```
The source and destination directories are in user desktop. And once you push the enter key, ISBN extraction takes place.
<br/>
<br/>
<br/>

## License
**forgy** is available under [AGPL3](https://www.gnu.org/licenses/agpl-3.0.txt) open source license

## Dependencies
- [requests - make HTTP request](https://github.com/psf/requests)
- [pypdf - extract text from PDF ebook](https://github.com/py-pdf/pypdf)
- [dotenv - manage user Google BooksAPI key-value pairs as environment variables](https://github.com/theskumar/python-dotenv)
- [reportlab - to create pdf file in some test](https://pypi.org/project/reportlab)
- [flake8 - format code](https://flake8.pycqa.org/en/latest/)

## TODO
- Package and release version 0.1.0 of FOrgy version (with a CLI and/or GUI)
