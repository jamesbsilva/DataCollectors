#!/usr/bin/env python

###################################################################################################

####  scrapeGameScores.py 
	
#	Scrapes WNBA game data from WNBA site using beautiful soup and saves it in csv format.
#
#	-
#	jbsilva
#
###################################################################################################


import numpy as np
import sys
import os
import time 
import urllib2
import re
import random
from bs4 import BeautifulSoup, SoupStrainer
from time import sleep
from datetime import date
from sys import maxint as MAXINT
import csv

###################################################################################################

####  Functions

###################################################################################################

TRANSFER_YEAR = 2005
TRANSFER_YEAR2 = 2008
teamsWNBA = ['Atlanta Dream', 'Chicago Sky', 'Connecticut Sun', 'Orlando Miracle', 'Indiana Fever', 'Los Angeles Sparks', 'Minnesota Lynx', 'New York Liberty', 'Phoenix Mercury', 'San Antonio Silver Stars', 'Utah Starzz', 'Seattle Storm', 'Tulsa Shock', 'Detroit Shock', 'Washington Mystics', 'Charlotte Sting', 'Cleveland Rockers', 'Houston Comets', 'Miami Sol', 'Portland Fire', 'Sacramento Monarchs']

def saveData(dataOut,filename,append, singleCol):
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

def getDayOfYear(month,day):
	m = month; d = day;
	m = m - 1
	while ( m > 0 ):
		if m == 2:
			d += 29
		elif (m == 4) or (m == 6) or (m == 9) or (m == 11):
			d += 30
		else:
			d += 31
		m = m - 1
	return d

def getWNBAScores(year):
	Months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
	for month in Months:
		try:
			dat = []
			if year > TRANSFER_YEAR2:
				datOut = getNewWNBA2(year,month)
			elif (year > TRANSFER_YEAR) and (year <= TRANSFER_YEAR2):
				datOut = getNewWNBA(year,month)
			else:
				datOut = getOldWNBA(year,month)
			saveData(datOut,"WNBAScores.csv",True, False)
		except urllib2.HTTPError:
			continue;
		except AttributeError:
			print "Problem With",str(year),"   ",str(month)
			continue;

def getWNBATeams():
	fileIn = "AllWNBATeams.csv"; teamsAll = []; NameRow = 0;
	with open(fileIn, 'rb') as csvfile:
		read = csv.reader(csvfile, delimiter=',')
		headerline = read.next();
		for row in read:
			teamsAll.append(row[NameRow]);
	return teamsAll

def getWNBATeamIndex(teamName):
	teamName = teamName.replace("if necessary","");
	teamName = teamName.replace("First Round","");
	teamName = teamName.strip();
	for team in teamsWNBA:
		if teamName in team:
			return teamsWNBA.index(team)
	print "NOT FOUND : ",teamName
	return -1

def reformatData(dataIn,year,month):
	Week =["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
	Months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
	monthOut = Months.index(month); dayOut = dataIn[1] 
	dayY = getDayOfYear(monthOut+1,int(dayOut))
	curr = 2
	homeTeam = ""
	while not ( ("vs" in dataIn[curr]) or ("@" in dataIn[curr]) ) :
		homeTeam = homeTeam +" " + dataIn[curr]
		curr += 1
	if "vs" in dataIn[curr]:
		home = 0;
	else:
		home = 1;
	curr += 1
	awayTeam = ""
	while not ( ("-" in dataIn[curr]) ) :
		awayTeam = awayTeam +" "+ dataIn[curr]
		curr += 1
	homeTeam = homeTeam.strip(); awayTeam = awayTeam.strip();
	scr = dataIn[curr].split("-")
	hscr = scr[0]; ascr = scr[1].replace("(OT)","");
	return [dayY,monthOut,dayOut,getWNBATeamIndex(homeTeam),getWNBATeamIndex(awayTeam),home,hscr,ascr,year]

	 
def getOldWNBA(year,month):
	Week =["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
	time.sleep(0.0+random.random()*2.0)
	url = "http://www.wnba.com/schedules/"+str(year)+"_game_schedule/"+str(month)+".html"
	response = urllib2.urlopen(url)
	page_source = response.read()
	soup = BeautifulSoup(page_source)
	table = soup.find("table",  {'class': 'gScGTable'})
	table_subset = table.findAll("tr")
	lastDate=""; lastDay=""; datAll = []
	for row in range(len(table_subset)):
		if row < 1:
			continue;
		cells = table_subset[row].findAll("td")
		table_data = []; datIn = cells[0].text.split()
		dateGood = True; curr = 0;
		if len(datIn) < 1:	
			dateGood = False;
		if not dateGood:
			table_data.append(lastDay);
			table_data.append(lastDate);
		else:
			table_data.append(datIn[0]);
			table_data.append(datIn[1]);
			lastDay = (datIn[0]); lastDate = (datIn[1]);
			curr += 2
		for u in range(2):
			c = cells[u+1]
			datIn = c.text.split()
			for dat  in datIn:
				if ("Preseason" in dat) or ("Semi" in dat) or ("Finals" in dat) or ("Conf." in dat) or ("WNBA" in dat):
					continue;
				table_data.append(dat);
		dataReformed = reformatData(table_data,year,month)
		badData = False
		if dataReformed[3]  == (-1):
			badData = True;
		if dataReformed[4] == (-1):
			badData = True;
		if not badData:
			datAll.append(dataReformed)
	return datAll

def getNewWNBA(year,month):
	Week =["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
	time.sleep(0.0+random.random()*2.0)
	url = "http://www.wnba.com/schedules/"+str(year)+"_game_schedule/"+str(month)+".html"
	response = urllib2.urlopen(url)
	page_source = response.read()
	soup = BeautifulSoup(page_source)
	table = soup.find("table",  {'class': 'genSchedTable past'})
	table_subset = table.findAll("tr")
	lastDate=""; lastDay=""; datAll = []
	for row in range(len(table_subset)):
		if row < 1:
			continue;
		cells = table_subset[row].findAll("td")
		checkGoodRow = False
		for c in cells:
			if "-" in c.text:
				checkGoodRow = True;
		if not checkGoodRow:
			continue

		table_data = []; datIn = cells[0].text.split()
		dateGood = True; curr = 0;
		if len(datIn) < 1:	
			dateGood = False;
		if not dateGood:
			table_data.append(lastDay);
			table_data.append(lastDate);
		else:
			table_data.append(datIn[0]);
			table_data.append(datIn[1]);
			lastDay = (datIn[0]); lastDate = (datIn[1]);
			curr += 2
		for u in range(2):
			c = cells[u+1]
			datIn = c.text.split()
			for dat  in datIn:
				if ("Preseason" in dat) or ("Semi" in dat) or ("Finals" in dat) or ("Conf." in dat) or ("WNBA" in dat):
					continue;
				table_data.append(dat);
		dataReformed = reformatData(table_data,year,month)
		badData = False
		if dataReformed[3]  == (-1):
			badData = True;
		if dataReformed[4] == (-1):
			badData = True;
		if not badData:
			datAll.append(dataReformed)
	return datAll

def getNewWNBA2(year,month):
	Week =["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
	time.sleep(0.0+random.random()*2.0)
	url = "http://www.wnba.com/schedules/"+str(year)+"_game_schedule/"+str(month)+".html"
	response = urllib2.urlopen(url)
	page_source = response.read()
	soup = BeautifulSoup(page_source)
	table = soup.find("table",  {'class': 'past schedule'})
	table_subset = table.findAll("tr")
	lastDate=""; lastDay=""; datAll = []
	for row in range(len(table_subset)):
		if row < 1:
			continue;
		cells = table_subset[row].findAll("td")
		#print cells
		checkGoodRow = False
		for c in cells:
			if "-" in c.text:
				checkGoodRow = True;
		if not checkGoodRow:
			continue
		table_data = []; datIn = cells[0].text.split()
		dateGood = True; curr = 0;
		if len(datIn) < 1:	
			dateGood = False;
		if not dateGood:
			table_data.append(lastDay);
			table_data.append(lastDate);
		else:
			table_data.append(datIn[0]);
			table_data.append(datIn[1]);
			lastDay = (datIn[0]); lastDate = (datIn[1]);
			curr += 2
		for u in range(2):
			c = cells[u+1]
			datIn = c.text.split()
			for dat  in datIn:
				if ("Preseason" in dat) or ("Semi" in dat) or ("Finals" in dat) or ("Conf." in dat) or ("WNBA" in dat):
					continue;
				table_data.append(dat);
		dataReformed = reformatData(table_data,year,month)
		badData = False
		if dataReformed[3]  == (-1):
			badData = True;
		if dataReformed[4] == (-1):
			badData = True;
		if not badData:
			datAll.append(dataReformed)
	return datAll


startYear = 2001;
endYear = 2014;
print "Getting NBA Data from "+str(startYear)+"   to  "+str(endYear)
for u in range(endYear-startYear):
	yearIn = startYear + u 
	print "Working on year : ",yearIn
	getWNBAScores(yearIn)

#print getWNBATeams()
