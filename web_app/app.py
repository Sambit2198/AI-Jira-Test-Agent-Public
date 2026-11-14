
import os
import json
import queue
import threading
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from time import perf_counter

import streamlit as st
from dotenv import load_dotenv

from src.ai_agent.test_generator import AITestGenerator
from src.ai_agent.playwright_executor import PlaywrightExecutor
from src.reporting.result_adapter import adapt_ai_report
from src.reporting.word_reporter import WordReporter
from src.reporting.excel_reporter import ExcelReporter

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_FOLDER = PROJECT_ROOT / "reports"
REPORT_FOLDER.mkdir(exist_ok=True)


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


def prepare_test_case(test_case, website_url):
    test_case = deepcopy(test_case)
    test_case = resolve_test_data(test_case)

    steps = test_case.get("steps", [])

    navigation_step = next(
        (step for step in steps if step.get("action") == "navigate"),
        None
    )

    if navigation_step:
        navigation_step["target"] = website_url
        steps.remove(navigation_step)
        steps.insert(0, navigation_step)
    else:
        steps.insert(0, {
            "action": "navigate",
            "target": website_url,
            "value": "",
            "expected_result": "Website opens successfully."
        })

    return test_case


def _execute_test_suite_in_worker(test_cases, website_url, message_queue):
    """
    All Playwright operations happen inside this worker thread.
    The browser, contexts, pages and Playwright session are created,
    used and closed in this same thread.
    """
    from playwright.sync_api import sync_playwright

    execution_results = []
    suite_start = datetime.now()
    counter_start = perf_counter()

    message_queue.put("Starting Playwright in the dedicated browser thread...")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
            slow_mo=1000,
            args=["--start-maximized"]
        )

        try:
            message_queue.put("Chromium browser launched successfully.")

            for index, original_case in enumerate(test_cases, start=1):
                test_case = prepare_test_case(original_case, website_url)

                test_id = test_case.get("id", "UNKNOWN")
                title = test_case.get("title", "Untitled test")

                message_queue.put(
                    f"Executing {index}/{len(test_cases)}: "
                    f"{test_id} - {title}"
                )

                context = None
                page = None

                try:
                    context = browser.new_context(no_viewport=True)
                    page = context.new_page()

                    executor = PlaywrightExecutor(page)
                    result = executor.execute_test_case(test_case)

                    execution_results.append(result)

                    message_queue.put(
                        f"{test_id}: {result.get('status', 'UNKNOWN')}"
                    )

                except Exception as error:
                    execution_results.append({
                        "test_case_id": test_id,
                        "title": title,
                        "preconditions": test_case.get("preconditions", ""),
                        "expected_result": test_case.get("expected_result", ""),
                        "status": "FAIL",
                        "start_time": "Not recorded",
                        "end_time": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "duration": 0,
                        "actual_result": f"Test execution failed: {error}",
                        "error": str(error),
                        "steps": []
                    })

                    message_queue.put(
                        f"{test_id}: execution error - {error}"
                    )

                finally:
                    if page is not None:
                        try:
                            if not page.is_closed():
                                page.wait_for_timeout(10000)
                        except Exception:
                            pass

                    if context is not None:
                        try:
                            context.close()
                        except Exception:
                            pass

        finally:
            browser.close()

    suite_end = datetime.now()
    duration = round(perf_counter() - counter_start, 2)

    timing = {
        "suite_start_time": suite_start.strftime("%Y-%m-%d %H:%M:%S"),
        "suite_end_time": suite_end.strftime("%Y-%m-%d %H:%M:%S"),
        "suite_duration": duration
    }

    return execution_results, timing


def execute_test_suite(test_cases, website_url, progress):
    """
    Starts a dedicated worker thread for Playwright.
    Streamlit UI updates remain on the main Streamlit thread.
    """
    message_queue = queue.Queue()
    worker_result = {}

    def worker_task():
        try:
            results, timing = _execute_test_suite_in_worker(
                test_cases,
                website_url,
                message_queue
            )

            worker_result["results"] = results
            worker_result["timing"] = timing

        except BaseException as error:
            worker_result["error"] = error

    browser_thread = threading.Thread(
        target=worker_task,
        name="PlaywrightBrowserWorker",
        daemon=False
    )

    browser_thread.start()

    while browser_thread.is_alive():
        try:
            message = message_queue.get(timeout=0.5)
            progress.write(message)
        except queue.Empty:
            pass

    browser_thread.join()

    while True:
        try:
            message = message_queue.get_nowait()
            progress.write(message)
        except queue.Empty:
            break

    if "error" in worker_result:
        raise RuntimeError(
            f"Browser worker failed: {worker_result['error']}"
        ) from worker_result["error"]

    return worker_result["results"], worker_result["timing"]


def generate_reports(report):
    json_path = REPORT_FOLDER / "ai_execution_report.json"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    adapted_results = adapt_ai_report(report)

    word_path = WordReporter().generate_report(
        report_title="AI Web Test Execution Report",
        test_cases=adapted_results,
        report_name="AI_Web_Test_Execution_Report"
    )

    excel_reporter = ExcelReporter(module="AI Execution")

    for result in report.get("execution_results", []):
        excel_result = dict(result)

        excel_result["status"] = (
            "PASSED" if result.get("status") == "PASS" else "FAILED"
        )

        excel_result["test_case_id"] = result.get(
            "test_case_id", "UNKNOWN"
        )

        excel_result["title"] = result.get(
            "title", "Untitled test"
        )

        excel_result["module"] = "AI Execution"

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

    excel_path = excel_reporter.generate_report()

    return Path(json_path), Path(word_path), Path(excel_path)


# ---------------------------------------------------------
# STREAMLIT USER INTERFACE
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Web Testing Agent",
    page_icon="🧪",
    layout="wide"
)

st.title("AI Web Testing Agent")

st.caption(
    "Generate test cases, execute browser automation, "
    "capture evidence and create professional reports."
)

st.divider()

with st.sidebar:
    st.title("AI Testing Agent")

    st.markdown("### Navigation")
    st.info("New Test Execution")

    st.divider()

    st.markdown("### Execution Engine")
    st.write("AI Provider: Groq")
    st.write("Browser Automation: Playwright")
    st.write("Reports: Word and Excel")

    st.divider()

    st.caption("Initial integration: SauceDemo")


st.subheader("Start a new test execution")

website_url = st.text_input(
    "Website URL",
    value="https://www.saucedemo.com",
    placeholder="https://www.saucedemo.com"
)

test_prompt = st.text_area(
    "Describe what you want to test",
    placeholder=(
        "Example: Run TC_LOGIN_001, TC_LOGIN_002 and TC_LOGIN_003. "
        "Verify the complete shopping journey and invalid username handling."
    ),
    height=160
)

st.info(
    "Initial version supports SauceDemo test scenarios "
    "TC_LOGIN_001 through TC_LOGIN_008. "
    "Include the required test IDs in your instructions."
)

start_execution = st.button(
    "Generate and Execute Tests",
    type="primary",
    use_container_width=True
)


if start_execution:
    normalized_url = website_url.strip().rstrip("/").casefold()

    if normalized_url not in {
        "https://www.saucedemo.com",
        "https://saucedemo.com"
    }:
        st.error(
            "This initial version is configured for SauceDemo only. "
            "Please enter https://www.saucedemo.com."
        )

    elif not test_prompt.strip():
        st.error("Please enter your testing instructions.")

    elif not any(
        f"TC_LOGIN_00{i}" in test_prompt.upper()
        for i in range(1, 9)
    ):
        st.error(
            "Please include at least one test ID, "
            "from TC_LOGIN_001 to TC_LOGIN_008."
        )

    else:
        progress_status = st.status(
            "Starting AI test execution...",
            expanded=True
        )

        try:
            with progress_status:
                progress_status.write("Connecting to Groq AI...")

                generator = AITestGenerator()
                generated = generator.generate_test_cases(test_prompt)

                test_cases = generated["test_cases"]

                if not test_cases:
                    raise RuntimeError(
                        "The AI did not generate any test cases."
                    )

                progress_status.write(
                    f"Generated {len(test_cases)} test cases."
                )

                progress_status.write(
                    "Starting visible Playwright browser..."
                )

                execution_results, timing = execute_test_suite(
                    test_cases,
                    website_url.strip(),
                    progress_status
                )

                passed = sum(
                    result.get("status") == "PASS"
                    for result in execution_results
                )

                failed = sum(
                    result.get("status") == "FAIL"
                    for result in execution_results
                )

                report = {
                    "provider": generated.get("provider", "Groq"),
                    "model": generated.get("model", ""),
                    "total_test_cases": len(execution_results),
                    "passed": passed,
                    "failed": failed,
                    "suite_start_time": timing["suite_start_time"],
                    "suite_end_time": timing["suite_end_time"],
                    "total_execution_duration": timing["suite_duration"],
                    "execution_results": execution_results
                }

                progress_status.write(
                    "Generating Word and Excel reports..."
                )

                json_path, word_path, excel_path = generate_reports(report)

                st.session_state["last_execution"] = {
                    "report": report,
                    "json_path": str(json_path),
                    "word_path": str(word_path),
                    "excel_path": str(excel_path)
                }

                progress_status.update(
                    label="Test execution completed.",
                    state="complete",
                    expanded=False
                )

        except Exception as error:
            progress_status.update(
                label="Test execution failed.",
                state="error",
                expanded=True
            )

            st.error(f"Execution error: {error}")


# ---------------------------------------------------------
# EXECUTION RESULTS
# ---------------------------------------------------------

if "last_execution" in st.session_state:
    last = st.session_state["last_execution"]
    report = last["report"]

    st.divider()
    st.subheader("Execution Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tests", report["total_test_cases"])
    col2.metric("Passed", report["passed"])
    col3.metric("Failed", report["failed"])

    col4.metric(
        "Duration",
        f"{report['total_execution_duration']} sec"
    )

    st.subheader("Test Case Results")

    for result in report["execution_results"]:
        status = result.get("status", "FAIL")
        icon = "✅" if status == "PASS" else "❌"

        with st.expander(
            f"{icon} {result.get('test_case_id')} - "
            f"{result.get('title')} ({status})"
        ):
            st.write(
                "Expected:",
                result.get("expected_result", "")
            )

            st.write(
                "Actual:",
                result.get("actual_result", "")
            )

            if result.get("error"):
                st.error(result["error"])

            st.write("Execution steps:")

            for index, step in enumerate(
                result.get("steps", []),
                start=1
            ):
                st.write(
                    f"{index}. {step.get('action')} - "
                    f"{step.get('target')} - "
                    f"{step.get('status')}"
                )

    st.divider()
    st.subheader("Download Execution Reports")

    col1, col2, col3 = st.columns(3)

    report_files = [
        (
            "JSON Report",
            last["json_path"],
            "application/json"
        ),
        (
            "Word Report",
            last["word_path"],
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        (
            "Excel Report",
            last["excel_path"],
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    ]

    for column, (label, path, mime) in zip(
        [col1, col2, col3],
        report_files
    ):
        report_file = Path(path)

        if report_file.exists():
            column.download_button(
                label=f"Download {label}",
                data=report_file.read_bytes(),
                file_name=report_file.name,
                mime=mime,
                use_container_width=True
            )


st.divider()

st.caption(
    "AI Web Testing Agent | Groq + Python + Playwright + Streamlit"
)
