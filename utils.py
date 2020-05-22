from flask import jsonify
import requests
import settings
import re

standardCol = settings.getFixedStandardColumns()

"""
Find the Google Sheet row (exact) of each name matching with expr [no off-by-one error]
Use only in Candidate Tracker Sheet (candSheet variable for reference)
"""
def matchAllCandidates(expr, sheetName):
    expr = expr.lower()
    nameIndices = []
    nameLst = sheetName.col_values(standardCol['name'])[1:]

    for i in range(len(nameLst)):
        # expr matches candidate name
        if re.search(expr, nameLst[i].lower()):
            nameIndices.append(i+2)

    return nameIndices

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
POST Error message to Slack
"""
def error_res(msg, attachments, response_url):
    data = {
        "response_type": "ephemeral",
        "text": msg,
        "attachments": attachments
    }
    requests.post(response_url, json=data)