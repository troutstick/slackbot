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
sheetNames = ['Candidate Tracker', 'One-On-Ones', 'Feedback Responses']
candSheet, onoSheet, feedback_sheet = authorization.get_sheet_objects(sheetNames)

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
    if event_type == 'oh' and channel_dct['office-hours'] != channel_id and channel_dct['officers'] != channel_id:
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
    # Find Number of Current One on One
    candidate_row = onoSheet.row_values(candidate_row_number)

    # Get total number of One on Ones in Candidate Tracking Sheet (last number in cell)
    current_count = int(candidate_row[-1])

    # Candidate email (unique number)
    candidate_email = candidate_row[settings.get_fixed_column_values()['email']-1]

    # Get number of feedback Ones in Feedback form
    oh_feedback_cols = settings.get_OH_feedback_columns()
    feedback_emails = feedback_sheet.col_values(oh_feedback_cols['email'])

    feedback_count = feedback_emails.count(candidate_email)

    if current_count > feedback_count:
        return "Something went wrong: candidate sheet checked off more than feedback form please examine it"

    if current_count == feedback_count:
        return "Candidate has already been checked off for all office hours"

    # Find latest cell value
    new_feedback_row_number = [i for i, email in enumerate(feedback_emails) if email == candidate_email][current_count]
    new_feedback_row = feedback_sheet.row_values(new_feedback_row_number)
    oh_type = new_feedback_row[oh_feedback_cols['oh_type']-1]
    oh_name = new_feedback_row[oh_feedback_cols['oh_holder']-1]

    # Check if space left in spreadsheet
    if "" not in candidate_row:
        return "No more space within spreadsheet. Contact an officer to increase spreadsheet size"
    # Find the first empty cell that exists
    empty_index_col = candidate_row.index('') + 1

    # Update cell values with current content
    onoSheet.update_cell(candidate_row_number, empty_index_col, oh_type)
    onoSheet.update_cell(candidate_row_number, empty_index_col+1, oh_name)

    return 'Successfully checked off {type} by {name}'.format(type=oh_type, name=oh_name)

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
    return 'Successfully checked off candidate for their challenge!'

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
				"text": text
			}

		},
		{
			"type": "divider"
		}
        ]
    }
    requests.post(req['response_url'], json=data)
