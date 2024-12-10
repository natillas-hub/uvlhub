from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def test_change_password():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f'{host}/')
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.LINK_TEXT, "Forgot your password?").click()
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        driver.find_element(By.ID, "answer1").send_keys("Fluffy")
        driver.find_element(By.ID, "answer2").send_keys("Mr. Smith")
        driver.find_element(By.ID, "answer3").send_keys("Soccer")
        driver.find_element(By.ID, "new_password").send_keys("12345")
        driver.find_element(By.CSS_SELECTOR, ".btn").click()

        # Confirm password change
        driver.get(f'{host}/')
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        driver.find_element(By.ID, "password").send_keys("12345")
        driver.find_element(By.ID, "submit").click()
        print("Test change password passed!")

    except NoSuchElementException as e:
        raise AssertionError(f"Test change password failed: {e}")

    finally:
        close_driver(driver)


def test_change_security_answers():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f'{host}/')
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        driver.find_element(By.ID, "password").send_keys("12345")
        driver.find_element(By.ID, "submit").click()
        driver.get(f'{host}/profile/edit')
        driver.find_element(By.LINK_TEXT, "Configure security answers").click()
        driver.find_element(By.ID, "answer1").send_keys("Sevilla")
        driver.find_element(By.ID, "answer2").send_keys("Sr. Holmes")
        driver.find_element(By.ID, "answer3").send_keys("Futbol")
        driver.find_element(By.CSS_SELECTOR, ".btn").click()

        # Verify changes
        driver.get(f'{host}/logout')
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.LINK_TEXT, "Forgot your password?").click()
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        driver.find_element(By.ID, "answer1").send_keys("Sevilla")
        driver.find_element(By.ID, "answer2").send_keys("Sr. Holmes")
        driver.find_element(By.ID, "answer3").send_keys("Futbol")
        driver.find_element(By.ID, "new_password").send_keys("1234")
        driver.find_element(By.CSS_SELECTOR, ".btn").click()
        print("Test change security answers passed!")

    except NoSuchElementException as e:
        raise AssertionError(f"Test change security answers failed: {e}")

    finally:
        close_driver(driver)


def test_restart_data():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f'{host}/')
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        driver.find_element(By.ID, "password").send_keys("1234")
        driver.find_element(By.ID, "submit").click()
        driver.get(f'{host}/profile/edit')
        driver.find_element(By.LINK_TEXT, "Configure security answers").click()
        driver.find_element(By.ID, "answer1").send_keys("Fluffy")
        driver.find_element(By.ID, "answer2").send_keys("Mr. Smith")
        driver.find_element(By.ID, "answer3").send_keys("Soccer")
        driver.find_element(By.CSS_SELECTOR, ".btn").click()
        print("Test restart data passed!")

    except NoSuchElementException as e:
        raise AssertionError(f"Test restart data failed: {e}")

    finally:
        close_driver(driver)


# Call all test functions
test_change_password()
test_change_security_answers()
test_restart_data()
