"""
UPE Slack Bot Slack Commands
----------------------------------------------------------------------------
/newevent <type> | <name> | <mm/dd> | <password>
- Inserts name and date (e.g. Jane Street (2/24)) into spreadsheet
- Inserts password for checkoff on the event into spreadshseet

/newevent help
- Retrieves the help text shown

/newevent list-all
- Lists all the current events
"""
# Google Sheets Imports
import gspread

# Flask Imports
import re
import requests

# Package Imports
import authorization
import utils
import settings

# Help Text
helpTxt = settings.get_actions()['/newevent']['helpTxt']

# Candidate Worksheets
sheetNames = ['Socials', 'Professional Events']
socialSheet, profSheet = authorization.get_sheet_objects(sheetNames)

# Keywords - Type attribute
keywords = ['social', 'prof']
socials, profs = utils.get_keywords(keywords)

# Row values on spreadsheet for gspread to retrieve correct values
NAME_ROW = 2
PWD_ROW = 1

"""
Add event into the Candidate Tracker spreadsheet
@params: event, name, pwd - attributes needed to insert into spreadsheet
@return: err - if err is None then successful add 
"""
def add_event(event, name, pwd):
    # Figure out exact event worksheet
    worksheet = None
    if event == 'social':
        worksheet = socialSheet
    else:
        worksheet = profSheet
    
    # Grab all the event names in the spreadsheet (event names)
    event_names = worksheet.row_values(NAME_ROW)
    
    # Check whether there exists an empty cell until end of spreadsheet
    if "" not in event_names:
        return "No more space within spreadsheet. Contact an officer to increase spreadsheet size"
    
    empty_index_col = event_names.index('') + 1

    # Update empty cell with current password
    worksheet.update_cell(PWD_ROW, empty_index_col, pwd)
    # Update empty cell with current event
    worksheet.update_cell(NAME_ROW, empty_index_col, name)

    return None

"""
Parse the text field of slack payload: '<type> | <event name> | <date> | <password>'
@params: text - slack payload of command
@return: event_type, name, pwd, err - if err is None then valid parse
"""
def parse_event(text):
    # Parse out the groups
    match_text = re.match(r'(\w+)\s*\|\s*(.+)\s*\|\s*(\d+/\d+)\s*\|\s*(\w+)', text)
    if match_text == None:
         return None, None, None, 'Invalid command entry (e.g. `/newevent prof "Company" 2/24 hello`)'

    # Retrieve matches from reger command
    event_guess = match_text.group(1).lower()
    event_date = match_text.group(3)
    event_name = "{name} ({date})".format(name=match_text.group(2).strip(), date=event_date)
    event_pwd = match_text.group(4)

    # Check whether valid event
    if event_guess.lower() in socials:
        event_type = 'social'
    elif event_guess.lower() in profs:
        event_type = 'prof'
    else:
        return None, None, None, 'Invalid Event. `social` or `prof` are possible events'
    
    # Check whether valid name
    if len(event_name) < 7:
        return None, None, None, 'Specify a proper event name (e.g. Codenames (2/29))'
    
    # Check whether valid date
    slash_index = event_date.index("/")
    month = int(event_date[:slash_index])
    day = int(event_date[slash_index+1:])

    # Date bounds checking
    if (month < 1 or month > 12) or (day < 1 or day > 31):
        return None, None, None, 'Invalid date provided'
    
    # Date bound checking covering Feburary
    if (month== 2) and (day > 29):
        return None, None, None, 'Invalid date provided'

    # Date bounds checking covering March, June, September, November max 30 days
    if (month == 4 or month == 6 or month == 9 or month == 11) and (day > 30):
        return None, None, None, 'Invalid date provided'

    # Password Checking
    if len(event_pwd) < 5:
        return None, None, None, 'Passwords must be longer than 5 characters'

    # Password condition
    if len(text) != len(match_text.group(0)):
        return None, None, None, 'Password must be space-less'
    
    # Everything works
    return event_type, event_name, event_pwd, None

"""
Checks whether slack payload text is list-all action
"""
def is_list_all_command(text):
    return text.strip() == 'list-all'

"""
Lists all the events currently existed
"""
def list_all_events(response_url):
    # Retrieve event names
    socialNames = socialSheet.row_values(NAME_ROW)
    profNames = profSheet.row_values(NAME_ROW)

    # Remove non event names inside row
    socialNames = socialNames[4:len(socialNames)-1]
    profNames = profNames[4:len(profNames)-1]

    socialTxt = 'Current Social Events: \n'
    for eventName in socialNames:
        if eventName == '':
            break
        socialTxt += '\t • {name}\n'.format(name=eventName)
    
    profTxt = 'Current Professional Events: \n'
    for eventName in profNames:
        if eventName == '':
            break
        profTxt += '\t • {name}\n'.format(name=eventName)

    # Format response
    data = {
        'response_type': 'ephemeral',
        "blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": profTxt
			}
            
		},
		{
			"type": "divider"
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": socialTxt
			}
            
		},
        {
			"type": "divider"
		}
        ]
    }
    requests.post(response_url, json=data)

"""
Execute the /newevent command
"""
def exec_create_event(req):
    # Login into client
    authorization.login()
    
    # Check if request stemmed from #events channel
    softdev_id = settings.get_channel_ids()['softdev-bot-testing']
    if req['channel_name'] != 'events' and req['channel_id'] != softdev_id:
        return utils.error_res('Command must be submitted in #events channel', helpTxt, req['response_url'])

    # Check if command is 'list-all'
    if is_list_all_command(req['text']):
        list_all_events(req['response_url'])
        return

    # Parse text of body into correct components
    event, name, pwd, err = parse_event(req['text'])
    if err:
        utils.error_res(err, helpTxt, req['response_url'])
        return

    # Add event into the spreadsheet
    err = add_event(event, name, pwd)
    if err:
        utils.error_res(err, helpTxt, req['response_url'])
        return

    # Formatting for successful update
    success_text = 'Successfully added {name} as an event with password: {pwd} \n'.format(name=name, pwd=pwd)
    remind_text = 'To finish creating an event remember to add it to the UPE Google Calendar!'
    data = {
        'response_type': 'ephemeral',
        "blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": success_text + remind_text
			}
            
		},
		{
			"type": "divider"
		}
        ]
    }
    requests.post(req['response_url'], json=data)