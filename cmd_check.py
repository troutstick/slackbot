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

def get_matched_candidates(expr):
    candidates = {}

    # Find current column locations of candidate sheet
    col_dct = utils.get_candidate_sheet_col_numbers()

    # Locate rows of candidates matching with name (1-indexed)
    matchedLst = utils.get_candidate_row_number(expr, candSheet, col_dct['name'])

    # Retrieve respective information for every candidate matching the expression
    for cand_row in matchedLst:
        # Grab Candidate Infomation in `Candidate Tracker` Sheet
        candidate_content = candSheet.row_values(cand_row)

        cand_dct = {}

        # Retrieve all necessary information from 'Candidate Tracker' sheet
        for key, col_number in col_dct.items():
            if col_number > len(candidate_content):
                cand_dct[key] = ""
            else:
                cand_dct[key] = candidate_content[col_number - 1]
        
        # Retrieve List of socials candidate attended
        cand_dct['socials'] = get_candidate_social_and_prof_list(socialSheet, cand_row)
        # Retrieve List of professional candidate attended
        cand_dct['professional'] = get_candidate_social_and_prof_list(profSheet, cand_row)
        # Retrieve List of One on Ones candidate attended
        cand_dct['one_on_ones'] = get_candidate_one_on_one_list(cand_row)

        # Get Candidate Office Hour minimum checkout count
        cand_dct['onos_checkoff'] = int(onoSheet.row_values(cand_row)[col_dct['oh_total_count']-1])

        # Add candidate object into dictionary
        candidates[cand_dct['name']] = cand_dct

    return candidates

def get_candidate_social_and_prof_list(sheet, cand_row):
    # Social / Prof have password rows thus offset by one
    cand_row += 1

    # Grab row information in sheet
    candidate_content = sheet.row_values(cand_row)

    # Remove last column as represents final total
    candidate_content.pop()

    # Grab event title name
    event_title = sheet.row_values(2)

    visited_lst = []
    for i in range(len(candidate_content)):
        if candidate_content[i] == '1':
            visited_lst.append(event_title[i])

    return visited_lst

def get_candidate_one_on_one_list(cand_row):
    # Offset by given columns
    offset = 4

    # Grab row information in sheet
    candidate_content = onoSheet.row_values(cand_row)[offset:]

    attended_lst = []
    for i in range(0, len(candidate_content), 2):
        if len(candidate_content[i]) > 1:
            attended_lst.append("{type} : {name}".format(type=candidate_content[i], name=candidate_content[i+1]))
        else:
            break
    return attended_lst

"""
Format each candidate in dictionary into Slack Markdown Format
@param dct - dictionary of matched candidate and their info
@return block - list of Slack text components
"""
def format_candidate_text(dct):
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
        profTxt = '• Professional: {pss}/{req}\n'.format(pss=candInfo['professional_completed'], req=candInfo['professional_requirement'])
        for prof in candInfo['professional']:
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
        challengeTxt = '• Challenge: {done}\n'.format(done='Done' if candInfo['challenge_completed']=='YES' else '*NO*')
        if candInfo['challenge_desc']:
            challengeTxt += '\t - {task}\n'.format(task=candInfo['challenge_desc'])

        # General Meeting
        gm1 = '• GM1 Requirements: {done}\n'.format(done='Yes' if candInfo['gm1_requirement']=='YES' else '*NO*')
        gm2 = '• GM2 Requirements: {done}\n'.format(done='Yes' if candInfo['gm2_requirement']=='YES' else '*NO*')
        gm3 = '• GM3 Requirements: {done}\n'.format(done='Yes' if candInfo['gm3_requirement']=='YES' else '*NO*')
        paid = '• Paid: {done}\n'.format(done='Yes' if candInfo['candidate_paid']=='TRUE' else '*NO*')

        # Intiation ready
        checkpoint = '• Checkpoint: {done}\n'.format(done='Yes' if candInfo['checkpoint_met']=='YES' else '*NO*')
        initiation = '• Initiate: {done}\n'.format(done='Yes' if candInfo['initiate_met']=='YES' else '*NO*')

        finished = ''
        if candInfo['initiate_met']=='YES':
            finished = ''

        # --------------- REPLACE AFTER SP20 SEM -----------------
        # requirements = {
        #     'type':'section',
        #     'text': {
        #         'type': 'mrkdwn',
        #         'text': nameTxt + socialsTxt + profTxt + onoTxt + challengeTxt
        #     }
        # }

        # --------------- DELETE AFTER SP20 SEM -----------------
        social_ono_completed = int(candInfo['socials_completed']) + int(candInfo['one_on_ones_completed'])
        social_ono_required = int(candInfo['socials_requirement']) + int(candInfo['one_on_ones_requirement'])
        socialOnoTxt = '• Socials / One-on-One: {pss}/{req}\n'.format(pss=social_ono_completed, req=social_ono_required)
        for social in candInfo['socials']:
            socialOnoTxt += '\t - {social}\n'.format(social=social)
        
        onos_checkoff = candInfo['onos_checkoff']
        count = 0
        for ono in candInfo['one_on_ones']:
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

        threshold = {
            'type':'section',
            'text': {
                'type': 'mrkdwn',
                'text': checkpoint + initiation + finished
            }
        }

        # Add comments together into array block (printed using Slack)
        block.append(requirements)
        block.append(attendance)
        block.append(threshold)

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
    candidate_info = get_matched_candidates(req['text'])

    if len(candidate_info) == 0:
        utils.error_res('No candidates found with given keyword', helpTxt, req['response_url'])
        return

    # Format candidate info into Slack JSON format
    candidate_format_string = format_candidate_text(candidate_info)

    data = {
        'response_type': 'ephemeral',
        'blocks' : candidate_format_string,
    }
    requests.post(req['response_url'], json=data)
