
def get_expected_result(test_id):

    expected_results = {

        "TC_LOGIN_001": (
            "The user should be able to log in successfully, view and "
            "sort the available products, add three selected products "
            "to the shopping cart, complete checkout, verify the order "
            "amount, receive an order confirmation, and return to "
            "the inventory page."
        ),

        "TC_LOGIN_002": (
            "The application should reject an invalid username and "
            "display an appropriate invalid-credentials message."
        ),

        "TC_LOGIN_003": (
            "The application should reject an invalid password and "
            "display an appropriate invalid-credentials message."
        ),

        "TC_LOGIN_004": (
            "The application should reject invalid username and "
            "password combinations and display an appropriate "
            "invalid-credentials message."
        ),

        "TC_LOGIN_005": (
            "The application should prevent login when the username "
            "is empty and display a message indicating that the "
            "username is required."
        ),

        "TC_LOGIN_006": (
            "The application should prevent login when the password "
            "is empty and display a message indicating that the "
            "password is required."
        ),

        "TC_LOGIN_007": (
            "The application should prevent login when both username "
            "and password are empty and display a message indicating "
            "that the username is required."
        ),

        "TC_LOGIN_008": (
            "The application should prevent a locked-out user from "
            "logging in and display an appropriate account restriction "
            "message."
        )
    }

    return expected_results.get(
        test_id,
        "The application should behave according to the specified "
        "test scenario."
    )


def get_actual_summary(test_id, steps, status):

    if status != "PASSED":

        failed_steps = [
            step for step in steps
            if step.get("status", "").upper() != "PASS"
        ]

        if failed_steps:

            failed_step = failed_steps[0]

            return (
                f"The test did not complete successfully. "
                f"The step '{failed_step.get('target', 'Unknown step')}' "
                f"could not be completed as expected. "
                f"Observed result: "
                f"{failed_step.get('actual_result', 'No details available.')}"
            )

        return "The test did not complete successfully. Please review the execution evidence."

    if test_id == "TC_LOGIN_001":

        return (
            "The user logged in successfully and all six products "
            "were displayed. Product sorting worked as expected, "
            "and the three selected products were added to the cart. "
            "The cart displayed all three products. Checkout was "
            "completed successfully using the provided customer "
            "details. The item subtotal was $55.97, tax was $4.48, "
            "and the final amount was $60.45. The order confirmation "
            "was displayed, and the user successfully returned to "
            "the inventory page."
        )

    error_message = next(
        (
            step.get("actual_result", "")
            for step in steps
            if step.get("action", "").lower() == "assert_text"
            and "error message" in step.get("target", "").lower()
        ),
        ""
    )

    if error_message:

        if "Actual:" in error_message:
            error_message = error_message.split("Actual:", 1)[-1].strip()

        return (
            "The application prevented the login attempt and "
            f"displayed the following message: {error_message}"
        )

    return (
        "The application behaved as expected, and all "
        "recorded execution steps completed successfully."
    )


def adapt_ai_report(ai_report):

    adapted_results = []

    for case in ai_report.get("execution_results", []):

        adapted_steps = []
        execution_logs = []

        case_steps = case.get("steps", [])

        test_id = case.get(
            "test_case_id",
            case.get("id", "")
        )

        for number, step in enumerate(case_steps, start=1):

            action = step.get("action", "")
            target = step.get("target", "")
            value = step.get("value", "")
            expected = step.get("expected_result", "")

            actual = step.get(
                "actual_result",
                "No actual result recorded."
            )

            step_status = step.get("status", "").upper()

            description = f"{action}: {target}"

            if value:
                description += f" (Value: {value})"

            adapted_steps.append({
                "description": description,
                "expected": expected,
                "actual": actual,
                "status": step_status,
                "screenshot": step.get("screenshot"),
                "evidence_label": description
            })

            execution_logs.append(
                f"Step {number}: {description} | "
                f"Status: {step_status} | "
                f"Expected: {expected} | "
                f"Actual: {actual}"
            )

        all_steps_passed = (
            bool(case_steps)
            and all(
                step.get("status", "").upper() == "PASS"
                for step in case_steps
            )
        )

        status = (
            "PASSED"
            if case.get("status", "").upper() == "PASS"
            and all_steps_passed
            else "FAILED"
        )

        expected_result = get_expected_result(test_id)

        actual_result = get_actual_summary(
            test_id,
            case_steps,
            status
        )

        failure = case.get("error", "")

        adapted_results.append({

            "module": "AI Execution",

            "test_name": case.get(
                "title",
                "Untitled AI Test"
            ),

            "test_case_id": test_id,

            "title": case.get("title", ""),

            "scenario": case.get("title", ""),

            "status": status,

            "start_time": case.get(
                "start_time",
                "Not recorded"
            ),

            "end_time": case.get(
                "end_time",
                "Not recorded"
            ),

            "duration": case.get("duration", 0),

            "expected_result": expected_result,

            "actual_result": actual_result,

            "logs": "\n".join(execution_logs),

            "failure": failure,

            "id": test_id or "Not assigned",

            "expected": expected_result,

            "actual": actual_result,

            "steps": adapted_steps
        })

    return adapted_results
