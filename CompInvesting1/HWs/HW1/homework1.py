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

def optimizer(dt_start, dt_end, ls_symbols):
	bestSharpeRatio = -1
	bestAllocation = []
	bestVol = 0.0
	bestAvgRet = 0.0
	bestCumRet = 0.0
	
	# The closing proces in numpy arrays
	na_price = getData(dt_start, dt_end, ls_symbols)
	
	# Setting the initial allocation inside
	initial_allocation = 1
	
	for i in range (0, 11, 1):
		for j in range (0, 11, 1):
			for k in range (0, 11, 1):
				for l in range (0, 11, 1):
					if (i+j+k+l) == 10:
						ls_allocation = [i/10.0, j/10.0, k/10.0, l/10.0]
						vol, avgRet, sharpe, cumret = simulate(dt_start, dt_end, ls_symbols, ls_allocation, na_price, initial_allocation)
						if sharpe > bestSharpeRatio:
							bestSharpeRatio = sharpe
							bestAllocation = ls_allocation
							bestAvgRet= avgRet
							bestVol = vol
							bestCumRet = cumret
	print "Start Date:", dt_start
	print "End Date:", dt_end
	print "Symbols:", ls_symbols
	print "Optimal Allocation:", bestAllocation
	print "Sharpe Ratio:", bestSharpeRatio
	print "Volatality (stdev of daily returns):", bestVol
	print "Average Daily Return:", bestAvgRet
	print "Cumulative Return:", bestCumRet
	
def simulate(dt_start, dt_end, ls_symbols, ls_allocations, na_price, initial_allocation):

	k = 252 # for sharpe ratio
	
	# The Time of Closing is 1600 hrs 
	dt_timeofday = dt.timedelta(hours=16)
	
	# Get a list of trading days between the start and the end.
	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
	
	# Number of Trading days
	num_tradingDays = (len(ldt_timestamps))
    
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

vol, avgRet, sharpe, cumret = pfs.simulate(dt_start, dt_end, ls_symbols, ls_allocations)

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

vol, avgRet, sharpe, cumret = pfs.simulate(dt_start, dt_end, ls_symbols, ls_allocations)

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

'''
for i in range (0, 11, 1):
	for j in range (0, 11, 1):
		for k in range (0, 11, 1):
			for l in range (0, 11, 1):
				if (i+j+k+l) == 10:
					# print i, j, k, l
					alloc =  [i, j, k, l]
					print alloc
'''
'''
ls_symbols = ['AXP', 'HPQ', 'IBM', 'HNZ']
dt_start = dt.datetime(2010, 1, 1)
dt_end = dt.datetime(2010, 12, 31)
hw.optimizer(dt_start, dt_end, ls_symbols)
'''

#### Q1 -
'''
ls_symbols = ['C', 'GS', 'IBM', 'HNZ']
dt_start = dt.datetime(2010, 1, 1)
dt_end = dt.datetime(2010, 12, 31)
hw.optimizer(dt_start, dt_end, ls_symbols)
'''
###A1
'''
>>> hw.optimizer(dt_start, dt_end, ls_symbols)
Start Date: 2010-01-01 00:00:00
End Date: 2010-12-31 00:00:00
Symbols: ['C', 'GS', 'IBM', 'HNZ']
Optimal Allocation: [0.2, 0.0, 0.0, 0.8]
Sharpe Ratio: 1.36716552762
Volatality (stdev of daily returns): 0.0104738868269
Average Daily Return: 0.000902046043284
Cumulative Return: 1.23681132892
'''


#### Q2 -
'''
ls_symbols = ['BRCM', 'TXN', 'AMD', 'ADI'] 
dt_start = dt.datetime(2010, 1, 1)
dt_end = dt.datetime(2010, 12, 31)
hw.optimizer(dt_start, dt_end, ls_symbols)
'''
#### A2
'''
>>> hw.optimizer(dt_start, dt_end, ls_symbols)
Start Date: 2010-01-01 00:00:00
End Date: 2010-12-31 00:00:00
Symbols: ['BRCM', 'TXN', 'AMD', 'ADI']
Optimal Allocation: [0.4, 0.6, 0.0, 0.0]
Sharpe Ratio: 1.12334024545
Volatality (stdev of daily returns): 0.0174466092415
Average Daily Return: 0.00123458808756
Cumulative Return: 1.31223266453
'''

#### Q3
'''
ls_symbols = ['AAPL', 'GOOG', 'IBM', 'MSFT']
dt_start = dt.datetime(2010, 1, 1)
dt_end = dt.datetime(2010, 12, 31)
hw.optimizer(dt_start, dt_end, ls_symbols)
'''
#### A3
'''
>>> hw.optimizer(dt_start, dt_end, ls_symbols)
Start Date: 2010-01-01 00:00:00
End Date: 2010-12-31 00:00:00
Symbols: ['AAPL', 'GOOG', 'IBM', 'MSFT']
Optimal Allocation: [1.0, 0.0, 0.0, 0.0]
Sharpe Ratio: 1.68878026168
Volatality (stdev of daily returns): 0.0168315943362
Average Daily Return: 0.0017905981418
Cumulative Return: 1.51234162365
'''

#### Q4
'''
ls_symbols = ['BRCM', 'TXN', 'AMD', 'ADI'] 
dt_start = dt.datetime(2011, 1, 1)
dt_end = dt.datetime(2011, 12, 31)
hw.optimizer(dt_start, dt_end, ls_symbols)
'''
#### A4
'''
>>> hw.optimizer(dt_start, dt_end, ls_symbols)
Start Date: 2011-01-01 00:00:00
End Date: 2011-12-31 00:00:00
Symbols: ['BRCM', 'TXN', 'AMD', 'ADI']
Optimal Allocation: [0.0, 0.0, 0.0, 1.0]
Sharpe Ratio: 0.0459503421048
Volatality (stdev of daily returns): 0.0190475488687
Average Daily Return: 5.5135024918e-05
Cumulative Return: 0.968672026615
'''
