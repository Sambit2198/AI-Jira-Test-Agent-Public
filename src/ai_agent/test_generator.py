
import os
import json
import re
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError

load_dotenv()


# --------------------------------------------------
# TEST CASE SCENARIO CATALOG
# --------------------------------------------------

TEST_SCENARIO_CATALOG = {
    "TC_LOGIN_001": (
        "Complete SauceDemo shopping journey: "
        "valid login, verify inventory and all 6 products, "
        "sort products A-Z, Z-A and price low-to-high, "
        "add Sauce Labs Backpack, Sauce Labs Bike Light and "
        "Sauce Labs Bolt T-Shirt, verify cart count and contents, "
        "checkout using John Smith and postal code 12345, "
        "verify subtotal $55.97, tax $4.48 and total $60.45, "
        "finish order, verify exact confirmation message "
        "Thank you for your order!, click Back Home "
        "and verify inventory."
    ),
    "TC_LOGIN_002": (
        "Login with invalid username and valid password; "
        "verify the invalid credentials error."
    ),
    "TC_LOGIN_003": (
        "Login with valid username and invalid password; "
        "verify the invalid credentials error."
    ),
    "TC_LOGIN_004": (
        "Login with both invalid username and invalid password; "
        "verify the invalid credentials error."
    ),
    "TC_LOGIN_005": (
        "Login with empty username and valid password; "
        "verify username required error."
    ),
    "TC_LOGIN_006": (
        "Login with valid username and empty password; "
        "verify password required error."
    ),
    "TC_LOGIN_007": (
        "Login with both username and password empty; "
        "verify username required error."
    ),
    "TC_LOGIN_008": (
        "Login using locked_out_user and secret_sauce; "
        "verify the locked-out error."
    )
}


# --------------------------------------------------
# PYDANTIC SCHEMA
# --------------------------------------------------

class TestStep(BaseModel):
    action: Literal[
        "navigate",
        "fill",
        "click",
        "select",
        "assert_text",
        "assert_url",
        "assert_visible"
    ]

    target: str = ""
    value: str = ""
    expected_result: str


class TestData(BaseModel):
    name: str
    value: str


class TestCase(BaseModel):
    id: str
    title: str
    preconditions: str
    steps: list[TestStep]
    expected_result: str
    test_data: list[TestData]


class TestSuite(BaseModel):
    test_cases: list[TestCase]


# --------------------------------------------------
# AI TEST GENERATOR
# --------------------------------------------------

class AITestGenerator:

    def __init__(self):

        groq_key = os.getenv("GROQ_API_KEY")

        if not groq_key:
            raise ValueError(
                "GROQ_API_KEY was not found in your .env file."
            )

        self.client = OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1",
            timeout=60.0,
            max_retries=0
        )

        self.model = "openai/gpt-oss-20b"

    # --------------------------------------------------
    # JSON SCHEMA
    # --------------------------------------------------

    def _get_json_schema(self):

        return {
            "type": "object",
            "properties": {
                "test_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "title": {"type": "string"},
                            "preconditions": {"type": "string"},
                            "steps": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "action": {
                                            "type": "string",
                                            "enum": [
                                                "navigate",
                                                "fill",
                                                "click",
                                                "select",
                                                "assert_text",
                                                "assert_url",
                                                "assert_visible"
                                            ]
                                        },
                                        "target": {"type": "string"},
                                        "value": {"type": "string"},
                                        "expected_result": {
                                            "type": "string"
                                        }
                                    },
                                    "required": [
                                        "action",
                                        "target",
                                        "value",
                                        "expected_result"
                                    ],
                                    "additionalProperties": False
                                }
                            },
                            "expected_result": {"type": "string"},
                            "test_data": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "value": {"type": "string"}
                                    },
                                    "required": [
                                        "name",
                                        "value"
                                    ],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": [
                            "id",
                            "title",
                            "preconditions",
                            "steps",
                            "expected_result",
                            "test_data"
                        ],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["test_cases"],
            "additionalProperties": False
        }

    # --------------------------------------------------
    # EXTRACT NUMBERED SCENARIOS
    # --------------------------------------------------

    def _extract_scenarios(self, user_prompt):

        lines = user_prompt.splitlines()

        scenario_heading_found = False
        scenarios = []

        for line in lines:

            if re.match(
                r"^\s*(?:test\s+)?scenarios\s*:\s*",
                line,
                re.IGNORECASE
            ):

                scenario_heading_found = True

                heading_content = re.sub(
                    r"^\s*(?:test\s+)?scenarios\s*:\s*",
                    "",
                    line,
                    flags=re.IGNORECASE
                )

                lines_to_process = [heading_content]

            elif scenario_heading_found:

                lines_to_process = [line]

            else:
                continue

            for scenario_line in lines_to_process:

                if not scenario_line.strip():
                    continue

                match = re.match(
                    r"^\s*(\d+)[.)]\s+(.+?)\s*$",
                    scenario_line
                )

                if match:
                    scenarios.append(
                        match.group(2).strip()
                    )

        return scenarios

    # --------------------------------------------------
    # RESOLVE REQUESTED TEST SCENARIOS
    # --------------------------------------------------

    def _resolve_requested_scenarios(self, user_prompt):

        requested_ids = re.findall(
            r"\bTC_LOGIN_00[1-8]\b",
            user_prompt.upper()
        )

        requested_ids = list(
            dict.fromkeys(requested_ids)
        )

        if requested_ids:

            return [
                {
                    "id": test_id,
                    "description": TEST_SCENARIO_CATALOG[test_id]
                }
                for test_id in requested_ids
            ]

        return [
            {
                "id": None,
                "description": scenario
            }
            for scenario in self._extract_scenarios(user_prompt)
        ]

    # --------------------------------------------------
    # SCENARIO VALIDATION
    # --------------------------------------------------

    def _validate_scenario_coverage(
        self,
        user_prompt,
        test_cases
    ):

        scenarios = self._resolve_requested_scenarios(
            user_prompt
        )

        if not scenarios:
            raise ValueError(
                "No recognized test case IDs or numbered "
                "scenarios were found. Generation stopped."
            )

        if len(test_cases) != len(scenarios):

            raise ValueError(
                f"Scenario count mismatch. "
                f"Requested: {len(scenarios)}, "
                f"Generated: {len(test_cases)}."
            )

        requested_ids = [
            item["id"]
            for item in scenarios
            if item["id"] is not None
        ]

        if requested_ids:

            generated_ids = [
                test_case.id
                for test_case in test_cases
            ]

            if generated_ids != requested_ids:

                raise ValueError(
                    f"Test ID mismatch. "
                    f"Requested: {requested_ids}, "
                    f"Generated: {generated_ids}."
                )

        for test_case in test_cases:

            if test_case.id != "TC_LOGIN_001":
                continue

            steps = test_case.steps

            def normalize(text):

                return re.sub(
                    r"[^a-z0-9]",
                    "",
                    str(text).casefold()
                )

            def has_step(
                actions,
                targets=None,
                values=None,
                search_target_in_all_fields=False
            ):

                if isinstance(actions, str):
                    actions = [actions]

                targets = targets or []
                values = values or []

                for step in steps:

                    if step.action not in actions:
                        continue

                    step_target = normalize(step.target)
                    step_value = normalize(step.value)
                    expected = normalize(step.expected_result)

                    all_text = (
                        step_target
                        + " "
                        + step_value
                        + " "
                        + expected
                    )

                    if search_target_in_all_fields:

                        target_match = (
                            not targets
                            or any(
                                normalize(target) in all_text
                                for target in targets
                            )
                        )

                    else:

                        target_match = (
                            not targets
                            or any(
                                normalize(target) in step_target
                                or step_target in normalize(target)
                                for target in targets
                            )
                        )

                    value_match = (
                        not values
                        or any(
                            normalize(value) in all_text
                            for value in values
                        )
                    )

                    if target_match and value_match:
                        return True

                return False

            # Required shopping journey checks.
            required_checks = [

                (
                    ["navigate"],
                    ["https://www.saucedemo.com"],
                    [],
                    True
                ),
                (
                    ["fill"],
                    ["username input field", "username"],
                    [],
                    False
                ),
                (
                    ["fill"],
                    ["password input field", "password"],
                    [],
                    False
                ),
                (
                    ["click"],
                    ["login button", "login"],
                    [],
                    False
                ),
                (
                    ["assert_url"],
                    [],
                    ["https://www.saucedemo.com/inventory.html"],
                    False
                ),
                (
                    ["assert_visible"],
                    [
                        "inventory products are visible",
                        "inventory products"
                    ],
                    [],
                    False
                ),
                (
                    ["select"],
                    ["product sorting dropdown"],
                    ["Name (A to Z)"],
                    False
                ),
                (
                    ["select"],
                    ["product sorting dropdown"],
                    ["Name (Z to A)"],
                    False
                ),
                (
                    ["select"],
                    ["product sorting dropdown"],
                    ["Price (low to high)"],
                    False
                ),
                (
                    ["click"],
                    ["Add Sauce Labs Backpack to cart"],
                    [],
                    False
                ),
                (
                    ["click"],
                    ["Add Sauce Labs Bike Light to cart"],
                    [],
                    False
                ),
                (
                    ["click"],
                    ["Add Sauce Labs Bolt T-Shirt to cart"],
                    [],
                    False
                ),
                (
                    ["assert_text"],
                    ["cart badge"],
                    ["3"],
                    False
                ),
                (
                    ["click"],
                    ["shopping cart"],
                    [],
                    False
                ),
                (
                    ["assert_visible"],
                    ["cart products"],
                    [],
                    False
                ),
                (
                    ["click"],
                    ["checkout button", "checkout"],
                    [],
                    False
                ),
                (
                    ["fill"],
                    ["first name field", "first name"],
                    [],
                    False
                ),
                (
                    ["fill"],
                    ["last name field", "last name"],
                    [],
                    False
                ),
                (
                    ["fill"],
                    ["postal code field", "zip code"],
                    [],
                    False
                ),
                (
                    ["click"],
                    ["continue button", "continue"],
                    [],
                    False
                ),

                # Exact subtotal verification.
                (
                    ["assert_text"],
                    ["item subtotal", "subtotal"],
                    ["$55.97"],
                    False
                ),

                # Exact tax verification.
                (
                    ["assert_text"],
                    ["tax"],
                    ["$4.48"],
                    False
                ),

                # Exact total verification.
                (
                    ["assert_text"],
                    ["order total", "total"],
                    ["$60.45"],
                    False
                ),

                (
                    ["click"],
                    ["finish button", "finish"],
                    [],
                    False
                ),
                (
                    ["assert_text"],
                    ["order confirmation"],
                    ["Thank you for your order!"],
                    False
                ),
                (
                    ["click"],
                    ["back home button", "back home"],
                    [],
                    False
                ),
                (
                    ["assert_visible"],
                    [
                        "inventory products are visible",
                        "inventory products"
                    ],
                    [],
                    False
                )
            ]

            missing_checks = []

            for (
                actions,
                targets,
                values,
                search_target_in_all_fields
            ) in required_checks:

                if not has_step(
                    actions,
                    targets,
                    values,
                    search_target_in_all_fields
                ):

                    missing_checks.append(
                        f"actions={actions}: "
                        f"targets={targets}, values={values}"
                    )

            if missing_checks:

                raise ValueError(
                    "TC_LOGIN_001 is incomplete. "
                    "Missing required shopping journey steps:\n"
                    + "\n".join(missing_checks)
                )

        print(
            f"\nScenario validation successful: "
            f"{len(scenarios)} scenarios matched."
        )

    # --------------------------------------------------
    # GENERATION INSTRUCTIONS
    # --------------------------------------------------

    def _build_instructions(self):

        return """
You are a Senior QA Automation Engineer.

Generate accurate, executable Playwright test cases
from the user's requirements.

STRICT SCENARIO RULES:

1. Generate exactly one test case per supplied scenario.
2. Preserve the original scenario order.
3. Never combine, omit, replace or add scenarios.
4. Use the exact supplied test case ID.
5. Follow the complete scenario description.
6. Do not generate execution results.
7. Do not mark generated cases as passed.

APPLICATION:

Application: SauceDemo
URL: https://www.saucedemo.com

Valid credentials:
standard_user / secret_sauce

Successful login URL:
https://www.saucedemo.com/inventory.html

LOGIN ERROR MESSAGES:

Invalid username or password:
Epic sadface: Username and password do not match any user in this service

Empty username:
Epic sadface: Username is required

Empty password:
Epic sadface: Password is required

Both fields empty:
Epic sadface: Username is required

Locked-out user:
Use username locked_out_user and password secret_sauce.

Locked-out error:
Epic sadface: Sorry, this user has been locked out.

FULL SHOPPING JOURNEY:

For TC_LOGIN_001, generate the COMPLETE shopping journey.
Never replace it with a login-only test.

Include these operations in order:

1. Navigate to SauceDemo.
2. Fill valid username.
3. Fill valid password.
4. Click Login.
5. Verify inventory URL.
6. Verify all 6 inventory products are visible.
7. Sort products A-Z.
8. Sort products Z-A.
9. Sort products by price low-to-high.
10. Add Sauce Labs Backpack to cart.
11. Add Sauce Labs Bike Light to cart.
12. Add Sauce Labs Bolt T-Shirt to cart.
13. Verify cart badge count using assert_text.
14. Click shopping cart.
15. Verify all 3 cart products.
16. Click Checkout.
17. Enter first name John.
18. Enter last name Smith.
19. Enter postal code 12345.
20. Click Continue.
21. Verify subtotal, tax and total using EXACT TEXT ASSERTIONS.
22. Click Finish.
23. Verify exact order confirmation text.
24. Click Back Home.
25. Verify inventory products are visible again.

PRODUCT NAMES:

Sauce Labs Backpack
Sauce Labs Bike Light
Sauce Labs Bolt T-Shirt

CHECKOUT VALUES:

Subtotal: $55.97
Tax: $4.48
Total: $60.45

CRITICAL CHECKOUT ASSERTIONS:

These three checks are mandatory and independent.
You MUST generate three separate steps.

SUBTOTAL:

action: assert_text
target: item subtotal
value: $55.97

TAX:

action: assert_text
target: tax
value: $4.48

TOTAL:

action: assert_text
target: order total
value: $60.45

IMPORTANT:

Do NOT use assert_visible for these three checks.
Do NOT replace assert_text with assert_visible.
Do NOT omit the dollar sign.
Do NOT combine the three amounts into one assertion.
Do NOT use approximate or different amounts.

The exact action, target and value must match the
three specifications above.

ORDER CONFIRMATION:

The exact successful SauceDemo order confirmation
message is:

Thank you for your order!

Use exactly:

action: assert_text
target: order confirmation
value: Thank you for your order!

Do not use assert_visible alone for order confirmation.

Never use these incorrect messages:

Your order has been processed!
Order completed successfully!
Your order was successful!

CART COUNT:

Use exactly:

action: assert_text
target: cart badge
value: 3

Do not use assert_visible alone for cart count.

INVENTORY VERIFICATION:

Use this target for inventory assertions:

inventory products are visible

Use action assert_visible.

The executor verifies exactly 6 inventory products.

Use this target twice in TC_LOGIN_001:
- Once after successful login.
- Once after clicking Back Home.

CART VERIFICATION:

After clicking shopping cart, use exactly this target:

cart products

Use action assert_visible.

The executor verifies exactly 3 cart products:
- Sauce Labs Backpack
- Sauce Labs Bike Light
- Sauce Labs Bolt T-Shirt

NEVER use the inventory verification target on the cart page.

SORTING:

Use action select with target:
product sorting dropdown

Supported option labels:

Name (A to Z)
Name (Z to A)
Price (low to high)
Price (high to low)

LOGIN ASSERTIONS:

For invalid login scenarios:
- Verify the error message is visible.
- Verify its exact text using assert_text.

SUPPORTED ACTIONS:

navigate
fill
click
select
assert_text
assert_url
assert_visible

SUPPORTED TARGETS:

username input field
password input field
login button
error message
inventory page
inventory products are visible
Products heading
shopping cart
cart badge
cart products
product sorting dropdown
checkout button
first name field
last name field
postal code field
continue button
finish button
back home button
item subtotal
tax
order total
order confirmation

PRODUCT TARGETS:

To add products, use:

Add Sauce Labs Backpack to cart
Add Sauce Labs Bike Light to cart
Add Sauce Labs Bolt T-Shirt to cart

To remove a product, use:

Remove Sauce Labs Backpack from cart

TEST DATA:

Use standard_user and secret_sauce for valid credentials.
Use invalid credentials for invalid login scenarios.
Use empty strings for empty fields.
Use locked_out_user for the locked-out scenario.
Use John, Smith and 12345 for checkout information.

STEP RULES:

- One browser action per step.
- Navigate before interacting with the page.
- Do not use unsupported selectors.
- Do not invent error messages.
- Do not invent product names.
- Include meaningful expected results for every step.
- Use assert_text for displayed text.
- Use assert_visible for visibility checks.
- Use assert_url for URL checks.
- Avoid duplicate assertions.
- Do not omit required business operations.

Every test case must contain:
id, title, preconditions, steps,
expected_result, test_data.

Every step must contain:
action, target, value, expected_result.

Return only valid JSON matching the supplied schema.
"""

    # --------------------------------------------------
    # BUILD USER PROMPT
    # --------------------------------------------------

    def _build_prompt(self, user_prompt):

        scenarios = self._resolve_requested_scenarios(
            user_prompt
        )

        scenario_instruction = ""

        if scenarios:

            scenario_instruction = f"""

EXACT SCENARIOS TO GENERATE:

{json.dumps(scenarios, indent=4)}

STRICT REQUIREMENTS:

1. Generate exactly {len(scenarios)} test case(s).
2. Preserve the supplied scenario order.
3. Use the supplied test ID exactly.
4. Follow the complete scenario description.
5. Do not replace a shopping journey with a login-only test.
6. Do not omit major business operations.
7. Do not generate additional test cases.
"""

        return f"""
USER REQUEST:

{user_prompt}

{scenario_instruction}

Generate executable SauceDemo Playwright test cases.

For TC_LOGIN_001, generate the complete shopping journey,
not merely a login test.

MANDATORY CHECKOUT ASSERTIONS:

Generate three separate assert_text steps:

1. target = item subtotal, value = $55.97
2. target = tax, value = $4.48
3. target = order total, value = $60.45

Do not use assert_visible for any of these three checks.

For the cart count, use assert_text with value 3.

For order confirmation, use assert_text with target
"order confirmation" and exact value
"Thank you for your order!".

Use the target "cart products" for cart verification.
Use the target "inventory products are visible" only
for inventory verification.

Check every requested scenario before returning JSON.
Return only JSON matching the supplied schema.
"""

    # --------------------------------------------------
    # GENERATE USING GROQ
    # --------------------------------------------------

    def _generate_with_groq(self, user_prompt):

        print("\nConnecting to Groq AI...")
        print(f"Model: {self.model}")

        response = self.client.chat.completions.create(

            model=self.model,

            messages=[
                {
                    "role": "system",
                    "content": self._build_instructions()
                },
                {
                    "role": "user",
                    "content": self._build_prompt(user_prompt)
                }
            ],

            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "test_suite",
                    "strict": True,
                    "schema": self._get_json_schema()
                }
            },

            reasoning_effort="low",
            max_completion_tokens=8192
        )

        if not response.choices:

            raise RuntimeError(
                "Groq returned no response choices."
            )

        choice = response.choices[0]

        if choice.finish_reason == "length":

            raise RuntimeError(
                "Groq response reached its token limit."
            )

        if choice.message.refusal:

            raise RuntimeError(
                f"Groq refused the request: "
                f"{choice.message.refusal}"
            )

        content = choice.message.content

        if not content:

            raise RuntimeError(
                "Groq returned an empty response."
            )

        result = TestSuite.model_validate_json(content)

        # Diagnostic output.
        print("\n========== GENERATED TEST STEPS ==========")

        for test_case in result.test_cases:

            print(
                f"\n{test_case.id}: {test_case.title}"
            )

            for index, step in enumerate(
                test_case.steps,
                start=1
            ):

                print(
                    f"{index}. ACTION={step.action} | "
                    f"TARGET={step.target} | "
                    f"VALUE={step.value} | "
                    f"EXPECTED={step.expected_result}"
                )

        print("\n==========================================")

        # This validation runs BEFORE Playwright execution.
        self._validate_scenario_coverage(
            user_prompt,
            result.test_cases
        )

        print("\nGroq generation successful.")
        print("JSON validation successful.")
        print("Pydantic schema validation successful.")

        return result

    # --------------------------------------------------
    # PUBLIC GENERATION METHOD
    # --------------------------------------------------

    def generate_test_cases(self, user_prompt):

        if not user_prompt or not user_prompt.strip():

            raise ValueError(
                "Please provide a testing requirement."
            )

        try:

            result = self._generate_with_groq(user_prompt)

            test_cases = [
                test_case.model_dump()
                for test_case in result.test_cases
            ]

            return {
                "message": (
                    "Groq AI test cases generated successfully."
                ),
                "provider": "Groq",
                "model": self.model,
                "total_test_cases": len(test_cases),
                "test_cases": test_cases
            }

        except ValidationError as error:

            raise RuntimeError(
                f"AI returned data that failed "
                f"Pydantic validation: {error}"
            ) from error

        except Exception as error:

            raise RuntimeError(
                f"Groq test generation failed: {error}"
            ) from error


# --------------------------------------------------
# STANDALONE EXECUTION
# --------------------------------------------------

if __name__ == "__main__":

    try:

        generator = AITestGenerator()

        prompt = input(
            "\nDescribe what you want to test: "
        )

        result = generator.generate_test_cases(prompt)

        print("\nAI GENERATED TEST CASES\n")

        print(
            json.dumps(
                result,
                indent=4,
                ensure_ascii=False
            )
        )

    except KeyboardInterrupt:

        print("\nExecution cancelled by user.")

    except Exception as error:

        print(
            f"\nAI TEST GENERATOR ERROR: {error}"
        )
