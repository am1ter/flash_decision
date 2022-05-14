import app.config as cfg
from app.models import Authentication, User
from app.models import Session, Iteration, Decision, SessionResults, Scoreboard
from app.models import SessionCustom, SessionClassic, SessionBlitz, SessionCrypto
from app.models import check_db_connection

import logging
import socket
import traceback
from functools import wraps
from types import FunctionType

from flask import Blueprint, jsonify, request, Request
from flask.wrappers import Response
import jwt

from finam import FinamParsingError, FinamDownloadError


# App initialization
# ==================


# Set up loggers
logger_general = logging.getLogger('API.General')
logger_requests = logging.getLogger('API.Requests')
logger_responses = logging.getLogger('API.Responses')

# Register flask blueprint
api = Blueprint('api', __name__)

# Display Flask initialization output
local_ip = socket.gethostbyname(socket.gethostname())
network_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
network_socket.connect(("8.8.8.8", 80))
network_ip = network_socket.getsockname()[0]
logger_general.info(f'Flask started successfully')
logger_general.info(f'Flask`s local ip: {local_ip}, Flask`s network ip: {network_ip}')

# Parse finam for options for custom sessions during APP initialization
if cfg.PARSE_OPTIONS_AT_STARTUP:
    cfg.SessionOptions.update()
    logger_general.info('List of session`s options loaded')


# Decorators
# ==========


@api.before_request
def log_requests():
    """Log on debug level api requests"""
    # Do not log `options` requests (CORS: allow all origins)
    if request.method == 'OPTIONS':
        return
    # Check if request contains data with password. If yes delete from log
    if request.is_json:
        params = {k: v for (k, v) in request.json.items() if k != 'password'}
    else:
        params = {}
    # Log
    ip = find_request_ip(request)
    log_msg = f'Received {request.method} request to {request.path} from {ip} with params: {params}'
    logger_requests.debug(log_msg)


@api.after_request
def log_responses(resp):
    """Log on debug level api requests"""
    # Do not log `options` requests (CORS: allow all origins)
    if request.method == 'OPTIONS':
        return resp
    # Log
    ip = find_request_ip(request)
    params = str(resp.json)[: cfg.LOG_STRING_MAX_LENGTH]
    log_msg = f'Send response for request {request.path} to {ip} with params: {params}'
    logger_responses.debug(log_msg)
    return resp


def auth_required(f: FunctionType) -> FunctionType:
    @wraps(f)
    def _verify(*args, **kwargs):
        """Verify authorization token in request header"""

        invalid_msg = 'Invalid session. Registeration/authentication required.'
        expired_msg = 'Expired session. Reauthentication required.'
        finam_error_msg = 'Error during downloading quotes for selected security.'

        # Validate JSON Web Token (jwt) from header (is valid and not expired)
        try:
            User.get_user_by_jwt(request)
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            user_id_alias = 'UserId: ' + str(kwargs['user_id'])
            logger_general.warning(expired_msg + ' ' + user_id_alias)
            return jsonify(expired_msg), 401
        except (jwt.InvalidTokenError) as e:
            user_id_alias = 'UserId: ' + str(kwargs['user_id'])
            logger_general.warning(invalid_msg + ' ' + user_id_alias)
            return jsonify(invalid_msg), 401
        except (AssertionError) as e:
            assertion_msg = 'Error: ' + e.args[0]
            logger_general.error(assertion_msg + ' ' + user_id_alias)
            return jsonify(assertion_msg), 500
        except (FinamParsingError, FinamDownloadError):
            logger_general.error(finam_error_msg + ' ' + user_id_alias)
            return jsonify(finam_error_msg), 500

    return _verify


@api.errorhandler(500)
def internal_server_error(e):
    """Configure Flask internal error handler for current Blueprint"""

    logger_general.error(f'HTTPException {e.code}, Description: {e.description}')
    logger_general.error(f'Stack trace: {traceback.format_exc()}')

    # Prepare response to frontend
    errors = f'{e.name}. Something went wrong'
    resp = {'errors': errors}
    return jsonify(resp), 500


# API requests for authentication
# ===============================


@api.route('/sign-up/', methods=['POST'])
def api_sign_up() -> Response:
    """Get sign up form and create user record in db"""

    current_user = User.create(creds=request.json)

    # Record authentication in db
    status_code = 201
    details = {
        'ip_address': request.remote_addr,
        'user_agent': request.user_agent.string,
        'status_code': status_code,
    }
    Authentication.create(user=current_user, details=details)

    # Create JSON Web Token and prepare object to export to frontend
    data = {
        'id': current_user.UserId,
        'email': current_user.UserEmail,
        'token': current_user.encode_jwt_token(),
    }
    resp = {'data': data}
    logger_general.info(f'User {current_user} created')
    return jsonify(resp), 201


@api.route('/check-email-validity/', methods=['POST'])
def api_check_email() -> Response:
    """Check if email is free"""

    is_email_free = User.check_is_email_free(request.json['email'])

    # Prepare response to frontend
    data = {'isEmailFree': is_email_free}
    resp = {'data': data}
    logger_general.info(f'Email <{request.json["email"]}> is free: {is_email_free}')
    return jsonify(resp), 200


@api.route('/login/', methods=['POST'])
def api_login() -> Response:
    """Get request with login form and run authentication procedure"""

    try:
        # Check if user with specified email exists
        current_user = User.get_user_by_email(request.json['email'])
        # Check if password is correct
        is_password_correct = current_user.check_password(request.json['password'])
        is_email_valid = True
    except AttributeError:
        # If user for specified email was not found
        is_password_correct = False
        is_email_valid = False
        status_code = 204
        log_msg = f'Authentication failed. No user with email: {request.json["email"]}'

    # Save intermediate auth results in response object
    data = {
        'isEmailValid': is_email_valid,
        'isPasswordCorrect': is_password_correct,
    }

    # Process cases when user with specified email exists
    if is_email_valid and is_password_correct:
        # User found, password is correct
        # Create JSON Web Token and add it to response object
        new_data = {
            'id': current_user.UserId,
            'email': current_user.UserEmail,
            'token': current_user.encode_jwt_token(),
        }
        data.update(new_data)
        status_code = 200
        log_msg = f'User {current_user} authentificated'
    elif is_email_valid and is_password_correct == False:
        # User found, password is incorrect
        status_code = 401
        log_msg = f'Authentication failed for email: {request.json["email"]}. Incorrect password.'

    # Record authentication in db
    auth_user = current_user if is_email_valid else None
    db_record = {
        'ip_address': find_request_ip(request),
        'user_agent': request.user_agent.string,
        'status_code': status_code,
    }
    Authentication.create(user=auth_user, details=db_record)

    # Prepare response to frontend
    resp = {'data': data}
    logger_general.info(log_msg)
    return jsonify(resp), 200


# API requests for app operations
# ===============================


@api.route('/session-options/<string:mode>/', methods=['GET'])
@auth_required
def api_fetch_session_options(mode: str) -> Response:
    """Get lists of all available parameters (options) for new session builder to show them on frontend"""

    session_options = cfg.SessionOptions()

    # Prepare response to frontend
    data = session_options
    meta = {'mode': mode}
    resp = {'data': data, 'meta': meta}
    logger_general.info(f'List of session options for mode {mode} sent to frontend')
    return jsonify(resp), 200


@api.route('/sessions/<string:mode>/', methods=['POST'])
@auth_required
def api_start_new_session(mode: str) -> Response:
    """Start new session: Get mode and options, download quotes, create iterations"""

    # Create Session instance by mode from request
    session_creator = {
        'custom': SessionCustom,
        'classic': SessionClassic,
        'blitz': SessionBlitz,
        'crypto': SessionCrypto,
    }
    current_session = session_creator[mode].create(request=request.json)

    # Prepare response to frontend
    data = {
        'values': current_session.convert_to_dict(),
        'aliases': current_session.convert_to_dict_format(),
    }
    meta = {'mode': mode}
    resp = {'data': data, 'meta': meta}
    logger_general.info(f'{current_session} started')
    return jsonify(resp), 201


@api.route('/sessions/<string:mode>/<int:session_id>/iterations/<int:iter_num>/', methods=['GET'])
@auth_required
def api_render_chart(mode: str, session_id: int, iter_num: int) -> Response:
    """Send info about iteration (including json with chart data) to frontend"""

    # Get current iteration, current session and current user from db
    current_iter = Iteration.get_from_db(session_id, iter_num)
    current_session = Session.get_from_db(session_id)
    current_user = User.get_user_by_jwt(request)

    # Check if requested iteration exists
    if not current_iter:
        resp = {'data': {'isIterationFound': False}}
        log_msg = f'Chart generation for {current_session} skipped. Iteration {iter_num} not found'
        logger_general.warning(log_msg)
        return jsonify(resp), 200

    # Check if requested iteration (and session) owned by user who sent request
    if current_session.UserId != current_user.UserId:
        logger_general.warning(f'No access to {current_session} for {current_user}')
        return jsonify('You do not have no access to this session'), 401

    # Check if session is not closed
    if current_session.Status == cfg.SESSION_STATUS_CLOSED:
        logger_general.warning(f'Chart generation for {current_iter} failed (session is closed)')
        return jsonify('Something went wrong. Current session is already closed.'), 500

    # Check if all decisions before requested iteration were already made (manual skips is forbidden)
    total_decisions = len(current_session.decisions)
    blank_iterations = current_session.Iterations - len(current_session.iterations[:iter_num])
    if (total_decisions != iter_num - 1) and (total_decisions != iter_num - 1 - blank_iterations):
        logger_general.warning(f'Requested unexpected iteration info for {current_session}')
        return jsonify('Something went wrong. Please start new session.'), 500

    # Write 'Active' status for new session in db
    if current_session.Status == cfg.SESSION_STATUS_CREATED:
        current_session.set_status(cfg.SESSION_STATUS_ACTIVE)

    # Get info about iteration (including json with chart data) for current session to frontend
    data = {
        'values': current_session.convert_to_dict(),
        'aliases': current_session.convert_to_dict_format(),
        'chart': current_iter.prepare_chart_plotly(),
        'isIterationFound': True,
    }
    meta = {'mode': mode, 'sessionId': session_id, 'currentIterationNum': iter_num}
    resp = {'data': data, 'meta': meta}
    logger_general.info(f'Info about {current_iter} sent to frontend')
    return jsonify(resp), 200


@api.route('/sessions/<string:mode>/<int:session_id>/decisions/<int:iter_num>/', methods=['POST'])
@auth_required
def api_record_decision(mode: str, session_id: int, iter_num: int) -> Response:
    """Record decision in db and send confirmation to frontend"""

    # Get current iteration, current session and current user from db
    current_iter = Iteration.get_from_db(session_id, iter_num)
    current_session = Session.get_from_db(session_id)
    current_user = User.get_user_by_jwt(request)

    # Check if requested iteration exists
    if not current_iter:
        resp = {'data': {'isDecisionRecorded': False}}
        log_msg = f'Decision recording for {current_session} failed. Iteration {iter_num} not found'
        logger_general.warning(log_msg)
        return jsonify(resp), 200

    # Check if requested iteration (and session) owned by user who sent request
    if current_session.UserId != current_user.UserId:
        logger_general.warning(f'No access to {current_session} for {current_user}')
        return jsonify('You do not have no access to this session'), 401

    # Check if session is not closed
    if current_session.Status == cfg.SESSION_STATUS_CLOSED:
        logger_general.warning(f'Decision recording for {current_iter} failed (session is closed)')
        return jsonify('Something went wrong. Current session is already closed.'), 500

    # Check if all decisions before requested iteration were already made (manual skips is forbidden)
    total_decisions = len(current_session.decisions)
    blank_iterations = current_session.Iterations - len(current_session.iterations[:iter_num])
    if (total_decisions != iter_num - 1) and (total_decisions != iter_num - 1 - blank_iterations):
        logger_general.warning(f'Decision recording failed. {current_session} is inconsistent')
        return jsonify('Something went wrong. Please start new session.'), 500

    # Save user`s decision in db and calc results for it
    new_decision = Decision().create(iteration=current_iter, props=request.json)
    result = round(new_decision.ResultFinal * 100, 2)

    # Prepare response to frontend
    data = {'isDecisionRecorded': True}
    meta = {'mode': mode, 'sessionId': session_id, 'currentIterationNum': iter_num}
    resp = {'data': data, 'meta': meta}
    logger_general.info(f'New {new_decision} recorded with result {result}%')
    return jsonify(resp), 201


@api.route('/session-results/<string:mode>/<int:session_id>/', methods=['GET'])
@auth_required
def api_render_session_results(mode: str, session_id: int) -> Response:
    """When session is finished collect it's summary in one object and send it back to frontend"""

    # Get current iteration, current session and current user from db
    current_session = Session.get_from_db(session_id)
    current_user = User.get_user_by_jwt(request)

    # Check if requested session owned by user who sent request
    if current_session.UserId != current_user.UserId:
        logger_general.warning(f'No access to {current_session} for {current_user}')
        return jsonify('You do not have no access to this session'), 401

    # Write 'Closed' status for session in db
    if current_session.Status != cfg.SESSION_STATUS_CLOSED:
        current_session.set_status(cfg.SESSION_STATUS_CLOSED)

    # Get session's summary data by creating instance of SessionResults
    results = SessionResults(current_session)

    # Prepare response to frontend
    data = results
    meta = {'mode': mode, 'sessionId': session_id}
    resp = {'data': data, 'meta': meta}
    logger_general.info(f'{current_session} rendered. Session result is {results["totalResult"]}%')
    return jsonify(resp), 200


@api.route('/scoreboards/<string:mode>/<int:user_id>/', methods=['GET'])
@auth_required
def api_render_scoreboard(mode: str, user_id: int) -> Response:
    """Show global scoreboard and current user's results"""

    # Load user from db
    user = User.get_user_by_id(user_id)

    # Create Scoreboard instance
    sb = Scoreboard(mode=mode, user=user)

    # Prepare first part of the response
    top_users = sb.get_top_users(cfg.TOP_USERS_COUNT)
    data = {
        'topUsers': top_users,
        'isTopUsersRendered': True if top_users else False,
    }

    # Check if current user has results for current mode
    try:
        new_data = {
            'userSummary': sb.calc_user_summary(),
            'userRank': sb.get_user_rank(),
            'isUserSummaryRendered': True,
        }
        log_msg = f'{sb} generated'
    except (AssertionError, ValueError):
        new_data = {'isUserSummaryRendered': False}
        log_msg = f'No data for {sb})'

    # Prepare response to frontend
    data.update(new_data)
    meta = {'mode': mode, 'userId': user_id, 'topUsersCount': cfg.TOP_USERS_COUNT}
    resp = {'data': data, 'meta': meta}
    logger_general.info(log_msg)
    return jsonify(resp), 200


# API requests for testing
# ========================


@api.route('/check-backend/', methods=['GET'])
def api_check_backend() -> Response:
    """Check if backend is up"""
    data = {'isBackendUp': True}
    resp = {'data': data}
    logger_general.info(f'Backend check passed')
    return jsonify(resp), 200


@api.route('/check-db/', methods=['GET'])
def api_check_db() -> Response:
    """Check if there is a connection to db"""
    if check_db_connection():
        data = {'isDbUp': True}
        log_msg = f'Database connection check passed'
        status_code = 200
    else:
        data = {'isDbUp': False}
        log_msg = f'Database connection check failed'
        status_code = 500

    resp = {'data': data}
    logger_general.info(log_msg)
    return jsonify(resp), status_code


@api.route('/tests-cleanup/', methods=['DELETE'])
def api_tests_cleanup() -> Response:
    """Clean data generated during end2end tests"""
    # Delete test user
    user = User.get_user_by_email(cfg.USER_SIGNUP_EMAIL)
    if user:
        user.delete_user()
        is_deleted = True
    else:
        is_deleted = False

    # Prepare response to frontend
    data = {'isTestDataDeleted': is_deleted}
    resp = {'data': data}
    logger_general.info(f'Tests data clean up finished. Database records deleted: {is_deleted}')
    return jsonify(resp), 200


# Service functions
# =================


def find_request_ip(request: Request) -> str:
    """Find request`s sender real ip-address, even if server is behind reverse proxy"""
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip
