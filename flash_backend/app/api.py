from app import app
import app.config as cfg
import app.functions as fn
import app.service as srv
from app.models import Decision, Session, Iteration

from flask import Blueprint, request
from flask.wrappers import Response
import json


api = Blueprint('api', __name__)
session_options = cfg.collect_session_options()
srv.print_log(f'Flask has been started')


@api.route('/get-session-options/', methods=['GET'])
def get_session_options() -> Response:
    """Get lists of all available parameters of the training set to show them on the page"""
    srv.print_log(f'List of session options has been generated')
    return json.dumps(session_options, ensure_ascii=False)


@api.route('/start-new-session/', methods=['POST'])
def start_new_session() -> Response:
    """Start training session: Get json-object, create SQL record and download quotes data"""
    if request.json:
        try:
            current_session = Session()
            current_session.new(mode='custom', options=request.json)
            srv.print_log(f'{current_session} has been started')
            return json.dumps(current_session.SessionId)
        except RuntimeError as e:
            raise RuntimeError('Error: No connection to DB')
    else:
        raise RuntimeError('Error: Wrong POST request has been received')


@api.route('/get-chart/<int:session_id>/<int:iteration_num>/', methods=['GET'])
def get_chart(session_id: int, iteration_num: int) -> Response:
    """Send json with chart data to frontend"""
    try:
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
        return json.dumps(chart, ensure_ascii=False)
    except Exception:
        raise RuntimeError('Error: No connection to DB')


@api.route('/record-decision/', methods=['POST'])
def record_decision() -> Response:
    """Save user's decision in db and score results for it"""
    if request.json:
        try:
            new_decision = Decision()
            new_decision.new(props=request.json)
            srv.print_log(f'New decision {new_decision} has been recorded with result {round(new_decision.ResultFinal * 100, 2)}%')
            return json.dumps(new_decision.ResultFinal)
        except RuntimeError as e:
            raise RuntimeError('Error: No connection to DB')
    else:
        raise RuntimeError('Error: Wrong POST request has been received')


@api.route('/get-sessions-results/<int:session_id>/', methods=['GET'])
def get_sessions_results(session_id: int) -> Response:
    """When session is finished collect it's summary in one object and send it back to frontend"""
    try:
        # Load session from db
        current_session = Session()
        current_session = current_session.get_from_db(session_id)
        # Get session's summary
        current_session_summary = current_session.calc_sessions_summary()
        current_session_result = round(current_session_summary['totalResult'] * 100, 2)
        srv.print_log(f'Session {current_session} has been finished with result {current_session_result}%')
        return json.dumps(current_session_summary, ensure_ascii=False)
    except Exception:
        raise RuntimeError('Error: No connection to DB')


@api.route('/get-scoreboard/<int:user_id>/', methods=['GET'])
def get_scoreboard(user_id: int) -> Response:
    """Show global scoreboard and current user's results"""
    try:
        srv.print_log(f'Generated scoreboard for user #{user_id}')
        return json.dumps(True, ensure_ascii=False)
    except Exception:
        raise RuntimeError('Error: No connection to DB')