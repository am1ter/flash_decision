from app import app
import app.config as cfg
import app.functions as fn
from app.models import Decision, Session, Iteration

from flask import Blueprint, request
from flask.wrappers import Response
import json

api = Blueprint('api', __name__)
session_options = cfg.collect_session_options()


@api.route('/get-session-options/', methods=['GET'])
def get_session_options() -> Response:
    """Get lists of all available parameters of the training set to show them on the page"""
    return json.dumps(session_options, ensure_ascii=False)


@api.route('/start-new-session/', methods=['POST'])
def start_new_session() -> Response:
    """Start training session: Get json-object, create SQL record and download quotes data"""
    if request.json:
        try:
            current_session = Session()
            current_session.new(mode='custom', options=request.json)
            return json.dumps(current_session.SessionId)
        except RuntimeError as e:
            error = str(e.__dict__['orig'])
            print(error)
            return json.dumps(False)
    else:
        return json.dumps(False)


@api.route('/get-chart/<int:session_id>/<int:iteration_num>/', methods=['GET'])
def get_chart(session_id, iteration_num) -> Response:
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

    return json.dumps(chart, ensure_ascii=False)


@api.route('/record-decision/', methods=['POST'])
def record_decision() -> Response:
    """Start training session: Get json-object, create SQL record and download quotes data"""
    if request.json:
        try:
            new_decision = Decision()
            new_decision.new(action=request.json)
            # return json.dumps(new_decision.SessionId)
            return True
        except RuntimeError as e:
            error = str(e.__dict__['orig'])
            print(error)
            return json.dumps(False)
    else:
        return json.dumps(False)