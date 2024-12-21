from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path
import pytesseract
from datetime import datetime, timedelta  # time delta to add timezone info
import pytz
from metadata_search import get_file_size
from isbn_regex import isbn_pattern, format_isbn


def extract_text(pdf_path):
    extracted_text = ''

    #extract the first n pages of text
    try:
        reader = PdfReader(str(pdf_path), strict=False)
    except ValueError:
        pass
    for n in range(1,20):
        page = reader.pages[n]
        prelim_pages_text = page.extract_text()
        extracted_text = extracted_text + prelim_pages_text
    return extracted_text


def format_metadata_time(time_str):
    """converts time string from format
    "D:20221107172522+08'00'" into standard format"""

    # Strip the 'D:' prefix and timezone part
    datetime_str = time_str[2:16]  # '20221107172522'  2:16
    timezone_str = time_str[16:].replace("'", "")  # '+08:00' 17:
    print(datetime_str, timezone_str)

    # Convert to a datetime object
    dt = datetime.strptime(datetime_str, "%Y%m%d%H%M%S")

    # Adjusting to timezone
    timezone_offset = timedelta(hours=int(timezone_str[:3]), minutes=int(timezone_str[4:]))
    dt_with_tz = dt.replace(tzinfo=pytz.FixedOffset(timezone_offset.seconds // 60))

    # Print the result
    print("Datetime with timezone:", dt_with_tz)  #2022-11-07 17:25:22+08:00
    return f'{dt_with_tz}'

def fetch_metadata_from_file(file):
    #Fetch metadata from pdf file
    pdf_reader = PdfReader(file)
    meta = pdf_reader.metadata
    title = meta.title
    subtitle = 'NA'
    full_title = meta.title
    date_of_publication = f'{meta.creation_date}'
    publisher = meta.producer
    authors = meta.author
    page_count= str(len(pdf_reader.pages))
    isbn_10= 'NA'
    isbn_13= 'NA'
    ref_isbn= 'NA'
    source = 'file_metadata'
    file_size = get_file_size(file)
    file_metadata = title, subtitle, full_title, date_of_publication, publisher, authors, page_count,\
           isbn_10, isbn_13, ref_isbn, source, file_size
##    print(file_metadata)
    return file_metadata

#############
#testing the above
##from pathlib import Path
##import os
##
##home = Path.home()
##dst = home/"Desktop"/"MessyFOrg"/"ubooks_copy"
##
##for file in os.scandir(dst):
##    pdf_path = dst/file
##    print(pdf_path.stem,':', end='\n')
##    file_metadata = fetch_metadata_from_file(pdf_path)
####    print(file_metadata, end='\n\n')
##############
    

### extract_last pages (and fetch metadata for all unique isbns. enable
### user to pick a valid isbn from among the recovered

pdf_path = r'C:/Users/Ola/Desktop/Forgy/ubooks/Mark Roseman - Modern Tkinter for Busy Python Dev elopers-Late Afternoon Press (2021).pdf'

##reader = PdfReader(str(pdf_path), strict=False)
def extract_last_n_pages(file_path):  #needs reader object
    reader = PdfReader(str(file_path), strict=False) 
    #extract last n pages in a document
    extracted_text = ''
    for n in range(1,20):
        page = reader.pages[-n]
        prelim_pages_text = page.extract_text()
        extracted_text = extracted_text + prelim_pages_text
##    print(extracted_text)
    return extracted_text

##extract_last_n_pages(pdf_path)

def reverse_get_metadata(pdf_path):
    extracted_text = extract_last_n_pages(pdf_path)
    matched_isbn = []
    matched_regex = isbn_pattern.findall(extracted_text)
    matched_isbn.append(matched_regex)
    valid_isbn = format_isbn(matched_isbn)
    print(valid_isbn)
##    if valid_isbn != []:
##        for isbn in valid_isbn:
        #look for metadata on google api. if not available check openlib, hence return an empty dict. if metadata found, break out of loop
    

reverse_get_metadata(pdf_path)    

        
#Use OCR to extract text from book and retrieve metadata
##pdf_path = r'C:/Users/Ola/Desktop/Andersen - Business Process Improvement Toolbox-American Society for Quality (ASQ) (2007).pdf'
##def ocr_text_extract(file_path):
##    pdf_file = str(file_path)
##    pages = convert_from_path(pdf_file)
##    extracted_ocr_text = ''
##    def extract_text_from_image(image):
##        #Extract text from images
##        text = pytesseract.image_to_string(image)
##        return extract_text_from_image
##    for page in pages:
##        text = extract_text_from_image(page)
##        extracted_ocr_text = extracted_ocr_text + text + ' '
##    return extracted_ocr_text
##
##ocr_text_extract(pdf_path)
##poppler-utils needed for pdf_2image to work. check oschwartz10612 on github for latest
