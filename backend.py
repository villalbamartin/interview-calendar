#!/usr/bin/python3

import argparse

# Parse arguments for the program
parser = argparse.ArgumentParser(description='Performs queries to the calendar API')

# These are the list of operations that the GUI supports
# We ask for exactly one of them
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--see_slots', dest='see_slots', metavar='USER_ID',
                   help='See the available slots for the selected user')
group.add_argument('--meeting', dest='meeting_members', metavar='USER_ID', nargs='+',
                   help='Show possible meeeting dates. The first argument is the interviewee.')

args = parser.parse_args()

# Time to check which operation is the GUI requesting
if args.see_slots:
    print("Show slots")
elif args.meeting_members:
    print("Organize a meeting with: {}".format(args.meeting_members))
