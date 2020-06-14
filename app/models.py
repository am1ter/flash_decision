from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app.libs.mixins import UserMixin   # Module dulicated and modified because of usage "user_id" instead "id"


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, index=True, unique=True)
    user_email = db.Column(db.String, index=True, unique=True)
    user_password_hash = db.Column(db.String(128))

    sessions = db.relationship('Session', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.user_name)

    def set_password(self, password):
        self.user_password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.user_password_hash, password)


class Session(db.Model):
    __tablename__ = 'sessions'

    session_id = db.Column(db.Integer, primary_key=True)
    session_status = db.Column(db.String)
    session_datetime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    case_market = db.Column(db.String)
    case_ticker = db.Column(db.String)
    case_timeframe = db.Column(db.String)
    case_barsnumber = db.Column(db.Integer)
    case_timer = db.Column(db.Integer)
    case_datetime = db.Column(db.DateTime)
    case_iterations = db.Column(db.Integer)
    case_slippage = db.Column(db.Float)
    case_fixingbar = db.Column(db.Integer)

    decisions = db.relationship('Decision', backref='session', lazy='dynamic')

    def __repr__(self):
        return '<Session {}>'.format(self.session_id)


class Decision(db.Model):
    __tablename__ = 'decisions'

    decision_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.session_id'), index=True)
    iteration_id = db.Column(db.Integer)
    iteration_finishbar_datetime = db.Column(db.DateTime)
    decision_action = db.Column(db.String)
    decision_time = db.Column(db.Float)
    decision_result_raw = db.Column(db.Float)
    decision_result_corrected = db.Column(db.Float)

    def __repr__(self):
        return '<Decision {} during session {}>'.format(self.decision_id, self.session_id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
