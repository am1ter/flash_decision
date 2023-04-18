import unittest

import e2e.config as cfg
from e2e.modules import backend_functions as backend
from e2e.modules import frontend_pages as frontend


class TestBackend(unittest.TestCase):
    """API smoke tests"""

    @staticmethod
    def test_is_api_up() -> None:
        """Test: Backend API is up"""
        url = cfg.URL_BACKEND + "/check-backend"
        resp = backend.send_request("get", url)
        assert "errors" not in resp, "API is down"

    @staticmethod
    def test_is_db_up() -> None:
        """Test: Connection between backend and db is up"""
        url = cfg.URL_BACKEND + "/check-db"
        resp = backend.send_request("get", url)
        assert "errors" not in resp, "API is down"
        assert resp["data"]["isDbUp"], "Database is down"


class TestFrontend(unittest.TestCase):
    """Complex test (standart pattern)"""

    def _go_to_page(self, page: str) -> None:
        """Define URL of the main page"""
        assert frontend.PageBase.driver, "Driver is not set up"
        url = cfg.URL_FRONTEND + page
        frontend.PageBase.driver.get(url)

    def _cleanup_test_results(self) -> None:
        """Clean results of previous tests from db"""
        url = cfg.URL_BACKEND + "/tests-cleanup"
        resp = backend.send_request("delete", url)
        assert "errors" not in resp, "Test results cleanup failed"

    def setUp(self) -> None:
        """Setup chrome driver and go to main page"""
        TestBackend.test_is_db_up()
        frontend.PageBase.setup_driver()
        self._go_to_page("/")

    def test_is_frontend_up(self) -> None:
        """Test: Main page loaded correctly"""
        frontend.PageLogin()

    def test_login_via_form_correct(self) -> None:
        """Test: try to login with correct credentials"""
        frontend.PageLogin().login_form(email=cfg.USER_TEST_EMAIL, password=cfg.USER_TEST_PASS)
        frontend.PageSession()

    def test_login_via_form_incorrect(self) -> None:
        """Test: try to login with incorrect credentials"""
        frontend.PageLogin().login_form(email=cfg.USER_WRONG_EMAIL, password=cfg.USER_WRONG_PASS)
        frontend.PageLogin().check_error_message()

    def test_login_via_demo_button(self) -> None:
        """Test: try to login with demo button"""
        frontend.PageLogin().login_demo_button()
        frontend.PageSession()

    def test_logout(self) -> None:
        """Test: try to login with demo button"""
        self.test_login_via_form_correct()
        frontend.PageSession().logout()
        frontend.PageLogin()

    def test_signup_correct(self) -> None:
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
        frontend.PageSignup().sign_up(
            email=cfg.USER_SIGNUP_EMAIL,
            name=cfg.USER_SIGNUP_NAME,
            password=cfg.USER_SIGNUP_PASS,
        )
        # On page Session - logout
        frontend.PageSession().logout()
        # On page Login - login with new user credentials
        frontend.PageLogin().login_form(email=cfg.USER_SIGNUP_EMAIL, password=cfg.USER_SIGNUP_PASS)
        # Delete created test user
        self._cleanup_test_results()

    def test_signup_incorrect(self) -> None:
        """Test: try to create new user (delete it when test passed)"""
        # On page Login
        frontend.PageLogin().go_to_signup()
        # On page Signup - try to create new user with invalid creds
        frontend.PageSignup().sign_up(
            email=cfg.USER_WRONG_EMAIL,
            name=cfg.USER_WRONG_NAME,
            password=cfg.USER_WRONG_PASS,
        )
        frontend.PageSignup().check_error_messages(check="invalid")
        frontend.PageSignup().go_back_to_login()
        # On page Login
        frontend.PageLogin().go_to_signup()
        # On page Signup - try to create new user with already taken email
        frontend.PageSignup().sign_up(
            email=cfg.USER_TEST_EMAIL,
            name=cfg.USER_TEST_NAME,
            password=cfg.USER_TEST_PASS,
        )
        frontend.PageSignup().check_error_messages(check="taken")

    def test_custom_session(self) -> None:
        """Test: start new custom session, make decisions, look at results, go to scoreboard"""
        # On page Login
        self.test_login_via_form_correct()
        # Select mode on the Session page
        frontend.PageSession().select_mode(mode="custom")
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

    def test_classic_session(self) -> None:
        """Test: start new classic session, make decisions, look at results, start new session, go back to results"""
        # On page Login
        self.test_login_via_form_correct()
        # Select mode on the Session page
        frontend.PageSession().select_mode(mode="classic")
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
        frontend.PageSession().go_to_page("decision")
        # On page Results
        frontend.PageResults()

    def test_blitz_session(self) -> None:
        """Test: start new blitz session, make decisions, skip one decision by waiting, look at results"""
        # On page Login
        self.test_login_via_form_correct()
        # Select mode on the Session page
        frontend.PageSession().select_mode(mode="blitz")
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

    def test_crypto_session(self) -> None:
        """Test: start new blitz session, make decision, look at results"""
        # On page Login
        self.test_login_via_form_correct()
        # Select mode on the Session page
        frontend.PageSession().select_mode(mode="crypto")
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

    def test_scoreboard(self) -> None:
        """Test: go to scoreboard, switch between modes"""
        # On page Login
        self.test_login_via_form_correct()
        # Select mode on the Session page
        frontend.PageSession().go_to_page(page="scoreboard")
        # On page Scoreboard page
        frontend.PageScoreboard().select_mode(mode="classic")
        frontend.PageScoreboard().select_mode(mode="blitz")
        frontend.PageScoreboard().select_mode(mode="crypto")
        frontend.PageScoreboard().select_mode(mode="custom")

    def test_page_refreshes(self) -> None:
        """Test: try to reload every page"""
        # On page Login
        frontend.PageLogin().refresh_page()
        frontend.PageLogin().go_to_signup()
        # On page Signup
        frontend.PageSignup().refresh_page()
        frontend.PageSignup().go_back_to_login()
        # On page Login
        frontend.PageLogin().login_form(email=cfg.USER_TEST_EMAIL, password=cfg.USER_TEST_PASS)
        # On page Session
        frontend.PageSession().refresh_page()
        frontend.PageSession().select_mode(mode="custom")
        # On page Session Custom
        frontend.PageSessionCustom().refresh_page()
        frontend.PageSessionCustom().go_to_page("session")
        frontend.PageSession().select_mode(mode="classic")
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
        frontend.PageScoreboard().select_mode(mode="blitz")
        frontend.PageScoreboard().refresh_page()
        frontend.PageScoreboard().select_mode(mode="custom")

    def tearDown(self) -> None:
        if frontend.PageBase.driver:
            frontend.PageBase.driver.close()


if __name__ == "__main__":
    unittest.main()
