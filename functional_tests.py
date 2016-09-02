from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest


######################################################################
# Selenium functional tests. Not simulations!
######################################################################

class CCTestHomepage(unittest.TestCase):
    """Tests that check features on the homepage."""

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_title(self):
        """When we visit http://localhost:5000/, do we actually get the
        homepage?"""

        self.browser.get("http://localhost:5000/")
        self.assertEqual(self.browser.title, "Crafter's Closet Home")

    def test_login(self):
        """Test whether we can click from the homepage to the login form and
        actually authenticate. We know we've authenticated when we reach the
        user's inventory dashboard.

        NOTE: HTML Currently written w/ prefilled login fields! If you change
        that, update this test.
        """

        self.browser.get("http://localhost:5000/")
        sign_in_link = self.browser.find_element_by_link_text("Sign In")

        sign_in_link.click()

        # Wait until the elements we want to change are actually loaded.
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.presence_of_element_located((By.ID, "username")))

        # Click signin!
        sign_in_button = self.browser.find_element_by_id("signin-btn")
        sign_in_button.click()

        wait.until(EC.presence_of_element_located((By.ID, "inv-table")))


if __name__ == "__main__":
    unittest.main()
