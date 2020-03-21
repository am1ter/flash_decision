from app import app
from app import functions
from flask import render_template, request


@app.route('/')
@app.route('/index')
def web_index():
    tickers = functions.get_df_all_tickers()
    timeframes = functions.get_df_all_timeframes()
    return render_template('index.html', tickers=tickers['code'], timeframes=timeframes)


@app.route('/terminal', methods=['GET'])
def web_terminal():
    # Get session_id from url
    session_id = request.args.get('session_id', type=int)
    source = request.args.get('source', type=str)

    # Get parameters for current session
    session_params = functions.get_df_session_params(session_id)

    # Get chart
    chart = functions.draw_chart_plotly(session_params, source)

    return render_template('terminal.html', session_params=session_params, plot=chart)