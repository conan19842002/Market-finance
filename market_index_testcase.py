import functest
import unittest
from datetime import datetime, timedelta
from intervaltree import Interval, IntervalTree
from statistics import mean
import radar
import numpy as np
class TestMarketIndex(unittest.TestCase):
    """
    Test function getMarKetIndex that compute market indices
    """
    def test_invalid_data(self):
        """
        Test that if data is None or empty then return None
        """
        dtTree = IntervalTree()
        timeSeg = ['2014-01-01','2014-02-01']
        self.assertEqual(None, functest.getMarketIndex(dtTree, timeSeg))
        """
        Test that if data is not empty and time segment is None then return None
        """
        start = datetime.strptime('2014-01-01', '%Y-%m-%d').date()
        end = datetime.strptime('2014-04-01', '%Y-%m-%d').date()
        dtTree = IntervalTree()
        dtTree.addi(start,end,[3,0.1])
        timeSeg = ''
        self.assertEqual(None, functest.getMarketIndex(dtTree, timeSeg))
    def test_dedault_data(self):
        """
        Test if the function return correct market index list when given end date  < available end date
        """
        start = '2015-01-01'
        end = ['2015-01-17','2015-02-18','2015-03-19',
               '2015-03-21','2015-04-22','2015-04-24','2015-04-25']
        s = datetime.strptime(start, '%Y-%m-%d').date()
        raised_fx = [1,3,40,2,5,5,20]
        score = [0.01,0.004,0.05,0.12,0.5,0.003,0.2]
        dtTree = IntervalTree()
        for i in range(0,len(end)):
            e = datetime.strptime(end[i], '%Y-%m-%d').date()
            dtTree.addi(s,e,[raised_fx[i],score[i]])
        timeSeg = ['2015-01-01', '2015-01-22','2015-02-22','2015-03-22','2015-04-22']
        # compute expected market index
        mIndex = [0]*5
        mIndex[0] = 0 # No campaigns were available in this time segment
        mIndex[1] = 1000 # default index for the first time point
        mIndex[2] = mean([1,3])/mean([1])*1000
        mIndex[3] = mean([1,3,40,2])/mean([1,3])*1000
        mIndex[4] = mean([1,3,40,2,5])/mean([1,3,40,2])*1000
        error = 1e-7
        result = functest.getMarketIndex(dtTree, timeSeg)
        for i in range(0,4):
            self.assertTrue(abs(mIndex[i] - result[i])<error)        
if __name__ == '__main__':
    unittest.main()
