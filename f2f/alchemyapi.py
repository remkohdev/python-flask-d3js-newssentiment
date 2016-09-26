import http.client
import csv
from datetime import datetime
import json
from f2f import mycloudantdb

apikey = ""

def GetNews(searchterm=None, outputMode="json", startdate=None, enddate=None, count="5", returnfields="enriched.url.url"): 
	conn = http.client.HTTPSConnection("gateway-a.watsonplatform.net")
	headers = {
    	'content-type': "application/json",
    	'cache-control': "no-cache",
    	'postman-token': "87821524-958d-4038-b35e-6e47449062c1"
    }
	endpoint = ('/calls/data/GetNews?outputMode={0}&start={1}&end={2}&count={3}&q.enriched.url.enrichedTitle.keywords.keyword.text={4}&return={5}&apikey={6}').format(outputMode, startdate, enddate, count, searchterm, returnfields, apikey)
	print("==Calling GetNews endpoint: %s", endpoint)
	conn.request("GET", endpoint, headers=headers)
	res = conn.getresponse()
	errMsg = ("=====Error with GetNews: status[{0}], msg[{1}], reason[{2}]").format(res.status, res.msg, res.reason)
	print(errMsg)
	# HTTPResponse.read returns bytes[]
	data = res.read()
	responseStr = data.decode("utf-8")
	return responseStr

def FormatDate(dateStr=None):
	now = datetime.now()
	date1 = datetime.strptime(dateStr, '%Y-%m-%d')
	delta1 = now-date1
	date1 = ("now-{0}d").format(delta1.days)
	return date1

def ParseNews(articles=None, startdate1=None):
	status1 = ""
	startdate1 = datetime.strptime(startdate1, '%Y-%m-%d')
	if (articles==None or articles==""):
		print("=====Error with GetNews API, articles==None")
		status1 = 'ERROR'
		articles = mycloudantdb.GetNews()
		articlesJson = json.loads(articles)
		#print(articlesJson)
	else:
		print("=====Articles: %s", articles)
		articlesJson = json.loads(articles)
		status1 = articlesJson['status']
		if status1=='ERROR':
			# to avoid rate limits create a search result in cloudant
			# and on rate limit pull response from cloudant 'cache'
			print("=====News from Cloudant, continue")
			statusInfo = articlesJson['statusInfo']
			errMsg = ('==Error in GetNews. StatusInfo: {0}').format(statusInfo)
			print(errMsg)
			#return errMsg
			articles = mycloudantdb.GetNews()
			articlesJson = json.loads(articles)
		elif status1=='OK':
			print("=====News from GetNews")

	mycloudantdb.saveNews(articlesJson)
	result = articlesJson['result']

	docs = result['docs']
	print('=====status: %s', status1)
	sentimentList = []
	for doc in docs:
		source = doc['source']
		enriched = source['enriched']
		enrichedURL = enriched['url']
		# Get publicationDate
		publicationDate = enrichedURL['publicationDate']['date']
		sentiment = ""
		if status1=='OK':
			sentiment = enrichedURL['docSentiment']['score']
		elif status1=='ERROR':
			#sentiment = enrichedURL['enrichedTitle']['docSentiment']['score']
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
		if startdate1 < pubdate1:
			uniqueDates.add(pubdate1)
	uniqueDates = sorted(uniqueDates)
	
	# loop through the uniqueDates and calculate averages for duplicates by date
	i1 = 0
	for uniqueDate in uniqueDates:
		i1 = i1 + 1
		sentiments = 0
		i = 0
		for row in sentimentList:
			rowDate = datetime.strptime(row['publicationDate'], '%Y%m%dT%H%M%S')
			if rowDate==uniqueDate:
				i = i + 1
				sentiments += row['sentiment']
		avgSentiment = sentiments/i
		uniqueDateStr = datetime.strftime(uniqueDate, '%Y%m%dT%H%M%S')
		uniqueSentimentRow = {"publicationDate": uniqueDateStr, "sentiment": avgSentiment}
		uniqueSentimentList.append(uniqueSentimentRow)

	return uniqueSentimentList
	
def GetSentiment(outputMode="json", articleURL="https://developer.ibm.com/bluemix/2016/09/23/what-is-the-bluemix-garage/"):
	conn = http.client.HTTPSConnection("gateway-a.watsonplatform.net")
	headers = {
    	'content-type': "application/json"
    }
	endpoint = ('/calls/url/URLGetEmotion?outputMode={0}&url={1}&apikey={2}').format(outputMode, articleURL, apikey)
	print("==Calling GetSentiment endpoint: %s", endpoint)
	conn.request("GET", endpoint, headers=headers)
	res = conn.getresponse()
	data = res.read()
	return data.decode("utf-8")


