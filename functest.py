import ijson
from pprint import pprint
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys, os
import unittest
from intervaltree import Interval, IntervalTree
from statistics import mean
import warnings
#create data interval tree
def getDataTree(df):
    tree = IntervalTree()
    for row in df.itertuples():
        start = row[1]
        end = row[2]
        raised_money = row[3]
        score = row[5]
        tree.addi(start, end, [raised_money,score])
    return tree
#get market ranks
def getMarketRanks(reDf):
    r = reDf['rank']
    idx = np.where(r > -1)[0]
    r[idx] = r[idx].rank()
    r[r==-1] = 0
    reDf['rank'] = r
    return reDf
#compute market scores
def getMarketScores(dtTree, timeSeg):
    scoreV = []
    if (dtTree == None) | (len(dtTree) == 0):
        return None
    if len(timeSeg) == 0:
        return None
    # take the immediately preceding start time of the same length
    # if there is only one date available then take the start date
    # as the earliest date
    if len(timeSeg) == 1:
        preVDate = min(dtTree)[0].strftime('%Y-%m-%d')
    else:
        firstDate = datetime.strptime(timeSeg[0], '%Y-%m-%d').date()
        secondDate = datetime.strptime(timeSeg[1], '%Y-%m-%d').date()
        ndays = (secondDate - firstDate).days
        preVDate = (pd.Timestamp(firstDate)- timedelta(days=ndays)).strftime('%Y-%m-%d')
    preVDate = datetime.strptime(preVDate, '%Y-%m-%d').date()
    for i in range(0,len(timeSeg)):
        e = datetime.strptime(timeSeg[i], '%Y-%m-%d').date()
        re = list(dtTree.search(preVDate,e))
        #get score for ranking
        score = getMarketSegScore(re)
        scoreV.append(score)
        preVDate = e
    return scoreV
#compute market segment score
def getMarketSegScore(re):
    if (re == None) | (len(re)) == 0:
        return -1
    s = 0
    for i in range(0,len(re)):
        s += re[i][2][1]
    return s

def getTimeSegment(start, end):
    if (start == None) | (end == None)| (start == '') | (end == ''):
        print('EROROR: The start date and end date cannot be empty')
        return None
    if end == start:
        print('EROROR: The end date cannot be the same as start time')
        return None
    elif end < start:
        print('EROROR: The end date cannot be earlier than the start time')
        return None
    dateIndex = pd.date_range(start = start, end = end, freq='MS')
    # if time period is within month then split the period in days instead of months
    if len(dateIndex)==1:
        dateIndex = pd.date_range(start = start, periods = (end-start).days+1)
    re = dateIndex.strftime('%Y-%m-%d').tolist()
    # if the end date is not included in the final result then include it
    if dateIndex[-1].date() != end:
        re.append(end.strftime('%Y-%m-%d'))
    return re
#get a list of raised money amounts
def getRaisedList(re):
    r = []
    l = len(re)
    if l>0:
        for i in range(0,l):
            r.append(re[i][2][0])
    return r
#collect data
def getDataFrame(fileName):
    startV = []
    endV = []
    conceptV = []
    raisedFxV = []
    try:
        f = open(fileName)
    except IOError:
        sys.exit('ERROR: The json file was not found in the correct directory. '\
                     'Please show the path to the json file.' )
        
    for obj in ijson.items(f, 'item'):
            if 'start_time' in obj:
                start = obj['start_time']
                
            if 'end_time' in obj:
                end = obj['end_time']

            if 'raised_fx' in obj:
                raised_fx = obj['raised_fx']['GBP']
                
            if 'concepts' in obj:
                concepts = obj['concepts']
            for key, value in concepts.items():
                        for c in value:
                           for k, v in c.items():
                               if 'concept' in k:
                                   startV.append(start)
                                   endV.append(end)
                                   conceptV.append(v)
                                   raisedFxV.append(raised_fx)
    df = pd.DataFrame({'start':startV, 'end':endV, 'concept':conceptV, 'raised_fx':raisedFxV}, index = startV)
    df['raised_fx'] = df['raised_fx'].astype('float64')
    df1 = df.groupby(['start','end', 'raised_fx','concept'])['concept'].agg({'score':'count'})
    warnings.filterwarnings("ignore")
    df1 = df1.reset_index()
    df2 = df1.groupby('concept').transform('sum')['score']/df1['score'].sum()
    df1.score = df1.score*df2
    df1 = df1.groupby(['start','end','raised_fx']).sum()
    df1 = df1.reset_index()
    return df1
def getMarketIndex(dtTree, timeSeg):
    if (dtTree == None) | (len(dtTree) == 0):
        return None
    if (timeSeg == None) | (len(timeSeg) == 0):
        return None
    l = len(timeSeg)
    minTime = min(dtTree)
    minDate = minTime[0]
    prev = 0
    curr = 0
    indexV = [-1]*l
    first = -1
    d = []
    reL = []
    for i in range(0,l):
        d.append(datetime.strptime(timeSeg[i], '%Y-%m-%d').date())
    for i in range(0,l):
        re = list(dtTree.search(minDate, d[i], strict=True))
        # get list of raised amounts
        reL = getRaisedList(re)
        if len(reL) > 0:
            first = i
            indexV[i] = 1000
            break
        indexV[i] = 0
    if first==-1:
        return None
    prev = mean(reL)
    for i in range(first+1,l):
        re = list(dtTree.search(minDate, d[i], strict=True))
        # get list of raised amounts
        reL = getRaisedList(re)
        curr = mean(reL)
        if curr == 0:
            indexV[i] = 1000
        elif prev > 0:
            indexV[i] = curr/prev*1000
        prev = curr
    #set index to (maximum value + 1) for those which are -1
    if -1 in indexV:
        m = max(indexV)+1
        for (i, item) in enumerate(indexV):
            if item == -1:
                indexV[i] = m
    return indexV
