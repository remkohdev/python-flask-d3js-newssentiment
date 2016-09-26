import http.client
import csv

apikey = "<alchemyapi-apikey>"

def GetNews(searchterm=None, outputMode="json", startdate=None, enddate=None, count="5", returnfields="enriched.url.url"): 
	conn = http.client.HTTPSConnection("gateway-a.watsonplatform.net")
	headers = {
    	'content-type': "application/json"
	}
	endpoint = ('/calls/data/GetNews?outputMode={0}&start={1}&end={2}&count={3}&q.enriched.url.enrichedTitle.keywords.keyword.text={4}&return={5}&apikey={6}').format(outputMode, startdate, enddate, count, searchterm, returnfields, apikey)
	print("==Calling GetNews endpoint: %s", endpoint)
	conn.request("GET", endpoint, headers=headers)
	res = conn.getresponse()
	# HTTPResponse.read returns bytes[]
	data = res.read()
	return data.decode("utf-8")

	
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