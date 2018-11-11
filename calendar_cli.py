#!/usr/bin/python3

import argparse
import dateutil.parser
import sys
from backend import Calendar

# Parse arguments for the program
long_date_desc = 'Dates are expected and provided in ISO 8601 format (YYYY-MM-DDTHH:MM:SS), ' \
                 'with \'T\' as the default separator character.'
parser = argparse.ArgumentParser(description='Performs queries to the calendar API',
                                 epilog=long_date_desc)

# These are the list of operations that the GUI supports
# We ask for exactly one of them
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--add_user', dest='add_user', metavar=('USER_ID','NAME'), nargs=2,
                   help='Add a user to the database')
group.add_argument('--get_user', dest='get_user', metavar='USER_ID',
                   help='Get the name of a user in the database')
group.add_argument('--add_slot', dest='add_slot', metavar=('USER_ID','FROM', 'TO'), nargs=3,
                   help='Add a range of slots to the database')
group.add_argument('--see_slots', dest='see_slots', metavar='USER_ID',
                   help='See the available slots for the selected user')
group.add_argument('--meeting', dest='meeting_members', metavar='USER_ID', nargs='+',
                   help='Show possible meeting dates. See below for the proper date format.')

args = parser.parse_args()

# Time to check which operation is the GUI requesting
cal = Calendar('database.db')
if args.add_user:
    # Add a user to the database
    retval = cal.add_user(args.add_user[0], args.add_user[1])
    if retval['code'] != 0:
        print("Error adding user: {}".format(retval['desc']), file=sys.stderr)
elif args.get_user:
    # Show the name of a user
    retval = cal.get_user(args.get_user)
    if retval['data'] != '':
        print(retval['data'])
    else:
        print("User not found", file=sys.stderr)
elif args.add_slot:
    # Add a slot to the database
    retval = cal.add_slots(args.add_slot[0],
                           dateutil.parser.parse(args.add_slot[1]),
                           dateutil.parser.parse(args.add_slot[2]))
    if retval['code'] != 0:
        print("Error adding slot: {}".format(retval['desc']), file=sys.stderr)
elif args.see_slots:
    # Query available slots for a specific user
    retval = cal.get_slots (args.see_slots)
    if retval['code'] == 0:
        for slot in retval['data']:
            print(slot)
    else:
        print("Error querying slots: {}".format(retval['desc']), file=sys.stderr)
elif args.meeting_members:
    # Organize a meeting with a list of members
    retval = cal.organize_meeting(args.meeting_members[0], args.meeting_members[1:])
    if retval['code'] == 0:
        if len(retval['data']) == 0:
            print("No possible common schedule found")
        else:
            for slot in retval['data']:
                print(slot)
    else:
        print("Error querying meeting user: {}".format(retval['desc']), file=sys.stderr)
