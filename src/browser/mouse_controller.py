
import pyautogui


class MouseController:

    def __init__(self, page):

        self.page = page

    def click(self, locator):

        # Make sure the element is visible
        locator.scroll_into_view_if_needed()

        self.page.wait_for_timeout(500)

        # Get element position inside browser
        box = locator.bounding_box()

        if box is None:
            raise Exception("Element is not visible on screen.")

        # Calculate element centre
        x = box["x"] + box["width"] / 2
        y = box["y"] + box["height"] / 2

        # Get browser window screen information
        browser = self.page.evaluate("""() => ({
            screenX: window.screenX,
            screenY: window.screenY,
            outerWidth: window.outerWidth,
            outerHeight: window.outerHeight,
            innerWidth: window.innerWidth,
            innerHeight: window.innerHeight,
            dpr: window.devicePixelRatio
        })""")

        # Calculate browser frame dimensions
        border = (
            browser["outerWidth"] - browser["innerWidth"]
        ) / 2

        top_bar = (
            browser["outerHeight"]
            - browser["innerHeight"]
            - border
        )

        # Convert browser coordinates to Windows coordinates
        screen_x = (
            browser["screenX"] + border + x
        ) * browser["dpr"]

        screen_y = (
            browser["screenY"] + top_bar + y
        ) * browser["dpr"]

        # Move actual Windows cursor
        pyautogui.moveTo(
            screen_x,
            screen_y,
            duration=1
        )

        pyautogui.sleep(0.5)

        # Physically click
        pyautogui.click()

        pyautogui.sleep(0.5)
