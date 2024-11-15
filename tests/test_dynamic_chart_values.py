from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
import io


def compare_images(image1, image2):
    # Compare two images and return True if they are different
    diff = ImageChops.difference(image1, image2)
    return diff.getbbox() is not None


def test_dynamic_chart_values_by_screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to False to view the process
        page = browser.new_page()

        # Visit the application page
        page.goto("http://localhost:9090")  # Update port to 9090

        # Ensure the chart is loaded
        page.wait_for_selector(".nsewdrag", timeout=10000)
        chart_area = page.locator(".nsewdrag")  # Locate the chart area using locator

        # Simulate mouse movement over different positions on the chart and take screenshots
        page.hover(".nsewdrag", position={"x": 100, "y": 100})
        initial_screenshot = chart_area.screenshot()

        page.hover(".nsewdrag", position={"x": 200, "y": 200})
        updated_screenshot = chart_area.screenshot()

        # Convert screenshots to Image objects for comparison
        initial_image = Image.open(io.BytesIO(initial_screenshot))
        updated_image = Image.open(io.BytesIO(updated_screenshot))

        # Check if there is a difference between the screenshots
        assert compare_images(initial_image, updated_image), "The values in the red box did not change with mouse movement"

        print("Dynamic chart value screenshot comparison test passed")
        browser.close()


# Run the test
test_dynamic_chart_values_by_screenshot()
