# UPE Slack Bot

## Table Of Contents
  - [About](#about)
  - [Commands](#commands)
  - [Changing Semesters](#changing-semesters)
    - [Candidacy Spreadsheet Requirements](#candidacy-spreadsheet-requirements)
    - [Integrating Slack Bot](#integrating-slack-bot)

## Background

## Commands
The current live commands are as follows
- `/check <candidate name>` - looks up candidates inside the candidacy spreadsheet and returns the set of requirements left prior to initiation
- `/checkoff <type> | <candidate name>` - marks specified task for the given candidate as complete in the spreadsheet
- `/newevent <type> | <name> | <mm/dd> | <password>` - creates a new event (name and password) on candidate tracking sheet (only allowed in #events)
- `/challenge <officer first name> | <challenge desc> | <candidate name>` - assigned a new challenge to a given candidate by filling out on candidate tracking sheet
- `/award <person> | <points> | <feedback>` - award committee points based on achievements
- `/syntax` - lists all possible commands currently live on slack bot

All commands (besides `/syntax`) contains a help command (e.g. `/check help`) to pull up the help text

The endpoint for the commands rest here `https://upe.apphost.ocf.berkeley.edu/api/slackbot/<command name>`

## Getting Started

### Prerequisities
Run this command to `pip` install the necessary packages
```
pip install -r requirements.txt
```
### Directory
```
upe_slack_bot
│   README.md
│   requirements.txt
│   slackbot.py
│   authorization.py
│   settings.py
│   utils.py
│   cmd_award.py
│   cmd_challenge.py
│   cmd_check.py
│   cmd_checkoff.py
│   cmd_event.py
│   
└───assets
│   │
│   └───creds
│   │   │   tracker_creds.json
│   │
│   └───img

```
A brief summary of the purpose of each python file:
- `slackbot.py` - main Flask app conducting the HTTP Post requests
- `authorization.py` - initializes all the spreadsheets objects and authenticates with Googlesheets API using `/assets/tracker_creds.json`
- `settings.py` - fixed hardcoded values within the spreadsheets entered as dictionary items
- `utils.py` - helpful functions uses in processing slack slash commands (error response, retrieve keywords)
- `cmd_amard.py` - conduct the `/award` command
- `cmd_challenge.py` - process the `/challenge` command
- `cmd_check.py` - process the `/check` command
- `cmd_checkoff.py` - processs the `/checkoff` command
- `cmd_event.py` - process the `/newevent` command

### Documentation
Listed here is the documentation necessary to maintain the Slack bot (slash commands) and Google Sheets API
- [gspread](https://gspread.readthedocs.io/en/latest/)
- [slash commands](https://api.slack.com/interactivity/slash-commands)
- [slack message formatting](https://api.slack.com/reference/surfaces/formatting)

## Adding a command

## Deployment

### Beta testing (locally)

Whenever a slack command is changed, it is highly recommended to test it locally prior to submitting to our OCF servers because debugging on OCF is a pain (see below for commands to debug). Therefore, run an end point on a local server using [ngrok](https://ngrok.com) is extremely useful.
```
ngrok http 5000
```

Afterwards make sure you change the endpoint on each slash command you wanted to test on the slackbot build page

![slackbot installation](assets/img/slack_slash.png)

### OCF Deployment
When deploying on OCF server, pull from the github repository (https://github.com/upenu/slackbot) when SSH into the OCF servers.

Make sure these are valid and up to date
1. SSH into the UPE directory
2. **Edit the `run*` file with the new semester contents**
Fill in the values with the Slack IDs specified above
```
export SLACK_VERIFICATION_TOKEN=your-verification-token
export SLACK_TEAM_ID=your-team-id
```
2. Make sure `assets/creds/tracker_creds.json` is present and up to date
3. run the command `systemctl --user restart <insert app name here>` to restart the OCF Server
   
Afterwards run, this command to restart the slack bot app
```
systemctl --user restart slackbot
```

### OCF Server Maintenance
There are a couple useful commands when debugging inside ssh server.
- *Restart an app* - `systemctl --user restart slackbot`
- *Bring an app offline* - `systemctl --user stop slackbot`
- *Bring an app back online* - `systemctl --user start slackbot`
- *Check status of an app* - `systemctl --user status slackbot`
- *Check debug log for app* - `journalctl --user -n <insert number of lines>`

Please visit OCF's website and follow their directions on how to properly deploy web apps on their server
- [OCF Home](https://www.ocf.berkeley.edu)
- [App Hosting](https://www.ocf.berkeley.edu/docs/services/webapps/)
- [Python WebApps](https://www.ocf.berkeley.edu/docs/services/webapps/python/)



























## Deployment
Currently, our bot is hosted on Berkeley's Open Computing Facility Servers  


## History
(Last Updated: 05-14-2020)  
This project was the birth of the software developer (softdev) committee. During the Spring 2020 semester, the issue of having candidates to constantly find the location of the candidacy spreadsheet over and over was brought up by Celina, a former treasurer. Initially, the Slack bot was meant for candidates to have a simpler method of accessing their requirements, but the usefulness of such bot became apparently for other commands.

## Author
- Wallace Lim (Sp20 Software Dev)
- Leon Ming (Sp20 President)