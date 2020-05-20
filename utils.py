from flask import jsonify
import requests

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