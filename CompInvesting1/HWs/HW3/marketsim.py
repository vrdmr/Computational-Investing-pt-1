'''
Created on October, 2, 2013

@author: Varad Meru
@contact: varad.meru@gmail.com
@summary: Homework 3 - Market Simulator
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
import operator
import sys
import csv

'''
This function reads the file and converts the order requests into a matrix in NumPy for ease of use.
Make sure that the linebreaks are classical Unix '\n' and not any other line breaks. They can cause a problem (eg. orders2.csv has that issue)
'''
'''
@Depricated
'''
def readOrdersFile(filename):

	# opening the filename
	fr = open(filename)
	
	# reading the file and getting the numberOfLines
	numberOfLines = len(fr.readlines())
	
	# Making a zero matrix
	ordersMatrix = np.zeros((numberOfLines, 6))
	
	#Empty List
	symbolsList=[]
	
	#OrderType
	orderTypes = ["Buy", "Sell"]
	
	# Re-initiating the file reader
	fr = open(filename)
	
	# for row count in 
	index=0
	
	# For each line
	# A Sample Line - 2011,1,14,AAPL,Buy,1500
	for orderString in fr.readlines():
		
		# Stripping off the return line character
		orderString=orderString.strip()
		
		# Splitting the line and getting a List back
		listFromLine = orderString.split(',')
		updatedListFromLine = []
		
		if listFromLine[3] in symbolsList:
			updatedListFromLine = listFromLine
			updatedListFromLine[3] = symbolsList.index(listFromLine[3])
			updatedListFromLine[4] = orderTypes.index(listFromLine[4])
		else:
			# Add that symbol into symbolsList
			symbolsList.append(listFromLine[3])
			updatedListFromLine = listFromLine
			updatedListFromLine[3] = symbolsList.index(listFromLine[3])
			updatedListFromLine[4] = orderTypes.index(listFromLine[4])
			
		# Getting the first 6 entries from the listFromLine and putting it into returnMat with index.
		# colon op - get all elements from row. (row number = index)
		ordersMatrix[index,:]=updatedListFromLine[0:6]
				
		# incr.
		index+=1
	
	# The Matrix created by NumPy is Float, converting into ints
	integerMatrix = ordersMatrix.astype(int)
	
	# Sorting the matrix by date. Sorting the first 3 columns - 
	# First column is Year, Second- month, Third- Day
	# Sample - 2011,1,14,AAPL,Buy,1500,
	sortedMatrix = np.array(sorted(integerMatrix, key=tuple))
	
	return sortedMatrix, symbolsList, orderTypes
'''
Above Method is Deprecated. Do not use it. Pandas Rules |m|
'''

def readOrdersFileIntoDF(filename):

	# opening the filename
	fr = open(filename)
	
	# for row count in 
	index=0
	
	# Lists used for making the dataframe.
	dtList = []
	symbolList = []
	orderTypeList = []
	volumeList = []
	
	# For each line
	# A Sample Line - 2011,1,14,AAPL,Buy,1500
	for orderString in fr.readlines():
		
		# Stripping off the return line character
		orderString=orderString.strip()
		
		# Splitting the line and getting a List back
		listFromLine = orderString.split(',')
		
		# Adding the dates into dtList. 16,00,00 for 1600 hrs
		dtList.append(dt.datetime(int(listFromLine[0]), int(listFromLine[1]), int(listFromLine[2]), 16, 00, 00))
		
		# Adding the symbols into symbolList
		symbolList.append(listFromLine[3])
		
		# Adding the orders into orderTypeList
		orderTypeList.append(listFromLine[4])
		
		# Adding the number of shares into volumeList
		volumeList.append(listFromLine[5])
	
	# Creating a Dictionary for converting it into DataFrame later
	data = { 'datetime' : dtList, 'symbol' : symbolList, 'ordertype':orderTypeList, 'volume':volumeList }
	
	# Converting the Dictinary into a nice looking Pandas Dataframe
	ordersDataFrame = pd.DataFrame(data)
	
	#Sorting by datetime column #Makes Sense :)
	sortedOrdersDataFrame = ordersDataFrame.sort_index(by=['datetime'])
	sortedOrdersDataFrame = sortedOrdersDataFrame.reset_index(drop=True)
	
	
	# Making the datetime columns as the index and removing it from the table
	# sortedOrdersDataFrame.index = sortedOrdersDataFrame.datetime
	# del sortedOrdersDataFrame['datetime']
	
	# Getting the Symbols from the Orders. This list will be required for fetching the prices
	symbolList = list(set(sortedOrdersDataFrame['symbol']))
	
	# Returning it.
	return sortedOrdersDataFrame, symbolList
	
def fetchNYSEData(dt_start, dt_end, ls_symbols):
	
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
    
    timestampsForNYSEDays = d_data['close'].index

    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values
	
    # returning the closed prices for all the days    
    return na_price, ldt_timestamps
    
def marketsim(initialCash, ordersDataFrame, symbols):
		
	# reading the boundary dates
	dt_start = ordersDataFrame.datetime[0]
	dt_end = ordersDataFrame.datetime[len(ordersDataFrame)-1]
	
	# All the adjustedClosingPrices fetched from NYSE within the range and for given symbols
	closingPrices, ldt_timestamps = fetchNYSEData(dt_start, dt_end, symbols)
	
	num_tradingDays = len(ldt_timestamps)
	
	# For Holdings of the share	
	temp = np.zeros((1, len(symbols)))
	holdings = pd.DataFrame(temp, columns = symbols, index = ['holdings'])
	
	#Cash for the days
	temp = np.zeros((num_tradingDays, 1))
	cash = pd.DataFrame(temp, columns = ['cashinhand'])
	
	#Value for the days
	temp = np.zeros((num_tradingDays, 1))
	valueFrame = pd.DataFrame(temp, columns = ['valueOfPortfolio'])
	
	#Setting the first value to be the initial cash amount.
	cash.cashinhand.ix[0] = initialCash
	
	index = 0
	
	for tradingDayIndex in range(num_tradingDays):
		if tradingDayIndex != 0:
			cash.cashinhand.ix[tradingDayIndex] = cash.cashinhand.ix[tradingDayIndex - 1] 
		else:
			cash.cashinhand.ix[tradingDayIndex] = initialCash
		
		for tradingOrder in ordersDataFrame.datetime:				
			if tradingOrder == ldt_timestamps[tradingDayIndex]:
				if ordersDataFrame.ordertype.ix[index] == 'Buy':
					toBuySymbol = ordersDataFrame.symbol.ix[index]
					toBuy = symbols.index(toBuySymbol)
					numShares = ordersDataFrame.volume.ix[index]
					priceForTheDay = closingPrices[tradingDayIndex, toBuy]
					cash.cashinhand.ix[tradingDayIndex] = cash.cashinhand.ix[tradingDayIndex] - (priceForTheDay * float(numShares))						
					holdings[toBuySymbol].ix[0] += int(numShares)
					
				elif ordersDataFrame.ordertype.ix[index] == 'Sell':
					toSellSymbol = ordersDataFrame.symbol.ix[index]
					toSell = symbols.index(toSellSymbol)
					numShares = ordersDataFrame.volume.ix[index]
					priceForTheDay = closingPrices[tradingDayIndex, toSell]
					cash.cashinhand.ix[tradingDayIndex] = cash.cashinhand.ix[tradingDayIndex] + (priceForTheDay * float(numShares))						
					holdings[toSellSymbol].ix[0] -= int(numShares)
				else:
					print "error"
				index+=1
		
		valueFromPortfolio = 0
		
		for symbol in symbols:			
			priceForTheDay = closingPrices[tradingDayIndex, symbols.index(symbol)]
			valueFromPortfolio += holdings[symbol].ix[0] * priceForTheDay

		valueFrame.valueOfPortfolio.ix[tradingDayIndex] = valueFromPortfolio + cash.cashinhand.ix[tradingDayIndex]
		
	valueFrame.index = ldt_timestamps
	return holdings, valueFrame, cash

def writeValuesIntoCSV(valuesFilename, valueFrame):
	file = open(valuesFilename, 'w')
	writer = csv.writer(file)
	
	for index in range(len(valueFrame)):
		writer.writerow([valueFrame.index[index].year, valueFrame.index[index].month, valueFrame.index[index].day ,int(round(valueFrame.valueOfPortfolio.ix[index], 0))])
		
def analyze(valueFrame):
	symbols = ['$SPX']
	
	dt_start = valueFrame.index[0]
	dt_end = valueFrame.index[len(valueFrame)-1]

	# All the adjustedClosingPrices fetched from NYSE within the range and for given symbols
	spxClosingPrices, ldt_timestamps = fetchNYSEData(dt_start, dt_end, symbols)
	
	num_tradingDays = len(ldt_timestamps)
	dailyrets = np.zeros((num_tradingDays, 2))
	cumrets = np.zeros((num_tradingDays, 2))
	
	# The first day prices of the equities
	arr_firstdayPrices = [spxClosingPrices[0,0],valueFrame.valueOfPortfolio.ix[0]]

	for i in range(num_tradingDays):
		if i != 0:
			dailyrets[i,0] = ((spxClosingPrices[i,0]/spxClosingPrices[i-1,0]) - 1)
			dailyrets[i,1] = ((valueFrame.valueOfPortfolio.ix[i]/valueFrame.valueOfPortfolio.ix[i-1]) -1 )

	for i in range(num_tradingDays):
		if i != 0:
			cumrets[i,0] = ((spxClosingPrices[i,0]/arr_firstdayPrices[0]))
			cumrets[i,1] = ((valueFrame.valueOfPortfolio.ix[i]/arr_firstdayPrices[1]))
	
	averageSPXDailyRets = np.average(dailyrets[:,0])
	averagePortfolioDailyRets = np.average(dailyrets[:,1])
	
	stddevSPX = np.std(dailyrets[:,0])
	stddevPort = np.std(dailyrets[:,1])
	
	totalSPXRet = cumrets[-1,0]
	totalPortRet = cumrets[-1,1]
	
	k = 252
	sharpeRatioSPX = (k**(1/2.0))*(averageSPXDailyRets/stddevSPX)
	sharpeRatioPort = (k**(1/2.0))*(averagePortfolioDailyRets/stddevPort)
	
	print "The final value of the portfolio using the sample file is --", valueFrame.valueOfPortfolio.ix[-1]
	
	print "Details of the Performance of the portfolio"

	print ""
	
	print "Data Range :", ldt_timestamps[0] ," to ", ldt_timestamps[-1]
	
	print ""
	
	print "Sharpe Ratio of Fund :", sharpeRatioPort
	print "Sharpe Ratio of $SPX :", sharpeRatioSPX
	print ""
	
	print "Total Return of Fund :", totalPortRet
	print "Total Return of $SPX :", totalSPXRet
	
	print ""
	
	print "Standard Deviation of Fund :", stddevPort
	print "Standard Deviation of $SPX :", stddevSPX
	
	print ""
	
	print "Average Daily Return of Fund :", averagePortfolioDailyRets
	print "Average Daily Return of $SPX :", averageSPXDailyRets

def main():
	print 'Argument List:', str(sys.argv)
	
	initialCash = sys.argv[1]
	ordersFilename = sys.argv[2]
	valuesFilename = sys.argv[3]
	
	# Reading the data from the file, and getting a NumPy matrix
	ordersDataFrame, symbols = readOrdersFileIntoDF(ordersFilename)
	holdings, valueFrame, cash = marketsim(initialCash, ordersDataFrame, symbols)
	
	writeValuesIntoCSV(valuesFilename, valueFrame)
	
	analyze(valueFrame)
	
if __name__ == '__main__':
	main()

	
"""
Testing -1

# Reading the data from the file, and getting a NumPy matrix
ordersFilename = "orders.csv"
valuesFilename = "values.csv"
initialCash = 1000000
ordersDataFrame, symbols = hw.readOrdersFileIntoDF(ordersFilename)
holdings, valueFrame, cash = hw.marketsim(initialCash, ordersDataFrame, symbols)
hw.writeValuesIntoCSV(valuesFilename, valueFrame)
hw.analyze(valueFrame)

OUTPUT
Data Range : 2011-01-10 16:00:00  to  2011-12-20 16:00:00

Sharpe Ratio of Fund : 1.21540462111
Sharpe Ratio of $SPX : 0.0183391412227

Total Return of Fund : 1.13386
Total Return of $SPX : 0.97759401457

Standard Deviation of Fund : 0.00717514512699
Standard Deviation of $SPX : 0.0149090969828

Average Daily Return of Fund : 0.000549352749569
Average Daily Return of $SPX : 1.72238432443e-05

"""

"""
Testing -1

# Reading the data from the file, and getting a NumPy matrix
ordersFilename = "orders2.csv"
valuesFilename = "values2.csv"
initialCash = 1000000
ordersDataFrame, symbols = hw.readOrdersFileIntoDF(ordersFilename)
holdings, valueFrame, cash = hw.marketsim(initialCash, ordersDataFrame, symbols)
hw.writeValuesIntoCSV(valuesFilename, valueFrame)
hw.analyze(valueFrame)

OUTPUT
Data Range : 2011-01-14 16:00:00  to  2011-12-14 16:00:00

Sharpe Ratio of Fund : 0.788985460132
Sharpe Ratio of $SPX : -0.177204632551

Total Return of Fund : 1.0787526
Total Return of $SPX : 0.937041848381

Standard Deviation of Fund : 0.00708034136287
Standard Deviation of $SPX : 0.0149914504972

Average Daily Return of Fund : 0.000351902965125
Average Daily Return of $SPX : -0.000167347202139
"""