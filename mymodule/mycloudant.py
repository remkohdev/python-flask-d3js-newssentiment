from cloudant.client import Cloudant
import json

username = "<cloudant-username>"
password = "<cloudant-password>"
cloudantURL = "https://<cloudant-accountname>.cloudant.com"
        
client = Cloudant(username, password, url=cloudantURL)

def SaveNews(doc):
	print('Save Document')
	# class should be 'dict'
	if isinstance(doc, str):
		doc = json.loads(doc)

	client.connect()
	my_database = client['newssentiment']

	my_document = my_database.create_document(doc)
	if my_document.exists():
	    print('Save Document: SUCCESS')
	else:
		print('Save Document: ERROR')

	client.disconnect()
	
def GetNews(): 
	client.connect()
	my_database = client['newssentiment']
	# document_id
	news = my_database[document_id]
	client.disconnect()
	# json to string
	news = json.dumps(news)
	return news;