# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from flask import Flask, jsonify, render_template, Response, request
from f2f import alchemyapi, mycloudantdb
from datetime import datetime
import json

app = Flask(__name__)

@app.route('/')
def Welcome():
    #return app.send_static_file('index.html')
    return render_template('index.html')
    
@app.route('/search')
def Search(startdate=None, enddate=None, searchterm=None, count=None):
	startdateStr = request.args.get('startdate', '7daysago')
	enddateStr = request.args.get('enddate', 'today')
	searchterm = request.args.get('searchterm')
	count = request.args.get('count')
	
	now = datetime.now()
	startdate1 = datetime.strptime(startdateStr, '%Y-%m-%d')
	enddate2 = datetime.strptime(enddateStr, '%Y-%m-%d')
	deltastart = now-startdate1
	deltaend = now-enddate2
	startdate = ("now-{0}d").format(deltastart.days)
	enddate = ("now-{0}d").format(deltaend.days)

	# GetNews with Sentiment
	returnfields = 'enriched.url.url%2Cenriched.url.title%2Cenriched.url.publicationDate.date%2Cenriched.url.docSentiment.score'
	articles = alchemyapi.GetNews(searchterm=searchterm, returnfields=returnfields, startdate=startdate, enddate=enddate, count=count)
	articlesJson = json.loads(articles)

	status1 = articlesJson['status']
	if status1=='ERROR':
		statusInfo = articlesJson['statusInfo']
		errMsg = ('==Error in GetNews. StatusInfo: {0}').format(statusInfo)
		print(errMsg)
		# workaround for annoying alchemyapi rate limit
		#return errMsg
		articles = mycloudantdb.GetNews()
		articlesJson = json.loads(articles)
		print("=====News from Cloudant, continue")
	elif status1=='OK':
		print("=====News from GetNews")

	docs = articlesJson['result']['docs']
	sentimentList = []
	for doc in docs:
		enrichedURL = doc['source']['enriched']['url']
		# Get publicationDate
		publicationDate = enrichedURL['publicationDate']['date']
		sentiment = ""
		if status1=='OK':
			sentiment = enrichedURL['docSentiment']['score']
		elif status1=='ERROR':
			sentiment = enrichedURL['enrichedTitle']['docSentiment']['score']
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
	
	# loop through the uniqueDates set and calculate averages per date
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

	response = {
		'news' : uniqueSentimentList,
	    'startdate' : startdateStr,
	    'enddate' : enddateStr,
	    'searchterm' : searchterm
	}

	return render_template('report.html',  
		response=response)

	'''
	For each News article, URLGetSentiment separately
	which will return scores of 5 emotions: 
	    "anger": "0.538312",
    	"disgust": "0.525831",
    	"fear": "0.375013",
    	"joy": "0.518644",
    	"sadness": "0.029991"
	'''
	'''
		sentiment = alchemyapi.GetSentiment('json', articleURL['url'])
		sentimentJson = json.loads(sentiment)
		status1 = sentimentJson['status']
		if status1=='ERROR':
			statusInfo = sentimentJson['statusInfo']
			errMsg = ('==Error in GetSentiment. StatusInfo: {0}').format(statusInfo)
			print(errMsg)
			sentimentCsv = ('{0},{1}').format(publicationDate, errMsg)
			sentimentCsvList.append(sentimentCsv)
			continue
		sentimentCsv = alchemyapi.ParseSentimentToCsv(publicationDate, sentimentJson)
		sentimentCsvList.append(sentimentCsv)
	'''

@app.route('/api/people')
def GetPeople():
    list = [
        {'name': 'John', 'age': 28},
        {'name': 'Bill', 'val': 26}
    ]
    return jsonify(results=list)

@app.route('/api/people/<name>')
def SayHello(name):
    message = {
        'message': 'Hello ' + name
    }
    return jsonify(results=message)

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
