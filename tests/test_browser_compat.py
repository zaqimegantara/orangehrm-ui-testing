import pytest
import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException # Import WebDriverException

# Import WebDriverManager classes and their respective Service classes
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService # Explicitly import ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService # Explicitly import EdgeService


# Load .env from root
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)

# Use GitHub secret or fallback (os.getenv returns None if not found, which might cause issues later)
# It's safer to have a default empty string if BASE_URL is critical
BASE_URL = os.getenv("BASE_URL", "") # Added empty string default for safety. Make sure secret is set!

# Detect if running in GitHub Actions
IS_CI = os.getenv("CI") == "true"
BROWSERS = ["chrome", "firefox", "edge"] # Now truly includes all three for CI and local

@pytest.mark.parametrize("browser", BROWSERS)
def test_login_browser_compat(browser):
    print(f"\n[{browser}] Starting test...")

    driver = None # Initialize driver to None
    try:
        if browser == "chrome":
            options = ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--user-agent=ngrok-skip-browser-warning")
            # Correct way to use ChromeDriverManager with ChromeService
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        elif browser == "firefox":
            options = FirefoxOptions()
            options.add_argument("--headless")
            # Correct way to use GeckoDriverManager with FirefoxService
            # Increased timeout for Firefox as discussed
            service = FirefoxService(GeckoDriverManager().install(), timeout=180)
            driver = webdriver.Firefox(service=service, options=options)

        elif browser == "edge":
            options = EdgeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--user-agent=ngrok-skip-browser-warning")
            # --- THIS IS THE CRITICAL FIX FOR EDGE ---
            # Correct way to use EdgeChromiumDriverManager with EdgeService
            driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
            # --- END CRITICAL FIX ---

        else:
            raise ValueError("Unsupported browser")

        driver.set_window_size(1920, 1080)
        wait = WebDriverWait(driver, 30) # Increased the general wait timeout from 15 to 30 for stability

        # Visit ngrok root
        if not BASE_URL:
            raise ValueError("BASE_URL environment variable is not set. Please check your .env file or GitHub secret.")
        driver.get(BASE_URL)
        print(f"[{browser}] Opened: {driver.current_url}")

        # Bypass ngrok warning (using specific exception for clarity)
        try:
            visit_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Visit Site')]"))
            )
            print(f"[{browser}] Clicking ngrok warning button...")
            visit_btn.click()
            time.sleep(1) # Give a moment for redirect
        except TimeoutException:
            # This is okay if no ngrok warning is present or it's bypassed instantly by user-agent
            print(f"[{browser}] No ngrok warning or button not found within timeout.")
        except Exception as e:
            # Catch other potential errors during warning bypass, e.g., if page content isn't as expected
            print(f"[{browser}] Error during ngrok warning bypass: {e}")
            # Optionally, you might want to raise this if it's a critical early failure
            # raise

        # Go to login
        login_url = f"{BASE_URL}/web/index.php/auth/login"
        driver.get(login_url)
        print(f"[{browser}] Navigated to login page: {driver.current_url}")
        driver.save_screenshot(f"before_login_elements_wait-{browser}.png") # Screenshot for debugging

        username_input = wait.until(EC.visibility_of_element_located((By.NAME, "username")))
        password_input = driver.find_element(By.NAME, "password")
        username_input.send_keys("zaqimegantara")
        password_input.send_keys("rizkyzaqI3@")
        driver.find_element(By.TAG_NAME, "button").click()

        # Wait for dashboard
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-topbar-header-breadcrumb-module")))
        driver.save_screenshot(f"login-{browser}.png")
        assert "dashboard" in driver.page_source.lower()
        print(f"[{browser}] ✅ Login successful. Screenshot saved.")

    except (TimeoutException, WebDriverException) as e: # Catch WebDriverException for broader driver issues
        if driver:
            driver.save_screenshot(f"error-{browser}.png")
        print(f"[{browser}] ❌ Test failed with Selenium error: {e}")
        raise # Re-raise the exception to fail the test

    except Exception as e:
        if driver:
            driver.save_screenshot(f"error-{browser}.png")
        print(f"[{browser}] ❌ Unexpected general error: {e}")
        raise # Re-raise the exception to fail the test

    finally:
        if driver:
            driver.quit()