from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from oauth2client.service_account import ServiceAccountCredentials
from config import *
from time import sleep
import gspread


# noinspection PyGlobalUndefined
def auto_login():
    global windows_before
    driver = webdriver.Chrome("webdriver/chromedriver")
    for index, user in enumerate(user_list.values()):

        if index == 0:
            non_insert = True
            # Open Website
            driver.get(url_website)

            # Get Current Window
            windows_before = driver.current_window_handle

            while non_insert:
                non_insert = insert_user_password(driver, non_insert, user)

                if not non_insert:
                    wait = login(driver)
                    verify(driver, wait)
                    confirm(driver, wait)

            # Insert Result to Google Sheet
            return_result(index, user)

        elif index > 0:
            non_insert = True
            # Open Website
            driver.execute_script(open_script)

            # Get Numbers of Window is Opening and Switch to new window
            windows_after = driver.window_handles
            new_window = [x for x in windows_after if x != windows_before][-1]
            driver.switch_to.window(new_window)

            while non_insert:
                non_insert = insert_user_password(driver, non_insert, user)

                if not non_insert:
                    wait = login(driver)
                    verify(driver, wait)
                    confirm(driver, wait)

            # Insert Result to Google Sheet
            return_result(index, user)

            # Get Current Window
            windows_before = driver.current_window_handle

    sleep(120)


def confirm(driver, wait):
    XPATH = (By.XPATH, '/html/body/div[4]/div/div/div[3]/button[2]')
    wait.until(ec.presence_of_element_located(XPATH))
    driver.find_element_by_xpath('/html/body/div[4]/div/div/div[3]/button[2]').click()


def login(driver, timeout=120):
    wait = WebDriverWait(driver, timeout)
    wait.until(ec.element_to_be_clickable((By.XPATH, '//*[@id="page"]/div/div/form/button')))
    return wait


def verify(driver, wait):
    XPATH = (By.XPATH, '//*[@id="displaymobile"]/div[9]/div[2]/input')
    wait.until(ec.presence_of_element_located(XPATH))
    driver.find_element_by_xpath('//*[@id="displaymobile"]/div[9]/div[2]/input').click()


def return_result(index, user):
    worker = list(user_list.keys())
    data = [worker[index], user["username"], user["password"]]
    google_sheet_api(data)


def insert_user_password(driver, insert, user):
    # noinspection PyBroadException
    try:
        wait = WebDriverWait(driver, 0.5)
        username_textbox = wait.until(ec.presence_of_element_located((By.NAME, "idCard")))
        # username_textbox = driver.find_element_by_id("email")
        username_textbox.send_keys(user["username"])
        password_textbox = driver.find_element_by_name("password")
        password_textbox.send_keys(user["password"])
        insert = False
    except Exception:
        driver.refresh()
    return insert


def google_sheet_api(row):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(credentials)
    sheet = client.open_by_url(url_google_sheet)

    # Get worksheet
    worksheet = sheet.get_worksheet(0)

    # Insert Data
    worksheet.append_row(row)


auto_login()
