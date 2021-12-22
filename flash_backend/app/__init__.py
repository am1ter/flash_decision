import app.service as service
from app.config import FlaskConfig

# from flask import Flask, config, jsonify
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

import logging
import traceback


# Fix bug with finam-export lib v.4.1.0
# service.fix_lib_finamexport()


# Create Flask application and configure it
app = Flask(__name__, static_url_path='')
app.config.from_object(FlaskConfig)
cors = CORS(app, resources={r'/api/*': {'origins': '*'}})

login = LoginManager(app)
login.login_view = 'login'


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
# from app import routes # TODO: Delete before release
from app.models import User, Session, Iteration
from app.api import api
app.register_blueprint(api, url_prefix='/api')