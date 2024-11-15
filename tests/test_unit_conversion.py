from playwright.sync_api import Playwright, sync_playwright


def test_unit_conversion(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Open the application page and load with initial parameters (only open once)
    page.goto(
        "http://localhost:9090/?id-dbt-input=25.0&id-tr-input=25.0&id-v-input=0.1&id-rh-input=50.0&id-met-input=1.0&id-clo-input=0.61&id-unit-toggle=SI&id-model-selection=PMV_ashrae&id-chart-selection=Temperature+vs.+Relative+Humidity&id-functionality-selection=Default")

    # Define the input fields to validate unit conversion and their conversion formulas
    input_selectors = {
        "id-dbt-input": ("Dry-bulb Temperature", lambda x: x * 9 / 5 + 32),  # Celsius to Fahrenheit
        "id-tr-input": ("Mean Radiant Temperature", lambda x: x * 9 / 5 + 32),
        "id-v-input": ("Air Velocity", lambda x: x * 3.28084)  # m/s to ft/s
    }

    # Record values in the initial (SI) units
    initial_values = {}
    for selector in input_selectors.keys():
        initial_values[selector] = float(page.locator(f"#{selector}").input_value())

    # Click the unit toggle button (switch to IP units)
    unit_toggle_button = page.locator("#id-inputs-form span").nth(1)
    unit_toggle_button.click()

    # Click the relevant input fields to ensure unit conversion takes effect
    for selector in input_selectors.keys():
        page.locator(f"#{selector}").click()

    # Validate values after unit conversion
    for selector, (description, conversion_fn) in input_selectors.items():
        # Get the value after conversion
        updated_value = float(page.locator(f"#{selector}").input_value())
        expected_value = conversion_fn(initial_values[selector])  # Calculate expected value

        # Assert the conversion is correct (allowing for some floating-point error)
        assert abs(
            updated_value - expected_value) < 0.1, f"{description} unit conversion failed: expected {expected_value}, got {updated_value}"

    print("First unit conversion test passed.")

    # Click the unit toggle button again (switch back to SI units)
    unit_toggle_button.click()

    # Click the relevant input fields to ensure unit conversion back to SI units takes effect
    for selector in input_selectors.keys():
        page.locator(f"#{selector}").click()

    # Validate values after reverting back to SI units
    for selector, (description, _) in input_selectors.items():
        # Get the value after reverting back to SI units
        reverted_value = float(page.locator(f"#{selector}").input_value())
        initial_value = initial_values[selector]  # Original SI unit value

        # Assert the reversion is correct
        assert abs(
            reverted_value - initial_value) < 0.1, f"{description} unit reversion failed: expected {initial_value}, got {reverted_value}"

    print("Second unit conversion (reversion) test passed.")

    # Close the context and browser
    context.close()
    browser.close()


# Run the test using sync_playwright
with sync_playwright() as playwright:
    test_unit_conversion(playwright)
