#!/bin/bash

python event.py 2008,1,1 2009,12,31 sp5002012 eventschart.pdf
python marketsim.py 50000 orders.csv values.csv
