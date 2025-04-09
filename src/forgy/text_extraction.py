"""
A module to extract text from a pdf document.
The resulting text strin is scanned for ISBN
with the help of isbn_regex module.

The module also contains a function to directly
extract in-built book metadata from a pdf document
"""

from datetime import datetime
from pathlib import Path

from pypdf import PdfReader

from .metadata_search import get_file_size
from .isbn_regex import isbn_pattern, format_isbn
from .logger import create_logger


logger = create_logger("text_extraction")


def extract_text(pdf_path, no_of_pages=20):
    """A function to extract a specific no of
        pages of text from a PDF ebook into a
        long string.

    Only the first 20 pages are extracted here(default) as
    most book ISBNs can be found in this range.
    """
    extracted_text = ""

    total_no_of_pages = 0

    # Extract the first n pages of text
    try:
        pdf_reader = PdfReader(str(pdf_path), strict=False)

        total_no_of_pages = len(pdf_reader.pages)
    except ValueError as v:
        print(f"ValueError encountered: {v}")
        pass
    except Exception as e:
        logger.exception(f"An unexpected error occured: {e}")
        pass

    if no_of_pages < total_no_of_pages:
        for page_no in range(1, no_of_pages + 1):
            page = pdf_reader.pages[page_no]
            page_text = page.extract_text()
            extracted_text = extracted_text + page_text

    elif (
        no_of_pages > total_no_of_pages
        or no_of_pages == total_no_of_pages
    ):
        for page_no in range(0, total_no_of_pages):
            page = pdf_reader.pages[page_no]
            page_text = page.extract_text()
            extracted_text = extracted_text + page_text
    else:
        logger.error(f"Text extraction not successful: {pdf_path}")

    return extracted_text


def fetch_metadata_from_file(file):
    """
    Function to fetch in-built metadata encoded with pdf book.

    Not every book has in-built metadata, so this will not
    always yield expected results. This unreliability is why
    it's not been added as a default book
    metadata
    source.
    """
    pdf_reader = PdfReader(file)
    meta = pdf_reader.metadata
    title = meta.title
    subtitle = "NA"
    full_title = meta.title

    try:
        date_of_publication = f"{meta.creation_date}"
    except Exception as e:
        logger.exception(f"Error {e} encountered")
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
    logger.info(f"Metadata for {file}: {file_metadata}")

    return file_metadata


def _extract_last_n_pages(file_path):
    """
    Function to extract text from last 20 pages of a
    pdf document.
    """

    reader = PdfReader(str(file_path), strict=False)
    extracted_text = ""

    for n in range(1, 20):
        page = reader.pages[-n]
        prelim_pages_text = page.extract_text()
        extracted_text = extracted_text + prelim_pages_text

    return extracted_text


def _reverse_get_isbn(pdf_path):
    """
    Function to extract text from last n pages of a
    pdf document.

    This is not a very reliable way of extracting ISBN from
    a book since some publishers do advertise related books
    at the back of some or all of their books. In this case
    All ISBNs for different books are matched. This is why
    getting ISBN from last n pages of a book has not bee applied
    in FOrgy by default.

    Note: examples of publishers include: Packt, NoStarch Press,
        and Manning
    """
    extracted_text = _extract_last_n_pages(pdf_path)
    matched_isbn = []
    matched_regex = isbn_pattern.findall(extracted_text)
    matched_isbn.append(matched_regex)
    valid_isbn = format_isbn(matched_isbn)
    logger.info(
        f"Valid ISBNs from {Path(pdf_path).name}: {valid_isbn}"
    )


if not __name__ == '__main__':
    pass
