from app import app
import app.config as cfg
from app.models import Authentication, User, Decision, Session, Iteration

from flask import Blueprint, jsonify, request
from flask.wrappers import Response
import jwt
from datetime import datetime, timedelta
from functools import wraps
import socket
from finam import FinamParsingError
import logging
import traceback
import re


# Set up logger
logger = logging.getLogger('API')

# Set up api prefix
api = Blueprint('api', __name__)

# Display Flask initialization output
local_ip = socket.gethostbyname(socket.gethostname())
network_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
network_socket.connect(("8.8.8.8", 80))
network_ip = network_socket.getsockname()[0]
logger.info(f'Flask started successfully')
logger.info(f'Flask`s local ip: {local_ip}, Flask`s network ip: {network_ip}')

# Get initial app settings
session_options = cfg.collect_session_options()
logger.info('List of session`s options loaded')


def log_request(f):
    @wraps(f)
    def _log(*args, **kwargs):
        """Log on debug level api requests"""
        # Check if request contains data with password. If yes delete from log
        if request.data:
            params_byte = str(request.data)[2:-1]
            params_str = ' with parameters: ' + re.sub(',"password":.*"', '', params_byte)
        else:
            params_str = ''
        logger.debug(f'{request.method} request to {request.path} from ip {request.remote_addr}{params_str}')
        return f(*args, **kwargs)
    return _log


def auth_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        """Verify authorization token in request header"""
        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = 'Invalid session. Registeration/authentication required.'
        expired_msg = 'Expired session. Reauthentication required.'
        finam_error_msg = 'Error during downloading quotes for selected security. Plase try again later.'
        runtime_msg = 'Runtime error during API request processing'
        
        # Check if header looks like header with auth info
        assert len(auth_headers) == 2, invalid_msg

        # Validate JWT from header is valid and not expired
        try:
            token = auth_headers[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            current_user = User.get_user_by_email(email=data['sub'])
            assert current_user, f'User {data["sub"]} not found'
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            logger.warning(expired_msg)
            return jsonify(expired_msg), 401
        except (jwt.InvalidTokenError) as e:
            logger.warning(invalid_msg)
            return jsonify(invalid_msg), 401
        except (AssertionError) as e:
            assertion_msg = 'Error: ' + e.args[0]
            logger.error(assertion_msg)
            return jsonify(assertion_msg), 500
        except (FinamParsingError):
            logger.error(finam_error_msg)
            return jsonify(finam_error_msg), 500
        except (Exception) as e:
            error_dict = {
                'description': e.description,
                'stack_trace': traceback.format_exc()
            }
            log_msg = f"HTTPException: Description: {error_dict['description']}, Stack trace: {error_dict['stack_trace']}"
            logger.error(log_msg)
            return jsonify(runtime_msg), 500

    return _verify


@api.errorhandler(500)
def internal_server_error(e):
    """Configure Flask error handler for current Blueprint"""
    error_dict = {
        'code': e.code,
        'description': e.description,
        'stack_trace': traceback.format_exc()
    }
    log_msg = f"HTTPException {error_dict['code']}, Description: {error_dict['description']}, Stack trace: {error_dict['stack_trace']}"
    logger.error(log_msg)
    if e.code == 500:
        response = jsonify(e.name + ' (' + str(e.code) + '): ' + e.original_exception.args[0]), 500
    else:
        response = jsonify(error_dict)
    return response


@api.route('/check-backend/', methods=['GET'])
@log_request
def check_backend() -> Response:
    """Check if backend is up"""
    return jsonify(True), 200


@api.route('/check-db/', methods=['GET'])
@log_request
def check_db() -> Response:
    """Check if backend is up"""
    User.get_user_by_email(cfg.USER_DEMO_EMAIL)
    return jsonify(True), 200


@api.route('/create-user/', methods=['POST'])
@log_request
def sign_up() -> Response:
    """Get registration form and create user's record in db for it"""
    assert request.json, 'Error: Wrong POST request has been received'
    current_user = User()
    current_user.new(creds=request.json)
    logger.info(f'User {current_user} created')

    # Create JSON Web Token and prepare export to frontend
    token = jwt.encode({
        'sub': current_user.UserEmail,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=60)},
        app.config['SECRET_KEY'])
    resp = {'id': current_user.UserId, 'email': current_user.UserEmail, 'token': token}

    # Record authentication in db
    status_code = '201'
    details = {'ip_address': request.remote_addr, 'user_agent': request.user_agent.string, 'status_code': status_code}
    Authentication(user=current_user, details=details)

    return jsonify(resp), 200


@api.route('/check-email/', methods=['GET', 'POST'])
@log_request
def check_email() -> Response:
    """Check if email is free"""
    assert request.json, 'Error: Wrong POST request has been received'
    email_is_free = User.check_is_email_free(request.json['email'])
    return jsonify(email_is_free), 200


@api.route('/login/', methods=['POST'])
@log_request
def sign_in() -> Response:
    """Get filled login form and run authentication procedure"""
    assert request.json, 'Error: Wrong POST request has been received'
    current_user = User.get_user_by_email(request.json['email'])

    # Check if user exists and password is correct
    if current_user:
        is_password_correct = current_user.check_password(request.json['password'])
    else:
        is_password_correct = False

    # Create JSON Web Token and prepare export to frontend
    if is_password_correct:
        token = jwt.encode({
            'sub': current_user.UserEmail,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=60)},
            app.config['SECRET_KEY'])
        resp = {'id': current_user.UserId, 'email': current_user.UserEmail, 'token': token}
        status_code = '200'
        logger.info(f'User {current_user} authentificated')
    else:
        resp = False
        status_code = '401'
        logger.info(f'Authentication failed for email {request.json["email"]}')

    # Record authentication in db
    auth_user = current_user if resp else None
    details = {'ip_address': request.remote_addr, 'user_agent': request.user_agent.string, 'status_code': status_code}
    Authentication(user=auth_user, details=details)

    return jsonify(resp), 200


@api.route('/get-session-options/', methods=['GET'])
@log_request
@auth_required
def get_session_options() -> Response:
    """Get lists of all available parameters of the training set to show them on the page"""
    logger.info(f'List of session options sent to frontend')
    return jsonify(session_options), 200


@api.route('/start-new-session/', methods=['POST'])
@auth_required
@log_request
def start_new_session() -> Response:
    """Start training session: Get json-object, create SQL record and download quotes data"""
    assert request.json, 'Error: Wrong POST request has been received'
    current_session = Session()
    current_session.new(mode='custom', options=request.json)
    logger.info(f'{current_session} started')
    return jsonify(current_session.SessionId), 200


@api.route('/get-chart/<int:session_id>/<int:iteration_num>/', methods=['GET'])
@auth_required
@log_request
def get_chart(session_id: int, iteration_num: int) -> Response:
    """Send json with chart data to frontend"""
    # Load session from db
    current_session = Session()
    current_session = current_session.get_from_db(session_id)
    # Check if iteration number from API request is correct
    assert 1 <= iteration_num <= current_session.Iterations, 'Error: Wrong iteration number'
    # Check if session is still active
    assert current_session.Status == cfg.SESSION_STATUS_ACTIVE, 'Error: Session is closed'

    # Get iteration from db and read data file
    loaded_iteration = Iteration()
    loaded_iteration = loaded_iteration.get_from_db(session_id, iteration_num)

    # Format data to draw it with plotly
    chart = loaded_iteration.prepare_chart_plotly()

    logger.info(f'New chart for {loaded_iteration} generated')
    return jsonify(chart), 200


@api.route('/record-decision/', methods=['POST'])
@auth_required
@log_request
def record_decision() -> Response:
    """Save user's decision in db and score results for it"""
    assert request.json, 'Error: Wrong POST request has been received'
    new_decision = Decision()
    new_decision.new(props=request.json)
    logger.info(f'New decision {new_decision} recorded with result {round(new_decision.ResultFinal * 100, 2)}%')
    return jsonify(new_decision.ResultFinal), 200


@api.route('/get-sessions-results/<int:session_id>/', methods=['GET'])
@auth_required
@log_request
def get_sessions_results(session_id: int) -> Response:
    """When session is finished collect it's summary in one object and send it back to frontend"""
    # Load session from db
    current_session = Session()
    current_session = current_session.get_from_db(session_id)
    # Get session's summary
    current_session_summary = current_session.calc_sessions_summary()
    logger.info(f'{current_session} finished with result {current_session_summary["totalResult"]}%')
    return jsonify(current_session_summary), 200


@api.route('/get-scoreboard/<int:user_id>/', methods=['GET'])
@auth_required
@log_request
def get_scoreboard(user_id: int) -> Response:
    """Show global scoreboard and current user's results"""
    logger.info(f'Generated scoreboard for user #{user_id}')
    return jsonify(True), 200


@api.route(f'/cleanup-tests-results/', methods=['POST'])
@log_request
def cleanup_tests_results() -> Response:
    """Clean data generated during end2end tests"""
    # Delete test user
    result = User.delete_user_by_email(cfg.USER_TEST_EMAIL)
    logger.info(f'Tests data clean up finished. DB records deleted: {result}')
    return jsonify(result), 200