import os


# Flask configuration
class FlaskConfig(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'flashDecisionSecretKey'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///../flash_decision.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# SQL table names
SQL_TABLE_SESSIONS = 'sessions'
SQL_TABLE_DECISIONS = 'decisions'


# Files
PATH_APP = os.path.dirname(os.path.abspath(__file__))
PATH_UPLOAD_FOLDER = os.path.join(os.path.dirname(PATH_APP), 'upload_folder') # go up one folder


# Session parameters
SESSION_STATUS_ACTIVE = 'active'
SESSION_STATUS_CLOSED = 'closed'


# Chart parameters
DF_DAYS_BEFORE = 90
COLUMN_RESULT = '<CLOSE>'