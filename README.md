# UPE Slack Bot

## Table Of Contents
  - [About](#about)
  - [Commands](#commands)
  - [Changing Semesters](#changing-semesters)
    - [Candidacy Spreadsheet Requirements](#candidacy-spreadsheet-requirements)
    - [Integrating Slack Bot](#integrating-slack-bot)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Deployment](#deployment)
    - [OCF WebApp Deploy](#ocf-webapp-deploy)
    - [OCF Server Maintenance](#ocf-server-maintenance)
  - [History](#history)
  - [Author](#author)

## About

## Commands
The current live commands are as follows
- `\check <candidate name>` - looks up candidates inside the candidacy spreadsheet and returns the set of requirements left prior to initiation
- `\checkoff <INSERT VALUES HERE>` - marks specified task for the given candidate as complete in the spreadsheet, given correct access controls
- `\newevent <type> "<name>" <date> <pwd>` - creates a new event (name and password) on candidate tracking sheet (only allowed in #events)
- `\challenge <INSERT VALUES HERE>` - assigned a new challenge to a given candidate by filling out on candidate tracking sheet
- `\award <INSERT VALUES HERE>` -- award committee points based on achievements

## Getting Started
NOTE: This shouldn't be necessary as the bot is already up and running. Please refer to [Changing Semesters](#changing-semesters) for mitrating the slackbot to the following semester. This section is only used for reference when adding additional implementations towards the slackbot.

### Prerequisites
Install these packages if not already done so on the SSH UPE server.

```
pip install gspread
pip install oauth2client
pip install flask
pip install gunicorn
```

### Documentation
Listed here is the documentation necessary to maintain the Slack bot (slash commands) and Google Sheets API
- [gspread](https://gspread.readthedocs.io/en/latest/)
- [slash commands](https://api.slack.com/interactivity/slash-commands)
- [slack message formatting](https://api.slack.com/reference/surfaces/formatting)

## Deployment
Currently, our bot is hosted on Berkeley's Open Computing Facility Servers  

### OCF WebApp Deploy
1. SSH into the UPE directory
2. **Edit the `run*` file with the new semester contents**
Fill in the values with the Slack IDs specified above
```
export SLACK_VERIFICATION_TOKEN=your-verification-token
export SLACK_TEAM_ID=your-team-id
```
3. run the command `systemctl --user restart <insert app name here>` to restart the OCF Serverr

Please visit OCF's website and follow their directions on how to properly deploy web apps on their server
- [OCF Home](https://www.ocf.berkeley.edu)
- [App Hosting](https://www.ocf.berkeley.edu/docs/services/webapps/)
- [Python WebApps](https://www.ocf.berkeley.edu/docs/services/webapps/python/)

### OCF Server Maintenance
There are a couple useful commands when debugging. For every `<insert app name here>`, please insert `slackbot`
- *Restart an app* - `systemctl --user restart <insert app name here>`
- *Bring an app offline* - `systemctl --user stop <insert app name here>`
- *Bring an app back online* - `systemctl --user start <insert app name here>`
- *Check status of an app* - `systemctl --user status <insert app name here>`
- *Check debug log for app* - `journalctl --user -n <insert number of lines>`

## History
(Last Updated: 05-14-2020)  
This project was the birth of the software developer (softdev) committee. During the Spring 2020 semester, the issue of having candidates to constantly find the location of the candidacy spreadsheet over and over was brought up by Celina, a former treasurer. Initially, the Slack bot was meant for candidates to have a simpler method of accessing their requirements, but the usefulness of such bot became apparently for other commands.

## Author
- Wallace Lim (Sp20 Software Dev)
- Leon Ming (Sp20 President)