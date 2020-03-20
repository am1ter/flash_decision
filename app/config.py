import os

# SQL connection properties
SQL_DRIVER = '{SQL Server}'
SQL_SERVER = 'sql-scan.nemanadvisors.com'
SQL_PORT = '1433'
SQL_DB = 'flash'
SQL_USER = 'flash'
SQL_PASSWORD = '4C_vVizZ!'

# SQL table names
SQL_TABLE_SESSIONS = '[flash].[dbo].[sessions]'

# Files
PATH_APP = os.path.dirname(os.path.abspath(__file__))
PATH_UPLOAD_FOLDER = os.path.join(os.path.dirname(PATH_APP), 'upload_folder') # go up one folder

# Chart parameters
DF_DURATION_DAYS = 90