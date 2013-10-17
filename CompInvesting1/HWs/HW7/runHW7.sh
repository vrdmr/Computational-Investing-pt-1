#!/bin/bash

python bollingerEvents.py 2008,1,1 2009,12,31 sp5002012 eventschart.pdf 20
python marketsim.py 100000 orders.csv values.csv