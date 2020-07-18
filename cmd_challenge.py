"""
UPE Slack Bot Slack Commands
----------------------------------------------------------------------------
/challenge <officer first name> | <challenge description> | <candidate name>
- Inserts challege into the spreadsheet

/challenge help
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
helpTxt = settings.get_actions()['/challenge']['helpTxt']

# Sheet Names
sheetNames = ['Candidate Tracker']
candidateSheet = authorization.get_sheet_objects(sheetNames)

# Get Channel IDs
channelIDs = settings.get_channel_ids()

"""
Parse the text field of slack payload: '<officer first name> | <challenge description> | <candidate name>'
@params: text - slack payload of command
@return: officer_name, challenge_text, candidate_name, err - if err is None then valid parse
"""
def parse_challenge(text):
    # Parse out the groups
    match_text = re.match(r'(\w+)\s*\|\s*(.+)\s*\|\s*(.+)', text.strip())

    # Verify that the input can be correctly matched, and if not, return an error string
    if match_text == None:
         return None, None, None, 'Invalid command entry (e.g. `/challenge <officer first name> "<challenge description>" <candidate name>`)'

    # Separate and label corresponding information from input
    officer_name = match_text.group(1)
    challenge_text = match_text.group(2)
    candidate_name = match_text.group(3)
    
    # Return parsed values with 'None' error string
    return officer_name, challenge_text, candidate_name, None

"""
Execute the /newevent command
"""
def exec_assign_challenge(req):
    # Login into client
    authorization.login()

    # Get current Slack channel id
    channel_id = req['channel_id']
    
    # Verify that the command was run in #officers or #softdev-bot-testing
    if channel_id != channelIDs['officers'] and channel_id != channelIDs['softdev-bot-testing']:
        utils.error_res("Command must be submitted in #officers", helpTxt, req['response_url'])
        return
    
    # Parse expr for arguments
    officer_name, challenge_text, candidate_name, err_string = parse_challenge(req['text'])
    # Throw error if err_string is not 'None'
    if err_string:
        utils.error_res(err_string, helpTxt, req['response_url'])
        return

    # Find current column locations of candidate sheet
    col_dct = utils.get_candidate_sheet_col_numbers()

    # Locate matching candidate rows from candidate_name
    candidate_row_list = utils.get_candidate_row_number(candidate_name, candidateSheet, col_dct['name'])
    
    # If no candidate rows are returned, throw an error
    if len(candidate_row_list) <= 0:
        utils.error_res("Candidate could not be identified; please check your spelling and try again", helpTxt, req['response_url'])
        return

    # If too many candidate rows are returned, throw an error
    if len(candidate_row_list) > 3:
        utils.error_res("Too many candidate matches; please be more specific", helpTxt, req['response_url'])
        return

    # If two or three candidates rows, list them and throw an error
    if len(candidate_row_list) > 1 and len(candidate_row_list) <= 3:

        # Locate candidate name column index
        candidate_name_col = col_dct['name']
        
        err_string = "Too many candidate matches; current matches: "
        # Iterate through the candidates to get their names
        for row_index in candidate_row_list:            

            # Get candidate's name, and append to err_string
            curr_name = candidateSheet.cell(row_index, candidate_name_col).value
            err_string += curr_name + ", "
        
        utils.error_res(err_string[:len(err_string)-2], helpTxt, req['response_url'])
        return

    # Extract candidate row index from candidate_row_list
    candidate_row = candidate_row_list[0]

    # Locate challenge column index
    candidate_col = col_dct['challenge_desc']

    # Update challenge cell with new challenge  
    candidateSheet.update_cell(candidate_row, candidate_col, officer_name + ": " + challenge_text)

    # Formatting for successful update
    data = {
        'response_type': 'ephemeral',
        "blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Successfully assigned challenge to candidate {candidate_name}".format(candidate_name=candidate_name)
			}
            
		},
		{
			"type": "divider"
		}
        ]
    }
    requests.post(req['response_url'], json=data)