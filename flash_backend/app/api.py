import app.config as cfg
from app.models import Authentication, User, Session, Iteration, Decision, SessionResults, Scoreboard
from app.models import SessionCustom, SessionClassic, SessionBlitz, SessionCrypto
from app.models import check_db_connection

from flask import Blueprint, jsonify, request
from flask.wrappers import Response
import jwt
from functools import wraps
import socket
import logging
import traceback
from types import FunctionType

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
    params = {k: v for (k, v) in request.json.items() if k != 'password'} if request.is_json else {}
    # Find real ip address if reverse proxy is used
    ip = request.headers.getlist("X-Forwarded-For")[0] if request.headers.getlist("X-Forwarded-For") else request.remote_addr
    # Log
    logger_requests.debug(f'Received {request.method} request to {request.path} from ip {ip} with params: {params}')


@api.after_request
def log_responses(resp):
    """Log on debug level api requests"""
    # Do not log `options` requests (CORS: allow all origins)
    if request.method == 'OPTIONS':
        return resp
    # Check if request contains data with password. If yes delete from log
    ip = request.headers.getlist("X-Forwarded-For")[0] if request.headers.getlist("X-Forwarded-For") else request.remote_addr
    logger_responses.debug(f'Send response for request {request.path} to ip {ip} with params: {str(resp.json)[:500]}')
    return resp


def auth_required(f: FunctionType) -> FunctionType:
    @wraps(f)
    def _verify(*args, **kwargs):
        """Verify authorization token in request header"""

        invalid_msg = 'Invalid session. Registeration/authentication required.'
        expired_msg = 'Expired session. Reauthentication required.'
        finam_error_msg = 'Error during downloading quotes for selected security. Plase try again later.'
        
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

    runtime_msg = f'{e.name}. Something go wrong'
    return jsonify(runtime_msg), 500


# API requests for authentication
# ===============================

@api.route('/sign-up/', methods=['POST'])
def api_sign_up() -> Response:
    """Get sign up form and create user record in db"""

    assert request.json, 'Error: Wrong POST request received'
    current_user = User.create(creds=request.json)
    logger_general.info(f'User {current_user} created')

    # Create JSON Web Token and prepare object to export to frontend
    resp = {'id': current_user.UserId, 'email': current_user.UserEmail, 'token': current_user.encode_jwt_token()}

    # Record authentication in db
    status_code = '201'
    details = {'ip_address': request.remote_addr, 'user_agent': request.user_agent.string, 'status_code': status_code}
    Authentication.create(user=current_user, details=details)

    return jsonify(resp), 200


@api.route('/check-email-validity/', methods=['POST'])
def api_check_email() -> Response:
    """Check if email is free"""
    assert request.json, 'Error: Wrong POST request received'
    is_email_free = User.check_is_email_free(request.json['email'])
    return jsonify(is_email_free), 200


@api.route('/login/', methods=['POST'])
def api_login() -> Response:
    """Get request with login form and run authentication procedure"""

    assert request.json, 'Error: Wrong POST request received'
    current_user = User.get_user_by_email(request.json['email'])

    # Check if user with specified email exists
    if current_user:
        # Check if password is correct
        is_password_correct = current_user.check_password(request.json['password'])
        if is_password_correct:
            # Password is correct
            # Create JSON Web Token and prepare object to export to frontend
            resp = {'id': current_user.UserId, 'email': current_user.UserEmail, 'token': current_user.encode_jwt_token()}
            status_code = '200'
            logger_general.info(f'User {current_user} authentificated')
        else:
            # Password is incorrect
            resp = False
            status_code = '401'
            logger_general.info(f'Authentication failed for email {request.json["email"]}')
    
    # If user for specified email was not found
    if not current_user:
        resp = False
        status_code = '404'
        is_password_correct = False
        logger_general.info(f'Authentication failed. No user with email {request.json["email"]}')

    # Record authentication in db
    auth_user = current_user if resp else None
    details = {'ip_address': request.remote_addr, 'user_agent': request.user_agent.string, 'status_code': status_code}
    Authentication.create(user=auth_user, details=details)

    return jsonify(resp), 200


# API requests for app operations
# ===============================

@api.route('/get-session-options/<string:mode>/', methods=['GET'])
@auth_required
def api_get_session_options(mode: str) -> Response:
    """Get lists of all available parameters (options) for custom session to show them on frontend"""
    session_options = cfg.SessionOptions()
    logger_general.info(f'List of session options for mode {mode} sent to frontend')
    return jsonify(session_options), 200


@api.route('/start-new-session/', methods=['POST'])
@auth_required

def api_start_new_session() -> Response:
    """Start training session: Get json-object, create SQL record and download quotes data"""

    assert request.json, 'Error: Wrong POST request received'

    # Create Session instance by mode from request
    session_creator = {
        'custom': SessionCustom,
        'classic': SessionClassic,
        'blitz': SessionBlitz,
        'crypto': SessionCrypto
    }
    current_session = session_creator[request.json['mode']].create(request=request.json)

    # Prepare response to frontend
    response = {
        'values': current_session.convert_to_dict(),
        'aliases': current_session.convert_to_dict_format()
    }
    
    logger_general.info(f'{current_session} started')
    return jsonify(response), 200


@api.route('/get-chart/<int:session_id>/<int:iteration_num>/', methods=['GET'])
@auth_required
def api_get_chart(session_id: int, iteration_num: int) -> Response:
    """Send json with chart data to frontend"""

    # Get current iteration and current session from db
    current_iteration = Iteration.get_from_db(session_id, iteration_num)
    current_session = Session.get_from_db(session_id)

    # Check if there is requested iteration, if not - skip it at the frontend
    if not current_iteration:
        logger_general.warning(f'Chart generation for {current_session} failed (iteration not found)')
        return jsonify(False), 200

    # Check if session is not closed
    if current_session.Status == cfg.SESSION_STATUS_CLOSED:
        logger_general.warning(f'Chart generation for {current_iteration} failed (session is already closed)')
        return jsonify('Something went wrong. Current session is already closed'), 500

    # Write 'Active' status for new session in db
    if current_session.Status == cfg.SESSION_STATUS_CREATED:
        current_session.set_status(cfg.SESSION_STATUS_ACTIVE)

    # Format data to draw it with plotly
    chart = current_iteration.prepare_chart_plotly()
    
    logger_general.info(f'New chart for {current_iteration} generated')
    return jsonify(chart), 200


@api.route('/get-iteration-info/<int:session_id>/<int:iteration_num>/', methods=['GET'])
@auth_required
def api_get_iteration_info(session_id: int, iteration_num: int) -> Response:
    """Get info about iteration for current session and send it back to frontend"""

    # Get current iteration, current session and current user from db
    current_iteration = Iteration.get_from_db(session_id, iteration_num)
    current_session = Session.get_from_db(session_id)
    current_user = User.get_user_by_jwt(request)

    # Check if requested iteration exists
    if not current_iteration:
        logger_general.warning(f'Requested iteration #{iteration_num} during {current_session} does not exist')
        return jsonify('Something went wrong. There is no such iteration.'), 404

    # Check if requested iteration (and session) owned by user who sent request
    if current_session.UserId != current_user.UserId:
        logger_general.warning(f'No access to {current_session} for {current_user}')
        return jsonify('You do not have no access to this session'), 401
    
    # Check if session is already closed
    if current_session.Status == cfg.SESSION_STATUS_CLOSED:
        logger_general.warning(f'Requested iteration info for closed {current_session}')
        return jsonify('Something went wrong. Session is already closed.'), 500

    # Check if all decisions before requested iteration were already made (manual skips is forbidden)
    total_decisions = len(current_session.decisions)
    if total_decisions != iteration_num - 1:
        logger_general.warning(f'Requested unexpected iteration info for {current_session}')
        return jsonify('Something went wrong. Please start new session.'), 500

    # Prepare response to frontend
    response = {
        'values': current_session.convert_to_dict(),
        'aliases': current_session.convert_to_dict_format()
    }
    
    logger_general.info(f'Info about {current_iteration} sent to frontend')
    return jsonify(response), 200


@api.route('/record-decision/', methods=['POST'])
@auth_required
def api_record_decision() -> Response:
    """Save user`s decision in db and calc results for it"""

    assert request.json["sessionId"], 'Error: Wrong POST request received'
    new_decision = Decision.create(props=request.json)

    # Check if decision is recorded in db. If not - handle it on the frontend.
    if new_decision:
        logger_general.info(f'New {new_decision} recorded with result {round(new_decision.ResultFinal * 100, 2)}%')
        return jsonify(new_decision.ResultFinal), 200
    else:
        session = Session.get_from_db(request.json["sessionId"])
        logger_general.warning(f'New decision recording for {session} failed')
        return jsonify(False), 200


@api.route('/get-sessions-results/<int:session_id>/', methods=['GET'])
@auth_required
def api_get_sessions_results(session_id: int) -> Response:
    """When session is finished collect it's summary in one object and send it back to frontend"""

    # Load session from db
    current_session = Session.get_from_db(session_id)

    # Get session's summary data by creating instance of SessionResults
    session_results = SessionResults(current_session)

    # Write 'Closed' status for session in db
    current_session.set_status(cfg.SESSION_STATUS_CLOSED)

    logger_general.info(f'{current_session} finished with result {session_results["totalResult"]}%')
    return jsonify(session_results), 200


@api.route('/get-scoreboard/<string:mode>/<int:user_id>/', methods=['GET'])
@auth_required
def api_get_scoreboard(mode: str, user_id: int) -> Response:
    """Show global scoreboard and current user's results"""

    # Load user from db
    user = User.get_user_by_id(user_id)

    # Create Scoreboard instance
    sb = Scoreboard(mode=mode, user=user)

    # Check if there is scoreboard for current mode
    try:
        top3_users = sb.get_users_top3()
    except:
        logger_general.info(f'No scoreboard for {user} (mode: {mode})')
        return jsonify(False), 200
    
    # Check if current user has results for current mode
    try:
        user_summary = sb.calc_user_summary()
        user_rank = sb.get_user_rank()
    except (AssertionError, ValueError):
        user_summary = {}
        user_rank = -1
        logger_general.warning(f'Scoreboard generation failed for {user} (mode: {mode})')

    response = {
        'mode': mode,
        'userSummary': user_summary,
        'userRank': user_rank,
        'top3Users': top3_users
        }

    logger_general.info(f'{sb} generated')
    return jsonify(response), 200


# API requests for testing
# ========================

@api.route('/check-backend/', methods=['GET'])
def api_check_backend() -> Response:
    """Check if backend is up"""
    return jsonify(True), 200


@api.route('/check-db/', methods=['GET'])
def api_check_db() -> Response:
    """Check if there is a connection to db"""
    if check_db_connection():
        logger_general.info(f'Database connection check passed')
        return jsonify(True), 200
    else:
        logger_general.info(f'Database connection check failed')
        return jsonify(False), 500


@api.route('/cleanup-tests-results/', methods=['GET'])
def api_cleanup_tests_results() -> Response:
    """Clean data generated during end2end tests"""
    # Delete test user
    user = User.get_user_by_email(cfg.USER_TEST_SIGNUP_EMAIL)
    if user:
        user.delete_user()
        is_user_deleted = True
    else:
        is_user_deleted = False
    logger_general.info(f'Tests data clean up finished. Database records deleted: {is_user_deleted}')
    return jsonify(True), 200
