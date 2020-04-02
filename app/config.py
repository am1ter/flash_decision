import os

# SQL connection properties
SQL_DRIVER_PYODBC = '{SQL Server}'
SQL_SERVER = 'sql-scan.nemanadvisors.com'
SQL_PORT = '1433'
SQL_DB = 'flash'
SQL_USER = 'flash'
SQL_PASSWORD = '4C_vVizZ!'

# SQL Alchemy options
SQL_DRIVER_ALCHEMY = 'SQL Server'
SQL_ENGINE = "mssql+pyodbc://%s:%s@%s:%s/%s?driver=%s" % \
              (SQL_USER, SQL_PASSWORD, SQL_SERVER, SQL_PORT, SQL_DB, SQL_DRIVER_ALCHEMY)

# SQL table names
SQL_TABLE_SESSIONS = 'sessions'
SQL_TABLE_DECISIONS = 'decisions'

# Files
PATH_APP = os.path.dirname(os.path.abspath(__file__))
PATH_UPLOAD_FOLDER = os.path.join(os.path.dirname(PATH_APP), 'upload_folder') # go up one folder

# Session parameters
SESSION_STATUS_ACTIVE = 'active'
SESSION_STATUS_CLOSED = 'closed'

# Chart parameters
DF_DURATION_DAYS = 90