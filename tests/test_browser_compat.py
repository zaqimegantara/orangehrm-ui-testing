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
from selenium.common.exceptions import TimeoutException

# Import WebDriverManager classes
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService

# Load .env from root
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)

# Use GitHub secret or fallback (os.getenv returns None if not found, which is fine for driver.get later)
BASE_URL = os.getenv("BASE_URL")

# Detect if running in GitHub Actions
IS_CI = os.getenv("CI") == "true"
# Updated BROWSERS list: Always include Edge if you intend to test it in CI and locally
# The previous logic was explicitly excluding Edge when IS_CI was true.
BROWSERS = ["chrome", "firefox", "edge"]

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
            driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), options=options)

        elif browser == "firefox":
            options = FirefoxOptions()
            options.add_argument("--headless")
            service = FirefoxService(GeckoDriverManager().install(), timeout=180) # Try 180 seconds (3 minutes)
            driver = webdriver.Firefox(service=service, options=options)

        elif browser == "edge":
            # REMOVED: if IS_CI: pytest.skip("Edge is not supported in GitHub Actions runners.")
            # Now, Edge is supported and will be run in CI.
            options = EdgeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--user-agent=ngrok-skip-browser-warning")
            # Correct and single line for Edge driver initialization using webdriver-manager
            driver = webdriver.Edge(service=webdriver.EdgeService(EdgeChromiumDriverManager().install()), options=options)

        else:
            raise ValueError("Unsupported browser")

        driver.set_window_size(1920, 1080)
        wait = WebDriverWait(driver, 15)

        # Visit ngrok root
        driver.get(BASE_URL)
        print(f"[{browser}] Opened: {driver.current_url}")

        # Bypass ngrok warning (using specific exception for clarity)
        try:
            visit_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Visit Site')]"))
            )
            print(f"[{browser}] Clicking ngrok warning button...")
            visit_btn.click()
            time.sleep(1)
        except TimeoutException: # Catch TimeoutException if button not found
            print(f"[{browser}] No ngrok warning or button not found within timeout.")
        except Exception as e: # Catch other potential errors during warning bypass
            print(f"[{browser}] Error bypassing ngrok warning: {e}")

        # Go to login
        driver.get(BASE_URL + "/web/index.php/auth/login")
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

    except TimeoutException:
        if driver:
            driver.save_screenshot(f"error-{browser}.png")
        print(f"[{browser}] ❌ TimeoutException: Element not found or action timed out.")
        raise # Re-raise the exception to fail the test

    except Exception as e:
        if driver:
            driver.save_screenshot(f"error-{browser}.png")
        print(f"[{browser}] ❌ Unexpected error: {e}")
        raise # Re-raise the exception to fail the test

    finally:
        if driver:
            driver.quit()