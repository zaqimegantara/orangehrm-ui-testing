# 🧪 OrangeHRM Testing Automation

## 📋 Overview

This project presents a case study of functional, non-functional, automated, and acceptance testing for the **OrangeHRM** web application. The goal is to ensure system reliability and quality through comprehensive test coverage, including CI/CD integration using GitHub Actions.

---

## 🚀 Key Features

* ✅ **Functional Testing**: Login, Add Employee, Logout
* 🌐 **Non-Functional Testing**: Cross-browser compatibility (Chrome, Firefox, Edge)
* 🤖 **Automated Testing**: Selenium WebDriver with Python & Pytest
* 🔄 **CI/CD Integration**: GitHub Actions with headless browser testing
* 🧪 **Acceptance Testing**: User-based validation aligned with user expectations
* 📸 **Screenshot Logging**: Visual logs for all test cases
* 📊 **Testing Metrics**: 100% pass rate, full coverage

---

## 🧰 Tech Stack

* **Framework**: Selenium WebDriver, Pytest
* **CI/CD**: GitHub Actions
* **Automation**: Headless testing with Chrome, Firefox, and Edge
* **Environment**: Docker Compose, ngrok

---

## ⚙️ Setup Instructions

1. Clone the repository
2. Start OrangeHRM using Docker Compose:

```bash
docker-compose up -d
```

3. Expose local app with `ngrok`:

```bash
ngrok http 8080
```

4. Store the ngrok URL, test username, and password in a `.env` file:

```env
BASE_URL=https://your-ngrok-url
TEST_USERNAME=your_username
TEST_PASSWORD=your_password
```

5. Run tests locally:

```bash
pytest
```

6. All test cases run automatically on push via GitHub Actions.

---

## 🧪 Test Scenarios

| No. | Test Scenario                   | Type           | Expected Result                        |
| --- | ------------------------------- | -------------- | -------------------------------------- |
| 1   | Login with valid credentials    | Functional     | Redirect to dashboard                  |
| 2   | Login with invalid credentials  | Functional     | Show error message                     |
| 3   | Add employee with complete data | Functional     | Success message, data added            |
| 4   | Add employee with empty fields  | Functional     | Show validation error, no data saved   |
| 5   | Logout                          | Functional     | Redirect to login page                 |
| 6   | Login on Chrome, Firefox, Edge  | Non-Functional | Consistent results across all browsers |

---

## 📊 Test Metrics

| Category               | Metric                      | Result     |
| ---------------------- | --------------------------- | ---------- |
| Functional Testing     | Test Case Execution Rate    | 100% (6/6) |
|                        | Test Case Pass Rate         | 100% (6/6) |
|                        | Test Case Failure Rate      | 0%         |
| Non-Functional Testing | Browser Compatibility       | 100% (3/3) |
| Automation             | CI/CD Pipeline Success Rate | 100%       |
|                        | Automation Coverage         | 100%       |
|                        | Screenshot Logging Rate     | 100%       |

---

## 📅 Acceptance Test Summary

* ✅ All 6 test cases passed
* 📆 Conducted between 1–3 July 2025
* 👥 Verified by representatives from both user and developer teams
* 📝 No defects or issues were found

---

## 📚 References

1. Najihi et al., “Software Testing from an Agile and Traditional view,” 2022.
2. Ali et al., “A comprehensive study on automated testing,” 2024.
3. Olaoye & Idowu, “Balancing Quality in Agile Teams.”
4. Tramontana et al., “Automated testing of mobile applications,” 2019.
5. Shahid & Tasneem, “Impact of avoiding non-functional requirements,” 2017.
6. Umar, “Comprehensive study of software testing,” 2019.
7. Putra et al., “Software Testing Strategies: SLR,” 2023.

---

## 📎 Screenshots & Artifacts

All screenshots and HTML reports are automatically uploaded as GitHub Actions artifacts for review and documentation.

---

