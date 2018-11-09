#!/usr/bin/python3

import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime


class Calendar:
    def __init__(self, database):
        """Class that concentrates all operations over the backend.

        Parameters
        ----------
        database : str
            A filename with the database connection string.

        Notes
        -----
        This specific version of the code uses SQLite as its backend. It also assumes that your
        SQLite version is new enough to have foreign key support (> 3.6, released in 2009).
        """
        # Open the SQLite database
        self.conn = sqlite3.connect('example.db')
        cursor = self.conn.cursor()
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        # If the database is empty, we create the required tables
        cursor.execute("CREATE TABLE IF NOT EXISTS person("
                       "username TEXT PRIMARY KEY NOT NULL, name TEXT)")

        cursor.execute("CREATE TABLE IF NOT EXISTS slots("
                       "username TEXT NOT NULL, date_from TEXT NOT NULL, date_to TEXT NOT NULL,"
                       "FOREIGN KEY(username) REFERENCES person(username))")

    def add_slots(self, user_id, slot_from, slot_to):
        """Adds a slot for the given user id.

        Parameters
        ----------
        user_id : str
            The ID of the user whose slot will be added.
        slot_from : datetime
            The earlier date at which the user is available.
            Minutes, seconds, and microseconds are discarded/set to 0.
        slot_to : datetime
            The earliest date at which the user is *not* available
            Minutes, seconds, and microseconds are discarded/set to 0.

        Returns
        -------
        A JSON object with two fields: `code` and `desc`.
        `code` is the error code, and `desc` is a human-readable explanation of the
        error code, if required.

        Notes
        -----
        This operation will add_slots slots in the range [slot_from, slot_to). That is: if the user
        is willing to start the meeting anytime from 16:00 to 20:00, then `slot_to` should
        have a value of 21:00.
        """
        retval = {'code': 0, 'desc': 'Operation successful'}
        if not(isinstance(user_id, str) and isinstance(slot_from, datetime) and isinstance(slot_to, datetime)):
            retval['code'] = 1
            retval['desc'] = 'Error in add_slots: parameters of wrong type'
        elif (slot_to - slot_from).total_seconds() <= 0:
            retval['code'] = 2
            retval['desc'] = 'Error in add_slots: empty range'

        return json.dumps(retval)

    def get_slots(self, user_id):
        """Returns the available slots for the given user id.

        Parameters
        ----------
        user_id : str
            The ID of the user whose slots will be queried.

        Returns
        -------
        A JSON objects with three fields: `code`, `data`, and `desc`.
        `code` is the error code for the operation, `data` is a set of available times,
        and `desc` is a human-readable explanation of the error code, if required.
        """
        retval = {'code': 0, 'data': [], 'desc': 'Operation successful'}
        return json.dumps(retval)

class TestCaseAdd(unittest.TestCase):
    """Tests adding items to the calendar."""
    def setUp(self):
        # Setting these tests up includes creating an empty database
        self.new_db = tempfile.NamedTemporaryFile(delete=False)
        self.testCal = Calendar(self.new_db.name)

    def tearDown(self):
        # Delete the temporary database
        os.unlink(self.new_db.name)

    def testAdd(self):
        # Test all kind of wrong arguments
        all_args = ['2018/12/12 06:20', 12, None, 12.21, datetime.now()]
        for user in all_args:
            for start in all_args:
                for end in all_args:
                    # There is exactly one case in which the input is valid,
                    # so we need to check for that first
                    if not (isinstance(user, str) and isinstance(start, datetime) and isinstance(end, datetime)):
                        retval = json.loads(self.testCal.add_slots(user, start, end))
                        self.assertNotEqual(retval['code'], 0, '\'add_slots\' is not validating arguments correctly')

        # Tests for an empty range
        start = datetime(2018, 12, 15, 13)
        end = datetime(2018, 12, 15, 14)
        retval = json.loads(self.testCal.add_slots('username', start, start))
        self.assertNotEqual(retval['code'], 0, '\'add_slots\' is allowing empty ranges')
        retval = json.loads(self.testCal.add_slots('username', end, start))
        self.assertNotEqual(retval['code'], 0, '\'add_slots\' is allowing empty ranges')

        # Tests a valid interval
        start = datetime(2018, 12, 15, 13)
        end = datetime(2018, 12, 15, 14)
        retval = json.loads(self.testCal.add_slots('username', start, end))
        self.assertEqual(retval['code'], 0, 'The \'add_slots\' operation should succeed')

        # Tests whether the 'add_slots' operation actually adds something
        retval = json.loads(self.testCal.get_slots('new_user'))
        slots_before = len(retval['data'])
        start = datetime(2018, 12, 15, 8)
        end = datetime(2018, 12, 15, 21)
        retval = json.loads(self.testCal.add_slots('new_user', start, end))
        self.assertEqual(retval['code'], 0, 'The \'add_slots\' operation should succeed')
        retval = json.loads(self.testCal.get_slots('new_user'))
        slots_after = len(retval['data'])
        self.assertNotEqual(slots_after - slots_before, 0, 'The \'add_slots\' operation is not adding correctly')


if __name__ == '__main__':
    # Run all test cases
    suite_loader = unittest.TestLoader()
    suite1 = suite_loader.loadTestsFromTestCase(TestCaseAdd)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suite)