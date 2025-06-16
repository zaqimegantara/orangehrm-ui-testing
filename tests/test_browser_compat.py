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

# Load .env from root
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)

# Use GitHub secret or fallback
BASE_URL = os.getenv("BASE_URL", "https://example.ngrok-free.app")

# Detect if running in GitHub Actions
IS_CI = os.getenv("CI") == "true"
BROWSERS = ["chrome", "firefox"] if IS_CI else ["chrome", "firefox", "edge"]

@pytest.mark.parametrize("browser", BROWSERS)
def test_login_browser_compat(browser):
    print(f"\n[{browser}] Starting test...")

    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--user-agent=ngrok-skip-browser-warning")
        driver = webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        if IS_CI:
            options.binary_location = "/usr/bin/firefox"
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)

    elif browser == "edge":
        if IS_CI:
            pytest.skip("Edge is not supported in GitHub Actions runners.")
        options = EdgeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Edge(options=options)

    else:
        raise ValueError("Unsupported browser")

    driver.set_window_size(1920, 1080)
    wait = WebDriverWait(driver, 15)

    try:
        # Visit ngrok root
        driver.get(BASE_URL)
        print(f"[{browser}] Opened: {driver.current_url}")

        # Bypass ngrok warning
        try:
            visit_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Visit Site')]"))
            )
            print(f"[{browser}] Clicking ngrok warning button...")
            visit_btn.click()
            time.sleep(1)
        except:
            print(f"[{browser}] No ngrok warning.")

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
        driver.save_screenshot(f"error-{browser}.png")
        print(f"[{browser}] ❌ TimeoutException.")
        raise

    except Exception as e:
        driver.save_screenshot(f"error-{browser}.png")
        print(f"[{browser}] ❌ Unexpected error: {e}")
        raise

    finally:
        driver.quit()
