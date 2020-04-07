from app import app, config, functions
from flask import render_template, request, redirect, Response


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def web_index_get():
    session_id = functions.get_last_session_id()
    timeframes = functions.get_df_all_timeframes()
    markets = functions.get_df_all_markets()
    tickers = functions.get_df_all_tickers()
    return render_template('index.html',
                           session_id=session_id, markets=markets, timeframes=timeframes, tickers=tickers['code'])


@app.route('/index', methods=['POST'])
def web_index_post():
    # Update session parameters
    session_id = functions.get_last_session_id() + 1
    session_status = config.SESSION_STATUS_ACTIVE

    # Get form data from webpage
    username = request.form['form_username']
    market = request.form['form_market']
    ticker = request.form['form_ticker']
    timeframe = request.form['form_timeframe']
    bars_number = request.form['form_bars_number']
    timer = request.form['form_timer']
    datetime_finish = request.form['form_datetime_finish']
    iterations = request.form['form_iterations']
    slippage = request.form['form_slippage']
    fixing_bar = request.form['form_fixing_bar']

    # Create dataframe
    df_dict = {'session_id': str(session_id), 'username': [username], 'session_status': [session_status],
               'case_market': [market], 'case_ticker': [ticker], 'case_datetime': [datetime_finish],
               'case_timeframe': [timeframe], 'case_bars_number': [bars_number], 'case_timer': [timer],
               'case_iterations': [iterations], 'case_slippage': [slippage], 'case_fixing_bar': [fixing_bar]}

    functions.db_insert_session(df_dict)

    return redirect(f'/terminal?session_id={session_id}')


@app.route('/terminal', methods=['GET'])
def web_terminal_get():
    # Get key parameters from url
    session_id = request.args.get('session_id', type=int)
    source = request.args.get('source', type=str, default='internet')

    # Get parameters for current session
    session_params = functions.get_df_session_params(session_id)

    # Get chart
    chart = functions.draw_chart_plotly(session_params, source)

    return render_template('terminal.html', session_params=session_params, plot=chart)


@app.route('/terminal', methods=['POST'])
def web_terminal_post():
    # Get key parameters from url
    session_id = request.form['session_id']

    # Get decision parameters
    decision = {'session_id': session_id, 'decision_action': request.form['form_button'], 'decision_time': 1.9}

    functions.db_insert_decision(decision)
    functions.db_update_close_session(session_id)

    #return redirect(f'/index')
    return Response('You decided to ' + decision['decision_action'] + '. Time spent: ' + str(decision['decision_time']))