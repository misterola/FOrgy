"""
Tests on text and book metadata
extraction from pdf document
"""

import os
import sys
import unittest
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import textwrap


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
)

from forgy.text_extraction import (
    extract_text,
    fetch_metadata_from_file
)

def create_sample_pdf(file_name):

    book_text = "The AI Revolution.  \
    The times are changing and artificial intelligence has transformed from an academic toy technology \
    into a something every serious professional must pay close attention to. \
    While some people believe in the saying that: 'Whoever one AI cannot replace, several AIs will', \
    I urge you to say to yourself “AI is never going to replace me” :). \
    And when you are done, dedicate more time towards doing what humans do...adapt & grow!   @misterola 2025-04-08"

    wraped_book_text = textwrap.fill(book_text, width=100)

    # create pdf document
    doc = SimpleDocTemplate(
        f"{file_name}",
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # build pdf
    doc.build([Paragraph(book_text.replace("\n", "<br />"), getSampleStyleSheet()["Normal"]),])

    return None


def create_empty_pdf(file_name):
    canvas = Canvas(file_name, pagesize=A4)

    canvas.drawString(72, 72, "")

    canvas.save()

    return None


extracted_text = "The AI Revolution. The times are changing and artificial intelligence has transformed \
from an academic toy\ntechnology into a something every serious professional must pay close attention to. \
While some people\nbelieve in the saying that: 'Whoever one AI cannot replace, several AIs will', \
I urge you to say to yourself\n“AI is never going to replace me” :). And when you are done, dedicate \
more time towards doing what\nhumans do...adapt & grow! @misterola 2025-04-08\n"


class TestTextExtraction(unittest.TestCase):
    file_name = 'ai_and_me.pdf'
    empty_file = 'empty.pdf'

    def setUp(self):
        """Create sample pdf files named above"""

        create_sample_pdf(TestTextExtraction.file_name)
        # self.assertTrue(os.path.exists(TestTextExtraction.file_name))

        create_empty_pdf(TestTextExtraction.empty_file)
        # self.assertTrue(os.path.exists(TestTextExtraction.empty_file))


    def tearDown(self):
        """Delete the above pdf files from workspace"""

        if (os.path.exists(TestTextExtraction.file_name)
            and os.path.exists(TestTextExtraction.empty_file)
        ):
            os.remove(TestTextExtraction.file_name)
            os.remove(TestTextExtraction.empty_file)
        else:
            print("File nonexistent")
            pass

    def test_extract_text(self):
        """Test on extraction of text from a non-empty pdf file"""
        self.assertEqual(extract_text(TestTextExtraction.file_name), extracted_text)


    def test_empty_text(self):
        """Test on extraction of text from an emtpy pdf file"""
        self.assertEqual(len(extract_text(TestTextExtraction.empty_file)), 0)


    def test_file_metadata_filled(self):
        """Test on extraction of file metadata from a non-empty pdf file"""
        self.assertEqual(len(fetch_metadata_from_file(TestTextExtraction.empty_file)), 12)

    def test_file_metadata_empty(self):
        """Test on extraction of file metadata from an empty pdf file"""
        self.assertEqual(len(fetch_metadata_from_file(TestTextExtraction.empty_file)), 12)
    

if __name__=='__main__':
    unittest.main(verbosity=2)
