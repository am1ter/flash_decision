from selenium.webdriver.common.by import By


class LocatorsPageLogin(object):
    """Locators for page_Login"""
    input_email = (By.ID, 'input-email')
    input_password = (By.ID, 'input-password')
    button_signin = (By.ID, 'button-signin')
    button_signup = (By.ID, 'button-signup')
    button_signin_demo = (By.ID, 'button-signin-demo')


class LocatorsPageSession(object):
    """Locators for page_Session"""
    button_logout = (By.ID, 'button-logout')
    button_start = (By.ID, 'button-start')
    input_market = (By.NAME, 'market')
    input_ticker = (By.NAME, 'ticker')
    input_timeframe = (By.NAME, 'timeframe')
    input_barsnumber = (By.NAME, 'barsnumber')
    input_timelimit = (By.NAME, 'timelimit')
    input_date = (By.ID, 'date__value_')
    input_iterations = (By.NAME, 'iterations')
    input_slippage = (By.NAME, 'slippage')
    input_fixingbar = (By.NAME, 'fixingbar')


class LocatorsPageDecision(object):
    """Locators for page_Decision"""
    button_sell = (By.ID, 'button-sell')
    button_skip = (By.ID, 'button-skip')
    button_buy = (By.ID, 'button-buy')


class LocatorsPageResults(object):
    """Locators for page_Decision"""
    button_go_to_scoreboard = (By.ID, 'button-go-to-scoreboard')