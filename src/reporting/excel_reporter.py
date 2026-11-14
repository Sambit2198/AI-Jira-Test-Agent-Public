
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule
from datetime import datetime
from pathlib import Path


class ExcelReporter:

    TEST_CASES = {
        # Login test cases
        "test_valid_login": {
            "id": "TC_LOGIN_001",
            "module": "Login",
            "steps": (
                "1. Open SauceDemo\n"
                "2. Enter valid username\n"
                "3. Enter valid password\n"
                "4. Click Login\n"
                "5. Verify inventory page opens"
            ),
        },
        "test_invalid_username": {
            "id": "TC_LOGIN_002",
            "module": "Login",
            "steps": (
                "1. Open SauceDemo\n"
                "2. Enter invalid username\n"
                "3. Enter password\n"
                "4. Click Login\n"
                "5. Verify error message"
            ),
        },
        "test_invalid_password": {
            "id": "TC_LOGIN_003",
            "module": "Login",
            "steps": (
                "1. Open SauceDemo\n"
                "2. Enter valid username\n"
                "3. Enter invalid password\n"
                "4. Click Login\n"
                "5. Verify error message"
            ),
        },
        "test_empty_username": {
            "id": "TC_LOGIN_004",
            "module": "Login",
            "steps": (
                "1. Open SauceDemo\n"
                "2. Leave username empty\n"
                "3. Enter password\n"
                "4. Click Login\n"
                "5. Verify username-required error"
            ),
        },
        "test_empty_password": {
            "id": "TC_LOGIN_005",
            "module": "Login",
            "steps": (
                "1. Open SauceDemo\n"
                "2. Enter username\n"
                "3. Leave password empty\n"
                "4. Click Login\n"
                "5. Verify password-required error"
            ),
        },
        "test_both_fields_empty": {
            "id": "TC_LOGIN_006",
            "module": "Login",
            "steps": (
                "1. Open SauceDemo\n"
                "2. Leave username empty\n"
                "3. Leave password empty\n"
                "4. Click Login\n"
                "5. Verify username-required error"
            ),
        },
        "test_locked_out_user": {
            "id": "TC_LOGIN_007",
            "module": "Login",
            "steps": (
                "1. Open SauceDemo\n"
                "2. Enter locked-out username\n"
                "3. Enter password\n"
                "4. Click Login\n"
                "5. Verify locked-out error message"
            ),
        },
        "test_password_is_masked": {
            "id": "TC_LOGIN_008",
            "module": "Login",
            "steps": (
                "1. Open SauceDemo\n"
                "2. Inspect password field\n"
                "3. Verify password field uses masking"
            ),
        },

        # Inventory and checkout test cases
        "test_inventory_page_opens_after_login": {
            "id": "TC_INVENTORY_001",
            "module": "Inventory",
            "steps": (
                "1. Open SauceDemo\n"
                "2. Log in with valid credentials\n"
                "3. Verify inventory page is displayed"
            ),
        },
        "test_all_products_are_displayed": {
            "id": "TC_INVENTORY_002",
            "module": "Inventory",
            "steps": (
                "1. Log in to SauceDemo\n"
                "2. Open the inventory page\n"
                "3. Verify all six products are displayed"
            ),
        },
        "test_all_product_names_are_displayed": {
            "id": "TC_INVENTORY_003",
            "module": "Inventory",
            "steps": (
                "1. Log in to SauceDemo\n"
                "2. Retrieve displayed product names\n"
                "3. Verify product names against the expected list"
            ),
        },
        "test_all_product_prices_are_displayed": {
            "id": "TC_INVENTORY_004",
            "module": "Inventory",
            "steps": (
                "1. Log in to SauceDemo\n"
                "2. Retrieve displayed product prices\n"
                "3. Verify prices against the expected values"
            ),
        },
        "test_all_product_descriptions_are_displayed": {
            "id": "TC_INVENTORY_005",
            "module": "Inventory",
            "steps": (
                "1. Log in to SauceDemo\n"
                "2. Inspect each displayed product\n"
                "3. Verify product descriptions are present"
            ),
        },
        "test_sort_products_by_name_ascending": {
            "id": "TC_INVENTORY_006",
            "module": "Inventory",
            "steps": (
                "1. Log in to SauceDemo\n"
                "2. Select name ascending sort\n"
                "3. Verify products are sorted A to Z"
            ),
        },
        "test_sort_products_by_name_descending": {
            "id": "TC_INVENTORY_007",
            "module": "Inventory",
            "steps": (
                "1. Log in to SauceDemo\n"
                "2. Select name descending sort\n"
                "3. Verify products are sorted Z to A"
            ),
        },
        "test_sort_products_by_price_ascending": {
            "id": "TC_INVENTORY_008",
            "module": "Inventory",
            "steps": (
                "1. Log in to SauceDemo\n"
                "2. Select price ascending sort\n"
                "3. Verify prices are sorted lowest to highest"
            ),
        },
        "test_add_product_to_cart": {
            "id": "TC_INVENTORY_009",
            "module": "Inventory",
            "steps": (
                "1. Log in to SauceDemo\n"
                "2. Select a product\n"
                "3. Add the product to the cart\n"
                "4. Verify the cart count is updated"
            ),
        },
        "test_product_is_displayed_in_cart": {
            "id": "TC_INVENTORY_010",
            "module": "Inventory",
            "steps": (
                "1. Log in to SauceDemo\n"
                "2. Add a product to the cart\n"
                "3. Open the cart\n"
                "4. Verify the product and price are displayed"
            ),
        },
        "test_enter_checkout_information": {
            "id": "TC_INVENTORY_011",
            "module": "Inventory",
            "steps": (
                "1. Log in to SauceDemo\n"
                "2. Add products to the cart\n"
                "3. Proceed to checkout\n"
                "4. Enter customer information\n"
                "5. Continue to the next checkout stage"
            ),
        },
        "test_checkout_overview": {
            "id": "TC_INVENTORY_012",
            "module": "Inventory",
            "steps": (
                "1. Log in to SauceDemo\n"
                "2. Add products to the cart\n"
                "3. Enter checkout information\n"
                "4. Verify checkout products and prices\n"
                "5. Verify subtotal, tax, and total\n"
                "6. Complete the order\n"
                "7. Verify order confirmation"
            ),
        },
    }

    def __init__(self, module="Login"):

        self.results = []
        self.module = module

        self.project_root = Path(__file__).resolve().parents[2]
        self.report_folder = self.project_root / "reports"
        self.report_folder.mkdir(
            parents=True,
            exist_ok=True
        )

    def add_result(self, result):
        self.results.append(result)

    def generate_report(self):

        workbook = Workbook()

        # --------------------------------------------------
        # Worksheet 1: Test Summary
        # --------------------------------------------------

        summary = workbook.active
        summary.title = "Test Summary"

        passed = sum(
            1 for result in self.results
            if result.get("status") == "PASSED"
        )

        failed = sum(
            1 for result in self.results
            if result.get("status") == "FAILED"
        )

        total_duration = sum(
            float(result.get("duration", 0) or 0)
            for result in self.results
        )

        summary_data = [
            ["SAUCEDEMO TEST EXECUTION REPORT"],
            ["Project", "AI Jira Test Agent"],
            ["Application", "SauceDemo"],
            ["Automation Tool", "Python + Playwright + Pytest + Gemini AI"],
            ["Report Scope", self.module],
            ["Execution Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Total Tests", len(self.results)],
            ["Passed", passed],
            ["Failed", failed],
            ["Total Execution Duration (seconds)", round(total_duration, 2)],
            ["Overall Status", "PASSED" if failed == 0 else "FAILED"],
        ]

        for row in summary_data:
            summary.append(row)

        summary.merge_cells("A1:B1")

        summary["A1"].font = Font(
            bold=True,
            size=16,
            color="FFFFFF"
        )

        summary["A1"].fill = PatternFill(
            start_color="1F4E78",
            end_color="1F4E78",
            fill_type="solid"
        )

        summary["A1"].alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

        summary.row_dimensions[1].height = 30

        for row in range(2, summary.max_row + 1):
            summary.cell(row, 1).font = Font(bold=True)

        summary.column_dimensions["A"].width = 42
        summary.column_dimensions["B"].width = 38

        # --------------------------------------------------
        # Worksheet 2: Test Details
        # --------------------------------------------------

        details = workbook.create_sheet("Test Details")

        details.append([
            "Module",
            "Test ID",
            "Test Scenario",
            "Test Steps",
            "Start Time",
            "End Time",
            "Expected Result",
            "Actual Result",
            "Status",
            "Duration (seconds)"
        ])

        for index, result in enumerate(self.results, start=1):

            test_name = result.get(
                "test_name",
                "Untitled Test"
            )

            test_information = self.TEST_CASES.get(
                test_name,
                {}
            )

            # Preserve AI-generated test IDs.
            test_id = result.get(
                "test_case_id",
                test_information.get(
                    "id",
                    f"{self.module.upper()}-{index:03d}"
                )
            )

            # Prefer the module supplied by the result.
            test_module = result.get(
                "module",
                test_information.get(
                    "module",
                    self.module
                )
            )

            # Use dynamically generated AI steps when available.
            if result.get("steps"):

                test_steps = "\n".join(
                    (
                        f"{step_number}. "
                        f"{step.get('description', 'Execution Step')}"
                    )
                    for step_number, step in enumerate(
                        result["steps"],
                        start=1
                    )
                )

            else:

                test_steps = test_information.get(
                    "steps",
                    "Steps not defined."
                )

            details.append([
                test_module,
                test_id,
                result.get("title", test_name),
                test_steps,
                result.get("start_time", "Not recorded"),
                result.get("end_time", "Not recorded"),
                result.get("expected_result", "Not specified"),
                result.get("actual_result", "Not recorded"),
                result.get("status", "NOT RECORDED"),
                result.get("duration", 0)
            ])

        details.freeze_panes = "A2"
        details.auto_filter.ref = details.dimensions

        # --------------------------------------------------
        # Worksheet 3: Execution Logs
        # --------------------------------------------------

        logs = workbook.create_sheet("Execution Logs")

        logs.append([
            "Module",
            "Test Name",
            "Execution Log",
            "Failure Details"
        ])

        for result in self.results:

            test_name = result.get(
                "test_name",
                "Untitled Test"
            )

            test_information = self.TEST_CASES.get(
                test_name,
                {}
            )

            logs.append([
                result.get(
                    "module",
                    test_information.get("module", self.module)
                ),
                test_name,
                result.get("logs", ""),
                result.get("failure", "")
            ])

        logs.freeze_panes = "A2"
        logs.auto_filter.ref = logs.dimensions

        # --------------------------------------------------
        # Formatting
        # --------------------------------------------------

        header_fill = PatternFill(
            start_color="1F4E78",
            end_color="1F4E78",
            fill_type="solid"
        )

        header_font = Font(
            bold=True,
            color="FFFFFF"
        )

        thin_border = Border(
            bottom=Side(
                style="thin",
                color="D9E2F3"
            )
        )

        for worksheet in [details, logs]:

            for cell in worksheet[1]:

                cell.font = header_font
                cell.fill = header_fill

                cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center",
                    wrap_text=True
                )

            worksheet.row_dimensions[1].height = 30

            for row in worksheet.iter_rows(min_row=2):

                for cell in row:

                    cell.alignment = Alignment(
                        vertical="top",
                        wrap_text=True
                    )

                    cell.border = thin_border

            for column in worksheet.columns:

                column_letter = get_column_letter(
                    column[0].column
                )

                max_length = max(
                    (
                        len(str(cell.value))
                        for cell in column
                        if cell.value is not None
                    ),
                    default=10
                )

                worksheet.column_dimensions[column_letter].width = min(
                    max(max_length + 4, 15),
                    55
                )

        # Set practical widths for Test Details.
        details.column_dimensions["A"].width = 16
        details.column_dimensions["B"].width = 20
        details.column_dimensions["C"].width = 38
        details.column_dimensions["D"].width = 55
        details.column_dimensions["E"].width = 22
        details.column_dimensions["F"].width = 22
        details.column_dimensions["G"].width = 45
        details.column_dimensions["H"].width = 45
        details.column_dimensions["I"].width = 14
        details.column_dimensions["J"].width = 22

        for row in range(2, details.max_row + 1):
            details.row_dimensions[row].height = 90

        # Highlight PASSED and FAILED statuses.
        status_column = "I"

        if details.max_row >= 2:

            details.conditional_formatting.add(
                f"{status_column}2:{status_column}{details.max_row}",
                CellIsRule(
                    operator="equal",
                    formula=['"PASSED"'],
                    fill=PatternFill(
                        start_color="E2F0D9",
                        end_color="E2F0D9",
                        fill_type="solid"
                    ),
                    font=Font(
                        color="006100",
                        bold=True
                    )
                )
            )

            details.conditional_formatting.add(
                f"{status_column}2:{status_column}{details.max_row}",
                CellIsRule(
                    operator="equal",
                    formula=['"FAILED"'],
                    fill=PatternFill(
                        start_color="FCE4D6",
                        end_color="FCE4D6",
                        fill_type="solid"
                    ),
                    font=Font(
                        color="9C0006",
                        bold=True
                    )
                )
            )

        # --------------------------------------------------
        # Save Excel Report
        # --------------------------------------------------

        filename = (
            "SauceDemo_"
            + self.module
            + "_Report_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".xlsx"
        )

        report_path = self.report_folder / filename

        workbook.save(report_path)

        print(
            f"\nExcel report generated: {report_path}"
        )

        return report_path
