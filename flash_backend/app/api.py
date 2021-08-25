from app import app
from app.config import collect_session_options
import app.functions as fn
from app.models import Session, Iteration

from flask import Blueprint, request
from flask.wrappers import Response
import json

api = Blueprint('api', __name__)
session_options = collect_session_options()


@api.route('/get-session-options/', methods=['GET'])
def get_session_options() -> Response:
    """Get lists of all available parameters of the training set to show them on the page"""
    return json.dumps(session_options, ensure_ascii=False)


@api.route('/start-new-session/', methods=['POST'])
def start_new_session() -> Response:
    """Start training session: Get json-object, create SQL record and download quotes data"""
    request.get_json({'userId': 1, 'market': 'Market.SHARES', 'ticker': 'SBER', 'timeframe': 'Timeframe.MINUTES5', 'barsnumber': '10', 'timelimit': '10', 'date': '2021-08-13', 'iterations': '10', 'slippage': '0.1', 'fixingbar': '15'}) #TODO: Delete when debug will be finished
    if request.json:
        print(request.json) #TODO: Delete when debug will be finished
        try:
            current_session = Session()
            current_session.new(mode='custom', options=request.json)
            current_session.download_quotes() 
            return json.dumps(current_session.SessionId)
        except RuntimeError as e:
            error = str(e.__dict__['orig'])
            print(error)
            return json.dumps(False)
    else:
        return json.dumps(False)


@api.route('/get-chart/<int:session_id>/<int:iteration_num>/', methods=['GET'])
def get_chart(session_id, iteration_num) -> Response:
    print('get request received')
    current_session = Session()
    current_session = current_session.get_from_db(session_id)
    chart = fn.draw_chart_plotly(session=current_session)
    return json.dumps(chart)
    #return jsonify(True)