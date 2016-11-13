#!/usr/bin/env python
import csv

def writeRes(outFile,dataList):
	'''
	This writes a line of data, provided in list form (i.e., [a,b,c,...])
	to a csv file.
	'''
	oFile = open(outFile,'ab')
	fWriter = csv.writer(oFile,delimiter=',')
	fWriter.writerow(dataList)
	oFile.close()
