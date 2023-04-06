from pdb import set_trace
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector
import utils as utils
import time

# Prepare mysql connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="whspr",
    database="escambia2"
)
mycursor = mydb.cursor()
mycursor.execute("""
CREATE TABLE IF NOT EXISTS summary
(id BIGINT PRIMARY KEY AUTO_INCREMENT,
court_type VARCHAR(255),
case_type VARCHAR(255),
case_number VARCHAR(255),
uniform_case_number VARCHAR(255),
status VARCHAR(255),
clerk_file_date VARCHAR(255),
status_date VARCHAR(255),
total_fees_due VARCHAR(255),
agency VARCHAR(255))
""")
mycursor.execute("""
CREATE TABLE IF NOT EXISTS charge
(id BIGINT PRIMARY KEY AUTO_INCREMENT,
count VARCHAR(255),
description TEXT,
level VARCHAR(255),
degree VARCHAR(255),
plea VARCHAR(255),
disposition VARCHAR(255),
summary_id BIGINT,
FOREIGN KEY (summary_id) REFERENCES summary(id))
""")
mycursor.execute("""
CREATE TABLE IF NOT EXISTS event
(id BIGINT PRIMARY KEY AUTO_INCREMENT,        
date VARCHAR(255),
event VARCHAR(255),
judge VARCHAR(255),
location VARCHAR(255),
result VARCHAR(255),
summary_id BIGINT,
FOREIGN KEY (summary_id) REFERENCES summary(id))
""")
mycursor.execute("""
CREATE TABLE IF NOT EXISTS outstanding_amount
(id BIGINT PRIMARY KEY AUTO_INCREMENT,
count VARCHAR(255),
code VARCHAR(255),
description TEXT,
paid VARCHAR(255),
waived VARCHAR(255),
balance VARCHAR(255),
payment_plan VARCHAR(255),
due_date VARCHAR(255),
summary_id BIGINT,
FOREIGN KEY (summary_id) REFERENCES summary(id))
""")
mycursor.execute("""
CREATE TABLE IF NOT EXISTS receipt
(id BIGINT PRIMARY KEY AUTO_INCREMENT,
date VARCHAR(255),
recipt_num VARCHAR(255),
applied_amount VARCHAR(255),
summary_id BIGINT,
FOREIGN KEY (summary_id) REFERENCES summary(id))
""")
mycursor.execute("""
CREATE TABLE IF NOT EXISTS case_docket
(id BIGINT PRIMARY KEY AUTO_INCREMENT,
date VARCHAR(255),
entry TEXT,
summary_id BIGINT,
FOREIGN KEY (summary_id) REFERENCES summary(id))
""")

# Prepare selenium driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Define component variables
url = 'https://public.escambiaclerk.com/BMWebLatest/Home.aspx/Search'
capcha_xpath = '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/div/div[2]/form/img'

# Image size and location
left = 821
top = 644
right = left + 300
bottom = top + 120

# Image color filtering
thres = 20
r_range = (132 - thres, 132 + thres)
g_range = (125 - thres, 125 + thres)
b_range = (118 - thres, 118 + thres)

# Click login button
driver.get(url)
driver.implicitly_wait(3)

from pdb import set_trace as bp
bp()

# screenshot = driver.get_screenshot_as_png()
# img = driver.find_element('xpath', capcha_xpath)
# image = Image.open(BytesIO(screenshot))
# image = image.crop((left, top, right, bottom))
# image.save('test.png')
# image = cv2.imread('test.png')
# # text = pytesseract.image_to_string(image)
# mask = ((image[..., 0] < r_range[0]) | (image[..., 0] > r_range[1]) |
#         (image[..., 1] < g_range[0]) | (image[..., 1] > g_range[1]) |
#         (image[..., 2] < b_range[0]) | (image[..., 2] > b_range[1]))
# image[mask] = (0, 0, 0)
# Image.fromarray(image).save('test.png')

for page_idx in range(100):
    table = driver.find_element('xpath', '//*[@id="gridSearchResults"]/tbody')
    row_num = len(table.find_elements('xpath', './tr'))
    for row_idx in range(row_num):
        print(f">>>>> PAGE {page_idx + 1} ROW {row_idx + 1} <<<<<")
        try:
            table = driver.find_element('xpath', '//*[@id="gridSearchResults"]/tbody')
            row = table.find_elements('xpath', './tr')[row_idx]
        except:
            print('[ERROR] Table not found')
            bp()
        # If defendant, not plaintiff
        if row.find_elements('xpath', './td')[2].text == 'DEFENDANT ':

            # Open the detailed page
            row.find_elements('xpath', './td')[3].find_element('xpath', './a').click()
            driver.implicitly_wait(5)

            # Find necessary elements
            try:
                summary_text = driver.find_element('xpath', '//*[@id="summaryAccordionCollapse"]').text
                charges_rows = driver.find_element('xpath', '//*[@id="gridCharges"]/tbody').find_elements('xpath', './tr')
                events_rows = driver.find_element('xpath', '//*[@id="gridCaseEvents"]/tbody').find_elements('xpath', './tr')
                outstanding_amount_rows = driver.find_element('xpath', '//*[@id="feesAccordionCollapse"]/div/table/tbody').find_elements('xpath', './tr')
                receipts_rows = driver.find_element('xpath', '//*[@id="Table2"]').find_element('xpath', './tbody').find_elements('xpath', './tr')
                case_dockets_rows = driver.find_element('xpath', '//*[@id="gridDockets"]/tbody').find_elements('xpath', './tr')
            except:
                # If stuck here, find the corresponding row element, open the page manually, then press 'c'
                bp()
                summary_text = driver.find_element('xpath', '//*[@id="summaryAccordionCollapse"]').text
                charges_rows = driver.find_element('xpath', '//*[@id="gridCharges"]/tbody').find_elements('xpath', './tr')
                events_rows = driver.find_element('xpath', '//*[@id="gridCaseEvents"]/tbody').find_elements('xpath', './tr')
                outstanding_amount_rows = driver.find_element('xpath', '//*[@id="feesAccordionCollapse"]/div/table/tbody').find_elements('xpath', './tr')
                receipts_rows = driver.find_element('xpath', '//*[@id="Table2"]').find_element('xpath', './tbody').find_elements('xpath', './tr')
                case_dockets_rows = driver.find_element('xpath', '//*[@id="gridDockets"]/tbody').find_elements('xpath', './tr')

            # Get summary id to be used as FK
            try:
                summary_text += '\n' # To prevent index out of range error
                summary = utils.parse_text('summary', summary_text)
                summary_query = utils.create_query(summary, 'summary')
                print(summary_query)
                mycursor.execute(summary_query)
                mydb.commit()
                mycursor.execute("SELECT LAST_INSERT_ID()")
                result = mycursor.fetchone()
                summary_id = result[0]
            except:
                print('[ERROR] Summary error')
                bp()

            # Create query for charges
            try:
                for charges in charges_rows:
                    charge = utils.parse_text('charges', charges)
                    charge['summary_id'] = summary_id
                    charge_query = utils.create_query(charge, 'charge')
                    print(charge_query)
                    mycursor.execute(charge_query)
                    mydb.commit()
            except:
                print('[ERROR] Charges error')
                bp()
            
            # Create query for  events
            try:
                for events in events_rows:
                    event = utils.parse_text('events', events)
                    if event == None:
                        break
                    event['summary_id'] = summary_id
                    event_query = utils.create_query(event, 'event')
                    print(event_query)
                    mycursor.execute(event_query)
                    mydb.commit()
            except:
                print('[ERROR] Events error')
                bp()
            
            # Create query for  outstanding amounts
            try:
                for outstanding_amounts in outstanding_amount_rows:
                    outstanding_amount = utils.parse_text('outstanding_amounts', outstanding_amounts)
                    if outstanding_amount == None:
                        break
                    outstanding_amount['summary_id'] = summary_id
                    outstanding_amount_query = utils.create_query(outstanding_amount, 'outstanding_amount')
                    print(outstanding_amount_query)
                    mycursor.execute(outstanding_amount_query)
                    mydb.commit()
            except:
                print('[ERROR] Outstanding amounts error')
                bp()

            # Create query for  receipts
            try:
                for receipts in receipts_rows:
                    receipt = utils.parse_text('receipts', receipts)
                    if receipt == None:
                        break
                    receipt['summary_id'] = summary_id
                    receipt_query = utils.create_query(receipt, 'receipt')
                    print(receipt_query)
                    mycursor.execute(receipt_query)
                    mydb.commit()
            except:
                print('[ERROR] Receipts error')
                bp()

            # Get Create query for  dockets
            try:
                for case_dockets in case_dockets_rows:
                    case_docket = utils.parse_text('case_dockets', case_dockets)
                    if case_docket == None:
                        break
                    case_docket['summary_id'] = summary_id
                    case_docket_query = utils.create_query(case_docket, 'case_docket')
                    print(case_docket_query)
                    mycursor.execute(case_docket_query)
                    mydb.commit()
            except:
                print('[ERROR] Case dockets error')
                bp()

            driver.back()
            driver.implicitly_wait(3)
    
    # Go to the next page
    try:
        driver.find_element('xpath', '//*[@id="gridpager"]/table/tbody/tr/td[6]/a').click()
        driver.implicitly_wait(3)
    except:
        bp()
