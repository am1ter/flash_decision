import os
from sys import platform


# == Flask configuration
class FlaskConfig(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'flashDecisionSecretKey'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///../flash_decision.db' # SQLITE
    SQLALCHEMY_DATABASE_URI = "postgresql://" + os.environ.get('DATABASE_USER') + ":" \
                              + os.environ.get('DATABASE_PASS') + "@" \
                              + os.environ.get('DATABASE_URL') + ":" \
                              + os.environ.get('DATABASE_PORT') \
                              if os.environ.get('DATABASE_URL') \
                              else "postgresql://postgres:flash!Pass@localhost:5432"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# == System parameters
PLATFORM = platform


# == Files
PATH_APP = os.path.dirname(os.path.abspath(__file__))
PATH_UPLOAD_FOLDER = os.path.join(os.path.dirname(PATH_APP), 'upload_folder')
# Check if PATH_UPLOAD_FOLDER exists or we need to make it
if not os.path.exists(PATH_UPLOAD_FOLDER):
    os.mkdir(PATH_UPLOAD_FOLDER)


# == Session parameters
SESSION_STATUS_ACTIVE = 'active'
SESSION_STATUS_CLOSED = 'closed'


# == Chart parameters
DF_DAYS_BEFORE = 90
COLUMN_RESULT = '<CLOSE>'
