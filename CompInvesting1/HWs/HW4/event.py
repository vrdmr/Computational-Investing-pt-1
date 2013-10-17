'''
Created on September, 13, 2013

@author: Varad Meru
@contact: varad.meru@gmail.com
@summary: Homework 2 - Event Profiler

'''

# Third Party Imports
import copy
import math
import numpy as np
import pandas as pd
import datetime as dt

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

import sys
import csv

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""

def find_events(ls_symbols, d_data):
	''' Finding the event dataframe '''
	
	file = open("orders.csv", 'w')
	writer = csv.writer(file)
	
	df_close = d_data['actual_close']
	ts_market = df_close['SPY']

	print "Finding Events"

    # Creating an empty dataframe
	df_events = copy.deepcopy(df_close)
	df_events = df_events * np.NAN

	# Time stamps for the event range
	ldt_timestamps = df_close.index

	for s_sym in ls_symbols:
		for i in range(1, len(ldt_timestamps)):
		
            # Calculating the returns for this timestamp
			f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
			f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
			
			if f_symprice_today < 9.0 and f_symprice_yest >= 9.0:
				today = ldt_timestamps[i]
				todayplus5 = ldt_timestamps[i+5]
				
				writer.writerow([today.year, today.month, today.day , s_sym, "Buy","100"])
				writer.writerow([todayplus5.year, todayplus5.month, todayplus5.day, s_sym, "Sell","100"])
				
				df_events[s_sym].ix[ldt_timestamps[i]] = 1
				
	# Closing the file
	file.close()
	
	return df_events


def writeValuesIntoCSV(valuesFilename, valueFrame):

	for index in range(len(valueFrame)):
		writer.writerow([valueFrame.index[index].year, valueFrame.index[index].month, valueFrame.index[index].day ,int(round(valueFrame.valueOfPortfolio.ix[index], 0))])
		
	file.close()

if __name__ == '__main__':

	print 'Argument List:', str(sys.argv)
	
	startdaysplit = sys.argv[1].split(',')
	enddaysplit = sys.argv[2].split(',')
	spxversion = sys.argv[3]
	nameofchartfile = sys.argv[4]
	
	dt_start = dt.datetime(int(startdaysplit[0]),int(startdaysplit[1]), int(startdaysplit[2]), 16, 00, 00)
	dt_end = dt.datetime(int(enddaysplit[0]),int(enddaysplit[1]), int(enddaysplit[2]), 16, 00, 00)
	
	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

	dataobj = da.DataAccess('Yahoo')
	#ls_symbols = dataobj.get_symbols_from_list('sp5002012')
	ls_symbols = dataobj.get_symbols_from_list(spxversion)
	
	ls_symbols.append('SPY')

	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))

	for s_key in ls_keys:
		d_data[s_key] = d_data[s_key].fillna(method='ffill')
		d_data[s_key] = d_data[s_key].fillna(method='bfill')
		d_data[s_key] = d_data[s_key].fillna(1.0)

	df_events = find_events(ls_symbols, d_data)
	print "Creating Study"
	ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20, s_filename=nameofchartfile, b_market_neutral=True, b_errorbars=True,s_market_sym='SPY')
