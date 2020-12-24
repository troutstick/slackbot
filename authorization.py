# Google Sheets Imports
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Uitl Imports
import os

# Authorization
DIRNAME = os.path.dirname(__file__)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Candidate Tracker API Authentication
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
onoSheet = candidate_sheet.worksheet('Professional Services')
officerSheet = candidate_sheet.worksheet('Officer Chats')
softdev_metadata_sheet = candidate_sheet.worksheet("Softdev Metadata")

feedback_sheet = oh_res_sheet.worksheet("Feedback Responses")
oh_metadata_sheet = oh_res_sheet.worksheet("Metadata")


sheetNames = {
    "Candidate Tracker" : candSheet,
    'Socials' : socialSheet,
    'Professional Events' : profSheet,
    'One-On-Ones' : onoSheet,
    'Officer Chats' : officerSheet,
    'Feedback Responses' : feedback_sheet,
    'OH Metadata' : oh_metadata_sheet,
    'SoftDev Metadata' : softdev_metadata_sheet
}

def authorize():
    return client

def login():
    # Login into client
    if creds.access_token_expired:
        client.login()

"""
Return the spreadsheet Objects according to those requested
@params spreadsheetsNames - list of requested sheet names
@return lst - list of list of allowed keywords
"""
def get_sheet_objects(spreadsheetsNames):
    if len(spreadsheetsNames) == 1:
        return sheetNames[spreadsheetsNames[0]]

    lst = []
    for name in spreadsheetsNames:
        lst.append(sheetNames[name])
    return lst

"""
Check whether request contains correct access permissions
@params - 
@return - true if valid, false otherwise
"""
def check_permission(channel_type, channel_id):
    # Bypass permissions if #softdev-slackbot channel
    if channel_id == os.environ['SLACK_DEVELOP']:
        return True

    # Check access controls based on request
    if channel_type == 'professional-mentors':
        return channel_id == os.environ['SLACK_MENTORS']
    elif channel_type == 'officer'
        return channel_id == os.environ['SLACK_OFFICER']
    elif channel_type == 'event'
        return channel_id == os.environ['SLACK_EVENTS']
    
    return False