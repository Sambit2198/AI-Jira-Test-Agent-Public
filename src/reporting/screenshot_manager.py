
import os
from pathlib import Path
from datetime import datetime


class ScreenshotManager:

    def __init__(self, page):
        self.page = page

        self.project_root = Path(__file__).resolve().parents[2]

        self.screenshot_folder = (
            self.project_root / "reports" / "screenshots"
        )

        self.screenshot_folder.mkdir(
            parents=True,
            exist_ok=True
        )

    def capture(self, test_name, step_name):

        # Get the currently running pytest test name
        current_test = os.environ.get(
            "PYTEST_CURRENT_TEST",
            "manual_execution"
        )

        current_test = current_test.split(" ")[0]
        current_test = current_test.split("::")[-1]

        # Clean the test and step names
        safe_test_name = current_test.replace(" ", "_")
        safe_module_name = test_name.replace(" ", "_")
        safe_step_name = step_name.replace(" ", "_")

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        filename = (
            f"{safe_test_name}_"
            f"{safe_module_name}_"
            f"{safe_step_name}_"
            f"{timestamp}.png"
        )

        screenshot_path = (
            self.screenshot_folder / filename
        )

        self.page.screenshot(
            path=str(screenshot_path),
            full_page=True
        )

        print(
            f"\nScreenshot captured: {screenshot_path}"
        )

        return screenshot_path
