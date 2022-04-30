import os
from sys import platform

from finam.export import Exporter           # https://github.com/ffeast/finam-export
from finam.const import Market, Timeframe   # https://github.com/ffeast/finam-export


# General app settings
# ====================

# Application's system users
USER_DEMO_EMAIL = 'demo@alekseisemenov.ru'
USER_DEMO_NAME = 'demo'
USER_DEMO_PASSWORD = 'demo'
USER_TEST_EMAIL = 'test@alekseisemenov.ru'
USER_TEST_NAME = 'test'
USER_TEST_PASSWORD = 'uc8a&Q!W'

# Files
PLATFORM = platform
SAVE_FORMAT = 'json' # Options: 'json' or 'csv'
PATH_APP = os.path.dirname(os.path.abspath(__file__))
PATH_DOWNLOADS = os.path.join(os.path.dirname(PATH_APP), 'downloads')

# Session parameters
SESSION_STATUS_CREATED = 'created'
SESSION_STATUS_ACTIVE = 'active'
SESSION_STATUS_CLOSED = 'closed'
DAYS_IN_WEEK = 5
DAYS_IN_MONTH = 21
TRADINGDAY_DURATION_MINS = (9*60) - 15 - 5  # Standart trading day duration in minutes
DOWNLOAD_SAFETY_FACTOR = 1.1    # Multiply on this value to ensure downloading df with enough data
RANDOM_WORKDAY_LIMIT = 500  # How many business days in the past use to get random business day


# Flask configuration
# ===================

class FlaskConfig(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'flashDecisionSecretKey'
    SQLALCHEMY_DATABASE_URI = "postgresql://" + os.environ.get('DATABASE_USER') + ":" \
                              + os.environ.get('DATABASE_PASS') + "@" \
                              + os.environ.get('DATABASE_URL') + ":" \
                              + os.environ.get('DATABASE_PORT') \
                              if os.environ.get('DATABASE_URL') \
                              else "postgresql://postgres:flash!Pass@localhost:5432"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_PREFIX = '/api'
    HOST = '0.0.0.0'
    PORT = 8001


# Session options
# ===============

class SessionOptions:
    """Collect in one instance all session options"""

    # Limit new session creation perimeter
    _MARKETS_EXCLUDE_LIST = ('FUTURES_ARCHIVE', 'FUTURES_USA', 'CURRENCIES', 'SPB')
    _TIMEFRAME_EXCLUDE_LIST = ('TICKS', 'WEEKLY', 'MONTHLY')

    # Attributes for storing parsed finam data (options)
    markets = []
    tickers = {}
    timeframes = []

    # Mapping tables (Raw name -> Beautiful name alias)
    aliases_markets = {
            'BONDS': 'Bonds',
            'COMMODITIES': 'Commodities',
            'CURRENCIES_WORLD': 'Currencies',
            'ETF': 'International ETFs',
            'ETF_MOEX': 'Russian ETFs',
            'FUTURES': 'Futures',
            'INDEXES': 'Indexes',
            'SHARES': 'Russian shares',
            'USA': 'International shares',
            'CRYPTO_CURRENCIES': 'Cryptocurrencies',
        }

    aliases_timeframes = {
            'MINUTES1': '1 min.',
            'MINUTES5': '5 min.',
            'MINUTES10': '10 min.',
            'MINUTES15': '15 min.',
            'MINUTES30': '30 min.',
            'HOURLY': '1 hour',
            'DAILY': '1 day',
        }

    # Option: Bars number
    barsnumber = (
        {'id': 1, 'name': '15 bars', 'code': '15'},
        {'id': 2, 'name': '30 bars', 'code': '30'},
        {'id': 3, 'name': '50 bars', 'code': '50'},
        {'id': 4, 'name': '100 bars', 'code': '100'}
    )

    # Option: Time limit
    timelimit = (
        {'id': 1, 'name': '5 sec.', 'code': '5'},
        {'id': 2, 'name': '10 sec.', 'code': '10'},
        {'id': 3, 'name': '30 sec.', 'code': '30'},
        {'id': 4, 'name': '60 sec.', 'code': '30'},
        {'id': 5, 'name': '120 sec.', 'code': '120'}
    )

    # Option: Iterations
    iterations = (
        {'id': 1, 'name': '5', 'code': '5'},
        {'id': 2, 'name': '10', 'code': '10'},
        {'id': 3, 'name': '20', 'code': '20'},
        {'id': 4, 'name': '30', 'code': '30'}
    )
    
    # Option: Slippage
    slippage = (
        {'id': 1, 'name': '0%', 'code': '0'},
        {'id': 2, 'name': '0.1%', 'code': '0.001'},
        {'id': 3, 'name': '0.5%', 'code': '0.005'},
        {'id': 4, 'name': '1%', 'code': '0.01'}
    )

    # Option: Fixing bar
    fixingbar = (
        {'id': 1, 'name': '10', 'code': '10'},
        {'id': 2, 'name': '15', 'code': '15'},
        {'id': 3, 'name': '20', 'code': '20'},
        {'id': 4, 'name': '50', 'code': '50'}
    )

    def __repr__(self) -> str:
        """Return the user email"""
        return f'<Session options>'
    
    def __new__(self) -> dict:
        """Collect all session options in a single object before exporting to frontend"""

        # Check if parsed options is not saved in class attributes yet
        if not all((self.markets, self.tickers, self.timeframes)):
            self.update()

        # Final list
        session_options = {
            'markets': self.markets,
            'tickers': self.tickers,
            'timeframes': self.timeframes,
            'barsnumber': self.barsnumber,
            'timelimit': self.timelimit,
            'iterations': self.iterations,
            'slippage': self.slippage,
            'fixingbar': self.fixingbar
        }

        return session_options

    @classmethod
    def _parse_markets(cls) -> None:
        """Read all markets from finam module (hardcoded enum in external lib)"""

        # Prepare export: convert enum to list of formatted objects
        for idx, market in enumerate(Market):
            # Skip excluded markets
            if market.name in cls._MARKETS_EXCLUDE_LIST:
                continue
            # Format object before export (+1 for idx because of vue-simple-search-dropdown)
            options = {'id': idx+1, 'name': cls.aliases_markets[market.name], 'code': market.name}
            cls.markets.append(options)

        # Sort markets by name
        cls.markets.sort(key=lambda x: x['name'])

    @classmethod
    def _parse_tickers(cls) -> None:
        """Read all markets from finam module (hardcoded in external lib) and enrich it by downloaded tickers"""

        # Read tickers for every market and convert it to dict
        exporter = Exporter()
        for market in Market:
            # Skip excluded markets
            if market.name in cls._MARKETS_EXCLUDE_LIST:
                continue
            # Find tickers by market name
            tickers = exporter.lookup(market=market)
            # Drop duplicated codes
            tickers = tickers.drop_duplicates()
            # Drop removed tickers
            tickers = tickers[tickers['code'].str.match('.*-RM')==False]
            # Copy index to column
            tickers.reset_index(inplace=True)
            # Replace special symbols in ticker's names
            tickers['name'] = tickers.loc[:, 'name'].apply(lambda str: str.replace('(', ' - ').replace(')', '').replace('\\', ''))
            # Add ticker's code to displayed name
            tickers['name'] = tickers['name'] + ' - ' + tickers['code']
            # Create filled dict of dicts instead of pandas df
            cls.tickers[market.name] = tickers.to_dict(orient='records')
            # Order tickers for every market by name
            cls.tickers[market.name].sort(key=lambda x: x['name'])
            
    @classmethod
    def _parse_timeframes(cls) -> None:
        """Read timeframes from finam module (hardcoded in external lib)"""

        # Prepare export: convert enum to list of formatted objects 
        for idx, tf in enumerate(Timeframe):
            # Skip some timeframes from the session's options list
            if tf.name in cls._TIMEFRAME_EXCLUDE_LIST:
                continue
            # Format object before export (+1 for idx because of vue-simple-search-dropdown)
            option = {'id': idx+1, 'name': cls.aliases_timeframes[tf.name], 'code': tf.name}
            cls.timeframes.append(option)

    @classmethod
    def update(cls) -> None:
        """Parse finam data and save results in class attributes"""
        if not all((cls.markets, cls.tickers, cls.timeframes)):
            cls._parse_markets()
            cls._parse_tickers()
            cls._parse_timeframes()

    @classmethod
    def find_alias_ticker(cls, market, ticker) -> str:
        """Find in class ticker for specified market and return full name of it"""
        market_tickers = cls.tickers[market]
        ticker_alias = [t['name'] for t in market_tickers if t['code'] == ticker][0]
        return ticker_alias

    @staticmethod
    def convert_tf_to_min(tf: str) -> int:
        """Map timeframe names with their duration in minutes"""
        minutes_in_timeframe = {
            'MINUTES1': 1,
            'MINUTES5': 5,
            'MINUTES10': 10,
            'MINUTES15': 15,
            'MINUTES30': 30,
            'HOURLY': 60,
            'DAILY': 24*60
        }
        return minutes_in_timeframe[tf]
