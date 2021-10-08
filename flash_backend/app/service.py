import app.config as cfg
import os
import sys
import time
from shutil import copyfile


# ==============================
# == Service functions
# ==============================


def fix_lib_finamexport() -> None:
    """Fix bug in finam-export v.4.1.0 with ParserError / This fix should be runned only once"""
    
    path_lib_finamexport = f'./flash_backend/venv/lib/python{ sys.version[:3] }/site-packages/finam/export.py'
    line_with_bug = 'from pandas.io.parsers import ParserError'
    line_without_bug = 'from pandas.errors import ParserError # amiter bug fix'

    # Read the file with the bug
    if os.path.isfile(path_lib_finamexport):
        with open(path_lib_finamexport, 'r') as file:
            filedata = file.read()

        if line_with_bug in filedata:
            # Make backup of the file with the bug
            copyfile(path_lib_finamexport, path_lib_finamexport[:-3] + '_backup.py')

            # Replace the string with the bug
            filedata = filedata.replace(line_with_bug, line_without_bug)

            # Write the file with correct string
            with open(path_lib_finamexport, 'w') as file:
                file.write(filedata)  


def print_log(string: str) -> str:
    """Print formatted string with local time"""
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ': ' + string)