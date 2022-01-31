from re import S
from flask_sqlalchemy import BaseQuery
from pandas.core.frame import DataFrame
from app import db, login
import app.config as cfg
import app.service as service

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError 
from sqlalchemy.sql import func
from math import ceil
import json
from plotly.utils import PlotlyJSONEncoder
from plotly import graph_objs
from statistics import median

from finam.export import Exporter, LookupComparator     # https://github.com/ffeast/finam-export
from finam.const import Market, Timeframe               # https://github.com/ffeast/finam-export

from app.libs.mixins import UserMixin   # Module duplicated and modified because of usage "UserId" instead "id"


# DB related classes
# ==================

class User(UserMixin, db.Model):
    __tablename__ = 'User'

    UserId = db.Column(db.Integer, primary_key=True, index=True)
    UserName = db.Column(db.String, index=True, unique=True)
    UserEmail = db.Column(db.String, index=True, unique=True)
    UserPassword = db.Column(db.String(128))

    sessions = db.relationship('Session', backref='User', lazy='dynamic', passive_deletes=True)

    def __repr__(self) -> str:
        """Return the user name"""
        return f'<User {self.UserName}>'

    def new(self, name: str, email: str, password: str) -> None:
        """Create new user instance with hashed password and save it to DB"""
        self.UserName = name
        self.set_email(email)
        self.set_password(password)
        # Write to db
        write_object_to_db(self)

    def get_user_by_id(id: int) -> BaseQuery:
        """Return object by id"""
        return User.query.get(int(id))

    def get_user_by_name(name: str) -> BaseQuery:
        """Return object by name"""
        return User.query.filter(User.UserName == name).first()

    def set_email(self, email: str) -> None:
        """Set new email for the user"""
        self.UserEmail = email
    
    def set_password(self, password: str) -> None:
        """Set new password for the user"""
        self.UserPassword = generate_password_hash(password)

    def check_password(self, password: str) -> None:
        """Check the password against stored hashed password """
        return check_password_hash(self.UserPassword, password)


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

    iterations = db.relationship('Iteration', backref='Session', lazy='dynamic', passive_deletes=True)
    decisions = db.relationship('Decision', backref='Session', lazy='dynamic', passive_deletes=True)
    
    def __repr__(self):
        """Return the session id"""
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
            # One iteration per day
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
        assert len(security) == 1, 'Unable to find correct security for this ticker'

        # Download quotes
        try:
            df_quotes = exporter.download(id_=security.index[0], market=eval(self.Market),
                                    start_date=self.FirstBarDatetime, end_date=self.LastFixingBarDatetime,
                                    timeframe=eval(self.Timeframe))
            df_quotes.index = pd.to_datetime(df_quotes['<DATE>'].astype(str) + ' ' + df_quotes['<TIME>'])
        except:
            raise RuntimeError('Unable to download quotes')

        # Save full df to file
        if cfg.SAVE_FORMAT == 'csv':
            df_quotes.to_csv(save_path, index=True, index_label='index')
        elif cfg.SAVE_FORMAT == 'json':
            df_quotes.to_json(save_path, index=True, orient='records')
        else:
            raise RuntimeError('Error: Unsupported export file format')

        # Return DF to create iterations
        return df_quotes

    def _update_session_with_df_data(self, df_quotes) -> None:
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

    def _create_iterations(self, df_quotes) -> None:
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

    def get_from_db(self, session_id: int) -> db.Model:
        """Get session's options from DB and fill with them the object"""
        try:
            return Session.query.get(int(session_id))
        except:
            raise SQLAlchemyError('Error: No connection to DB')

    def calc_sessions_summary(self) -> float:
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

    def __repr__(self):
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
        self.StartBarNum = self.FinalBarNum - session.Barsnumber
    
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

    def get_from_db(self, session_id: int, iteration_num: int) -> db.Model:
        """Get iterations's options from DB and fill with them the object"""
        return Iteration.query.filter(Iteration.SessionId == session_id, Iteration.IterationNum == iteration_num).first()

    def _generate_filename_iteration(self):
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
    SessionId = db.Column(db.Integer, db.ForeignKey('Session.SessionId', ondelete='CASCADE'), index=True)
    IterationId = db.Column(db.Integer, db.ForeignKey('Iteration.IterationId', ondelete='CASCADE'), index=True)
    Action = db.Column(db.String)
    TimeSpent = db.Column(db.Float)
    ResultRaw = db.Column(db.Float)
    ResultFinal = db.Column(db.Float)

    def __repr__(self):
        return f'<Decision {self.DecisionId} during session {self.SessionId}>'

    def new(self, props: dict) -> None:
        """Create new session and write it to db"""
        current_iter = Iteration()
        current_iter = current_iter.get_from_db(session_id=props['sessionId'], iteration_num=props['iterationNum'])
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


def write_object_to_db(object):
    """Default way to write SQLAlchemy object to DB"""
    try:
        db.session.add(object)
        db.session.commit()
    except SQLAlchemyError as e:
        raise SQLAlchemyError('Error: No connection to DB')


def create_def_user() -> None:
    """Create default user during first run of the script"""
    if User.get_user_by_name('admin') is None:
        def_user = User()
        def_user.new(name='admin', email='admin@localhost', password='admin')
        service.print_log('Default user "admin" has been created')