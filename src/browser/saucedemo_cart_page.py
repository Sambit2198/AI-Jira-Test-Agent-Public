
from src.browser.mouse_controller import MouseController


class SauceDemoCartPage:

    def __init__(self, page):
        self.page = page
        self.mouse = MouseController(page)
        self.url = "https://www.saucedemo.com/cart.html"

    def open_cart(self):

        cart_button = self.page.locator(
            ".shopping_cart_link"
        )

        # Move the actual Windows cursor and physically click
        self.mouse.click(cart_button)

        # Wait until Cart page navigation completes
        self.page.wait_for_url(
            "**/cart.html",
            timeout=10000
        )

    def is_cart_page_open(self):

        return self.page.url == self.url

    def get_cart_product_names(self):

        return self.page.locator(
            ".inventory_item_name"
        ).all_text_contents()

    def get_cart_product_prices(self):

        return self.page.locator(
            ".inventory_item_price"
        ).all_text_contents()
