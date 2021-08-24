import app.functions as fn

import os
from sys import platform
from flask import jsonify
from flask.wrappers import Response

# Flask configuration
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


# System parameters
PLATFORM = platform


# Files
PATH_APP = os.path.dirname(os.path.abspath(__file__))
PATH_UPLOAD_FOLDER = os.path.join(os.path.dirname(PATH_APP), 'upload_folder')
# Check if PATH_UPLOAD_FOLDER exists or we need to make it
if not os.path.exists(PATH_UPLOAD_FOLDER):
    os.mkdir(PATH_UPLOAD_FOLDER)


# Session parameters
SESSION_STATUS_ACTIVE = 'active'
SESSION_STATUS_CLOSED = 'closed'


# Chart parameters
DF_DAYS_BEFORE = 90
COLUMN_RESULT = '<CLOSE>'


# Session options
# ===============


def collect_session_options():

    # Option: Timeframes
    timeframes = fn.read_session_options_timeframes()
    
    # Option: Markets
    markets = fn.read_session_options_markets()
    
    # Option: Securities
    securities = fn.collect_session_options_securities()

    # Option: Bars number
    barsnumber = [
        {'id': 1, 'name': '10 bars', 'code': '10'},
        {'id': 2, 'name': '15 bars', 'code': '15'},
        {'id': 3, 'name': '50 bars', 'code': '50'},
        {'id': 4, 'name': '100 bars', 'code': '100'}
    ]

    # Option: Time limit
    timelimit = [
        {'id': 1, 'name': '5 sec.', 'code': '5'},
        {'id': 2, 'name': '10 sec.', 'code': '10'},
        {'id': 3, 'name': '30 sec.', 'code': '30'},
        {'id': 4, 'name': '60 sec.', 'code': '30'},
        {'id': 5, 'name': '120 sec.', 'code': '120'}
    ]

    # Option: Iterations
    iterations = [
        {'id': 1, 'name': '5', 'code': '5'},
        {'id': 2, 'name': '10', 'code': '10'},
        {'id': 3, 'name': '20', 'code': '20'},
        {'id': 4, 'name': '50', 'code': '50'}
    ]
    
    # Option: Slippage
    slippage = [
        {'id': 1, 'name': '0%', 'code': '0'},
        {'id': 2, 'name': '0.1%', 'code': '0.1'},
        {'id': 3, 'name': '0.5%', 'code': '0.5'},
        {'id': 4, 'name': '1%', 'code': '1'}
    ]

    # Option: Fixing bar
    fixingbar = [
        {'id': 1, 'name': '10', 'code': '10'},
        {'id': 2, 'name': '15', 'code': '15'},
        {'id': 3, 'name': '20', 'code': '20'},
        {'id': 4, 'name': '50', 'code': '50'}
    ]

    # Final list
    session_options = {
        'markets': markets,
        'securities': securities,
        'timeframes': timeframes,
        'barsnumber': barsnumber,
        'timelimit': timelimit,
        'iterations': iterations,
        'slippage': slippage,
        'fixingbar': fixingbar
    }

    return session_options