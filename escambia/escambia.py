from pdb import set_trace
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector
import utils as utils
import time
from pdb import set_trace as bp

class escambia(object):
    def __init__(self):
        # Prepare mysql connection
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="whspr",
            database="escambia3"
        )
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("""
        CREATE TABLE IF NOT EXISTS defendant
        (id BIGINT PRIMARY KEY,
        name VARCHAR(255),
        dob VARCHAR(255),
        gender VARCHAR(255),
        race VARCHAR(255))
        """)
        self.mycursor.execute("""
        CREATE TABLE IF NOT EXISTS bond
        (id BIGINT PRIMARY KEY AUTO_INCREMENT,
        bond_number VARCHAR(255),
        issued_date VARCHAR(255),
        amount VARCHAR(255),
        defendant_id BIGINT,
        FOREIGN KEY (defendant_id) REFERENCES defendant(id))
        """)
        self.mycursor.execute("""
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
        agency VARCHAR(255),
        defendant_id BIGINT,
        FOREIGN KEY (defendant_id) REFERENCES defendant(id))
        """)
        self.mycursor.execute("""
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
        self.mycursor.execute("""
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
        self.mycursor.execute("""
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
        self.mycursor.execute("""
        CREATE TABLE IF NOT EXISTS receipt
        (id BIGINT PRIMARY KEY AUTO_INCREMENT,
        date VARCHAR(255),
        recipt_num VARCHAR(255),
        applied_amount VARCHAR(255),
        summary_id BIGINT,
        FOREIGN KEY (summary_id) REFERENCES summary(id))
        """)
        self.mycursor.execute("""
        CREATE TABLE IF NOT EXISTS case_docket
        (id BIGINT PRIMARY KEY AUTO_INCREMENT,
        date VARCHAR(255),
        entry TEXT,
        summary_id BIGINT,
        FOREIGN KEY (summary_id) REFERENCES summary(id))
        """)

        # Prepare selenium driver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        # Define component variables
        self.url = 'https://public.escambiaclerk.com/BMWebLatest/Home.aspx/Search'


    def bond_search(self):
        # Click login button
        self.driver.get(self.url)
        self.driver.implicitly_wait(3)

        # Solve capcha
        capcha_answer = None
        while True:
            try:
                capcha_answer = int(input('Solve the capcha quiz: '))
                break
            except:
                capcha_answer = int(input('Not a valid input. Solve the capcha quiz: '))
        self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/div/div[2]/form/input[1]').send_keys(capcha_answer)
        self.driver.find_element('xpath', '//*[@id="searchButton"]').click()

        for page_idx in range(100):
            table = self.driver.find_element('xpath', '//*[@id="gridSearchResults"]/tbody')
            row_num = len(table.find_elements('xpath', './tr'))
            for row_idx in range(row_num):
                print(f">>>>> PAGE {page_idx + 1} ROW {row_idx + 1} <<<<<")
                try:
                    table = self.driver.find_element('xpath', '//*[@id="gridSearchResults"]/tbody')
                    row = table.find_elements('xpath', './tr')[row_idx]
                except:
                    print('[ERROR] Table not found')
                    bp()

                # If defendant, not plaintiff
                if row.find_elements('xpath', './td')[2].text == 'DEFENDANT ':

                    # Get name. If followed by parentheses, remove it
                    name = row.find_elements('xpath', './td')[1].text
                    if "(" in name:
                        name = name[:name.rindex("(")-1]

                    # Open the detailed page
                    row.find_elements('xpath', './td')[3].find_element('xpath', './a').click()
                    self.driver.implicitly_wait(5)


                    # Open the Bonds tab
                    self.driver.find_element('xpath', '//*[@id="tabBonds"]').click()
                    self.driver.implicitly_wait(3)

                    try:
                        bond_table = self.driver.find_element('xpath', '//*[@id="bondItems"]')
                    except:
                        print("bond table not located")
                        bp()
                    
                    # If there is a bond
                    if bond_table.text != '(0) Bonds':
                        bond_items = bond_table.find_elements('xpath', './tr')
                        for bond_item in bond_items:
                            bond_item.click()
                            self.driver.implicitly_wait(3)

                            try:
                                bond_number =  self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[1]/td[2]').text
                                bond_issued_date = self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]').text
                                bond_amount = self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[5]/td[2]').text
                            except:
                                print('bond elements not found')
                                bp()
                                bond_number =  self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[1]/td[2]').text
                                bond_issued_date = self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]').text
                                bond_amount = self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[5]/td[2]').text
                            print(bond_number, bond_issued_date, bond_amount)
                        
                        # Look for the inmate name
                        self.name_search(name)
                    
                    # Go back to the list
                    self.driver.back()
                    self.driver.implicitly_wait(3)


    def name_search(self, name):
        self.driver.find_element('xpath', '//*[@id="Home.aspx/Search"]/a').click()
        self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td[1]/table/tbody/tr[2]/td/div/label[1]/input').click()
        self.driver.find_element('xpath', '//*[@id="name"]').send_keys(name)

        # Solve capcha
        capcha_answer = None
        while True:
            try:
                capcha_answer = int(input('Solve the capcha quiz: '))
                break
            except:
                capcha_answer = int(input('Not a valid input. Solve the capcha quiz: '))
        self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/div/div[2]/form/input[1]').send_keys(capcha_answer)
        self.driver.find_element('xpath', '//*[@id="searchButton"]').click()
        self.driver.implicitly_wait(3)

        try:
            # If no case is found
            # idk why this happens but if a name containes postfix or sth it shows no result
            # and it's kinda risky to assume that all the names without the postfix to be the same inmate
            if self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/table[1]/tbody/tr/td/table/tbody/tr[4]/td[2]').text == '0':
                # Go back to the case search table
                self.driver.back()
                self.driver.implicitly_wait(3)
                self.driver.back()
                self.driver.implicitly_wait(3)
                return
        except:
            pass

        # Iterate through table
        table = None
        try:
            table = self.driver.find_element('xpath', '//*[@id="gridSearchResults"]/tbody')
        except:
            pass

        print('name search')
        bp()
        # If there's more than one records:
        if table is not None:
            row_num = len(table.find_elements('xpath', './tr'))
            for row_idx in range(row_num):
                print(f">>>>> DEFENDANT {name} CASE ROW {row_idx + 1} <<<<<")
                table = self.driver.find_element('xpath', '//*[@id="gridSearchResults"]/tbody')
                row = table.find_elements('xpath', './tr')[row_idx]
                if row.find_elements('xpath', './td')[2].text == 'DEFENDANT ':
                    row.find_elements('xpath', './td')[3].find_element('xpath', './a').click()

                    defendant_id = self.defendant_scrape()
                    self.bond_scrape(defendant_id)
                    self.summary_scrape(defendant_id)

                    self.driver.back()
                    self.driver.implicitly_wait(3)
        else:
            defendant_id = self.defendant_scrape()
            self.bond_scrape(defendant_id)
            self.summary_scrape(defendant_id)


    def bond_scrape(self, defendant_id):
        self.driver.find_element('xpath', '//*[@id="tabBonds"]').click()
        self.driver.implicitly_wait(3)

        try:
            bond_table = self.driver.find_element('xpath', '//*[@id="bondItems"]')
        except:
            print("bond table not located")
            bp()
        
        # If there is no bond
        if bond_table.text == '(0) Bonds':
            self.driver.back()
            self.driver.implicitly_wait(3)
            return

        bond_number = self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[1]/td[2]').text
        issued_date = self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]').text
        amount = self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[5]/td[2]').text

        defendant_query = utils.create_query({"defendant_id": int(defendant_id),"bond_number": bond_number,"issued_date": issued_date,"amount": amount}, 'bond')
        print(defendant_query)
        self.mycursor.execute(defendant_query)
        self.mydb.commit()

        self.driver.back()
        self.driver.implicitly_wait(3)


    def defendant_scrape(self):
        row = self.driver.find_element('xpath', '//*[@id="gridParties"]/tbody').find_elements('xpath', './tr')
        defendant = [r for r in row if r.find_elements('xpath', './td')[0].text == 'DEFENDANT '][0]
        defendant.find_elements('xpath', './td')[1].click()
        self.driver.implicitly_wait(3)

        name = self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[1]/td[2]').text
        dob = self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[4]/td[2]').text
        gender = self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[6]/td[2]').text
        id = self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[8]/td[2]').text

        defendant_query = utils.create_query({"id": id, "name": name,"dob": dob,"gender": gender}, 'defendant')
        print(defendant_query)
        self.mycursor.execute(defendant_query)
        self.mydb.commit()

        self.driver.back()
        self.driver.implicitly_wait(3)
        
        # Return defendant id for FK
        return id
    
    def summary_scrape(self, defendant_id):
        self.driver.find_element('xpath', '//*[@id="tabSummary"]').click()
        self.driver.implicitly_wait(3)

        # Find necessary elements
        try:
            summary_text = self.driver.find_element('xpath', '//*[@id="summaryAccordionCollapse"]').text
            charges_rows = self.driver.find_element('xpath', '//*[@id="gridCharges"]/tbody').find_elements('xpath', './tr')
            events_rows = self.driver.find_element('xpath', '//*[@id="gridCaseEvents"]/tbody').find_elements('xpath', './tr')
            outstanding_amount_rows = self.driver.find_element('xpath', '//*[@id="feesAccordionCollapse"]/div/table/tbody').find_elements('xpath', './tr')
            receipts_rows = self.driver.find_element('xpath', '//*[@id="Table2"]').find_element('xpath', './tbody').find_elements('xpath', './tr')
            case_dockets_rows = self.driver.find_element('xpath', '//*[@id="gridDockets"]/tbody').find_elements('xpath', './tr')
        except:
            # If stuck here, find the corresponding row element, open the page manually, then press 'c'
            bp()
            summary_text = self.driver.find_element('xpath', '//*[@id="summaryAccordionCollapse"]').text
            charges_rows = self.driver.find_element('xpath', '//*[@id="gridCharges"]/tbody').find_elements('xpath', './tr')
            events_rows = self.driver.find_element('xpath', '//*[@id="gridCaseEvents"]/tbody').find_elements('xpath', './tr')
            outstanding_amount_rows = self.driver.find_element('xpath', '//*[@id="feesAccordionCollapse"]/div/table/tbody').find_elements('xpath', './tr')
            receipts_rows = self.driver.find_element('xpath', '//*[@id="Table2"]').find_element('xpath', './tbody').find_elements('xpath', './tr')
            case_dockets_rows = self.driver.find_element('xpath', '//*[@id="gridDockets"]/tbody').find_elements('xpath', './tr')

        # Get summary id to be used as FK
        try:
            summary_text += '\n' # To prevent index out of range error
            summary = utils.parse_text('summary', summary_text)
            summary['defendant_id'] = int(defendant_id)
            summary_query = utils.create_query(summary, 'summary')
            print(summary_query)
            self.mycursor.execute(summary_query)
            self.mydb.commit()
            self.mycursor.execute("SELECT LAST_INSERT_ID()")
            result = self.mycursor.fetchone()
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
                self.mycursor.execute(charge_query)
                self.mydb.commit()
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
                self.mycursor.execute(event_query)
                self.mydb.commit()
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
                self.mycursor.execute(outstanding_amount_query)
                self.mydb.commit()
        except:
            print('[ERROR] Outstanding amounts error')
            bp()

        # Create query for receipts
        try:
            for receipts in receipts_rows:
                receipt = utils.parse_text('receipts', receipts)
                if receipt == None:
                    break
                receipt['summary_id'] = summary_id
                receipt_query = utils.create_query(receipt, 'receipt')
                print(receipt_query)
                self.mycursor.execute(receipt_query)
                self.mydb.commit()
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
                self.mycursor.execute(case_docket_query)
                self.mydb.commit()
        except:
            print('[ERROR] Case dockets error')
            bp()
            
            # Go to the next page
            # try:
            #     self.driver.find_element('xpath', '//*[@id="gridpager"]/table/tbody/tr/td[6]/a').click()
            #     self.driver.implicitly_wait(3)
            # except:
            #     bp()

if __name__ == '__main__':
    esc = escambia()
    esc.bond_search()
