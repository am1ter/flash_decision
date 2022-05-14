from os import environ as env

# URLs
URL_FRONTEND = env.get('URL_FRONTEND') if env.get('URL_FRONTEND') else 'http://localhost:8000'
URL_BACKEND = env.get('URL_BACKEND') if env.get('URL_BACKEND') else 'http://localhost:8001'

# Driver settings
WAIT_TIMEOUT = 10
DRIVER_HEADLESS = True
DRIVER_START_MAXIMIZED = True

# Test users credentials
USER_DEMO_EMAIL = 'demo@alekseisemenov.ru'
USER_DEMO_NAME = 'demo'
USER_DEMO_PASS = 'demo'
USER_TEST_EMAIL = 'test@alekseisemenov.ru'
USER_TEST_NAME = 'test'
USER_TEST_PASS = 'uc8a&Q!W'
USER_WRONG_EMAIL = 'wrong@alekseisemenov'
USER_WRONG_NAME = ''
USER_WRONG_PASS = 'wrong'
USER_SIGNUP_EMAIL = 'test-signup@alekseisemenov.ru'
USER_SIGNUP_NAME = 'test-signup'
USER_SIGNUP_PASS = 'uc8a&Q!W'