
from datetime import datetime
from pathlib import Path

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
# EXPECTED RESULTS
# --------------------------------------------------

EXPECTED_RESULTS = {
    "test_valid_login":
        "User successfully logs in and reaches the inventory page.",

    "test_invalid_username":
        "Username and password do not match any user.",

    "test_invalid_password":
        "Username and password do not match any user.",

    "test_empty_username":
        "Username is required.",

    "test_empty_password":
        "Password is required.",

    "test_both_fields_empty":
        "Username is required.",

    "test_locked_out_user":
        "Locked-out user is prevented from logging in.",

    "test_password_is_masked":
        "Password field uses password masking.",
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
}


# --------------------------------------------------
# TEST CASE INFORMATION FOR WORD REPORT
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

    test_file = Path(str(item.path)).stem

    if test_file.startswith("test_"):
        module_name = test_file.replace("test_", "", 1).title()
    else:
        module_name = test_file.title()

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
    })


# --------------------------------------------------
# FIND SCREENSHOTS FOR INDIVIDUAL TEST
# --------------------------------------------------

def get_test_screenshots(test_name):

    # Test-specific screenshot naming will be added
    # to screenshot_manager.py in our next step.

    screenshots = list(
        SCREENSHOT_FOLDER.glob(f"{test_name}_*.png")
    )

    screenshots.sort(
        key=lambda file: file.stat().st_mtime
    )

    return screenshots


# --------------------------------------------------
# BUILD WORD REPORT TEST CASES
# --------------------------------------------------

def build_word_test_cases(results):

    word_test_cases = []

    for result in results:

        test_name = result["test_name"]

        test_information = LOGIN_TEST_CASES.get(test_name)

        if not test_information:
            continue

        screenshots = get_test_screenshots(test_name)

        steps = []

        for index, screenshot in enumerate(screenshots, start=1):

            steps.append({
                "description": screenshot.stem,
                "expected": "The application should perform the expected action.",
                "actual": "Execution evidence captured successfully.",
                "screenshot": screenshot,
            })

        if not steps:
            steps.append({
                "description": "Test execution",
                "expected": result["expected_result"],
                "actual": result["actual_result"],
                "screenshot": None,
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

    for module_name, results in module_results.items():

        print(f"\nGenerating {module_name} test report...")

        # Generate existing Excel report
        reporter = ExcelReporter(module=module_name)

        for result in results:

            report_result = result.copy()
            report_result.pop("module")

            reporter.add_result(report_result)

        reporter.generate_report()

        # Generate consolidated Word report for Login tests
        if module_name == "Login":

            print("\nGenerating Login Word execution report...")

            word_test_cases = build_word_test_cases(results)

            if word_test_cases:

                word_reporter = WordReporter()

                word_reporter.generate_report(
                    report_title="SauceDemo Login Test Execution Report",
                    test_cases=word_test_cases,
                    report_name="SauceDemo_Login_Execution_Report",
                )

            else:
                print("No Login test cases available for Word reporting.")
