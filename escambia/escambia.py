from pdb import set_trace
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector
import utils as utils
import argparse

class escambia(object):
    def __init__(self, args):
        # Prepare mysql connection
        self.mydb = mysql.connector.connect(
            host=args.host,
            user=args.user,
            password=args.password,
            database=args.database
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

        # Define indices for finding inmages
        self.page_idx = 0
        self.row_idx = 0
        self.defendant_id = 0
    
    def print_help(self):
        print("""
    Welcome to escambia web scraping tool.
    Please follow the instruction below.
    1) Set "Date Opened" field by selecting the dates
    2) Set Court Types: FELONY, MISDEMEANOR
    3) Solve the capcha quiz -- this will lead to a list of cases
    4) Run (1) Find an inmate with a bond amount -- this will find
       an inmate with nonzero bond amount and paste the name to the
       search by name option
    5) Solve the capcha quiz -- this will lead to a list of cases
       made by the selected defendant
    6) Click on the defendant name
    7) Run (2) Scrape inmate info
    8) Go back, and click on the case number
    9) Run (3) Scrape summary
    10) Click on "Bonds" tab and run (4) Scrape bond for each bond
        item
    11) Repeat 8) - 10) for each case number
    12) Once you're done with scraping all info associated with
        current defendant, go back to a list of cases, and repeat
        4) - 11)
""")

    def run(self):
        self.driver.get(self.url)
        print('[INFO] Before selecting an option, make sure you are at correct webpage')
        while True:
            user_input = input("""
=====================================
Select an option:
(1) Find an inmate with a bond amount
(2) Scrape inmate info
(3) Scrape summary
(4) Scrape bond
(q) Quit
=====================================
>> """)
            if user_input == "1":
                # code for option 1
                try:
                    self.find_next_inmate()
                    print('[INFO] Inmate found. Solve the puzzle and move on to the defendant info page for the defendant_scrape.')
                except:
                    print('[WARN] Cannot run find_next_inmate. Are you at the correct webpage?')
            elif user_input == "2":
                try:
                    self.defendant_scrape()
                    print('[INFO] Defendant scrape done. Move on to the summary page for the summary_scrape.')
                except:
                    print('[WARN] Cannot run defendant_scrape. Are you at the correct webpage?')
            elif user_input == "3":
                try:
                    self.summary_scrape(self.defendant_id)
                    print('[INFO] Summary scrape done. Move on to the bond tab for the bond_scrape.')
                except:
                    print('[WARN] Cannot run summary_scrape. Are you at the correct webpage?')
            elif user_input == "4":
                try:
                    self.bond_scrape(self.defendant_id)
                    print('[INFO] Bond scrape done. Move on to the next bond, or move on to the next case.')
                except:
                    print('[WARN] Cannot run bond_scrape. Are you at the correct webpage?')
            elif user_input.lower() == "q":
                print("Exiting program...")
                break
            else:
                print("Invalid input. Please enter a number between 0 and 2 or 'q' to quit.")


    def find_next_inmate(self):
        # for page_idx in range(100):
        while True:
            table = self.driver.find_element('xpath', '//*[@id="gridSearchResults"]/tbody')
            row_num = len(table.find_elements('xpath', './tr'))
            while self.row_idx < row_num:
                self.row_idx += 1
                print(f"Searching: PAGE {self.page_idx + 1} ROW {self.row_idx}\r", end="")
                row = table.find_elements('xpath', './tr')[self.row_idx]

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
                    bond_table = self.driver.find_element('xpath', '//*[@id="bondItems"]')
                    
                    # If there is a bond
                    if bond_table.text != '(0) Bonds':
                        # Look for the inmate name
                        print(f"[INFO] Inmate found: {name} @ PAGE {self.page_idx + 1} ROW {self.row_idx + 1}")
                        self.name_search(name)
                        return


    def name_search(self, name):
        self.driver.find_element('xpath', '//*[@id="Home.aspx/Search"]/a').click()
        self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td[1]/table/tbody/tr[2]/td/div/label[1]/input').click()
        self.driver.find_element('xpath', '//*[@id="name"]').send_keys(name)
        return


    def bond_scrape(self, defendant_id):
        bond_number = self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[1]/td[2]').text
        issued_date = self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]').text
        amount = self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[5]/td[2]').text

        defendant_query = utils.create_query({"defendant_id": int(defendant_id),"bond_number": bond_number,"issued_date": issued_date,"amount": amount}, 'bond')
        print(defendant_query)
        try:
            self.mycursor.execute(defendant_query)
            self.mydb.commit()
        except:
            print('[WARN] PK constraint failed. Moving on without recording.')
            return


    def defendant_scrape(self):
        name = self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[1]/td[2]').text
        dob = self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[4]/td[2]').text
        gender = self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[6]/td[2]').text
        id = self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[8]/td[2]').text

        defendant_query = utils.create_query({"id": id, "name": name,"dob": dob,"gender": gender}, 'defendant')
        print(defendant_query)
        try:
            self.mycursor.execute(defendant_query)
            self.mydb.commit()
        except:
            print('[WARN] PK constraint failed. Moving on without recording.')
            return
        
        # Read defendant id for FK
        print(f'[INFO] Defendant id: {id}')
        self.defendant_id = id
    
    def summary_scrape(self, defendant_id):
        # Find necessary elements
        summary_text = self.driver.find_element('xpath', '//*[@id="summaryAccordionCollapse"]').text
        charges_rows = self.driver.find_element('xpath', '//*[@id="gridCharges"]/tbody').find_elements('xpath', './tr')
        events_rows = self.driver.find_element('xpath', '//*[@id="gridCaseEvents"]/tbody').find_elements('xpath', './tr')
        outstanding_amount_rows = self.driver.find_element('xpath', '//*[@id="feesAccordionCollapse"]/div/table/tbody').find_elements('xpath', './tr')
        receipts_rows = self.driver.find_element('xpath', '//*[@id="Table2"]').find_element('xpath', './tbody').find_elements('xpath', './tr')
        case_dockets_rows = self.driver.find_element('xpath', '//*[@id="gridDockets"]/tbody').find_elements('xpath', './tr')

        # Get summary id to be used as FK
        summary_text += '\n' # To prevent index out of range error
        summary = utils.parse_text('summary', summary_text)
        summary['defendant_id'] = int(defendant_id)
        summary_query = utils.create_query(summary, 'summary')
        print(summary_query)
        try:
            self.mycursor.execute(summary_query)
            self.mydb.commit()
        except:
            print('[WARN] PK constraint failed. Moving on without recording.')
            return
        self.mycursor.execute("SELECT LAST_INSERT_ID()")
        result = self.mycursor.fetchone()
        summary_id = result[0]

        # Create query for charges
        for charges in charges_rows:
            charge = utils.parse_text('charges', charges)
            charge['summary_id'] = summary_id
            charge_query = utils.create_query(charge, 'charge')
            print(charge_query)
            try:
                self.mycursor.execute(charge_query)
                self.mydb.commit()
            except:
                print('[WARN] PK constraint failed. Moving on without recording.')
                return
        
        # Create query for  events
        for events in events_rows:
            event = utils.parse_text('events', events)
            if event == None:
                break
            event['summary_id'] = summary_id
            event_query = utils.create_query(event, 'event')
            print(event_query)
            try:
                self.mycursor.execute(event_query)
                self.mydb.commit()
            except:
                print('[WARN] PK constraint failed. Moving on without recording.')
                return
        
        # Create query for  outstanding amounts
        for outstanding_amounts in outstanding_amount_rows:
            outstanding_amount = utils.parse_text('outstanding_amounts', outstanding_amounts)
            if outstanding_amount == None:
                break
            outstanding_amount['summary_id'] = summary_id
            outstanding_amount_query = utils.create_query(outstanding_amount, 'outstanding_amount')
            print(outstanding_amount_query)
            try:
                self.mycursor.execute(outstanding_amount_query)
                self.mydb.commit()
            except:
                print('[WARN] PK constraint failed. Moving on without recording.')
                return

        # Create query for receipts
        for receipts in receipts_rows:
            receipt = utils.parse_text('receipts', receipts)
            if receipt == None:
                break
            receipt['summary_id'] = summary_id
            receipt_query = utils.create_query(receipt, 'receipt')
            print(receipt_query)
            try:
                self.mycursor.execute(receipt_query)
                self.mydb.commit()
            except:
                print('[WARN] PK constraint failed. Moving on without recording.')
                return

        # Get Create query for  dockets
        for case_dockets in case_dockets_rows:
            case_docket = utils.parse_text('case_dockets', case_dockets)
            if case_docket == None:
                break
            case_docket['summary_id'] = summary_id
            case_docket_query = utils.create_query(case_docket, 'case_docket')
            print(case_docket_query)
            try:
                self.mycursor.execute(case_docket_query)
                self.mydb.commit()
            except:
                print('[WARN] PK constraint failed. Moving on without recording.')
                return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Escambia web scraping tool')
    parser.add_argument('--host', type=str, help='hostname for the database server', required=True)
    parser.add_argument('--user', type=str, help='username for the database', required=True)
    parser.add_argument('--password', type=str, help='password for the database', required=True)
    parser.add_argument('--database', type=str, help='name of the database', required=True)
    args = parser.parse_args()

    print('[INFO] Starting a scraping tool...')
    esc = escambia(args)
    esc.print_help()
    esc.run()
