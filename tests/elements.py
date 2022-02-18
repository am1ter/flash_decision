from selenium.webdriver.support import expected_conditions as EC


class ElementBase(object):
    """Base element class"""
    def __init__(self, page, locator) -> None:
        """Element setup"""
        self.page = page
        self.driver = page.driver
        self.locator = locator


class ElementInput(ElementBase):
    """Base page class for inputs. Using custom setters and getters (val) for interactions with inputs"""

    def __init__(self, page, locator) -> None:
        """Init"""
        ElementBase.__init__(self, page, locator)
        self.element = self.page.wait.until(EC.element_to_be_clickable(self.locator))
        self._val = None

    @property
    def val(self):
        """Custom getter: get the value of input as text"""
        self._val = self.element
        return self._val.get_attribute('value')

    @val.setter
    def val(self, value):
        """Custom setter: send keys as assignation to text _val attribute"""
        self._val = self.element
        self._val.clear()
        self._val.send_keys(value)


class ElementButton(ElementBase):
    """Base page class for buttons"""

    def __init__(self, page, locator) -> None:
        """Element setup"""
        ElementBase.__init__(self, page, locator)
        self.element = self.page.wait.until(EC.element_to_be_clickable(self.locator))
    
    def click(self):
        """Click on the button"""
        self.element.click()
