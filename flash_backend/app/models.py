from pandas.core.frame import DataFrame
from sqlalchemy import exc
from app import db, login
import app.config as config
import app.service as service

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError 

from finam.export import Exporter, LookupComparator # https://github.com/ffeast/finam-export
from finam.const import Market, Timeframe           # https://github.com/ffeast/finam-export

from app.libs.mixins import UserMixin   # Module duplicated and modified because of usage "UserId" instead "id"


class User(UserMixin, db.Model):
    __tablename__ = 'User'

    UserId = db.Column(db.Integer, primary_key=True, index=True)
    UserName = db.Column(db.String, index=True, unique=True)
    UserEmail = db.Column(db.String, index=True, unique=True)
    UserPassword = db.Column(db.String(128))

    sessions = db.relationship('Session', backref='User', lazy='dynamic', passive_deletes=True)

    def __repr__(self):
        """Return the user name"""
        return '<User {self.UserName}>'

    def new(self, name: str, email: str, password: str) -> None:
        """Create new user instance with hashed password and save it to DB"""
        self.UserName = name
        self.set_email(email)
        self.set_password(password)
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            print(error)

    def set_email(self, email):
        """Set new email for the user"""
        self.UserEmail = email
    
    def set_password(self, password):
        """Set new password for the user"""
        self.UserPassword = generate_password_hash(password)

    def check_password(self, password):
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
    SetFinishDatetime = db.Column(db.DateTime)
    Iterations = db.Column(db.Integer)
    Slippage = db.Column(db.Float)
    Fixingbar = db.Column(db.Integer)

    iterations = db.relationship('Iteration', backref='Session', lazy='dynamic', passive_deletes=True)
    
    def __repr__(self):
        """Return the session id"""
        return f'<Session {self.SessionId}>'

    def new(self, mode: str, options: dict) -> None:
        """Create new session and write it to db"""
        # Custom session with manual specific options
        if mode == 'custom':
            # Set session's status to active
            self.Status = config.SESSION_STATUS_ACTIVE
            # Get options data from webpage
            self.UserId = options['userId']
            self.Market = options['market']
            self.Ticker = options['ticker']
            self.Timeframe = options['timeframe']
            self.Barsnumber = options['barsnumber']
            self.Timelimit = options['timelimit']
            self.SetFinishDatetime = datetime.strptime(options['date'], '%Y-%m-%d')
            self.Iterations = options['iterations']
            self.Slippage = options['slippage']
            self.Fixingbar = options['fixingbar']
            # Write data to db
            try:
                db.session.add(self)
                db.session.commit()
            except SQLAlchemyError as e:
                error = str(e.__dict__['orig'])
                print(error)

    def download_quotes(self) -> None:
        """Download qoutes data using finam.export lib and save it to HDD"""

        # Set path to save/load downloaded quotes data
        save_path = service.get_filename_saved_data(self.SessionId, self.Ticker)

        # Determine required  period of quotes data according current session parameters
        if self.Timeframe == 'Timeframe.DAILY':
            days_before = (self.Iterations*31) + self.Barsnumber
        elif self.Timeframe == 'Timeframe.HOURLY':
            days_before = (self.Iterations * 4) + self.Barsnumber
        else:
            days_before = self.Iterations + 15

        period_start = self.SetFinishDatetime - timedelta(days=days_before)
        period_finish = self.SetFinishDatetime + timedelta(days=self.Fixingbar + 1)

        # Download data
        # Check: File for this session hasn't downloaded yet or it's size is smaller than 48 bytes (title row size)
        if not os.path.exists(save_path) or os.stat(save_path).st_size <= 48:
            
            # Parse quotes with finam.export lib
            exporter = Exporter()
            security = exporter.lookup(code=self.Ticker, market=eval(self.Market),
                                code_comparator=LookupComparator.EQUALS)
            assert len(security) == 1, 'Unable to find correct security for this ticker'
            
            # Download quotes
            try:
                df_quotes = exporter.download(id_=security.index[0], market=eval(self.Market),
                                        start_date=period_start, end_date=period_finish,
                                        timeframe=eval(self.Timeframe))
                df_quotes.index = pd.to_datetime(df_quotes['<DATE>'].astype(str) + ' ' + df_quotes['<TIME>'])
            except:
                raise RuntimeError('Unable to download quotes')

            # Save full df to file
            df_quotes.to_csv(save_path, index=True, index_label='index')

    def load_csv(self) -> DataFrame:
        """Get dataframe by reading data from hdd file"""
        # Set path to save/load downloaded ticker data
        save_path = service.get_filename_saved_data(self.SessionId, self.Ticker)
        # Load dataframe from hdd
        try:
            return pd.read_csv(save_path, parse_dates=True, index_col='index')
        except FileNotFoundError:
            raise FileNotFoundError('File not found: ' + save_path)

    def remove_csv(self) -> None:
        """Delete downloaded file with quotes"""
        if self.SessionId and self.Ticker:
            save_path = service.get_filename_saved_data(self.SessionId, self.Ticker)
            os.remove(save_path)
        else:
            raise FileNotFoundError('No information about id and ticker of the current session')

    def get_from_db(self, session_id: int):
        """Get session's options from DB and fill with them the object"""
        return Session.query.get(int(session_id))


class Iteration(db.Model):
    __tablename__ = 'Iteration'

    IterationId = db.Column(db.Integer, primary_key=True, index=True)
    SessionId = db.Column(db.Integer, db.ForeignKey('Session.SessionId', ondelete='CASCADE'), index=True)
    IterationNum = db.Column(db.Integer)
    FixingBarDatetime = db.Column(db.DateTime)
    Action = db.Column(db.String)
    TimeSpent = db.Column(db.Float)
    ResultRaw = db.Column(db.Float)
    ResultFinal = db.Column(db.Float)

    def __repr__(self):
        return f'<Iteration {self.IterationNum} during session {self.SessionId}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))