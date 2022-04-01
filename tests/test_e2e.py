import pages as pages

import unittest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests as r


class TestBackend(unittest.TestCase):
    """Smoke API tests"""
    def _get_api_url(self):
        """Get app url"""
        if os.environ.get('URL_BACKEND'):
            url = os.environ.get('URL_BACKEND')
        else:
            url = "http://localhost:8001"
        return url

    def test_is_api_up(self):
        """Test: Backend API is up"""
        url = self._get_api_url() + '/check-backend'
        try:
            resp = r.get(url)
            if resp.status_code != 200:
                return self.fail(resp.text)
        except r.exceptions.ConnectionError as e:
            self.fail('No response from API: ' + str(e))

    def test_is_db_up(self):
        """Test: Connection between backend and db is up"""
        url = self._get_api_url() + '/check-db'
        try:
            resp = r.get(url)
            if resp.status_code != 200:
                return self.fail(resp.text)
        except r.exceptions.ConnectionError as e:
            self.fail('No response from API: ' + str(e))


class TestFrontend(unittest.TestCase):
    """Complex test (standart pattern)"""

    def _go_to_page(self, page):
        if os.environ.get('URL_FRONTEND'):
            url = os.environ.get('URL_FRONTEND') + page
        else:
            url = "http://localhost:8000" + page
        self.driver.get(url)

    def _cleanup_test_results(self):
        """Clean results of previous tests from db"""
        url = TestBackend._get_api_url(None) + '/cleanup-tests-results'
        print(f'Results cleaned up: ' + url)
        try:
            resp = r.post(url)
            if resp.status_code != 200:
                return self.fail(resp.text)
        except r.exceptions.ConnectionError as e:
            self.fail('No response from API: ' + str(e))

    def setUp(self):
        """Setup chrome driver with webdriver service"""
        print('setUp')
        chromeService = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("--window-size=1920,1080")
        # options.add_argument("--start-maximized")
        options.add_argument('--disable-translate')
        options.add_argument('--lang=en-US')
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(service=chromeService, options=options)
        self._go_to_page('/')

    def test_is_frontend_up(self):
        """Test: Main page loaded correctly"""
        print('test_is_frontend_up')
        page_start = pages.PageLogin(self.driver)
        assert page_start.is_page_loaded(), "Frontend loading has been failed"

    def test_login_via_form_correct(self):
        """Test: try to login with correct credentials"""
        page_login = pages.PageLogin(self.driver)
        page_login.login_via_form(email='demo@alekseisemenov.ru', password='demo')
        page_session = pages.PageSession(self.driver)
        assert page_session.is_page_loaded(), "Login failed: Session page hasn't been loaded"

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

    def test_logout(self):
        """Test: try to login with demo button"""
        self.test_login_via_form_correct()
        page_session = pages.PageSession(self.driver)
        page_session.logout()
        page_login = pages.PageLogin(self.driver)

    def test_signup_correct(self):
        """Test: try to create new user (delete it when test passed)"""
        # Delete previous created test user
        self._cleanup_test_results()
        # Go to login page
        page_login = pages.PageLogin(self.driver)
        # Test: go back button
        page_login.go_to_signup()
        page_signup = pages.PageSignup(self.driver)
        page_signup.go_back()
        page_login = pages.PageLogin(self.driver)
        # Test sign up
        page_login.go_to_signup()
        page_signup = pages.PageSignup(self.driver)
        page_signup.sign_up(email='test@alekseisemenov.ru', name='test', password='uc8a&Q!W')
        page_session = pages.PageSession(self.driver)
        # Logout
        page_session.logout()
        # Login with new user credentials
        page_login = pages.PageLogin(self.driver)
        page_login.login_via_form(email='test@alekseisemenov.ru', password='uc8a&Q!W')

    def test_custom_session(self):
        """Test: start new session"""
        # On page Login
        self.test_login_via_form_correct()
        # On page Session
        page_session = pages.PageSession(self.driver)
        page_session.start_custom_session()
        # On page Decision
        page_decision = pages.PageDecision(self.driver)
        page_decision.action_sell()
        page_decision.action_skip()
        page_decision.action_buy()
        page_decision.action_sell()
        page_decision.action_buy()
        # On page Results
        page_results = pages.PageResults(self.driver)
        page_results.go_to_scoreboard()
        # On page Scoreboard page
        page_scoreboard = pages.PageScoreboard(self.driver)

    def tearDown(self):
        self.driver.close()

if __name__ == '__main__':
    unittest.main()