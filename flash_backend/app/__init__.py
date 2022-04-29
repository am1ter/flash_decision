from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
import logging.config
import yaml
from pathlib import Path


# Create logger
path_logs_local = Path.cwd() / 'flash_backend' / 'settings_logs.yaml'
path_logs_docker = Path.cwd() / 'settings_logs.yaml'
path_logs_settings = path_logs_local if path_logs_local.exists() else path_logs_docker

with open(str(path_logs_settings), 'r') as f:
    settings_logs = yaml.safe_load(f.read())
    logging.config.dictConfig(settings_logs)

logger = logging.getLogger('App')
logger.info('Logger started successfully')


# Create Flask application and load it`s config
from app.config import FlaskConfig
flask_app = Flask(__name__, static_url_path='')
flask_app.config.from_object(FlaskConfig)
cors = CORS(flask_app, resources={flask_app.config['API_PREFIX'] + '/*': {'origins': '*'}})
logger.info('Flask initialized')


# Create database and migrations
db = SQLAlchemy(flask_app)
migrate = Migrate(flask_app, db)


# Check if db connection is up and system users are exist (create them if not)
from app.models import check_db_connection, create_system_users
if not check_db_connection():
    logger.critical('Database connection error: Application closed.')
    exit(1)
logger.info('Connection to db established')
create_system_users()
logger.info('System users verified')


# Load scripts to run flask app, set up api prefix
from app.api import api
flask_app.register_blueprint(api, url_prefix=flask_app.config['API_PREFIX'])
logger.info('API started successfully')