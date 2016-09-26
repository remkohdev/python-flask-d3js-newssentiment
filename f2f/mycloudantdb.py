from cloudant.client import Cloudant
import json


username = ""
password = ""
cloudantURL = ""
client = Cloudant(username, password, url=cloudantURL)

def GetNews(): 
	client.connect()
	my_database = client['newssentiment']
	# document_id
	news = my_database['b6b6522da100f316cfd44191aebf4199']
	client.disconnect()
	# json to string
	news = json.dumps(news)
	return news;
