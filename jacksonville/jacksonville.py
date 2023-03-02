from datetime import date, timedelta
from pdb import set_trace
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import calendar

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

data = []

# Prepare selenium driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Define component variables
url = 'https://inmatesearch.jaxsheriff.org/login'
xpath_button = '//*[@id="mat-checkbox-1"]/label/span[1]'
xpath_in_sheet = '/html/body/wic-root/wic-layout/div[2]/div[2]/div/section/div/div[1]/div/ul/li[3]/a'
xpath_calender_icon = '/html/body/wic-root/wic-layout/div[2]/div[2]/div/section/div/div[2]/wic-report/div/mat-form-field/div/div[1]/div[2]/mat-datepicker-toggle/button'


driver.get(url)
driver.implicitly_wait(4)
driver.find_element('xpath', xpath_button).click()
driver.implicitly_wait(4)
driver.find_element('xpath', xpath_in_sheet).click()
driver.implicitly_wait(4)

# Date navigation
year = date.today().year
month = date.today().month
first_day = 1
last_day = date.today().day
month_has_changed = False
while date(year, month, first_day) >= date(2001, 1, 1):
    start_date = date(year, month, first_day)
    end_date = date(year, month, last_day)
    for single_date in daterange(start_date, end_date):
        try:
            driver.find_element('xpath', xpath_calender_icon).click()
            driver.implicitly_wait(4)
        except:
            time.sleep(5)
            driver.find_element('xpath', xpath_calender_icon).click()
            driver.implicitly_wait(4)

        date_string = single_date.strftime("%B X%d, %Y").replace('X0', 'X').replace('X', '')
        print(f'>>> {date_string} <<<')
        if month_has_changed:
            try:
                driver.find_element("xpath", '//*[@id="mat-datepicker-0"]/mat-calendar-header/div/div/button[2]').click()
            except:
                time.sleep(5)
                driver.find_element("xpath", '//*[@id="mat-datepicker-0"]/mat-calendar-header/div/div/button[2]').click()
            month_has_changed = False
        
        try:
            driver.find_element("xpath", f"//button[@aria-label='{date_string}']").click()
        except:
            time.sleep(5)
            driver.find_element("xpath", f"//button[@aria-label='{date_string}']").click()
        time.sleep(3)

        rows = len(driver.find_elements('xpath', "//*[@id='pr_id_1-table']/tbody/tr"))
        cols = len(driver.find_elements('xpath', '//*[@id="pr_id_1-table"]/tbody/tr[1]/td'))
        for row in range(1, rows):
            row_data = []
            for col in range(1, cols):
                try:
                    row_data.append(driver.find_element('xpath', f'//*[@id="pr_id_1-table"]/tbody/tr[{row}]/td[{col}]').text)
                except:
                    time.sleep(5)
                    row_data.append(driver.find_element('xpath', f'//*[@id="pr_id_1-table"]/tbody/tr[{row}]/td[{col}]').text)
            row_data.append(single_date.strftime('%b-%d-%Y'))
            print(row_data)
            with open(f"./data/data.csv", 'a') as f:
                f.write(','.join(row_data)+'\n')
            data.append(row_data)
    month -= 1
    month_has_changed = True
    if month == 0:
        year -= 1
        month = 12
    last_day = calendar.monthrange(year, month)[1]
            