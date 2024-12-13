import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver

from selenium.common.exceptions import NoSuchElementException
import re


def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def count_datasets(driver, host):
    driver.get(f"{host}/dataset/list")
    wait_for_page_to_load(driver)

    try:
        amount_datasets = len(driver.find_elements(By.XPATH, "//table//tbody//tr"))
    except Exception:
        amount_datasets = 0
    return amount_datasets


def test_upload_dataset():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the login page
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        # Find the username and password field and enter the values
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        # Send the form
        password_field.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # Count initial datasets
        initial_datasets = count_datasets(driver, host)

        # Open the upload dataset
        driver.get(f"{host}/dataset/upload")
        wait_for_page_to_load(driver)

        # Find basic info and UVL model and fill values
        title_field = driver.find_element(By.NAME, "title")
        title_field.send_keys("Title")
        desc_field = driver.find_element(By.NAME, "desc")
        desc_field.send_keys("Description")
        tags_field = driver.find_element(By.NAME, "tags")
        tags_field.send_keys("tag1,tag2")

        # Add two authors and fill
        add_author_button = driver.find_element(By.ID, "add_author")
        add_author_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)
        add_author_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        name_field0 = driver.find_element(By.NAME, "authors-0-name")
        name_field0.send_keys("Author0")
        affiliation_field0 = driver.find_element(By.NAME, "authors-0-affiliation")
        affiliation_field0.send_keys("Club0")
        orcid_field0 = driver.find_element(By.NAME, "authors-0-orcid")
        orcid_field0.send_keys("0000-0000-0000-0000")

        name_field1 = driver.find_element(By.NAME, "authors-1-name")
        name_field1.send_keys("Author1")
        affiliation_field1 = driver.find_element(By.NAME, "authors-1-affiliation")
        affiliation_field1.send_keys("Club1")

        # Obtén las rutas absolutas de los archivos
        file1_path = os.path.abspath("app/modules/dataset/uvl_examples/file1.uvl")
        file2_path = os.path.abspath("app/modules/dataset/uvl_examples/file2.uvl")

        # Subir el primer archivo
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file1_path)
        wait_for_page_to_load(driver)

        # Subir el segundo archivo
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file2_path)
        wait_for_page_to_load(driver)

        # Add authors in UVL models
        show_button = driver.find_element(By.ID, "0_button")
        show_button.send_keys(Keys.RETURN)
        add_author_uvl_button = driver.find_element(By.ID, "0_form_authors_button")
        add_author_uvl_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        name_field = driver.find_element(By.NAME, "feature_models-0-authors-2-name")
        name_field.send_keys("Author3")
        affiliation_field = driver.find_element(By.NAME, "feature_models-0-authors-2-affiliation")
        affiliation_field.send_keys("Club3")

        # Check I agree and send form
        check = driver.find_element(By.ID, "agreeCheckbox")
        check.send_keys(Keys.SPACE)
        wait_for_page_to_load(driver)

        upload_btn = driver.find_element(By.ID, "upload_button")
        upload_btn.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)
        time.sleep(2)  # Force wait time

        assert driver.current_url == f"{host}/dataset/list", "Test failed!"

        # Count final datasets
        final_datasets = count_datasets(driver, host)
        assert final_datasets == initial_datasets + 1, "Test failed!"

        print("Test passed!")

    finally:

        # Close the browser
        close_driver(driver)


# Tests de Selenium de la feature Download All
def test_download_all_uvl():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f'{host}/')
        driver.set_window_size(1920, 1080)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        driver.find_element(By.CSS_SELECTOR, ".btn-primary:nth-child(1)").click()
        time.sleep(1)
        driver.find_element(By.LINK_TEXT, "Download all in UVL").click()
        time.sleep(3)
        print("Test download all uvl passed!")

    except NoSuchElementException as e:
        raise AssertionError(f"Test download all uvl failed: {e}")

    finally:
        close_driver(driver)


def test_download_all_glencoe():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f'{host}/')
        driver.set_window_size(1920, 1080)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        driver.find_element(By.CSS_SELECTOR, ".btn-primary:nth-child(1)").click()
        time.sleep(1)
        driver.find_element(By.LINK_TEXT, "Download all in GLENCOE").click()
        time.sleep(3)
        print("Test download all glencoe passed!")

    except NoSuchElementException as e:
        raise AssertionError(f"Test download all glencoe failed: {e}")

    finally:
        close_driver(driver)


def test_download_all_dimacs():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f'{host}/')
        driver.set_window_size(1920, 1080)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        driver.find_element(By.CSS_SELECTOR, ".btn-primary:nth-child(1)").click()
        time.sleep(1)
        driver.find_element(By.LINK_TEXT, "Download all in DIMACS").click()
        time.sleep(3)
        print("Test download all DIMACS passed!")

    except NoSuchElementException as e:
        raise AssertionError(f"Test download all DIMACSfailed: {e}")

    finally:
        close_driver(driver)


def test_download_all_splot():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f'{host}/')
        driver.set_window_size(1920, 1080)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        driver.find_element(By.CSS_SELECTOR, ".btn-primary:nth-child(1)").click()
        time.sleep(1)
        driver.find_element(By.LINK_TEXT, "Download all in SPLOT").click()
        time.sleep(3)
        print("Test download all splot passed!")

    except NoSuchElementException as e:
        raise AssertionError(f"Test download all uvl failed: {e}")

    finally:
        close_driver(driver)


def test_download_uvl():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f'{host}/')
        driver.set_window_size(912, 1028)
        driver.find_element(By.ID, "downloadAsDropdown").click()
        time.sleep(1)
        driver.find_element(By.LINK_TEXT, "UVL").click()
        time.sleep(3)
        print("Test download uvl passed!")

    except NoSuchElementException as e:
        raise AssertionError(f"Test download uvl failed: {e}")

    finally:
        close_driver(driver)


def test_download_glecone():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f'{host}/')
        driver.set_window_size(912, 1028)
        driver.find_element(By.ID, "downloadAsDropdown").click()
        time.sleep(1)
        driver.find_element(By.LINK_TEXT, "Glecone").click()
        time.sleep(3)
        print("Test download glecone passed!")

    except NoSuchElementException as e:
        raise AssertionError(f"Test download glecone failed: {e}")

    finally:
        close_driver(driver)


def test_download_dimacs():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f'{host}/')
        driver.set_window_size(912, 1028)
        driver.find_element(By.ID, "downloadAsDropdown").click()
        time.sleep(1)
        driver.find_element(By.LINK_TEXT, "DIMACS").click()
        time.sleep(3)
        print("Test download dimacs passed!")

    except NoSuchElementException as e:
        raise AssertionError(f"Test download dimacs failed: {e}")

    finally:
        close_driver(driver)


def test_download_splot():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f'{host}/')
        driver.set_window_size(912, 1028)
        driver.find_element(By.ID, "downloadAsDropdown").click()
        time.sleep(1)
        driver.find_element(By.LINK_TEXT, "SPLOT").click()
        time.sleep(3)
        print("Test download splot passed!")

    except NoSuchElementException as e:
        raise AssertionError(f"Test download splot failed: {e}")

    finally:
        close_driver(driver)


def test_upload_dataset_draft():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the login page
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        # Find the username and password field and enter the values
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        # Send the form
        password_field.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # Count initial datasets
        initial_datasets = count_datasets(driver, host)

        # Open the upload dataset
        driver.get(f"{host}/dataset/upload")
        wait_for_page_to_load(driver)

        # Find basic info and UVL model and fill values
        title_field = driver.find_element(By.NAME, "title")
        title_field.send_keys("Title")
        desc_field = driver.find_element(By.NAME, "desc")
        desc_field.send_keys("Description")
        tags_field = driver.find_element(By.NAME, "tags")
        tags_field.send_keys("tag1,tag2")

        # Add two authors and fill
        add_author_button = driver.find_element(By.ID, "add_author")
        add_author_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)
        add_author_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        name_field0 = driver.find_element(By.NAME, "authors-0-name")
        name_field0.send_keys("Author0")
        affiliation_field0 = driver.find_element(By.NAME, "authors-0-affiliation")
        affiliation_field0.send_keys("Club0")
        orcid_field0 = driver.find_element(By.NAME, "authors-0-orcid")
        orcid_field0.send_keys("0000-0000-0000-0000")

        name_field1 = driver.find_element(By.NAME, "authors-1-name")
        name_field1.send_keys("Author1")
        affiliation_field1 = driver.find_element(By.NAME, "authors-1-affiliation")
        affiliation_field1.send_keys("Club1")
        # Obtén las rutas absolutas de los archivos
        file1_path = os.path.abspath("app/modules/dataset/uvl_examples/file1.uvl")
        file2_path = os.path.abspath("app/modules/dataset/uvl_examples/file2.uvl")

        # Subir el primer archivo
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file1_path)
        wait_for_page_to_load(driver)

        # Subir el segundo archivo
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file2_path)
        wait_for_page_to_load(driver)

        # Add authors in UVL models
        show_button = driver.find_element(By.ID, "0_button")
        show_button.send_keys(Keys.RETURN)
        add_author_uvl_button = driver.find_element(By.ID, "0_form_authors_button")
        add_author_uvl_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        name_field = driver.find_element(By.NAME, "feature_models-0-authors-2-name")
        name_field.send_keys("Author3")
        affiliation_field = driver.find_element(By.NAME, "feature_models-0-authors-2-affiliation")
        affiliation_field.send_keys("Club3")
        time.sleep(2)  # Force wait time
        upload_btn = driver.find_element(By.ID, "upload_button_draft")
        upload_btn.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)
        time.sleep(2)  # Force wait time
        # Find the last table
        tables = driver.find_elements(By.CLASS_NAME, "card-body")
        last_table = tables[-1]

        # Find the first URL in the last table
        first_url = last_table.find_element(By.TAG_NAME, "a").get_attribute("href")
        res_id = first_url.split("/")[-2]
        
        time.sleep(2)  # Force wait time

        assert driver.current_url == f"{host}/dataset/list", "Test failed!"

        # Count final datasets
        final_datasets = count_datasets(driver, host)
        assert final_datasets == initial_datasets + 1, "Test failed!"

        print("Test upload dataset draft passed!")

    finally:

        # Close the browser
        close_driver(driver)

    return res_id


url_id = test_upload_dataset_draft()


def test_edit_dataset_draft():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the login page
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        # Find the username and password field and enter the values
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        # Send the form
        password_field.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # Count initial datasets
        initial_datasets = count_datasets(driver, host)

        # Open the upload dataset
        driver.get(f"{host}/dataset/edit/{url_id}")
        wait_for_page_to_load(driver)

        # Find basic info and UVL model and fill values
        title_field = driver.find_element(By.NAME, "title")
        title_field.clear()
        title_field.send_keys("Title edited")
        desc_field = driver.find_element(By.NAME, "desc")
        desc_field.clear()
        desc_field.send_keys("Description edited")
        public_doi = driver.find_element(By.NAME, "publication_type")
        public_doi.send_keys(Keys.RETURN)
        public_doi.send_keys(Keys.DOWN)
        public_doi.send_keys(Keys.RETURN)
        tags_field = driver.find_element(By.NAME, "tags")
        tags_field.clear()
        tags_field.send_keys("tag1,tag2,tag3")

        edit_btn = driver.find_element(By.CLASS_NAME, "btn-primary")
        edit_btn.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        time.sleep(2)  # Force wait time

        assert driver.current_url == f"{host}/dataset/list", "Test failed!"

        # Count final datasets
        final_datasets = count_datasets(driver, host)
        assert final_datasets == initial_datasets, "Test failed!"

        print("Test edit dataset draft passed!")

    finally:

        # Close the browser
        close_driver(driver)


def test_publish_dataset():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the login page
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        # Find the username and password field and enter the values
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        # Send the form
        password_field.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # Count initial datasets
        initial_datasets = count_datasets(driver, host)
        # Open the upload dataset
        # Get the last dataset index
        driver.get(f"{host}/dataset/publish/{url_id}")
        wait_for_page_to_load(driver)
        time.sleep(2)

        # Count final datasets
        final_datasets = count_datasets(driver, host)
        assert final_datasets == initial_datasets, "Test failed!"

        print("Test publish dataset draft passed!")

    finally:

        # Close the browser
        close_driver(driver)


# Call the test function
test_download_all_uvl()
test_download_all_dimacs()
test_download_all_glencoe()
test_download_all_splot()
test_download_uvl()
test_download_glecone()
test_download_dimacs()
test_download_splot()
test_edit_dataset_draft()
test_publish_dataset()
