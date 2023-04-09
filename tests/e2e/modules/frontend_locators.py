from typing import NamedTuple

from selenium.webdriver.common.by import By


class Locator(NamedTuple):
    """Define particular locator"""

    by: str
    element: str


class LocPageBase:
    """Locators for all pages"""

    div_errors = Locator(By.ID, "errors")
    div_loader = Locator(By.ID, "vld-icon")
    div_footer = Locator(By.ID, "credits")

    button_logout = Locator(By.ID, "button-logout")
    button_menu_session = Locator(By.ID, "button-menu-session")
    button_menu_decision = Locator(By.ID, "button-menu-decision")
    button_menu_scoreboard = Locator(By.ID, "button-menu-scoreboard")


class LocPageLogin:
    """Locators for Login page"""

    input_email = Locator(By.ID, "input-email")
    input_password = Locator(By.ID, "input-password")
    button_signin = Locator(By.ID, "button-login")
    button_signup = Locator(By.ID, "button-signup")
    button_signin_demo = Locator(By.ID, "button-login-demo")


class LocPageSignup:
    """Locators for Signup page"""

    input_email = Locator(By.ID, "input-email")
    input_name = Locator(By.ID, "input-name")
    input_password = Locator(By.ID, "input-password")
    button_signup = Locator(By.ID, "button-signup")
    button_go_back = Locator(By.ID, "button-go-back")


class LocPageSession:
    """Locators for main page (Session page)"""

    button_mode_custom = Locator(By.ID, "button-custom")
    button_mode_classic = Locator(By.ID, "button-classic")
    button_mode_blitz = Locator(By.ID, "button-blitz")
    button_mode_crypto = Locator(By.ID, "button-crypto")


class LocPageSessionCustom:
    """Locators for Session Custom page"""

    input_market = Locator(By.NAME, "input-market")
    input_ticker = Locator(By.NAME, "input-ticker")
    input_timeframe = Locator(By.NAME, "input-timeframe")
    input_barsnumber = Locator(By.NAME, "input-barsnumber")
    input_timelimit = Locator(By.NAME, "input-timelimit")
    input_date = Locator(By.ID, "input-date")
    input_iterations = Locator(By.NAME, "input-iterations")
    input_slippage = Locator(By.NAME, "input-slippage")
    input_fixingbar = Locator(By.NAME, "input-fixingbar")
    button_start = Locator(By.ID, "button-start")


class LocPageDecision:
    """Locators for Decision page"""

    button_sell = Locator(By.ID, "button-sell")
    button_skip = Locator(By.ID, "button-skip")
    button_buy = Locator(By.ID, "button-buy")


class LocPageResults:
    """Locators for Session Results page"""

    button_to_scoreboard = Locator(By.ID, "button-to-scoreboard")
    button_new_session = Locator(By.ID, "button-new-session")


class LocPageScoreboard:
    """Locators for Scoreboard page"""

    button_mode_custom = Locator(By.ID, "button-mode-custom")
    button_mode_classic = Locator(By.ID, "button-mode-classic")
    button_mode_blitz = Locator(By.ID, "button-mode-blitz")
    button_mode_crypto = Locator(By.ID, "button-mode-crypto")
