from pypdf import PdfReader
from datetime import datetime
from .metadata_search import get_file_size
from .isbn_regex import isbn_pattern, format_isbn


def extract_text(pdf_path):
    extracted_text = ""

    # extract the first n pages of text
    try:
        reader = PdfReader(str(pdf_path), strict=False)
    except ValueError:
        pass
    for n in range(1, 20):
        page = reader.pages[n]
        prelim_pages_text = page.extract_text()
        extracted_text = extracted_text + prelim_pages_text
    return extracted_text


def fetch_metadata_from_file(file):
    """Function to fetch metadata encoded with pdf book.

    Not every book has inbuilt metadata, so this will not
    always yield expected results.
    """
    # Fetch metadata from pdf file
    pdf_reader = PdfReader(file)
    meta = pdf_reader.metadata
    title = meta.title
    subtitle = "NA"
    full_title = meta.title
    try:
        date_of_publication = f"{meta.creation_date}"
    except Exception as e:
        print(f"Error {e} encountered")
        date_of_publication = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    publisher = meta.producer
    authors = meta.author
    page_count = str(len(pdf_reader.pages))
    isbn_10 = "NA"
    isbn_13 = "NA"
    ref_isbn = "NA"
    source = "file_metadata"
    file_size = get_file_size(file)
    file_metadata = (
        title,
        subtitle,
        full_title,
        date_of_publication,
        publisher,
        authors,
        page_count,
        isbn_10,
        isbn_13,
        ref_isbn,
        source,
        file_size,
    )
    # print(file_metadata)
    return file_metadata


# reader = PdfReader(str(pdf_path), strict=False)
def extract_last_n_pages(file_path):  # needs reader object
    reader = PdfReader(str(file_path), strict=False)
    # extract last n pages in a document
    extracted_text = ""
    for n in range(1, 20):
        page = reader.pages[-n]
        prelim_pages_text = page.extract_text()
        extracted_text = extracted_text + prelim_pages_text
        # print(extracted_text)
    return extracted_text


# extract_last_n_pages(pdf_path)
def reverse_get_isbn(pdf_path):
    extracted_text = extract_last_n_pages(pdf_path)
    matched_isbn = []
    matched_regex = isbn_pattern.findall(extracted_text)
    matched_isbn.append(matched_regex)
    valid_isbn = format_isbn(matched_isbn)
    print(valid_isbn)

