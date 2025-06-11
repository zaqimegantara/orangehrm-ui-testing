import pytest
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
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
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": "ngrok-skip-browser-warning"
    })
    yield driver
    driver.quit()

def test_logout(driver):
    wait = WebDriverWait(driver, 15)

    # 1. Log in
    driver.get(BASE_URL + "/web/index.php/auth/login")
    username_input = wait.until(EC.visibility_of_element_located((By.NAME, "username")))
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys("zaqimegantara")
    password_input.send_keys("rizkyzaqI3@")
    driver.find_element(By.TAG_NAME, "button").click()

    # 2. Open user menu (top right corner)
    profile_dropdown = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "oxd-userdropdown-name")))
    profile_dropdown.click()

    # 3. Click Logout
    logout_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Logout")))
    logout_btn.click()

    # 4. Assert redirected back to login
    wait.until(EC.visibility_of_element_located((By.NAME, "username")))
    driver.save_screenshot("logout-success.png")
    assert "login" in driver.current_url.lower()
