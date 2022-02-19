from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class ElementBase(object):
    """Base element class"""
    def __init__(self, page, locator) -> None:
        """Element setup"""
        self.page = page
        self.driver = page.driver
        self.locator = locator


class ElementInput(ElementBase):
    """Base element class for inputs. Using custom setters and getters (val) for interactions with inputs"""

    def __init__(self, page, locator) -> None:
        """Init"""
        ElementBase.__init__(self, page, locator)
        self.element = self.page.wait.until(EC.element_to_be_clickable(self.locator))

    @property
    def val(self):
        """Custom getter: get the value of input as text"""
        return self.element.get_attribute('value')

    @val.setter
    def val(self, value):
        """Custom setter: send keys as assignation to text _val attribute"""
        self.element.clear()
        self.element.send_keys(value)


class ElementButton(ElementBase):
    """Base element class for buttons"""

    def __init__(self, page, locator) -> None:
        """Element setup"""
        ElementBase.__init__(self, page, locator)
    
    def click(self):
        """Click on the button"""
        self.element = self.page.wait.until(EC.element_to_be_clickable(self.locator))
        self.element.click()


class ElementDatePicker(ElementBase):
    """Base page class for bootstrap datapicker"""

    def __init__(self, page, locator) -> None:
        """Init"""
        ElementBase.__init__(self, page, locator)
        self.element = self.page.wait.until(EC.element_to_be_clickable(self.locator))

    def last_workday(self):
        """Custom setter: send keys as assignation to text _val attribute"""
        weekday = datetime.today().isoweekday()

        # Activate datetime dropdown
        self.driver.execute_script("arguments[0].click();", self.element)

        # Send keyboard keys without bounding with element (ActionChains)
        actions = ActionChains(self.driver)
        actions.pause(1/8)

        # If it is weekend go to the last workday with ARROW_LEFT key
        if weekday == 6:
            actions.send_keys(Keys.ARROW_LEFT)
        elif weekday == 7:
            actions.send_keys(Keys.ARROW_LEFT)
            actions.send_keys(Keys.ARROW_LEFT)

        # Send keys without bounding with element
        actions.send_keys(Keys.ENTER)
        actions.perform()