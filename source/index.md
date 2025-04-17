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
- [Example](#example)
     - [Using forgy CLI (recommended)](#using-forgy-cli-recommended)
     - [Using forgy public APIs](#using-forgy-public-apis)
- [Setting up forgy locally](#setting-up-forgy-locally)
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
   
   ```cmd
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
     ```

From the above, there are eight major sub-commands you can use to carryout various operations on your files and directories. These include:
- ```get_metadata```
- ```get_isbns_from_texts```
- ```get_single_metadata```
- ```organize_extension```
- ```get_files_from_dir```
- ```copy_directory_contents```
- ```move_directories```
- ```delete_files_directories```

The function of the above sub-commands are as stated in the command-line help shown earlier. You can view usage of sub-commands using: 
<br/>

```forgy sub-command --help```.
<br/>

Note that the ```get_metadata``` sub-command requires an optional GoogleBooks API key. This ```get_metadata``` sub-command is built on two major books API (Google and Openlibrary) which 
are freely available. 

Openlibrary API is available for free with some API request per minute per IP limit to enforce responsible usage. Google BooksAPI, on the other hand has a default quota of about 1000
free API calls per month per IP, which can theoretically be increased via the Google cloud console.

To avoid overwhelming a single API and gain access to more book metadata, providing Google BooksAPI key is recommended and forgy
randomly selects between these two APIs for metadata retrieval.

Google BooksAPI key can be obtained via [Google Cloud Console](https://console.cloud.google.com/) . 

```text
On the home page:
Select a project if existing or Create new (right beside Google Console Logo) > New Project > Create > Left hand menu > APIs and Services > Credentials >
> Create Credentials > API Key (API key created and displayed in dialog box. Copy it and use) > Close dialog > API key (optional) > API Restrictions >
> Restrict key > Google Cloud APIs > OK
```

<br/>

[🔝 Back to Table of Contents](#table-of-contents)
<br/>
<br/>

## Example
**Task**: Extract all valid ISBNs from all PDF books located in a directory
### Using forgy CLI (recommended)
First, we view command-line help to identify a sub-command for ISBN extraction. Looking at the sample output above (see _sample output_ in usage section), the ```get_isbns_from_texts``` 
sub-command is the one that _extract isbns from several PDF e-books contained in source_directory_. For the sake of simplicity, we keep all PDF e-books inside one folder and then we 
view help page for get_isbns_from_texts sub-command to understand how to use it.
```cmd
forgy get_isbns_from_texts -h
```
Sample output:

```
usage: forgy get_isbns_from_texts [-h] [--isbn_text_filename ISBN_TEXT_FILENAME] source_directory destination_directory

Extract valid ISBNs from PDF files as a dictionary with filenames as keys and valid ISBNs as a list of values

positional arguments:
  source_directory      provide source directory for input pdf files
  destination_directory
                        provide destination for text file containing book titles and extracted isbns
options:
  -h, --help            show this help message and exit
  --isbn_text_filename ISBN_TEXT_FILENAME
                        provide name of text file containing extracted e-book isbns
```

The usage of the sub-command is shown on the first line in the help screen above. Only two postional arguments (```source_directory``` and ```destination_directory```) are mandatory 
here, while the name of the text file to contain extracted valid ISBNs is optional (the default name is ```extracted_isbns.txt```). 

The ```source_directory``` contains PDF files to extract ISBNs from and the ```destination_directory``` is the location on your computer where the file containing extracted ISBNs is 
saved. The format of the output is a text file containing file names as keys and extracted valid ISBNs as a list of values and the ISBN text file is found in the 
```destination_directory``` defined.

The command to extract ISBNs from texts, contained in ```source-directory``` into a text file located in ```destination-directory``` with both ```source-directory``` and 
```destination_directory``` located in user's desktop directory:
```cmd
forgy get_isbns_from_texts C:\Users\User-name\Desktop\source-directory C:\Users\User-name\Desktop\destination-directory
```

Once you press the enter key, ISBN extraction from all PDF files in ```C:\Users\User-name\Desktop\source-directory``` takes place.

<br/>

[🔝 Back to Table of Contents](#table-of-contents)
<br/>

### Using forgy public APIs
1. Import the ```get_isbns_from_texts``` function to execute the current task and ```pathlib.Path``` from python standard library to properly handle the path to source and destination
   directories.
   ```cmd
   >>> from forgy.messyforg import get_isbns_from_texts
   ```
2. Define the source and destination directories.
   ```cmd
   >>> source_directory = Path(r'C:\Users\USER-NAME\Desktop\SOURCE-DIRECTORY')
   >>> txt_destination_dir = Path(r'C:\Users\USER-NAME\Desktop')
   ```
3. Get ISBNs from all PDF e-books in the source directory by calling the imported function.
   ```cmd
   >>> get_isbns_from_texts(source_directory, txt_destination_dir)
   ```
**Note:** API documentation for forgy is still in progress and the CLI option is much more documented at this point and is therefore recommended. Feel free to explore forgy internals.
In the next section, you will learn how to set up forgy locally on your computer and explore the workings of its modules and the public APIs within them.
 <br/>
 
 [🔝 Back to Table of Contents](#table-of-contents)
 
 <br/>
 
## Setting up forgy locally
1. Verify that you have python installed on your computer.
   
   Open windows command prompt (```windows button + cmd + enter```) and check python version using ```python --version```+ ```enter```. You should see
   your python version, which in this case is ```3.12```.

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
   
   You need git installed to clone a repo on Windows. If you don't already use git for version control, you may download git for windows [here](https://git-scm.com/downloads/win) ,
   install and open the downloaded git bash, navigate to the destination directory for the cloned forgy repo (desktop in this case) and clone repository using the clone command (in git)
   as shown below.
   ```bash
   cd desktop
   ```

   ```
   git clone https://github.com/misterola/forgy.git
   ```
   <br/>
5. Re-open Windows command prompt and navigate to the project root directory (```desktop/forgy```).
   You may use the command prompt henceforth.
   ```cmd
   cd forgy
   ```
   <br/>
6. Create virtual environment.
   
   ```cmd
   python -m venv venv
   ```
   <br/>
7. Activate virtual environment.
   
   You should see '(venv)' in front of your current path in command prompt after activating virtual environment.
    ```cmd
    venv\Scripts\activate
    ```
    <br/>
8. Install dependencies.
    
   ```cmd
   python -m pip install -r requirements.txt
   ```
   <br/>
9. You can leave virtual environment at any point using ```deactivate``` command prompt.
   <br/>
   <br/>
   <br/>
10. Navigate to **cli** package in **src** directory. The main.py module contains the CLI logic.
   ```cmd
   cd src/cli
   ```
   
   <br/>
11. To view help page to understand all subcommands available.

   ```cmd
   python -m main -h
   ```
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

[🔝 Back to Table of Contents](#table-of-contents)
<br/>
<br>

[Back to Top](#forgy)
