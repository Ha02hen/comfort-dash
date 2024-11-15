import asyncio
from playwright.async_api import async_playwright

async def test_unit_conversion():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Open the application page and load the specified URL
        await page.goto(
            "http://localhost:9090/?id-dbt-input=25.0&id-tr-input=25.0&id-v-input=0.1&id-rh-input=50.0&id-met-input=1.0&id-clo-input=0.61&id-unit-toggle=SI&id-model-selection=PMV_ashrae&id-chart-selection=Temperature+vs.+Relative+Humidity&id-functionality-selection=Default")

        # Define input selectors for verifying unit conversion
        input_selectors = {
            "id-dbt-input": "Dry-bulb Temperature",
            "id-tr-input": "Mean Radiant Temperature",
            "id-v-input": "Air Velocity",
            # Additional input selectors can be added here
        }

        # Initial check: Record input values in SI units
        initial_values = {}
        for selector in input_selectors.keys():
            initial_values[selector] = float(await page.locator(f"#{selector}").input_value())

        # Click the unit toggle button to switch units from SI to IP
        unit_toggle_selector = "#id-unit-toggle"
        unit_toggle = page.locator(unit_toggle_selector)

        # Ensure the element is visible and within the viewport
        await unit_toggle.scroll_into_view_if_needed()
        await unit_toggle.wait_for(state="visible", timeout=10000)
        await unit_toggle.click()

        # Check after switching: Record input values in IP units and verify conversion
        for selector, description in input_selectors.items():
            updated_value = float(await page.locator(f"#{selector}").input_value())
            initial_value = initial_values[selector]

            # Verify if the unit conversion is correct (check based on expected conversion rules)
            if description == "Dry-bulb Temperature" or description == "Mean Radiant Temperature":
                # Celsius to Fahrenheit conversion
                expected_value = initial_value * 9 / 5 + 32
            elif description == "Air Velocity":
                # Meters per second to feet per second conversion
                expected_value = initial_value * 3.28084
            else:
                expected_value = initial_value  # Other units remain unchanged

            assert abs(
                updated_value - expected_value) < 0.1, f"{description} unit conversion failed: expected {expected_value}, got {updated_value}"

        print("Unit conversion test passed.")

        # Close browser context and page
        await context.close()
        await browser.close()

# Run asynchronous test
asyncio.run(test_unit_conversion())
