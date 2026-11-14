
from src.browser.saucedemo_login_page import SauceDemoLoginPage
from src.browser.saucedemo_inventory_page import SauceDemoInventoryPage
from src.browser.saucedemo_cart_page import SauceDemoCartPage
from src.browser.saucedemo_checkout_page import SauceDemoCheckoutPage
from src.reporting.screenshot_manager import ScreenshotManager


def test_saucedemo_complete_end_to_end_flow(page):

    # Initialize screenshot manager
    screenshots = ScreenshotManager(page)

    # --------------------------------------------------
    # 1. LOGIN PAGE
    # --------------------------------------------------

    login_page = SauceDemoLoginPage(page)

    print("\n1. OPENING SAUCEDEMO LOGIN PAGE")

    login_page.open()

    page.wait_for_timeout(1000)

    # Capture login page before credentials
    screenshots.capture(
        "e2e",
        "login_page_before_credentials"
    )

    print("\nLOGIN PAGE OPENED")

    # --------------------------------------------------
    # 2. ENTER LOGIN CREDENTIALS
    # --------------------------------------------------

    print("\n2. ENTERING LOGIN CREDENTIALS")

    login_page.enter_username("standard_user")
    login_page.enter_password("secret_sauce")

    # Verify password masking
    assert login_page.is_password_masked()

    # Capture credentials before clicking Login
    screenshots.capture(
        "e2e",
        "login_page_after_credentials"
    )

    print("\nLOGIN CREDENTIALS ENTERED")

    # --------------------------------------------------
    # 3. CLICK LOGIN AND VERIFY
    # --------------------------------------------------

    print("\n3. CLICKING LOGIN")

    login_page.click_login()

    page.wait_for_url("**/inventory.html", timeout=10000)

    inventory_page = SauceDemoInventoryPage(page)

    assert login_page.is_login_successful()
    assert inventory_page.is_inventory_page_open()

    screenshots.capture(
        "e2e",
        "login_successful"
    )

    print("\n3. LOGIN SUCCESSFUL")

    # --------------------------------------------------
    # 4. VERIFY INVENTORY AND PRODUCTS
    # --------------------------------------------------

    product_count = inventory_page.get_product_count()

    assert product_count == 6

    expected_names = [
        "Sauce Labs Backpack",
        "Sauce Labs Bike Light",
        "Sauce Labs Bolt T-Shirt",
        "Sauce Labs Fleece Jacket",
        "Sauce Labs Onesie",
        "Test.allTheThings() T-Shirt (Red)"
    ]

    product_names = inventory_page.get_product_names()

    assert product_names == expected_names

    expected_prices = [
        "$29.99",
        "$9.99",
        "$15.99",
        "$49.99",
        "$7.99",
        "$15.99"
    ]

    product_prices = inventory_page.get_product_prices()

    assert product_prices == expected_prices

    product_descriptions = (
        inventory_page.get_product_descriptions()
    )

    assert len(product_descriptions) == 6
    assert all(
        description.strip()
        for description in product_descriptions
    )

    screenshots.capture(
        "e2e",
        "inventory_products_verified"
    )

    print("\n4. ALL SIX PRODUCTS VERIFIED")

    # --------------------------------------------------
    # 5. VERIFY PRODUCT SORTING
    # --------------------------------------------------

    inventory_page.sort_products("Name (A to Z)")

    product_names = inventory_page.get_product_names()

    assert product_names == sorted(product_names)

    inventory_page.sort_products("Name (Z to A)")

    product_names = inventory_page.get_product_names()

    assert product_names == sorted(
        product_names,
        reverse=True
    )

    inventory_page.sort_products("Price (low to high)")

    product_prices = inventory_page.get_product_prices()

    actual_prices = [
        float(price.replace("$", ""))
        for price in product_prices
    ]

    expected_sorted_prices = [
        7.99,
        9.99,
        15.99,
        15.99,
        29.99,
        49.99
    ]

    assert actual_prices == expected_sorted_prices

    screenshots.capture(
        "e2e",
        "product_sorting_verified"
    )

    print("\n5. PRODUCT SORTING VERIFIED")

    # --------------------------------------------------
    # 6. ADD PRODUCTS TO CART
    # --------------------------------------------------

    inventory_page.add_product_to_cart(
        "Sauce Labs Backpack"
    )

    inventory_page.add_product_to_cart(
        "Sauce Labs Bike Light"
    )

    inventory_page.add_product_to_cart(
        "Sauce Labs Bolt T-Shirt"
    )

    cart_count = inventory_page.get_cart_item_count()

    assert cart_count == 3

    screenshots.capture(
        "e2e",
        "three_products_added_to_cart"
    )

    print("\n6. THREE PRODUCTS ADDED TO CART")

    # --------------------------------------------------
    # 7. OPEN AND VERIFY CART
    # --------------------------------------------------

    cart_page = SauceDemoCartPage(page)

    cart_page.open_cart()

    assert cart_page.is_cart_page_open()

    cart_product_names = (
        cart_page.get_cart_product_names()
    )

    cart_product_prices = (
        cart_page.get_cart_product_prices()
    )

    assert len(cart_product_names) == 3

    assert "Sauce Labs Backpack" in cart_product_names
    assert "Sauce Labs Bike Light" in cart_product_names
    assert "Sauce Labs Bolt T-Shirt" in cart_product_names

    assert "$29.99" in cart_product_prices
    assert "$9.99" in cart_product_prices
    assert "$15.99" in cart_product_prices

    screenshots.capture(
        "e2e",
        "cart_page_verified"
    )

    print("\n7. SHOPPING CART VERIFIED")

    # --------------------------------------------------
    # 8. CHECKOUT INFORMATION
    # --------------------------------------------------

    checkout_page = SauceDemoCheckoutPage(page)

    checkout_page.click_checkout()

    checkout_page.enter_first_name("John")
    checkout_page.enter_last_name("Smith")
    checkout_page.enter_postal_code("12345")

    assert page.locator("#first-name").input_value() == "John"
    assert page.locator("#last-name").input_value() == "Smith"
    assert page.locator("#postal-code").input_value() == "12345"

    screenshots.capture(
        "e2e",
        "checkout_information_entered"
    )

    checkout_page.click_continue()

    assert checkout_page.is_checkout_overview_open()

    print("\n8. CHECKOUT INFORMATION VERIFIED")

    # --------------------------------------------------
    # 9. VERIFY CHECKOUT OVERVIEW AND PRICE CALCULATIONS
    # --------------------------------------------------

    checkout_product_names = (
        checkout_page.get_checkout_product_names()
    )

    assert len(checkout_product_names) == 3

    assert "Sauce Labs Backpack" in checkout_product_names
    assert "Sauce Labs Bike Light" in checkout_product_names
    assert "Sauce Labs Bolt T-Shirt" in checkout_product_names

    subtotal = checkout_page.get_subtotal()
    tax = checkout_page.get_tax()
    total = checkout_page.get_total()

    print("\nCHECKOUT OVERVIEW")
    print("Products:", checkout_product_names)
    print("Subtotal:", subtotal)
    print("Tax:", tax)
    print("Total:", total)

    assert "$55.97" in subtotal
    assert "$4.48" in tax
    assert "$60.45" in total

    screenshots.capture(
        "e2e",
        "checkout_overview_verified"
    )

    print("\n9. CHECKOUT TOTALS VERIFIED")

    # --------------------------------------------------
    # 10. COMPLETE ORDER
    # --------------------------------------------------

    checkout_page.click_finish()

    assert checkout_page.is_order_confirmation_open()

    confirmation_message = (
        checkout_page.get_order_confirmation_message()
    )

    assert confirmation_message == "Thank you for your order!"

    screenshots.capture(
        "e2e",
        "order_confirmation"
    )

    print("\n10. ORDER COMPLETED SUCCESSFULLY")

    # --------------------------------------------------
    # 11. RETURN TO INVENTORY
    # --------------------------------------------------

    checkout_page.click_back_home()

    assert checkout_page.is_back_home_navigation_successful()

    screenshots.capture(
        "e2e",
        "back_home_inventory"
    )

    print("\n11. SUCCESSFULLY RETURNED TO INVENTORY")

    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------

    print("\n========================================")
    print("COMPLETE SAUCEDEMO FLOW PASSED")
    print("========================================")
