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
helpTxt = [{'text': 'Type `/challenge <officer first name> "<challenge description>" <candidate name>` to assign a challenge for a given candidate'}]

# Sheet Names
sheetNames = ['Candidate Tracker']
candidateSheet = authorization.getSheetObjects(sheetNames)

# Column Names
standardCol = settings.getFixedStandardColumns()
candSheetCol = settings.getCandidateTrackerColumns()

# Get Channel IDs
channelIDs = settings.getChannelIDs()

def parseChallenge(text):
    
    # Parse out the groups
    match_text = re.match(r'(\w+)\s+[\'"“”‘’](.+)[\'"“”‘’]\s+(.+)', text)
    
    # Verify that the input can be correctly matched, and if not, return an error string
    if match_text == None:
         return None, None, None, 'Invalid command entry (e.g. `/challenge <officer first name> "<challenge description>" <candidate name>`)'

    # Separate and label corresponding information from input
    officer_name = match_text.group(1)
    challenge_text = match_text.group(2)
    candidate_name = match_text.group(3)
    
    # Return parsed values with 'None' error string
    return officer_name, challenge_text, candidate_name, None

def assign_challenge(req):
    authorization.login()

    # Get current Slack channel id
    channel_id = req['channel_id']
    
    # Verify that the command was run in #officers or #softdev-bot-testing
    if channel_id != channelIDs['officers'] and channel_id['softdev-bot-testing'] != channelIDs:
        error_res("Command must be submitted in #officers", helpTxt, req['response_url'])
        return
    
    # Parse expr for arguments
    officer_name, challenge_text, candidate_name, err_string = parseChallenge(req['text'])

    # Throw error if err_string is not 'None'
    if err_string:
        error_res(err_string, helpTxt, req['response_url'])
        return

    # Locate matching candidate rows from candidate_name
    candidate_row_list = matchAllCandidates(candidate_name, candidateSheet)

    # If no candidate rows are returned, throw an error
    if len(candidate_row_list) <= 0:
        error_res("Candidate could not be identified; please check your spelling and try again", helpTxt, req['response_url'])
        return

    # If too many candidate rows are returned, throw an error
    if len(candidate_row_list) > 3:
        error_res("Too many candidate matches; please be more specific", helpTxt, req['response_url'])
        return

    # If two or three candidates rows, list them and throw an error
    if len(candidate_row_list) > 1 and len(candidate_row_list) <= 3:

        # Locate candidate name column index
        candidate_name_col = standardCol['name']
        
        err_string = "Too many candidate matches; current matches: "
        # Iterate through the candidates to get their names
        for row_index in candidate_row_list:            

            # Get candidate's name, and append to err_string
            curr_name = candidateSheet.cell(row_index, candidate_name_col).value
            err_string += curr_name + ", "
        
        error_res(err_string[:len(err_string)-2], helpTxt, req['response_url'])
        return

    # Extract candidate row index from candidate_row_list
    candidate_row = candidate_row_list[0]

    # Locate challenge column index
    candidate_col = candSheetCol['challenge_task']

    # Get candidate's current challenge, if already assigned
    prev_challenge = candidateSheet.cell(candidate_row, candidate_col).value

    # If candidate already has a challenge, throw error
    if prev_challenge:
        error_res("This candidate already has a challenge assigned!", helpTxt, req['response_url'])
        return

    # Update challenge cell with new challenge  
    candidateSheet.update_cell(candidate_row, candidate_col, officer_name + ": " + challenge_text)

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