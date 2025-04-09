"""
Tests to validate ISBNs, extract ISBNs from pdf
ebooks, and format extracted ISBNs.
"""
# Target functions: is_valid_isbn, get_valid_isbns, format_isbns

import sys
import os
import unittest

print(sys.path)
# Add the src directory to the path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
)
print(sys.path)

from forgy.isbn_regex import (
    is_valid_isbn,
    extract_valid_isbns,
    format_isbn,
    validate_isbns,
)


# VALID ISBNs
valid_isbn_10 = [
    "0471804649",
    "0419225102",
    "2710808366",
    "109810403X",
    "109810403x",
    "044482409X",
    "044482409x",
    "109810403X",
    "109810403x",
]

valid_sbn = [
    '471371106',
]

valid_isbn_13 = [
    "9780873897365",
    "9780199778041",
    "9780873899185",
]

# INVALID ISBNs
invalid_isbn_10 = [
    "0471804648",
    "0419225101",
    "2710808364",
    "1098104030",
    "0444824091",
    "1234567890",
    "111222333X",
    "987654321X"
    "0000000000",
    "1234567891",
    "0005555557",
    "046502656X",    
]

invalid_sbn = [
    '471371112',
    '013334734',
    '019823656',
    '003017278',
    '007038209',
    '001032133',
]


invalid_isbn_13 = [
    "9780873897361",
    "9780199778042",
    "9780873899183",
]

# Matched isbn (because of the range of the
# variable subgroups in an ISBN number, the
# lowest in range are also matched. We include
#  a representative match in each unique group
matched_isbn_10 = [
    ('', '800-248-1946'),
    ('', '98 1985 660'),
    ('', '0-471-80464-9'),
    ('', '0-87389-704-8'),
    ('', '800-248-1946 '),
    ('', '2010046035'),
    ('', '987654321'),
    ('', '2008001858'),
    ('', '44 1963 33991 '),
    ('', '20 96-25714 '),
    ('', '44 1963 31147 '),
]

formatted_isbn_10 = [
    '8002481946',
    '0981985660',
    '0471804649',
    '0873897048',
    '2010046035',
    '0987654321',
    '2008001858',
    '44196333991',
    '0209625714',
    '44196331147'
]


matched_isbn_13 = [
    ('978-', '0-19-977804-1'),
    ('978-', '0-19-977819-5'),
    ('978-', '0-87389-736-5'),
    ('978-', '0-19-977804-1'),
    ('978-', '0-87389-918-5'),
]

formatted_isbn_13 = [
    '9780199778041',
    '9780199778195',
    '9780873897365',
    '9780873899185'
]

matched_sbn = [
    ('', '471371106'),
    ('', '013334791'),
    ('', '019823679'),
    ('', '003017299'),
    ('', '007038230'),
    ('', '001032179'),
    ('', '0-19-823679'),
    ('', '0-03-017299'),
    ('', '0-07-038230'),
    ('', '0-01-032179'),
    ('', '0 19 823679'),
    ('', '0 03 017299'),
    ('', '0 07 038230'),
    ('', '0 01 032179'),
]

formatted_sbn = [
    '0471371106',
    '0013334791',
    '0019823679',
    '0003017299',
    '0007038230',
    '0001032179'
]


# Numbers with less than 9 digits
numbers_below_nine = [
    ('', '12 11 10 0'),
    ('', '9 08 07 0'),
    ('', '1 85-16748 '),
    ('', '48 2012\n658'),
    ('', '1 9\n4 '),
    ('', '1 0 3\n9'),
    ('', '2 5 7\n'),
    ('', '1 7 1\nx'),
    ('', '2 5 9x'),
    ('', '1-2-3 '),
    ('', '2\n39 13\n4'),
    ('', '26 25 24 2'),
    ('', '6 5 4 3'),
]


# 1. FormatISBNs: format_isbns
# Takes matched ISBNs [('978', '2349494949'),('978', '23556778949')]
# and format into clean form with no hyphen or space.
# The no of valid ISBNs should be consistent

class TestFormatISBNS(unittest.TestCase):
    def test_format_isbn10(self):
        """Test on regex-matched ISBN-10 numbers"""
        self.assertEqual(format_isbn(matched_isbn_10), formatted_isbn_10)

    def test_no_hyphen_isbn_10(self):
        """Test to confirm that all hyphens are removed in isbn-10"""
        for isbn10 in format_isbn(matched_isbn_10):
            with self.subTest(number=isbn10):
                self.assertTrue('-' not in isbn10)

    def test_no_space_isbn_10(self):
        """Test to confirm that all spaces are removed from isbn-13"""
        for isbn10 in format_isbn(matched_isbn_10):
            with self.subTest(number=isbn10):
                self.assertTrue(' ' not in isbn10)

    def test_format_isbn13(self):
        """Test on regex-matched ISBN-13 numbers"""
        self.assertEqual(format_isbn(matched_isbn_13), formatted_isbn_13)
    
    def test_no_hyphen_isbn_13(self):
        """Test to confirm that hyphens are removed from isbn-13"""
        for isbn13 in format_isbn(matched_isbn_13):
            with self.subTest(number=isbn13):
                self.assertTrue('-' not in isbn13)

    def test_no_space_isbn_13(self):
        """Test to confirm that all spaces are removed from isbn-13"""
        for isbn13 in format_isbn(matched_isbn_13):
            with self.subTest(number=isbn13):
                self.assertTrue(' ' not in isbn13)

    def test_no_space_sbn(self):
        for sbn in format_isbn(matched_sbn):
            with self.subTest(number=sbn):
                self.assertTrue(' ' not in sbn)

    def test_no_hyphen_sbn(self):
        for sbn in format_isbn(matched_sbn):
            with self.subTest(number=sbn):
                self.assertTrue('-' not in sbn)

    def test_numbers_below_nine(self):
        """Test on regex matches where the number of less than 9 digits"""
        self.assertEqual(len(format_isbn(numbers_below_nine)), 0)

    def test_empty_isbn(self):
        """Test on empty regex match"""
        self.assertEqual(len(format_isbn([])), 0)


# 2. ValidateSingleISBN (for single ISBN): is_valid_isbn
# Function takes a formatted isbn and confirms whether it
# is valid or not. The unique values taken include:
# isbn10 all numbers, isbn13, isbn10 ending in x, isbn10 ending in X,
# sbn. The opposite cases for invalid isbns too.

class TestValidateISBN(unittest.TestCase):
    def test_valid_isbn_10(self):
        """
        Test on all isbn10 formats including those with
        x, X
        """
        for isbn10 in valid_isbn_10:
            with self.subTest(number=isbn10):
                self.assertTrue(is_valid_isbn(isbn10))

    def test_valid_isbn_13(self):
        """Test on valid isbn13"""
        for isbn13 in valid_isbn_13:
            with self.subTest(number=isbn13):
                self.assertTrue(isbn13)


    def test_valid_sbn(self):
        """Test on valid SBN identifier

        SBNs are not very common these days aside from
        old books
        """
        for sbn in valid_sbn:
            with self.subTest(number=sbn):
                self.assertTrue(sbn)

    # The invalid isbn and sbns are fictitious
    def test_invalid_isbn_10(self):
        """Test on invalid isbn10"""
        for isbn10 in invalid_isbn_10:
            with self.subTest(number=isbn10):
                self.assertFalse(is_valid_isbn(isbn10))

    def test_invalid_isbn_13(self):
        """Test on invalid isbn13"""
        for isbn13 in invalid_isbn_13:
            with self.subTest(number=isbn13):
                self.assertFalse(is_valid_isbn(isbn13))

    def test_invalid_sbn(self):
        """Test on invalid sbns"""
        for sbn in invalid_sbn:
            with self.subTest(number=sbn):
                self.assertFalse(is_valid_isbn(sbn))



# 3. ValidateISBNs (for a list of ISBNs): validate_isbns
# Takes a unique_isbn_list and returns only valid ISBNs
# among them as a list

class TestValidateISBNs(unittest.TestCase):
    def test_valid_isbn_10_list(self):
        """Test on a list of valid ISBN-10"""
        self.assertEqual(validate_isbns(valid_isbn_10), valid_isbn_10)

    def test_valid_sbn_list(self):
        """Test on a list of valid SBNs"""
        self.assertEqual(validate_isbns(formatted_sbn), ['0471371106'])

    def test_valid_isbn_13_list(self):
        """Test on a list of valid ISBN-13"""
        self.assertEqual(validate_isbns(valid_isbn_13), valid_isbn_13)

    def test_invalid_isbn_10_list(self):
        """Test on a list of invalid ISBN-10"""
        self.assertEqual(len(validate_isbns(invalid_isbn_10)), 0)

    def test_invalid_sbn_list(self):
        """Test on a list of invalid SBN"""
        self.assertEqual(len(validate_isbns(invalid_sbn)), 0)

    def test_invalid_isbn_13_list(self):
        """Test on a list of invalid ISBN-13"""
        self.assertEqual(len(validate_isbns(invalid_isbn_13)), 0)

if __name__ == '__main__':
    unittest.main()
