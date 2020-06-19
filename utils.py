from flask import jsonify
import requests
import settings
import re

# Fixed columns on each spreadsheet
standardCol = settings.get_fixed_column_values()

"""
Find the Google Sheet row (exact) of each name matching with expr [no off-by-one error]
Use only in Candidate Tracker Sheet (candSheet variable for reference)
"""
def get_candidate_row_number(expr, sheetName):
    expr = expr.lower()
    nameIndices = []
    nameLst = sheetName.col_values(standardCol['name'])[1:]

    for i in range(len(nameLst)):
        # expr matches candidate name
        if re.search(expr, nameLst[i].lower()):
            nameIndices.append(i+2)

    return nameIndices

"""
Find the Google Sheet row (exact) of each name matching with email
Use only in Candidate Tracker Sheet (candSheet variable for reference)
"""
def get_candidate_row_number_by_email(target_email, sheetName):
    emailLst = sheetName.col_values(standardCol['email'])[1:]
    print("Target email: ", target_email)
    for i in range(len(emailLst)):
        # email matches Candidate Tracker record
        if target_email == emailLst[i]:
            return i+2
    return -1

"""
Return the keywords given event type
@params keywords - list of requested event types (e.g. social, prof, oh)
@return lst - list of list of allowed keywords
"""
def get_keywords(keywords):
    office = ['o', '1', 'oh', 'office', 'hours']
    socials = ['s', 'soc', 'social', 'socials']
    profs = ['p', 'prof', 'professional']
    chall = ['c', 'chall', 'challenge']

    keywordNames = {
        'social' : socials,
        'prof' : profs,
        'oh' : office,
        'chall' : chall
    }

    if len(keywords) == 1:
        return keywordNames[keywords[0]]

    lst = []
    for name in keywords:
        lst.append(keywordNames[name])
    return lst

"""
POST Error message to Slack
"""
def error(msg, attachments):
    return jsonify(
        response_type='ephemeral',
        text=msg,
        attachments=attachments,
    )

"""
POST Error message to Slack using response url
"""
def error_res(msg, attachments, response_url):
    data = {
        "response_type": "ephemeral",
        "text": msg,
        "attachments": attachments
    }
    requests.post(response_url, json=data)