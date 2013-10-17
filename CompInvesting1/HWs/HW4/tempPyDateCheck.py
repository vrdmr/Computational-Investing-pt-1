import datetime as dt
import sys

if __name__ == '__main__':
	print 'Argument List:', str(sys.argv)
	argssplit = sys.argv[1].split(',')
	print "argssplit", argssplit
	date = dt.datetime(int(argssplit[0]),int(argssplit[1]), int(argssplit[2]), 16, 00, 00)
	print "date", date
