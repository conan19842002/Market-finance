# Market-finance
The assignment is organised in following files:
- test.py: the file that contains main program.
- market_index_testcase.py: This file declares testcases used to test the function that computes market index
- market_segment_ranking_testcase.py: This file declares testcases used to test the function that computes trending market segment.
- time_segment_split_testcase.py: This file declares testcases used to test the function that split a given time period into time segments.
- functest.py: This file contains functions which are used to test.
- test1.json: default test data, this is used for testing code.
- doc.pdf: Details of solutions.

How to run program:

You can run file test.py to start doing the analysis. Once it starts, the program will first need to load the data from 'projects.json' file, this process may take some time. It then prompts you to enter a time period (start and end dates). You can use appropriate keys to enter start and end dates. The program will then start computing the trending market segment and market index and store the outputs into files named 'segrank.json' and 'market_index.json', respectively. The json files are structured in two fields 'time' and 'rank' or 'index' where 'time' contains time segments and 'rank' or 'index' contains ranking scores or market indices, respectively.
