"""
UPE Slack bot CRON Job
----------------------------------------------------------------------------
Queries the `Office Hours Feedback Form` for candidates
- increase the count of `Feedback Count` column in the One-on-Ones section of
Candidate Tracker

CRON Job Time: 10 minutes / run
"""
# Google Sheets Imports
import gspread

# Package Imports
import authorization
import utils

# Spreadsheet Names
sheetNames = ['One-On-Ones', 'Feedback Responses', 'OH Metadata']
onoSheet, feedback_sheet, oh_metadata_sheet = authorization.get_sheet_objects(sheetNames)

def update_candidate_onos(candidate_row, oh_holder, oh_type, col_dct):
    # Retrieve current number of uploaded feedback
    feedback_column = col_dct['oh_feedback_count']
    feedback_number = int(onoSheet.cell(candidate_row, feedback_column).value)

    # Find next cell to input contents
    next_column_number = 4 + feedback_number * 2 + 1

    # Check if trying to fill into other column information
    if onoSheet.cell(candidate_row, next_column_number).value != '':
        # Max filled to something
        return

    # Insert OH feed into cells
    onoSheet.update_cell(candidate_row, next_column_number, oh_type)
    onoSheet.update_cell(candidate_row, next_column_number + 1, oh_holder)

def exec_oh_checkoff():
    # Login into client
    authorization.login()

    # Find current column locations of candidate sheet
    col_dct = utils.get_candidate_sheet_col_numbers()

    # Find current number of OH processed
    processed_feedback_row = int(oh_metadata_sheet.cell(1, 2).value)

    # Retrieve necessary information from OH Feedback form
    email_lst = feedback_sheet.col_values(2)
    oh_holder_lst = feedback_sheet.col_values(3)
    oh_type_lst = feedback_sheet.col_values(4)

    # Update Candidate Tracker (One-on-One sheet) for every misssing entry
    while processed_feedback_row <= len(email_lst):
        email = email_lst[processed_feedback_row-1]
        oh_holder = oh_holder_lst[processed_feedback_row-1]
        oh_type = oh_type_lst[processed_feedback_row-1]

        # Find candidate row in Candidate Tracker
        candidate_row = utils.get_candidate_row_number_by_email(email, onoSheet, col_dct['email'])

        if candidate_row > 0:
            # Write Value to Candidate Sheet
            update_candidate_onos(candidate_row, oh_holder, oh_type, col_dct)

        # Increment for next row entry
        processed_feedback_row += 1

    # Write back metadata
    oh_metadata_sheet.update_cell(1, 2, str(processed_feedback_row))
