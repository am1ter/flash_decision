import os


URL_FRONTEND = os.environ.get('URL_FRONTEND') if os.environ.get('URL_FRONTEND') else 'http://localhost:8000'
URL_BACKEND = os.environ.get('URL_BACKEND') if os.environ.get('URL_BACKEND') else 'http://localhost:8001'
WAIT_TIMEOUT = 10
HEADLESS = False
START_MAXIMIZED = True