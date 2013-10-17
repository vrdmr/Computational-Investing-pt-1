'''
@author: Varad Meru
@contact: varad.meru@gmail.com
@summary: Homework 6 - Events based on Bollinger Bands
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

# Third Party Imports
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import numpy as np
import operator
import copy
import math
import sys
import csv

# User Inputs
import bollinger as bo

def fetchNYSEDataForEvents(dt_start, dt_end, spxversion, marketSym):
	
	# The Time of Closing is 1600 hrs 
	dt_timeofday = dt.timedelta(hours=16)
	# Get a list of trading days between the start and the end.
	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

	# Creating an object of the dataaccess class with Yahoo as the source.
	c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
	
	# Fetching the equities from the SPX verion
	ls_symbols = c_dataobj.get_symbols_from_list(spxversion)
	
	#Appending the market symbol
	ls_symbols.append(marketSym)
	
	# Keys to be read from the data, it is good to read everything in one go.
	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	
	# Reading the data, now d_data is a dictionary with the keys above.
	# Timestamps and symbols are the ones that were specified before.
	ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))
	
	timestampsForNYSEDays = d_data['close'].index

	# Filling the data for NAN
	for s_key in ls_keys:
		d_data[s_key] = d_data[s_key].fillna(method='ffill')
		d_data[s_key] = d_data[s_key].fillna(method='bfill')
		d_data[s_key] = d_data[s_key].fillna(1.0)
	
	# Getting the numpy ndarray of close prices.
	na_price = d_data['close'].values
	
	# returning the closed prices for all the days    
	return na_price, ldt_timestamps, ls_symbols, d_data

	'''
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
		'''

def find_bollinger_events(df_bollingerValues):
	''' Finding the event dataframe '''
	
	# Fetching the symbols from the dataframe column. 
	ls_symbols = df_bollingerValues.columns.values
	
	file = open("orders.csv", 'w')
	writer = csv.writer(file)
	
	ts_market = df_bollingerValues['SPY']

	print "Finding Events"

    # Creating an empty dataframe
	df_events = copy.deepcopy(df_bollingerValues)
	df_events = df_events * np.NAN

	# Time stamps for the event range
	ldt_timestamps = df_bollingerValues.index

	for s_sym in ls_symbols:
		for i in range(1, len(ldt_timestamps)):
			f_eqbollingerValueToday = df_bollingerValues[s_sym].ix[ldt_timestamps[i]]
			f_eqbollingerValueYesterday = df_bollingerValues[s_sym].ix[ldt_timestamps[i - 1]]
			f_marketBollingerValueYesterday = ts_market[ldt_timestamps[i]]

			if f_eqbollingerValueToday <= -2.0 and f_eqbollingerValueYesterday >= -2.0 and f_marketBollingerValueYesterday >= 1.0:
				df_events[s_sym].ix[ldt_timestamps[i]] = 1
				
	return df_events
	
def main():
	print 'Argument List:', str(sys.argv)
	
	startdaysplit = sys.argv[1].split(',')
	enddaysplit = sys.argv[2].split(',')
	spxversion = sys.argv[3]
	nameofchartfile = sys.argv[4]
	lookbackPeriod = int(sys.argv[5])
	market = 'SPY'
	
	dt_start = dt.datetime(int(startdaysplit[0]),int(startdaysplit[1]), int(startdaysplit[2]), 16, 00, 00)
	dt_end = dt.datetime(int(enddaysplit[0]),int(enddaysplit[1]), int(enddaysplit[2]), 16, 00, 00)
	
	# Fetching the NYSE data
	closingPrices, ldt_timestamps, ls_symbols, d_data = fetchNYSEDataForEvents(dt_start, dt_end, spxversion, market)
	
	# Converting the two outputs from NYSEDataFetch into one dataframe
	df_closingprices = pd.DataFrame(closingPrices, columns = ls_symbols, index = ldt_timestamps)
	
	# Sending the df_closingprices and lookback period to get the bollinger band values, simple moving average of the equities and rolling stddev of the equities
	df_bollinger_vals, df_movingavg, df_movingstddev = bo.bollinger(df_closingprices, lookbackPeriod)
	
	# Finding the events
	df_events = find_bollinger_events(df_bollinger_vals)
	
	#print "Creating Study"
	ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20, s_filename=nameofchartfile, b_market_neutral=True, b_errorbars=True,s_market_sym='SPY')

if __name__ == '__main__':
	main()


"""
dt_start = dt.datetime(2010,1,1, 16, 00, 00)
dt_end = dt.datetime(2010,12,31, 16, 00, 00)
spxversion = 'sp5002012'
nameofchartfile = "event.pdf"
market = 'SPY'

closingPrices, ldt_timestamps, ls_symbols = boe.fetchNYSEDataForEvents(dt_start, dt_end, spxversion, market)
df_closingprices = pd.DataFrame(closingPrices, columns = ls_symbols, index = ldt_timestamps)
df_bollinger_vals, df_movingavg, df_movingstddev = bo.bollinger(df_closingprices, lookbackPeriod)
boe.find_bollinger_events(df_bollinger_vals)
"""