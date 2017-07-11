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
#check if a data is in valid format
def isDateValid(date_text):
    try:
        if date_text != datetime.strptime(date_text, '%Y-%m-%d').strftime('%Y-%m-%d'):
            raise ValueError
        return True
    except ValueError:
        return False
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
#split time period into segments
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
#compute market index
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

#save json file
def saveJsonFile(df, fileName):
    try:
        out = df.to_json(orient='records')[1:-1]
        out = '[' + out + ']'
        with open(fileName, 'w') as f:
            f.write(out)
            f.close()
        print('output file has been saved!')
    except IOError:
        sys.exit('ERROR: Cannot save json file!')
#executed menu
def exec_menu(choice):
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
            try:
                menu_actions[ch]()
            except KeyError:
                print('Invalid selection, please try again. \n')
                menu_actions['main_menu']()
#Menu for entering start date of time period
def start_date_menu():
    print('Start date (enter in format YYYY-mm-dd, ex. 2015-01-01): \n')
    global start_i
    start_i = input(' >> ')
    if(start_i=='b' or start_i == 'q' or start_i ==''):
        exec_menu(start_i)
        return
    elif isDateValid(start_i) is not True:
        print('Date entered is either empty or not valid!')
        start_date_menu()
        return
    else:
        if end_i is None:
            end_date_menu()
    return
#Menu for entering end date of time period
def end_date_menu():
    if start_i is None:
        print('Please enter start date first!')
        start_date_menu()
        return
    print('End date (enter in format YYYY-mm-dd, ex. 2015-01-01):')
    global end_i
    end_i = input(' >> ')
    if(end_i=='b' or end_i == 'q' or end_i == ''):
        exec_menu(end_i)
        return
    elif isDateValid(end_i)  is not True:
        print('Date entered is either empty or not valid!')
        end_date_menu()
        return
    else:
        if start_i is None:
            start_date_menu()
    s = datetime.strptime(start_i, '%Y-%m-%d').date()
    e =  datetime.strptime(end_i, '%Y-%m-%d').date()
    if e <= s:
        print('End date cannot happen before start date!')
        end_date_menu()
    return
def main_menu():
    print('Please enter time period for analysis:\n')
    print('1. Press 1 to enter start date')
    print('2. Press 2 to enter end date')
    print('3. Press b to go back to main menu')
    print('4. Press q to quit')
    choice = input(" >> ")
    exec_menu(choice)
    return
def back():
    menu_actions['main_menu']()
def sysexit():
    sys.exit()
#Menu definition
menu_actions = {
    'main_menu':main_menu,
    '1': start_date_menu,
    '2':end_date_menu,
    'b':back,
    'q':sysexit
    }
# global start and end date of time period
start_i = None
end_i = None
def main():
    os.system('clear')
    print('Loading data for computation...')
    warnings.filterwarnings("ignore")
    df = getDataFrame('projects.json')
    while True:
        main_menu()
        global start_i
        global end_i
        start_i = datetime.strptime(start_i,'%Y-%m-%d')
        end_i = datetime.strptime(end_i,'%Y-%m-%d')
        
        df['start'] = pd.to_datetime(df['start']).apply(lambda x: x.date())
        df['end'] = pd.to_datetime(df['end']).apply(lambda x: x.date())
        maxEnd = max(df['end'])
        minStart = min(df['start'])
        # check if the given time period is valid
        if (end_i.date() < minStart) | (start_i.date() > maxEnd):
            sys.exit('ERROR: The entered time period is out of valid range.')
        timeSeg = getTimeSegment(start_i, end_i)
        
        # end time period
        e = datetime.strptime(timeSeg[-1], '%Y-%m-%d').date()
        #filter records which have end date after the specified start date
        df1 = df[df['start'] <= e]
        print('Computing market segment ranking...')
        #get data interval tree
        dtTree = getDataTree(df1)      
        
        rankV = getMarketScores(dtTree,timeSeg)
        if (rankV == None) | (len(rankV) ==0):
            sys.exit('ERROR:There does not exist campaigns in specified time period.')
        reDf = (pd.DataFrame({'time':timeSeg, 'rank':rankV}, index = timeSeg))
        reDf = getMarketRanks(reDf)
        # save to file
        saveJsonFile(reDf,'segrank.json')
        # compute market index
        print('Computing market index...')
        #get computed indices
        indexV = getMarketIndex(dtTree,timeSeg)
        if (indexV ==None) | (len(indexV) ==0):
            print('There does not exist campaigns in specified time period.')
            return
        miDf = (pd.DataFrame({'time':timeSeg, 'index':indexV}, index = timeSeg))
        # save to file
        saveJsonFile(miDf,'market_index.json')
        print('Press any key to continue or q to exit')
        ch = input(' >> ')
        if(ch.lower()=='q'):
            return
main()
