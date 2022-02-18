import pages as pages

import unittest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class TestCommon(unittest.TestCase):
    """Complex test (standart pattern)"""

    def _go_to_page(self, page):
        if os.environ.get('FLASH_URL'):
            url = os.environ.get('FLASH_URL') + page
        else:
            url = "http://localhost:8000" + page
        self.driver.get(url)

    def setUp(self):
        """Setup chrome driver with webdriver service"""
        chromeService = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.headless = False
        options.add_argument("--window-size=1920,1080")
        # options.add_argument("--start-maximized")
        options.add_argument('--disable-translate')
        options.add_argument('--lang=en-US')
        self.driver = webdriver.Chrome(service=chromeService, options=options)
        self._go_to_page('/')

    def test_load_start(self):
        """Test: main page loaded correctly"""
        page_start = pages.PageLogin(self.driver)
        assert page_start.is_page_loaded(), "Page loaded incorrectly"
        assert page_start.is_title_matches(), "Webpage title doesn't match"

    def test_login_via_form_correct(self):
        """Test: try to login with correct credentials"""
        page_login = pages.PageLogin(self.driver)
        page_login.login_via_form(email='demo@alekseisemenov.ru', password='demo')
        page_session = pages.PageSession(self.driver)
        assert page_session.is_title_matches(), "Login failed: session page hasn't been loaded"

    def test_login_via_form_incorrect(self):
        """Test: try to login with incorrect credentials"""
        page_login = pages.PageLogin(self.driver)
        page_login.login_via_form(email='wrong@alekseisemenov.ru', password='wrong')
        page_login.has_text_incorrect_creds()

    def test_login_via_demo_button(self):
        """Test: try to login with demo button"""
        page_login = pages.PageLogin(self.driver)
        page_login.login_via_demo_button()
        page_session = pages.PageSession(self.driver)
        assert page_session.is_title_matches(), "Login failed: session page hasn't been loaded"

    def test_logout(self):
        """Test: try to login with demo button"""
        self.test_login_via_demo_button()
        page_session = pages.PageSession(self.driver)
        page_session.logout()
        page_login = pages.PageLogin(self.driver)
        assert page_login.is_title_matches(), "Logout failed: login page hasn't been loaded"

    def tearDown(self):
        self.driver.close()

if __name__ == '__main__':
    unittest.main()