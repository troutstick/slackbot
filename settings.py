def getFixedStandardColumns():
    return {
        'email': 1,
        'name': 2,
        'track': 3,
        'committee': 4
        }

def getCandidateTrackerColumns():
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

def getOfficeHourFeedbackColumns():
    return {
        'email' : 2,
        'oh_holder' : 3,
        'oh_type' : 4
    }

def getChannelIDs():
    return {
        'officers' : 'G01347N2S4S',
        'softdev-bot-testing' : 'G013VTM2XBQ',
        'office-hours' : "INSERT VALUES IN HERE"
    }