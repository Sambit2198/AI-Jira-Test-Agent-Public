
import os
import json
from datetime import datetime
from time import perf_counter

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from src.ai_agent.test_generator import AITestGenerator
from src.ai_agent.playwright_executor import PlaywrightExecutor

from src.reporting.result_adapter import adapt_ai_report
from src.reporting.word_reporter import WordReporter
from src.reporting.excel_reporter import ExcelReporter

load_dotenv()


# --------------------------------------------------
# 1. RESOLVE TEST DATA
# --------------------------------------------------

def resolve_test_data(test_case):

    credentials = {
        "<valid_username>": os.getenv("SAUCEDEMO_USERNAME", "standard_user"),
        "<valid_password>": os.getenv("SAUCEDEMO_PASSWORD", "secret_sauce"),
        "<VALID_USERNAME>": os.getenv("SAUCEDEMO_USERNAME", "standard_user"),
        "<VALID_PASSWORD>": os.getenv("SAUCEDEMO_PASSWORD", "secret_sauce"),
        "<invalid_username>": "invalid_user",
        "<invalid_password>": "invalid_password",
        "<INVALID_USERNAME>": "invalid_user",
        "<INVALID_PASSWORD>": "invalid_password"
    }

    for step in test_case.get("steps", []):
        value = step.get("value", "")
        if value in credentials:
            step["value"] = credentials[value]

    for data in test_case.get("test_data", []):
        value = data.get("value", "")
        if value in credentials:
            data["value"] = credentials[value]

    return test_case


# --------------------------------------------------
# 2. ENSURE VALID NAVIGATION
# --------------------------------------------------

def ensure_navigation_first(test_case):

    steps = test_case.get("steps", [])

    navigation_step = next(
        (step for step in steps if step.get("action") == "navigate"),
        None
    )

    if navigation_step:

        target = navigation_step.get("target", "")

        if not target.startswith(("http://", "https://")):
            navigation_step["target"] = "https://www.saucedemo.com"

        steps.remove(navigation_step)
        steps.insert(0, navigation_step)

    else:

        steps.insert(0, {
            "action": "navigate",
            "target": "https://www.saucedemo.com",
            "value": "",
            "expected_result": "SauceDemo login page opens successfully."
        })

    return test_case


# --------------------------------------------------
# 3. EXECUTE AI-GENERATED TEST CASES
# --------------------------------------------------

def execute_test_suite(test_cases):

    execution_results = []

    suite_start_time = datetime.now()
    suite_start_counter = perf_counter()

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=False,
            slow_mo=1000,
            args=["--start-maximized"]
        )

        try:

            for test_case in test_cases:

                context = browser.new_context(no_viewport=True)
                page = context.new_page()

                executor = PlaywrightExecutor(page)

                try:

                    test_case = resolve_test_data(test_case)
                    test_case = ensure_navigation_first(test_case)

                    print(
                        f"\nExecuting: "
                        f"{test_case.get('id', 'UNKNOWN')} - "
                        f"{test_case.get('title', 'Untitled test')}"
                    )

                    result = executor.execute_test_case(test_case)
                    execution_results.append(result)

                except Exception as error:

                    print(
                        f"\nTEST FAILED: "
                        f"{test_case.get('id', 'UNKNOWN')}"
                    )
                    print(f"Reason: {error}")

                    execution_results.append({
                        "test_case_id": test_case.get("id", "UNKNOWN"),
                        "title": test_case.get("title", "Untitled test"),
                        "preconditions": test_case.get("preconditions", ""),
                        "expected_result": test_case.get("expected_result", ""),
                        "status": "FAIL",
                        "start_time": "Not recorded",
                        "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "duration": 0,
                        "actual_result": f"Test execution failed: {str(error)}",
                        "error": str(error),
                        "steps": []
                    })

                finally:

                    print("\nTest completed. Browser will close in 10 seconds.")

                    try:
                        page.wait_for_timeout(10000)
                    except Exception:
                        pass

                    context.close()

        finally:
            browser.close()

    suite_end_counter = perf_counter()
    suite_end_time = datetime.now()

    suite_timing = {
        "suite_start_time": suite_start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "suite_end_time": suite_end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "suite_duration": round(suite_end_counter - suite_start_counter, 2)
    }

    return execution_results, suite_timing


# --------------------------------------------------
# 4. GENERATE JSON REPORT
# --------------------------------------------------

def save_json_report(report):

    os.makedirs("reports", exist_ok=True)

    report_path = "reports/ai_execution_report.json"

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print(f"\nJSON report saved: {report_path}")

    return report_path


# --------------------------------------------------
# 5. GENERATE WORD REPORT
# --------------------------------------------------

def generate_word_report(report):

    print("\nGenerating Word execution report...")

    try:

        adapted_results = adapt_ai_report(report)

        word_reporter = WordReporter()

        report_path = word_reporter.generate_report(
            report_title="AI Web Test Execution Report",
            test_cases=adapted_results,
            report_name="AI_Web_Test_Execution_Report"
        )

        print("\nWord report generated successfully.")
        print(f"Word report saved: {report_path}")

        return report_path

    except Exception as error:

        print("\nWORD REPORT GENERATION FAILED.")
        print(f"Reason: {error}")
        print("The JSON execution report is still available.")

        return None


# --------------------------------------------------
# 6. GENERATE EXCEL REPORT
# --------------------------------------------------

def generate_excel_report(report):

    print("\nGenerating Excel execution report...")

    try:

        excel_reporter = ExcelReporter(module="AI Execution")

        for result in report.get("execution_results", []):

            # ExcelReporter expects PASSED / FAILED.
            excel_result = dict(result)

            excel_result["status"] = (
                "PASSED"
                if result.get("status") == "PASS"
                else "FAILED"
            )

            # Preserve AI-generated test IDs and titles.
            excel_result["test_case_id"] = result.get(
                "test_case_id", "UNKNOWN"
            )

            excel_result["title"] = result.get(
                "title", "Untitled test"
            )

            excel_result["module"] = "AI Execution"

            # Convert executor steps into Excel descriptions.
            excel_result["steps"] = [
                {
                    "description": (
                        f"{step.get('action', '')} "
                        f"{step.get('target', '')} "
                        f"{step.get('value', '')}"
                    ).strip()
                }
                for step in result.get("steps", [])
            ]

            excel_result["logs"] = "\n".join(
                step.get("actual_result", "")
                for step in result.get("steps", [])
            )

            excel_result["failure"] = result.get("error", "")

            excel_reporter.add_result(excel_result)

        report_path = excel_reporter.generate_report()

        print("\nExcel report generated successfully.")
        print(f"Excel report saved: {report_path}")

        return report_path

    except Exception as error:

        print("\nEXCEL REPORT GENERATION FAILED.")
        print(f"Reason: {error}")
        print("The JSON execution report is still available.")

        return None


# --------------------------------------------------
# 7. MAIN AI TEST RUNNER
# --------------------------------------------------

def main():

    print("\n========================================")
    print("       AI WEB TESTING AGENT")
    print("========================================")

    prompt = input(
        "\nDescribe what you want to test: "
    ).strip()

    if not prompt:
        print("\nPlease enter a testing requirement.")
        return

    print("\nGenerating test cases using Groq AI...")

    generator = AITestGenerator()

    generated_result = generator.generate_test_cases(prompt)

    test_cases = generated_result["test_cases"]

    print(f"\nProvider: {generated_result.get('provider', 'Groq')}")
    print(f"Model: {generated_result.get('model', 'Configured model')}")
    print(f"Generated test cases: {len(test_cases)}")

    if not test_cases:
        print("\nNo relevant test cases were generated.")
        return

    print("\nStarting Playwright execution...")

    execution_results, suite_timing = execute_test_suite(test_cases)

    passed = sum(
        result.get("status") == "PASS"
        for result in execution_results
    )

    failed = sum(
        result.get("status") == "FAIL"
        for result in execution_results
    )

    report = {
        "provider": generated_result.get("provider", "Groq"),
        "model": generated_result.get("model", ""),
        "total_test_cases": len(execution_results),
        "passed": passed,
        "failed": failed,
        "suite_start_time": suite_timing["suite_start_time"],
        "suite_end_time": suite_timing["suite_end_time"],
        "total_execution_duration": suite_timing["suite_duration"],
        "execution_results": execution_results
    }

    # Generate all three reports.

    save_json_report(report)
    generate_word_report(report)
    generate_excel_report(report)

    print("\n========================================")
    print("       EXECUTION SUMMARY")
    print("========================================")

    print(f"Total:    {len(execution_results)}")
    print(f"Passed:   {passed}")
    print(f"Failed:   {failed}")
    print(f"Duration: {suite_timing['suite_duration']} seconds")

    print("\nReports are available in the reports folder.")


# --------------------------------------------------
# 8. APPLICATION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":

    try:
        main()

    except Exception as error:
        print(f"\nAI TEST RUNNER ERROR: {error}")
