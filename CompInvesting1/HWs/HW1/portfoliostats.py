'''
Created on September, 13, 2013

@author: Varad Meru
@contact: varad.meru@gmail.com
@summary: Homework 1 - Portfolio Management

'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def simulate(dt_start, dt_end, ls_symbols, ls_allocations):

	# Setting the initial allocation inside
	initial_allocation = 1.0
	k = 252 # for sharpe ratio
	
	# The Time of Closing is 1600 hrs 
	dt_timeofday = dt.timedelta(hours=16)
	
	# Get a list of trading days between the start and the end.
	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
	
	# Number of Trading days
	num_tradingDays = (len(ldt_timestamps))
	
	# The closing proces in numpy arrays
	na_price = getData(dt_start, dt_end, ls_symbols)
    
	# The first day prices of the quities
	arr_firstdayPrices = na_price[0,:]
	
	# The cumulative statistics of the overall fund, which will be updated while incrementally parsing over the prices for the equity
	# It'll contain the 
	## [0] fund invest - The sum of the invested money 
	## [1] fund's cumulative return
	## [2] fund's daily returns. The daily 
	fund_stats = np.zeros((num_tradingDays, 3)) # Number of trading days * 3
	
	# For all the trading days
	for i in range(num_tradingDays):
		# For all the equities
		for j in range(len(na_price[i,:])):
			# Do
			fund_stats[i,0] += ((na_price[i,j]/arr_firstdayPrices[j]) * ( initial_allocation * ls_allocations[j]) )
			
	for i in range(num_tradingDays):
		fund_stats[i,1] = ((fund_stats[i,0]/initial_allocation) * 100)
		if i != 0:
			fund_stats[i,2] = ((fund_stats[i,0]/fund_stats[i-1,0]) - 1 )

	avgDailyReturn = np.average(fund_stats[:,2])
	sqStdDev = np.std(fund_stats[:,2])
	sharpeRatio = (k**(1/2.0))*(avgDailyReturn/sqStdDev)
	cumReturn = fund_stats[-1,0]
	
	return sqStdDev, avgDailyReturn, sharpeRatio, cumReturn
    
def getData(dt_start, dt_end, ls_symbols):

    # The Time of Closing is 1600 hrs 
    dt_timeofday = dt.timedelta(hours=16)
    
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values
    
    # returning the closed prices for all the days    
    return na_price

def main():
    simulate(dt_start, dt_end, ls_symbols, ls_allocations)

if __name__ == '__main__':
    main()
    
'''
### Testing
# List of symbols
ls_symbols = ['AAPL', 'GLD', 'GOOG', 'XOM']

# List of allocations, mapped by index to the symbols
ls_allocations = [0.4, 0.4, 0.0, 0.2]

# Start and End date of the charts
dt_start = dt.datetime(2011, 1, 1)
dt_end = dt.datetime(2011, 12, 31)

vol, avgRet, sharpe, cumret = hw.simulate(dt_start, dt_end, ls_symbols, ls_allocations)

print vol
print avgRet
print sharpe
print cumret

### Expected output
Sharpe Ratio: 1.02828403099
Volatility (stdev of daily returns):  0.0101467067654
Average Daily Return:  0.000657261102001
Cumulative Return:  1.16487261965

### Output
sharpe: 1.02828403099
vol: 0.0101467067654
avgRet: 0.000657261102001
cumret: 16.4872619645
'''

'''
### Testing
reload(homework1)
# List of symbols
ls_symbols = ['AXP', 'HPQ', 'IBM', 'HNZ']

# List of allocations, mapped by index to the symbols
ls_allocations = [0.0, 0.0, 0.0, 1.0]

# Start and End date of the charts
dt_start = dt.datetime(2010, 1, 1)
dt_end = dt.datetime(2010, 12, 31)

vol, avgRet, sharpe, cumret = hw.simulate(dt_start, dt_end, ls_symbols, ls_allocations)

print vol
print avgRet
print sharpe
print cumret

### Expected output
# Sharpe Ratio: 1.29889334008
# Volatility (stdev of daily returns): 0.00924299255937
# Average Daily Return: 0.000756285585593
# Cumulative Return: 1.1960583568

### Output
# sharpe: 1.29631360895
# vol: 0.00924299255937
# avgRet: 0.000756285585593
# cumret: 19.6058356795
'''