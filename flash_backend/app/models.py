from xmlrpc.client import Boolean
from app import db
import app.config as cfg

from flask_sqlalchemy import BaseQuery
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError 
import pandas as pd
from pandas.core.frame import DataFrame
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from math import ceil
import json
from plotly.utils import PlotlyJSONEncoder
from plotly import graph_objs
from statistics import median
from functools import wraps
import logging
from collections import OrderedDict
from itertools import islice

from finam.export import Exporter, LookupComparator     # https://github.com/ffeast/finam-export
from finam.const import Market, Timeframe               # https://github.com/ffeast/finam-export


# Set up logger
# ==================
logger = logging.getLogger('Models')


# Decorators
# ==================

def catch_db_exception(f):
    @wraps(f)
    def _catch_exception(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except SQLAlchemyError as e:
            raise SQLAlchemyError('Error: No connection to DB')
    return _catch_exception


# DB related classes
# ==================

class User(db.Model):
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

    def new(self, creds: dict) -> None:
        """Create new user instance with hashed password and save it to DB"""
        self.set_email(creds['email'])
        self.UserName = creds['name']
        self.set_password(creds['password'])
        # Write to db
        write_object_to_db(self)

    @catch_db_exception
    def get_user_by_id(id: int) -> BaseQuery:
        """Return object by id"""
        return User.query.get(int(id))

    @catch_db_exception
    def get_user_by_email(email: str) -> BaseQuery:
        """Return object by email"""
        return User.query.filter(User.UserEmail == email).first()

    @catch_db_exception
    def delete_user_by_email(email: str) -> BaseQuery:
        """Return object by email"""
        # Get user from db
        user = User.get_user_by_email(email)
        if user:
            # Delete it from db
            delete_object_from_db(user)
            return True
        else:
            return False

    def set_email(self, email: str) -> None:
        """Set new email for the user"""
        self.UserEmail = email
    
    def set_password(self, password: str) -> None:
        """Set new password for the user"""
        self.UserPassword = generate_password_hash(password)

    def check_password(self, password: str) -> None:
        """Check the password against stored hashed password """
        return check_password_hash(self.UserPassword, password)

    def check_is_email_free(email: str) -> Boolean:
        """Check if email is free"""
        if User.get_user_by_email(email):
            return False
        else:
            return True

    def calc_user_summary(self, mode: str) -> dict:
        """Calculate user's summary along his activity"""

        closed_sessions = self.sessions.filter(Session.Status == 'closed', Session.Mode == mode).all()
        sessions_results = [s.calc_sessions_summary() for s in closed_sessions]

        total_sessions = len(closed_sessions)
        profitalbe_sessions = len([s['totalResult'] for s in sessions_results if s['totalResult'] > 0])
        unprofitalbe_sessions = len([s['totalResult'] for s in sessions_results if s['totalResult'] <= 0])
        total_result = round(sum([s['totalResult'] for s in sessions_results]), 2)
        median_result = round(median([s['totalResult'] for s in sessions_results]), 2)
        best_result = round(max([s['totalResult'] for s in sessions_results]), 2)
        first_session = min([s.CreateDatetime for s in closed_sessions]).strftime("%d.%m.%Y")

        user_summary = {
            'userId': self.UserId,
            'userName': self.UserName,
            'totalSessions': total_sessions,
            'profitableSessions': profitalbe_sessions,
            'unprofitableSessions': unprofitalbe_sessions,
            'totalResult': total_result,
            'medianResult': median_result,
            'bestSessionResult': best_result,
            'firstSession': first_session
        }

        return user_summary


class Authentication(db.Model):
    __tablename__ = 'Authentication'

    AuthId = db.Column(db.Integer, primary_key=True, index=True)
    UserId = db.Column(db.Integer, db.ForeignKey('User.UserId', ondelete='CASCADE'), index=True)
    AuthDatetime = db.Column(db.DateTime, default=datetime.utcnow)
    IpAddress = db.Column(db.String)
    UserAgent = db.Column(db.String)
    StatusCode = db.Column(db.String)

    def __repr__(self) -> str:
        """Return description"""
        return f'<Authentication {self.AuthId} for {self.UserId} at {self.AuthDatetime}>'

    def __init__(self, user, details):
        """Create new record in db with authentication details"""
        
        self.UserId = user.UserId if user else None
        self.IpAddress = details['ip_address']
        self.UserAgent = details['user_agent']

        assert details['status_code'] in ['200', '201', '401', '500'], 'Wrong status code'
        self.StatusCode = details['status_code']
        
        # Write record to db
        write_object_to_db(self)


class Session(db.Model):
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
    iterations = db.relationship('Iteration', backref='Session', lazy='dynamic', passive_deletes=True)
    decisions = db.relationship('Decision', backref='Session', lazy='dynamic', passive_deletes=True)
    
    def __repr__(self) -> str:
        """Return object description"""
        return f'<Session {self.SessionId}>'

    def new(self, mode: str, options: dict) -> None:
        """Create new session and write it to db"""

        # Custom session with manual specific options
        if mode == 'custom':
            # Set session's status to active
            self.Status = cfg.SESSION_STATUS_ACTIVE
            # Get options data from webpage
            self.UserId = int(options['userId'])
            self.Market = options['market']
            self.Ticker = options['ticker']
            self.Timeframe = options['timeframe']
            self.Barsnumber = int(options['barsnumber'])
            self.Timelimit = int(options['timelimit'])
            self.LastFixingBarDatetime = datetime.strptime(options['date'], '%Y-%m-%d')
            self.Iterations = int(options['iterations'])
            self.Slippage = float(options['slippage'])
            self.Fixingbar = int(options['fixingbar'])
            self.TradingType = self._determine_trading_type()
            self.FirstBarDatetime = self._calc_first_bar_datetime()
            self.Mode = mode
        else:
            raise RuntimeError('Only custom mode is available')

        # Write form data to db
        write_object_to_db(self)

        # Download quotes and update current session options in DB
        df_quotes = self._download_quotes()

        # Update current session options in DB
        self._update_session_with_df_data(df_quotes)

        # Create all iterations
        self._create_iterations(df_quotes)


    def _determine_trading_type(self) -> str:
        """Determine how long trader will keep the security: <day, <week or >week"""
        tf_in_mins = cfg.convert_timeframe_to_mintues(self.Timeframe)
        iteration_period_bars = self.Barsnumber + self.Fixingbar
        iteration_period_mins = iteration_period_bars * tf_in_mins

        if iteration_period_mins < cfg.TRADINGDAY_DURATION_MINS:
            trading_type = 'daytrading'
        elif iteration_period_mins < cfg.TRADINGDAY_DURATION_MINS * 5:
            trading_type = 'swingtrading'
        elif iteration_period_mins < cfg.TRADINGDAY_DURATION_MINS * 20:
            trading_type = 'shortinvesting'
        else:
            trading_type = 'longinvesting'

        return trading_type

    def _calc_first_bar_datetime(self) -> datetime:
        """Calculate datetime of the first bar in downloaded quotes dataset"""
        if self.TradingType == 'daytrading':
            # One iteration per day (round up)
            days_before = ceil(self.Iterations / 5) * 7 
        elif self.TradingType == 'swingtrading':
            # One iteration per week
            days_before = self.Iterations * 7
        elif self.TradingType == 'shortinvesting':
            # One iteration per month
            days_before = self.Iterations * 31
        else:
            # One iteration per 3 months
            days_before = self.Iterations * 31 * 3
        return self.LastFixingBarDatetime - timedelta(days=days_before)

    def _generate_filename_session(self):
        """ Get filename for current session """

        # Generate dirname
        if cfg.PLATFORM == 'win32':
            dir_path = cfg.PATH_DOWNLOADS + '\\' + str(self.SessionId) + '_' + str(self.Ticker) + '\\'
        else:
            dir_path = cfg.PATH_DOWNLOADS + '/' + str(self.SessionId) + '_' + str(self.Ticker) + '/'

        # Create dirs if not exist
        for dir in [cfg.PATH_DOWNLOADS, dir_path]:
            if not os.path.exists(dir):
                os.mkdir(dir)

        # Generate filename
        if cfg.SAVE_FORMAT == 'csv':
            filename = 'session_' + str(self.SessionId) + '.csv'
        elif cfg.SAVE_FORMAT == 'json':
            filename = 'session_' + str(self.SessionId) + '.json'

        # Return full path
        return dir_path + filename

    def _download_quotes(self) -> DataFrame:
        """Download qoutes data using finam.export lib and save it to HDD"""

        # Set path to save/load downloaded quotes data
        save_path = self._generate_filename_session()

        # Check: Pass if file for this session hasn't downloaded yet or it's size is smaller than 48 bytes
        assert not os.path.exists(save_path) or os.stat(save_path).st_size <= 48, 'Error: Quotes has already downloaded'   

        # Parse quotes with finam.export lib
        exporter = Exporter()
        security = exporter.lookup(code=self.Ticker, market=eval(self.Market),
                            code_comparator=LookupComparator.EQUALS)

        # If there are more than 1 security with the following ticker, use the first one
        if len(security) == 0:
            raise RuntimeError('Unable to find correct security for this ticker')
        elif len(security) >= 1:
            security = security.iloc[0]

        # Download quotes
        try:
            df_quotes = exporter.download(id_=security.name, market=eval(self.Market),
                                    start_date=self.FirstBarDatetime, end_date=self.LastFixingBarDatetime,
                                    timeframe=eval(self.Timeframe))
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
        """Update current session options in the DB"""
        # Write count of bars in the downloaded df
        self.TotalSessionBars = len(df_quotes)
        # Write LastFixingBarDatetime with a precise time from downloaded df
        dt_fix = df_quotes.iloc[-1:].index
        self.LastFixingBarDatetime = datetime.combine(pd.to_datetime(dt_fix).date[0], pd.to_datetime(dt_fix).time[0])
        # Write FirstBarDatetime with a precise time from downloaded df
        dt_start = df_quotes.iloc[:1].index
        self.FirstBarDatetime = datetime.combine(pd.to_datetime(dt_start).date[0], pd.to_datetime(dt_start).time[0])
        # Write to db
        write_object_to_db(self)

    def _create_iterations(self, df_quotes: pd.DataFrame) -> None:
        """Create all iterations for current session (self)"""
        for i in range (1, self.Iterations + 1):
            iteration = Iteration()
            iteration.new(session=self, iteration_num=i, df_quotes=df_quotes)

    def load_csv(self) -> DataFrame:
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

    @catch_db_exception
    def get_from_db(session_id: int) -> db.Model:
        """Get session's options from DB and fill with them the object"""
        return Session.query.get(int(session_id))

    def calc_sessions_summary(self) -> dict:
        """Collect all session attributes in one object"""
        try:
            decisions = self.decisions.all()
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
                'userId': self.UserId,
                'sessionId': self.SessionId,
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
        except:
            raise SQLAlchemyError('Error: No connection to DB')

    def set_status(self, status: str) -> None:
        """Record new session's status in db"""
        self.Status = status
        write_object_to_db(self)


class Iteration(db.Model):
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
        return f'<Iteration {self.IterationNum} of the session {self.SessionId}>'

    def new(self, session: Session, iteration_num: int, df_quotes: DataFrame) -> None:
        """Create new iteration"""
        
        # Check how much iterations is already created for this session
        assert len(session.iterations.all()) <= session.Iterations, 'Error: All iterations for this sessions was already created'

        # Fill basic options
        self.SessionId = session.SessionId
        self.IterationNum = iteration_num

        # Start generation iterations from the end of df
        if iteration_num == 1:
            # For first iteration use session options
            self.FixingBarDatetime = session.LastFixingBarDatetime
            self.FixingBarNum = session.TotalSessionBars - 1   # first bar num = 0
        else:
            # For other iteration find last created iteration and use it to calc new vals
            last_iteration = session.iterations.all()[-1:][0]
            self.FixingBarDatetime = last_iteration._calc_new_iteration_fixbardatetime()
            self.FixingBarNum = df_quotes.index.get_loc(str(self.FixingBarDatetime), method='nearest')
        
        # Fill other required bars numbers
        self.FinalBarNum = self.FixingBarNum - session.Fixingbar
        if session.Barsnumber <= self.FinalBarNum:
            self.StartBarNum = self.FinalBarNum - session.Barsnumber
        else:
            return

        # Write data to db
        write_object_to_db(self)

        # Save iteration quotes df to file
        df_quotes_cut = df_quotes.iloc[self.StartBarNum + 1:self.FixingBarNum + 1]
        save_path = self._generate_filename_iteration()
        if cfg.SAVE_FORMAT == 'csv':
            df_quotes_cut.to_csv(save_path, index=True, index_label='index')
        elif cfg.SAVE_FORMAT == 'json':
            df_quotes_cut.to_json(save_path, index=True, orient='records')
        else:
            raise RuntimeError('Error: Unsupported export file format')

        # Save iterations' prices
        self.StartBarPrice = df_quotes_cut.iloc[:1]['<CLOSE>'].values[0]
        self.FinalBarPrice = df_quotes_cut.iloc[session.Barsnumber-1:session.Barsnumber]['<CLOSE>'].values[0]
        self.FixingBarPrice = df_quotes_cut.iloc[-1:]['<CLOSE>'].values[0]
        
        # Update db object
        write_object_to_db(self)

    def _calc_new_iteration_fixbardatetime(self) -> datetime:
        """Calculate datetime of the previous bar in downloaded quotes dataset"""
        trading_type = self.Session.TradingType
        if trading_type == 'daytrading':
            # One iteration per day
            days_before = 1
        elif trading_type == 'swingtrading':
            # One iteration per week
            days_before = 7
        elif trading_type == 'shortinvesting':
            # One iteration per month
            days_before = 31
        else:
            # One iteration per 3 months
            days_before = 31 * 3
        return self.FixingBarDatetime - timedelta(days=days_before)

    @catch_db_exception
    def get_from_db(session_id: int, iteration_num: int) -> db.Model:
        """Get iterations's options from DB and fill with them the object"""
        return Iteration.query.filter(Iteration.SessionId == session_id, Iteration.IterationNum == iteration_num).first()

    def _generate_filename_iteration(self) -> str:
        """ Get filename for current iteration """

        # Generate dirname
        if cfg.PLATFORM == 'win32':
            dir_path = cfg.PATH_DOWNLOADS + '\\' + str(self.SessionId) + '_' + str(self.Session.Ticker) + '\\'
        else:
            dir_path = cfg.PATH_DOWNLOADS + '/' + str(self.SessionId) + '_' + str(self.Session.Ticker) + '/'

        # Create dirs if not exist
        for dir in [cfg.PATH_DOWNLOADS, dir_path]:
            if not os.path.exists(dir):
                os.mkdir(dir)
        
        # Generate filename
        if cfg.SAVE_FORMAT == 'csv':
            filename = 'iteration_' + str(self.SessionId) + '_' + str(self.IterationNum) + '.csv'
        elif cfg.SAVE_FORMAT == 'json':
            filename = 'iteration_' + str(self.SessionId) + '_' + str(self.IterationNum) + '.json'

        # Return full path
        return dir_path + filename

    def _read_data_file(self) -> DataFrame:
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
                        data=[graph_objs.Candlestick(
                        x=df.id + 1,                    #x=df.id OR x=df.index
                        open=df['<OPEN>'],
                        close=df['<CLOSE>'],
                        low=df['<LOW>'],
                        high=df['<HIGH>'],

                        increasing_line_color='#3c996e',
                        decreasing_line_color='#e15361'
                    )]
        )

        # Export chart and iteration in one JSON
        data = []
        data.append(chart_data)
        data.append(self._convert_to_dict())

        chart_JSON = json.dumps(data, cls=PlotlyJSONEncoder)
        return chart_JSON


class Decision(db.Model):
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
        return f'<Decision {self.DecisionId} during session {self.SessionId}>'

    def new(self, props: dict) -> None:
        """Create new session and write it to db"""
        current_iter = Iteration.get_from_db(session_id=props['sessionId'], iteration_num=props['iterationNum'])
        if not current_iter:
            return
        self.UserId = current_iter.Session.UserId
        self.SessionId = current_iter.SessionId
        self.IterationId = current_iter.IterationId
        self.Action = props['action']
        self.TimeSpent = props['timeSpent']
        
        # Calc results taking into account the slippage level
        price_change = round((current_iter.FixingBarPrice - current_iter.FinalBarPrice) / current_iter.StartBarPrice, 6)
        if self.Action == 'Buy':
            self.ResultRaw = price_change * 1
        elif self.Action == 'Skip':
            self.ResultRaw = price_change * 0
        elif self.Action == 'Sell':
            self.ResultRaw = price_change * -1
        else:
            raise RuntimeError('Unsupported action')
        self.ResultFinal = round(self.ResultRaw - current_iter.Session.Slippage, 6)

        # Write data to db
        write_object_to_db(self)


class Scoreboard:
    def __repr__(self) -> str:
        """Return object description"""
        return f'<Scoreboard>'

    def _get_all_users_results(mode: str) -> dict:
        """Return list of all users results"""
        closed_sessions = Session.query.filter(Session.Mode == mode, Session.Status == 'closed').all()
        sessions_results = [s.calc_sessions_summary() for s in closed_sessions]
        
        # Sum results of all sessions for every user
        users_results = {}
        for r in sessions_results:
            if r['userId'] not in users_results:
                users_results[r['userId']] = r['totalResult'] 
            else:
                users_results[r['userId']] += r['totalResult'] 
        
        # Order users by result
        users_results = OrderedDict(sorted(users_results.items(), key=lambda r: r[1], reverse=True))
        return users_results

    def get_users_top3(mode: str) -> dict:
        """Return list of top 3 leaders for selected mode"""
        users_results = Scoreboard._get_all_users_results(mode)
        
        # Cut dict to top3, round results and replace ids with names
        users_results = OrderedDict(islice(users_results.items(), 3))
        users_results_final = {}
        for idx, user in enumerate(users_results):
            users_results_final[idx] = {'name': User.get_user_by_id(user).UserName, 'result': round(users_results[user], 2)}

        return users_results_final  

    def get_user_rank(user, mode: str) -> int:
        """Return rank of user in global scoreboard"""
        users_results = Scoreboard._get_all_users_results(mode)
        rank = list(users_results).index(user.UserId)

        return rank


# General functions
# ==================

def write_object_to_db(object):
    """Default way to write SQLAlchemy object to DB"""
    try:
        db.session.add(object)
        db.session.commit()
    except SQLAlchemyError as e:
        raise SQLAlchemyError('Error: DB transaction has failed')
        

def delete_object_from_db(object):
    """Default way to write SQLAlchemy object to DB"""
    try:
        db.session.delete(object)
        db.session.commit()
    except SQLAlchemyError as e:
        raise SQLAlchemyError('Error: DB transaction has failed')


def create_system_users() -> None:
    """Create system users during first run of the script"""
    # Check if there is tables in db
    meta = db.MetaData(bind=db.engine)
    meta.reflect()
    if not meta.tables:
        logger.warning('DB is empty')
        return

    # Create demo user
    if User.get_user_by_email(cfg.USER_DEMO_EMAIL) is None:
        demo_user = User()
        creds = {'email': cfg.USER_DEMO_EMAIL, 'name': cfg.USER_DEMO_NAME, 'password': cfg.USER_DEMO_PASSWORD}
        demo_user.new(creds=creds)
        logger.info(f'Demo user "{cfg.USER_DEMO_EMAIL}" has been created')
        
    # Create test user
    if User.get_user_by_email(cfg.USER_TEST_EMAIL) is None:
        test_user = User()
        creds = {'email': cfg.USER_TEST_EMAIL, 'name': cfg.USER_TEST_NAME, 'password': cfg.USER_TEST_PASSWORD}
        test_user.new(creds=creds)
        logger.info(f'Test user "{cfg.USER_TEST_EMAIL}" has been created')