import numpy as np
import sys
import os
import time 
import urllib2
import re
import random
import csv
from bs4 import BeautifulSoup, SoupStrainer
from time import sleep
from datetime import date
from sys import maxint as MAXINT

# Column for Richter Magnitude data
MAG_COL = 4;

#
#	USGS Download
#
# 	Uses USGS API to get earthquake data for various locations such as the LA county area.
#
#	-
#	jbsilva

def fetchSite(url) :
	time.sleep(0.0+random.random()*2.0)
	BAD_RETRIEVE = 0.0
	lstSent = BAD_RETRIEVE
	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
	headers = { 'User-Agent' : user_agent }
	r = urllib2.Request(url, headers=headers)
	try :
		web_page = urllib2.urlopen(r).read()
	except urllib2.HTTPError :
		print("HTTPERROR!")
	except urllib2.URLError :
		print("URLERROR!")
	return web_page

def downloadDataOK(monthS,yearS,monthE,yearE,minMag):
	query = "http://comcat.cr.usgs.gov/fdsnws/event/1/query?starttime="+str(yearS)+"-"+str(monthS)+"-07+00%3A00%3A00&endtime="+str(yearE)+"-"+str(monthE)+"-27+23%3A59%3A59&minmagnitude="+str(minMag)+"&format=csv&latitude=35.65&longitude=-97.55&minradiuskm=0&maxradiuskm=200&kmlcolorby=age&orderby=time"
	dataIn = fetchSite(query);
	filename = "OK/earthquake-"+str(monthS)+"-"+str(yearS)+"--"+str(monthE)+"-"+str(yearE)+"-minMag-"+str(minMag)+".csv"
	saveData(dataIn,filename)

def downloadDataLosAngeles(monthS,yearS,monthE,yearE,minMag):
	query = "http://comcat.cr.usgs.gov/fdsnws/event/1/query?starttime="+str(yearS)+"-"+str(monthS)+"-07+00%3A00%3A00&endtime="+str(yearE)+"-"+str(monthE)+"-27+23%3A59%3A59&minmagnitude="+str(minMag)+"&format=csv&latitude=34.05&longitude=-118.25&minradiuskm=0&maxradiuskm=250&kmlcolorby=age&orderby=time"
	dataIn = fetchSite(query);
	filename = "LosAngeles/earthquake-"+str(monthS)+"-"+str(yearS)+"--"+str(monthE)+"-"+str(yearE)+"-minMag-"+str(minMag)+".csv"
	saveData(dataIn,filename)

def downloadDataUS(monthS,yearS,monthE,yearE,minMag):
	query = "http://comcat.cr.usgs.gov/fdsnws/event/1/query?starttime="+str(yearS)+"-"+str(monthS)+"-07+00%3A00%3A00&endtime="+str(yearE)+"-"+str(monthE)+"-27+23%3A59%3A59&minmagnitude="+str(minMag)+"&format=csv&latitude=41.23&longitude=-98.42&minradiuskm=0&maxradiuskm=2200&kmlcolorby=age&orderby=time"
	dataIn = fetchSite(query);
	filename = "US/earthquake-"+str(monthS)+"-"+str(yearS)+"--"+str(monthE)+"-"+str(yearE)+"-minMag-"+str(minMag)+".csv"
	saveData(dataIn,filename)


def downloadDataEarth(monthS,yearS,monthE,yearE,minMag):
	query = "http://comcat.cr.usgs.gov/fdsnws/event/1/query?starttime="+str(yearS)+"-"+str(monthS)+"-07+00%3A00%3A00&endtime="+str(yearE)+"-"+str(monthE)+"-27+23%3A59%3A59&minmagnitude="+str(minMag)+"&format=csv&orderby=time"
	dataIn = fetchSite(query);
	filename = "Earth/earthquake-"+str(monthS)+"-"+str(yearS)+"--"+str(monthE)+"-"+str(yearE)+"-minMag-"+str(minMag)+".csv"
	saveData(dataIn,filename)

def saveData(data,filename):	
	text_file = open(filename, "w")
	text_file.write(data)
	text_file.close()

def getLargeDataOK(yearS,yearE):
	yearsRange = yearE-yearS;
	for year in range(yearsRange):
		yearNow = yearS+year;
		for u in range(2):
			m = 6*u+1;
			downloadDataOK(m,yearNow,m+5,yearNow,1);

def getLargeDataLA(yearS,yearE):
	yearsRange = yearE-yearS;
	for year in range(yearsRange):
		yearNow = yearS+year;
		for u in range(2):
			m = 6*u+1;
			downloadDataLosAngeles(m,yearNow,m+5,yearNow,1);

def getLargeDataUS(yearS,yearE):
	yearsRange = yearE-yearS;
	for year in range(yearsRange):
		yearNow = yearS+year;
		for u in range(6):
			m = 2*u+1;
			downloadDataUS(m,yearNow,m+1,yearNow,1);

def getLargeDataEarth(yearS,yearE):
	yearsRange = yearE-yearS;
	for year in range(yearsRange):
		yearNow = yearS+year;
		for u in range(6):
			m = 2*u+1;
			downloadDataEarth(m,yearNow,m+1,yearNow,1);

def appendFileData(fileIn,dataAll):
	appended = 0;
	with open(fileIn, 'rb') as f:
		reader = csv.reader(f)
		for row in reader:
			if not row[MAG_COL] == "mag":
				dataAll.append(row[MAG_COL]);
				appended +=  1
	if appended > 0:
		return [False,appended]
	else:
		return [True,0]
	
def gatherData(direct):
	dirList=os.listdir(direct)
	magAll = np.empty(1); dataAll = []; yearF = 0; yearI = 3000
	for fileIn in dirList:	
		[emptyFile,num] = appendFileData(direct+fileIn,dataAll)
		yearN = int(fileIn.split("-")[2])
		if ( yearN > yearF ) and not emptyFile:
			yearF = int(fileIn.split("-")[2])
		if ( yearN < yearI ) and not emptyFile:
			yearI = int(fileIn.split("-")[2])
	sp = direct.split("/")
	direct = sp[len(sp)-2]		
	saveDataMag(dataAll,"all"+str(direct)+"-"+str(yearI)+"-"+str(yearF)+".csv",False,True)

def updateWithEvents(fileIn,yearC,dataAll):
	newYear = True;
	appended = 0;
	with open(fileIn, 'rb') as f:
		reader = csv.reader(f)
		for row in reader:
			if not row[MAG_COL] == "mag":
				appended +=  1
	events = appended
	print "0020    ",events,"   ",len(dataAll)
	if events < 1:
		return [True, dataAll]	

	print "0000    ",events,"   ",len(dataAll)
	newYear = True	
	for yearDat in dataAll:
		print yearDat
		if yearDat[0] == yearC:
			yearDat[1] += events
			newYear = False;
			break;
	if newYear:
		dataAll.append([yearC,events])
	return [False, dataAll]

def gatherDataYear(direct):
	dirList=os.listdir(direct)
	dataAll = []; yearF = 0; yearI = 3000
	for fileIn in dirList:	
		yearN = int(fileIn.split("-")[2])
		[emptyFile,dataAll] = updateWithEvents(direct+fileIn,yearN,dataAll)
		if ( yearN > yearF ) and not emptyFile:
			yearF = int(fileIn.split("-")[2])
		if ( yearN < yearI ) and not emptyFile:
			yearI = int(fileIn.split("-")[2])
	sp = direct.split("/")
	direct = sp[len(sp)-2]		
	print dataAll	
	saveDataMag(dataAll,"allYear"+str(direct)+"-"+str(yearI)+"-"+str(yearF)+".csv",False,False)

def saveDataMag(dataOut,filename,append, singleCol):
	try:
		with open(filename): pass
	except IOError:
		print 'Need to make new file.'
		file = open(filename, 'w')
		file.write('')
		file.close()
	if append:
		f = open(filename, 'a+')
	else:
		f = open(filename, 'w+')
	if not singleCol:
		for data in dataOut:
			out = ""; 
			initCols = True
			for cols in data:
				if initCols:			
					out = str(cols); initCols = False;
				else:
					out = out +","+ str(cols)
			out = out + "\n"
			f.write(out)
	else:
		out = ""; 
		initCols = True
		for data in dataOut:
			if initCols:			
				out = str(data); initCols = False;
			else:
				out = out +","+ str(data)
		out = out + "\n"
		f.write(out)


#getLargeDataUS(1970,2020);
#getLargeDataEarth(1970,2020);



