from selenium.webdriver.common.by import By


class LocatorsPageBase(object):
    """Locators for all pages"""
    div_errors = (By.ID, 'errors')
    div_footer = (By.ID, 'credits')


class LocatorsPageLogin(object):
    """Locators for Login page"""
    input_email = (By.ID, 'input-email')
    input_password = (By.ID, 'input-password')
    button_signin = (By.ID, 'button-signin')
    button_signup = (By.ID, 'button-signup')
    button_signin_demo = (By.ID, 'button-signin-demo')


class LocatorsPageSignup(object):
    """Locators for Signup page"""
    input_email = (By.ID, 'input-email')
    input_name = (By.ID, 'input-name')
    input_password = (By.ID, 'input-password')
    button_signup = (By.ID, 'button-signup')
    button_go_back = (By.ID, 'button-go-back')


class LocatorsPageSession(object):
    """Locators for main page (Session page)"""
    button_logout = (By.ID, 'button-logout')
    button_menu_session = (By.ID, 'button-menu-session')
    button_menu_decision = (By.ID, 'button-menu-decision')
    button_menu_scoreboard = (By.ID, 'button-menu-scoreboard')
    button_mode_custom = (By.ID, 'button-custom')
    button_mode_classic = (By.ID, 'button-classic')
    button_mode_blitz = (By.ID, 'button-blitz')
    button_mode_crypto = (By.ID, 'button-crypto')


class LocatorsPageSessionCustom(object):
    """Locators for Session Custom page"""
    input_market = (By.NAME, 'input-market')
    input_ticker = (By.NAME, 'input-ticker')
    input_timeframe = (By.NAME, 'input-timeframe')
    input_barsnumber = (By.NAME, 'input-barsnumber')
    input_timelimit = (By.NAME, 'input-timelimit')
    input_date = (By.ID, 'input-date')
    input_iterations = (By.NAME, 'input-iterations')
    input_slippage = (By.NAME, 'input-slippage')
    input_fixingbar = (By.NAME, 'input-fixingbar')
    button_start = (By.ID, 'button-start')


class LocatorsPageDecision(object):
    """Locators for Decision page"""
    button_sell = (By.ID, 'button-sell')
    button_skip = (By.ID, 'button-skip')
    button_buy = (By.ID, 'button-buy')


class LocatorsPageResults(object):
    """Locators for Session Results page"""
    button_go_to_scoreboard = (By.ID, 'button-go-to-scoreboard')
    button_start_new_session = (By.ID, 'button-start-new-session')


class LocatorsPageScoreboard(object):
    """Locators for Scoreboard page"""
    button_mode_custom = (By.ID, 'button-mode-custom')
    button_mode_classic = (By.ID, 'button-mode-classic')
    button_mode_blitz = (By.ID, 'button-mode-blitz')
    button_mode_crypto = (By.ID, 'button-mode-crypto')