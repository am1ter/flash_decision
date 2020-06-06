from app import config

from flask import Flask, jsonify

import logging
import traceback

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# Create Flask application and configure it
app = Flask(__name__, static_url_path='')
app.config.from_object(config.FlaskConfig)


# Create database and migrations
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Debug: Create logger
logger = logging.getLogger()


# Debug: Create exception route
@app.errorhandler(code_or_exception=500)
def handle_http_exception(error):
    error_dict = {
        'code': error.code,
        'description': error.description,
        'stack_trace': traceback.format_exc()
    }
    log_msg = f"HTTPException {error_dict['code']}, Description: {error_dict['description']}, Stack trace: {error_dict['stack_trace']}"
    logger.log(msg=log_msg, level=40)
    if error.code == 500:
        response = jsonify(error.name + '. ' + str(error.original_exception))
    else:
        response = jsonify(error_dict)
    return response


# Load scripts to run flask app
from app import routes
from app.models import User, Session, Decision


# Debug: flask shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Session': Session, 'Decision': Decision}


