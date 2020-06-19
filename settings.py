"""
UPE Slack Settings
----------------------------------------------------------------------------
- Key values to maintain throughout semesters
"""

'''
List of valid commands and their help text if errors
'''
def get_actions():
    return {
        '/check' : {
            'helpTxt' : [{'text': "Type `/check <candidate name>` to view a candidate's status"}],
            'cmdInfo' : ['`/check <candidate name>`'],
            'cmdTxt' : 'Lookup a candidate\'s current candidacy requirements given a regex expression on names\n'
        },
        '/newevent' : {
            'helpTxt' : [{'text': 'Type `/newevent <type> | <name> | <mm>/<dd> | <password>` to create a new event \n(e.g. `/check whale`)'}],
            'cmdInfo' : [
                '`/newevent <type> | <name> | <mm/dd> | <password>` ',
                '`/newevent list-all` - list all current created events',
                '`/newevent help` - Brings up the help text info'
                ],
            'cmdTxt' : 'Create a new event name and password on internal sheet (type: s - social, p - professional)\n(e.g. `/newevent social | Beat HKN | 4/20 | better_frat`)\n'
        },
        '/checkoff' : {
            'helpTxt' : [{'text': 'Type `/checkoff <type> | <candidate name>` to checkoff a given candidate \n(e.g. `/checkoff oh | UPE`)'}],
            'cmdInfo' : [
                '`/checkoff <type> | <candidate name>`',
                '`/checkoff help` - Brings up the help text info'
                ],
            'cmdTxt' : 'Checkoff given candidate for their requirement (type: oh - office hour, c - challenge)\n(e.g. `/checkoff oh | Whale`)\n'
        },
        '/challenge' : {
            'helpTxt' : [{'text': 'Type `/challenge <officer first name> | <challenge desc> | <candidate name>` to assign a challenge for a candidate \n(e.g. `/challenge whale | Troll HKN | UPE`)'}],
            'cmdInfo' : [
                '`/challenge <officer first name> | <challenge desc> | <candidate name>`',
                '`/challenge help` - Brings up the help text info'
                ],
            'cmdTxt' : 'Assign a challenge to the a candidate\n(e.g. `/challenge whale | Troll HKN | UPE`)\n'
        },
        '/award' : {
            'helpTxt' : [{'text': ''}],
            'cmdInfo' : [
                '`/award <person> | <points> | <feedback>`',
                '`/award hi bot` - Introductory message',
                '`/award why is bot` - Describes purpose of award bot',
                '`/award showAll` - lists all the committee members'
            ],
            'cmdTxt' : 'Rewards points to committee members\n'
        },
        '/syntax' : {
            'helpTxt' : [],
            'cmdInfo' : [
                '`/syntax`'
            ],
            'cmdTxt' : 'Displays all possilbe commands\n'
        }
    }

"""
Column numbers of the first 4 columns values on every Candidate Tracking sheet
"""
def get_fixed_column_values():
    return {
        'email': 1,
        'name': 2,
        'track': 3,
        'committee': 4
    }

"""
Column numbers of the Candidate Tracking > Candidate Tracking sheet
"""
def get_candidate_columns():
    return {
        'socials_complete': 8,
        'socials_reqs': 12,
        'prof_complete': 9,
        'prof_reqs': 13,
        'ono_complete': 10,
        'ono_reqs': 14,
        'gm1': 20,
        'gm2': 21,
        'gm3': 22,
        'paid': 23,
        'challenge_finished': 25,
        'challenge_task': 26,
        'socials_ono_comp': 11, #DELETE THIS AFTER SP20 SEM
        'socials_ono_reqs': 15 #DELETE THIS AFTER SP20 SEM
    }

"""
Column number of the Candidate Tracking > One-on-Ones Sheet
"""
def get_one_on_one_columns():
    return {
        'Checked Off' : 17,
        'Feedback' : 18,
        'Total One-on-Ones' : 19
    }

"""
OH Feedback Spreadsheet columns
"""
def get_OH_feedback_columns():
    return {
        'email' : 2,
        'oh_holder' : 3,
        'oh_type' : 4
    }

"""
Channel IDs for slack channel validations
"""
def get_channel_ids():
    return {
        'officers' : 'G01347N2S4S',
        'softdev-bot-testing' : 'G013VTM2XBQ',
        'oh-holders' : "G015NTXBFNU"
    }