"""
UPE Slack Bot Slack Commands
----------------------------------------------------------------------------
/award 
- awards person
"""

# API imports
import requests

def exec_award(req):
    # Sent a POST request to Google Apps Script Server handling award
    res = requests.post('https://script.google.com/macros/s/AKfycby8RYu-1BNRDsdFw01ulcBWtwqHKZ1WxoTxd8FqkXbZULSKeI_U/exec', data=req)

    data = {
        'response_type': 'ephemeral',
        'text' : res.text
    }
    # Post request back to command
    requests.post(req['response_url'], json=data)
