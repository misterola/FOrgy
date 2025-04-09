"""
Test on main module in forgy package
"""

import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
)

from forgy.messyforg import fetch_book_metadata, get_isbns_from_texts
