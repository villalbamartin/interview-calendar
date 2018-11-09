#!/usr/bin/python3

import json
import unittest
from datetime import datetime


class Calendar:
    def __init__(self):
        pass

    def add(self, user_id, slot_from, slot_to):
        """Adds a slot for the given user

        Parameters
        ----------
        user_id : str
            The ID of the user whose slot will be added
        slot_from : datetime
            The earlier date at which the user is available.
            Minutes, seconds, and microseconds are discarded/set to 0.
        slot_to : datetime
            The earliest date at which the user is *not* available
            Minutes, seconds, and microseconds are discarded/set to 0.

        Returns
        -------
        A JSON object with two fields, `code` and `desc`.
        `code` is the error code, and `desc` is a human-readable explanation of the error.

        Notes
        -----
        This operation will add slots in the range [slot_from, slot_to). That is: if the user
        is willing to start the meeting anytime from 16:00 to 20:00, then `slot_to` should
        have a value of 21:00.
        """
        retval = {'code' : 0, 'desc': 'Operation successful'}
        return json.dumps(retval)

class TestCaseAdd(unittest.TestCase):
    """Tests adding items to the calendar."""
    def setUp(self):
        self.testCal = Calendar()

    def tearDown(self):
        pass

    def testAdd(self):
        # Test a valid interval
        start = datetime(2018, 12, 12, 13)
        end = datetime(2018, 12, 12, 14)
        retval = json.loads(self.testCal.add('username', start, end))
        self.assertEquals(retval['code'], 0, 'The \'add\' operation should succeed')
        # Test all kind of wrong arguments
        all_args = ['2018/12/12 06:20', 12, None, 12.21, datetime.now()]
        for user in all_args:
            for start in [None, 14, 3.5, '2018/12/12 06:20', datetime.now()]:
                for end in [None, 14, 3.5, '2018/12/12 06:20']:
                    if not (isinstance(user, str) and isinstance(start, datetime) and isinstance(end, datetime)):
                        retval = json.loads(self.testCal.add(user, start, end))
                        self.assertNotEquals(retval['code'], 0, '\'add\' is not validating its arguments correctly')


if __name__ == '__main__':
    # Run all test cases
    suite_loader = unittest.TestLoader()
    suite1 = suite_loader.loadTestsFromTestCase(TestCaseAdd)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suite)