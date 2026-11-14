
from datetime import datetime

from src.browser.saucedemo_login_page import SauceDemoLoginPage


def log_step(message):
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{current_time}] {message}", flush=True)


def capture(login_page, step_name):
    login_page.screenshots.capture("login", step_name)


def open_login_page(login_page):
    log_step("Opening SauceDemo website...")
    login_page.open()
    login_page.page.wait_for_timeout(1000)
    capture(login_page, "login_page_loaded")


def capture_error(login_page):
    login_page.page.locator("[data-test='error']").wait_for(
        state="visible",
        timeout=5000
    )
    capture(login_page, "login_error_displayed")


def test_valid_login(page):
    login_page = SauceDemoLoginPage(page)

    open_login_page(login_page)

    log_step("Entering valid username...")
    login_page.enter_username("standard_user")

    log_step("Entering valid password...")
    login_page.enter_password("secret_sauce")
    capture(login_page, "valid_credentials_entered")

    log_step("Clicking Login...")
    login_page.click_login()
    page.wait_for_url("**/inventory.html", timeout=10000)

    assert login_page.is_login_successful()
    capture(login_page, "login_successful")

    log_step("VALID LOGIN TEST PASSED!")


def test_invalid_username(page):
    login_page = SauceDemoLoginPage(page)

    open_login_page(login_page)

    login_page.enter_username("wrong_user")
    login_page.enter_password("secret_sauce")
    capture(login_page, "invalid_username_credentials_entered")

    login_page.click_login()

    expected = (
        "Epic sadface: Username and password do not match "
        "any user in this service"
    )
    actual = login_page.get_error_message()

    assert login_page.is_error_visible()
    assert actual == expected

    capture_error(login_page)
    log_step("INVALID USERNAME TEST PASSED!")


def test_invalid_password(page):
    login_page = SauceDemoLoginPage(page)

    open_login_page(login_page)

    login_page.enter_username("standard_user")
    login_page.enter_password("wrong_password")
    capture(login_page, "invalid_password_credentials_entered")

    login_page.click_login()

    expected = (
        "Epic sadface: Username and password do not match "
        "any user in this service"
    )
    actual = login_page.get_error_message()

    assert login_page.is_error_visible()
    assert actual == expected

    capture_error(login_page)
    log_step("INVALID PASSWORD TEST PASSED!")


def test_empty_username(page):
    login_page = SauceDemoLoginPage(page)

    open_login_page(login_page)

    login_page.enter_password("secret_sauce")
    capture(login_page, "empty_username_password_entered")

    login_page.click_login()

    expected = "Epic sadface: Username is required"
    actual = login_page.get_error_message()

    assert login_page.is_error_visible()
    assert actual == expected

    capture_error(login_page)
    log_step("EMPTY USERNAME TEST PASSED!")


def test_empty_password(page):
    login_page = SauceDemoLoginPage(page)

    open_login_page(login_page)

    login_page.enter_username("standard_user")
    capture(login_page, "empty_password_username_entered")

    login_page.click_login()

    expected = "Epic sadface: Password is required"
    actual = login_page.get_error_message()

    assert login_page.is_error_visible()
    assert actual == expected

    capture_error(login_page)
    log_step("EMPTY PASSWORD TEST PASSED!")


def test_both_fields_empty(page):
    login_page = SauceDemoLoginPage(page)

    open_login_page(login_page)

    capture(login_page, "both_fields_empty_before_login")

    login_page.click_login()

    expected = "Epic sadface: Username is required"
    actual = login_page.get_error_message()

    assert login_page.is_error_visible()
    assert actual == expected

    capture_error(login_page)
    log_step("BOTH FIELDS EMPTY TEST PASSED!")


def test_locked_out_user(page):
    login_page = SauceDemoLoginPage(page)

    open_login_page(login_page)

    login_page.enter_username("locked_out_user")
    login_page.enter_password("secret_sauce")
    capture(login_page, "locked_out_credentials_entered")

    login_page.click_login()

    expected = "Epic sadface: Sorry, this user has been locked out."
    actual = login_page.get_error_message()

    assert login_page.is_error_visible()
    assert actual == expected

    capture_error(login_page)
    log_step("LOCKED-OUT USER TEST PASSED!")


def test_password_is_masked(page):
    login_page = SauceDemoLoginPage(page)

    open_login_page(login_page)

    login_page.enter_password("secret_sauce")

    is_masked = login_page.is_password_masked()

    assert is_masked is True

    capture(login_page, "password_masking_verified")
    log_step("PASSWORD MASKING TEST PASSED!")
