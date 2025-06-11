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

# Load BASE_URL from .env
load_dotenv()
BASE_URL = os.getenv("BASE_URL")

@pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
def test_login_browser_compat(browser):
    print(f"\n[{browser}] Starting test...")

    # --- Setup drivers ---
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
        # comment this line for visible debugging
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)

    elif browser == "edge":
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
        # STEP 1: Go to the base URL (not directly to login)
        driver.get(BASE_URL)
        print(f"[{browser}] Opened: {driver.current_url}")

        # STEP 2: Detect and click 'Visit Site' if on ngrok warning
        try:
            visit_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Visit Site')]"))
            )
            print(f"[{browser}] Ngrok warning detected. Clicking 'Visit Site'...")
            visit_btn.click()
            time.sleep(1)
        except:
            print(f"[{browser}] No ngrok warning or 'Visit Site' button not found.")

        # STEP 3: Now go to the actual login page
        driver.get(BASE_URL + "/web/index.php/auth/login")
        print(f"[{browser}] Navigated to login page.")

        # STEP 4: Perform login
        username_input = wait.until(EC.visibility_of_element_located((By.NAME, "username")))
        password_input = driver.find_element(By.NAME, "password")
        username_input.send_keys("zaqimegantara")
        password_input.send_keys("rizkyzaqI3@")
        driver.find_element(By.TAG_NAME, "button").click()
        print(f"[{browser}] Login submitted.")

        # STEP 5: Wait for dashboard
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-topbar-header-breadcrumb-module")))

        # STEP 6: Save success screenshot
        driver.save_screenshot(f"login-{browser}.png")
        assert "dashboard" in driver.page_source.lower()
        print(f"[{browser}] Test passed. Screenshot saved: login-{browser}.png")

    except TimeoutException:
        print(f"[{browser}] TimeoutException occurred. Saving error screenshot...")
        driver.save_screenshot(f"error-{browser}.png")
        raise

    except Exception as e:
        print(f"[{browser}] Unexpected error: {e}")
        driver.save_screenshot(f"error-{browser}.png")
        raise

    finally:
        driver.quit()
