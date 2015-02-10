#!/usr/bin/env python

import sys;
import urllib2;
import os;

def createDirs(dirs):
    currSub = ""
    for d in dirs:
        currSub = currSub+d+"/";
        if not os.path.exists(currSub):
            os.makedirs(currSub);

#http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
def parseFilename(filename):
    #convertChar = {"%5d":"]","%5b":"[","%20":"_","%2f":"/","%c3%b1":"n","%c3%":"i","%28":"(","%29":")"};
    convertChar = {"%5d":"]","%5b":"[","%20":" ","%2f":"/","%c3%b1":"n","%c3%":"i","%28":"(","%29":")"};
    for k in convertChar.keys():
        filename = filename.replace(k,convertChar[k]);
    splFile = filename.split("/");
    filename = "/".join(splFile[:])
    createDirs(splFile[:-1])
    return filename

def downloadURL(url):
    file_name = url.split('/')[-1]
    file_name = parseFilename(file_name)
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info(); scaleFile = 1000000;
    file_size = int(meta.getheaders("Content-Length")[0])/scaleFile
    print "Downloading: %s MBytes: %s" % (file_name, file_size)

    file_size_dl = 0; block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d Mb [%3.2f%%]" % (file_size_dl/scaleFile, (file_size_dl/scaleFile) * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()

def getLinks(linksfile):
    linksOut = [];
    with open(linksfile) as f:
        lines = f.readlines()
        for line in lines:
            linksOut.append(line.strip());
    return linksOut

if len(sys.argv) < 2:
    print "need input links file";
else:
    linksOut = getLinks(sys.argv[1]);
    print "Links File : ",sys.argv[1]
    for link in linksOut:
        downloadURL(link);

