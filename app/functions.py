from app import config
import pyodbc
import pandas as pd
import datetime

# Data readers
from finam.export import Exporter, Market, LookupComparator, Timeframe
# import pandas_datareader as pdr


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


def sql_select_to_pandas(request):
    """ Execute sql request and export data to pandas """

    # Connect to DB
    connection = sql_connect_to_db()

    # Read sql data
    df = pd.read_sql(request, connection)

    return df


def get_df_session_params(session_id):
    """Get dataframe with session parameters"""

    # Select Query:
    request = \
        f'''SELECT 
               [session_id]
              ,[session_status]
              ,[case_market]
              ,[case_ticker]
              ,[case_datetime]
              ,[case_timeframe]
              ,[case_bars_number]
              ,[case_timer]
          FROM {config.SQL_TABLE_SESSIONS}
          WHERE session_id = {session_id}
        '''

    # Get pandas df from request
    df = sql_select_to_pandas(request)
    return df


def get_df_all_tickers():
    """Get dataframe with all tickers by finam.export library https://www.finam.ru/profile/moex-akcii/gazprom/export/"""
    exporter = Exporter()
    tickers = exporter.lookup(market=[Market.SHARES])
    return tickers


def get_df_all_timeframes():
    all_timeframes = []
    for idx, tf in enumerate(Timeframe):
        all_timeframes.append(str(list(tuple(Timeframe))[idx]))
    return all_timeframes


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
        sec = exporter.download(id_=instrument.index[0], market=eval(market),
                                 start_date=start, end_date=datetime.datetime(2020, 3, 16),
                                 timeframe=eval(timeframe))
        print(sec.tail(bars_number))

        sec.to_csv(save_path)
    elif source == 'hdd':
        try:
            sec = pd.read_csv(save_path, parse_dates=True)
        except FileNotFoundError:
            raise FileNotFoundError('File not found: ' + save_path)
    else:
        raise NameError('Only internet or hdd can be used as data source')
    return sec


def graphs_plotly(seq):
    #seq['Start'] = seq.iloc[15-1]
    mpl_fig = plt.figure()
    graph = mpl_fig.add_subplot(111)
    graph.plot(seq, lw=5)
    plt.title('Pattern starts at ' + str(seq.index[15-1]))
    b = plotly.tools.mpl_to_plotly(mpl_fig, resize=True)
    b['layout']['xaxis']['showgrid'] = True
    b['layout']['yaxis']['showgrid'] = True
    plotly.offline.plot(b)


def get_chart(session_params, source):
    """Get all data to draw chart"""
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

    chart = 'Chart'
    return data