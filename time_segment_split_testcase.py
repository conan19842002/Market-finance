import functest
import unittest
from datetime import datetime, timedelta
from intervaltree import Interval, IntervalTree
class TestTimeSegment(unittest.TestCase):
    """
    Test time split function in getTimeSegment()
    """
    def test_equal_start_end_time(self):
        """
        Test that if start and end dates are the same, then throw an exception error
        """
        start = datetime.strptime('2015-01-01', '%Y-%m-%d').date()
        end = start
        self.assertRaises('ERROR: The end date cannot be the same as start time', functest.getTimeSegment(start,end))
    def test_end_ealier_than_start_time(self):
        """
        Test that if start and end dates are the same, then throw an exception error
        """
        start = datetime.strptime('2015-01-01', '%Y-%m-%d').date()
        end = datetime.strptime('2014-01-01', '%Y-%m-%d').date()
        self.assertRaises('ERROR: The end date cannot be earlier than the start time', functest.getTimeSegment(start,end))
    def test_empty_start_end_time(self):
        """
        Test that if start date or end date is empty (or None) then throw en exception error
        """
        #start date is empty, end date is not empty
        start = ''
        end = datetime.strptime('2014-01-01', '%Y-%m-%d').date()
        self.assertRaises('ERROR: The start date and end date cannot be empty', functest.getTimeSegment(start,end))
        # start date is not empty, end date is empty
        start = datetime.strptime('2014-01-01', '%Y-%m-%d').date()
        end = ''
        self.assertRaises('ERROR: The start date and end date cannot be empty', functest.getTimeSegment(start,end))
        #start date is None, end date is not None
        start = None
        end = ''
        self.assertRaises('ERROR: The start date and end date cannot be empty', functest.getTimeSegment(start,end))
        #end date is None, start date is not None
        start = ''
        end = None
        self.assertRaises('ERROR: The start date and end date cannot be empty', functest.getTimeSegment(start,end))
    def test_time_segment_split(self):
        """
        Test that if start and end dates are valid, then split the time period in month segments
        """
        start = datetime.strptime('2014-01-01', '%Y-%m-%d').date()
        end = datetime.strptime('2014-04-01', '%Y-%m-%d').date()
        segments = ['2014-01-01','2014-02-01','2014-03-01','2014-04-01']
        self.assertEqual(segments, functest.getTimeSegment(start,end))
    def test_start_end_within_month(self):
        """
        Test that if start and end dates are within a mont then return time segmemnts in days
        """
        start = datetime.strptime('2014-01-01', '%Y-%m-%d').date()
        end = datetime.strptime('2014-01-04', '%Y-%m-%d').date()
        segments = ['2014-01-01','2014-01-02','2014-01-03','2014-01-04']
        self.assertEqual(segments, functest.getTimeSegment(start,end))

if __name__ == '__main__':
    unittest.main()
