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
            'helpTxt' : [{'text': 'Type `/newevent <type> | <name> | <mm>/<dd> | <password>` to create a new event \n(e.g. `/newevent social | Beat HKN | 4/20 | better_frat`)'}],
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
                '`/checkoff <type> | <candidate name>` - for professional services and challenges',
                '`/checkoff <type> | <candidate name> | <officer first name>` - for officer chats',
                '`/checkoff help` - Brings up the help text info'
                ],
            'cmdTxt' : 'Checkoff given candidate for their requirement (type: oh - professional services, c - challenge, oc - officer chats)\n(e.g. `/checkoff oh | Whale`)\n'
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
        'oh-holders' : "G019E3F8U9M"
    }