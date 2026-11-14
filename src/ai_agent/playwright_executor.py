
import re
from datetime import datetime
from pathlib import Path
from time import perf_counter

from playwright.sync_api import Page, expect

from src.browser.mouse_controller import MouseController
from src.reporting.screenshot_manager import ScreenshotManager


class PlaywrightExecutor:

    def __init__(self, page: Page):
        self.page = page
        self.mouse = MouseController(page)
        self.screenshot_manager = ScreenshotManager(page)

    # --------------------------------------------------
    # 1. RESOLVE AI-GENERATED TARGETS
    # --------------------------------------------------

    def resolve_target(self, target: str):

        normalized = re.sub(
            r"\s+", " ", target
        ).strip().casefold()

        targets = {
            # Login
            "username input field": '[data-test="username"]',
            "username field": '[data-test="username"]',
            "username input": '[data-test="username"]',
            "password input field": '[data-test="password"]',
            "password field": '[data-test="password"]',
            "password input": '[data-test="password"]',
            "login button": '[data-test="login-button"]',
            "login": '[data-test="login-button"]',
            "error message": '[data-test="error"]',
            "error": '[data-test="error"]',
            "login error message": '[data-test="error"]',

            # Inventory
            "inventory page": ".inventory_list",
            "inventory products": ".inventory_item",
            "inventory products are visible": ".inventory_item",
            "all inventory products": ".inventory_item",
            "all six products": ".inventory_item",
            "six inventory products": ".inventory_item",
            "product list": ".inventory_list",
            "products heading": ".title",
            "products page heading": ".title",
            "product heading": ".title",
            "inventory heading": ".title",
            "inventory page header": ".title",
            "inventory page heading": ".title",
            "products title": ".title",
            "page title": ".title",

            # Cart
            "shopping cart": ".shopping_cart_link",
            "cart icon": ".shopping_cart_link",
            "shopping cart icon": ".shopping_cart_link",
            "cart": ".shopping_cart_link",
            "cart badge": ".shopping_cart_badge",
            "cart item": ".cart_item",
            "cart products": ".cart_item",
            "cart items": ".cart_item",
            "cart contents": ".cart_item",
            "three products in cart": ".cart_item",
            "all three cart products": ".cart_item",

            # Sorting
            "product sorting dropdown": '[data-test="product-sort-container"]',
            "sorting dropdown": '[data-test="product-sort-container"]',

            # Checkout
            "checkout button": '[data-test="checkout"]',
            "first name field": '[data-test="firstName"]',
            "last name field": '[data-test="lastName"]',
            "postal code field": '[data-test="postalCode"]',
            "continue button": '[data-test="continue"]',
            "finish button": '[data-test="finish"]',
            "back home button": '[data-test="back-to-products"]',

            # Checkout overview
            "item subtotal": ".summary_subtotal_label",
            "subtotal": ".summary_subtotal_label",
            "tax": ".summary_tax_label",
            "tax amount": ".summary_tax_label",
            "order total": ".summary_total_label",
            "total": ".summary_total_label",

            # Confirmation
            "order confirmation": ".complete-header",
            "confirmation message": ".complete-header",
            "order confirmation message": ".complete-header",
        }

        if normalized in targets:
            return self.page.locator(targets[normalized])

        # Product-specific cart or inventory target
        match = re.match(
            r"^(?:add|select)\s+(.+?)\s+(?:to cart|to the cart)$",
            normalized
        )

        if match:
            product_name = match.group(1)

            product_pattern = re.compile(
                re.escape(product_name),
                re.IGNORECASE
            )

            if self.page.locator(".cart_item").count() > 0:
                return self.page.locator(
                    ".cart_item"
                ).filter(has_text=product_pattern)

            product = self.page.locator(
                ".inventory_item"
            ).filter(has_text=product_pattern)

            return product.get_by_role(
                "button",
                name=re.compile("add to cart", re.IGNORECASE)
            )

        # Product-specific cart removal
        match = re.match(
            r"^remove\s+(.+?)\s+from cart$",
            normalized
        )

        if match:
            product_name = match.group(1)

            product = self.page.locator(
                ".cart_item"
            ).filter(
                has_text=re.compile(
                    re.escape(product_name),
                    re.IGNORECASE
                )
            )

            return product.get_by_role(
                "button",
                name=re.compile("remove", re.IGNORECASE)
            )

        raise ValueError(
            f"Unsupported target: {target}. "
            "Please add its locator mapping."
        )

    # --------------------------------------------------
    # 2. NORMALIZE TEXT
    # --------------------------------------------------

    @staticmethod
    def normalize_text(text: str):
        text = re.sub(r"\s+", " ", text).strip()
        text = text.rstrip(".!?")
        return text.casefold()

    # --------------------------------------------------
    # 3. CONTROLLED WAIT
    # --------------------------------------------------

    def wait(self, milliseconds=700):
        self.page.wait_for_timeout(milliseconds)

    # --------------------------------------------------
    # 4. PHYSICAL MOUSE CLICK
    # --------------------------------------------------

    def physical_click(self, locator):
        locator.wait_for(state="visible")
        locator.scroll_into_view_if_needed()
        self.wait(500)
        self.mouse.click(locator)
        self.wait(500)

    # --------------------------------------------------
    # 5. SCREENSHOT
    # --------------------------------------------------

    def capture_step_screenshot(
        self, test_case_id, step_number, status
    ):
        try:
            screenshot_path = self.screenshot_manager.capture(
                test_case_id,
                f"Step_{step_number}_{status}"
            )
            return str(Path(screenshot_path).resolve())

        except Exception as screenshot_error:
            print(f"Screenshot capture failed: {screenshot_error}")
            return None

    # --------------------------------------------------
    # 6. VERIFY INVENTORY PRODUCTS
    # --------------------------------------------------

    def verify_inventory_products(self):

        if "/inventory.html" not in self.page.url:
            raise AssertionError(
                "Inventory verification was requested "
                f"on the wrong page: {self.page.url}"
            )

        locator = self.page.locator(".inventory_item")

        expect(locator).to_have_count(6)
        expect(locator.first).to_be_visible()

        return (
            "Inventory verification passed. "
            "All 6 products are displayed."
        )

    # --------------------------------------------------
    # 7. VERIFY CART PRODUCTS
    # --------------------------------------------------

    def verify_cart_products(self):

        expected_products = [
            "Sauce Labs Backpack",
            "Sauce Labs Bike Light",
            "Sauce Labs Bolt T-Shirt",
        ]

        cart_items = self.page.locator(".cart_item")

        expect(cart_items).to_have_count(3)

        for product_name in expected_products:

            product = cart_items.filter(
                has_text=re.compile(
                    re.escape(product_name),
                    re.IGNORECASE
                )
            )

            expect(product).to_have_count(1)
            expect(product).to_be_visible()

        return (
            "Cart verification passed. "
            "All 3 expected products are present."
        )

    # --------------------------------------------------
    # 8. EXECUTE INDIVIDUAL STEP
    # --------------------------------------------------

    def execute_step(self, step: dict):

        action = step["action"]
        target = step.get("target", "")
        value = step.get("value", "")
        expected_result = step.get("expected_result", "")

        actual_result = ""

        normalized_target = re.sub(
            r"\s+", " ", target
        ).strip().casefold()

        print(f"\nAction: {action}")
        print(f"Target: {target}")

        if action == "navigate":

            if not target.startswith(("http://", "https://")):
                raise ValueError("Invalid navigation URL.")

            self.wait(500)

            response = self.page.goto(
                target,
                wait_until="domcontentloaded"
            )

            self.wait(1500)

            actual_result = (
                f"Browser navigated to {self.page.url}."
            )

            if response is not None:
                actual_result += (
                    f" HTTP response status: {response.status}."
                )

                if response.status >= 400:
                    raise AssertionError(
                        f"Navigation returned HTTP status {response.status}."
                    )

        elif action == "fill":

            locator = self.resolve_target(target)
            self.physical_click(locator)

            locator.press_sequentially(
                value,
                delay=120
            )

            self.wait(500)

            actual_result = (
                f"Input field '{target}' was "
                f"{'populated' if value else 'left empty'}."
            )

        elif action == "click":

            locator = self.resolve_target(target)
            self.physical_click(locator)

            actual_result = (
                f"Physical mouse click on '{target}' completed."
            )

        elif action == "select":

            locator = self.resolve_target(target)
            locator.wait_for(state="visible")
            locator.scroll_into_view_if_needed()

            self.physical_click(locator)
            locator.select_option(label=value)

            self.wait(1000)

            actual_result = (
                f"Selected '{value}' in '{target}'."
            )

        elif action == "assert_text":

            locator = self.resolve_target(target)

            if not value:
                raise ValueError(
                    "assert_text requires expected text."
                )

            expect(locator).to_be_visible()

            actual_text = locator.inner_text()

            if self.normalize_text(value) not in self.normalize_text(actual_text):
                raise AssertionError(
                    f"Expected '{value}', actual text was '{actual_text}'."
                )

            actual_result = (
                f"Text verification passed. "
                f"Expected: '{value}'. Actual: '{actual_text}'."
            )

        elif action == "assert_url":

            if not value:
                raise ValueError(
                    "assert_url requires an expected URL."
                )

            expect(self.page).to_have_url(
                re.compile(re.escape(value))
            )

            actual_result = (
                f"URL verification passed. Current URL: {self.page.url}."
            )

        elif action == "assert_visible":

            # Inventory verification
            if normalized_inventory_target(target):

                actual_result = self.verify_inventory_products()

            # Cart verification
            elif normalized_target in {
                "cart products",
                "cart items",
                "cart contents",
                "three products in cart",
                "all three cart products",
            }:

                if "/cart.html" not in self.page.url:
                    raise AssertionError(
                        "Cart verification was requested "
                        f"on the wrong page: {self.page.url}"
                    )

                actual_result = self.verify_cart_products()

            # General visibility verification
            else:

                locator = self.resolve_target(target)
                expect(locator).to_be_visible()

                actual_result = (
                    f"Visibility verification passed. "
                    f"'{target}' is displayed."
                )

        else:
            raise ValueError(f"Unsupported action: {action}")

        print("Step PASSED.")
        print(f"Expected: {expected_result}")
        print(f"Actual: {actual_result}")

        return {
            "action": action,
            "target": target,
            "value": value,
            "expected_result": expected_result,
            "actual_result": actual_result,
            "status": "PASS"
        }

    # --------------------------------------------------
    # 9. BUILD OVERALL RESULT
    # --------------------------------------------------

    def build_actual_result(self, results, status):

        verified_results = [
            result["actual_result"]
            for result in results
            if result.get("action", "").startswith("assert_")
            and result.get("status") == "PASS"
        ]

        failed_results = [
            result["actual_result"]
            for result in results
            if result.get("status") == "FAIL"
        ]

        if status == "PASS":
            if verified_results:
                return (
                    "Test execution completed successfully. "
                    "Verified application behaviour: "
                    + " ".join(verified_results)
                )

            return (
                "All executable steps completed, "
                "but no application assertions were performed."
            )

        if failed_results:
            return "Test execution failed. " + " ".join(failed_results)

        return (
            "Test execution failed before all expected "
            "application behaviours could be verified."
        )

    # --------------------------------------------------
    # 10. EXECUTE COMPLETE TEST CASE
    # --------------------------------------------------

    def execute_test_case(self, test_case: dict):

        results = []

        start_datetime = datetime.now()
        start_counter = perf_counter()

        print("\n" + "=" * 60)
        print(f"Executing: {test_case['id']}")
        print(f"Title: {test_case['title']}")
        print("=" * 60)

        for step_number, step in enumerate(
            test_case["steps"], start=1
        ):

            print(f"\nStep {step_number}")

            try:
                result = self.execute_step(step)

                result["screenshot"] = self.capture_step_screenshot(
                    test_case["id"],
                    step_number,
                    "PASS"
                )

                results.append(result)

            except Exception as error:

                screenshot_path = self.capture_step_screenshot(
                    test_case["id"],
                    step_number,
                    "FAIL"
                )

                results.append({
                    "action": step.get("action", ""),
                    "target": step.get("target", ""),
                    "value": step.get("value", ""),
                    "expected_result": step.get(
                        "expected_result", ""
                    ),
                    "actual_result": f"Step failed: {str(error)}",
                    "status": "FAIL",
                    "error": str(error),
                    "screenshot": screenshot_path
                })

                print(f"Step FAILED: {error}")
                break

        end_counter = perf_counter()
        end_datetime = datetime.now()

        duration = round(end_counter - start_counter, 2)

        status = (
            "PASS"
            if results
            and all(r["status"] == "PASS" for r in results)
            and len(results) == len(test_case["steps"])
            else "FAIL"
        )

        overall_actual_result = self.build_actual_result(
            results, status
        )

        failure_details = [
            result.get("error", "")
            for result in results
            if result.get("status") == "FAIL"
        ]

        print(f"\nTest Status: {status}")
        print(f"Execution Duration: {duration} seconds")
        print(f"Actual Result: {overall_actual_result}")

        return {
            "test_case_id": test_case["id"],
            "title": test_case["title"],
            "preconditions": test_case.get("preconditions", ""),
            "expected_result": test_case.get(
                "expected_result",
                "Expected result not provided."
            ),
            "status": status,
            "start_time": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": duration,
            "actual_result": overall_actual_result,
            "error": " | ".join(failure_details),
            "steps": results
        }


def normalized_inventory_target(target: str) -> bool:

    normalized = re.sub(
        r"\s+", " ", target
    ).strip().casefold()

    return normalized in {
        "inventory products",
        "inventory products are visible",
        "all inventory products",
        "all six products",
        "six inventory products",
    }
