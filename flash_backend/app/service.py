import app.config as cfg
import os
import sys
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


def generate_filename_session(session):
    """ Get filename for current session """

    # Generate dirname
    if cfg.PLATFORM == 'win32':
        dir_path = cfg.PATH_DOWNLOADS + '\\' + str(session.SessionId) + '_' + str(session.Ticker) + '\\'
    else:
        dir_path = cfg.PATH_DOWNLOADS + '/' + str(session.SessionId) + '_' + str(session.Ticker) + '/'

    # Create dirs if not exist
    for dir in [cfg.PATH_DOWNLOADS, dir_path]:
        if not os.path.exists(dir):
            os.mkdir(dir)

    # Generate filename
    if cfg.SAVE_FORMAT == 'csv':
        filename = 'session_' + str(session.SessionId) + '.csv'
    elif cfg.SAVE_FORMAT == 'json':
        filename = 'session_' + str(session.SessionId) + '.json'

    # Return full path
    return dir_path + filename
    
    
def generate_filename_iteration(iteration):
    """ Get filename for current iteration """

    # Generate dirname
    if cfg.PLATFORM == 'win32':
        dir_path = cfg.PATH_DOWNLOADS + '\\' + str(iteration.SessionId) + '_' + str(iteration.Session.Ticker) + '\\'
    else:
        dir_path = cfg.PATH_DOWNLOADS + '/' + str(iteration.SessionId) + '_' + str(iteration.Session.Ticker) + '/'

    # Create dirs if not exist
    for dir in [cfg.PATH_DOWNLOADS, dir_path]:
        if not os.path.exists(dir):
            os.mkdir(dir)
    
    # Generate filename
    if cfg.SAVE_FORMAT == 'csv':
        filename = 'iteration_' + str(iteration.SessionId) + '_' + str(iteration.IterationNum) + '.csv'
    elif cfg.SAVE_FORMAT == 'json':
        filename = 'iteration_' + str(iteration.SessionId) + '_' + str(iteration.IterationNum) + '.json'

    # Return full path
    return dir_path + filename