"""
The isbn_regex module matches ISBN numbers in a
PDF document using regex, validates ISBN numbers
and formats them for use in this and other modules.
"""

import re
import sqlite3

from .logger import create_logger

logger = create_logger("isbn_regex")


r"""Some notes on ISBN
ISBN is the international standard book number that was adopted by ISO
as a unique identifier for books and some other publications. It is a
ten- or thirteen-digit number, containing four or five groups of numbers
for ISBN10 and ISBN13 respectively, used to manage books in libraries,
bookstores, publishing houses, etc. Although there are other identifiers,
ISBN remains a very common identifier for books.

The format of the ISBN identifier is:\d{a}\d{b}\d{c}\{d}\{e},
where a+b+c+d=10 for ISBN10 a+b+c+d=13 for ISBN13. Separators may
also be included between the groups.

The ISBN identifier has five parts denoted by letters \d{a} to \d{e}.
In the ISBN, the first (a) and last(e) groups have a fixed number of
elements 3 and 1 respectively. The remaining groups (b,c,d) vary in length.

The groups in ISBN are defined below;
1. Prefix element (a): The prefix element has a constant length of 3 digits.
                        It is issued by GS1 and valued 978 or 979.

2. Registration group element (b): It represents country, geographical region,
                                or language group of the place of publication
                                of book. The registration group element if the
                                ISBN can ranges from 1 to 5 digits in length. This
                                code is assigned by the international ISBN Agency

3. Registrant element (c): This identifies a publisher within the publication group and
                        is issued by country ISBN agency at place of publicationt to
                        each publisher. The length ranges from 1 to 7 digits and is
                        inversely proportioal to the publisher's output.

4. Publication element(d):  It identifies specific titles or editions by
                            a publisher. The length of the publication element ranges
                            from 1 to 6 digits and is directly propeortional to publisher
                            output with a zero indicating the absence of a digit

5. Check digit (e): The check digit establishes the validity of the ISBN number. It has
                    a constant length of 1 digit. Its value is calculated using a modulus 11
                    (for isbn 10) or modulus 10 (for isbn 13) algorithm
"""



# ISBN regex pattern explanation:
# -The first group:
#  (\d{3}-|\d{3}\s|\d{3}:|\d{3})?
#  Captures prefix element in ISBN-13

# -The second group:
#  (\d{1,5}[-\s]\d{1,7}[-\s]\d{1,6}(?:[-\s])?(?:[\dxX])?|\d{9}[\dxX]?)
#  The terms before pipe operator "|" capture ISBN-10 with groups separated by
#  space or hyphen, ISBN-10 ending in x or X, ISBN-13 with separators when the
#  first group is matched also,
#  9-digit SBNs with separators (if matching stops at \d{1,6}). After the
#  pipe operator, regex matches 9 digit SBNs with no separators, ISBN-10
#  with 10 digits and no separators, ISBN-10 (with no separators) ending in x or X.
#
# NOTEs:
# - SBNs have no check digit and prefix elements, so we only matched the three
# variable groups.
# - It may be difficult to find ISBN patterns not yet included in
#   the regex expression above as the aforementioned cover almost all
#   ISBN formats available.
# - We have captured two groups in regex to separate the prefix element
# - from the remaining groups. To match regex as one number without capturing
# - the groups separately, the formats of the groups are changed from (...)(...) to
# - (?:...)(?:...) to match and not capture the two groups as separate.
isbn_pattern = re.compile(
    r"""(\d{3}-|\d{3}\s|\d{3}:|\d{3})?
        (\d{1,5}[-\s]\d{1,7}[-\s]\d{1,6}(?:[-\s])?(?:[\dxX])?|
         \d{9}[\dxX]?)""", re.VERBOSE
)


def is_valid_isbn(isbn):
    """
    Checks if an extracted ISBN is valid.

    Cases handled:
        1. 10 digit all numbers
        2. 10 digits ending in X or x
        3. 13 digits

    ISBN 10 has 10 digits and ISBN 13 is a 13 digit number
    The last digit of an ISBN number is the check
    digit. This number can be verified using the previous
    12 (for ISBN 13) or previous 9 digits (for ISBN 10).
    The calculation involved is called check digit
    calculation and it's been explained by the official
    ISBN agency @ www.isbn.org (see links to useful resources
    below). See specific explanation for each ISBN type below.

    ISBN 10 validation (modulus 11 operation):
    When each number (starting from the beginning) is multiplied
    by numbers 10 to 1, the resulting sum must be divisible by 11.
    In practice, we exclude the last digit from this summation and
    simply multiply first 9 digit by numbers 10 to 2 and adding all
    the products. The calculated check digit is the number needed to
    make the total sum the next higher multiple of 11. That is, when
    the resulting sum is added to the check digit, the result must be
    divisible by 11 without a remainder for the number to be a valid
    ISBN 10 number. This is the main priciple behind ISBN 10 check
    digit calculation. To carryout the calculation on a computer,
    a modulo 11 operation is used.

    


    ISBN 13 validation (a mod 10 operation):
    When each number in an ISBN number is multiplied by alternating 1 and 3
    till the 13th digit, the resulting sum must be divisible by 10.
    In practice, we exclude the last digit in this calculation and instead
    multiply the first 12 digits by alternating 1 and 3 and sum all products.
    The calculated check digit is the number needed to make the calculated sum
    to be the next higher multiple of 10. This implies that when the calculated
    sum is added to the unknown check digit, the resulting number must be a multiple
    of 10 without a remainder for he number to be a valid ISBN. This is the method
    employed in ISBN 10 check digit calculation. This calculation is carried
    out on computer using modulo 10 operation on alternating 1 and 3 multipliers.
    
    The resulting sum should be the number needed to
    make the total sum the next higher multiple of 11. That is, when
    the resulting sum is added to the check digit, the result must be
    divisible by 11 without a remainder for the number to be a valid
    ISBN 10 number. This is the main priciple behind ISBN 10 check
    digit calculation. To carryout the calculation on a computer,
    a modulo 11 operation is used.

    NB: Modulus operator simply takes the remainder when a number is divided by another.
    For instance, modulus (mod) 11 is simply the remainder when a number is divided
    by 11. The format is "N modulus 11".
    Example: 35 modulus 11 = 2 (in python: 35 % 11; % is modulus operator)


    Sources:
    ISBN-10:
    Official ISBN Users' manual(4th edition(int'l)-1999):
    https://web.archive.org/web/20130522043458/http://www.isbn.org/
    standards/home/isbn/international/html/usm4.htm

    ISBN-13:
    Official ISBN Users' manual(6th edition(int'l)-2012):
    https://www.isbn-international.org/sites/default/files/
    ISBN%20Manual%202012%20-corr.pdf


    ISBN- 10&13:
    https://en.wikipedia.org/wiki/ISBN
    """

    # Get check digit (the last element) from provided ISBN in book
    try:
        book_check_digit = int(isbn[-1])
    except ValueError:
        # when checkdigit is 'X' (or in some cases 'x'
        book_check_digit = isbn[-1].upper()

    # ISBN 10 check digit calculation (mod 11):
    # To multiply first 9 numbers by 10, 9, 8,...,2, you multiply by
    # (11-(index+1)) so that for number at index 0, the multiplier is
    # 10 (11 - (0+1)), at index 1 it is 9 (11 -(1+1)), at index 2 it is
    # 8(11-(2+1)) and so on. The last digit of ISBN 10 ranges from 0 to 10
    # and in the latter case, 10 is represented by 'X' in the ISBN number.
    # the one (1) added to index changes indexing from 0 (python default) to 1.
    if len(isbn) == 10:

        # Total of (first nine digit * multiplier)
        # First nine digit = int(digit)
        # Multipler = 11 - (index + 1)
        total = 0

        for index, digit in enumerate(isbn[0:9]):
            total = total + (11 - (index + 1)) * int(digit)

        calculated_check_digit = 11 - (total % 11)

        # If calculated check digit is equal to 10, the value is 'X'
        # and if it's greater than 10, it's value is zero (0). Otherwise,
        # use the checkdigit calculated from loop above
        if calculated_check_digit == 10:
            calculated_check_digit = "X"
        elif calculated_check_digit == 11:
            calculated_check_digit = 0
        else:
            # this is just to avoid the assignment:
            # calculated_check_digit = calculated_check_digit
            calculated_check_digit = 11 - (total % 11)

    elif len(isbn) == 13:
        # # ISBN 13 check digit calculation (mod 10):
        # To multiply numbers in ISBN digits 1 to 12 by alternating 1 and 3
        # we first convert index of numbers to 1 so that for multipliers at
        # index 1, 2, 3, 4,... to be respectively 1, 3, 1, 3,...numbers with
        # odd index must be multiplied by 1 and numbers with even index must
        # be multiplied by 3. To test your understanding of this, the multiplier
        # at index 12 will be?..3 since 3 is an even number. We take modulus
        # 10 of the sum (remainder when number is divided by 10). The resulting
        # remainder here can range from 0 to 9. We then subtract the remainder
        # from 10 to get final calculated check digit and make the check digit
        # to range from 1 to 10. 

        total = 0
        
        for index, digit in enumerate(isbn[0:12]):
            if (index + 1) % 2 == 0:
                total = total + int(digit) * 3
            else:
                total = total + int(digit) * 1

        calculated_check_digit = 10 - (total % 10)

        # If the calculated check digit is 10, it is represented by with a
        # zero(0) else it's the earlier estimated check digit. The one in
        # (index+1) is to change indexing from 0 (default in python) to 1.
        if calculated_check_digit == 10:
            calculated_check_digit = 0
        else:
            calculated_check_digit = 10 - (total % 10)

    else:
        # Numbers not 10 or 13 digits long are not valid ISBNs
        return False


    logger.info(
        f"""book_check_digit = {book_check_digit},
        calculated_check_digit={calculated_check_digit}""")

    return (calculated_check_digit == book_check_digit)


def format_isbn(matched_isbn):
    """
    Format isbn into a list containing valid and unique isbns.

    The regex-extracted isbn is a list (named matched_isbn) of list
    containing a list of tuples with the format (for two matches):
    [[('978', '2349494949'),('978', '23556778949')]]
    """

    # Fetch content of the inner list using it's zero index
    # The matched_isbn_tuples is a list of tuples
    # matched_isbn_tuples = matched_isbn[0]

    # Merge the different parts of matched isbn (contained in
    # matched_isbn_tuples) into one, append all values to a new list
    # isbn_list

    isbn_list = []

    # for val in matched_isbn_tuples:
    for val in matched_isbn:
        if len(val) == 0:
            print(f"VAL is empty")
            return


        merged_isbn = val[0] + val[1]

        # ISBNS are typically separated by spaces or hyphens
        # and these are of no use in our API search.
        space_removed_isbn = merged_isbn.replace(" ", "")
        isbn = space_removed_isbn.replace("-", "")

        isbn_list.append(isbn)

    logger.info(f"ISBN LIST: {isbn_list}")
    print(f"ISBN LIST: {isbn_list}")

    # Values below 9 digits are not valid ISBNs or SBNs
    for val in isbn_list.copy():
        if len(val) < 9:
            val_index = isbn_list.index(val)
            del isbn_list[val_index]

    logger.info(f"CLEANED ISBN LIST: {isbn_list}")
    print(f"CLEANED ISBN LIST: {isbn_list}")

    # extract only unique isbn into unique_isbn list
    unique_isbn = []

    for val in isbn_list:
        # Modify 9-digit SBNs by adding a zero as first digit
        # before adding unique values to unique_isbn_list
        # SBN is the precursor to the current ISBN, which came
        # in 1970. Matching SBNs makes it easy to work on older
        # books.
        if len(val) == 9:
            val = "0" + val

        # isalnum() eliminates matches with  symbols such as
        # '\n, @$/.&' which are not valid ISBN digits
        if (val not in unique_isbn) and val.isalnum():
            unique_isbn.append(val)
        else:
            del val

    logger.info(f"UNIQUE ISBN: {unique_isbn}")
    print(f"UNIQUE ISBN: {unique_isbn}")

    # Validate isbn
    valid_isbn = []
    for val in unique_isbn:
        # print(f"VAL: {val}")
        if is_valid_isbn(val):
            valid_isbn.append(val)
        else:
            del val
        logger.info(f"Valid ISBNS: {valid_isbn}")
    return valid_isbn


def get_valid_isbns(extracted_text):
    """
    Match ISBNs in an extracted text, format and validate
    ISBNS. into matched_isbn list
    """
    matched_isbn = []

    matched_regex = isbn_pattern.findall(extracted_text)

    # matched_isbn.append(matched_regex)

    matched_isbn = matched_regex
    

    print(f"MATCHED ISBN: {matched_isbn}")

    import time
    time.sleep(5)

    valid_isbn = format_isbn(matched_isbn)

    return valid_isbn


"""
Add isbns in valid_isbn list to a set containing isbns
def add_isbn_to_set(isbn_list, isbn_set):
    for isbn in isbn_list:
        isbn_set.add(isbn)
    return isbn_set
"""


def isbns_in_set(isbn_list, isbn_set):
    """
    Check isbn_set for presence of isbns in extracted isbn_list.

    This prevents duplication of requests to API
    """
    outcome = []
    
    for isbn in isbn_list:
        if isbn in isbn_set:
            outcome.append(True)
        else:
            outcome.append(False)

    # 'and outcome' eliminates case of empty list which
    # also return true with any()
    if all(outcome) and outcome:  
        return True
    else:
        return False

def add_to_ref_isbn_set(ref_isbn, ref_isbn_set):
    """Add ref_isbn to ref_isbn_set"""
    ref_isbn_set.add(ref_isbn)
    return None


if __name__ == '__main__':
    # Check_isbn_regex

    # Test isbn_validator
    print(is_valid_isbn('0596520689'))
