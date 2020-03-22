from app import config
import pyodbc
import pandas as pd
import datetime

import numpy as np
import json
import plotly
import plotly.graph_objs as go

# Data readers
from finam.export import Exporter, Market, LookupComparator, Timeframe # https://github.com/ffeast/finam-export
# import pandas_datareader as pdr


# ==============================
# == Service functions
# ==============================


def sql_connect_to_db():
    """ Connect to SQL Server """
    try:
        connection = pyodbc.connect(f'Driver={config.SQL_DRIVER};'
                                    f'Server={config.SQL_SERVER};'
                                    f'Port={config.SQL_PORT};'
                                    f'Database={config.SQL_DB};'
                                    f'UID={config.SQL_USER};'
                                    f'PWD={config.SQL_PASSWORD}')
    except Exception as error:
        raise SystemError(f"Failed to connect to DB. {error.args}")
    return connection


def sql_select_to_value(query):
    """ Execute sql query and export data to pandas """

    # Connect to DB
    connection = sql_connect_to_db()

    # Create cursor
    cursor = connection.cursor()

    # Run query
    cursor.execute(query)
    value = cursor.fetchone()
    value = value[0]

    return value


def sql_select_to_pandas(query):
    """ Execute sql query and export data to pandas """

    # Connect to DB
    connection = sql_connect_to_db()

    # Read sql data
    df = pd.read_sql(query, connection)

    return df


# ==============================
# == Index
# ==============================


def get_last_session_id():
    """Get: Last session_id in DB """
    # Select Query:
    query = \
        f'''SELECT 
                TOP(1) [session_id]
            FROM {config.SQL_TABLE_SESSIONS}
            ORDER BY [session_id] DESC
        '''

    # Get pandas df from query
    session_id = sql_select_to_value(query)
    return session_id


def get_df_all_timeframes():
    all_timeframes = []
    for idx, tf in enumerate(Timeframe):
        all_timeframes.append(str(list(tuple(Timeframe))[idx]))
    return all_timeframes


def get_df_all_markets():
    all_markets = []
    for idx, market in enumerate(Market):
        all_markets.append(str(list(tuple(Market))[idx]))
    return all_markets


def get_df_all_tickers():
    """Get dataframe with all tickers by finam.export library https://www.finam.ru/profile/moex-akcii/gazprom/export/"""
    exporter = Exporter()
    tickers = exporter.lookup(market=[Market.SHARES])
    return tickers


# ==============================
# == Terminal
# ==============================


def get_df_session_params(session_id):
    """Get dataframe with session parameters"""

    # Select Query:
    query = \
        f'''SELECT 
               [session_id]
              ,[session_status]
              ,[username]
              ,[case_market]
              ,[case_ticker]
              ,[case_datetime]
              ,[case_timeframe]
              ,[case_bars_number]
              ,[case_timer]
              ,[case_iterations]
          FROM {config.SQL_TABLE_SESSIONS}
          WHERE session_id = {session_id}
        '''

    # Get pandas df from query
    df = sql_select_to_pandas(query)
    return df


def get_df_chart_data(source, market, ticker, timeframe, bars_number, start, finish):
    """Get dataframe with finance data"""

    # Set path to save/load downloaded ticker data
    save_path = config.PATH_UPLOAD_FOLDER + '\\' + ticker + '.csv'

    if source == 'internet':
        # Parse quotes with finam.export library
        exporter = Exporter()
        instrument = exporter.lookup(code=ticker, market=eval(market),
                              code_comparator=LookupComparator.EQUALS)
        assert len(instrument) == 1
        df_full = exporter.download(id_=instrument.index[0], market=eval(market),
                                 start_date=start, end_date=finish,
                                 timeframe=eval(timeframe))
        df = df_full.iloc[-bars_number:]
        df.to_csv(save_path)
    elif source == 'hdd':
        # Load dataframe from hdd
        try:
            df = pd.read_csv(save_path, parse_dates=True)
        except FileNotFoundError:
            raise FileNotFoundError('File not found: ' + save_path)
    else:
        raise NameError('Only internet or hdd can be used as data source')
    return df


def get_chart(session_params, source):
    """Get all data to draw chart"""
    # Format parameters
    chart_market = session_params['case_market'].values[0]
    chart_ticker = session_params['case_ticker'].values[0]
    chart_timeframe = session_params['case_timeframe'].values[0]
    chart_bars_number = session_params['case_bars_number'].values[0]
    chart_start = pd.to_datetime((session_params['case_datetime'] - pd.offsets.Day(config.DF_DURATION_DAYS)).values[0])
    chart_finish = pd.to_datetime(session_params['case_datetime'].values[0])

    # Send parameters to parser and get chart data
    data = get_df_chart_data(source=source, market=chart_market, ticker=chart_ticker,
                             timeframe = chart_timeframe, bars_number = chart_bars_number,
                             start=chart_start, finish=chart_finish)

    return data


def draw_chart_plotly(session_params, source):
    df = get_chart(session_params, source)
    df['id'] = df.reset_index().index

    data = [
        go.Figure(
            data=[go.Candlestick(
                x=df['id'],                             #x=df.index,
                open=df['<OPEN>'],
                close=df['<CLOSE>'],
                low=df['<LOW>'],
                high=df['<HIGH>'],

                increasing_line_color='#59a14f',
                decreasing_line_color='#e15759'
            )]
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON