from app.config import FlaskConfig

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


# Create Flask application and load it's config
app = Flask(__name__, static_url_path='')
app.config.from_object(FlaskConfig)
cors = CORS(app, resources={r'/api/*': {'origins': '*'}})
logger.info('Flask initialized')


# Create database and migrations
db = SQLAlchemy(app)
migrate = Migrate(app, db)
logger.info('Connection to db established')


# Check if system users are exist, create them if not
from app.models import create_system_users
create_system_users()
logger.info('System users verified')


# Load scripts to run flask app
from app.api import api
app.register_blueprint(api, url_prefix='/api')
logger.info('API started successfully')