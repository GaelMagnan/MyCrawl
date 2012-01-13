#! /usr/bin/env python
import csv
import argparse
import signal
import sys
import socket
from httplib import InvalidURL
from httplib import BadStatusLine
from urllib2 import urlopen, URLError
from HtmlParse import toSite
from HtmlParse import extractlinks
from HtmlParse import getPreparedHtml
from HtmlParse import getMatriceWords
from Graph import saveGraphs
from Graph import timedSave
from Data import Page
from Data import Site
from Data import AllPages
from HtmlParse import stopWords

parser = argparse.ArgumentParser(description='Crawl from a list of websites and display a graph of the visited pages and sites.')
parser.add_argument('url', nargs='+',action='append',
                   help='a starting point for the crawler')
parser.add_argument('--bl', dest='blackList', action='store',nargs='?',
                   help='blackList file (csv)')
parser.add_argument('--wc', dest='wordCorpus', action='store',nargs='?',
                   help='word corpus file (csv)')
parser.add_argument('--d', dest='degree', type=int, action='store',nargs='?', default=5,
                   help='minimum degree for relevance')
parser.add_argument('--dt', dest='degreeTotal', type=int, action='store',nargs='?', default=10,
                   help='minimum added degrees for relevance')
parser.add_argument('--st', dest='sizeTop', type=int, action='store',nargs='?', default=5,
                   help='size of the best words for relevance')
parser.add_argument('--swf', dest='stopWords', action='store',nargs='?', default="stopWords.csv",
                   help='stopWords file (csv)')
parser.add_argument('--to', dest='timeout', type=int, action='store',nargs='?', default=10,
                   help='timeout time in seconds')
parser.add_argument('--tex', dest='timeEx', type=int, action='store',nargs='?', default=-1,
                   help='max time of execution in seconds')
parser.add_argument('--ts', dest='timeSave', type=int, action='store',nargs='?', default=-1,
                   help='time between each generation of a graph in seconds')
parser.add_argument('--o', dest='outputFile', action='store',nargs='?',default="graph.gexf",
                   help='output file (gexf)')
args = parser.parse_args()

bannedList=set()
openList=[]
timeExecution = args.timeEx
timeSave = args.timeSave
wordCorpus=[]
degree=args.degree
degreeTotal=args.degreeTotal
Page.sizeTop=args.sizeTop

def handler(signum, frame):
	print 'saved by user'
	saveGraphs(args.outputFile)

def handlerAlarm(signum, frame): 
	global timeSave,timeRemaining,timeExecution,nbrSave,args
	if timeSave!=-1:
		print 'saved nbr:'+str(nbrSave)
		timedSave(args.outputFile,nbrSave)
		nbrSave=nbrSave+1
		if timeExecution!=-1:
			if (nbrSave+1)*timeSave>timeExecution:
				timeRemaining=timeExecution-nbrSave*timeSave
				timeSave=-1
				signal.alarm(timeRemaining)
			else:
				signal.alarm(timeSave)
		else:
			signal.alarm(timeSave)
	else:
		print 'Time over:'
		saveGraphs(args.outputFile)
		sys.exit(0)

timeout = args.timeout
# timeout of a connection in seconds
socket.setdefaulttimeout(timeout)

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGALRM, handlerAlarm)
nbrSave=0
if timeSave !=-1 and (timeSave<timeExecution or timeExecution==-1):
	signal.alarm(timeSave)
else:
	if timeExecution !=-1:
		signal.alarm(timeExecution)

for tmp in args.url:
	for add in tmp:
		page=Page(add)
		openList.append(page)

if args.blackList!=None:
	csvfile = open(args.blackList)
	dialect = csv.Sniffer().sniff(csvfile.read(1024))
	csvfile.seek(0)
	reader = csv.reader(csvfile, dialect)
	for row in reader:
		if row != []:
			tmp=row[0]
			if not tmp.startswith('http://') and not tmp.startswith('https://'):
				if not tmp.startswith('/') and not tmp.startswith('mailto:') and not tmp.startswith('#'):
					tmp='http://'+tmp
				else:
					continue
				bannedList.add(toSite(tmp))

if args.wordCorpus!=None:
	csvfile = open(args.wordCorpus)
	dialect = csv.Sniffer().sniff(csvfile.read(1024))
	csvfile.seek(0)
	reader = csv.reader(csvfile, dialect)
	for row in reader:
		if row != []:
			tmp=row[0]
            		tmp = tmp.lower()
			wordCorpus.append(tmp)
	Page.corpus=wordCorpus

if args.stopWords!=None:
	csvfile = open(args.stopWords)
	dialect = csv.Sniffer().sniff(csvfile.read(1024))
	csvfile.seek(0)
	reader = csv.reader(csvfile, dialect)
	for row in reader:
		if row != []:
			lang=row[0]
			word=row[1].lower()
			if lang not in stopWords:
				stopWords[lang]={}
			stopWords[lang][word]=True

def addFils(page, stack):
	for url in stack:
		site=toSite(url)
		if site in bannedList:
			continue
		if url not in AllPages:
			page.addFils(url)
			openList.append(AllPages[url])
		else:
			page.addFils(url)
			tmp=AllPages[url]
			if not tmp.errorDL and not tmp.errorRead and tmp.notRelevent:
				if tmp.checkRelevance(page,degree,degreeTotal):
					tmp.notRelevent=False
					tmp.deadEnd=False
					addFils(tmp,tmp.FilsURL)
					tmp.FilsURL=[]

	

# loop on each line
while len(openList)>0:
	page=openList.pop(0)
	page.handled=True
	try:
		response=urlopen(page.URL)
		encoding = response.headers.getparam('charset')
		if encoding!=None:
			the_page = response.read().decode(encoding)
		else:		
			the_page = response.read()
		try:
			soup=getPreparedHtml(the_page)
			stack=extractlinks(soup)
			page.setWords(getMatriceWords(soup))
			if not page.checkCorpusRelevance():
				if not page.checkAllRelevance(degree,degreeTotal):
					page.deadEnd=True
					page.notRelevent=True
					page.FilsURL=stack
					continue
			else:
				page.relevantByCorpus=True
			page.cleanFathers()		
			addFils(page, stack)						
		except UnicodeDecodeError,de:
			page.errorRead=True
			page.deadEnd=True
			print de
			print 'on:'+page.URL
		except UnicodeEncodeError,ee:
			page.errorRead=True
			page.deadEnd=True
			print ee
			print 'on:'+page.URL
	except TypeError,te:
		page.errorRead=True
		page.deadEnd=True
		print te
		print 'on:'+page.URL
	except UnicodeError,ue:
		page.errorRead=True
		page.deadEnd=True
		print ue
		print 'on:'+page.URL
	except UnicodeDecodeError,de:
		page.errorRead=true
		page.deadEnd=true
		print de
		print 'on:'+page.URL
	except UnicodeEncodeError,ee:
		page.errorRead=True
		page.deadEnd=True
		print ee
		print 'on:'+page.URL
	except BadStatusLine,bs:
		page.errorDL=True
		page.deadEnd=True
		print bs
		print 'on:'+page.URL
	except InvalidURL, ie:
		page.errorDL=True
		page.deadEnd=True
		print e
		print 'on:'+page.URL
	except URLError,e:
		page.errorDL=True
		page.deadEnd=True
		print e
		print 'on:'+page.URL
	except socket.error,se:
		page.errorDL=True
		page.deadEnd=True
		print se
		print 'on:'+page.URL

saveGraphs(args.outputFile)


