from app import app
import app.functions as fn

from flask import Blueprint, jsonify

api = Blueprint('api', __name__)


@api.route('/get-session-options/', methods=['GET'])
def api_get_session_options():
    """Get lists of all available parameters of the training set to show them on the page"""
    
    # Option: Securities
    securities = fn.get_security_list()
    # Convert pandas dfs to dicts (key = market)
    securities_no_pd = {
        key: securities[key].to_dict(orient='records') for key in securities.keys()
    }
    
    # Option: Timeframes
    timeframes = fn.get_df_all_timeframes()

    # Option: Bars number
    bars_number = [10, 20, 50, 100]

    # Option: Time limit
    time_limit = [5, 10, 30, 60, 120]

    # Option: Iterations
    iterations = [5, 10, 20]
    
    # Option: Slippage
    slippage = [0, 0.1, 0.5, 1]

    # Option: Fixing bar
    fixing_bar = [10, 15, 20, 50]

    # Dict with session options
    session_options = {
        'securities': securities_no_pd,
        'timeframes': timeframes,
        'bars_number': bars_number,
        'time_limit': time_limit,
        'iteration': iterations,
        'slippage': slippage,
        'fixing_bar': fixing_bar
    }

    return jsonify(session_options)