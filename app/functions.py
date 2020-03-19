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
              ,[case_ticker]
              ,[case_datetime]
              ,[case_timeframe]
              ,[case_bars_number]
              ,[case_duration]
          FROM {config.SQL_TABLE_SESSIONS}
          WHERE session_id = {session_id}
        '''

    # Get pandas df from request
    df = sql_select_to_pandas(request)
    return df


def get_df_chart_data(ticker, source, start, finish, parser):
    """Get dataframe with finance data"""
    save_path = config.PATH_UPLOAD_FOLDER + '\\' + ticker.values[0] + '.csv'

    if source == 'internet':
        # Parse quotes with finam.export library https://www.finam.ru/profile/moex-akcii/gazprom/export/
        exporter = Exporter()

        print('*** Looking up all RTS futures codes ***')
        res = exporter.lookup(
            market=[Market.USA],
            name='Microsoft',
            name_comparator=LookupComparator.STARTSWITH)
        print(','.join(res['code']))

        oil = exporter.lookup(name='Microsoft', market=[Market.USA],
                              name_comparator=LookupComparator.STARTSWITH)
        assert len(oil) == 1
        data = exporter.download(oil.index[0], market=Market.USA,
                                 start_date=datetime.date(2020, 3, 15), end_date=None,
                                 timeframe=Timeframe.HOURLY)
        print(data.tail(5))

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
    chart_ticker = session_params['case_ticker']
    chart_duration = int(session_params['case_timeframe'] * session_params['case_bars_number'])
    chart_start = session_params['case_datetime'] - pd.offsets.Second(chart_duration)
    chart_finish = session_params['case_datetime']
    data = get_df_chart_data(ticker=chart_ticker, source=source, start=chart_start, finish=chart_finish)

    chart = 'Chart'
    return data