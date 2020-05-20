# Google Sheets Imports
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Flask Imports
import re
import requests
import os

# Error Imports
from utils import error_res

# Authorization
DIRNAME = os.path.dirname(__file__)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Candidate Tracker / Announcements
tracker_creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(DIRNAME, 'assets/creds/tracker_creds.json'), scope)
tracker_client = gspread.authorize(tracker_creds)

sheet = tracker_client.open('Candidate Tracking Sheet (Internal)')

# Sheet Names
candSheet = sheet.worksheet("Candidate Tracker")
socialSheet = sheet.worksheet('Socials')
profSheet = sheet.worksheet('Professional Events')
onoSheet = sheet.worksheet('One-On-Ones')

# Help Text
helpTxt = [{'text': "Type `/check <candidate name>` to view a candidate's status"}]

# Standand Google SpreadSheet Excel Column Locations
standardCol = {
    'email': 1,
    'name': 2,
    'track': 3,
    'committee': 4
}
# Candidate Tracker Sheet Column Values
candSheetCol = {
    'socials_complete': 8,
    'socials_reqs': 12,
    'prof_complete': 9,
    'prof_reqs': 13,
    'ono_complete': 10,
    'ono_reqs': 14,
    'gm1': 20,
    'gm2': 21,
    'gm3': 22,
    'paid': 23,
    'challenge': 25,
    'challenge_task': 26,
    'socials_ono_comp': 11, #DELETE THIS AFTER SP20 SEM
    'socials_ono_reqs': 15 #DELETE THIS AFTER SP20 SEM
}


"""
Find the Google Sheet row of each name matching with expr
"""
def matchAllCandidates(expr):
    expr = expr.lower()
    nameIndices = []
    nameLst = candSheet.col_values(standardCol['name'])[1:]

    for i in range(len(nameLst)):
        # expr matches candidate name
        if re.search(expr, nameLst[i].lower()):
            nameIndices.append(i+2)

    return nameIndices

"""
Search for candidate given regex expr
@param expr - regex expression from typed comment `/check <expr>`
@return dictionary each candidate's info matching <expr>
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
        sheetLabels = sheetName.row_values(2)
        candidate_row_loc = candRow + 1 # Prof / Social Sheet off by one bc of passwords listed
        if event == 'onos':
            jump = 2
            # Labels of current sheet
            sheetLabels = sheetName.row_values(1)
            candidate_row_loc = candRow
        
        # Candidate Info on current sheet
        candSheet = sheetName.row_values(candidate_row_loc)

        eventsVisited = []
        for eventIndex in range(4, len(sheetLabels)-2, jump):
            if candSheet[eventIndex] and jump == 2:
                eventsVisited.append("{type} : {name}".format(type=candSheet[eventIndex], name=candSheet[eventIndex+1]))
            elif candSheet[eventIndex] == '1' and candSheet[eventIndex] != "":
                eventsVisited.append(sheetLabels[eventIndex])

        return eventsVisited


    candidates = {}

    # Locate rows of candidates matching with name
    matchedLst = matchAllCandidates(expr)

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
        socialsTxt = '• Socials: {pss}/{req}\n'.format(pss=candInfo['socials_complete'], req=candInfo['socials_reqs'])
        for social in candInfo['socials']:
            socialsTxt += '\t - {social}\n'.format(social=social)

        # Professional
        profTxt = '• Professional: {pss}/{req}\n'.format(pss=candInfo['prof_complete'], req=candInfo['prof_reqs'])
        for prof in candInfo['prof']:
            profTxt += '\t - {prof}\n'.format(prof=prof)

        # One-on-Ones
        onoTxt = '• One-on-One: {pss}/{req}\n'.format(pss=candInfo['ono_complete'], req=candInfo['ono_reqs'])
        for ono in candInfo['onos']:
            onoTxt += '\t - {ono}\n'.format(ono=ono)

        # Challenge
        challengeTxt = '• Challenge: {done}\n'.format(done='Done' if candInfo['challenge']=='YES' else '*NO*')
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
        for ono in candInfo['onos']:
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
def track_candidates(req):
    # Login into client
    if tracker_creds.access_token_expired:
        tracker_client.login()
    
    response_url = req['response_url']

    # Check if argument len is sufficient
    if len(req['text']) < 3:
        error_res('Please submit an expression with more than two characters', helpTxt, req['response_url'])
        return

    # Retrieve candidate info according to text in Slack payload
    candidateInfos = getMatchedCandidates(req['text'])

    if len(candidateInfos) == 0:
        error_res('No candidates found with given keyword', helpTxt, req['response_url'])
        return

    # Format candidate info into Slack JSON format
    candidateFormatString = formatCandidateText(candidateInfos)

    data = {
        'response_type': 'ephemeral',
        'blocks' : candidateFormatString,
    }
    requests.post(response_url, json=data)