from app import config

import pyodbc
import pandas as pd
import datetime
from sqlalchemy import create_engine

import json
import plotly
import plotly.graph_objs as go

# Data readers
from finam.export import Exporter, Market, LookupComparator, Timeframe # https://github.com/ffeast/finam-export
# import pandas_datareader as pdr


# ==============================
# == Service functions
# ==============================


def sqlalchemy_create_engine():
    engine = create_engine(config.SQL_ENGINE, pool_size=10, max_overflow=20, convert_unicode=True)
    return engine


def sql_connect_to_db():
    """ Connect to SQL Server """
    try:
        connection = pyodbc.connect(f'Driver={config.SQL_DRIVER_PYODBC};'
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


def sql_update(query):
    """ Execute sql query and export data to pandas """

    # Connect to DB
    connection = sql_connect_to_db()

    # Create cursor
    cursor = connection.cursor()

    # Run query
    cursor.execute(query)
    connection.commit()

    return


def sql_select_to_pandas(query):
    """ Execute sql query and export data to pandas """

    # Connect to DB
    connection = sql_connect_to_db()

    # Read sql data
    df = pd.read_sql(query, connection)

    return df


def sql_insert_from_pandas(df, table):
    """ Insert into SQL table pandas dataframe with SQL-Alchemy """
    try:
        df.to_sql(table, con=sqlalchemy_create_engine(), if_exists='append', index=False)
    except Exception as error:
        raise SystemError(f"Failed to insert DF into the table. {error.args}")


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
    session_id = int(sql_select_to_value(query))
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


def db_insert_session(df_dict):
    # Insert into the SQL table with SQL-Alchemy:

    # Create DataFrame
    df = pd.DataFrame(df_dict)

    # Insert df
    sql_insert_from_pandas(df=df, table=config.SQL_TABLE_SESSIONS)


# ==============================
# == Terminal
# ==============================


def get_df_session_params(session_id):
    """Get dataframe with session parameters"""

    # Select query:
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
              ,[case_slippage]
              ,[case_fixing_bar]
          FROM {config.SQL_TABLE_SESSIONS}
          WHERE session_id = {session_id}
        '''

    # Get pandas df from query
    df = sql_select_to_pandas(query)
    if df['session_status'].values[0] == config.SESSION_STATUS_ACTIVE:
        return df
    else:
        raise ValueError('This session is not active. Return to home page and try again.')


def get_df_download_data(market, ticker, timeframe, bars_number, start, finish, fixing_bar):
    """Get dataframe with finance data and save it to file"""

    # Set path to save/load downloaded ticker data
    save_path = config.PATH_UPLOAD_FOLDER + '\\' + ticker + '.csv'

    # Parse quotes with finam.export library
    exporter = Exporter()
    instrument = exporter.lookup(code=ticker, market=eval(market),
                          code_comparator=LookupComparator.EQUALS)
    assert len(instrument) == 1
    df_full = exporter.download(id_=instrument.index[0], market=eval(market),
                             start_date=start, end_date=current_date,
                             timeframe=eval(timeframe))

    # Save full df to file
    df_full.to_csv(save_path)

    return df_full


def get_df_chart_data(source, market, ticker, timeframe, bars_number, start, finish, fixing_bar):
    """Get dataframe with finance data"""

    # Get current date to download data (df to finish date will be cut after download)
    current_date = pd.to_datetime(datetime.datetime.now())

    # Set path to save/load downloaded ticker data
    save_path = config.PATH_UPLOAD_FOLDER + '\\' + ticker + '.csv'

    if source == 'internet':
        # Parse quotes with finam.export library
        exporter = Exporter()
        instrument = exporter.lookup(code=ticker, market=eval(market),
                              code_comparator=LookupComparator.EQUALS)
        assert len(instrument) == 1
        df_full = exporter.download(id_=instrument.index[0], market=eval(market),
                                 start_date=start, end_date=current_date,
                                 timeframe=eval(timeframe))
        # Save full df to file
        df_full.to_csv(save_path)
        # Cut df to selected finish date
        df_cut = df_full[:(df_full.index.get_loc(str(finish), method='nearest'))+1]
        # Cut df with selected bars_number
        df = df_cut.iloc[-bars_number:]

        # Get df with final result: finish bar number + fixing bar number
        finish_df_shift = df_full.index.get_loc(str(finish), method='nearest') + fixing_bar
        df_result = df_full[finish_df_shift:finish_df_shift+1][config.COLUMN_RESULT]


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
    chart_fixing_bar = session_params['case_fixing_bar'].values[0]

    # Send parameters to parser and get chart data
    data = get_df_chart_data(source=source, market=chart_market, ticker=chart_ticker,
                             timeframe=chart_timeframe, bars_number=chart_bars_number,
                             start=chart_start, finish=chart_finish, fixing_bar=chart_fixing_bar)

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


def db_update_close_session(session_id):
    """Close current session"""

    # Update query:
    query = \
        f'''UPDATE {config.SQL_TABLE_SESSIONS}
            SET
              [session_status] = '{config.SESSION_STATUS_CLOSED}'
          WHERE session_id = {session_id}
        '''

    sql_update(query)


def db_insert_decision(decision):
    """Insert decision into table"""

    # Create df from dict
    df = pd.DataFrame(decision, index=[0])

    sql_insert_from_pandas(df, config.SQL_TABLE_DECISIONS)