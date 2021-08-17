from app import app, functions, forms
from app.models import User, Session, Decision

from datetime import timedelta
from flask import render_template, request, redirect, flash, url_for, jsonify
from flask_login import current_user, login_user, logout_user, login_required
import json


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Flask's authentication page"""
    if current_user.is_authenticated:
        return redirect(url_for('web_index_get'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.user_name == form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('web_index_get'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Flask's logout page"""
    logout_user()
    return redirect(url_for('login'))

# DELETE IT
# @app.route('/', methods=['GET'])
# @app.route('/index', methods=['GET'])
# @login_required
# def web_index_get():
#     """Setting training session parameters"""
#     # Get lists of all available parameters of the training set to show them on the page
#     timeframes = functions.read_session_options_timeframes()
#     # Securities is a combination of market + tickers
#     # markets = functions.get_df_all_markets()
#     # tickers = functions.get_df_all_tickers()
#     securities = functions.collect_session_options_securities()

#     # Jsonify dict of pandas df
#     securities_no_pd = {
#         key: securities[key].to_dict(orient='records')
#         for key in securities.keys()
#     }
#     securities_json = json.dumps(securities_no_pd, ensure_ascii=False)

#     return render_template('index.html', markets=securities.keys(), timeframes=timeframes, securities=securities,
#                            securities_json=securities_json)


@app.route('/index', methods=['POST'])
@login_required
def web_index_post():
    """Starting training session"""
    functions.create_session(form=request.form)
    session_id = functions.get_last_session_id()
    return redirect(f'/terminal?session_id={session_id}&iteration=1')


@app.route('/terminal', methods=['GET'])
@login_required
def web_terminal_get():
    """Showing traiding chart"""
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
        if current_session.case_timeframe == 'Timeframe.DAILY':
            iteration_datetime_offset = current_session.case_datetime - timedelta(weeks=(iteration - 1)*4)
        elif current_session.case_timeframe == 'Timeframe.HOURLY':
            iteration_datetime_offset = current_session.case_datetime - timedelta(weeks=iteration - 1)
        else:
            iteration_datetime_offset = current_session.case_datetime - timedelta(days=(iteration - 1)*2)
        current_session_iteration.case_datetime = iteration_datetime_offset
        # Get chart
        chart = functions.draw_chart_plotly(current_session_iteration, source)
        return render_template('terminal.html', session=current_session_iteration, iteration=iteration, plot=chart)


@app.route('/terminal', methods=['POST'])
@login_required
def web_terminal_post():
    """Saving decision"""
    session_id = int(request.form['session_id'])
    iteration = int(request.form['iteration'])
    total_iterations = int(request.form['total_iterations'])

    # Create new decision
    functions.create_decision(form=request.form)

    # Check: Is it the last iteration?
    if iteration >= total_iterations:
        functions.close_session(session_id)
        return redirect(f'/results?session_id={session_id}')
    else:
        iteration += 1
        return redirect(f'/terminal?session_id={session_id}&iteration={iteration}')


@app.route('/results', methods=['GET'])
@login_required
def web_results_get():
    """Showing results"""
    # Get key parameters from url
    session_id = request.args.get('session_id', type=int)

    # Get all decisions by username
    all_decisions = functions.get_all_decisions(current_user.user_id)

    # Convert data to JSON to export to html
    data_json = all_decisions.to_json(orient='records')

    # Get results for current session
    if session_id:
        summary = functions.get_session_summary(session_id)
        return render_template('results.html', summary=summary, data_json=data_json)
    else:
        return render_template('results.html', data_json=data_json)