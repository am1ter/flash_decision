from app import app
import app.config as cfg
import app.service as srv
from app.models import Authentication, User, Decision, Session, Iteration

from flask import Blueprint, jsonify, request
from flask.wrappers import Response
import jwt
from datetime import datetime, timedelta
from functools import wraps
from finam import FinamParsingError


# Set up api prefix
api = Blueprint('api', __name__)

# Run during application initialization
srv.print_log(f'Flask has been started')
session_options = cfg.collect_session_options()


def auth_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        """Verify authorization token in request header"""
        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = 'Invalid session error. Registeration/authentication required.'
        expired_msg = 'Expired session error. Reauthentication required.'
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
            srv.print_log(expired_msg)
            return jsonify(expired_msg), 401
        except (jwt.InvalidTokenError, AssertionError) as e:
            srv.print_log(invalid_msg)
            return jsonify(invalid_msg), 401
        except (FinamParsingError):
            srv.print_log(finam_error_msg)
            return jsonify(finam_error_msg), 500
        except (Exception) as e:
            srv.print_log(runtime_msg)
            return jsonify(runtime_msg), 500

    return _verify


@api.errorhandler(500)
def internal_server_error(e):
    """Configure Flask error handler for current Blueprint"""
    return jsonify(e.name + ' (' + str(e.code) + '): ' + e.original_exception.args[0]), 500


@api.route('/check-backend/', methods=['GET'])
def check_backend() -> Response:
    """Check if backend is up"""
    return jsonify(True), 200


@api.route('/check-db/', methods=['GET'])
def check_db() -> Response:
    """Check if backend is up"""
    User.get_user_by_email(cfg.DEMO_EMAIL)
    return jsonify(True), 200


@api.route('/create-user/', methods=['POST'])
def sign_up() -> Response:
    """Get registration form and create user's record in db for it"""
    assert request.json, 'Error: Wrong POST request has been received'
    current_user = User()
    current_user.new(creds=request.json)
    srv.print_log(f'User {current_user} has been created')

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
def check_email() -> Response:
    """Check if email is free"""
    assert request.json, 'Error: Wrong POST request has been received'
    email_is_free = User.check_is_email_free(request.json['email'])
    return jsonify(email_is_free), 200


@api.route('/login/', methods=['POST'])
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
        srv.print_log(f'User {current_user} has been authentificated')
    else:
        resp = False
        status_code = '401'
        srv.print_log(f'Authentication failed for email {request.json["email"]}')

    # Record authentication in db
    auth_user = current_user if resp else None
    details = {'ip_address': request.remote_addr, 'user_agent': request.user_agent.string, 'status_code': status_code}
    Authentication(user=auth_user, details=details)

    return jsonify(resp), 200


@api.route('/get-session-options/', methods=['GET'])
@auth_required
def get_session_options() -> Response:
    """Get lists of all available parameters of the training set to show them on the page"""
    srv.print_log(f'List of session options has been generated')
    return jsonify(session_options), 200


@api.route('/start-new-session/', methods=['POST'])
@auth_required
def start_new_session() -> Response:
    """Start training session: Get json-object, create SQL record and download quotes data"""
    assert request.json, 'Error: Wrong POST request has been received'
    current_session = Session()
    current_session.new(mode='custom', options=request.json)
    srv.print_log(f'{current_session} has been started')
    return jsonify(current_session.SessionId), 200


@api.route('/get-chart/<int:session_id>/<int:iteration_num>/', methods=['GET'])
@auth_required
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

    srv.print_log(f'New chart for {loaded_iteration} has been drawed')
    return jsonify(chart), 200


@api.route('/record-decision/', methods=['POST'])
@auth_required
def record_decision() -> Response:
    """Save user's decision in db and score results for it"""
    assert request.json, 'Error: Wrong POST request has been received'
    new_decision = Decision()
    new_decision.new(props=request.json)
    srv.print_log(f'New decision {new_decision} has been recorded with result {round(new_decision.ResultFinal * 100, 2)}%')
    return jsonify(new_decision.ResultFinal), 200


@api.route('/get-sessions-results/<int:session_id>/', methods=['GET'])
@auth_required
def get_sessions_results(session_id: int) -> Response:
    """When session is finished collect it's summary in one object and send it back to frontend"""
    # Load session from db
    current_session = Session()
    current_session = current_session.get_from_db(session_id)
    # Get session's summary
    current_session_summary = current_session.calc_sessions_summary()
    srv.print_log(f'{current_session} has been finished with result {current_session_summary["totalResult"]}%')
    return jsonify(current_session_summary), 200


@api.route('/get-scoreboard/<int:user_id>/', methods=['GET'])
@auth_required
def get_scoreboard(user_id: int) -> Response:
    """Show global scoreboard and current user's results"""
    srv.print_log(f'Generated scoreboard for user #{user_id}')
    return jsonify(True), 200