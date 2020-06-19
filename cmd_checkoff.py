"""
UPE Slack Bot Slack Commands
----------------------------------------------------------------------------
/checkoff challenge | <candidate name>
- Marks given candidate as completed for their challenge

/checkoff oh | <candidate name>
- Compares 

/checkoff help
- Retrieves the help text shown
"""

# Google Sheets Imports
import gspread

# Flask Imports
import re
import requests

# Package Imports
import authorization
import settings
import utils

# Help Text
helpTxt = settings.get_actions()['/checkoff']['helpTxt']

# Spreadsheet Names
sheetNames = ['Candidate Tracker', 'One-On-Ones']
candSheet, onoSheet = authorization.get_sheet_objects(sheetNames)

"""
Parse the text field of slack payload: '<type> | <candidate name>'
@params: text - slack payload of command
@return: event_type, candidate_name, err - if err is None then valid parse
"""
def parseText(text):
    # Parse out the groups
    match_text = re.match(r'(\w+)\s*\|\s*(.+)', text)

    if match_text == None:
        return None, None, "Invalid command entry (e.g. /checkoff o John Doe"

    event_type = match_text.group(1).lower()
    candidate_name = match_text.group(2).strip()

    office = ['o', '1', 'oh', 'office', 'hours']
    socials = ['s', 'soc', 'social', 'socials']
    profs = ['p', 'prof', 'professional']
    chall = ['c', 'chall', 'challenge']

    if event_type in office:
        return 'oh', candidate_name, None
    elif event_type in socials:
        return 'social', candidate_name, None
    elif event_type in profs:
        return 'prof', candidate_name, None
    elif event_type in chall:
        return 'chall', candidate_name, None

    return None, None, "Invalid event type. o - office hours, s - socials, p - professional, c - challenge"

"""
Check whether slack command submitted in a valid channel
"""
def is_valid_channel(event_type, channel_id):
    channel_dct = settings.get_channel_ids()

    # Bypass all channel access rights
    if channel_dct['softdev-bot-testing'] == channel_id:
        return None

    # Office hours command can be ran in #office-hours and #officers
    if event_type == 'oh':
        if channel_dct['oh-holders'] == channel_id or channel_dct['officers'] == channel_id:
            return None
        else:
            return 'Office Hour command must be submitting in #office-hours channel'
    elif channel_dct['officers'] != channel_id:
        return 'Command must be submitted in #officers channel'
    return None

"""
Find the candidate names given the row values (1-indexed)
@params lst - list of row positions in spreadsheet
@return names - list of candidate names
"""
def get_candidate_names(lst):
    names = []
    stdColumnFormat = settings.get_fixed_column_values()
    for row in lst:
        names.append(candSheet.cell(row, stdColumnFormat['name']).value)
    return names

"""
Check off office hours
@params candidate_row_number - row position on spreadsheet of candidate
@return text - result of checking off candidate
"""
def checkoff_office_hours(candidate_row_number):
    # Column number of Checked off Count column
    checked_off_column = settings.get_one_on_one_columns()['Checked Off']

    # Retrieve previous cell value
    checked_off_count = int(onoSheet.cell(candidate_row_number, checked_off_column).value)

    # Increment count
    checked_off_count += 1

    # Checkoff candidate for their office hour
    onoSheet.update_cell(candidate_row_number, checked_off_column, str(checked_off_count))
    return 'Successfully checked off {name} for office hours!'

"""
Check off challenge event
@params candidate_row_number - row position on spreadsheet of candidate
@return text - result of checking off candidate
"""
def checkoff_challenge(candidate_row_number):
    # Column number of Challenge finished column
    challenge_col = settings.get_candidate_columns()['challenge_finished']

    # Retrieve previous cell value
    challenge_cell_value = candSheet.cell(candidate_row_number, challenge_col).value

    # Check if candidate previously checked off
    if challenge_cell_value == "YES":
        return "Candidate was previously checked off already"

    # Checkoff candidate for their challenge
    candSheet.update_cell(candidate_row_number, challenge_col, "YES")
    return 'Successfully checked off {name} for their challenge!'

"""
Execute /checkoff command
"""
def exec_checkoff_candidate(req):
    # Login into client
    authorization.login()

    # Parse the command text
    event_type, candidate_name, err = parseText(req['text'])
    if err:
        utils.error_res(err, helpTxt, req['response_url'])
        return

    # Check command originated in correct channel
    err = is_valid_channel(event_type, req['channel_id'])
    if err:
        utils.error_res(err, helpTxt, req['response_url'])
        return

    # Match all candidates
    matched_candidiate_list = utils.get_candidate_row_number(candidate_name, candSheet)
    if len(matched_candidiate_list) == 0:
        utils.error_res("No matched candidate found", helpTxt, req['response_url'])

    if len(matched_candidiate_list) > 3:
        utils.error_res("Multiple candidate name matches, please be more specific", helpTxt, req['response_url'])

    matched_candidate_names = get_candidate_names(matched_candidiate_list)
    if len(matched_candidiate_list) > 1:
        candidate_text = ' '.join(matched_candidate_names)
        utils.error_res("Matched more than 1 candidate: {names}".format(names=candidate_text), helpTxt, req['response_url'])

    # Depending on event type execute checkoff different commands
    text = None
    if event_type == 'oh':
        # Checkoff Office Hour
        text = checkoff_office_hours(matched_candidiate_list[0])

    elif event_type == 'social' or event_type == 'prof':
        # TODO
        utils.error_res("Command not implemented yet", helpTxt, req['response_url'])
        return
    else:
        # Checkoff Challenge
        text = checkoff_challenge(matched_candidiate_list[0])


    data = {
        'response_type': 'ephemeral',
        "blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": text.format(name=candidate_name)
			}

		},
		{
			"type": "divider"
		}
        ]
    }
    requests.post(req['response_url'], json=data)
