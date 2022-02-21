from elements import ElementInput, ElementButton, ElementDatePicker
import locators as loc

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PageBase:
    """Base class to initialize the base page that will be called from all pages"""

    def __init__(self, driver):
        self.title = ''
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        check_page_loaded = self.is_page_loaded()
        assert check_page_loaded == True, f'Error during {self} loading: {check_page_loaded}'


    def is_page_loaded(self):
        """Verifies that the page is loaded"""
        # Wait until page is loaded
        self.wait.until(EC.title_contains(self.title))
        self.wait.until(EC.visibility_of_element_located(loc.LocatorsPageBase.div_footer))
        # Make checks
        is_page_length_enough = len(self.driver.page_source) > 100
        is_title_matches = self.title in self.driver.title
        has_errors = self.driver.find_elements(*loc.LocatorsPageBase.div_errors)
        if is_page_length_enough and is_title_matches and not has_errors:
            return True
        elif has_errors:
            return has_errors[0].text.split('\n')[0]
        elif is_page_length_enough:
            return 'Page length <= 100 symbols'
        elif is_title_matches:
            return 'Unexpected page title'


class PageLogin(PageBase):
    """Login page"""

    def __repr__(self):
        """Return formated object name"""
        return f'<Page Login>'

    def __init__(self, driver):
        """Page setup"""
        PageBase.__init__(self, driver=driver)
        self.title = 'Sign in'
        self.input_email = ElementInput(page=self, locator=loc.LocatorsPageLogin.input_email)
        self.input_password = ElementInput(page=self, locator=loc.LocatorsPageLogin.input_password)
        self.button_signin = ElementButton(page=self, locator=loc.LocatorsPageLogin.button_signin)
        self.button_signup = ElementButton(page=self, locator=loc.LocatorsPageLogin.button_signup)
        self.button_signin_demo = ElementButton(page=self, locator=loc.LocatorsPageLogin.button_signin_demo)

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

    def __repr__(self):
        """Return formated object name"""
        return f'<Page Session>'

    def __init__(self, driver):
        """Page setup"""
        PageBase.__init__(self, driver=driver)
        self.title = 'Start new training session'
        self.button_logout = ElementButton(page=self, locator=loc.LocatorsPageSession.button_logout)
        self.button_start = ElementButton(page=self, locator=loc.LocatorsPageSession.button_start)
        self.input_market = ElementInput(page=self, locator=loc.LocatorsPageSession.input_market)
        self.input_ticker = ElementInput(page=self, locator=loc.LocatorsPageSession.input_ticker)
        self.input_timeframe = ElementInput(page=self, locator=loc.LocatorsPageSession.input_timeframe)
        self.input_barsnumber = ElementInput(page=self, locator=loc.LocatorsPageSession.input_barsnumber)
        self.input_timelimit = ElementInput(page=self, locator=loc.LocatorsPageSession.input_timelimit)
        self.input_date = ElementDatePicker(page=self, locator=loc.LocatorsPageSession.input_date)
        self.input_iterations = ElementInput(page=self, locator=loc.LocatorsPageSession.input_iterations)
        self.input_slippage = ElementInput(page=self, locator=loc.LocatorsPageSession.input_slippage)
        self.input_fixingbar = ElementInput(page=self, locator=loc.LocatorsPageSession.input_fixingbar)

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

    def __repr__(self):
        """Return formated object name"""
        return f'<Page Decision>'

    def __init__(self, driver):
        """Page setup"""
        PageBase.__init__(self, driver=driver)
        self.title = 'Make your decisions'
        self.button_sell = ElementButton(page=self, locator=loc.LocatorsPageDecision.button_sell)
        self.button_skip = ElementButton(page=self, locator=loc.LocatorsPageDecision.button_skip)
        self.button_buy = ElementButton(page=self, locator=loc.LocatorsPageDecision.button_buy)

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

    def __repr__(self):
        """Return formated object name"""
        return f'<Page Results>'

    def __init__(self, driver):
        """Page setup"""
        PageBase.__init__(self, driver=driver)
        self.title = 'Session’s summary'
        self.button_go_to_scoreboard = ElementButton(page=self, locator=loc.LocatorsPageResults.button_go_to_scoreboard)

    def go_to_scoreboard(self):
        """Press button with link to scoreboard"""
        self.button_go_to_scoreboard.click()


class PageScoreboard(PageBase):
    """Search results page action methods come here"""

    def __repr__(self):
        """Return formated object name"""
        return f'<Page Scoreboard>'

    def __init__(self, driver):
        """Page setup"""
        PageBase.__init__(self, driver=driver)
        self.title = 'Scoreboard'