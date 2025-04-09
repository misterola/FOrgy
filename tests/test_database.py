"""
Tests on database creation, content viewing,
and content extraction.
"""
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
)

from forgy.database import (
    create_db_and_table,
    view_database_table,
    get_all_metadata, 
)
