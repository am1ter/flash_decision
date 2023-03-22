from os import environ as env

import requests
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from finam.export import Exporter  # https://github.com/ffeast/finam-export
from finam.const import Market, Timeframe  # https://github.com/ffeast/finam-export


# General app settings
# ====================


# Application's users parameters
USER_AUTH_TIMEOUT = 60
USER_DEMO_EMAIL = 'demo@alekseisemenov.ru'
USER_DEMO_NAME = 'demo'
USER_DEMO_PASS = 'demo'
USER_TEST_EMAIL = 'test@alekseisemenov.ru'
USER_TEST_NAME = 'test'
USER_TEST_PASS = 'uc8a&Q!W'
USER_SIGNUP_EMAIL = 'test-signup@alekseisemenov.ru'

# Files
LOG_STRING_MAX_LENGTH = 500

# Session parameters
PARSE_OPTIONS_AT_STARTUP = True
SESSION_STATUS_CREATED = 'created'
SESSION_STATUS_ACTIVE = 'active'
SESSION_STATUS_CLOSED = 'closed'
DAYS_IN_WEEK = 5
DAYS_IN_MONTH = 21
TRADINGDAY_DURATION_MINS = (9 * 60) - 15 - 5  # Standart trading day duration in minutes
DOWNLOAD_SAFETY_FACTOR = 1.1  # Multiply on this value to ensure downloading df with enough data
RANDOM_WORKDAY_LIMIT = 500  # How many business days in the past use to get random business day

# Scoreboard parameters
TOP_USERS_COUNT = 3


# Flask configuration
# ===================


class FlaskConfig(object):
    SECRET_KEY = env.get('SECRET_KEY') or 'flashDecisionSecretKey'
    dburl = env.get('DATABASE_URL') if env.get('DATABASE_URL') else 'localhost'
    dbport = env.get('DATABASE_PORT') if env.get('DATABASE_PORT') else '5432'
    dbuser = env.get('DATABASE_USER') if env.get('DATABASE_USER') else 'postgres'
    dbpass = env.get('DATABASE_PASS') if env.get('DATABASE_PASS') else 'flash!Pass'
    SQLALCHEMY_DATABASE_URI = 'postgresql://' + dbuser + ':' + dbpass + '@' + dburl + ':' + dbport
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = 8001
    API_PREFIX = '/api'


# Session options
# ===============


class SessionOptions:
    """Collect in one instance all session options"""

    driver: WebDriver = None

    # Limit new session creation perimeter
    _MARKETS_EXCLUDE_LIST = ('FUTURES_ARCHIVE', 'FUTURES_USA', 'CURRENCIES', 'SPB')
    _TIMEFRAME_EXCLUDE_LIST = ('TICKS', 'WEEKLY', 'MONTHLY')

    # Attributes for storing parsed finam data (options)
    exporter = None
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
        {'id': 4, 'name': '100 bars', 'code': '100'},
    )

    # Option: Time limit
    timelimit = (
        {'id': 1, 'name': '5 sec.', 'code': '5'},
        {'id': 2, 'name': '10 sec.', 'code': '10'},
        {'id': 3, 'name': '30 sec.', 'code': '30'},
        {'id': 4, 'name': '60 sec.', 'code': '30'},
        {'id': 5, 'name': '120 sec.', 'code': '120'},
    )

    # Option: Iterations
    iterations = (
        {'id': 1, 'name': '5', 'code': '5'},
        {'id': 2, 'name': '10', 'code': '10'},
        {'id': 3, 'name': '20', 'code': '20'},
        {'id': 4, 'name': '30', 'code': '30'},
    )

    # Option: Slippage
    slippage = (
        {'id': 1, 'name': '0%', 'code': '0'},
        {'id': 2, 'name': '0.1%', 'code': '0.001'},
        {'id': 3, 'name': '0.5%', 'code': '0.005'},
        {'id': 4, 'name': '1%', 'code': '0.01'},
    )

    # Option: Fixing bar
    fixingbar = (
        {'id': 1, 'name': '10', 'code': '10'},
        {'id': 2, 'name': '15', 'code': '15'},
        {'id': 3, 'name': '20', 'code': '20'},
        {'id': 4, 'name': '50', 'code': '50'},
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
            'fixingbar': self.fixingbar,
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
            options = {'id': idx + 1, 'name': cls.aliases_markets[market.name], 'code': market.name}
            cls.markets.append(options)

        # Sort markets by name
        cls.markets.sort(key=lambda x: x['name'])

    @classmethod
    def _parse_tickers(cls) -> None:
        """Read all markets from finam module (hardcoded in external lib) and enrich it by downloaded tickers"""

        # Read tickers for every market and convert it to dict
        for market in Market:
            # Skip excluded markets
            if market.name in cls._MARKETS_EXCLUDE_LIST:
                continue
            # Find tickers by market name
            exporter = cls.get_exporter()
            tickers = exporter.lookup(market=market)
            # Drop duplicated codes
            tickers = tickers.drop_duplicates()
            # Drop removed (filter inactive) tickers from df
            tickers = tickers[tickers['code'].str.match('.*-RM') == False]
            # Copy index to column
            tickers.reset_index(inplace=True)
            # Replace special symbols in ticker's names
            func_replace = lambda str: str.replace('(', ' - ').replace(')', '').replace('\\', '')
            tickers['name'] = tickers.loc[:, 'name'].apply(func_replace)
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
            option = {'id': idx + 1, 'name': cls.aliases_timeframes[tf.name], 'code': tf.name}
            cls.timeframes.append(option)

    @classmethod
    def update(cls) -> None:
        """Parse finam data and save results in class attributes"""
        if not all((cls.exporter, cls.markets, cls.tickers, cls.timeframes)):
            cls.get_exporter()
            cls._parse_markets()
            cls._parse_tickers()
            cls._parse_timeframes()

    @classmethod
    def find_alias_ticker(cls, market, ticker) -> str:
        """Find in class ticker for specified market and return full name of it"""
        try:
            market_tickers = cls.tickers[market]
            ticker_alias = [t['name'] for t in market_tickers if t['code'] == ticker][0]
        except KeyError:
            cls.update()
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
            'DAILY': 24 * 60,
        }
        return minutes_in_timeframe[tf]

    @staticmethod
    def setup_driver() -> None:
        """Setup chrome driver with webdriver service"""
        chromeService = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.headless = False
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--disable-translate')
        options.add_argument('--lang=en-US')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=chromeService, options=options)
        return driver

    @classmethod
    def fetcher(cls, url, lines=False):
        if cls.driver:
            return cls.driver
        driver = SessionOptions.setup_driver()
        print ('>>>', url)
        driver.get(url)
        res = WebDriverWait(driver, 15).until( lambda driver: driver.find_element(By.XPATH, "//*").get_attribute('outerHTML'))
        if lines:
            res = res.encode('cp1252').decode('cp1251')
            res = res.split('\n')
            return res
        return res
    
    @staticmethod
    def fetcher_download(url, lines = False):
        print ('>>>', url)
        r = requests.get(url, headers = {'User-Agent':'Mozilla 8'}, stream=True)
        if lines:
            return r.content.decode('utf8').split('\n\r')
        else :
            return r.content.decode('utf8')

    @classmethod
    def get_exporter(cls) -> Exporter:
        """Return finam exporter for data parsing"""
        if cls.exporter:
            return cls.exporter
        cls.exporter = Exporter(fetcher = cls.fetcher)
        cls.exporter._fetcher = cls.fetcher_download
        return cls.exporter
