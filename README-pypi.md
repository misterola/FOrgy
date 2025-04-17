<p align="center">
    <img alt="forgy_logo" src="https://raw.githubusercontent.com/misterola/forgy/dev/forgy_logo.png">
</p>

------------------------

# forgy
**forgy** is a powerful file organizer and e-book manager with a command-line interface for reliable retrieval of e-book metadata and easy renaming of PDF e-books.

With **forgy**, you can automatically extract valid ISBNs from many PDF e-books, get metadata for ebooks using extracted ISBNs, rename 'unknown' books using retrieved metadata, organize
a messy file collection into folders according to their formats, and much more. This project arose due to the perceived need to reliably rename e-books with their correct titles while
keeping them organized on a computer, without installing and depending on bloated software with busy interface. 

The goal is to easily create and maintain a decent personal PDF e-book library, especially when identifying PDF e-books by their names becomes difficult. The name **forgy** is from the project's roots as a **f**ile **org**anizer in P**y**thon.

**Note:** Development and testing was done on a Windows 10 PC, with python ```3.12``` installed, in such a way as to ensure platform independence. Feel free to try forgy out on other
platforms.
<br/>
<br/>

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Dependencies](#dependencies)
<br/>

## Installation
1. Verify that you have python installed on your computer.
   
   Open windows command prompt (```windows button + cmd + enter```) and check python version using ```python --version```+ ```enter```. You should see
   your python version, which in this case is ```3.12```.

   If you don't have python installed, you can download it [here](https://www.python.org/downloads)
   <br/>
   <br/>

2. Install forgy directly from PyPI.
   
   ```cmd
   python -m pip install forgy
   ```
   This installation includes forgy public APIs and its command-line interface. You can also include ```forgy>=0.1.0``` in your ```requirements.txt``` to install forgy as a dependency 
   in your project
   <br/>

   [🔝 Back to Table of Contents](#table-of-contents)
   <br/>
   <br/>

## Usage
**forgy** can be used via its CLI (recommended) or by importing or calling its public APIs directly. The CLI option currently has more documentation and is therefore recommended.
This section assumes that you have installed forgy via ```pip``` as earlier explained.

1. Check whether the commandline tool is properly installed on your computer. Once you enter ***forgy*** in your command line, you should see the Namespace object from parser.
    ```
    Namespace(subcommands=None)
    Please provide a valid subcommand
     ```
   If you see the above, forgy CLI should be accessible via command prompt. However, if that is not the case, you may need to add python Scripts to your PATH to enable execution of the
   CLI.
   <br/>
   <br/>
3. To view help page to understand all sub-commands available in **forgy**, pass the **h***elp argument to forgy.
   
   ```forgy -h```

   
   Sample output:
   ```
   usage: forgy [-h] [--version]
             {get_metadata,get_isbns_from_texts,get_single_metadata,organize_extension,get_files_from_dir,copy_directory_contents,move_directories,delete_files_directories}
             ...

   A powerful file organizer, ebook manager, and book metadata extractor in python

   options:
     -h, --help            show this help message and exit
     --version             show program's version number and exit

   forgy Operations:
     Valid subcommands

     {get_metadata,get_isbns_from_texts,get_single_metadata,organize_extension,get_files_from_dir,copy_directory_contents,move_directories,delete_files_directories}
	get_metadata    retrieve PDF e-book metadata and rename several PDF e-books with it
	get_isbns_from_texts
	                    extract isbns from several PDF e-books contained in source_directory
	get_single_metadata
	                    get metatada for a single book using file path and title or isbn
	organize_extension  organize files by extension or format
	get_files_from_dir  aggregate pdf files from various directories/sources
	copy_directory_contents
	                       copy contents of source directory into destination directory (files and directories included)
	move_directories    move directories to another destination
	delete_files_directories
	                        delete files or directo- ries in source directory. WARNING: permanent operation!

  Welcome to forgy v0.1.3!
  ```
  <br/>

From the above, there are eight major sub-commands you can use to carryout various operations on your files and directories. These include:
<br/>
- ```get_metadata```
- ```get_isbns_from_texts```
- ```get_single_metadata```
- ```organize_extension```
- ```get_files_from_dir```
- ```copy_directory_contents```
- ```move_directories```
- ```delete_files_directories```
<br/>

The function of the above sub-commands are as stated in the command-line help shown earlier. You can view usage of sub-commands using: ```forgy sub-command --help```.

See project GitHub page [here](https://github.com/misterola/forgy) for more details.
<br/>
<br/>


[🔝 Back to Table of Contents](#table-of-contents)
<br/>
<br/>

## License
GNU Affero General Public License ([AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.txt))
<br/>

[🔝 Back to Table of Contents](#table-of-contents)
<br/>
<br/>

## Dependencies
- [requests - make HTTP request](https://github.com/psf/requests)
- [pypdf - extract text from PDF ebook](https://github.com/py-pdf/pypdf)
- [dotenv - manage user Google BooksAPI key-value pairs as environment variables](https://github.com/theskumar/python-dotenv)
- [flake8 - format code](https://flake8.pycqa.org/en/latest/)
- [reportlab - to create pdf file in some test](https://pypi.org/project/reportlab)
<br/>
<br>

[Back to Top](#forgy)
