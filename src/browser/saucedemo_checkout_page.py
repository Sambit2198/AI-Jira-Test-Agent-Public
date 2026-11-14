
from src.browser.mouse_controller import MouseController


class SauceDemoCheckoutPage:

    def __init__(self, page):
        self.page = page
        self.mouse = MouseController(page)

    def click_checkout(self):

        checkout_button = self.page.locator("#checkout")

        # Physically move and click Checkout
        self.mouse.click(checkout_button)

        # Wait for Checkout Information page
        self.page.wait_for_url(
            "**/checkout-step-one.html",
            timeout=10000
        )

    def enter_first_name(self, first_name):

        first_name_field = self.page.locator("#first-name")

        # Physically move and click First Name
        self.mouse.click(first_name_field)

        # Enter first name
        first_name_field.fill(first_name)

    def enter_last_name(self, last_name):

        last_name_field = self.page.locator("#last-name")

        # Physically move and click Last Name
        self.mouse.click(last_name_field)

        # Enter last name
        last_name_field.fill(last_name)

    def enter_postal_code(self, postal_code):

        postal_code_field = self.page.locator("#postal-code")

        # Physically move and click Postal Code
        self.mouse.click(postal_code_field)

        # Enter postal code
        postal_code_field.fill(postal_code)

    def click_continue(self):

        continue_button = self.page.locator("#continue")

        # Physically move and click Continue
        self.mouse.click(continue_button)

        # Wait for Checkout Overview navigation
        self.page.wait_for_url(
            "**/checkout-step-two.html",
            timeout=10000
        )

    def is_checkout_overview_open(self):

        return "checkout-step-two.html" in self.page.url

    def get_checkout_product_names(self):

        return self.page.locator(
            ".inventory_item_name"
        ).all_text_contents()

    def get_subtotal(self):

        return self.page.locator(
            ".summary_subtotal_label"
        ).inner_text()

    def get_tax(self):

        return self.page.locator(
            ".summary_tax_label"
        ).inner_text()

    def get_total(self):

        return self.page.locator(
            ".summary_total_label"
        ).inner_text()

    def click_finish(self):

        finish_button = self.page.locator("#finish")

        # Physically move and click Finish
        self.mouse.click(finish_button)

        # Wait for Order Confirmation page
        self.page.wait_for_url(
            "**/checkout-complete.html",
            timeout=10000
        )

    def is_order_confirmation_open(self):

        return "checkout-complete.html" in self.page.url

    def get_order_confirmation_message(self):

        return self.page.locator(
            ".complete-header"
        ).inner_text()

    
    def click_back_home(self):

        back_home_button = self.page.locator("#back-to-products")

        # Physically move the Windows cursor and click Back Home
        self.mouse.click(back_home_button)

        # Wait for Inventory page navigation
        self.page.wait_for_url(
            "**/inventory.html",
            timeout=10000
        )

    def is_back_home_navigation_successful(self):

        return "inventory.html" in self.page.url
