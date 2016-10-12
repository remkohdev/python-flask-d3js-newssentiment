import http.client
import csv
from datetime import datetime
import json
from mymodule import mycloudant

apikey = "<your-apikey>"

def GetNews(searchterm=None, outputMode="json", startdate=None, enddate=None, count="5", returnfields="enriched.url.url"): 
	conn = http.client.HTTPSConnection("gateway-a.watsonplatform.net")
	headers = {
    	'content-type': "application/json"
	}
	endpoint = ('/calls/data/GetNews?outputMode={0}&start={1}&end={2}&count={3}&q.enriched.url.enrichedTitle.keywords.keyword.text={4}&return={5}&apikey={6}').format(outputMode, startdate, enddate, count, searchterm, returnfields, apikey)
	print("GetNews API. endpoint: %s", endpoint)
	conn.request("GET", endpoint, headers=headers)
	res = conn.getresponse()
	logMsg = ("GetNews API. response: status[{0}], msg[{1}], reason[{2}]").format(res.status, res.msg, res.reason)
	print(logMsg)
	# HTTPResponse.read returns bytes[]
	data = res.read()
	responseStr = data.decode("utf-8")
	return responseStr


'''
1. the GetNews Alchemy API takes date formats in UTC timezone in seconds,
it also has convenience methods, in the form of 'now-1M' for the last month,
'now-1d' for yesterday, so I here convert any datetime to 'now-{0}d',
so that start and end could be e.g. 'now-30d' to 'now-0d'.
'''
def FormatDate(dateStr=None):
	now = datetime.now()
	date1 = datetime.strptime(dateStr, '%Y-%m-%d')
	delta1 = now-date1
	date1 = ("now-{0}d").format(delta1.days)
	return date1

'''
1. d3js takes an array of assiociative arrays as input, for convenience
I prepare that arrayon the server. 
2. I create an array of unique days to be visualized in d3js and 
have to order the set, cause d3js create a graph by drawing a line from
point to point, and i want to prevent the line to go back and forth,
creating a very messy graph.
'''
def ParseNews(articles=None, startdate1=None, enddate1=None):
	#print(("=====Articles: {0}").format(articles))
	status1 = ""
	startdate1 = datetime.strptime(startdate1, '%Y-%m-%d')
	enddate1 = datetime.strptime(enddate1, '%Y-%m-%d')
	if (articles==None or articles==""):
		logMsg = "GetNews API Error: no response."
		print(logMsg)
		return logMsg
	else:
		logMsg = ("GetNews API response: {0}").format(articles)
		#print(logMsg)
		articlesJson = json.loads(articles)
		status1 = articlesJson['status']
		if status1=='ERROR':
			statusInfo = articlesJson['statusInfo']
			logMsg = ('GetNews API Error. StatusInfo: {0}').format(statusInfo)
			print(logMsg)
			return logMsg
		elif status1=='OK':
			logMsg = "GetNews API status: OK"
			#print(logMsg)

	# Here everything is OK
	mycloudant.SaveNews(articles)
	sentimentList = []
	docs = articlesJson['result']['docs']
	for doc in docs:
		enrichedURL = doc['source']['enriched']['url']
		# Get publicationDate
		publicationDate = enrichedURL['publicationDate']['date']
		sentiment = enrichedURL['docSentiment']['score']
		# construct data array for d3js, append row
		sentimentRow = {"publicationDate": publicationDate, "sentiment": sentiment}
		sentimentList.append(sentimentRow)

	#get unique publicationDates
	uniqueSentimentList=[]
	uniqueDates = set()
	for dic in sentimentList:
		pubdate1 = dic['publicationDate']
		pubdate1 = datetime.strptime(pubdate1, '%Y%m%dT%H%M%S')
		# make sure publicationdates are within range
		if (startdate1 < pubdate1) and (pubdate1 < enddate1):
			# set times for all dates to zero for Ymd comparison
			pubdate1 = pubdate1.replace(hour=0, minute=0, second=0)
			# only add the date if new date
			if pubdate1 not in uniqueDates:
				uniqueDates.add(pubdate1)
	uniqueDates = sorted(uniqueDates)
	
	# loop through the uniqueDates and calculate averages for duplicates by date
	i1 = 0
	for uniqueDate in uniqueDates:
		i1+=1
		sentiments = 0
		i=0
		for row in sentimentList:
			rowDate = datetime.strptime(row['publicationDate'], '%Y%m%dT%H%M%S')
			# set times for all dates to zero for Ymd comparison
			rowDate = rowDate.replace(hour=0, minute=0, second=0)
			if rowDate==uniqueDate:
				i+=1
				sentiments += row['sentiment']
		avgSentiment = sentiments/i
		shortUniqueDate = ("{0}-{1}-{2}").format(uniqueDate.strftime("%Y"), uniqueDate.strftime("%m"), uniqueDate.strftime("%d"))
		uniqueSentimentRow = {"publicationDate": shortUniqueDate, "sentiment": avgSentiment}
		uniqueSentimentList.append(uniqueSentimentRow)

	return uniqueSentimentList


