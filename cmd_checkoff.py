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
sheetNames = ['Candidate Tracker', 'One-On-Ones', 'Officer Chats']
candSheet, onoSheet, officerSheet = authorization.get_sheet_objects(sheetNames)

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
Parse the text field of slack payload: '<type> | <candidate name>'
@params: text - slack payload of command
@return: event_type, candidate_name, err - if err is None then valid parse
"""
def parseText(text):

    # Parse out the groups
    match_text = text.split('|')

    if len(match_text) != 2 and len(match_text) != 3:
        return None, None, None, "Invalid command entry (e.g. /checkoff oh | John Doe)"

    event_type = match_text[0].lower().strip()
    candidate_name = match_text[1].strip()
    officer_name = ""

    office_hours = ['1', 'oh', 'office', 'hours', 'ps']
    socials = ['s', 'soc', 'social', 'socials']
    profs = ['p', 'prof', 'professional']
    chall = ['c', 'chall', 'challenge']
    officer_chats = ['oc', 'officer', 'officer chat', 'officer chats']

    if event_type in office_hours:
        if len(match_text) == 2:
            return 'oh', candidate_name, officer_name, None
        else:
            return None, None, None, "Invalid command for checking off office hours (e.g. /checkoff oh | candidate)"
    # elif event_type in socials:
    #     return 'social', candidate_name, officer_name, None
    # elif event_type in profs:
    #     return 'prof', candidate_name, officer_name, None
    elif event_type in chall:
        if len(match_text) == 2:
            return 'chall', candidate_name, officer_name, None
        else:
            return None, None, None, "Invalid command for checking off challenge (e.g /checkoff c | candidate)"
    elif event_type in officer_chats:
        if len(match_text) == 3:
            officer_name = match_text[2].strip()
            return 'oc', candidate_name, officer_name.capitalize(), None
        else:
            return None, None, None, "Please write officer name in checking off for officer chats (e.g. /checkoff oc | John Doe | UPE)"

    return None, None, None, "Invalid event type. oh - office hours, c - challenge, oc - officer chats"

"""
Find the candidate names given the row values (1-indexed)
@params lst - list of row positions in spreadsheet
@return names - list of candidate names
"""
def get_candidate_names(lst, name_column):
    names = []
    for row in lst:
        names.append(candSheet.cell(row, name_column).value)
    return names

"""
Check off office hours
@params candidate_row_number - row position on spreadsheet of candidate
@return text - result of checking off candidate
"""
def checkoff_office_hours(candidate_row_number, checked_off_column):
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
def checkoff_challenge(candidate_row_number, challenge_column):
    # Retrieve previous cell value
    challenge_cell_value = candSheet.cell(candidate_row_number, challenge_column).value

    # Check if candidate previously checked off
    if challenge_cell_value == "YES":
        return "Candidate was previously checked off already"

    # Checkoff candidate for their challenge
    candSheet.update_cell(candidate_row_number, challenge_column, "YES")
    return 'Successfully checked off {name} for their challenge!'

def checkoff_officer_chats(candidate_row_number, total_officer_chat_column, officer_name):
    # Retrieve previous cell value
    officer_chat_count = int(officerSheet.cell(candidate_row_number, total_officer_chat_column).value)

    # Write Officer Name in next available column
    update_column = officer_chat_count + 5

    if update_column == total_officer_chat_column:
        return 'No more space within spreadsheet. Contact an exec to increase space'
    
    officerSheet.update_cell(candidate_row_number, update_column, officer_name)
    return 'Successfully checked off {name} for their officer chat!'

"""
Execute /checkoff command
"""
def exec_checkoff_candidate(req):
    # Login into client
    authorization.login()

    # Parse the command text
    event_type, candidate_name, officer_name, err = parseText(req['text'])
    if err:
        utils.error_res(err, helpTxt, req['response_url'])
        return

    # Check command originated in correct channel
    err = is_valid_channel(event_type, req['channel_id'])
    if err:
        utils.error_res(err, helpTxt, req['response_url'])
        return

    # Find current column locations of candidate sheet
    col_dct = utils.get_candidate_sheet_col_numbers()

    # Match all candidates
    matched_candidiate_list = utils.get_candidate_row_number(candidate_name, candSheet, col_dct['name'])
    if len(matched_candidiate_list) == 0:
        utils.error_res("No matched candidate found", helpTxt, req['response_url'])
        return

    if len(matched_candidiate_list) > 3:
        utils.error_res("Multiple candidate name matches, please be more specific", helpTxt, req['response_url'])
        return

    matched_candidate_names = get_candidate_names(matched_candidiate_list, col_dct['name'])
    if len(matched_candidiate_list) > 1:
        candidate_text = ', '.join(matched_candidate_names)
        utils.error_res("Matched more than 1 candidate: {names}".format(names=candidate_text), helpTxt, req['response_url'])
        return

    # Depending on event type execute checkoff different commands
    text = None
    if event_type == 'oh':
        # Checkoff Office Hour
        text = checkoff_office_hours(matched_candidiate_list[0], col_dct['oh_checked_off_count'])
    elif event_type == 'social' or event_type == 'prof':
        # TODO
        utils.error_res("Command not implemented yet", helpTxt, req['response_url'])
        return
    elif event_type == 'chall':
        # Checkoff Challenge
        text = checkoff_challenge(matched_candidiate_list[0], col_dct['challenge_completed'])
    elif event_type =='oc':
        # Checkoff Officer Chat
        text = checkoff_officer_chats(matched_candidiate_list[0], col_dct['officer_total_count'], officer_name)


    data = {
        'response_type': 'ephemeral',
        "blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": text.format(name=matched_candidate_names[0])
			}

		},
		{
			"type": "divider"
		}
        ]
    }
    requests.post(req['response_url'], json=data)
