"""
UPE Slack Bot Slack Commands
----------------------------------------------------------------------------
/check <candidate name>
- Retrieves candidate values from spreadsheet
"""
# Google Sheets Imports
import gspread

# Flask Imports
import re
import requests

# Package Importss
import authorization
import settings
import utils

# Spreadsheet Objects
sheetNames = ['Candidate Tracker', 'Socials', 'Professional Events', 'One-On-Ones']
candSheet, socialSheet, profSheet, onoSheet = authorization.get_sheet_objects(sheetNames)

# Help Text
helpTxt = settings.get_actions()['/check']['helpTxt']

# Standand Google SpreadSheet Excel Column Locations
standardCol = settings.get_fixed_column_values()
# Candidate Tracker Sheet Column Values
candSheetCol = settings.get_candidate_columns()

"""
Search for candidate given regex expr
@param expr - regex expression from typed comment `/check <expr>`
@return dictionary each candidates' info matching <expr>
Example dct[<candidate name>]
{
    'socials_complete': '1',
    'socials_reqs': '2',
    'prof_complete': '2',
    'prof_reqs': '2',
    'ono_complete': '2',
    'ono_reqs': '2',
    'socials': ['Big/Little Mixer 2/15'],
    'prof': ['Jane Street (2/26)']
    'gm1': YES,
    'gm2': YES,
    'gm3': NO,
    'paid': TRUE,
    'challenge': YES,
    'socialAndOno':
}
"""
def getMatchedCandidates(expr):
    def getCandidateEvents(sheetName, event):
        # Configure whether event is One-on-Ones or not
        jump = 1
        sheet_labels = sheetName.row_values(2)
        candidate_row_loc = candRow + 1 # Prof / Social Sheet off by one bc of passwords listed

        # Remove excess columns
        cleaned_sheet_titles = sheet_labels[4:len(sheet_labels)-1]
        
        if event == 'onos':
            jump = 2
            # Labels of current sheet
            sheet_labels = sheetName.row_values(1)
            cleaned_sheet_titles = sheet_labels[4:len(sheet_labels)-3]
            candidate_row_loc = candRow

        # Candidate Info on current sheet
        candSheet = sheetName.row_values(candidate_row_loc)

        # Add visited events into list
        eventsVisited = []
        for eventIndex in range(4, len(cleaned_sheet_titles)+4, jump):
            # Different scenarios for 1-1s and other event types
            if event == 'onos' and candSheet[eventIndex] != '':
                eventsVisited.append("{type} : {name}".format(type=candSheet[eventIndex], name=candSheet[eventIndex+1]))
            elif event != 'onos' and candSheet[eventIndex] == '1':
                eventsVisited.append(sheet_labels[eventIndex])

        return eventsVisited

    candidates = {}

    # Locate rows of candidates matching with name
    matchedLst = utils.get_candidate_row_number(expr, candSheet)

    # Retrieve respective information for every candidate
    for candRow in matchedLst:
        # Grab Candidate Infomation in `Candidate Tracker` Sheet
        candidate = candSheet.row_values(candRow)

        candInfo = {}

        # Insert `Candidate Tracker` contents into dictionary
        for col, colNum in candSheetCol.items():
            if colNum - 1 >= len(candidate):
                candInfo[col] = ""
            else:
                candInfo[col] = candidate[colNum-1]

        # Insert `Socials` contents into dictionary
        candInfo['socials'] = getCandidateEvents(socialSheet, 'socials')
        # Insert `Professional Events` contents into dictionary
        candInfo['prof'] = getCandidateEvents(profSheet, 'prof')
        # Insert `One-on-Ones` contents into dictionary
        candInfo['onos'] = getCandidateEvents(onoSheet, 'onos')

        # Get Candidate Office Hour minimum checkout count
        candInfo['onos_checkoff'] = int(onoSheet.row_values(candRow)[settings.get_one_on_one_columns()['Total One-on-Ones']-1])

        # Add candidate object into dictionary
        candidates[candidate[standardCol['name'] - 1]] = candInfo

    return candidates

"""
Format each candidate in dictionary into Slack Markdown Format
@param dct - dictionary of matched candidate and their info
@return block - list of Slack text components
"""
def formatCandidateText(dct):
    block = []
    # Format each candidate into markdown format
    for name in dct.keys():
        # Grab candidate contents
        candInfo  = dct[name]

        nameTxt = '*{name}*\n'.format(name=name)

        # Socials
        # socialsTxt = '• Socials: {pss}/{req}\n'.format(pss=candInfo['socials_complete'], req=candInfo['socials_reqs'])
        # for social in candInfo['socials']:
        #     socialsTxt += '\t - {social}\n'.format(social=social)

        # Professional
        profTxt = '• Professional: {pss}/{req}\n'.format(pss=candInfo['prof_complete'], req=candInfo['prof_reqs'])
        for prof in candInfo['prof']:
            profTxt += '\t - {prof}\n'.format(prof=prof)

        # One-on-Ones
        # onos_checkoff = candInfo['onos_checkoff']
        # count = 0
        # onoTxt = '• One-on-One: {pss}/{req}\n'.format(pss=candInfo['ono_complete'], req=candInfo['ono_reqs'])
        # for ono in candInfo['onos']:
        #     if count < onos_checkoff:
        #         onoTxt += '\t - {ono} (checked off)\n'.format(ono=ono)
        #         count += 1
        #     else:
        #         onoTxt += '\t - {ono}\n'.format(ono=ono)

        # Challenge
        challengeTxt = '• Challenge: {done}\n'.format(done='Done' if candInfo['challenge_finished']=='YES' else '*NO*')
        if candInfo['challenge_task']:
            challengeTxt += '\t - {task}\n'.format(task=candInfo['challenge_task'])

        # General Meeting
        gm1 = '• GM1 Requirements: {done}\n'.format(done='Yes' if candInfo['gm1']=='YES' else '*NO*')
        gm2 = '• GM2 Requirements: {done}\n'.format(done='Yes' if candInfo['gm2']=='YES' else '*NO*')
        gm3 = '• GM3 Requirements: {done}\n'.format(done='Yes' if candInfo['gm3']=='YES' else '*NO*')
        paid = '• Paid: {done}\n'.format(done='Yes' if candInfo['paid']=='TRUE' else '*NO*')

        # --------------- REPLACE AFTER SP20 SEM -----------------
        # requirements = {
        #     'type':'section',
        #     'text': {
        #         'type': 'mrkdwn',
        #         'text': nameTxt + socialsTxt + profTxt + onoTxt + challengeTxt
        #     }
        # }

        # --------------- DELETE AFTER SP20 SEM -----------------
        socialOnoTxt = '• Socials / One-on-One: {pss}/{req}\n'.format(pss=candInfo['socials_ono_comp'], req=candInfo['socials_ono_reqs'])
        for social in candInfo['socials']:
            socialOnoTxt += '\t - {social}\n'.format(social=social)
        
        onos_checkoff = candInfo['onos_checkoff']
        count = 0
        for ono in candInfo['onos']:
            if count < onos_checkoff:
                socialOnoTxt += '\t - {ono} :white_check_mark:\n'.format(ono=ono)
                count += 1
            else:
                socialOnoTxt += '\t - {ono}\n'.format(ono=ono)

        requirements = {
            'type':'section',
            'text': {
                'type': 'mrkdwn',
                'text': nameTxt + socialOnoTxt + profTxt + challengeTxt
            }
        }
        # --------------- END DELETE AFTER SP20 SEM -----------------

        attendance = {
            'type':'section',
            'text': {
                'type': 'mrkdwn',
                'text': gm1 + gm2 + gm3 + paid
            }
        }

        # Add comments together into array block (printed using Slack)
        block.append(requirements)
        block.append(attendance)

        # Push divider
        block.append({"type" : "divider"})

    return block

"""
Runs bread and butter of code and POST back to slack
"""
def exec_track_candidates(req):
    # Login into client
    authorization.login()

    # Check if argument len is sufficient
    if len(req['text']) < 3:
        utils.error_res('Please submit an expression with more than two characters', helpTxt, req['response_url'])
        return

    # Retrieve candidate info according to text in Slack payload
    candidateInfos = getMatchedCandidates(req['text'])

    if len(candidateInfos) == 0:
        utils.error_res('No candidates found with given keyword', helpTxt, req['response_url'])
        return

    # Format candidate info into Slack JSON format
    candidateFormatString = formatCandidateText(candidateInfos)

    data = {
        'response_type': 'ephemeral',
        'blocks' : candidateFormatString,
    }
    requests.post(req['response_url'], json=data)
