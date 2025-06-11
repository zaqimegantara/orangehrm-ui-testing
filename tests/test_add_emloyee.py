import pytest
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random

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

def login(driver):
    driver.get(BASE_URL + "/web/index.php/auth/login")
    wait = WebDriverWait(driver, 15)
    username_input = wait.until(EC.visibility_of_element_located((By.NAME, "username")))
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys("zaqimegantara")
    password_input.send_keys("rizkyzaqI3@")
    driver.find_element(By.TAG_NAME, "button").click()

def go_to_add_employee(driver):
    wait = WebDriverWait(driver, 15)
    pim_menu = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "PIM")))
    pim_menu.click()
    add_employee_btn = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Add Employee")))
    add_employee_btn.click()

def test_add_employee_valid(driver):
    login(driver)
    go_to_add_employee(driver)

    wait = WebDriverWait(driver, 15)

    first_name = wait.until(EC.visibility_of_element_located((By.NAME, "firstName")))
    middle_name = driver.find_element(By.NAME, "middleName")
    last_name = driver.find_element(By.NAME, "lastName")

    first_name.send_keys("James")
    middle_name.send_keys("Anderson")
    last_name.send_keys("Harden")

    save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    save_btn.click()
    print("Save button clicked. Waiting for page to redirect...")

    try:
        WebDriverWait(driver, 10).until_not(
            EC.text_to_be_present_in_element((By.CLASS_NAME, "orangehrm-main-title"), "Add Employee")
        )

        header = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "orangehrm-main-title")))
        print("Header after Save:", header.text)
        driver.save_screenshot("add-employee-valid.png")
        assert "personal details" in header.text.lower()
    except Exception as e:
        driver.save_screenshot("add-employee-failed.png")
        print("Save failed or page did not redirect. Screenshot saved.")
        raise e



def test_add_employee_invalid(driver):
    login(driver)
    go_to_add_employee(driver)

    wait = WebDriverWait(driver, 15)
    # Leave fields empty and try to submit
    save_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    save_button.click()

    # Expect validation errors
    error_messages = wait.until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "oxd-input-field-error-message")
    ))

    driver.save_screenshot("add-employee-invalid.png")
    assert any("required" in error.text.lower() for error in error_messages)

