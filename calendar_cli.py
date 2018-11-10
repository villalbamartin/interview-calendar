#!/usr/bin/python3

import argparse
import json
import sys
from backend import Calendar

# Parse arguments for the program
parser = argparse.ArgumentParser(description='Performs queries to the calendar API')

# These are the list of operations that the GUI supports
# We ask for exactly one of them
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--add_user', dest='add_user', metavar='STR', nargs=2,
                   help='Add a user to the database')
group.add_argument('--add_slot', dest='add_slot', metavar='STR', nargs=3,
                   help='Add a range of slots to the database')
group.add_argument('--see_slots', dest='see_slots', metavar='USER_ID',
                   help='See the available slots for the selected user')
group.add_argument('--meeting', dest='meeting_members', metavar='USER_ID', nargs='+',
                   help='Show possible meeting dates. The first argument is the interviewee.')

args = parser.parse_args()

# Time to check which operation is the GUI requesting
cal = Calendar('database.db')
if args.add_user:
    # Add a user to the database
    retval = json.loads(cal.add_user(args.add_user[0], args.add_user[1]))
    if retval['code'] != 0:
        sys.stderr.write("Error adding user: {}".format(retval['desc']))
elif args.add_slot:
    # Add a slot to the database
    # TODO: make it easier to enter a date
    retval = json.loads(cal.add_slots(args.add_slot[0], args.add_slot[1], args.add_slot[2]))
    if retval['code'] != 0:
        sys.stderr.write("Error adding user: {}".format(retval['desc']))
elif args.see_slots:
    # Query available slots for a specific user
    retval = json.loads(cal.get_slots (args.see_slots))
    if retval['code'] == 0:
        for slot in retval['data']:
            print(slot)
    else:
        sys.stderr.write("Error querying slots: {}".format(retval['desc']))
elif args.meeting_members:
    # Organize a meeting with a list of members
    retval = json.loads(cal.organize_meeting(args.meeting_members[0], args.meeting_members[1:]))
    if retval['code'] == 0:
        if len(retval['data']) == 0:
            print("No possible common schedule found")
        else:
            for slot in retval['data']:
                print(slot)
    else:
        sys.stderr.write("Error querying meeting user: {}".format(retval['desc']))
