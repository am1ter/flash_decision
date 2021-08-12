from app import app
import app.functions as fn

from flask import Blueprint, jsonify

api = Blueprint('api', __name__)


@api.route('/get-session-options/', methods=['GET'])
def api_get_session_options():
    """Get lists of all available parameters of the training set to show them on the page"""
    
    # Option: Markets
    markets = fn.get_markets_list()
    # Conver list of strings to list of objects (+1 for idx because of vue-simple-search-dropdown)
    markets = [
        {'id': idx+1, 'name': market.replace('Market.', '')} for idx, market in enumerate(markets)
    ]

    # Option: Securities
    securities = fn.get_security_list()
    # Convert pandas dfs to dicts (key = market)
    securities = {
        key: securities[key].to_dict(orient='records') for key in securities.keys()
    }
    
    # Option: Timeframes
    timeframes = fn.get_df_all_timeframes()
    # Conver list of strings to list of objects (+1 for idx because of vue-simple-search-dropdown)
    timeframes = [
        {'id': idx+1, 'name': tf.replace('Timeframe.', '')} for idx, tf in enumerate(timeframes)
    ]

    # Option: Bars number
    barsNumber = [
        {'id': 1, 'name': '10'},
        {'id': 2, 'name': '15'},
        {'id': 3, 'name': '50'},
        {'id': 4, 'name': '100'}
        ]

    # Option: Time limit
    timeLimit = [
        {'id': 1, 'name': '5'},
        {'id': 2, 'name': '10'},
        {'id': 3, 'name': '30'},
        {'id': 4, 'name': '60'},
        {'id': 5, 'name': '120'}
        ]

    # Option: Iterations
    iterations = [
        {'id': 1, 'name': '5'},
        {'id': 2, 'name': '10'},
        {'id': 3, 'name': '20'},
        {'id': 4, 'name': '50'}
        ]
    
    # Option: Slippage
    slippage = [
        {'id': 1, 'name': '0'},
        {'id': 2, 'name': '0.1'},
        {'id': 3, 'name': '0.5'},
        {'id': 4, 'name': '1'}
        ]

    # Option: Fixing bar
    fixingBar = [
        {'id': 1, 'name': '10'},
        {'id': 2, 'name': '15'},
        {'id': 3, 'name': '20'},
        {'id': 4, 'name': '50'}
        ]

    # Dict with session options
    session_options = {
        'markets': markets,
        'securities': securities,
        'timeframes': timeframes,
        'barsNumber': barsNumber,
        'timeLimit': timeLimit,
        'iterations': iterations,
        'slippage': slippage,
        'fixingBar': fixingBar
    }

    return jsonify(session_options)