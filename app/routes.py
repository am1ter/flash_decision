from app import app, config, functions, forms
from app.models import User, Session, Decision

from datetime import timedelta
from flask import render_template, request, redirect, flash, url_for

import pandas as pd


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        return redirect(url_for('web_index_get'))
    return render_template('login.html', form=form)


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def web_index_get():
    timeframes = functions.get_df_all_timeframes()
    markets = functions.get_df_all_markets()
    tickers = functions.get_df_all_tickers()
    return render_template('index.html', markets=markets, timeframes=timeframes, tickers=tickers['code'])


@app.route('/index', methods=['POST'])
def web_index_post():
    functions.create_session(form=request.form)
    session_id = functions.get_last_session_id()
    return redirect(f'/terminal?session_id={session_id}&iteration=1')


@app.route('/terminal', methods=['GET'])
def web_terminal_get():
    # Get key parameters from url
    session_id = request.args.get('session_id', type=int)
    iteration = request.args.get('iteration', type=int)

    # Get parameters for current session
    current_session = functions.get_session(session_id)

    # Change route by iteration number
    if iteration == 1:
        source = 'internet'
        # Get chart
        chart = functions.draw_chart_plotly(current_session, source)
        return render_template('terminal.html', session=current_session, iteration=iteration, plot=chart)
    else:
        source = 'hdd'
        # Duplicate session for modify during iteration
        current_session_iteration = current_session
        # Modify session by changing datetime for current iteration number
        iteration_datetime_offset = current_session.case_datetime - timedelta(weeks=iteration - 1)
        current_session_iteration.case_datetime = iteration_datetime_offset
        # Get chart
        chart = functions.draw_chart_plotly(current_session_iteration, source)
        return render_template('terminal.html', session=current_session_iteration, iteration=iteration, plot=chart)


@app.route('/terminal', methods=['POST'])
def web_terminal_post():

    session_id = int(request.form['session_id'])
    iteration = int(request.form['iteration'])
    total_iterations = int(request.form['total_iterations'])

    # Create new decision
    functions.create_decision(form=request.form)

    # Check: Is it last iteration?
    if iteration >= total_iterations:
        functions.close_session(session_id)
        return redirect(f'/results?session_id={session_id}')
    else:
        iteration += 1
        return redirect(f'/terminal?session_id={session_id}&iteration={iteration}')


@app.route('/results', methods=['GET'])
def web_results_get():
    # Get key parameters from url
    session_id = request.args.get('session_id', type=int)

    if not session_id:
        raise ValueError('You should start session before you will be able to look at results')

    # Get results for current session
    summary = functions.get_session_summary(session_id)

    # Get username for current session
    user_id = summary['user_id']

    # Get all decisions by username
    all_decisions = functions.get_all_decisions(user_id)

    # Convert data to JSON to export to html
    data_json = all_decisions.to_json(orient='records')

    return render_template('results.html', summary=summary, data_json=data_json)
