#!/usr/bin/env python

import time 
import urllib2
from bs4 import BeautifulSoup, SoupStrainer
import json
from time import sleep
from datetime import date
from lxml import etree
from xml.etree.ElementTree import fromstring
import re

###################################################################################################

import smtplib
import urllib2
import shutil
import os
from os.path import expanduser
import subprocess
from subprocess import call


#
#		scrapeReddit
#
#	scrapeReddit scrapes reddit for vote data.
#
#	-
#	jbsilva
#



####  Functions
###################################################################################################

def fetchSite(url) :
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

def getCommentsLinks(siteRaw):
	soup = BeautifulSoup(siteRaw)
	commentsLinks = []
	for link in soup.find_all('a'):
		if link.get('href') is not None: 	
			if "comments" in link.text: 
				commentsLinks.append(link.get('href'))
	return commentsLinks
					
def getNextLink(siteRaw):
	soup = BeautifulSoup(siteRaw)
	for link in soup.find_all('a'):
		if link.get('href') is not None: 	
			if ("next" in link.text) and ("count=" in link.get('href')): 
				return link.get('href')
	return None

def getLinkScore(soup):
	soupSite = BeautifulSoup(soup)
	for link in soupSite.find_all('div', {'class': 'score'}):
		for l in soupSite.find_all('span', {'class': 'number'}):
			return int(l.text.replace(",",""))

def getPointsLikesDelta(siteRed):
	soup = BeautifulSoup(siteRed); count = 0; pointsDat = []; curr = 0;
	minPoints = 5; minThresh = 100; searchingThread = True;
	for link in soup.find_all( 'span', {'class': 'score likes'} ):
		# print link.text
		points = re.sub('[^0-9.]','', str(link.text))		
		if count is 1:
			countLast = float(points);				
		count = count + 1;
		if ( count % 2 ) is 0 and (count > 1) and ( float(points) > 0 ):
			pointsDat.append( float(points) / countLast )
			countLast =	float(points);			
	return pointsDat	

def getPointsLikesDecay(siteRed):
	soup = BeautifulSoup(siteRed); count = 0; pointsDat = []; placeDat = []; curr = 0;
	minPoints = 5; minThresh = 100; searchingThread = True;
	for link in soup.find_all( 'span', {'class': 'score likes'} ):
		# print link.text
		points = re.sub('[^0-9.]','', str(link.text))
		if searchingThread and ( int(points) >= minThresh ):
			searchingThread = False;
		if searchingThread:
			continue;		
		if count is 0:
			countMax = float(points);				
		count = count + 1;
		if ( int(points) < minPoints ):
			count = 0; searchingThread = True;
		else:
			if ( count % 2 ) is 0:
				pointsDat.append( [ int(count/2.0) , (float(points) / countMax) , countMax , float(points) ])
	return pointsDat	

def getPointsLikesDecayDel(siteRed):
	soup = BeautifulSoup(siteRed); count = 0; pointsDat = []; curr = 0;
	minPoints = 5; minThresh = 100; searchingThread = True;
	for link in soup.find_all( 'span', {'class': 'score likes'} ):
		# print link.text
		points = re.sub('[^0-9.]','', str(link.text))
		if searchingThread and ( int(points) >= minThresh ):
			searchingThread = False;
		if searchingThread:
			continue;		
		if count is 1:
			countLast = float(points);				
		count = count + 1;
		if ( int(points) < minPoints ):
			count = 0; searchingThread = True;
		else:
			if ( count % 2 ) is 0 and (count > 1):
				pointsDat.append( float(points) / countLast )
				countLast =	float(points);			
	return pointsDat	


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


###########################################################################################

#### Main Loop


urlIn = "http://www.reddit.com/"
currentSite = urlIn

# Parse data only from reddit articles over 1000 votes
THRESH_VOTES = 1000
dataOutFile = "/home/jbsilva/Data/"

# Parse data only 5 pages in from front page
for i in range(5):
	try:
		commentsSites = getCommentsLinks(fetchSite(currentSite))
		for siteIn in commentsSites:
			print siteIn		
			if "http:" in siteIn:	
				try:
					siteF =	fetchSite(siteIn)	
					if THRESH_VOTES > getLinkScore(siteF):
						continue;	
					data = getPointsLikesDelta(siteF); 
					saveData(data,dataOutFile+"redditDelta.csv",True, True)
					data = getPointsLikesDecay(siteF);
					saveData(data,dataOutFile+"redditDecay.csv",True, False) 
					data = getPointsLikesDecayDel(siteF); 
					saveData(data,dataOutFile+"redditDecayDel.csv",True, True)
				except AttributeError:
					continue;
		currentSite = getNextLink(currentSite)
	except AttributeError:
		continue;


