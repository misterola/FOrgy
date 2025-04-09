"""
Tests to establish metadata search
capabilities usigGoogle and Openlibrary
APIs
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
)
from forgy.metadata_search import (
    get_metadata_google,
    get_metadata_openlibrary,
    get_single_book_metadata,
    get_book_covers,
)
