
from src.browser.mouse_controller import MouseController


class SauceDemoInventoryPage:

    def __init__(self, page):
        self.page = page
        self.mouse = MouseController(page)
        self.url = "https://www.saucedemo.com/inventory.html"

    def is_inventory_page_open(self):
        return self.page.url == self.url

    def get_product_count(self):
        return self.page.locator(".inventory_item").count()

    def get_product_names(self):
        return self.page.locator(
            ".inventory_item_name"
        ).all_text_contents()

    def get_product_prices(self):
        return self.page.locator(
            ".inventory_item_price"
        ).all_text_contents()

    def get_product_descriptions(self):
        return self.page.locator(
            ".inventory_item_desc"
        ).all_text_contents()

    def sort_products(self, option):
        self.page.locator(
            ".product_sort_container"
        ).select_option(label=option)

    def add_product_to_cart(self, product_name):

        # Locate the exact product
        product = self.page.locator(
            ".inventory_item"
        ).filter(
            has=self.page.locator(
                ".inventory_item_name",
                has_text=product_name
            )
        )

        assert product.count() == 1, (
            f"Expected exactly one product named {product_name}."
        )

        # Locate Add to Cart button
        add_button = product.get_by_role(
            "button",
            name="Add to cart",
            exact=True
        )

        assert add_button.count() == 1, (
            f"Add to Cart button not found for {product_name}."
        )

        # Move the actual Windows cursor and click
        self.mouse.click(add_button)

        # Verify the product was added
        remove_button = product.get_by_role(
            "button",
            name="Remove",
            exact=True
        )

        assert remove_button.count() == 1, (
            f"{product_name} was not successfully added to the cart."
        )

        print(f"\nSuccessfully added: {product_name}")

    def get_cart_item_count(self):

        cart_badge = self.page.locator(
            ".shopping_cart_badge"
        )

        if cart_badge.count() == 0:
            return 0

        return int(cart_badge.inner_text())
