from pandas.core.frame import DataFrame
from app import db
import app.config as config
import app.service as service
from app.models import User, Session, Decision

import os
import pyodbc
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.sql import func

import json
import plotly
import plotly.graph_objs as go

from finam.export import Exporter, LookupComparator             # https://github.com/ffeast/finam-export
from finam.const import Market, Timeframe                       # https://github.com/ffeast/finam-export


# Session page
# ============


def read_session_options_timeframes() -> list:
    """Read timeframes from finam module (hardcoded in external lib)"""

    options_timeframes = []
    for idx, tf in enumerate(Timeframe):
        options_timeframes.append(str(list(tuple(Timeframe))[idx]))
    return options_timeframes


def read_session_options_markets() -> list:
    """Read all markets from finam module (hardcoded in external lib)"""

    options_markets = []
    for idx, market in enumerate(Market):
        options_markets.append(str(list(tuple(Market))[idx]))

    return options_markets


def collect_session_options_securities() -> dict:
    """Read all markets from finam module (hardcoded in external lib) and enrich it by downloaded tickers"""

    exporter = Exporter()
    options_securities = {}

    # Read tickers for every market and convert it to dict
    for idx, market in enumerate(Market):
        tickers = exporter.lookup(market=[market])
        # Copy df to avoid chained assignation below
        tickers = tickers.copy(deep=True)
        # Copy index to column
        tickers.reset_index(inplace=True)
        # Replace special symbols in ticker's names
        tickers['name'] = tickers.loc[:, 'name'].apply(lambda str: str.replace('(', ' - ').replace(')', ''))
        # Create dict
        options_securities[str(list(tuple(Market))[idx])] = tickers

    return options_securities


# Decision page
# =============


def get_session(session_id):
    """Get session parameters by id"""

    current_session = Session.query.get(session_id)

    if current_session.session_status == config.SESSION_STATUS_ACTIVE:
        return current_session
    else:
        raise ValueError('This session is not active. Return to home page and try again.')


def download_data(session, start, finish):
    """Get dataframe with finance data and save it to file"""

    # Set path to save/load downloaded ticker data
    save_path = service.get_filename_saved_data(session.SessionId, session.Ticker)

    # Check: Has file for this session already downloaded?
    if not os.path.exists(save_path):
        # Parse quotes with finam.export library
        exporter = Exporter()
        instrument = exporter.lookup(code=session.Ticker, market=eval(session.Market),
                              code_comparator=LookupComparator.EQUALS)
        assert len(instrument) == 1
        df_full = exporter.download(id_=instrument.index[0], market=eval(session.Market),
                                 start_date=start, end_date=finish,
                                 timeframe=eval(session.Timeframe))
        # Save full df to file
        df_full.index = pd.to_datetime(df_full['<DATE>'].astype(str) + ' ' + df_full['<TIME>'])
        df_full.to_csv(save_path, index=True, index_label='index')
    else:
        df_full = load_hdd_data(session=session)

    return df_full


def load_hdd_data(session):
    """Get dataframe by reading data from hdd file"""
    # Set path to save/load downloaded ticker data
    save_path = service.get_filename_saved_data(session.SessionId, session.Ticker)

    # Load dataframe from hdd
    try:
        df_full = pd.read_csv(save_path, parse_dates=True, index_col='index')
    except FileNotFoundError:
        raise FileNotFoundError('File not found: ' + save_path)

    return df_full


def create_decision(form):
    """Create new decision for current session and write it to db"""

    new_decision = Decision()

    # Get parameters for current session
    current_session = get_session(form['session_id'])

    # Fill parameters by reading hidden form
    new_decision.session_id = form['session_id']
    new_decision.iteration_id = form['iteration']
    new_decision.iteration_finishbar_datetime = pd.to_datetime(form['datetime'])
    new_decision.decision_action = form['form_button']
    new_decision.decision_time = form['time_spent']

    # Get result
    if new_decision.decision_action != 'skip':
        # Raw result
        df_full = load_hdd_data(session=current_session)
        chart_value_finishbar = pd.to_datetime(new_decision.iteration_finishbar_datetime)

        # Get value of the object in last bar of the case chart
        finish_df_shift = df_full.index.get_loc(str(chart_value_finishbar), method='nearest')
        df_finish = df_full[finish_df_shift:finish_df_shift + 1][config.COLUMN_RESULT]
        val_finish = df_finish[0]

        # Get value of the object in fixing bar (last bar + fixing bar)
        fixing_df_shift = int(finish_df_shift) + int(current_session.case_fixingbar)
        df_fixing = df_full[fixing_df_shift:fixing_df_shift + 1][config.COLUMN_RESULT]
        try:
            val_fixing = df_fixing[0]
        except ValueError:
            raise ValueError('Fixing bar is not exist yet. Choose an earlier date')

        # Get percent change
        new_decision.decision_result_raw = round(((val_fixing - val_finish) / val_finish), 4)

        # Correct result by slippage
        new_decision.decision_result_corrected = new_decision.decision_result_raw - current_session.case_slippage
        new_decision.decision_result_corrected = round(new_decision.decision_result_corrected, 4)
    else:
        # Write nulls if there is no decision
        new_decision.decision_result_raw = 0
        new_decision.decision_result_corrected = 0

    # Write data to db
    db.session.add(new_decision)
    db.session.commit()


# def get_chart(current_session, source) -> DataFrame:
#     """Get all data to draw chart"""
#     # Format session parameters
#     if current_session.Timeframe == 'Timeframe.DAILY':
#         days_before = (current_session.Iterations*31) + current_session.Barsnumber
#     elif current_session.Timeframe == 'Timeframe.HOURLY':
#         days_before = (current_session.Iterations * 4) + current_session.Barsnumber
#     else:
#         days_before = current_session.Iterations + 15

#     chart_start = current_session.SetFinishDatetime - timedelta(days=days_before)
#     chart_finish = current_session.SetFinishDatetime + timedelta(days=current_session.Fixingbar + 1)

#     if source == 'internet':
#         # Send parameters to parser and download data
#         df_full = download_data(session=current_session, start=chart_start, finish=chart_finish)
#     elif source == 'hdd':
#         df_full = load_hdd_data(session=current_session)

#     # Parameters to cut dataframe
#     chart_value_finishbar = pd.to_datetime(current_session.SetFinishDatetime)

#     # Cut df to selected finish date
#     df_cut = df_full[:(df_full.index.get_loc(str(chart_value_finishbar), method='nearest'))+1]
#     # Cut df with selected bars_number
#     df_final = df_cut.iloc[-current_session.Barsnumber:]

#     return df_final


# def draw_chart_plotly(session, source):
#     """Prepare JSON with chart data to export into HTML-file"""
#     df = get_chart(session, source)
#     df['id'] = df.reset_index().index

#     data = [
#         go.Figure(
#             data=[go.Candlestick(
#                 x=df.id,                             #x=df.id OR x=df.index
#                 open=df['<OPEN>'],
#                 close=df['<CLOSE>'],
#                 low=df['<LOW>'],
#                 high=df['<HIGH>'],

#                 increasing_line_color='#59a14f',
#                 decreasing_line_color='#e15759'
#             )]
#         )
#     ]

#     chart_JSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

#     return chart_JSON


def get_chart(current_session) -> DataFrame:
    """Get all data to draw chart"""
    # Format session parameters
    if current_session.Timeframe == 'Timeframe.DAILY':
        days_before = (current_session.Iterations*31) + current_session.Barsnumber
    elif current_session.Timeframe == 'Timeframe.HOURLY':
        days_before = (current_session.Iterations * 4) + current_session.Barsnumber
    else:
        days_before = current_session.Iterations + 15

    chart_start = current_session.SetFinishDatetime - timedelta(days=days_before)
    chart_finish = current_session.SetFinishDatetime + timedelta(days=current_session.Fixingbar + 1)

    df_full = load_hdd_data(session=current_session)

    # Parameters to cut dataframe
    chart_value_finishbar = pd.to_datetime(current_session.SetFinishDatetime)

    # Cut df to selected finish date
    df_cut = df_full[:(df_full.index.get_loc(str(chart_value_finishbar), method='nearest'))+1]
    # Cut df with selected bars_number
    df_final = df_cut.iloc[-current_session.Barsnumber:]

    return df_final


def draw_chart_plotly(session):
    """Prepare JSON with chart data to export into HTML-file"""
    df = get_chart(session)
    df['id'] = df.reset_index().index

    data = [
        go.Figure(
            data=[go.Candlestick(
                x=df.id,                             #x=df.id OR x=df.index
                open=df['<OPEN>'],
                close=df['<CLOSE>'],
                low=df['<LOW>'],
                high=df['<HIGH>'],

                increasing_line_color='#59a14f',
                decreasing_line_color='#e15759'
            )]
        )
    ]

    chart_JSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return chart_JSON


def close_session(session_id):
    """Close current session"""

    # Get parameters for current session
    current_session = get_session(session_id)

    # Update session status
    current_session.Status = config.SESSION_STATUS_CLOSED

    # Write data to db
    db.session.commit()

    # Delete file with downloaded data
    save_path = service.get_filename_saved_data(current_session.SessionId, current_session.Ticker)
    if save_path and os.path.exists(save_path):
        os.remove(save_path)

# ==============================
# == Results
# ==============================


def get_session_summary(session_id):
    """Get list with decision summary for current session"""

    user_id = Session.query.filter(Session.session_id == session_id).first().user_id
    iterations = db.session.query(func.count(Decision.decision_id)).filter(Decision.session_id == session_id).first()[0]
    time = db.session.query(func.sum(Decision.decision_time)).filter(Decision.session_id == session_id).first()[0]
    result = db.session.query(func.sum(Decision.decision_result_corrected)).filter(Decision.session_id == session_id).first()[0]

    summary = {'user_id': user_id, 'iterations': iterations, 'time': time, 'result': result}

    # Return
    if result:
        return summary
    else:
        raise ValueError('There is no results for this session')


def get_all_decisions(user_id):
    """Get dataframe with all decisions"""

    query = db.session.query(Session, Decision.decision_action, Decision.decision_time, Decision.iteration_id,
                             Decision.decision_result_corrected).outerjoin(Session).filter(Session.user_id == user_id)
    df = pd.read_sql(query.statement, db.session.bind)

    # Return
    if len(df) >= 1:
        return df
    else:
        raise ValueError('There are no decisions in the database')
