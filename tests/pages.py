from elements import ElementInput, ElementButton, ElementDatePicker
from locators import LocatorsPageLogin, LocatorsPageSession, LocatorsPageDecision, LocatorsPageResults

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PageBase:
    """Base class to initialize the base page that will be called from all pages"""

    def __init__(self, driver):
        self.title = ''
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)

    def is_title_matches(self):
        """Verifies that the hardcoded text appears in page title"""
        self.wait.until(EC.title_contains(self.title))
        return self.title in self.driver.title


class PageLogin(PageBase):
    """Login page"""

    def __init__(self, driver):
        """Page setup"""
        PageBase.__init__(self, driver=driver)
        self.title = 'Sign in'
        self.input_email = ElementInput(page=self, locator=LocatorsPageLogin.input_email)
        self.input_password = ElementInput(page=self, locator=LocatorsPageLogin.input_password)
        self.button_signin = ElementButton(page=self, locator=LocatorsPageLogin.button_signin)
        self.button_signup = ElementButton(page=self, locator=LocatorsPageLogin.button_signup)
        self.button_signin_demo = ElementButton(page=self, locator=LocatorsPageLogin.button_signin_demo)

    def is_page_loaded(self):
        """Verifies that the page is loaded"""
        return len(self.driver.page_source) > 100

    def login_via_form(self, email, password):
        """Send email and password with html form"""
        self.input_email.val = email
        self.input_password.val = password
        self.button_signin.click()

    def login_via_demo_button(self):
        """Send email and password with html form"""
        self.button_signin_demo.click()

    def has_text_incorrect_creds(self):
        """Check if there is an alert on the page"""
        return 'Incorrect email or password' in self.driver.page_source


class PageSession(PageBase):
    """Session page"""

    def __init__(self, driver):
        """Page setup"""
        PageBase.__init__(self, driver=driver)
        self.title = 'Start new training session'
        self.button_logout = ElementButton(page=self, locator=LocatorsPageSession.button_logout)
        self.button_start = ElementButton(page=self, locator=LocatorsPageSession.button_start)
        self.input_market = ElementInput(page=self, locator=LocatorsPageSession.input_market)
        self.input_ticker = ElementInput(page=self, locator=LocatorsPageSession.input_ticker)
        self.input_timeframe = ElementInput(page=self, locator=LocatorsPageSession.input_timeframe)
        self.input_barsnumber = ElementInput(page=self, locator=LocatorsPageSession.input_barsnumber)
        self.input_timelimit = ElementInput(page=self, locator=LocatorsPageSession.input_timelimit)
        self.input_date = ElementDatePicker(page=self, locator=LocatorsPageSession.input_date)
        self.input_iterations = ElementInput(page=self, locator=LocatorsPageSession.input_iterations)
        self.input_slippage = ElementInput(page=self, locator=LocatorsPageSession.input_slippage)
        self.input_fixingbar = ElementInput(page=self, locator=LocatorsPageSession.input_fixingbar)

    def logout(self):
        """Click on the logout button"""
        self.button_logout.click()

    def start_custom_session(self):
        self.input_market.val = 'SHARES'
        self.input_ticker.val = 'AFLT'
        self.input_timeframe.val = '15'
        self.input_barsnumber.val = '50'
        self.input_timelimit.val = '120'
        self.input_date.last_workday()
        self.input_iterations.val = '5'
        self.input_slippage.val = '0.1'
        self.input_fixingbar.val = '15'
        self.button_start.click()


class PageDecision(PageBase):
    """Search results page action methods come here"""

    def __init__(self, driver):
        """Page setup"""
        PageBase.__init__(self, driver=driver)
        self.title = 'Make your decisions'
        self.button_sell = ElementButton(page=self, locator=LocatorsPageDecision.button_sell)
        self.button_skip = ElementButton(page=self, locator=LocatorsPageDecision.button_skip)
        self.button_buy = ElementButton(page=self, locator=LocatorsPageDecision.button_buy)

    def action_sell(self):
        """Press action button"""
        self.button_sell.click()

    def action_skip(self):
        """Press action button"""
        self.button_skip.click()

    def action_buy(self):
        """Press action button"""
        self.button_buy.click()


class PageResults(PageBase):
    """Search results page action methods come here"""

    def __init__(self, driver):
        """Page setup"""
        PageBase.__init__(self, driver=driver)
        self.title = 'Session’s summary'
        self.button_go_to_scoreboard = ElementButton(page=self, locator=LocatorsPageResults.button_go_to_scoreboard)

    def go_to_scoreboard(self):
        """Press button with link to scoreboard"""
        self.button_go_to_scoreboard.click()


class PageScoreboard(PageBase):
    """Search results page action methods come here"""

    def __init__(self, driver):
        """Page setup"""
        PageBase.__init__(self, driver=driver)
        self.title = 'Scoreboard'