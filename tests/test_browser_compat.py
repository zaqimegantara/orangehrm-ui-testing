import os
import time
import logging
import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService


from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)

BASE_URL = os.getenv("BASE_URL", "")
USERNAME = os.getenv("TEST_USERNAME", "")
PASSWORD = os.getenv("TEST_PASSWORD", "")
IS_CI = os.getenv("CI") == "true"
BROWSERS = ["chrome", "firefox", "edge"]

@pytest.mark.parametrize("browser", BROWSERS)
def test_login_browser_compat(browser):
    logger.info(f"[{browser}] Starting test...")
    driver = None
    geckodriver_log_path = None

    try:
        # Browser setup
        if browser == "chrome":
            options = ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("user-agent=Mozilla/5.0 (ngrok-skip-browser-warning)")
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        elif browser == "firefox":
            options = FirefoxOptions()
            options.add_argument("--headless")
            geckodriver_log_path = os.path.join(os.getcwd(), "geckodriver_firefox.log")

            service = FirefoxService(
                GeckoDriverManager().install(),
                timeout=300,
                log_output=geckodriver_log_path
            )
            driver = webdriver.Firefox(service=service, options=options)

        elif browser == "edge":
            options = EdgeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("user-agent=Mozilla/5.0 (ngrok-skip-browser-warning)")
            driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

        else:
            raise ValueError(f"Unsupported browser: {browser}")

        driver.set_window_size(1920, 1080)
        wait = WebDriverWait(driver, 30)

        # Check URL setup
        if not BASE_URL or not USERNAME or not PASSWORD:
            raise ValueError("Missing BASE_URL, TEST_USERNAME, or TEST_PASSWORD in environment variables.")

        # Step 1: Visit base URL
        driver.get(BASE_URL)
        logger.info(f"[{browser}] Opened: {driver.current_url}")

        # Step 2: Handle ngrok warning if exists
        try:
            visit_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Visit Site')]"))
            )
            logger.info(f"[{browser}] Clicking ngrok warning button...")
            visit_btn.click()
            time.sleep(1)
        except TimeoutException:
            logger.info(f"[{browser}] No ngrok warning found.")
        except Exception as e:
            logger.warning(f"[{browser}] Error bypassing ngrok warning: {e}")

        # Step 3: Navigate to login
        login_url = f"{BASE_URL}/web/index.php/auth/login"
        driver.get(login_url)
        logger.info(f"[{browser}] Navigated to login page.")
        driver.save_screenshot(f"before_login_elements_wait-{browser}.png")

        # Step 4: Login
        username_input = wait.until(EC.visibility_of_element_located((By.NAME, "username")))
        password_input = driver.find_element(By.NAME, "password")
        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        driver.find_element(By.TAG_NAME, "button").click()

        # Step 5: Wait for dashboard
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-topbar-header-breadcrumb-module")))
        driver.save_screenshot(f"login-{browser}.png")
        assert "dashboard" in driver.page_source.lower()
        logger.info(f"[{browser}] ✅ Login successful.")

    except (TimeoutException, WebDriverException) as e:
        if driver:
            driver.save_screenshot(f"error-{browser}.png")
        logger.error(f"[{browser}] ❌ Selenium error: {e}")
        raise

    except Exception as e:
        if driver:
            driver.save_screenshot(f"error-{browser}.png")
        logger.error(f"[{browser}] ❌ General error: {e}")
        raise

    finally:
        if driver:
            driver.quit()

        if browser == "firefox" and geckodriver_log_path and os.path.exists(geckodriver_log_path):
            print("\n--- Geckodriver log content ---")
            try:
                with open(geckodriver_log_path, 'r') as log_file:
                    print(log_file.read())
            except Exception as e:
                print(f"Could not read log file: {e}")
            print("--- End Geckodriver log ---")
