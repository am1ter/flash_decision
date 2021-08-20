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

    def __init__(self, name: str, email: str, password: str) -> None:
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

    def __repr__(self):
        """Return the user name"""
        return '<User {self.UserName}>'

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

    decisions = db.relationship('Decision', backref='Session', lazy='dynamic', passive_deletes=True)

    def __init__(self, mode: str, form: dict) -> None:
        """Create new session and write it to db"""

        # Custom session with manual specific options
        if mode == 'custom' and form is not None:
            # Set session's status to active
            self.Status = config.SESSION_STATUS_ACTIVE
            # Get form data from webpage
            self.UserId = form['userId']
            self.Market = form['market']
            self.Ticker = form['ticker']
            self.Timeframe = form['timeframe']
            self.Barsnumber = form['barsnumber']
            self.Timelimit = form['timelimit']
            self.SetFinishDatetime = datetime.strptime(form['date'], '%Y-%m-%d')
            self.Iterations = form['iterations']
            self.Slippage = form['slippage']
            self.Fixingbar = form['fixingbar']
            # Write data to db
            try:
                db.session.add(self)
                db.session.commit()
            except SQLAlchemyError as e:
                error = str(e.__dict__['orig'])
                print(error)

    def __repr__(self):
        """Return the session id"""
        return f'<Session {self.SessionId}>'

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
        save_path = service.get_filename_saved_data(self.SessionId, self.Ticker)
        os.remove(save_path)


class Decision(db.Model):
    __tablename__ = 'Decision'

    DecisionId = db.Column(db.Integer, primary_key=True, index=True)
    SessionId = db.Column(db.Integer, db.ForeignKey('Session.SessionId', ondelete='CASCADE'), index=True)
    IterationNum = db.Column(db.Integer)
    IterationFixingBarDatetime = db.Column(db.DateTime)
    DecisionAction = db.Column(db.String)
    DecisionTime = db.Column(db.Float)
    DecisionResultRaw = db.Column(db.Float)
    DecisionResultFinal = db.Column(db.Float)

    def __repr__(self):
        return f'<Decision {self.DecisionId} during session {self.SessionId}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))