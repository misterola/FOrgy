"""
Filesystem operations tests
"""

import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
)

from forgy.filesystem_utils import (
    get_files_from_sources,
    organize_files_in_directory,
    delete_files_in_directory,
    copy_directory_contents,
    move_folders,
)  
