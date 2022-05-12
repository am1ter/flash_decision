from app import db
import app.config as cfg

from sqlalchemy.exc import SQLAlchemyError 
from sqlalchemy.sql import text
import pandas as pd
from pandas.tseries.offsets import BDay
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from math import ceil
import json
from plotly.utils import PlotlyJSONEncoder
from plotly import graph_objs
from statistics import median
import logging
from collections import OrderedDict
from itertools import islice
import random
import jwt
from flask import Request

from finam.export import LookupComparator     # https://github.com/ffeast/finam-export
from finam.const import Market, Timeframe               # https://github.com/ffeast/finam-export


# Set up logger
# =============
logger = logging.getLogger('Models')


# Database related classes (ORM)
# ==============================

class User(db.Model):
    """
    ORM object `User` is used to identify individuals who use application.
    Sign up is available for everyone, but not required (there is a demo user).
    All users have the same privileges.
    """

    __tablename__ = 'User'

    UserId = db.Column(db.Integer, primary_key=True, index=True)
    UserName = db.Column(db.String, index=True)
    UserEmail = db.Column(db.String, index=True, unique=True)
    UserPassword = db.Column(db.String(128))

    sessions = db.relationship('Session', backref='User', lazy='dynamic', passive_deletes=True)
    authentications = db.relationship('Authentication', backref='User', lazy='dynamic', passive_deletes=True)

    def __repr__(self) -> str:
        """Return the user email"""
        return f'<User {self.UserEmail}>'

    @classmethod
    def create(cls, creds: dict) -> db.Model:
        """Create new user instance with hashed password and save it to db"""
        user = cls()
        user.set_email(creds['email'].lower())
        user.set_name(creds['name'])
        user.set_password(creds['password'])
        return user

    @classmethod
    def get_user_by_id(cls, id: int) -> db.Model:
        """Return object by id"""
        return cls.query.get(int(id))

    @classmethod
    def get_user_by_email(cls, email: str) -> db.Model:
        """Return object by email"""
        return cls.query.filter(User.UserEmail == email.lower()).first()

    def delete_user(self) -> None:
        """Delete user and all related to it object from db"""
        delete_object_from_db(self)

    def set_email(self, email: str) -> None:
        """Set new email for the user"""
        self.UserEmail = email
        # Write to db
        write_object_to_db(self)

    def set_name(self, name: str) -> None:
        """Set new email for the user"""
        self.UserName = name
        # Write to db
        write_object_to_db(self)
    
    def set_password(self, password: str) -> None:
        """Set new password for the user"""
        self.UserPassword = generate_password_hash(password)
        # Write to db
        write_object_to_db(self)

    def check_password(self, password: str) -> bool:
        """Check the password against stored hashed password"""
        return check_password_hash(self.UserPassword, password)

    @classmethod
    def check_is_email_free(cls, email: str) -> bool:
        """Check if email is free"""
        if cls.get_user_by_email(email):
            return False
        else:
            return True

    def encode_jwt_token(self) -> str:
        """Create JSON Web Token for current user"""
    
        token = jwt.encode(
            payload={'sub': self.UserEmail, 
                     'iat': datetime.utcnow(), 
                     'exp': datetime.utcnow() + timedelta(minutes=cfg.USER_AUTH_TIMEOUT)},
            key=cfg.FlaskConfig.SECRET_KEY)
        
        return token

    @classmethod
    def get_user_by_jwt(cls, request: Request) -> db.Model:
        """Decode JSON Web Token from request`s header and find User object"""

        auth_headers = request.headers.get('Authorization', '').split()

        # Check if header looks like correct header with auth info
        assert len(auth_headers) == 2, 'Wrong request header'

        # Try to decode jwt token and verify user information
        token = auth_headers[1]
        jwt_dict = jwt.decode(token, cfg.FlaskConfig.SECRET_KEY, algorithms="HS256")
        current_user = cls.get_user_by_email(email=jwt_dict['sub'])
        assert current_user, f'User {jwt_dict["sub"]} not found'

        return current_user


class Authentication(db.Model):
    """
    ORM object `Authentication` is record in db with auth info.
    It describe auth attempts (including unsuccessful ones) and new sign ups.
    """

    __tablename__ = 'Authentication'

    AuthId = db.Column(db.Integer, primary_key=True, index=True)
    UserId = db.Column(db.Integer, db.ForeignKey('User.UserId', ondelete='CASCADE'), index=True)
    AuthDatetime = db.Column(db.DateTime, default=datetime.utcnow)
    IpAddress = db.Column(db.String)
    UserAgent = db.Column(db.String)
    StatusCode = db.Column(db.String)

    def __repr__(self) -> str:
        """Return description"""
        return f'<Authentication #{self.AuthId} for {self.UserId} at {self.AuthDatetime}>'

    @classmethod
    def create(cls, user: db.Model, details: dict) -> db.Model:
        """Create new record in db with authentication details"""
        
        auth = cls()
        auth.UserId = user.UserId if user else None
        auth.IpAddress = details['ip_address']
        auth.UserAgent = details['user_agent']

        assert details['status_code'] in (200, 201, 204, 401, 404, 500), 'Wrong status code'
        auth.StatusCode = details['status_code']
        
        # Write record to db
        write_object_to_db(auth)
        
        return auth


class Session(db.Model):
    """
    ORM object `Session` is core object of the application. 
    All users` app interactions use session`s data. Create new session is main function of the app.
    Class attributes is options which determine most application functions behavior.
    Sessions has different modes - each of them is subclass.
    """

    __tablename__ = 'Session'

    SessionId = db.Column(db.Integer, primary_key=True, index=True)
    CreateDatetime = db.Column(db.DateTime, default=datetime.utcnow)
    Status = db.Column(db.String)
    UserId = db.Column(db.Integer, db.ForeignKey('User.UserId', ondelete='CASCADE'), index=True)
    Market = db.Column(db.String)
    Ticker = db.Column(db.String)
    Timeframe = db.Column(db.String)
    Barsnumber = db.Column(db.Integer)
    Timelimit = db.Column(db.Integer)
    LastFixingBarDatetime = db.Column(db.DateTime)
    Iterations = db.Column(db.Integer)
    Slippage = db.Column(db.Float)
    Fixingbar = db.Column(db.Integer)
    TradingType = db.Column(db.String)
    FirstBarDatetime = db.Column(db.DateTime)
    TotalSessionBars = db.Column(db.Integer)
    Mode = db.Column(db.String)

    iterations = db.relationship('Iteration', backref='Session', lazy='dynamic', order_by='Iteration.IterationId', passive_deletes=True)
    decisions = db.relationship('Decision', backref='Session', lazy='selectin', passive_deletes=True)
    
    __mapper_args__ = {
        'polymorphic_on': Mode,
    }

    # Random security generation attributes
    _random_security = {
        'USA': ('AMZN', 'NVDA', 'FB', 'MSFT', 'AAPL', 'DIS', 'XOM', 'GS', 'BA', 'NKE'),
        'SHARES': ('SBER', 'AFLT', 'GAZP', 'ROSN', 'YNDX', 'MOEX', 'MGNT', 'GMKN'),
        'CRYPTO_CURRENCIES': ('ETHUSD', 'BTCUSD', 'LTCUSD')
        }

    def __repr__(self) -> str:
        """Return object description"""
        return f'<Session #{self.SessionId} (mode: {self.Mode})>'

    def _determine_trading_type(self) -> str:
        """Determine how long trader will keep the security: <day, <week or >week"""

        tf_in_mins = cfg.SessionOptions.convert_tf_to_min(self.Timeframe)
        days_in_week = cfg.DAYS_IN_WEEK
        days_in_month = cfg.DAYS_IN_MONTH
        iteration_period_bars = self.Barsnumber + self.Fixingbar
        iteration_period_mins = iteration_period_bars * tf_in_mins

        if iteration_period_mins < cfg.TRADINGDAY_DURATION_MINS:
            trading_type = 'daytrading'
        elif iteration_period_mins < cfg.TRADINGDAY_DURATION_MINS * days_in_week:
            trading_type = 'swingtrading'
        elif iteration_period_mins < cfg.TRADINGDAY_DURATION_MINS * days_in_month:
            trading_type = 'shortinvesting'
        else:
            trading_type = 'longinvesting'

        return trading_type

    def _calc_first_bar_datetime(self) -> datetime:
        """Calculate datetime of the first bar in downloaded quotes dataset"""

        days_before = {
            'daytrading': ceil(self.Iterations / 5) * 7, # One iteration per day (round up)
            'swingtrading': self.Iterations * 7, # One iteration per week
            'shortinvesting': self.Iterations * 31, # One iteration per month
            'longinvesting': self.Iterations * 31 * 3 # One iteration per 3 months
        }
    
        safety_factor = cfg.DOWNLOAD_SAFETY_FACTOR

        return self.LastFixingBarDatetime - timedelta(days=days_before[self.TradingType] * safety_factor)

    def _generate_filename_session(self) -> str:
        """ Get filename for current session """

        # Generate dirname
        if cfg.PLATFORM == 'win32':
            dir_path = cfg.PATH_DOWNLOADS + '\\' + str(self.SessionId) + '_' + str(self.Ticker) + '\\'
        else:
            dir_path = cfg.PATH_DOWNLOADS + '/' + str(self.SessionId) + '_' + str(self.Ticker) + '/'

        # Create dirs if not exist
        for dir in (cfg.PATH_DOWNLOADS, dir_path):
            if not os.path.exists(dir):
                os.mkdir(dir)

        # Generate filename
        if cfg.SAVE_FORMAT == 'csv':
            filename = 'session_' + str(self.SessionId) + '.csv'
        elif cfg.SAVE_FORMAT == 'json':
            filename = 'session_' + str(self.SessionId) + '.json'

        # Return full path
        return dir_path + filename

    def _download_quotes(self) -> pd.DataFrame:
        """Download qoutes data using finam.export lib and save it to HDD"""

        # Set path to save/load downloaded quotes data
        save_path = self._generate_filename_session()

        # Check: Pass if file for this session hasn't downloaded yet or it's size is smaller than 48 bytes
        assert not os.path.exists(save_path) or os.stat(save_path).st_size <= 48, 'Error: Quotes already downloaded'   

        # Parse quotes with finam.export lib
        exporter = cfg.SessionOptions.get_exporter()
        security = exporter.lookup(code=self.Ticker, market=Market[self.Market],
                            code_comparator=LookupComparator.EQUALS)

        # If there are more than 1 security with the following ticker, use the first one
        if len(security) == 0:
            raise RuntimeError('Unable to find correct security for this ticker')
        elif len(security) >= 1:
            security = security.iloc[0]

        # Download quotes
        try:
            df_quotes = exporter.download(id_=security.name, market=Market[self.Market],
                                    start_date=self.FirstBarDatetime, end_date=self.LastFixingBarDatetime,
                                    timeframe=Timeframe[self.Timeframe])
            df_quotes.index = pd.to_datetime(df_quotes['<DATE>'].astype(str) + ' ' + df_quotes['<TIME>'])
        except:
            raise RuntimeError('Unable to download quotes')
        
        # Check if downloaded quotes is correct
        assert len(df_quotes) > 0, 'There are no quotes for this security for the selected period'

        # Save full df to file
        if cfg.SAVE_FORMAT == 'csv':
            df_quotes.to_csv(save_path, index=True, index_label='index')
        elif cfg.SAVE_FORMAT == 'json':
            df_quotes.to_json(save_path, index=True, orient='records')
        else:
            raise RuntimeError('Error: Unsupported export file format')

        # Return DF to create iterations
        return df_quotes

    def _update_session_with_df_data(self, df_quotes: pd.DataFrame) -> None:
        """Update current session options in the db"""
        # Write count of bars in the downloaded df
        self.TotalSessionBars = len(df_quotes)
        # Write LastFixingBarDatetime with a precise time with last bar of downloaded df
        self.LastFixingBarDatetime = df_quotes.iloc[-1].name
        # Write FirstBarDatetime with a precise time with first bar of downloaded df
        self.FirstBarDatetime = df_quotes.iloc[1].name
        # Write to db
        write_object_to_db(self)

    def _create_iterations(self, df_quotes: pd.DataFrame) -> None:
        """Create all iterations for current session (self)"""
        for i in range(1, self.Iterations + 1):
            Iteration.create(session=self, iteration_num=i, df_quotes=df_quotes)

    @staticmethod
    def _get_last_workday():
        """Get last workday before today for preset sessions"""
        return (datetime.today() - BDay(1)).strftime('%Y-%m-%d')

    @staticmethod
    def _get_random_workday():
        """Get one of the random business days from the last 500 business days"""
        random_bday = random.randint(0, cfg.RANDOM_WORKDAY_LIMIT)
        return (datetime.today() - BDay(random_bday)).strftime('%Y-%m-%d')

    @classmethod
    def _select_random_security(cls, market: str) -> str:
        """Select one random security from short list for current mode"""
        return random.choice(cls._random_security[market])

    @classmethod
    def create(cls, options: dict) -> db.Model:
        """Create new session and write it to db"""

        session = cls()

        # Set session's status to active
        session.Status = cfg.SESSION_STATUS_CREATED
        # Get options data from webpage
        session.UserId = int(options['userId'])
        session.Market = options['market']
        session.Ticker = options['ticker']
        session.Timeframe = options['timeframe']
        session.Barsnumber = int(options['barsnumber'])
        session.Timelimit = int(options['timelimit'])
        session.LastFixingBarDatetime = datetime.strptime(options['date'], '%Y-%m-%d')
        session.Iterations = int(options['iterations'])
        session.Slippage = float(options['slippage'])
        session.Fixingbar = int(options['fixingbar'])
        session.TradingType = session._determine_trading_type()
        session.FirstBarDatetime = session._calc_first_bar_datetime()
        # Set session's mode
        session.Mode = cls.mode

        # Write form data to db
        write_object_to_db(session)

        # Download quotes and update current session options in db
        df_quotes = session._download_quotes()

        # Update current session options in db
        session._update_session_with_df_data(df_quotes)

        # Create all iterations
        session._create_iterations(df_quotes)

        return session

    def convert_to_dict(self) -> dict:
        """Convet SQLAlchemy object to dict"""
        as_dict = {i.name: str(getattr(self, i.name)) for i in self.__table__.columns}
        return as_dict

    def convert_to_dict_format(self) -> dict:
        """Convet SQLAlchemy object to dict with beautiful strings as values"""
        as_dict = {
            'UserId': self.UserId,
            'Market': cfg.SessionOptions.aliases_markets[self.Market],
            'Ticker': cfg.SessionOptions.find_alias_ticker(self.Market, self.Ticker),
            'Timeframe': cfg.SessionOptions.aliases_timeframes[self.Timeframe],
            'Barsnumber': str(self.Barsnumber) + ' bars',
            'Timelimit': str(self.Timelimit) + ' sec',
            'Date': self.LastFixingBarDatetime.strftime('%Y-%m-%d'),
            'Iterations': str(self.Iterations),
            'Slippage': str(float(self.Slippage) * 100) + '%',
            'Fixingbar': str(self.Fixingbar),
            'Mode': self.Mode
        }
        return as_dict

    def load_csv(self) -> pd.DataFrame:
        """Get dataframe by reading data from hdd file"""

        # Set path to save/load downloaded ticker data
        save_path = self._generate_filename_session()
        
        # Load dataframe from hdd
        try:
            return pd.read_csv(save_path, parse_dates=True, index_col='index')
        except FileNotFoundError:
            raise FileNotFoundError('File not found: ' + save_path)

    def remove_csv(self) -> None:
        """Delete downloaded file with quotes"""
        if self.SessionId and self.Ticker:
            save_path = self._generate_filename_session()
            os.remove(save_path)
        else:
            raise FileNotFoundError('No information about id and ticker of the current session')

    @classmethod
    def get_from_db(cls, session_id: int) -> db.Model:
        """Get session's options from db and fill with them the object"""
        return cls.query.get(int(session_id))

    def set_status(self, status: str) -> None:
        """Record new session's status in db"""
        self.Status = status
        write_object_to_db(self)


class SessionCustom(Session):
    """
    Subclass for session with manually selected options (custom). 
    User is able to set up all session options by himself.
    """

    mode = 'custom'
    __mapper_args__ = {
        'polymorphic_identity': mode
    }

    @classmethod
    def create(cls, request: dict) -> db.Model:
        """Call super method with mode == custom"""
        session = super().create(options=request)
        return session


class SessionClassic(Session):
    """
    Subclass for preset session (classic)
    Balanced mode with common USA shares. Used as application default.
    """

    mode = 'classic'
    __mapper_args__ = {
        'polymorphic_identity': mode
    }

    @classmethod
    def create(cls, request: dict) -> db.Model:
        """Setup attributes for classic session"""
        # Collect all options for new session generation
        options = {
            'userId': request['userId'],
            'mode': cls.mode,
            'market': 'USA',
            'ticker': cls._select_random_security('USA'),
            'timeframe': 'HOURLY',
            'barsnumber': '100',
            'timelimit': '60',
            'date': cls._get_last_workday(),
            'iterations': '5',
            'slippage': '0.005',
            'fixingbar': '50'
            }
        session = super().create(options=options)
        return session


class SessionBlitz(Session):
    """
    Subclass for preset session (blitz)
    High speed mode - time for decision making is very limited.
    """
    
    mode = 'blitz'
    __mapper_args__ = {
        'polymorphic_identity': mode
    }

    @classmethod
    def create(cls, request: dict) -> db.Model:
        """Setup attributes for blitz session"""
        # Collect all options for new session generation
        options = {
            'userId': request['userId'],
            'mode': cls.mode,
            'market': 'SHARES',
            'ticker': cls._select_random_security('SHARES'),
            'timeframe': 'MINUTES5',
            'barsnumber': '30',
            'timelimit': '5',
            'date': cls._get_random_workday(),
            'iterations': '10',
            'slippage': '0.001',
            'fixingbar': '15'
            }
        session = super().create(options=options)
        return session


class SessionCrypto(Session):
    """
    Subclass for preset session (cryptocurrencies)
    Cryptocurrencies is high volatility securities, so results are less predictable.
    """

    mode = 'crypto'
    __mapper_args__ = {
        'polymorphic_identity': mode
    }

    @classmethod
    def create(cls, request: dict) -> db.Model:
        """Setup attributes for crypto session"""
        # Collect all options for new session generation
        options = {
            'userId': request['userId'],
            'mode': cls.mode,
            'market': 'CRYPTO_CURRENCIES',
            'ticker': cls._select_random_security('CRYPTO_CURRENCIES'),
            'timeframe': 'MINUTES15',
            'barsnumber': '50',
            'timelimit': '30',
            'date': cls._get_random_workday(),
            'iterations': '10',
            'slippage': '0.001',
            'fixingbar': '50'
            }
        session = super().create(options=options)
        return session


class Iteration(db.Model):
    """
    Every session is divided into several parts - iterations (ORM object).
    For every iteration user make a decision - to buy, to sell or do nothing.
    """

    __tablename__ = 'Iteration'

    IterationId = db.Column(db.Integer, primary_key=True, index=True)
    CreateDatetime = db.Column(db.DateTime, default=datetime.utcnow)
    SessionId = db.Column(db.Integer, db.ForeignKey('Session.SessionId', ondelete='CASCADE'), index=True)
    IterationNum = db.Column(db.Integer)
    StartBarNum = db.Column(db.Integer)
    FinalBarNum = db.Column(db.Integer)
    FixingBarNum = db.Column(db.Integer)
    FixingBarDatetime = db.Column(db.DateTime)
    StartBarPrice = db.Column(db.Float)
    FinalBarPrice = db.Column(db.Float)
    FixingBarPrice = db.Column(db.Float)

    decisions = db.relationship('Decision', backref='Iteration', lazy='dynamic', passive_deletes=True)

    def __repr__(self) -> str:
        """Return object description"""
        return f'<Iteration #{self.IterationNum} of {self.Session}>'

    @classmethod
    def create(cls, session: Session, iteration_num: int, df_quotes: pd.DataFrame) -> db.Model:
        """Create new iteration and write it to db"""
        
        # Check how much iterations is already created for this session
        assert len(session.iterations.all()) <= session.Iterations, 'Error: All iterations for this sessions was already created'

        # Fill basic options
        iter = cls()
        iter.SessionId = session.SessionId
        iter.IterationNum = iteration_num

        # Start iterations generation from the end of df
        if iteration_num == 1:
            # For first iteration use session options
            iter.FixingBarDatetime = session.LastFixingBarDatetime
            iter.FixingBarNum = session.TotalSessionBars - 1   # first bar num = 0
        else:
            # For other iterations find last created iteration for current session and use it to calc new values
            last_iteration = session.iterations.filter(cls.Session == session).all()[-1:][0]
            # Calc new iteration fixing date and bar number considering if there is a skipped iterations 
            iterations_distance = iter.IterationNum - last_iteration.IterationNum
            iter.FixingBarDatetime = last_iteration._calc_new_iteration_fixbardatetime(iterations_distance)
            iter.FixingBarNum = int(df_quotes.index.get_indexer([iter.FixingBarDatetime], method='nearest')[0])
        
            # Skip dates with no data for chart
            if iter.FixingBarNum - last_iteration.FixingBarNum > session.Fixingbar * -1:
                logger.warning(f'Skip iteration generation for <Iteration #{iteration_num} of {session}> because of no data for {iter.FixingBarDatetime}')
                return None

        # Fill other required bars numbers
        iter.FinalBarNum = iter.FixingBarNum - session.Fixingbar
        if session.Barsnumber <= iter.FinalBarNum:
            iter.StartBarNum = iter.FinalBarNum - session.Barsnumber
        else:
            # Stop iteration generation if not enough data in df
            logger.warning(f'Skip iteration generation for <Iteration #{iteration_num} of {session}> because not enough data in dataframe')
            return None

        # Write data to db
        write_object_to_db(iter)

        # Save iteration quotes df to file
        df_quotes_cut = df_quotes.iloc[iter.StartBarNum + 1:iter.FixingBarNum + 1]
        save_path = iter._generate_filename_iteration()
        if cfg.SAVE_FORMAT == 'csv':
            df_quotes_cut.to_csv(save_path, index=True, index_label='index')
        elif cfg.SAVE_FORMAT == 'json':
            df_quotes_cut.to_json(save_path, index=True, orient='records')
        else:
            raise RuntimeError('Error: Unsupported export file format')

        # Save iterations' prices
        iter.StartBarPrice = df_quotes_cut.iloc[:1]['<CLOSE>'].values[0]
        iter.FinalBarPrice = df_quotes_cut.iloc[session.Barsnumber-1:session.Barsnumber]['<CLOSE>'].values[0]
        iter.FixingBarPrice = df_quotes_cut.iloc[-1:]['<CLOSE>'].values[0]
        
        # Update db object
        write_object_to_db(iter)

        return iter

    def _calc_new_iteration_fixbardatetime(self, distance: int) -> datetime:
        """Calculate datetime of the previous bar in downloaded quotes dataset"""
        trading_type = self.Session.TradingType
        if trading_type == 'daytrading':
            # One iteration per day
            days_before = 1
        elif trading_type == 'swingtrading':
            # One iteration per week
            days_before = cfg.DAYS_IN_WEEK
        elif trading_type == 'shortinvesting':
            # One iteration per month
            days_before = cfg.DAYS_IN_MONTH
        else:
            # One iteration per 3 months
            days_before = cfg.DAYS_IN_MONTH * 3
        
        # Add to days number amount of skipped iterations (distance between iterations) 
        days_before = days_before + (distance - 1)

        # Skip weekends
        bar_date = self.FixingBarDatetime - BDay(days_before)

        return bar_date

    def get_from_db(session_id: int, iteration_num: int) -> db.Model:
        """Get iterations's options from db and fill with them the object"""
        return Iteration.query.filter(Iteration.SessionId == session_id, Iteration.IterationNum == iteration_num).first()

    def _generate_filename_iteration(self) -> str:
        """ Get filename for current iteration """

        # Generate dirname
        if cfg.PLATFORM == 'win32':
            dir_path = cfg.PATH_DOWNLOADS + '\\' + str(self.SessionId) + '_' + str(self.Session.Ticker) + '\\'
        else:
            dir_path = cfg.PATH_DOWNLOADS + '/' + str(self.SessionId) + '_' + str(self.Session.Ticker) + '/'

        # Create dirs if not exist
        for dir in (cfg.PATH_DOWNLOADS, dir_path):
            if not os.path.exists(dir):
                os.mkdir(dir)
        
        # Generate filename
        if cfg.SAVE_FORMAT == 'csv':
            filename = 'iteration_' + str(self.SessionId) + '_' + str(self.IterationNum) + '.csv'
        elif cfg.SAVE_FORMAT == 'json':
            filename = 'iteration_' + str(self.SessionId) + '_' + str(self.IterationNum) + '.json'

        # Return full path
        return dir_path + filename

    def _read_data_file(self) -> pd.DataFrame:
        """Get dataframe by reading data from hdd file"""
        # Set path to save/load downloaded ticker data
        save_path = self._generate_filename_iteration()
        # Load dataframe from hdd
        try:
            if cfg.SAVE_FORMAT == 'csv':
                return pd.read_csv(save_path, parse_dates=True, index_col='index')
            elif cfg.SAVE_FORMAT == 'json':
                return pd.read_json(save_path, orient='records')
        except FileNotFoundError:
            raise FileNotFoundError('File not found: ' + save_path)

    def _convert_to_dict(self) -> dict:
        """Convet SQLAlchemy object to dict"""
        as_dict = {i.name: str(getattr(self, i.name)) for i in self.__table__.columns}
        return as_dict

    def prepare_chart_plotly(self) -> json:
        """Prepare JSON with chart data to export into HTML-file"""

        # Read iteration df
        df = self._read_data_file()
        # Show bars only between Start and Final (hide bars between Final and Fixing)
        df = df.iloc[:self.Session.Barsnumber]
        # Add numerical id instead date
        df['id'] = df.reset_index().index

        # Convert it to plotly formatted json
        chart_data = graph_objs.Figure(
                        data=[
                            graph_objs.Candlestick(
                                x=df.id + 1,
                                open=df['<OPEN>'],
                                close=df['<CLOSE>'],
                                low=df['<LOW>'],
                                high=df['<HIGH>'],

                                increasing_line_color='#3c996e',
                                decreasing_line_color='#e15361'
                            )
                        ]
        )

        # Export chart and iteration in one JSON
        chart_JSON = json.dumps(chart_data, cls=PlotlyJSONEncoder)
        return chart_JSON


class Decision(db.Model):
    """
    For every session user make several decisions (ORM objects).
    There are 3 types of decisions - to buy, to sell or do nothing.
    For every decision app calculates financial result - 
    how much user would earn if open position right now and close it after a while.
    """

    __tablename__ = 'Decision'

    DecisionId = db.Column(db.Integer, primary_key=True, index=True)
    CreateDatetime = db.Column(db.DateTime, default=datetime.utcnow)
    UserId = db.Column(db.Integer, db.ForeignKey('User.UserId', ondelete='CASCADE'), index=True)
    SessionId = db.Column(db.Integer, db.ForeignKey('Session.SessionId', ondelete='CASCADE'), index=True)
    IterationId = db.Column(db.Integer, db.ForeignKey('Iteration.IterationId', ondelete='CASCADE'), index=True)
    Action = db.Column(db.String)
    TimeSpent = db.Column(db.Float)
    ResultRaw = db.Column(db.Float)
    ResultFinal = db.Column(db.Float)

    def __repr__(self) -> str:
        """Return object description"""
        return f'<Decision #{self.DecisionId} for {self.Iteration}>'

    def create(self, iteration: Iteration, props: dict) -> db.Model:
        """Create new self and write it to db"""

        self.UserId = iteration.Session.UserId
        self.SessionId = iteration.SessionId
        self.IterationId = iteration.IterationId
        self.Action = props['action']
        self.TimeSpent = props['timeSpent']
        
        # Calc results taking into account the slippage level
        price_change = round((iteration.FixingBarPrice - iteration.FinalBarPrice) / iteration.StartBarPrice, 6)
        if self.Action == 'Buy':
            self.ResultRaw = price_change * 1
            self.ResultFinal = round(self.ResultRaw - iteration.Session.Slippage, 6)
        elif self.Action == 'Skip':
            self.ResultRaw = 0
            self.ResultFinal = 0
        elif self.Action == 'Sell':
            self.ResultRaw = price_change * -1
            self.ResultFinal = round(self.ResultRaw - iteration.Session.Slippage, 6)
        else:
            raise RuntimeError('Unsupported action')

        # Write data to db
        write_object_to_db(self)

        return self


# Non-ORM classes
# ===============

class SessionResults:
    """
    `SessionResults` is not an ORM object - no tables in db for storing session results.
    This class contains methods related to rendering session result pages.
    Methods from this class could be situated in class Session and moved here only for codebase simplification.
    """

    def __repr__(self) -> str:
        """Return object description"""
        return f'<SessionResults for {self.session}>'

    def __new__(self, session: Session) -> dict:
        """Collect all session attributes in one object"""

        self.session = session
        decisions = session.decisions

        total_result = round(sum([d.ResultFinal for d in decisions]) * 100, 4)
        total_decisions = len(decisions)
        profitable_decisions = len([d for d in decisions if d.ResultFinal>0])
        unprofitable_decisions = len([d for d in decisions if d.ResultFinal<=0 and d.Action!='Skip'])
        skipped_decisions = len([d for d in decisions if d.Action=='Skip'])
        median_decisions_result = round(median([d.ResultFinal for d in decisions]), 4)
        best_decisions_result = round(max([d.ResultFinal for d in decisions]) * 100, 4)
        worst_decisions_result = round(min([d.ResultFinal for d in decisions]) * 100, 4)
        total_time_spent = sum([d.TimeSpent for d in decisions])
        total_time_spent = str(timedelta(seconds=total_time_spent))

        session_summary = {
            'userId': session.UserId,
            'sessionId': session.SessionId,
            'mode': session.Mode,
            'totalResult': total_result,
            'totalDecisions': total_decisions,
            'profitableDecisions': profitable_decisions,
            'unprofitableDecisions': unprofitable_decisions,
            'skippedDecisions': skipped_decisions,
            'medianDecisionsResult': median_decisions_result,
            'bestDecisionsResult': best_decisions_result,
            'worstDecisionsResult': worst_decisions_result,
            'totalTimeSpent': total_time_spent
            }

        return session_summary


class Scoreboard:
    """
    `Scoreboard` is not an ORM object - no tables in db for scoreboards.
    This class contains methods related to scoreboard rendering.
    Methods from this class could be in class User and moved here only for codebase simplification.
    """

    def __repr__(self) -> str:
        """Return object description"""
        return f'<Scoreboard for {self.user} (mode: {self.mode})>'

    def __init__(self, mode: str, user: User) -> None:
        """Create new instance"""
        self.mode = mode
        self.user = user
        self.closed_sessions = []
        self.sessions_results = []

    def _get_all_users_results(self) -> dict:
        """Return list of all users results"""

        # Check current Scoreboard instance for cached objects
        if not any((self.closed_sessions, self.sessions_results)):
            self.closed_sessions = Session.query.filter(Session.Mode == self.mode, Session.Status == cfg.SESSION_STATUS_CLOSED).all()
            self.sessions_results = [SessionResults(s) for s in self.closed_sessions]
        
        # Sum results of all sessions for every user
        users_results = {}
        for r in self.sessions_results:
            if r['userId'] not in users_results:
                users_results[r['userId']] = r['totalResult'] 
            else:
                users_results[r['userId']] += r['totalResult'] 

        # Order users by result
        users_results = OrderedDict(sorted(users_results.items(), key=lambda r: r[1], reverse=True))
        return users_results

    def get_top_users(self, count: int) -> dict:
        """Return list of specified top users (leaders) for selected mode"""

        users_results = self._get_all_users_results()
        
        # Cut dict to users count, round results and replace ids with names
        users_results = OrderedDict(islice(users_results.items(), count))
        users_results_final = {}
        for idx, user in enumerate(users_results):
            users_results_final[idx] = {'name': User.get_user_by_id(user).UserName, 
                                        'result': round(users_results[user], 2)}

        return users_results_final  

    def get_user_rank(self) -> int:
        """Return rank of user in global scoreboard"""

        users_results = self._get_all_users_results()
        rank = list(users_results).index(self.user.UserId)

        return rank

    def calc_user_summary(self) -> dict:
        """Calculate user`s activity summary"""

        user = self.user

        # Check current Scoreboard instance for cached objects
        if not any((self.closed_sessions, self.sessions_results)):
            self.closed_sessions = user.sessions.filter(Session.Status == cfg.SESSION_STATUS_CLOSED, Session.Mode == self.mode).all()
            self.sessions_results = [SessionResults(s) for s in self.closed_sessions]

        # Check if there is results for current user
        if not any((self.closed_sessions, self.sessions_results)):
            return False

        total_sessions = len(self.closed_sessions)
        profitalbe_sessions = len([s['totalResult'] for s in self.sessions_results if s['totalResult'] > 0])
        unprofitalbe_sessions = len([s['totalResult'] for s in self.sessions_results if s['totalResult'] <= 0])
        total_result = round(sum([s['totalResult'] for s in self.sessions_results]), 2)
        median_result = round(median([s['totalResult'] for s in self.sessions_results]), 2)
        best_result = round(max([s['totalResult'] for s in self.sessions_results]), 2)
        first_session = min([s.CreateDatetime for s in self.closed_sessions]).strftime("%d.%m.%Y")

        user_summary = {
            'mode': self.mode,
            'userId': user.UserId,
            'userName': user.UserName,
            'totalSessions': total_sessions,
            'profitableSessions': profitalbe_sessions,
            'unprofitableSessions': unprofitalbe_sessions,
            'totalResult': total_result,
            'medianResult': median_result,
            'bestSessionResult': best_result,
            'firstSession': first_session
        }

        return user_summary


# General functions
# ==================

def check_db_connection() -> None:
    """Check if connection to db can be established"""
    try:
        db.engine.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


def write_object_to_db(object: db.Model) -> None:
    """Default way to write SQLAlchemy object to db"""
    db.session.add(object)
    db.session.commit()
        

def delete_object_from_db(object: db.Model) -> None:
    """Default way to write SQLAlchemy object to db"""
    db.session.delete(object)
    db.session.commit()


def create_system_users() -> None:
    """Create system users during first run of the script"""
    
    # Check if there is tables in db
    meta = db.MetaData(bind=db.engine)
    meta.reflect()
    if not meta.tables:
        logger.warning('Database is empty')
        return

    # Create demo user
    if User.get_user_by_email(cfg.USER_DEMO_EMAIL) is None:
        creds = {'email': cfg.USER_DEMO_EMAIL, 'name': cfg.USER_DEMO_NAME, 'password': cfg.USER_DEMO_PASSWORD}
        demo_user = User.create(creds=creds)
        logger.info(f'Demo user "{demo_user}" created')
        
    # Create test user
    if User.get_user_by_email(cfg.USER_TEST_EMAIL) is None:
        creds = {'email': cfg.USER_TEST_EMAIL, 'name': cfg.USER_TEST_NAME, 'password': cfg.USER_TEST_PASSWORD}
        test_user = User.create(creds=creds)
        logger.info(f'Test user "{test_user}" created')
