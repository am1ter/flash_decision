from elements import ElementInput, ElementButton, ElementDatePicker
import locators as loc

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PageBase:
    """Base class to initialize the base page that will be called from all pages"""

    title = ''

    def __init__(self, driver) -> None:
        self.driver = driver
        self.set_wait_timer(10)
        check_page_loaded = self.is_page_loaded()
        assert check_page_loaded == True, f'Error during {self} loading: {check_page_loaded}'

    def set_wait_timer(self, timeout: int) -> None:
        """Reset webdriver wait timer with new timeout (seconds) value"""
        # Delete existed wait timer and replace it with new one
        try:
            del self.wait
        except AttributeError:
            pass
        self.wait = WebDriverWait(self.driver, timeout)        

    def is_page_loaded(self) -> bool:
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

    def refresh_page(self) -> None:
        """Press F5 to reload page"""
        self.driver.refresh()
        assert self.is_page_loaded(), 'Error during page refresh'


class PageLogin(PageBase):
    """Login page"""

    title = 'Login'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page Login>'

    def __init__(self, driver):
        """Page setup"""
        super().__init__(driver)
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

    def go_to_signup(self):
        """Send email and password with html form"""
        self.button_signup.click()

    def has_text_incorrect_creds(self):
        """Check if there is an alert on the page"""
        return 'Incorrect email or password' in self.driver.page_source


class PageSignup(PageBase):
    """Signup page"""

    title = 'Create account'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page Signup>'

    def __init__(self, driver):
        """Page setup"""
        super().__init__(driver)
        self.input_email = ElementInput(page=self, locator=loc.LocatorsPageSignup.input_email)
        self.input_name = ElementInput(page=self, locator=loc.LocatorsPageSignup.input_name)
        self.input_password = ElementInput(page=self, locator=loc.LocatorsPageSignup.input_password)
        self.button_signup = ElementButton(page=self, locator=loc.LocatorsPageSignup.button_signup)
        self.button_go_back = ElementButton(page=self, locator=loc.LocatorsPageSignup.button_go_back)

    def go_back(self):
        """Click on the back button"""
        self.button_go_back.click()

    def sign_up(self, email, name, password):
        """Click on the back button"""
        self.input_email.val = email
        self.input_name.val = name
        self.input_password.val = password
        self.button_signup.click()


class PageSession(PageBase):
    """Session page"""

    title = 'Start new training session'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page SessionCustom>'

    def __init__(self, driver):
        super().__init__(driver)
        self.button_logout = ElementButton(page=self, locator=loc.LocatorsPageSession.button_logout)
        self.button_menu_session = ElementButton(page=self, locator=loc.LocatorsPageSession.button_menu_session)
        self.button_menu_decision = ElementButton(page=self, locator=loc.LocatorsPageSession.button_menu_decision)
        self.button_menu_scoreboard = ElementButton(page=self, locator=loc.LocatorsPageSession.button_menu_scoreboard)
        self.button_logout = ElementButton(page=self, locator=loc.LocatorsPageSession.button_logout)
        self.button_mode_custom = ElementButton(page=self, locator=loc.LocatorsPageSession.button_mode_custom)
        self.button_mode_classic = ElementButton(page=self, locator=loc.LocatorsPageSession.button_mode_classic)
        self.button_mode_blitz = ElementButton(page=self, locator=loc.LocatorsPageSession.button_mode_blitz)
        self.button_mode_crypto = ElementButton(page=self, locator=loc.LocatorsPageSession.button_mode_crypto)

    def logout(self):
        """Click on the logout button"""
        self.button_logout.click()

    def go_to_page(self, page):
        """Click on the logout button"""
        menu_to_click = {
            'session': self.button_menu_session,
            'decision': self.button_menu_decision,
            'scoreboard': self.button_menu_scoreboard
        }
        menu_to_click[page].click()

    def select_mode(self, mode):
        """Select mode by clicking mode button"""
        button_to_click = {
            'custom': self.button_mode_custom,
            'classic': self.button_mode_classic,
            'blitz': self.button_mode_blitz,
            'crypto': self.button_mode_crypto
        }
        button_to_click[mode].click()


class PageSessionCustom(PageBase):
    """Custom Session page"""

    title = 'Start new training session'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page SessionCustom>'

    def __init__(self, driver):
        """Page setup"""
        super().__init__(driver)
        self.input_market = ElementInput(page=self, locator=loc.LocatorsPageSessionCustom.input_market)
        self.input_ticker = ElementInput(page=self, locator=loc.LocatorsPageSessionCustom.input_ticker)
        self.input_timeframe = ElementInput(page=self, locator=loc.LocatorsPageSessionCustom.input_timeframe)
        self.input_barsnumber = ElementInput(page=self, locator=loc.LocatorsPageSessionCustom.input_barsnumber)
        self.input_timelimit = ElementInput(page=self, locator=loc.LocatorsPageSessionCustom.input_timelimit)
        self.input_date = ElementDatePicker(page=self, locator=loc.LocatorsPageSessionCustom.input_date)
        self.input_iterations = ElementInput(page=self, locator=loc.LocatorsPageSessionCustom.input_iterations)
        self.input_slippage = ElementInput(page=self, locator=loc.LocatorsPageSessionCustom.input_slippage)
        self.input_fixingbar = ElementInput(page=self, locator=loc.LocatorsPageSessionCustom.input_fixingbar)
        self.button_start = ElementButton(page=self, locator=loc.LocatorsPageSessionCustom.button_start)

    def start(self):
        self.input_market.val = 'Russian shares'
        self.input_ticker.val = 'SBER'
        self.input_timeframe.val = '5'
        self.input_barsnumber.val = '50'
        self.input_timelimit.val = '120'
        self.input_date.last_workday()
        self.input_iterations.val = '5'
        self.input_slippage.val = '0.1'
        self.input_fixingbar.val = '15'
        self.button_start.click()


class PageSessionPreset(PageBase):
    """Page for waiting before preset session"""

    title = 'Start new training session'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page Session Preseted>'

    def __init__(self, driver):
        """Page setup"""
        super().__init__(driver)

    def wait_for_start(self):
        """Wait until session has started"""
        self.wait.until(EC.title_contains(PageDecision.title))


class PageDecision(PageBase):
    """Search results page action methods come here"""

    title = 'Make your decisions'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page Decision>'

    def __init__(self, driver):
        """Page setup"""
        super().__init__(driver)
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

    def no_action(self):
        """Decision has not made - Skip"""
        # Wait until url has changed
        url = self.driver.current_url
        self.wait.until(EC.url_changes(url))


class PageResults(PageBase):
    """Search results page action methods come here"""

    title = 'Session’s summary'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page Results>'

    def __init__(self, driver):
        """Page setup"""
        super().__init__(driver)
        self.button_go_to_scoreboard = ElementButton(page=self, locator=loc.LocatorsPageResults.button_go_to_scoreboard)
        self.button_start_new_session = ElementButton(page=self, locator=loc.LocatorsPageResults.button_start_new_session)

    def go_to_scoreboard(self):
        """Press button with link to scoreboard"""
        self.button_go_to_scoreboard.click()

    def start_new_session(self):
        """Press button with link to scoreboard"""
        self.button_start_new_session.click()


class PageScoreboard(PageBase):
    """Search results page action methods come here"""

    title = 'Scoreboard'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page Scoreboard>'

    def __init__(self, driver):
        """Page setup"""
        super().__init__(driver)
        self.button_mode_custom = ElementButton(page=self, locator=loc.LocatorsPageScoreboard.button_mode_custom)
        self.button_mode_classic = ElementButton(page=self, locator=loc.LocatorsPageScoreboard.button_mode_classic)
        self.button_mode_blitz = ElementButton(page=self, locator=loc.LocatorsPageScoreboard.button_mode_blitz)
        self.button_mode_crypto = ElementButton(page=self, locator=loc.LocatorsPageScoreboard.button_mode_crypto)

    def select_mode(self, mode):
        """Select mode by clicking mode button"""
        button_to_click = {
            'custom': self.button_mode_custom,
            'classic': self.button_mode_classic,
            'blitz': self.button_mode_blitz,
            'crypto': self.button_mode_crypto
        }
        button_to_click[mode].click()
        # Wait until url has changed
        self.wait.until(EC.url_contains(mode))