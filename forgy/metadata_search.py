#metadata search on google and openlib apis
import json
import requests
import time
import os
import random
from user_requirements import headers,api_key



def merge_list_items(given_list):   #format can be first author et al if list contains more than two et al
    """convert content of
        list into a single string of the
        list of values neatly separated
        by a comma"""
    if isinstance(given_list, list):
        list_length = len(given_list)
        appended_values = ""
        given_list = [str(val) for val in given_list]
        for i in range(list_length):
            appended_values = appended_values + given_list[i] + "," + " "
        f_appended_values = appended_values.rstrip(" ").rstrip(",")
##        print(f_appended_values)
        return f_appended_values
    else:
        print(f'parameter is of type {type(given_list)}, not of type:list')
        pass


#a function to handle keys and values of different types, including missing keys and values of type str, list
#dict of interest is populated with available values whose keys match those in API
def metadata_handler(dict_of_interest, metadata_dict):
    """dict of interest is empty_valued while metadata_dict is from json data from api"""
    for key in dict_of_interest.keys():
        #if key in defined empty-valued book dictionary also exist
        #in metadata keys from api (this means data is available)
        if key in metadata_dict.keys():
            #if value in retrieved dict is a list containing single element, extract that element using zero index
            #and update the defined empty_valued dictionary (dict_of_interest)
            if isinstance(metadata_dict[key], list) and len(metadata_dict[key])==1:
                dict_of_interest[key] = dict_of_interest[key] + metadata_dict[key][0]

            #if value in retrieved dict is a list containing multiple elements, extract that element using zero index
            #and update the defined empty_valued dictionary (dict_of_interest)
            elif isinstance(metadata_dict[key], list) and len(metadata_dict[key])>1:
                dict_of_interest[key]  = dict_of_interest[key] + merge_list_items(metadata_dict[key])
            else:
                #if value is a single value (string), simply assign the value to corresponding key in empty-valued dictionary
                dict_of_interest[key] = metadata_dict[key] #if the value is a str or int
        else:
            #absent values are market 'NA'
            dict_of_interest[key] = 'NA' #if key not in metadata

    return dict_of_interest

#handle title, subtitle and derive subtitle from the former
def get_title_subtitle(metadata_dict, dict_of_interest):
    if ("title" in metadata_dict.keys()) and ("subtitle" not in metadata_dict.keys()):
        subtitle = 'NA'
        full_title = dict_of_interest["title"]
    else: #("title" in metadata_dict.keys()) and ("subtitle" in metadata_dict.keys())
        subtitle = dict_of_interest["subtitle"]
        full_title = dict_of_interest["title"] + ': ' + dict_of_interest["subtitle"]
    return full_title, subtitle


def get_isbns(metadee):
    """fetches isbn10 and isbn13 from metadata via google and
        returns 'NA' if isbn value is not available the result
        is a list of two dictionaries each dict has two key:value
        pairs (e.g. {'type':ISBN_10, 'identifier':'2382932220'})"""
    if "industryIdentifiers" in metadee.keys():
        #if index 0 in list is for ISBN_10 dictionary and index1 in list is for ISBN_13 dictionary
        if metadee["industryIdentifiers"][0]["type"]=="ISBN_10" and ('ISBN_10' in metadee["industryIdentifiers"][0].values()) and metadee["industryIdentifiers"][1]["type"]=="ISBN_13" and ('ISBN_13' in metadee["industryIdentifiers"][1].values()):
            try:
                isbn_10 = metadee["industryIdentifiers"][0]["identifier"]
            except(UnboundLocalError, IndexError):
                isbn_10 = "NA" 
            try:
                isbn_13 = metadee["industryIdentifiers"][1]["identifier"]
            except(UnboundLocalError, IndexError):
                isbn_13 = "NA"

        #if index 0 in list if for ISBN_13 dictionary and index1 in list is for ISBN_10 dictionary
        elif metadee["industryIdentifiers"][0]["type"]=="ISBN_13" and ('ISBN_13' in metadee["industryIdentifiers"][0].values()) and metadee["industryIdentifiers"][1]["type"]=="ISBN_10" and ('ISBN_10' in metadee["industryIdentifiers"][1].values()):
            try:
                isbn_13 = metadee["industryIdentifiers"][0]["identifier"]
            except (UnboundLocalError, IndexError):
                isbn_13 = "NA"
            try:
                isbn_10 = metadee["industryIdentifiers"][1]["identifier"]
            except (UnboundLocalError, IndexError):
                isbn_10 = "NA"
        else:
            #(metadee["industryIdentifiers"][0]["type"]== "OTHER") and len(metadee["industryIdentifiers"]==1)
            #to handle cases like this:'industryIdentifiers': [{'type': 'OTHER', 'identifier': 'UOM:39015058578744'}]
            isbn_10 = "NA"
            isbn_13 = "NA"
    else:
        #if error is returned by database or metadata retrieve unsuccessful
        isbn_10="NA"
        isbn_13="NA"
    return isbn_10, isbn_13



def get_isbns2(metadata_dict):
    """Fetches ISBNS from openlibrary sourced
        metadata"""
    if "isbn_10" in metadata_dict.keys():
        isbn_10 = metadata_dict["isbn_10"][0]
    else:
        isbn_10 = "NA"

    if "isbn_13" in metadata_dict.keys():
        isbn_13 = metadata_dict["isbn_13"][0]
    else:
        isbn_13 = "NA"
    return isbn_10, isbn_13


def get_file_size(file_path):
    #uses file path to obtain file size
    file_stats = os.stat(file_path)
    ##print(file_stats): returns an os.stat_result object(st_size in object is the filesize in bytes)
    file_size_bytes = file_stats.st_size
    ##print(file_size_bytes) returns size of file in bytes
    file_size_MB = file_size_bytes/(1024*1024)
    return f'{file_size_MB:.2f}'
    #returns file_size in megabytes: 9.493844985961914
    #.st_size returns filesize in bytes and this is divided
    #by 1024 twice to get value in MB
    #filesize = os.stat(file_src).st_size/(1024*1024


#for use in main script
def google_api(isbn, api_key):
    googleapi_metadata = 'https://www.googleapis.com/books/v1/volumes?q=isbn:'+\
                                         isbn+'&key='+api_key
    #define function load metadata for both google and openlibrary api to return json_metadata
    # check google api for book metadata
    book_metadata = requests.get(googleapi_metadata, headers=headers, timeout=60) #300 works
    book_metadata.raise_for_status()
    json_metadata = json.loads(book_metadata.text)
    return json_metadata

#for use in main script
def openlibrary_api(isbn):
    olibapi_metadata = 'https://openlibrary.org/isbn/' + isbn + '.json'
    book_metadata = requests.get(olibapi_metadata, headers=headers, timeout=60)
    book_metadata.raise_for_status()
    json_metadata = json.loads(book_metadata.text)
    return json_metadata


##    #assign dict from extracted metadata to metadata_dict



##assign dict from extracted metadata to metadata_dict
def google_metadata_dict(isbn):
    json_metadata = google_api(isbn, api_key)
    try:
        metadata_dict = json_metadata["items"][0]["volumeInfo"]
    except KeyError:
        metadata_dict = {"kind":"books#volumes", "totalItems":0}
    return metadata_dict

def openlibrary_metadata_dict(isbn):
    json_metadata = openlibrary_api(isbn)
    #values are directly avvailable in json_metadata without nesting, so we assign the extracted json to metadata_dict
    try:
        openlibrary_metadata_dict = json_metadata
    except KeyError:
        openlibrary_metadata_dict = {"error": "notfound", "key": "/044482409x"}  #this dict is that returned by openlib when metadata not available
    return openlibrary_metadata_dict


#if there is an error fetching data from api, a dictionary with all values as 'NA' is returned.
#the function below converts this into an empty dictionary
def get_dictionary(dictionary):
    #checks if all values in a dictionary are 'NA' and returns an empty dictionary in that case.
    #some values in dict can be missing but not all!
    empty_dict = {}
    final_dict = {}
    for key,value in dictionary.items():
        if key == 'NA':
            dictionary.pop(key)
        else:
            final_dict[key] = value
        #else append value to null_dict (of no use)
    if len(final_dict)==0:
        return empty_dict
    else:
        return final_dict


#prev: isbn, api, headers as input
def get_metadata_google(isbn, file, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}):
    """Supply extracted isbn to fetch book metadata as a json from either google.com api or openlibrary.org api"""
    #gets file metadata from google or openlibrary apis
##    json_metadata = google_api(isbn)

    #initialize dictionary with most important keys also present in json and values initialized to empty string
    dict_of_interest = {"title":'', "subtitle":'', "publishedDate":'', "publisher":'', "authors":'', "pageCount":''}

##    #assign dict from extracted metadata to metadata_dict
    metadata_dict = google_metadata_dict(isbn)

    #populate dictionary with metadata values whose keys are initialized with empty_values are automatically added)
    dict_of_interest = get_dictionary(metadata_handler(dict_of_interest, metadata_dict))

    if len(dict_of_interest)==0:
        return
    else:
        pass   
    
    #assign title to variable
    title = dict_of_interest["title"]

    #fetch sub_title and full title
##    full_title, subtitle = get_title_subtitle(metadata_dict, metadata_dict)
    full_title, subtitle = get_title_subtitle(metadata_dict, dict_of_interest)

    #assign values populated in dict_of_interest to variables (keys are: title, publishedDate, publisher, authors, pageCount)
    date_of_publication = dict_of_interest["publishedDate"]
    publisher = dict_of_interest["publisher"]
    authors = dict_of_interest["authors"]
    page_count = str(dict_of_interest["pageCount"])

    #GET OTHER VALUES
    #get isbns from metadata

    isbn_10, isbn_13 = get_isbns(metadata_dict)


    #get reference isbn (ref_isbn), the one used to retrieve the metadata
    ref_isbn = isbn

    source='www.google.com'

    #get file size
    file_size = get_file_size(file)

    #update dict_of_interest
    dict_of_interest["full_title"] = full_title
    dict_of_interest["isbn_10"] = isbn_10
    dict_of_interest["isbn_13"] = isbn_13
    dict_of_interest["ref_isbn"] = isbn
    dict_of_interest["source"] = source
    dict_of_interest["filesizes"] = file_size

##    print(dict_of_interest)

##    print(f"""
##        title = {title},
##        subtitle = {subtitle},
##        full_title = {full_title},
##        date_of_publication = {date_of_publication},
##        publisher = {publisher},
##        authors = {authors},
##        page_count = {str(page_count)},
##        isbn_10 = {isbn_10},
##        isbn_13 = {isbn_13},
##        ref_isbn = isbn,
##        source = {source},
##        filesize = {filesize:.2f} MB""")
    return (title, subtitle, full_title, date_of_publication, publisher, authors, page_count, isbn_10, isbn_13, ref_isbn, source, file_size)



def get_metadata_openlibrary(isbn, file, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}):
    """Supply extracted isbn to fetch book metadata as a json from either google.com api or openlibrary.org api"""
##    json_metadata = openlibrary_api(isbn)
    #initialize dictionary with most important keys also present in json and values initialized to empty string
    dict_of_interest = {"title":'', "subtitle":'', "publish_date":'', "publishers":'', "by_statement":'', "number_of_pages":''}  # str by_statement rep authors in openlib api
    #openlib also has "full_title" key in json
            
##    #values are directly avvailable in json_metadata without nesting, so we assign the extracted json to metadata_dict
    metadata_dict = openlibrary_metadata_dict(isbn)

    #populate dictionary with metadata values whose keys are initialized with empty_values are automatically added)
    dict_of_interest = metadata_handler(dict_of_interest, metadata_dict)
             
    #assign title 
    title = dict_of_interest["title"]

    #fetch sub_title and full title
    full_title, subtitle = get_title_subtitle(metadata_dict, dict_of_interest)

    #assign values populated in dict_of_interest to variables (keys are: title, publishedDate, publisher, authors, pageCount)
    date_of_publication = dict_of_interest["publish_date"]
    publisher = dict_of_interest["publishers"]
    authors = dict_of_interest["by_statement"]
    page_count = str(dict_of_interest["number_of_pages"])

    #GET OTHER VALUES
    #get isbns from metadata

    isbn_10, isbn_13 = get_isbns2(metadata_dict)

    #get reference isbn (ref_isbn), the one used to retrieve the metadata
    ref_isbn = isbn

    source='www.openlibrary.org'

    #get file size
    file_size = get_file_size(file)

    #update dict_of_interest
    dict_of_interest["full_title"] = full_title
    dict_of_interest["isbn_10"] = isbn_10
    dict_of_interest["isbn_13"] = isbn_13
    dict_of_interest["ref_isbn"] = isbn
    dict_of_interest["source"] = source
    dict_of_interest["filesizes"] = file_size

##    print(dict_of_interest)

##    print(f"""
##        title = {title},
##        subtitle = {subtitle},
##        full_title = {full_title},
##        date_of_publication = {date_of_publication},
##        publisher = {publisher},
##        authors = {authors},
##        page_count = {str(page_count)},
##        isbn_10 = {isbn_10},
##        isbn_13 = {isbn_13},
##        ref_isbn = "isbn",
##        source = {source},
##        file_size = {file_size:.2f} MB"""
##        )
    return (title, subtitle, full_title, date_of_publication, publisher, authors, page_count, isbn_10, isbn_13, ref_isbn, source, file_size)
         

#if api = google and json values returned, use google api,
#else: we use openlibrary api
    #case 1. api = openlibrary and json values returned; retrieve values
    #case 2. api = openlibrary  and json values not returned; set api as google api and if values not returned,,, print values not found
        
#Define a function to enable user check individual book for ISBN and automatically apply metadata to book         
            

            
