
from src.browser.mouse_controller import MouseController
from src.reporting.screenshot_manager import ScreenshotManager


class SauceDemoLoginPage:

    def __init__(self, page):

        self.page = page

        self.mouse = MouseController(page)
        self.screenshots = ScreenshotManager(page)

        self.url = "https://www.saucedemo.com/"

        self.username_field = page.locator("#user-name")
        self.password_field = page.locator("#password")
        self.login_button = page.locator("#login-button")
        self.error_message = page.locator("[data-test='error']")

    # Open login page
    def open(self):

        self.page.goto(self.url)

        self.page.wait_for_load_state("domcontentloaded")

    # Enter username
    def enter_username(self, username):

        self.mouse.click(self.username_field)

        self.username_field.fill(username)

    # Enter password
    def enter_password(self, password):

        self.mouse.click(self.password_field)

        self.password_field.fill(password)

    # Click login button
    def click_login(self):

        self.mouse.click(self.login_button)

        self.page.wait_for_timeout(1500)

    # Complete login
    def login(self, username, password):

        self.enter_username(username)

        self.enter_password(password)

        self.click_login()

    # Read error message
    def get_error_message(self):

        return self.error_message.inner_text()

    # Check error visibility
    def is_error_visible(self):

        return self.error_message.is_visible()

    # Check password masking
    def is_password_masked(self):

        password_type = self.password_field.get_attribute("type")

        return password_type == "password"

    # Check successful login
    def is_login_successful(self):

        return "inventory.html" in self.page.url
