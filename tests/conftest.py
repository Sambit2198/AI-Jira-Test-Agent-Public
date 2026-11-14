
from datetime import datetime
from pathlib import Path
import re

import pytest
from playwright.sync_api import sync_playwright

from src.reporting.excel_reporter import ExcelReporter
from src.reporting.word_reporter import WordReporter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_FOLDER = PROJECT_ROOT / "reports" / "screenshots"


# --------------------------------------------------
# BROWSER FIXTURE
# --------------------------------------------------

@pytest.fixture
def page():

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=False,
            slow_mo=1000,
            args=["--start-maximized"]
        )

        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        yield page

        print("\nTest completed! Browser will close in 10 seconds...")
        page.wait_for_timeout(10000)

        browser.close()


# --------------------------------------------------
# TEST RESULT STORAGE
# --------------------------------------------------

test_results = []
test_start_times = {}


# --------------------------------------------------
# LOGIN TEST CASE DEFINITIONS
# --------------------------------------------------

LOGIN_TEST_CASES = {

    "test_valid_login": {
        "id": "TC_LOGIN_001",
        "title": "Valid User Login",
        "scenario": "Verify successful login with valid credentials.",
    },

    "test_invalid_username": {
        "id": "TC_LOGIN_002",
        "title": "Invalid Username",
        "scenario": "Verify login rejection with an invalid username.",
    },

    "test_invalid_password": {
        "id": "TC_LOGIN_003",
        "title": "Invalid Password",
        "scenario": "Verify login rejection with an invalid password.",
    },

    "test_empty_username": {
        "id": "TC_LOGIN_004",
        "title": "Empty Username",
        "scenario": "Verify validation when username is empty.",
    },

    "test_empty_password": {
        "id": "TC_LOGIN_005",
        "title": "Empty Password",
        "scenario": "Verify validation when password is empty.",
    },

    "test_both_fields_empty": {
        "id": "TC_LOGIN_006",
        "title": "Both Login Fields Empty",
        "scenario": "Verify validation when both fields are empty.",
    },

    "test_locked_out_user": {
        "id": "TC_LOGIN_007",
        "title": "Locked-Out User",
        "scenario": "Verify that a locked-out user cannot log in.",
    },

    "test_password_is_masked": {
        "id": "TC_LOGIN_008",
        "title": "Password Masking",
        "scenario": "Verify that the password field masks its contents.",
    },
}


# --------------------------------------------------
# END-TO-END TEST CASE
# --------------------------------------------------

END_TO_END_TEST_CASES = {

    "test_saucedemo_complete_end_to_end_flow": {
        "id": "TC_E2E_001",
        "title": "SauceDemo Complete End-to-End Flow",
        "scenario": (
            "Verify the complete SauceDemo journey including login, "
            "inventory, product verification, sorting, shopping cart, "
            "checkout, order confirmation and return to inventory."
        ),
    },
}


ALL_TEST_CASES = {
    **LOGIN_TEST_CASES,
    **END_TO_END_TEST_CASES,
}


# --------------------------------------------------
# EXPECTED RESULTS
# --------------------------------------------------

EXPECTED_RESULTS = {

    "test_valid_login":
        "User successfully logs in and reaches the inventory page.",

    "test_invalid_username":
        "Application rejects the invalid username and displays an error.",

    "test_invalid_password":
        "Application rejects the incorrect password and displays an error.",

    "test_empty_username":
        "Application displays the username-required validation message.",

    "test_empty_password":
        "Application displays the password-required validation message.",

    "test_both_fields_empty":
        "Application displays the username-required validation message.",

    "test_locked_out_user":
        "Application prevents the locked-out user from logging in.",

    "test_password_is_masked":
        "Password characters are masked in the password field.",

    "test_saucedemo_complete_end_to_end_flow": (
        "Complete SauceDemo journey is successfully executed, "
        "including login, inventory verification, product sorting, "
        "cart operations, checkout calculations, order confirmation "
        "and return to inventory."
    ),
}


# --------------------------------------------------
# ACTUAL RESULTS
# --------------------------------------------------

ACTUAL_RESULTS = {

    "test_valid_login":
        "User successfully reached the Inventory page.",

    "test_invalid_username":
        "Application rejected the unrecognized username and password combination.",

    "test_invalid_password":
        "Application rejected the incorrect password and prevented access.",

    "test_empty_username":
        "Application prevented login and displayed the username-required message.",

    "test_empty_password":
        "Application prevented login and displayed the password-required message.",

    "test_both_fields_empty":
        "Application prevented login and indicated that username is required.",

    "test_locked_out_user":
        "Application identified the locked-out account and prevented access.",

    "test_password_is_masked":
        "Password field type was verified as password, confirming masking.",

    "test_saucedemo_complete_end_to_end_flow": (
        "Login, all six products, product sorting, three cart products, "
        "checkout information, subtotal, tax, total, order confirmation "
        "and return to inventory were successfully verified."
    ),
}


# --------------------------------------------------
# SCREENSHOT STEP DEFINITIONS
# --------------------------------------------------

SCREENSHOT_STEPS = {

    # E2E LOGIN EVIDENCE

    "login_page_before_credentials": {
        "description": "Login Page - Before Entering Credentials",
        "expected": "The login page should load with empty username and password fields.",
        "actual": "The login page loaded successfully and both credential fields were empty.",
    },

    "login_page_after_credentials": {
        "description": "Login Page - Credentials Entered",
        "expected": "The username and password should be entered before clicking Login.",
        "actual": "The credentials were entered successfully.",
    },

    # INDIVIDUAL LOGIN TEST EVIDENCE

    "login_page_loaded": {
        "description": "SauceDemo Login Page Loaded",
        "expected": "The SauceDemo login page should load with empty username and password fields.",
        "actual": "The login page loaded successfully.",
    },

    "valid_credentials_entered": {
        "description": "Valid Login Credentials Entered",
        "expected": "The valid username and password should be entered, with the password masked.",
        "actual": "The valid credentials were entered into the login form.",
    },

    "login_successful": {
        "description": "Login Successful",
        "expected": "The user should be authenticated and redirected to the inventory page.",
        "actual": "Login was successful and the inventory page was displayed.",
    },

    "invalid_username_credentials_entered": {
        "description": "Invalid Username Entered",
        "expected": "The incorrect username and valid password should be entered.",
        "actual": "The invalid username and valid password were entered.",
    },

    "invalid_password_credentials_entered": {
        "description": "Invalid Password Entered",
        "expected": "The valid username and incorrect password should be entered.",
        "actual": "The valid username and incorrect password were entered.",
    },

    "empty_username_password_entered": {
        "description": "Password Entered - Username Left Empty",
        "expected": "The username should remain empty while the valid password is entered.",
        "actual": "The username was left empty and the password was entered.",
    },

    "empty_password_username_entered": {
        "description": "Username Entered - Password Left Empty",
        "expected": "The valid username should be entered while the password remains empty.",
        "actual": "The username was entered and the password was left empty.",
    },

    "both_fields_empty_before_login": {
        "description": "Both Login Fields Empty",
        "expected": "Both username and password fields should remain empty before login.",
        "actual": "Both login fields were left empty.",
    },

    "locked_out_credentials_entered": {
        "description": "Locked-Out User Credentials Entered",
        "expected": "The locked-out username and valid password should be entered.",
        "actual": "The locked-out user's credentials were entered.",
    },

    "password_masking_verified": {
        "description": "Password Masking Verified",
        "expected": "The password field should use password input type and mask entered characters.",
        "actual": "The password field type was verified as password.",
    },

    "login_error_displayed": {
        "description": "Login Validation Error Displayed",
        "expected": "The application should display the expected login validation error.",
        "actual": "The expected login validation error was displayed.",
    },

    # E2E INVENTORY AND CHECKOUT EVIDENCE

    "inventory_products_verified": {
        "description": "Inventory Products Verified",
        "expected": "The inventory page should display all six products with their names, descriptions and prices.",
        "actual": "All six inventory products and their displayed details were verified.",
    },

    "product_sorting_verified": {
        "description": "Product Sorting Verified",
        "expected": "Products should be sorted correctly by name ascending, name descending and price ascending.",
        "actual": "All three sorting options were selected and their product order was verified.",
    },

    "three_products_added_to_cart": {
        "description": "Three Products Added to Cart",
        "expected": "Backpack, Bike Light and Bolt T-Shirt should be added to the shopping cart.",
        "actual": "All three selected products were added successfully and the cart count was verified.",
    },

    "cart_page_verified": {
        "description": "Shopping Cart Verified",
        "expected": "The cart should display the three selected products with their correct names and prices.",
        "actual": "All three selected products and their prices were verified in the cart.",
    },

    "checkout_information_entered": {
        "description": "Checkout Information Entered",
        "expected": "The checkout form should accept the customer's first name, last name and postal code.",
        "actual": "Checkout information was entered successfully and the process continued.",
    },

    "checkout_overview_verified": {
        "description": "Checkout Overview Verified",
        "expected": "The checkout overview should display the selected products and correct subtotal, tax and total.",
        "actual": "Products and checkout calculations were verified: subtotal $55.97, tax $4.48 and total $60.45.",
    },

    "order_confirmation": {
        "description": "Order Confirmation",
        "expected": "The order should be completed and the confirmation message should be displayed.",
        "actual": "The order was completed successfully and the thank-you confirmation message was verified.",
    },

    "back_home_inventory": {
        "description": "Return to Inventory Page",
        "expected": "Clicking Back Home should navigate the user to the inventory page.",
        "actual": "The Back Home action returned the user successfully to the inventory page.",
    },
}


# --------------------------------------------------
# EXPECTED LOGIN STEPS FOR EACH TEST CASE
# --------------------------------------------------

LOGIN_TEST_STEPS = {

    "test_valid_login": [
        "login_page_loaded",
        "valid_credentials_entered",
        "login_successful",
    ],

    "test_invalid_username": [
        "login_page_loaded",
        "invalid_username_credentials_entered",
        "login_error_displayed",
    ],

    "test_invalid_password": [
        "login_page_loaded",
        "invalid_password_credentials_entered",
        "login_error_displayed",
    ],

    "test_empty_username": [
        "login_page_loaded",
        "empty_username_password_entered",
        "login_error_displayed",
    ],

    "test_empty_password": [
        "login_page_loaded",
        "empty_password_username_entered",
        "login_error_displayed",
    ],

    "test_both_fields_empty": [
        "login_page_loaded",
        "both_fields_empty_before_login",
        "login_error_displayed",
    ],

    "test_locked_out_user": [
        "login_page_loaded",
        "locked_out_credentials_entered",
        "login_error_displayed",
    ],

    "test_password_is_masked": [
        "login_page_loaded",
        "password_masking_verified",
    ],
}


# --------------------------------------------------
# EXPECTED E2E STEPS
# --------------------------------------------------

E2E_TEST_STEPS = [
    "login_page_before_credentials",
    "login_page_after_credentials",
    "login_successful",
    "inventory_products_verified",
    "product_sorting_verified",
    "three_products_added_to_cart",
    "cart_page_verified",
    "checkout_information_entered",
    "checkout_overview_verified",
    "order_confirmation",
    "back_home_inventory",
]


# --------------------------------------------------
# TEST EXECUTION START TIME
# --------------------------------------------------

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):

    test_start_times[item.nodeid] = datetime.now()


# --------------------------------------------------
# CAPTURE TEST EXECUTION RESULTS
# --------------------------------------------------

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):

    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    test_name = item.name

    test_end_time = datetime.now()
    test_start_time = test_start_times.get(item.nodeid)

    status = "PASSED" if report.passed else "FAILED"

    execution_logs = report.capstdout or ""

    actual_result = (
        ACTUAL_RESULTS.get(
            test_name,
            "Test passed. See execution logs."
        )
        if report.passed
        else "Test failed. See failure details and execution logs."
    )

    failure_details = (
        report.longreprtext if report.failed else ""
    )

    if test_name == "test_saucedemo_complete_end_to_end_flow":
        module_name = "End-to-End"
    else:
        test_file = Path(str(item.path)).stem
        module_name = test_file.replace("test_", "", 1).title()

    test_results.append({
        "module": module_name,
        "test_name": test_name,
        "start_time": (
            test_start_time.strftime("%Y-%m-%d %H:%M:%S")
            if test_start_time else ""
        ),
        "end_time": test_end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "expected_result": EXPECTED_RESULTS.get(
            test_name,
            "Expected result not defined."
        ),
        "actual_result": actual_result,
        "status": status,
        "duration": round(report.duration, 2),
        "logs": execution_logs,
        "failure": failure_details,
        "_start_timestamp": (
            test_start_time.timestamp()
            if test_start_time else 0
        ),
    })


# --------------------------------------------------
# GET ONLY CURRENT TEST EXECUTION SCREENSHOTS
# --------------------------------------------------

def get_test_screenshots(test_name, start_timestamp):

    if not SCREENSHOT_FOLDER.exists():
        return []

    screenshots = []

    pattern = re.compile(
        r"_(\d{8}_\d{6}_\d{6})$"
    )

    for screenshot in SCREENSHOT_FOLDER.glob(
        f"{test_name}_*.png"
    ):

        match = pattern.search(screenshot.stem)

        if not match:
            continue

        try:
            screenshot_time = datetime.strptime(
                match.group(1),
                "%Y%m%d_%H%M%S_%f"
            )

        except ValueError:
            continue

        if screenshot_time.timestamp() >= start_timestamp:
            screenshots.append(screenshot)

    screenshots.sort(
        key=lambda file: file.stat().st_mtime
    )

    return screenshots


# --------------------------------------------------
# EXTRACT SCREENSHOT STEP NAME
# --------------------------------------------------

def get_screenshot_step_key(screenshot, test_name):

    stem = screenshot.stem

    prefix = f"{test_name}_"

    if not stem.startswith(prefix):
        return None

    remaining = stem[len(prefix):]

    # Remove category prefix, such as login_ or e2e_
    if "_" not in remaining:
        return None

    remaining = remaining.split("_", 1)[1]

    # Remove timestamp suffix
    match = re.search(
        r"_\d{8}_\d{6}_\d{6}$",
        remaining
    )

    if match:
        remaining = remaining[:match.start()]

    return remaining


# --------------------------------------------------
# BUILD WORD REPORT TEST CASES
# --------------------------------------------------

def build_word_test_cases(results):

    word_test_cases = []

    for result in results:

        test_name = result["test_name"]

        test_information = ALL_TEST_CASES.get(test_name)

        if not test_information:
            continue

        screenshots = get_test_screenshots(
            test_name,
            result.get("_start_timestamp", 0)
        )

        # Create a lookup of screenshot step names
        screenshot_lookup = {}

        for screenshot in screenshots:

            step_key = get_screenshot_step_key(
                screenshot,
                test_name
            )

            if step_key:
                screenshot_lookup[step_key] = screenshot

        steps = []

        # Login test cases use their own predefined step sequence
        if test_name in LOGIN_TEST_STEPS:

            expected_step_keys = LOGIN_TEST_STEPS[test_name]

        # E2E uses its own predefined step sequence
        elif test_name == "test_saucedemo_complete_end_to_end_flow":

            expected_step_keys = E2E_TEST_STEPS

        else:
            expected_step_keys = []

        for step_key in expected_step_keys:

            step_information = SCREENSHOT_STEPS[step_key]

            screenshot = screenshot_lookup.get(step_key)

            steps.append({
                "description": step_information["description"],
                "expected": step_information["expected"],
                "actual": (
                    step_information["actual"]
                    if screenshot
                    else "Screenshot evidence was not captured for this step."
                ),
                "screenshot": screenshot,
                "evidence_label": (
                    step_information["description"]
                    if screenshot
                    else "Screenshot evidence missing"
                ),
            })

        # Fallback for any other test
        if not steps:

            steps.append({
                "description": "Test Execution",
                "expected": result["expected_result"],
                "actual": result["actual_result"],
                "screenshot": None,
                "evidence_label": "No screenshot available",
            })

        word_test_cases.append({
            "id": test_information["id"],
            "title": test_information["title"],
            "scenario": test_information["scenario"],
            "expected": result["expected_result"],
            "actual": result["actual_result"],
            "status": (
                "PASS" if result["status"] == "PASSED" else "FAIL"
            ),
            "steps": steps,
            "failure": result.get("failure", ""),
        })

    return word_test_cases


# --------------------------------------------------
# GENERATE EXCEL AND WORD REPORTS
# --------------------------------------------------

def pytest_sessionfinish(session, exitstatus):

    if not test_results:
        return

    module_results = {}

    for result in test_results:

        module_name = result["module"]

        if module_name not in module_results:
            module_results[module_name] = []

        module_results[module_name].append(result)

    # Generate individual module Excel reports
    for module_name, results in module_results.items():

        print(f"\nGenerating {module_name} Excel report...")

        reporter = ExcelReporter(module=module_name)

        for result in results:

            report_result = result.copy()
            report_result.pop("module", None)
            report_result.pop("_start_timestamp", None)

            reporter.add_result(report_result)

        reporter.generate_report()

    # Generate consolidated Excel report
    print("\nGenerating consolidated Excel report...")

    consolidated_excel = ExcelReporter(module="Consolidated")

    for result in test_results:

        report_result = result.copy()
        report_result.pop("_start_timestamp", None)

        consolidated_excel.add_result(report_result)

    consolidated_excel.generate_report()

    # Generate consolidated Word report
    print("\nGenerating consolidated Word report...")

    word_test_cases = build_word_test_cases(test_results)

    if word_test_cases:

        word_reporter = WordReporter()

        word_reporter.generate_report(
            report_title="SauceDemo Complete Test Execution Report",
            test_cases=word_test_cases,
            report_name="SauceDemo_Consolidated_Execution_Report",
        )

        print(
            f"\nTotal Word test cases generated: {len(word_test_cases)}"
        )

        # Print evidence audit
        for test_case in word_test_cases:

            captured = sum(
                1 for step in test_case["steps"]
                if step["screenshot"]
            )

            total = len(test_case["steps"])

            print(
                f"{test_case['id']}: "
                f"{captured}/{total} screenshots captured"
            )

    else:
        print("No test cases available for Word reporting.")
