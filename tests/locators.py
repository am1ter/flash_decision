from selenium.webdriver.common.by import By


class LocatorsPageLogin(object):
    """Locators for page_Login"""
    input_email = (By.ID, 'input-email')
    input_password = (By.ID, 'input-password')
    button_signin = (By.ID, 'button-signin')
    button_signup = (By.ID, 'button-signup')
    button_signin_demo = (By.ID, 'button-signin-demo')


class LocatorsPageSession(object):
    """Locators for page_Session"""
    button_logout = (By.ID, 'button-logout')
    button_start = (By.ID, 'button-start')