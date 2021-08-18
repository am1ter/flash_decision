import re

from flask.scaffold import F
from app import app
import app.functions as fn

from flask import Blueprint, jsonify, request
from flask.wrappers import Response

api = Blueprint('api', __name__)


@api.route('/get-session-options/', methods=['GET'])
def api_get_session_options() -> Response:
    """Get lists of all available parameters of the training set to show them on the page"""
    
    # Option: Markets
    # ---------------
    markets = fn.read_session_options_markets()
    # Conver list of strings to list of objects (+1 for idx because of vue-simple-search-dropdown)
    markets = [
        {'id': idx+1, 'name': market.replace('Market.', ''), 'code': market} for idx, market in enumerate(markets)
    ]

    # Option: Securities
    # ------------------
    securities = fn.collect_session_options_securities()
    # Convert dict filled with pandas' dfs to dict of dicts (key = market)
    securities = {
        key: securities[key].to_dict(orient='records') for key in securities.keys()
    }
    
    # Option: Timeframes
    # ------------------
    timeframes = fn.read_session_options_timeframes()
    # Conver list of strings to list of dicts (+1 for idx because of vue-simple-search-dropdown)
    timeframes = [
        {'id': idx+1, 'name': tf.replace('Timeframe.', ''), 'code': tf} for idx, tf in enumerate(timeframes)
    ]

    # Option: Bars number
    # -------------------
    barsnumber = [
        {'id': 1, 'name': '10 bars', 'code': '10'},
        {'id': 2, 'name': '15 bars', 'code': '15'},
        {'id': 3, 'name': '50 bars', 'code': '50'},
        {'id': 4, 'name': '100 bars', 'code': '100'}
        ]

    # Option: Time limit
    # ------------------
    timelimit = [
        {'id': 1, 'name': '5 sec.', 'code': '5'},
        {'id': 2, 'name': '10 sec.', 'code': '10'},
        {'id': 3, 'name': '30 sec.', 'code': '30'},
        {'id': 4, 'name': '60 sec.', 'code': '30'},
        {'id': 5, 'name': '120 sec.', 'code': '120'}
        ]

    # Option: Iterations
    # ------------------
    iterations = [
        {'id': 1, 'name': '5', 'code': '5'},
        {'id': 2, 'name': '10', 'code': '10'},
        {'id': 3, 'name': '20', 'code': '20'},
        {'id': 4, 'name': '50', 'code': '50'}
        ]
    
    # Option: Slippage
    # ----------------
    slippage = [
        {'id': 1, 'name': '0%', 'code': '0'},
        {'id': 2, 'name': '0.1%', 'code': '0.1'},
        {'id': 3, 'name': '0.5%', 'code': '0.5'},
        {'id': 4, 'name': '1%', 'code': '1'}
        ]

    # Option: Fixing bar
    # ------------------
    fixingbar = [
        {'id': 1, 'name': '10', 'code': '10'},
        {'id': 2, 'name': '15', 'code': '15'},
        {'id': 3, 'name': '20', 'code': '20'},
        {'id': 4, 'name': '50', 'code': '50'}
        ]

    # Dict with session options
    # -------------------------
    session_options = {
        'markets': markets,
        'securities': securities,
        'timeframes': timeframes,
        'barsnumber': barsnumber,
        'timelimit': timelimit,
        'iterations': iterations,
        'slippage': slippage,
        'fixingbar': fixingbar
    }

    return jsonify(session_options)


@api.route('/start-new-session/', methods=['POST'])
def api_start_new_session() -> Response:
    """Start training session: Get json-object, create SQL record and download quotes data"""
    request.get_json({'userId': 1, 'market': 'Market.SHARES', 'ticker': 'SBER', 'timeframe': 'Timeframe.MINUTES5', 'barsnumber': '10', 'timelimit': '10', 'date': '2021-08-13', 'iterations': '10', 'slippage': '0.1', 'fixingbar': '15'}) #TODO: Delete when debug will be finished
    if request.json:
        print(request.json) #TODO: Delete when debug will be finished
        try:
            current_session = fn.create_session_sql(form=request.json)
            fn.download_security_quotes(session=current_session)        
            return jsonify(True)
        except:
            return jsonify(False)
    else:
        return jsonify(False)