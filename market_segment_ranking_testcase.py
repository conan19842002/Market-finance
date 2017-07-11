import ijson
import functest
import unittest
import pandas as pd
from datetime import datetime, timedelta
from intervaltree import Interval, IntervalTree
from statistics import mean
import warnings
class TestMarketSegRank(unittest.TestCase):
    """
    Test function getMarKetIndex that compute market indices
    """
    def test_invalid_data(self):
        """
        Test that if data is None or empty then return None
        """
        dtTree = IntervalTree()
        timeSeg = ['2014-01-01','2014-02-01']
        self.assertEqual(None, functest.getMarketScores(dtTree, timeSeg))
        """
        Test that if data is not empty and time segment is None then return None
        """
        start = datetime.strptime('2014-01-01', '%Y-%m-%d').date()
        end = datetime.strptime('2014-04-01', '%Y-%m-%d').date()
        dtTree = IntervalTree()
        dtTree.addi(start,end,[3,0.1])
        timeSeg = ''
        self.assertEqual(None, functest.getMarketScores(dtTree, timeSeg))
    def test_default_data(self):
        """
        Test if the function returns correct market index list when given end date  < available end date
        """
        start = ['2015-01-01','2015-02-01','2015-01-21','2015-03-01','2015-04-01',
                 '2015-02-10', '2015-05-01']
        end = ['2015-01-17','2015-02-18','2015-03-19',
               '2015-03-21','2015-04-22','2015-03-24','2015-05-25']
        #real scores
        l = len(start)
        score = [0]*l
        total_concept = 18
        conceptList = ['a','b','c','d','f','g','h','k','l','m','n','p','q','i','j','t','r']
        concepts = {}
        freq_s = {}
        concepts[0] = [{'a':2,'b':2,'c':1,'h':1,'f':1,'g':2,'i':1,'k':1,'l':2,'d':1}]
        concepts[1] = [{'m':1,'n':3,'p':2,'q':1,'g':1,'k':1}]
        concepts[2] = [{'a':2,'n':1,'h':1,'k':1,'p':1,'b':1}]
        concepts[3] = [{'i':1,'j':1,'p':1,'q':1,'t':1,'r':1,'n':1,'g':1,'k':1}]
        concepts[4] = [{'c':1,'f':1,'k':3,'p':2,'d':1}]
        concepts[5] = [{'a':2,'c':1,'g':1,'h':1,'k':1,'d':1,'b':1,'f':1}]
        concepts[6] = [{'g':1,'c':1,'l':2,'i':1,'h':1,'p':1,'n':1,'q':1}]
        for c in conceptList:
            freq_s[c] = 0
        
        for k in concepts:
            for v in concepts[k]:
                for c in v:
                    freq_s[c] += v[c]
        s = 0
        for c in freq_s:
            s += freq_s[c]
        for c in conceptList:
            freq_s[c] /= s
        for i in range(0,l):
            for v in concepts[i]:
                for c in v: 
                    score[i] += v[c]*freq_s[c]
        # read test dataset
        fileName = 'test1.json'
        warnings.filterwarnings("ignore")
        df = functest.getDataFrame(fileName)
        df['start'] = pd.to_datetime(df['start']).apply(lambda x: x.date())
        df['end'] = pd.to_datetime(df['end']).apply(lambda x: x.date())
        dtTree = functest.getDataTree(df)
        s1 = datetime.strptime('2015-05-01', '%Y-%m-%d').date()
        e1 = datetime.strptime('2015-06-01', '%Y-%m-%d').date()

        # input dates
        s = datetime.strptime('2015-02-11', '%Y-%m-%d').date()
        e = datetime.strptime('2015-07-22', '%Y-%m-%d').date()
        timeSeg = ['2015-03-01', '2015-04-01', '2015-05-01', '2015-06-01', '2015-07-01', '2015-07-22']
        l = len(timeSeg)
        #expected scores
        exp_score = [-1]*l
        # campaigns from 2015-02-01 to 2015-03-01
        exp_score[0] = score[1] + score[2] + score[5]
        # campaigns from 2015-03-01 to 2015-04-01
        exp_score[1] = score[3] + score[5] + score[2]
        # campaigns from 2015-04-01 to 2015-05-01
        exp_score[2] = score[4] 
        # campaigns from 2015-05-01 to 2015-06-01
        exp_score[3] = score[6]
        # No campaigns from 2015-06-01 to 2015-07-01
        exp_score[4] = -1
        # No campaigns from 2015-07-01 to 2015-07-22
        exp_score[5] = -1
        
        # computed market scores
        reScores = functest.getMarketScores(dtTree,timeSeg)
        error = 1e-7
        for i in range(0,l):
            self.assertTrue(abs(reScores[i] - exp_score[i])<error)
        
if __name__ == '__main__':
    unittest.main()
