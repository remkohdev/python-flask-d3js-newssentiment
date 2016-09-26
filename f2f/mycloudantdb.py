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
	news = my_database['de0a130f410d883d8b432de4bc015eb3']
	client.disconnect()
	# json to string
	news = json.dumps(news)
	return news;

def saveNews(doc):
	print('=====Saving Document to Cloudant')
	client.connect()
	my_database = client['newssentiment']
	docId = doc['_id']
	doc1 = my_database[docId]
	if doc1.exists():
		msg = ('=====Document with id[{0}] already exists').format(docId)
		print(msg)
	else:
		my_document = my_database.create_document(doc)
		if my_document.exists():
		    print('SUCCESS')

	client.disconnect()
