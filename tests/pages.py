from elements import ElementInput, ElementButton
from locators import LocatorsPageLogin, LocatorsPageSession

from selenium.webdriver.support.ui import WebDriverWait


class PageBase:
    """Base class to initialize the base page that will be called from all pages"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)


class PageLogin(PageBase):
    """Login page"""

    def __init__(self, driver):
        """Page setup"""
        PageBase.__init__(self, driver=driver)
        self.input_email = ElementInput(page=self, locator=LocatorsPageLogin.input_email)
        self.input_password = ElementInput(page=self, locator=LocatorsPageLogin.input_password)
        self.button_signin = ElementButton(page=self, locator=LocatorsPageLogin.button_signin)
        self.button_signup = ElementButton(page=self, locator=LocatorsPageLogin.button_signup)
        self.button_signin_demo = ElementButton(page=self, locator=LocatorsPageLogin.button_signin_demo)

    def is_page_loaded(self):
        """Verifies that the page is loaded"""
        return len(self.driver.page_source) > 100

    def is_title_matches(self):
        """Verifies that the hardcoded text appears in page title"""
        return 'Flash decision' in self.driver.title

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
    """Search results page action methods come here"""

    def __init__(self, driver):
        """Page setup"""
        PageBase.__init__(self, driver=driver)
        self.button_logout = ElementButton(page=self, locator=LocatorsPageSession.button_logout)
        self.button_start = ElementButton(page=self, locator=LocatorsPageSession.button_start)

    def is_title_matches(self):
        """Verifies that the hardcoded text appears in page title"""
        return "Start new training session" in self.driver.title

    def logout(self):
        """Click on the logout button"""
        self.button_logout.click()