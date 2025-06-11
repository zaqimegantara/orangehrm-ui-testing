import pytest
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load from project root regardless of where the test file lives
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

BASE_URL = os.getenv("BASE_URL")

@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=ngrok-skip-browser-warning")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    # Apply ngrok-skip-browser-warning after init
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": "ngrok-skip-browser-warning"
    })

    yield driver
    driver.quit()

def test_login_with_valid_credentials(driver):
    driver.get(BASE_URL + "/web/index.php/auth/login")

    wait = WebDriverWait(driver, 15)
    username_input = wait.until(EC.visibility_of_element_located((By.NAME, "username")))
    password_input = driver.find_element(By.NAME, "password")

    username_input.send_keys("zaqimegantara")
    password_input.send_keys("rizkyzaqI3@")
    driver.find_element(By.TAG_NAME, "button").click()

    # Wait for dashboard breadcrumb header
    wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, "oxd-topbar-header-breadcrumb-module")
    ))

    dashboard_text = driver.find_element(By.CLASS_NAME, "oxd-topbar-header-breadcrumb-module").text
    driver.save_screenshot("login-success.png")
    assert "dashboard" in dashboard_text.lower()


def test_login_with_invalid_credentials(driver):
    driver.get(BASE_URL + "/web/index.php/auth/login")  # Load login page directly

    wait = WebDriverWait(driver, 15)
    username_input = wait.until(EC.visibility_of_element_located((By.NAME, "username")))
    password_input = driver.find_element(By.NAME, "password")

    username_input.send_keys("wronguser")
    password_input.send_keys("wrongpass")
    driver.find_element(By.TAG_NAME, "button").click()

    # Wait for error message to appear
    error = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "oxd-alert-content-text")))

    driver.save_screenshot("login-invalid.png")
    assert "invalid credentials" in error.text.lower()
