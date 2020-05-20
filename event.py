
# Google Sheets Imports
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Flask Imports
import re
import requests
import os

# Error Imports
from utils import *

# Authorization
DIRNAME = os.path.dirname(__file__)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Candidate Tracker / Announcements
tracker_creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(DIRNAME, 'assets/creds/tracker_creds.json'), scope)
tracker_client = gspread.authorize(tracker_creds)

sheet = tracker_client.open('Candidate Tracking Sheet (Internal)')

# Help Text
helpTxt = [{'text': 'Type `/newevent <type> "<name>" <date> <password>` to create a new event'}]

# Sheet Names
socialSheet = sheet.worksheet('Socials')
profSheet = sheet.worksheet('Professional Events')


def addEvent(event, name, pwd):
    # Figure out exact event worksheet
    worksheet = None
    if event == 'social':
        worksheet = socialSheet
    else:
        worksheet = profSheet
    
    # Grab all the event names in the spreadsheet (event names)
    event_names = worksheet.row_values(2)
    
    # Check whether there exists an empty cell until end of spreadsheet
    if "" not in event_names:
        return "No more space within spreadsheet. Contact an officer to increase spreadsheet size"
    
    empty_index_col = event_names.index('') + 1

    # Update empty cell with current password
    worksheet.update_cell(1, empty_index_col, pwd)
    # Update empty cell with current event
    worksheet.update_cell(2, empty_index_col, name)

    return None

"""

"""
def parseEvent(text):
    # Parse out the groups
    match_text = re.match(r'(\w+)\s+[\'"“”‘’](.+)[\'"“”‘’]\s+(\d+/\d+)\s+(\w+)', text)
    if match_text == None:
         return None, None, None, 'Invalid command entry (e.g. `/newevent prof "Company" 2/24 hello`)'

    event_guess = match_text.group(1).lower()
    event_name = "{name} ({date})".format(name=match_text.group(2), date=match_text.group(3))
    event_pwd = match_text.group(4)

    socials = ['s', 'soc', 'social', 'socials']
    profs = ['p', 'prof', 'professional']

    if event_guess in socials:
        event_type = 'social'
    elif event_guess in profs:
        event_type = 'prof'
    else:
        return None, None, None, 'Invalid Event. `social` or `prof` are possible events'
        
    if len(event_name) < 10:
        return None, None, None, 'Specify a proper event name (e.g. Codenames (2/29))'
    
    if len(event_pwd) < 5:
        return None, None, None, 'Passwords must be longer than 5 characters'
    
    return event_type, event_name, event_pwd, None
    
"""

"""
def create_event(req):
    # Login into client
    if tracker_creds.access_token_expired:
        tracker_client.login()
    
    # Check if request stemmed from #events channel
    if req['channel_name'] != 'events':
        return error_res('Command not submitted in #events channel', helpTxt, req['response_url'])
    
    event, name, pwd, err = parseEvent(req['text'])

    if err:
        error_res(err, helpTxt, req['response_url'])
        return
    
    err = addEvent(event, name, pwd)
    
    if err:
        error_res(err, helpTxt, req['response_url'])
        return

    data = {
        'response_type': 'ephemeral',
        'text': 'Sucessfully created a {event} event with {name} and {pwd}'.format(event=event, name=name, pwd=pwd)
    }
    requests.post(req['response_url'], json=data)