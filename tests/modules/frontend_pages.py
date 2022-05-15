import config as cfg
from modules import frontend_locators as loc
from modules.frontend_elements import ElementInput, ElementButton, ElementDatePicker

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class PageBase:
    """Base class to initialize the base page that will be called from all pages"""

    def __init__(self) -> None:
        # Basic setup
        self._set_wait_timer(cfg.WAIT_TIMEOUT)
        # Check if page loaded
        self.is_page_loaded()
        # Setup buttons
        self.button_logout = ElementButton(self, loc.LocPageBase.button_logout)
        self.button_menu_session = ElementButton(self, loc.LocPageBase.button_menu_session)
        self.button_menu_decision = ElementButton(self, loc.LocPageBase.button_menu_decision)
        self.button_menu_scoreboard = ElementButton(self, loc.LocPageBase.button_menu_scoreboard)

    def _set_wait_timer(self, timeout: int) -> None:
        """Reset webdriver wait timer with new timeout (seconds) value"""
        # Delete existed wait timer and replace it with new one
        try:
            del self.wait
        except AttributeError:
            pass
        self.wait = WebDriverWait(self.driver, timeout)

    @classmethod
    def setup_driver(cls) -> None:
        """Setup chrome driver with webdriver service"""
        chromeService = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.headless = cfg.DRIVER_HEADLESS
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--disable-translate')
        options.add_argument('--lang=en-US')
        options.add_argument('--no-sandbox')
        if cfg.DRIVER_HEADLESS and cfg.DRIVER_START_MAXIMIZED:
            options.add_argument("--start-maximized")
        cls.driver = webdriver.Chrome(service=chromeService, options=options)

    def is_page_loaded(self) -> None:
        """Verifies that the page is loaded"""

        # Wait until page is loaded
        self.wait.until(
            method=EC.invisibility_of_element_located(loc.LocPageBase.div_errors),
            message=f'Page is not loaded. Errors on the page: {self.driver.current_url}',
        )
        self.wait.until(
            method=EC.title_contains(self.title),
            message=f'Unexpected page title. No `{self.title}` in `{self.driver.title}`',
        )
        self.wait.until(
            method=EC.visibility_of_element_located(loc.LocPageBase.div_footer),
            message=f'No footer found on the page: {self.driver.current_url}',
        )
        self.wait.until(
            method=EC.invisibility_of_element_located(loc.LocPageBase.div_loader),
            message=f'Loading did not finish: {self.driver.current_url}',
        )

        # Make checks
        fails = []
        no_errors = len(self.driver.find_elements(*loc.LocPageBase.div_errors)) == 0
        is_page_length_enough = len(self.driver.page_source) > 100
        is_url_correct = 'undefined' not in self.driver.current_url
        no_undefined = 'undefined' not in self.driver.page_source.lower()

        if no_errors == False:
            fails.append('Errors displayed on the page')
        elif is_page_length_enough == False:
            fails.append('Page length <= 100 symbols')
        elif is_url_correct == False:
            fails.append('URL is incorrect. There is `undefined` in the URL.')
        elif no_undefined == False:
            fails.append('There are undefined values on the page')

        assert len(fails) == 0, f'Error during {self} loading: {fails}'

    def refresh_page(self) -> None:
        """Press F5 to reload page"""
        self.driver.refresh()
        # Check if page loaded
        self.is_page_loaded()

    def logout(self) -> None:
        """Click on the logout button"""
        self.button_logout.click()

    def go_to_page(self, page: str) -> None:
        """Click on the logout button"""
        menu_to_click = {
            'session': self.button_menu_session,
            'decision': self.button_menu_decision,
            'scoreboard': self.button_menu_scoreboard,
        }
        menu_to_click[page].click()


class PageLogin(PageBase):
    """Login page"""

    title = 'Login'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page Login>'

    def __init__(self) -> None:
        """Page setup"""
        super().__init__()
        self.input_email = ElementInput(self, loc.LocPageLogin.input_email)
        self.input_password = ElementInput(self, loc.LocPageLogin.input_password)
        self.button_signin = ElementButton(self, loc.LocPageLogin.button_signin)
        self.button_signup = ElementButton(self, loc.LocPageLogin.button_signup)
        self.button_signin_demo = ElementButton(self, loc.LocPageLogin.button_signin_demo)

    def login_form(self, email: str, password: str) -> None:
        """Send email and password with html form"""
        self.input_email.val = email
        self.input_password.val = password
        self.button_signin.click()

    def login_demo_button(self) -> None:
        """Send email and password with html form"""
        self.button_signin_demo.click()

    def go_to_signup(self) -> None:
        """Send email and password with html form"""
        self.button_signup.click()

    def check_error_message(self) -> None:
        """Check if there is an alert on the page"""
        check_passed = 'incorrect email or password' in self.driver.page_source.lower()
        assert check_passed, 'Login with incorrect credentials has failed'


class PageSignup(PageBase):
    """Signup page"""

    title = 'Create account'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page Signup>'

    def __init__(self) -> None:
        """Page setup"""
        super().__init__()
        self.input_email = ElementInput(self, loc.LocPageSignup.input_email)
        self.input_name = ElementInput(self, loc.LocPageSignup.input_name)
        self.input_password = ElementInput(self, loc.LocPageSignup.input_password)
        self.button_signup = ElementButton(self, loc.LocPageSignup.button_signup)
        self.button_go_back = ElementButton(self, loc.LocPageSignup.button_go_back)

    def go_back_to_login(self) -> None:
        """Click on the back button"""
        self.button_go_back.click()

    def sign_up(self, email: str, name: str, password: str) -> None:
        """Click on the back button"""
        self.input_email.val = email
        self.input_name.val = name
        self.input_password.val = password
        self.button_signup.click()

    def check_error_messages(self, check: str) -> None:
        """Check if there is an alert on the page"""
        msg_email_taken = 'Email has already been taken'.lower()
        msg_email_invalid = 'Please enter a valid email'.lower()
        msg_name_invalid = 'Please enter your name'.lower()
        msg_password_invalid = 'Password must contain at least 6 symbols'.lower()
        errors = []
        for msg in (msg_email_invalid, msg_email_taken, msg_name_invalid, msg_password_invalid):
            if msg in self.driver.page_source.lower():
                errors.append(msg)
        if check == 'invalid':
            invalid_list = [msg_email_invalid, msg_name_invalid, msg_password_invalid]
            assert invalid_list == errors, 'Check sign up with invalid credentials failed'
        elif check == 'invalid':
            taken_list = [msg_email_taken]
            assert taken_list == errors, 'Check sign up with already taken email failed'


class PageSession(PageBase):
    """Session page"""

    title = 'Start new training session'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page SessionCustom>'

    def __init__(self) -> None:
        """Page setup"""
        super().__init__()
        self.button_mode_custom = ElementButton(self, loc.LocPageSession.button_mode_custom)
        self.button_mode_classic = ElementButton(self, loc.LocPageSession.button_mode_classic)
        self.button_mode_blitz = ElementButton(self, loc.LocPageSession.button_mode_blitz)
        self.button_mode_crypto = ElementButton(self, loc.LocPageSession.button_mode_crypto)

    def select_mode(self, mode: str) -> None:
        """Select mode by clicking mode button"""
        button_to_click = {
            'custom': self.button_mode_custom,
            'classic': self.button_mode_classic,
            'blitz': self.button_mode_blitz,
            'crypto': self.button_mode_crypto,
        }
        button_to_click[mode].click()


class PageSessionCustom(PageBase):
    """Custom Session page"""

    title = 'Start new training session'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page SessionCustom>'

    def __init__(self) -> None:
        """Page setup"""
        super().__init__()
        self.input_market = ElementInput(self, loc.LocPageSessionCustom.input_market)
        self.input_ticker = ElementInput(self, loc.LocPageSessionCustom.input_ticker)
        self.input_timeframe = ElementInput(self, loc.LocPageSessionCustom.input_timeframe)
        self.input_barsnumber = ElementInput(self, loc.LocPageSessionCustom.input_barsnumber)
        self.input_timelimit = ElementInput(self, loc.LocPageSessionCustom.input_timelimit)
        self.input_date = ElementDatePicker(self, loc.LocPageSessionCustom.input_date)
        self.input_iterations = ElementInput(self, loc.LocPageSessionCustom.input_iterations)
        self.input_slippage = ElementInput(self, loc.LocPageSessionCustom.input_slippage)
        self.input_fixingbar = ElementInput(self, loc.LocPageSessionCustom.input_fixingbar)
        self.button_start = ElementButton(self, loc.LocPageSessionCustom.button_start)

    def start(self) -> None:
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

    def __init__(self) -> None:
        """Page setup"""
        super().__init__()

    def wait_for_start(self) -> None:
        """Wait until session is started"""
        self.wait.until(method=EC.title_contains(PageDecision.title), message='Session start error')


class PageDecision(PageBase):
    """Search results page action methods come here"""

    title = 'Make your decisions'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page Decision>'

    def __init__(self) -> None:
        """Page setup"""
        super().__init__()
        self.button_sell = ElementButton(self, loc.LocPageDecision.button_sell)
        self.button_skip = ElementButton(self, loc.LocPageDecision.button_skip)
        self.button_buy = ElementButton(self, loc.LocPageDecision.button_buy)

    def action_sell(self) -> None:
        """Press action button"""
        self.button_sell.click()

    def action_skip(self) -> None:
        """Press action button"""
        self.button_skip.click()

    def action_buy(self) -> None:
        """Press action button"""
        self.button_buy.click()

    def no_action(self) -> None:
        """Decision has not made - Skip"""
        # Wait until url has changed
        url = self.driver.current_url
        self.wait.until(method=EC.url_changes(url), message='Auto skip failed')


class PageResults(PageBase):
    """Search results page action methods come here"""

    title = 'Session’s summary'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page Results>'

    def __init__(self) -> None:
        """Page setup"""
        super().__init__()
        self.button_to_scoreboard = ElementButton(self, loc.LocPageResults.button_to_scoreboard)
        self.button_new_session = ElementButton(self, loc.LocPageResults.button_new_session)

    def go_to_scoreboard(self) -> None:
        """Press button with link to scoreboard"""
        self.button_to_scoreboard.click()

    def start_new_session(self) -> None:
        """Press button with link to scoreboard"""
        self.button_new_session.click()


class PageScoreboard(PageBase):
    """Search results page action methods come here"""

    title = 'Scoreboard'

    def __repr__(self) -> str:
        """Return formated object name"""
        return f'<Page Scoreboard>'

    def __init__(self) -> None:
        """Page setup"""
        super().__init__()
        self.button_mode_custom = ElementButton(self, loc.LocPageScoreboard.button_mode_custom)
        self.button_mode_classic = ElementButton(self, loc.LocPageScoreboard.button_mode_classic)
        self.button_mode_blitz = ElementButton(self, loc.LocPageScoreboard.button_mode_blitz)
        self.button_mode_crypto = ElementButton(self, loc.LocPageScoreboard.button_mode_crypto)

    def select_mode(self, mode: str) -> None:
        """Select mode by clicking mode button"""
        button_to_click = {
            'custom': self.button_mode_custom,
            'classic': self.button_mode_classic,
            'blitz': self.button_mode_blitz,
            'crypto': self.button_mode_crypto,
        }
        button_to_click[mode].click()

        # Wait until url has changed
        self.wait.until(method=EC.url_contains(mode), message='Mode selection failed')
