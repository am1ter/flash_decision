from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.exc import SQLAlchemyError 
from app.libs.mixins import UserMixin   # Module duplicated and modified because of usage "UserId" instead "id"


class User(UserMixin, db.Model):
    __tablename__ = 'User'

    UserId = db.Column(db.Integer, primary_key=True, index=True)
    UserName = db.Column(db.String, index=True, unique=True)
    UserEmail = db.Column(db.String, index=True, unique=True)
    UserPassword = db.Column(db.String(128))

    sessions = db.relationship('Session', backref='User', lazy='dynamic', passive_deletes=True)

    def __repr__(self):
        return '<User {}>'.format(self.UserName)

    def set_password(self, password):
        self.UserPassword = generate_password_hash(password)

    def check_password(self, password):
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

    def __repr__(self):
        return '<Session {}>'.format(self.SessionId)


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
        return '<Decision {} during session {}>'.format(self.DecisionId, self.SessionId)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


def create_new_user(name: str, email: str, password: str) -> None:
    """Create new user with hashed password"""
    new_user = User()
    new_user.UserName = name
    new_user.UserEmail = email
    User.set_password(new_user, password)

    try:
        db.session.add(new_user)
        db.session.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error