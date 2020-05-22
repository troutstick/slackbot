# Google Sheets Imports
import gspread

# Flask Imports
import re
import requests

# Error Imports
from utils import *
import settings
import authorization

# Help Text
helpTxt = [{'text': 'Type `/newevent <type> "<name>" <date> <password>` to create a new event'}]

sheetNames = ['Socials', 'Professional Events']
socialSheet, profSheet = authorization.getSheetObjects(sheetNames)


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
    event_date = match_text.group(3)
    event_name = "{name} ({date})".format(name=match_text.group(2), date=event_date)
    event_pwd = match_text.group(4)

    socials = ['s', 'soc', 'social', 'socials']
    profs = ['p', 'prof', 'professional']

    if event_guess in socials:
        event_type = 'social'
    elif event_guess in profs:
        event_type = 'prof'
    else:
        return None, None, None, 'Invalid Event. `social` or `prof` are possible events'
    
    # Name Checking
    if len(event_name) < 10:
        return None, None, None, 'Specify a proper event name (e.g. Codenames (2/29))'
    
    # Date Checking
    slash_index = event_date.index("/")
    month = int(event_date[:slash_index])
    day = int(event_date[slash_index+1:])

    if (month < 1 or month > 12) or (day < 1 or day > 31):
        return None, None, None, 'Invalid date provided'
    
    # Covering Feburary
    if (month== 2) and (day > 29):
        return None, None, None, 'Invalid date provided'

    # Covering March, June, September, November max 30 days
    if (month == 4 or month == 6 or month == 9 or month == 11) and (day > 30):
        return None, None, None, 'Invalid date provided'

    # Password Checking
    if len(event_pwd) < 5:
        return None, None, None, 'Passwords must be longer than 5 characters'

    if len(text) != len(match_text.group(0)):
        return None, None, None, 'Password must be space-less'
    
    # Everything works
    return event_type, event_name, event_pwd, None
    
"""

"""
def create_event(req):
    # Login into client
    authorization.login()
    
    # Check if request stemmed from #events channel
    softdev_id = settings.getChannelIDs()['softdev-bot-testing']
    if req['channel_name'] != 'events' and req['channel_id'] != softdev_id:
        return error_res('Command must be submitted in #events channel', helpTxt, req['response_url'])
    
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
        "blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Successfully added {name} as an event to the spreadsheet \n To finish creating an event remember to add it to the UPE Google Calendar!".format(name=name)
			}
            
		},
		{
			"type": "divider"
		}
        ]
    }
    requests.post(req['response_url'], json=data)