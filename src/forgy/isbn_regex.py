# AUTOGENERATE POSSIBLE ISBN VALUES IN VERBOSE FORM
import re
import sqlite3


# Rules applied to isbn 10 or last 10 digits in ISBN 13:
# The format is abcd (\d{a}-\d{b}-\d{c}-\d{d})where a+b+c+d=10,
# and each of a-d ranges from 1-9.

# def sum_of_four(a, b, c, d):
# total = a + b + c + d
# return total


def sum_of_values(*vals):
    total = 0
    for val in vals:
        total = total + val
    return total
    # print(sum_of_values(1,2,3,4))


isbn_ten_formats = []   # See a list of number combinations
isbn_regx = []
for a in range(1, 10):
    for b in range(1, 10):
        for c in range(1, 10):
            for d in range(1, 10):
                if sum_of_values(a, b, c, d) == 10:
                    str_isbn_format = str(a) + str(b) + str(c) + str(d)
                    isbn_ten_formats.append(str_isbn_format)
                    isbn_reg = (
                        r"\d{" + f"{a}" + r"}" + "-"
                        + r"\d{" + f"{b}" + r"}" + "-"
                        + r"\d{" + f"{c}" + r"}" + "-"
                        + r"\d{" + f"{d}" + r"}"
                        + "|"
                        + r"\d{" + f"{a}" + r"}" + r"\s"
                        + r"\d{" + f"{b}" + r"}" + r"\s"
                        + r"\d{" + f"{c}" + r"}" + r"\s"
                        + r"\d{" + f"{d}" + r"}"
                        + "|"
                    )

                    isbn_regx.append(isbn_reg)


# print(isbn_ten_formats)
# print(isbn_regx)
# print(f"Len isbn_ten_formats: {len(isbn_ten_formats)}")

# 1. First three digits
first_three_digit = r"(\d{3}-|\d{3}\s|\d{3}:|\d{3})?"

# 2. Next ten digits
# for val in isbn_regx:
#    print(val)

# 3. Matches for isbn 10 ending in x
# Rules applied to ISBN 10 ending in x or X or SBNs with only 9 digits:
# The format is abcx or abcX (\d{a}-\d{b}-\d{c}-X)where a+b+c=9,
# and each of a-d ranges from 1-9.

isbn_x_formats = []
isbn_x_regx = []
for a in range(1, 10):
    for b in range(1, 10):
        for c in range(1, 10):
            if sum_of_values(a, b, c) == 9:
                str_isbn_format = str(a) + str(b) + str(c) + "X"
                isbn_x_formats.append(str_isbn_format)
                isbn_reg = (
                    r"\d{" + f"{a}" + r"}" + "-"
                    + r"\d{" + f"{b}" + r"}" + "-"
                    + r"\d{" + f"{c}" + r"}" + "-"
                    + r"([-xX])*"
                    + "|"
                    + r"\d{" + f"{a}" + r"}" + r"\s"
                    + r"\d{" + f"{b}" + r"}" + r"\s"
                    + r"\d{" + f"{c}" + r"}" + r"\s"
                    + r'([-xX])*'
                    + r"|"
                )
                isbn_x_regx.append(isbn_reg)

# for val in isbn_x_regx:
#    print(val)

# 4. match ISBN-10 with consecutive digits and no seperators

ten_digits = r"\d{10}|"

# 5. match ISBN-10 with 9 digits ending in x and SBNs with 9 digits
nine_digits = r"\d{9}[xX]?)"


# 6. Combine 1 to 5 to create multiline isbn regex patterns (print in interactive window and paste here)

"""AUTOGENERATE ALL REGEX PATTERNS
print(first_three_digit)

print("(", end="")

for val in isbn_regx:
    print(val)

for val in isbn_x_regx:
    print(val)

    print(ten_digits, end="")

    print(nine_digits, end="")
"""

# The final isbn regex (this is auto-generated. Do not modify)
isbn_pattern = re.compile(r'''
    (\d{3}-|\d{3}\s|\d{3}:|\d{3})?
    (\d{1}-\d{1}-\d{1}-\d{7}|\d{1}\s\d{1}\s\d{1}\s\d{7}|
    \d{1}-\d{1}-\d{2}-\d{6}|\d{1}\s\d{1}\s\d{2}\s\d{6}|
    \d{1}-\d{1}-\d{3}-\d{5}|\d{1}\s\d{1}\s\d{3}\s\d{5}|
    \d{1}-\d{1}-\d{4}-\d{4}|\d{1}\s\d{1}\s\d{4}\s\d{4}|
    \d{1}-\d{1}-\d{5}-\d{3}|\d{1}\s\d{1}\s\d{5}\s\d{3}|
    \d{1}-\d{1}-\d{6}-\d{2}|\d{1}\s\d{1}\s\d{6}\s\d{2}|
    \d{1}-\d{1}-\d{7}-\d{1}|\d{1}\s\d{1}\s\d{7}\s\d{1}|
    \d{1}-\d{2}-\d{1}-\d{6}|\d{1}\s\d{2}\s\d{1}\s\d{6}|
    \d{1}-\d{2}-\d{2}-\d{5}|\d{1}\s\d{2}\s\d{2}\s\d{5}|
    \d{1}-\d{2}-\d{3}-\d{4}|\d{1}\s\d{2}\s\d{3}\s\d{4}|
    \d{1}-\d{2}-\d{4}-\d{3}|\d{1}\s\d{2}\s\d{4}\s\d{3}|
    \d{1}-\d{2}-\d{5}-\d{2}|\d{1}\s\d{2}\s\d{5}\s\d{2}|
    \d{1}-\d{2}-\d{6}-\d{1}|\d{1}\s\d{2}\s\d{6}\s\d{1}|
    \d{1}-\d{3}-\d{1}-\d{5}|\d{1}\s\d{3}\s\d{1}\s\d{5}|
    \d{1}-\d{3}-\d{2}-\d{4}|\d{1}\s\d{3}\s\d{2}\s\d{4}|
    \d{1}-\d{3}-\d{3}-\d{3}|\d{1}\s\d{3}\s\d{3}\s\d{3}|
    \d{1}-\d{3}-\d{4}-\d{2}|\d{1}\s\d{3}\s\d{4}\s\d{2}|
    \d{1}-\d{3}-\d{5}-\d{1}|\d{1}\s\d{3}\s\d{5}\s\d{1}|
    \d{1}-\d{4}-\d{1}-\d{4}|\d{1}\s\d{4}\s\d{1}\s\d{4}|
    \d{1}-\d{4}-\d{2}-\d{3}|\d{1}\s\d{4}\s\d{2}\s\d{3}|
    \d{1}-\d{4}-\d{3}-\d{2}|\d{1}\s\d{4}\s\d{3}\s\d{2}|
    \d{1}-\d{4}-\d{4}-\d{1}|\d{1}\s\d{4}\s\d{4}\s\d{1}|
    \d{1}-\d{5}-\d{1}-\d{3}|\d{1}\s\d{5}\s\d{1}\s\d{3}|
    \d{1}-\d{5}-\d{2}-\d{2}|\d{1}\s\d{5}\s\d{2}\s\d{2}|
    \d{1}-\d{5}-\d{3}-\d{1}|\d{1}\s\d{5}\s\d{3}\s\d{1}|
    \d{1}-\d{6}-\d{1}-\d{2}|\d{1}\s\d{6}\s\d{1}\s\d{2}|
    \d{1}-\d{6}-\d{2}-\d{1}|\d{1}\s\d{6}\s\d{2}\s\d{1}|
    \d{1}-\d{7}-\d{1}-\d{1}|\d{1}\s\d{7}\s\d{1}\s\d{1}|
    \d{2}-\d{1}-\d{1}-\d{6}|\d{2}\s\d{1}\s\d{1}\s\d{6}|
    \d{2}-\d{1}-\d{2}-\d{5}|\d{2}\s\d{1}\s\d{2}\s\d{5}|
    \d{2}-\d{1}-\d{3}-\d{4}|\d{2}\s\d{1}\s\d{3}\s\d{4}|
    \d{2}-\d{1}-\d{4}-\d{3}|\d{2}\s\d{1}\s\d{4}\s\d{3}|
    \d{2}-\d{1}-\d{5}-\d{2}|\d{2}\s\d{1}\s\d{5}\s\d{2}|
    \d{2}-\d{1}-\d{6}-\d{1}|\d{2}\s\d{1}\s\d{6}\s\d{1}|
    \d{2}-\d{2}-\d{1}-\d{5}|\d{2}\s\d{2}\s\d{1}\s\d{5}|
    \d{2}-\d{2}-\d{2}-\d{4}|\d{2}\s\d{2}\s\d{2}\s\d{4}|
    \d{2}-\d{2}-\d{3}-\d{3}|\d{2}\s\d{2}\s\d{3}\s\d{3}|
    \d{2}-\d{2}-\d{4}-\d{2}|\d{2}\s\d{2}\s\d{4}\s\d{2}|
    \d{2}-\d{2}-\d{5}-\d{1}|\d{2}\s\d{2}\s\d{5}\s\d{1}|
    \d{2}-\d{3}-\d{1}-\d{4}|\d{2}\s\d{3}\s\d{1}\s\d{4}|
    \d{2}-\d{3}-\d{2}-\d{3}|\d{2}\s\d{3}\s\d{2}\s\d{3}|
    \d{2}-\d{3}-\d{3}-\d{2}|\d{2}\s\d{3}\s\d{3}\s\d{2}|
    \d{2}-\d{3}-\d{4}-\d{1}|\d{2}\s\d{3}\s\d{4}\s\d{1}|
    \d{2}-\d{4}-\d{1}-\d{3}|\d{2}\s\d{4}\s\d{1}\s\d{3}|
    \d{2}-\d{4}-\d{2}-\d{2}|\d{2}\s\d{4}\s\d{2}\s\d{2}|
    \d{2}-\d{4}-\d{3}-\d{1}|\d{2}\s\d{4}\s\d{3}\s\d{1}|
    \d{2}-\d{5}-\d{1}-\d{2}|\d{2}\s\d{5}\s\d{1}\s\d{2}|
    \d{2}-\d{5}-\d{2}-\d{1}|\d{2}\s\d{5}\s\d{2}\s\d{1}|
    \d{2}-\d{6}-\d{1}-\d{1}|\d{2}\s\d{6}\s\d{1}\s\d{1}|
    \d{3}-\d{1}-\d{1}-\d{5}|\d{3}\s\d{1}\s\d{1}\s\d{5}|
    \d{3}-\d{1}-\d{2}-\d{4}|\d{3}\s\d{1}\s\d{2}\s\d{4}|
    \d{3}-\d{1}-\d{3}-\d{3}|\d{3}\s\d{1}\s\d{3}\s\d{3}|
    \d{3}-\d{1}-\d{4}-\d{2}|\d{3}\s\d{1}\s\d{4}\s\d{2}|
    \d{3}-\d{1}-\d{5}-\d{1}|\d{3}\s\d{1}\s\d{5}\s\d{1}|
    \d{3}-\d{2}-\d{1}-\d{4}|\d{3}\s\d{2}\s\d{1}\s\d{4}|
    \d{3}-\d{2}-\d{2}-\d{3}|\d{3}\s\d{2}\s\d{2}\s\d{3}|
    \d{3}-\d{2}-\d{3}-\d{2}|\d{3}\s\d{2}\s\d{3}\s\d{2}|
    \d{3}-\d{2}-\d{4}-\d{1}|\d{3}\s\d{2}\s\d{4}\s\d{1}|
    \d{3}-\d{3}-\d{1}-\d{3}|\d{3}\s\d{3}\s\d{1}\s\d{3}|
    \d{3}-\d{3}-\d{2}-\d{2}|\d{3}\s\d{3}\s\d{2}\s\d{2}|
    \d{3}-\d{3}-\d{3}-\d{1}|\d{3}\s\d{3}\s\d{3}\s\d{1}|
    \d{3}-\d{4}-\d{1}-\d{2}|\d{3}\s\d{4}\s\d{1}\s\d{2}|
    \d{3}-\d{4}-\d{2}-\d{1}|\d{3}\s\d{4}\s\d{2}\s\d{1}|
    \d{3}-\d{5}-\d{1}-\d{1}|\d{3}\s\d{5}\s\d{1}\s\d{1}|
    \d{4}-\d{1}-\d{1}-\d{4}|\d{4}\s\d{1}\s\d{1}\s\d{4}|
    \d{4}-\d{1}-\d{2}-\d{3}|\d{4}\s\d{1}\s\d{2}\s\d{3}|
    \d{4}-\d{1}-\d{3}-\d{2}|\d{4}\s\d{1}\s\d{3}\s\d{2}|
    \d{4}-\d{1}-\d{4}-\d{1}|\d{4}\s\d{1}\s\d{4}\s\d{1}|
    \d{4}-\d{2}-\d{1}-\d{3}|\d{4}\s\d{2}\s\d{1}\s\d{3}|
    \d{4}-\d{2}-\d{2}-\d{2}|\d{4}\s\d{2}\s\d{2}\s\d{2}|
    \d{4}-\d{2}-\d{3}-\d{1}|\d{4}\s\d{2}\s\d{3}\s\d{1}|
    \d{4}-\d{3}-\d{1}-\d{2}|\d{4}\s\d{3}\s\d{1}\s\d{2}|
    \d{4}-\d{3}-\d{2}-\d{1}|\d{4}\s\d{3}\s\d{2}\s\d{1}|
    \d{4}-\d{4}-\d{1}-\d{1}|\d{4}\s\d{4}\s\d{1}\s\d{1}|
    \d{5}-\d{1}-\d{1}-\d{3}|\d{5}\s\d{1}\s\d{1}\s\d{3}|
    \d{5}-\d{1}-\d{2}-\d{2}|\d{5}\s\d{1}\s\d{2}\s\d{2}|
    \d{5}-\d{1}-\d{3}-\d{1}|\d{5}\s\d{1}\s\d{3}\s\d{1}|
    \d{5}-\d{2}-\d{1}-\d{2}|\d{5}\s\d{2}\s\d{1}\s\d{2}|
    \d{5}-\d{2}-\d{2}-\d{1}|\d{5}\s\d{2}\s\d{2}\s\d{1}|
    \d{5}-\d{3}-\d{1}-\d{1}|\d{5}\s\d{3}\s\d{1}\s\d{1}|
    \d{6}-\d{1}-\d{1}-\d{2}|\d{6}\s\d{1}\s\d{1}\s\d{2}|
    \d{6}-\d{1}-\d{2}-\d{1}|\d{6}\s\d{1}\s\d{2}\s\d{1}|
    \d{6}-\d{2}-\d{1}-\d{1}|\d{6}\s\d{2}\s\d{1}\s\d{1}|
    \d{7}-\d{1}-\d{1}-\d{1}|\d{7}\s\d{1}\s\d{1}\s\d{1}|
    \d{1}-\d{1}-\d{7}-([-xX])*|\d{1}\s\d{1}\s\d{7}\s([-xX])*|
    \d{1}-\d{2}-\d{6}-([-xX])*|\d{1}\s\d{2}\s\d{6}\s([-xX])*|
    \d{1}-\d{3}-\d{5}-([-xX])*|\d{1}\s\d{3}\s\d{5}\s([-xX])*|
    \d{1}-\d{4}-\d{4}-([-xX])*|\d{1}\s\d{4}\s\d{4}\s([-xX])*|
    \d{1}-\d{5}-\d{3}-([-xX])*|\d{1}\s\d{5}\s\d{3}\s([-xX])*|
    \d{1}-\d{6}-\d{2}-([-xX])*|\d{1}\s\d{6}\s\d{2}\s([-xX])*|
    \d{1}-\d{7}-\d{1}-([-xX])*|\d{1}\s\d{7}\s\d{1}\s([-xX])*|
    \d{2}-\d{1}-\d{6}-([-xX])*|\d{2}\s\d{1}\s\d{6}\s([-xX])*|
    \d{2}-\d{2}-\d{5}-([-xX])*|\d{2}\s\d{2}\s\d{5}\s([-xX])*|
    \d{2}-\d{3}-\d{4}-([-xX])*|\d{2}\s\d{3}\s\d{4}\s([-xX])*|
    \d{2}-\d{4}-\d{3}-([-xX])*|\d{2}\s\d{4}\s\d{3}\s([-xX])*|
    \d{2}-\d{5}-\d{2}-([-xX])*|\d{2}\s\d{5}\s\d{2}\s([-xX])*|
    \d{2}-\d{6}-\d{1}-([-xX])*|\d{2}\s\d{6}\s\d{1}\s([-xX])*|
    \d{3}-\d{1}-\d{5}-([-xX])*|\d{3}\s\d{1}\s\d{5}\s([-xX])*|
    \d{3}-\d{2}-\d{4}-([-xX])*|\d{3}\s\d{2}\s\d{4}\s([-xX])*|
    \d{3}-\d{3}-\d{3}-([-xX])*|\d{3}\s\d{3}\s\d{3}\s([-xX])*|
    \d{3}-\d{4}-\d{2}-([-xX])*|\d{3}\s\d{4}\s\d{2}\s([-xX])*|
    \d{3}-\d{5}-\d{1}-([-xX])*|\d{3}\s\d{5}\s\d{1}\s([-xX])*|
    \d{4}-\d{1}-\d{4}-([-xX])*|\d{4}\s\d{1}\s\d{4}\s([-xX])*|
    \d{4}-\d{2}-\d{3}-([-xX])*|\d{4}\s\d{2}\s\d{3}\s([-xX])*|
    \d{4}-\d{3}-\d{2}-([-xX])*|\d{4}\s\d{3}\s\d{2}\s([-xX])*|
    \d{4}-\d{4}-\d{1}-([-xX])*|\d{4}\s\d{4}\s\d{1}\s([-xX])*|
    \d{5}-\d{1}-\d{3}-([-xX])*|\d{5}\s\d{1}\s\d{3}\s([-xX])*|
    \d{5}-\d{2}-\d{2}-([-xX])*|\d{5}\s\d{2}\s\d{2}\s([-xX])*|
    \d{5}-\d{3}-\d{1}-([-xX])*|\d{5}\s\d{3}\s\d{1}\s([-xX])*|
    \d{6}-\d{1}-\d{2}-([-xX])*|\d{6}\s\d{1}\s\d{2}\s([-xX])*|
    \d{6}-\d{2}-\d{1}-([-xX])*|\d{6}\s\d{2}\s\d{1}\s([-xX])*|
    \d{7}-\d{1}-\d{1}-([-xX])*|\d{7}\s\d{1}\s\d{1}\s([-xX])*|
    \d{10}|\d{9}[xX]?)''', re.VERBOSE)


# Validate isbn number
def is_valid_isbn(isbn):
    """checks if extracted isbn number is valid
        for all cases
        1. 10 digit all numbers
        2. 10 digits ending in X or x
        3. 13 digits
        Note:check  wikipedia https://en.wikipedia.org/wiki/ISBN
            'Check digits' section for checksum calculation. I have
            re-indexed the digits from python's zero to one
        """
    try:
        check_digit = int(isbn[-1])
    except ValueError:
        check_digit = isbn[-1].upper()

    if len(isbn) == 10:

        total = 0
        for i, digit in enumerate(isbn[0:9]):
            # print(i+1,digit)
            total = total + (11 - (i + 1)) * int(digit)
        # print(f'total = {total}')
        calc_digit = 11 - (total % 11)
        if calc_digit == 10:
            calc_digit = "X"
        elif calc_digit == 11:
            calc_digit = 0
        else:
            calc_digit = 11 - (total % 11)
            # print(f"check_digit = {check_digit}, calc_digit = {calc_digit}")

    else:

        total = 0
        for i, digit in enumerate(isbn[0:12]):
            # print(i+1, digit)
            if (i + 1) % 2 == 0:
                total = total + int(digit) * 3
            else:
                total = total + int(digit) * 1
        # print(f'total= {total}')
        calc_digit = 10 - (total % 10)
        if calc_digit == 10:
            calc_digit = 0
        else:
            calc_digit = 10 - (total % 10)
            # print(f'check_digit = {check_digit}, calc_digit={calc_digit}')
    # print(total)
    return (calc_digit == check_digit)


def format_isbn(matched_isbn):
    """Format isbn into a list containing valid,
        unique isbn"""
    # The regex-extracted isbn is a list of list containing list of tuples. \
    # this list is names 'matched_isbn' and the format is\
    # [[('978', '2349494949'),('978', '23556778949')]] for 2 matches

    # Fetch content of the inner list using it's zero index
    matched_isbn_tuples = matched_isbn[0]

    # Merge the different parts of matched isbn (contained in matched_isbn_tuples)
    # into one, append all values to isbn_list
    # Format isbn
    isbn_list = []

    for val in matched_isbn_tuples:
        merged_isbn = val[0] + val[1]

        # Format the isbn by removing spaces and hypens
        space_removed_isbn = merged_isbn.replace(" ", "")
        isbn = space_removed_isbn.replace("-", "")

        # Append formatted isbn to isbn_list
        isbn_list.append(isbn)
        # print(isbn_list)

    # extract only unique isbn into unique_isbn list
    unique_isbn = []

    for val in isbn_list:
        # Modify SBNs by adding a zero as first digit before adding unique values to unique_isbn_list
        if len(val) == 9:
            val = "0" + val

        # isalnum() eliminates matches with  symbols such as '\n, @$/.&' which are not valid
        if (val not in unique_isbn) and val.isalnum():
            unique_isbn.append(val)
        else:
            del val
        # print(unique_isbn)

    # Validate isbn
    valid_isbn = []
    for val in unique_isbn:
        if is_valid_isbn(val):
            valid_isbn.append(val)
        else:
            del val
        # print(valid_isbn)
    return valid_isbn


def get_valid_isbns(extracted_text):
    # Use regex to match isbn in extracted text, into matched_isbn list
    matched_isbn = []
    matched_regex = isbn_pattern.findall(extracted_text)
    matched_isbn.append(matched_regex)
    valid_isbn = format_isbn(matched_isbn)
    return valid_isbn

"""Add isbns in valid_isbn list to a set containing isbns
def add_isbn_to_set(isbn_list, isbn_set):
    for isbn in isbn_list:
        isbn_set.add(isbn)
    return isbn_set
"""


# Check if isbn set for presence of isbns in extracted list
def isbns_in_set(isbn_list, isbn_set):
    outcome = []
    for isbn in isbn_list:
        if isbn in isbn_set:
            outcome.append(True)
        else:
            outcome.append(False)
    if all(outcome) and outcome:  # 'and outcome' eliminates case of empty list which also return true with any()
        return True
    else:
        return False


# Add ref_isbn to ref_isbn_set
def add_to_ref_isbn_set(ref_isbn, ref_isbn_set):
    ref_isbn_set.add(ref_isbn)
    return None


# Check database for existence of isbn in RefISBN column
def is_isbn_in_db(database, table, isbn_list):
    # Extract isbn from database as a set (for better performance)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT RefISBN FROM {table};")
        existing_db_refisbns = cursor.fetchall()  # Has the form [('9780873897365',), ('9781636940274',)]
        ref_isbn_set = set()
        for isbn in existing_db_refisbns:
            add_to_ref_isbn_set(isbn[0], ref_isbn_set)
            # ref_isbn_set.add(isbn[0])

            # valid_isbn_set = set()

        #  Add all valid isbn in isbn_list to valid_isbn_set
        # add_isbn_to_set(isbn_list, valid_isbn)
    return isbns_in_set(isbn_list, ref_isbn_set)  # Are extracted values in list present in set of db ref_isbns

 # tests: is_isbn_in_db, is_valid_isbn, isbns_in_set, format_isbn   

if __name__ == '__main__':
    # Check_isbn_regex
    print(first_three_digit)

    print('(', end='')

    for val in isbn_regx:
        print(val)

    for val in isbn_x_regx:
        print(val)

    print(ten_digits, end='')

    print(nine_digits, end='')

    # Test isbn_validator
    print(is_valid_isbn('0596520689'))
