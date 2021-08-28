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
SAVE_FORMAT = 'json' # Options: 'json' or 'csv'
PATH_APP = os.path.dirname(os.path.abspath(__file__))
PATH_DOWNLOADS = os.path.join(os.path.dirname(PATH_APP), 'downloads')


# Session parameters
SESSION_STATUS_ACTIVE = 'active'
SESSION_STATUS_CLOSED = 'closed'


# Chart parameters
DF_DAYS_BEFORE = 90
COLUMN_RESULT = '<CLOSE>'


# Session options
# ===============

DOWNLOAD_SAFETY_FACTOR = 2                  # Enlarge time period for quotes downloading
TRADINGDAY_DURATION_MINS = (9*60) - 15 - 5   # Standart trading day duration in minutes


def convert_timeframe_to_mintues(tf: str) -> int:
    """Map timeframe names with their duration in minutes"""
    minutes_in_timeframe = {
        'Timeframe.TICKS': 0,
        'Timeframe.MINUTES1': 1,
        'Timeframe.MINUTES5': 5,
        'Timeframe.MINUTES10': 10,
        'Timeframe.MINUTES15': 15,
        'Timeframe.MINUTES30': 30,
        'Timeframe.HOURLY': 60,
        'Timeframe.DAILY': 24*60,
        'Timeframe.WEEKLY': 7*24*60,
        'Timeframe.MONTHLY': 31*24*60
    }
    return minutes_in_timeframe[tf]


def collect_session_options() -> dict:
    """Collect all session options in a single object"""

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
        {'id': 4, 'name': '30', 'code': '30'}
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