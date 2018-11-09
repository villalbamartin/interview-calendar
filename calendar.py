#!/usr/bin/python3

import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime


class Calendar:
    """Class that concentrates all operations over the backend.

    Notes
    -----
    This specific version of the code uses SQLite as its backend. It also assumes that your
    SQLite version is new enough to have foreign key support (> 3.6, released in 2009).

    Dates are stored as text due to SQLite not having a 'date' type. The format for those strings
    is the ISO 8601 format (YYYY-MM-DDTHH:MM:SS[.mmmmmm][+HH:MM]).
    """
    # Templates for all SQL queries
    INIT_DB_SQL1 = "CREATE TABLE IF NOT EXISTS people(" \
                   "username TEXT PRIMARY KEY NOT NULL, name TEXT);"
    INIT_DB_SQL2 = "CREATE TABLE IF NOT EXISTS slots(" \
                   "username TEXT NOT NULL, date_from TEXT NOT NULL, date_to TEXT NOT NULL," \
                   "FOREIGN KEY(username) REFERENCES people(username));"
    ADD_USER_SQL = "INSERT INTO people VALUES ('{}','{}');"
    ADD_SLOT_SQL = "INSERT INTO slots VALUES('{}','{}','{}');"
    GET_SLOT_SQL = "SELECT * FROM slots WHERE username = '{}';"

    def __init__(self, database):
        """Initializes the backend.

        Parameters
        ----------
        database : str
            A filename with the database connection string.
        """
        # Open the SQLite database
        self.conn = sqlite3.connect(database)
        cursor = self.conn.cursor()
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        # If the database is empty, we create the required tables
        cursor.execute(self.INIT_DB_SQL1)
        cursor.execute(self.INIT_DB_SQL2)

    def add_user(self, user_id, name):
        """Adds a new user to the database.

        Parameters
        ----------
        user_id : str
            The username of the new user.
        name : str
            The full name of the new user.

        Returns
        -------
        str
            A JSON object (encoded as string) with two fields: `code` and `desc`.
            `code` is the return code, and `desc` is a human-readable explanation of the
            return code, if required.
        """
        retval = {'code': 0, 'desc': 'Operation successful'}
        cursor = self.conn.cursor()
        try:
            cursor.execute(self.ADD_USER_SQL.format(user_id, name))
        except sqlite3.IntegrityError:
            retval = {'code': 1, 'desc': 'Cannot add user: user already exists'}

        return json.dumps(retval)

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
        str
            A JSON object (encoded as string) with two fields: `code` and `desc`.
            `code` is the return code, and `desc` is a human-readable explanation of the
            return code, if required.

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
        else:
            # Remove minutes, seconds, and microseconds from the slots
            slot_from.replace(minute=0, second=0, microsecond=0)
            slot_to.replace(minute=0, second=0, microsecond=0)
            # Add the new slot
            cursor = self.conn.cursor()
            try:
                cursor.execute(self.ADD_SLOT_SQL.format(user_id, slot_from.isoformat(), slot_to.isoformat()))
            except sqlite3.IntegrityError:
                retval = {'code': 3, 'desc': 'Cannot add slot: integrity error'}

        return json.dumps(retval)

    def get_slots(self, user_id):
        """Returns the available slots for the given user id.

        Parameters
        ----------
        user_id : str
            The ID of the user whose slots will be queried.

        Returns
        -------
        str
            A JSON object (encoded as string) with three fields: `code`, `data`, and `desc`.
            `code` is the return code for the operation, `data` is a set of returned time slots,
            and `desc` is a human-readable explanation of the return code, if required.
            Each hour in a time slot is returned as its own slot.
        """
        retval = {'code': 0, 'data': [], 'desc': 'Operation successful'}
        data = []
        cursor = self.conn.cursor()
        for row in cursor.execute(self.GET_SLOT_SQL.format(user_id)):
            print(row)
            date_from = datetime.strptime(row[1], "%Y-%m-%dT%H:%M:%S.%f")
            date_to = datetime.strptime(row[2], "%Y-%m-%dT%H:%M:%S.%f")
            data.append(0)
        retval['data'] = data
        return json.dumps(retval)


class TestCaseAddSlots(unittest.TestCase):
    """Tests adding items to the calendar."""
    def setUp(self):
        # Setting these tests up includes creating an empty database and one user
        self.new_db = tempfile.NamedTemporaryFile(delete=False)
        self.testCal = Calendar(self.new_db.name)
        self.testCal.add_user('existing_username', 'Existing User')

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
        retval = json.loads(self.testCal.add_slots('existing_username', start, start))
        self.assertNotEqual(retval['code'], 0, '\'add_slots\' is allowing empty ranges')
        retval = json.loads(self.testCal.add_slots('existing_username', end, start))
        self.assertNotEqual(retval['code'], 0, '\'add_slots\' is allowing empty ranges')

        # Tests a valid interval
        start = datetime(2018, 12, 15, 13)
        end = datetime(2018, 12, 15, 14)
        retval = json.loads(self.testCal.add_slots('existing_username', start, end))
        self.assertEqual(retval['code'], 0, 'The \'add_slots\' operation should succeed')

        # Tests whether the 'add_slots' operation actually adds something
        retval = json.loads(self.testCal.get_slots('existing_username'))
        slots_before = len(retval['data'])
        start = datetime(2018, 12, 15, 8)
        end = datetime(2018, 12, 15, 21)
        retval = json.loads(self.testCal.add_slots('existing_username', start, end))
        self.assertEqual(retval['code'], 0, 'The \'add_slots\' operation should succeed')
        retval = json.loads(self.testCal.get_slots('existing_username'))
        slots_after = len(retval['data'])
        self.assertNotEqual(slots_after - slots_before, 0, 'The \'add_slots\' operation is not adding correctly')


if __name__ == '__main__':
    # Run all test cases
    suite_loader = unittest.TestLoader()
    suite1 = suite_loader.loadTestsFromTestCase(TestCaseAddSlots)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suite)