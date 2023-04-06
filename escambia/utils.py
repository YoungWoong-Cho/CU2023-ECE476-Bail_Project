from typing import Union, List, Dict
import selenium
from pdb import set_trace as bp

def parse_text(_type: str, element:Union[str, selenium.webdriver.remote.webelement.WebElement]):
    assert _type in ['summary', 'charges', 'events', 'outstanding_amounts', 'receipts', 'case_dockets'], \
        'type not understood'
    
    if type(element) == selenium.webdriver.remote.webelement.WebElement:
        if len(element.find_elements('xpath', './td')) == 1:
            return
    
    if _type == 'summary':
        summary = {
            'court_type': element.split('\n')[element.split('\n').index('Court Type:') + 1].replace("'", "\\'"),
            'case_type': element.split('\n')[element.split('\n').index('Case Type:') + 1].replace("'", "\\'"),
            'case_number' : element.split('\n')[element.split('\n').index('Case Number:') + 1].replace("'", "\\'"),
            'uniform_case_number': element.split('\n')[element.split('\n').index('Uniform Case Number:') + 1].replace("'", "\\'"),
            'status': element.split('\n')[element.split('\n').index('Status:') + 1].replace("'", "\\'"),
            'clerk_file_date': element.split('\n')[element.split('\n').index('Clerk File Date:') + 1].replace("'", "\\'"),
            'status_date': element.split('\n')[element.split('\n').index('Status Date:') + 1].replace("'", "\\'"),
            'total_fees_due': element.split('\n')[element.split('\n').index('Total Fees Due:') + 1].replace("'", "\\'"),
            'agency': element.split('\n')[element.split('\n').index('Agency:') + 1].replace("'", "\\'"),
        }
    elif _type == 'charges':
        summary = {
            'count': element.find_elements('xpath', './td')[1].text.replace("'", "\\'"),
            'description': element.find_elements('xpath', './td')[2].text.replace("'", "\\'"),
            'level': element.find_elements('xpath', './td')[3].text.replace("'", "\\'"),
            'degree': element.find_elements('xpath', './td')[4].text.replace("'", "\\'"),
            'plea': element.find_elements('xpath', './td')[5].text.replace("'", "\\'"),
            'disposition': element.find_elements('xpath', './td')[6].text.replace("'", "\\'"),
        }
    elif _type == 'events':
        summary = {
            'date': element.find_elements('xpath', './td')[0].text.replace("'", "\\'"),
            'event': element.find_elements('xpath', './td')[1].text.replace("'", "\\'"),
            'judge': element.find_elements('xpath', './td')[2].text.replace("'", "\\'"),
            'location': element.find_elements('xpath', './td')[3].text.replace("'", "\\'"),
            'result': element.find_elements('xpath', './td')[4].text.replace("'", "\\'"),
        }
    elif _type == 'outstanding_amounts':
        summary = {
            'count': element.find_elements('xpath', './td')[0].text.replace("'", "\\'"),
            'code': element.find_elements('xpath', './td')[1].text.replace("'", "\\'"),
            'description': element.find_elements('xpath', './td')[2].text.replace("'", "\\'"),
            'paid': element.find_elements('xpath', './td')[3].text.replace("'", "\\'"),
            'waived': element.find_elements('xpath', './td')[4].text.replace("'", "\\'"),
            'balance': element.find_elements('xpath', './td')[5].text.replace("'", "\\'"),
            'payment_plan': element.find_elements('xpath', './td')[6].text.replace("'", "\\'"),
            'due_date': element.find_elements('xpath', './td')[7].text.replace("'", "\\'"),
        }
    elif _type == 'receipts':
        summary = {
            'date': element.find_elements('xpath', './td')[0].text.replace("'", "\\'"),
            'recipt_num': element.find_elements('xpath', './td')[1].text.replace("'", "\\'"),
            'applied_amount': element.find_elements('xpath', './td')[2].text.replace("'", "\\'"),
        }
    elif _type == 'case_dockets':
        summary = {
            'date': element.find_elements('xpath', './td')[1].text.replace("'", "\\'"),
            'entry': element.find_elements('xpath', './td')[2].text.replace("'", "\\'"),
        }
    else:
        bp()

    return summary

def create_query(data:Dict, table_name:str):
    query = f"INSERT INTO {table_name}"
    column_names = "("
    values = "("
    for key, val in data.items():
        column_names += f'{key},'
        values += f"\'{val}\',"
    column_names = column_names[:-1] + ')'
    values = values[:-1] + ')'
    
    query += f" {column_names} VALUES {values}"

    return query
