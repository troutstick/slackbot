# Google Sheets Imports
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Uitl Imports
import os
import settings

# Authorization
DIRNAME = os.path.dirname(__file__)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Candidate Tracker / Announcements
creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(DIRNAME, 'assets/creds/tracker_creds.json'), scope)
client = gspread.authorize(creds)

# Candidate Sheet
candidate_sheet = client.open('Candidate Tracking Sheet (Internal)')
# OH Feedback Form
oh_res_sheet = client.open('Office Hour Feedback Form (Responses)')

# Sheet Names
candSheet = candidate_sheet.worksheet("Candidate Tracker")
socialSheet = candidate_sheet.worksheet('Socials')
profSheet = candidate_sheet.worksheet('Professional Events')
onoSheet = candidate_sheet.worksheet('One-On-Ones')
feedback_sheet = oh_res_sheet.worksheet("Feedback Responses")

sheetNames = {
    "Candidate Tracker" : candSheet,
    'Socials' : socialSheet,
    'Professional Events' : profSheet,
    'One-On-Ones' : onoSheet,
    'Feedback Responses' : feedback_sheet
}

def authorize():
    return client

def login():
    # Login into client
    if creds.access_token_expired:
        client.login()

def getSheetObjects(spreadsheetsNames):
    lst = []
    for name in spreadsheetsNames:
        lst.append(sheetNames[name])
    return lst