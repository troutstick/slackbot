"""
UPE Slack Bot Endpoint Routes
----------------------------------------------------------------------------
REQUIREMENTS
Have there's as environment variables
   export SLACK_VERIFICATION_TOKEN= <app verification token>
   export SLACK_TEAM_ID= <slack channel team id>
   export FLASK_APP= slackbot.py (not needed when using gunicorn on OCF)

To find slack variables,
1) Slack TEAM_ID = located in browser URL in workspace in the form T-------
2) Slack Verification Token = check app for verification token
"""
# ---------- Set Up ----------
# Flask Imports
import os
import threading
from flask import abort, Flask, jsonify, request

app = Flask(__name__)

# Other files
from candidate_tracker import *
from event import *
from utils import *

'''
List of valid commands and their help text if errors
'''
actions = {
    '/check' : {
        'helpTxt' : [{'text': "Type `/check <candidate name>` to view a candidate's status"}],
    },
    '/newevent' : {
        'helpTxt' : [{'text': 'Type `/newevent <type> "<name>" <date> <password>` to create a new event'}]
    },
    '/checkoff' : {
        'helpTxt' : [{'text': 'Type `/checkoff <INSERT INFO HERE>` to checkoff a given candidate'}]
    },
}

# ---------- Authenticating ----------
"""
Checks whether payload matches correct verfication token and team ID
"""
def is_request_valid(request):
    is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
    is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']

    return is_token_valid and is_team_id_valid

"""
Checks whether provided action is a possible command
"""
def actionIsValid(action):
    return action in actions

# ---------- Commands ----------
"""
POST request from Slack channel
Command: `/check <candidate name>`
"""
@app.route('/check', methods=['POST'])
def check_candidates():
    # Check if valid request through (team_id) and (token)
    if not is_request_valid(request):
        abort(400)

    # Retrieve payload from Slack
    req = request.form

    # Check if possible command
    if not actionIsValid(req['command']):
        return error('Please submit a valid command', actions['/check']['helpTxt'])
    
    # Create a thread to spawn find the correct values
    processThread = threading.Thread(
            target=track_candidates,
            args=(req,)
        )
    processThread.start()

    # Send back a temporary loading response
    return jsonify(
        response_type='ephemeral',
        text='Loading your candidate data...',
    )

"""
POST request from Slack channel
Command: `/newevent <candidate name>`
Condition: made only in #events channel
"""
@app.route('/event', methods=['POST'])
def new_event():
    # Check if valid request through (team_id) and (token)
    if not is_request_valid(request):
        abort(400)

    # Retrieve payload from Slack
    req = request.form

    # Check if possible command
    if not actionIsValid(req['command']):
        return error('Please submit a valid command', actions['/newevent']['helpTxt'])
    
    # Create a thread to spawn find the correct values to mitigate 3 seconds
    processThread = threading.Thread(
            target=create_event,
            args=(req,)
        )
    processThread.start()

    # Send back a temporary loading response
    return jsonify(
        response_type='ephemeral',
        text='Creating new event...',
    )



# """
# POST request from Slack channel
# Command: `/checkoff <candidate name>`
# """
# @app.route('/checkoff', methods=['POST'])
# def checkoff_candidates():
#     # Check if valid request through (team_id) and (token)
#     if not is_request_valid(request):
#         abort(400)

#     # Retrieve payload from Slack
#     req = request.form

#     # Check if possible command
#     if not actionIsValid(req['command']):
#         return error('Please submit a valid command', actions['/checkoff']['helpTxt'])
#         

# """
# POST request from Slack channel
# Command: `/announcements <optional: type>`
# """
# @app.route('/announcements', methods=['POST'])
# def announcements():
#     # Check if valid request through (team_id) and (token)
#     if not is_request_valid(request):
#         abort(400)

#     # Retrieve payload from Slack
#     req = request.form

#     # Check if possible command
#     if not actionIsValid(req['command']):
#         return error('Please submit a valid command', actions['/announcements']['helpTxt'])

"""
GET request for testing
"""
@app.route('/test', methods=['GET'])
def test():
    return jsonify( text='What\'s HKN?')

if __name__ == '__main__':
    app.run()