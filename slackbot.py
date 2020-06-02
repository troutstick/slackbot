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
from cmd_check import exec_track_candidates
from cmd_event import exec_create_event
from cmd_challenge import exec_assign_challenge
from cmd_checkoff import exec_checkoff_candidate
from cmd_award import exec_award
from utils import *
from settings import *

API_ROUTE = '/api/slackbot'

'''
List of valid commands and their help text if errors
'''
actions = settings.get_actions()

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
def is_action_vaild(action):
    return action in actions

"""
Checks whether command is a request for helps
"""
def is_help_command(text):
    return text.strip().lower() == 'help'

# ---------- Commands ----------
"""
POST request from Slack channel
Command: `/check <candidate name>`
Actions: Retrieves data for a given candidate on Candidate Tracker spreadsheet
"""
@app.route(API_ROUTE + '/check', methods=['POST'])
def cmd_check():
    # Check if valid request through (team_id) and (token)
    if not is_request_valid(request):
        abort(400)

    # Retrieve payload from Slack
    req = request.form

    # Check if possible command
    if not is_action_vaild(req['command']):
        return error('Please submit a valid command', actions['/check']['helpTxt'])

    # Check if command indicated help
    if is_help_command(req['text']):
        print(actions[req['command']]['helpTxt'][0])
        return jsonify(
            response_type='ephemeral',
            text='Here is the format for `/check` command:',
            attachments=actions[req['command']]['helpTxt'],
        )

    # Create a thread to spawn find the correct values
    processThread = threading.Thread(
            target=exec_track_candidates,
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
Command: `/newevent /newevent <type> | <name> | <mm/dd> | <password>`
Condition: made only in #events channel
Action: Creates a new event and passsword on the Candidate Tracker Spreadsheet
"""
@app.route(API_ROUTE + '/event', methods=['POST'])
def cmd_event():
    # Check if valid request through (team_id) and (token)
    if not is_request_valid(request):
        abort(400)

    # Retrieve payload from Slack
    req = request.form

    # Check if possible command
    if not is_action_vaild(req['command']):
        return error('Please submit a valid command', actions['/newevent']['helpTxt'])

    # Check if command indicated help
    if is_help_command(req['text']):
        print(actions[req['command']]['helpTxt'][0])
        return jsonify(
            response_type='ephemeral',
            text='Here is the format for `/newevent` command:',
            attachments=actions[req['command']]['helpTxt'],
        )

    # Create a thread to spawn find the correct values to mitigate 3 seconds
    processThread = threading.Thread(
            target=exec_create_event,
            args=(req,)
        )
    processThread.start()

    # Send back a temporary loading response
    return jsonify(
        response_type='ephemeral',
        text='Creating new event...',
    )

"""
POST request from Slack channel
Command: `/checkoff <type> | <candidate name>`
Condition: made only in #officers and #officer-hour channel
Action: Checks off an event for a specific candidate on Candidate Tracker Spreadsheet
"""
@app.route(API_ROUTE + '/checkoff', methods=['POST'])
def cmd_checkoff():
    # Check if valid request through (team_id) and (token)
    if not is_request_valid(request):
        abort(400)

    # Retrieve payload from Slack
    req = request.form

    # Check if possible command
    if not is_action_vaild(req['command']):
        return error('Please submit a valid command', actions['/challenge']['helpTxt'])

    # Check if command indicated help
    if is_help_command(req['text']):
        print(actions[req['command']]['helpTxt'][0])
        return jsonify(
            response_type='ephemeral',
            text='Here is the format for `/checkoff` command:',
            attachments=actions[req['command']]['helpTxt'],
        )

    # Check if command indicated help
    if is_help_command(req['text']):
        print(actions[req['command']]['helpTxt'][0])
        return jsonify(
            response_type='ephemeral',
            text='Here is the format for `/checkoff` command:',
            attachments=actions[req['command']]['helpTxt'],
        )

    # Create a thread to spawn find the correct values to mitigate 3 seconds
    processThread = threading.Thread(
            target=exec_checkoff_candidate,
            args=(req,)
        )
    processThread.start()

    # Send back a temporary loading response
    return jsonify(
        response_type='ephemeral',
        text='Checking off candidate...',
    )


"""
POST request from Slack channel
Command: `/challenge <officer first name> | <challenge description> | <candidate name>`
Condition: made only in #officers channel
"""
@app.route(API_ROUTE + '/challenge', methods=['POST'])
def cmd_challenge():
    # Check if valid request through (team_id) and (token)
    if not is_request_valid(request):
        abort(400)

    # Retrieve payload from Slack
    req = request.form

    # Check if possible command
    if not is_action_vaild(req['command']):
        return error('Please submit a valid command', actions['/challenge']['helpTxt'])

    # Check if command indicated help
    if is_help_command(req['text']):
        return jsonify(
            response_type='ephemeral',
            text='Here is the format for `/challenge` command:',
            attachments=actions[req['command']]['helpTxt'],
        )

    # Create a thread to spawn find the correct values to mitigate 3 seconds
    processThread = threading.Thread(
            target=exec_assign_challenge,
            args=(req,)
        )
    processThread.start()

    # Send back a temporary loading response
    return jsonify(
        response_type='ephemeral',
        text='Creating new challenge...',
    )

"""
POST request from Slack channel
Command: `/award <person> | <points> | <feedback>`
"""
@app.route(API_ROUTE + '/award', methods=['POST'])
def cmd_award():
    # Check if valid request through (team_id) and (token)
    if not is_request_valid(request):
        abort(400)

    # Retrieve payload from Slack
    req = request.form

    # Check if possible command
    if not is_action_vaild(req['command']):
        return error('Please submit a valid command', actions['/award']['helpTxt'])

    # Create a thread to spawn find the correct values to mitigate 3 seconds
    processThread = threading.Thread(
            target=exec_award,
            args=(req,)
        )
    processThread.start()

    # Send back a temporary loading response
    return jsonify(
        response_type='ephemeral',
        text='Awarding a deserving :whale:...',
    )

"""
POST request from Slack channel
Command: `/syntax`
Action: Returns list of current commands and their syntax
"""
@app.route(API_ROUTE + '/syntax', methods=['POST'])
def cmd_commands():
    blocks = []
    intro = {
            'type':'section',
            'text': {
                'type': 'mrkdwn',
                'text': 'Here is the syntax for the list of available commands for UPE Dev Bot! Contact @Wally if there is any problems'
            }
        }
    for command in actions.keys():
        command_text = '{cmd}\n'.format(cmd=command)
        for cmdInfo in actions[command]['cmdInfo']:
            command_text += '• {cmdInfo}\n'.format(cmdInfo=cmdInfo)
        blocks.append({
            'type':'section',
            'text': {
                'type': 'mrkdwn',
                'text': command_text
            }
        })
        blocks.append({"type" : "divider"})

    # Senc back list of commands
    return jsonify(
        response_type='ephemeral',
        blocks= blocks
    )


"""
GET request for testing
"""
@app.route(API_ROUTE + '/test', methods=['GET'])
def cmd_test():
    return jsonify( text='What\'s HKN?')

if __name__ == '__main__':
    app.run()
