
import os
import sys


class MouseController:
    def __init__(self, page):
        self.page = page

    def click(self, locator):
        # Use Playwright clicks on Linux cloud servers.
        # Preserve physical mouse clicks on Windows locally.
        use_physical_mouse = (
            sys.platform == "win32"
            and os.getenv("PLAYWRIGHT_USE_PHYSICAL_MOUSE", "true").lower()
            == "true"
        )

        if not use_physical_mouse:
            locator.click()
            return

        import pyautogui

        locator.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)

        box = locator.bounding_box()

        if box is None:
            raise Exception("Element is not visible on screen.")

        x = box["x"] + box["width"] / 2
        y = box["y"] + box["height"] / 2

        browser = self.page.evaluate("""() => ({
            screenX: window.screenX,
            screenY: window.screenY,
            outerWidth: window.outerWidth,
            outerHeight: window.outerHeight,
            innerWidth: window.innerWidth,
            innerHeight: window.innerHeight,
            dpr: window.devicePixelRatio
        })""")

        border = (
            browser["outerWidth"] - browser["innerWidth"]
        ) / 2

        top_bar = (
            browser["outerHeight"]
            - browser["innerHeight"]
            - border
        )

        screen_x = (
            browser["screenX"] + border + x
        ) * browser["dpr"]

        screen_y = (
            browser["screenY"] + top_bar + y
        ) * browser["dpr"]

        pyautogui.moveTo(screen_x, screen_y, duration=1)
        pyautogui.sleep(0.5)
        pyautogui.click()
        pyautogui.sleep(0.5)
