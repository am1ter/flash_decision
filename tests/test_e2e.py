import config as cfg
import backend_functions as backend
import frontend_pages as frontend

import unittest


class TestBackend(unittest.TestCase):
    """Smoke API tests"""

    def test_is_api_up(self):
        """Test: Backend API is up"""
        url = cfg.URL_BACKEND + '/check-backend'
        resp = backend.send_request(url)
        assert resp == True, resp

    def test_is_db_up(self):
        """Test: Connection between backend and db is up"""
        url = cfg.URL_BACKEND + '/check-db'
        resp = backend.send_request(url)
        assert resp == True, resp


class TestFrontend(unittest.TestCase):
    """Complex test (standart pattern)"""

    def _go_to_page(self, page):
        """Define URL of the main page"""
        url = cfg.URL_FRONTEND + page
        frontend.PageBase.driver.get(url)

    def _cleanup_test_results(self):
        """Clean results of previous tests from db"""
        url = cfg.URL_BACKEND + '/cleanup-tests-results'
        resp = backend.send_request(url)
        assert resp == True, resp

    def setUp(self):
        """Setup chrome driver and go to main page"""
        frontend.PageBase.setup_driver()
        self._go_to_page('/')

    def test_is_frontend_up(self):
        """Test: Main page loaded correctly"""
        frontend.PageLogin()

    def test_login_via_form_correct(self):
        """Test: try to login with correct credentials"""
        frontend.PageLogin().login_via_form(email='test@alekseisemenov.ru', password='uc8a&Q!W')
        frontend.PageSession()

    def test_login_via_form_incorrect(self):
        """Test: try to login with incorrect credentials"""
        frontend.PageLogin().login_via_form(email='wrong@alekseisemenov.ru', password='wrong')
        frontend.PageLogin().check_error_message()

    def test_login_via_demo_button(self):
        """Test: try to login with demo button"""
        frontend.PageLogin().login_via_demo_button()
        frontend.PageSession()

    def test_logout(self):
        """Test: try to login with demo button"""
        self.test_login_via_form_correct()
        frontend.PageSession().logout()
        frontend.PageLogin()

    def test_signup_correct(self):
        """Test: try to create new user (delete it when test passed)"""
        # Delete previous created test user if exists
        self._cleanup_test_results()
        # On page Login
        frontend.PageLogin().go_to_signup()
        # On page Signup
        frontend.PageSignup().go_back_to_login()
        # On page Login
        frontend.PageLogin().go_to_signup()
        # On page Signup - create new user
        frontend.PageSignup().sign_up(email='test-signup@alekseisemenov.ru', name='test-signup', password='uc8a&Q!W')
        # On page Session - logout
        frontend.PageSession().logout()
        # On page Login - login with new user credentials
        frontend.PageLogin().login_via_form(email='test-signup@alekseisemenov.ru', password='uc8a&Q!W')
        # Delete created test user
        self._cleanup_test_results()

    def test_signup_incorrect(self):
        """Test: try to create new user (delete it when test passed)"""
        # On page Login
        frontend.PageLogin().go_to_signup()
        # On page Signup - try to create new user with invalid creds
        frontend.PageSignup().sign_up(email='wrong', name='', password='wrong')
        frontend.PageSignup().check_error_messages(check='invalid')
        frontend.PageSignup().go_back_to_login()
        # On page Login
        frontend.PageLogin().go_to_signup()
        # On page Signup - try to create new user with already taken email
        frontend.PageSignup().sign_up(email='test@alekseisemenov.ru', name='test', password='uc8a&Q!W')
        frontend.PageSignup().check_error_messages(check='taken')


    def test_custom_session(self):
        """Test: start new custom session, make decisions, look at results, go to scoreboard"""
        # On page Login
        self.test_login_via_form_correct()
        # Select mode on the Session page
        frontend.PageSession().select_mode(mode='custom')
        # On page Session Custom
        frontend.PageSessionCustom().start()
        # On page Decision
        frontend.PageDecision().action_buy()
        frontend.PageDecision().action_sell()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        # On page Results
        frontend.PageResults().go_to_scoreboard()
        # On page Scoreboard page
        frontend.PageScoreboard()

    def test_classic_session(self):
        """Test: start new classic session, make decisions, look at results, start new session, go back to results"""
        # On page Login
        self.test_login_via_form_correct()
        # Select mode on the Session page
        frontend.PageSession().select_mode(mode='classic')
        # On page Session Classic
        frontend.PageSessionPreset().wait_for_start()
        # On page Decision
        frontend.PageDecision().action_buy()
        frontend.PageDecision().action_sell()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        # On page Results
        frontend.PageResults().start_new_session()
        # On the Session page
        frontend.PageSession().go_to_page('decision')
        # On page Results
        frontend.PageResults()

    def test_blitz_session(self):
        """Test: start new blitz session, make decisions, skip one decision by waiting, look at results"""
        # On page Login
        self.test_login_via_form_correct()
        # Select mode on the Session page
        frontend.PageSession().select_mode(mode='blitz')
        # On page Session Classic
        frontend.PageSessionPreset().wait_for_start()
        # On page Decision
        frontend.PageDecision().action_buy()
        frontend.PageDecision().action_sell()
        frontend.PageDecision().no_action()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        # On page Results
        frontend.PageResults()

    def test_crypto_session(self):
        """Test: start new blitz session, make decision, look at results"""
        # On page Login
        self.test_login_via_form_correct()
        # Select mode on the Session page
        frontend.PageSession().select_mode(mode='crypto')
        # On page Session Classic
        frontend.PageSessionPreset().wait_for_start()
        # On page Decision
        frontend.PageDecision().action_sell()
        frontend.PageDecision().action_buy()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        # On page Results
        frontend.PageResults()

    def test_scoreboard(self):
        """Test: go to scoreboard, switch between modes"""
        # On page Login
        self.test_login_via_form_correct()
        # Select mode on the Session page
        frontend.PageSession().go_to_page(page='scoreboard')
        # On page Scoreboard page
        frontend.PageScoreboard().select_mode(mode='classic')
        frontend.PageScoreboard().select_mode(mode='blitz')
        frontend.PageScoreboard().select_mode(mode='crypto')
        frontend.PageScoreboard().select_mode(mode='custom')

    def test_page_refreshes(self):
        """Test: try to reload every page"""
        # On page Login
        frontend.PageLogin().refresh_page()
        frontend.PageLogin().go_to_signup()
        # On page Signup
        frontend.PageSignup().refresh_page()
        frontend.PageSignup().go_back_to_login()
        # On page Login
        frontend.PageLogin().login_via_form(email='test@alekseisemenov.ru', password='uc8a&Q!W')
        # On page Session
        frontend.PageSession().refresh_page()
        frontend.PageSession().select_mode(mode='custom')
        # On page Session Custom
        frontend.PageSessionCustom().refresh_page()
        frontend.PageSessionCustom().go_to_page('session')
        frontend.PageSession().select_mode(mode='classic')
        # On page Session Classic
        frontend.PageSessionPreset().refresh_page()
        # On page Decision
        frontend.PageDecision().action_skip()
        frontend.PageDecision().refresh_page()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().refresh_page()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        frontend.PageDecision().action_skip()
        # On page Results
        frontend.PageResults().refresh_page()
        frontend.PageResults().go_to_scoreboard()
        # On page Scoreboard page
        frontend.PageScoreboard().refresh_page()
        frontend.PageScoreboard().select_mode(mode='blitz')
        frontend.PageScoreboard().refresh_page()
        frontend.PageScoreboard().select_mode(mode='custom')
        
    def tearDown(self):
        frontend.PageBase.driver.close()


if __name__ == '__main__':
    unittest.main()
