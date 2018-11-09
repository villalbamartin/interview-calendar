#!/usr/bin/python3

import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta


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
        # Allow to refer to results via column name rather than just index
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        # Enables foreign keys, if possible
        cursor.execute("PRAGMA foreign_keys = ON")
        # If the database is empty, we create the required tables
        cursor.execute(self.INIT_DB_SQL1)
        cursor.execute(self.INIT_DB_SQL2)
        self.conn.commit()

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
            self.conn.commit()
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
                self.conn.commit()
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
            date_from = datetime.strptime(row['date_from'], "%Y-%m-%dT%H:%M:%S")
            date_to = datetime.strptime(row['date_to'], "%Y-%m-%dT%H:%M:%S")
            while date_from < date_to:
                data.append(date_from.isoformat())
                date_from += timedelta(seconds=3600)
        retval['data'] = data
        self.conn.commit()
        return json.dumps(retval)


class TestCaseAdd(unittest.TestCase):
    """Tests adding items to the calendar.
    By necessity, this class also tests whether it's possible to add a user,
    since there is no way to test any kind of insertion.
    """
    def setUp(self):
        # Setting these tests up includes creating an empty database and one user
        self.new_db = tempfile.NamedTemporaryFile(delete=False)
        self.testCal = Calendar(self.new_db.name)
        self.testCal.add_user('existing_username', 'Existing User')

    def tearDown(self):
        # Delete the temporary database
        os.unlink(self.new_db.name)

    def testAddSlots(self):
        """Tests whether adding elements to the database works."""
        # Note that `setUp` is already testing whether adding a user works,
        # or otherwise most examples here would fail

        # Test all kind of wrong arguments for 'add_slots'
        all_args = ['2018/12/12 06:20', 12, None, 12.21, datetime.now()]
        for user in all_args:
            for start in all_args:
                for end in all_args:
                    # There is exactly one case in which the input is valid,
                    # so we need to check for that first
                    if not (isinstance(user, str) and isinstance(start, datetime) and isinstance(end, datetime)):
                        retval = json.loads(self.testCal.add_slots(user, start, end))
                        self.assertNotEqual(retval['code'], 0, '\'add_slots\' is not validating arguments correctly')

        # Tests for an empty range when adding slots
        start = datetime(2018, 12, 15, 13)
        end = datetime(2018, 12, 15, 14)
        retval = json.loads(self.testCal.add_slots('existing_username', start, start))
        self.assertNotEqual(retval['code'], 0, '\'add_slots\' is allowing empty ranges')
        retval = json.loads(self.testCal.add_slots('existing_username', end, start))
        self.assertNotEqual(retval['code'], 0, '\'add_slots\' is allowing empty ranges')

        # Tests a valid interval for slots
        start = datetime(2018, 12, 15, 13)
        end = datetime(2018, 12, 15, 14)
        retval = json.loads(self.testCal.add_slots('existing_username', start, end))
        self.assertEqual(retval['code'], 0, 'The \'add_slots\' operation should succeed')

        # Tests whether the 'add_slots' operation actually adds correctly
        retval = json.loads(self.testCal.get_slots('existing_username'))
        slots_before = len(retval['data'])
        start = datetime(2018, 12, 15, 8)
        end = datetime(2018, 12, 15, 21)
        retval = json.loads(self.testCal.add_slots('existing_username', start, end))
        self.assertEqual(retval['code'], 0, 'The \'add_slots\' operation should succeed')
        retval = json.loads(self.testCal.get_slots('existing_username'))
        slots_after = len(retval['data'])
        self.assertEqual(slots_after - slots_before, 13, 'The \'add_slots\' operation is not adding correctly')

        # Tests whether it's possible to add a slot for a user that doesn't exist
        retval = json.loads(self.testCal.get_slots('random_username'))
        self.assertEqual(retval['code'], 0, 'Asking about a non-existent user should succeed')
        start = datetime(2018, 12, 15, 8)
        end = datetime(2018, 12, 15, 21)
        retval = json.loads(self.testCal.add_slots('random_username', start, end))
        self.assertNotEqual(retval['code'], 0, 'Adding slots to a non-existent user should not succeed')


class TestCaseGet(unittest.TestCase):
    """Tests querying items from the calendar.
    By necessity, this class also tests whether it's possible to add items,
    or the database would be empty for all queries.
    """
    def setUp(self):
        # Setting these tests up includes creating a simple database and some users
        self.new_db = tempfile.NamedTemporaryFile(delete=False)
        self.testCal = Calendar(self.new_db.name)
        self.testCal.add_user('manager1', 'Manager 1')
        self.testCal.add_user('manager2', 'Manager 2')
        self.testCal.add_user('manager3', 'Manager 3')
        self.testCal.add_user('interviewee', 'Interview Candidate')

        # 2018/11/19 is Monday. Putting all examples in the same week to make them easier
        # to understand and debug
        self.testCal.add_slots('manager1', datetime(2018, 11, 19, 8), datetime(2018, 11, 19, 18))
        self.testCal.add_slots('manager1', datetime(2018, 11, 21, 8), datetime(2018, 11, 21, 18))
        self.testCal.add_slots('manager1', datetime(2018, 11, 23, 8), datetime(2018, 11, 23, 18))
        self.testCal.add_slots('manager2', datetime(2018, 11, 19, 11), datetime(2018, 11, 19, 21))
        self.testCal.add_slots('manager2', datetime(2018, 11, 20, 11), datetime(2018, 11, 20, 21))
        self.testCal.add_slots('manager2', datetime(2018, 11, 21, 11), datetime(2018, 11, 21, 21))
        self.testCal.add_slots('manager2', datetime(2018, 11, 22, 11), datetime(2018, 11, 22, 13))
        self.testCal.add_slots('manager3', datetime(2018, 11, 22, 16), datetime(2018, 11, 23, 18))
        self.testCal.add_slots('interviewee', datetime(2018, 11, 19, 9), datetime(2018, 11, 19, 17))
        self.testCal.add_slots('interviewee', datetime(2018, 11, 20, 9), datetime(2018, 11, 20, 17))
        self.testCal.add_slots('interviewee', datetime(2018, 11, 21, 9), datetime(2018, 11, 21, 17))

    def tearDown(self):
        # Delete the temporary database
        os.unlink(self.new_db.name)

    def testCorrectlyAdded(self):
        all_slots = [('manager1', 30), ('manager2', 32), ('manager3', 26), ('interviewee', 24)]
        for user, slots in all_slots:
            retval = json.loads(self.testCal.get_slots(user))
            self.assertEqual(retval['code'], 0, 'Asking about existing slots should succeed')
            self.assertEqual(len(retval['data']), slots, 'The number of slots for \'{}\' is incorrect'.format(user))


if __name__ == '__main__':
    # Run all test cases
    suite_loader = unittest.TestLoader()
    suite1 = suite_loader.loadTestsFromTestCase(TestCaseAdd)
    suite2 = suite_loader.loadTestsFromTestCase(TestCaseGet)
    suite = unittest.TestSuite([suite1, suite2])
    unittest.TextTestRunner(verbosity=2).run(suite)