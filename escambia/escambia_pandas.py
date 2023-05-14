from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import utils as utils

class escambia(object):
    def __init__(self):
        # Prepare pandas instances
        self.defendant_df = pd.DataFrame(columns=['id', 'name', 'dob', 'gender'])
        self.bond_df = pd.DataFrame(columns=['bond_number', 'issued_date', 'amount', 'defendant_id'])
        self.summary_df = pd.DataFrame(columns=['court_type', 'case_type', 'case_number', 'uniform_case_number', 'status', 'clerk_file_date', 'status_date', 'total_fees_due', 'agency', 'defendant_id'])
        self.charge_df = pd.DataFrame(columns=['count', 'description', 'level', 'degree', 'plea', 'disposition', 'summary_id'])
        self.event_df = pd.DataFrame(columns=['date', 'event', 'judge', 'location', 'result', 'summary_id'])
        self.outstanding_amount_df = pd.DataFrame(columns=['count', 'code', 'description', 'paid', 'waived', 'balance', 'payment_plan', 'due_date', 'summary_id'])
        self.receipt_df = pd.DataFrame(columns=['date', 'receipt_num', 'applied_amount', 'summary_id'])
        self.case_docket_df = pd.DataFrame(columns=['date', 'entry', 'summary_id'])

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
(5) Save to an excel file
(q) Quit
=====================================
>> """)
            if user_input == "1":
                # code for option 1
                # try:
                    self.find_next_inmate()
                    print('[INFO] Inmate found. Solve the puzzle and move on to the defendant info page for the defendant_scrape.')
                # except:
                #     print('[WARN] Cannot run find_next_inmate. Are you at the correct webpage?')
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
            elif user_input == "5":
                try:
                    self.save_excel()
                    print('[INFO] Save to an excel file done.')
                except:
                    print('[WARN] Cannot save to an excel file.')
            elif user_input.lower() == "q":
                print("Exiting program...")
                break
            else:
                print("Invalid input. Please enter a number between 0 and 2 or 'q' to quit.")


    def find_next_inmate(self):
        # for page_idx in range(100):
        while self.page_idx < 100:
            table = self.driver.find_element('xpath', '//*[@id="gridSearchResults"]/tbody')
            row_num = len(table.find_elements('xpath', './tr'))
            while self.row_idx < row_num - 1:
                self.row_idx += 1
                
                # To attach the element again
                table = self.driver.find_element('xpath', '//*[@id="gridSearchResults"]/tbody')

                page_str = '{:03d}'.format(self.page_idx + 1) 
                row_str = '{:02d}'.format(self.row_idx)
                print(f"Searching: PAGE {page_str} ROW {row_str}\r", end="")
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
                    # Go back to the list
                    else:
                        self.driver.back()
                        self.driver.implicitly_wait(3)
            
            # Go to the next page
            self.page_idx += 1
            self.row_idx = 0
            try:
                self.driver.find_element('xpath', '//*[@id="gridpager"]/table/tbody/tr/td[6]/a').click()
            except:
                from pdb import set_trace as bp
                bp()
            self.driver.implicitly_wait(3)
        print("[INFO] Scraping done.")


    def name_search(self, name):
        self.driver.find_element('xpath', '//*[@id="Home.aspx/Search"]/a').click()
        self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td[1]/table/tbody/tr[2]/td/div/label[1]/input').click()
        self.driver.find_element('xpath', '//*[@id="name"]').send_keys(name)
        return


    def bond_scrape(self, defendant_id):
        bond_number = self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[1]/td[2]').text
        issued_date = self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]').text
        amount = self.driver.find_element('xpath', '//*[@id="caseBondItem"]/table[1]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[5]/td[2]').text

        self.bond_df = utils.add_row({"defendant_id": int(defendant_id),"bond_number": bond_number,"issued_date": issued_date,"amount": amount}, self.bond_df)


    def defendant_scrape(self):
        name = self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[1]/td[2]').text
        dob = self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[4]/td[2]').text
        gender = self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[6]/td[2]').text
        id = self.driver.find_element('xpath', '//*[@id="mainTableContent"]/tbody/tr/td/table/tbody/tr[2]/td[2]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[8]/td[2]').text

        self.defendant_df = utils.add_row({"id": id, "name": name,"dob": dob,"gender": gender}, self.defendant_df)
        
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
        self.summary_df = utils.add_row(summary, self.summary_df)

        summary_id = self.summary_df.index[-1]

        # Create query for charges
        for charges in charges_rows:
            charge = utils.parse_text('charges', charges)
            charge['summary_id'] = summary_id
            self.charge_df = utils.add_row(charge, self.charge_df)
        
        # Create query for  events
        for events in events_rows:
            event = utils.parse_text('events', events)
            if event == None:
                break
            event['summary_id'] = summary_id
            self.event_df = utils.add_row(event, self.event_df)
        
        # Create query for  outstanding amounts
        for outstanding_amounts in outstanding_amount_rows:
            outstanding_amount = utils.parse_text('outstanding_amounts', outstanding_amounts)
            if outstanding_amount == None:
                break
            outstanding_amount['summary_id'] = summary_id
            self.outstanding_amount_df = utils.add_row(outstanding_amount, self.outstanding_amount_df)

        # Create query for receipts
        for receipts in receipts_rows:
            receipt = utils.parse_text('receipts', receipts)
            if receipt == None:
                break
            receipt['summary_id'] = summary_id
            self.receipt_df = utils.add_row(receipt, self.receipt_df)

        # Get Create query for  dockets
        for case_dockets in case_dockets_rows:
            case_docket = utils.parse_text('case_dockets', case_dockets)
            if case_docket == None:
                break
            case_docket['summary_id'] = summary_id
            self.case_docket_df = utils.add_row(case_docket, self.case_docket_df)
    
    def save_excel(self):
        with pd.ExcelWriter('scrape_result.xlsx') as writer:
            self.defendant_df.to_excel(writer, sheet_name='Defendant', index=False)
            self.bond_df.to_excel(writer, sheet_name='Bond', index=False)
            self.summary_df.to_excel(writer, sheet_name='Summary', index=False)
            self.charge_df.to_excel(writer, sheet_name='Charge', index=False)
            self.event_df.to_excel(writer, sheet_name='Event', index=False)
            self.outstanding_amount_df.to_excel(writer, sheet_name='OutstandingAmount', index=False)
            self.receipt_df.to_excel(writer, sheet_name='Receipt', index=False)
            self.case_docket_df.to_excel(writer, sheet_name='CaseDocket', index=False)

if __name__ == '__main__':
    print('[INFO] Starting a scraping tool...')
    esc = escambia()
    esc.print_help()
    esc.run()
