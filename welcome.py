import os
from flask import Flask, jsonify, render_template, Response, request
from mymodule import myalchemyapi, mycloudant
import json

app = Flask(__name__)

@app.route('/')
def Welcome():
    #return app.send_static_file('index.html')
    return render_template('index.html')
    
@app.route('/search')
def Search(startdate=None, enddate=None, searchterm=None, count=None):
    startdateStr = request.args.get('startdate')
    enddateStr = request.args.get('enddate')
    searchterm = request.args.get('searchterm')
    count = request.args.get('count')
    
    # format the correct start and end formats
    startdate = myalchemyapi.FormatDate(startdateStr)
    enddate = myalchemyapi.FormatDate(enddateStr)

    # GetNews with Sentiment
    returnfields = 'enriched.url.url%2Cenriched.url.title%2Cenriched.url.publicationDate.date%2Cenriched.url.docSentiment.score'
    articles = myalchemyapi.GetNews(searchterm=searchterm, returnfields=returnfields, startdate=startdate, enddate=enddate, count=count)
    
    # prepare for d3js, calculate the average sentiment per day
    uniqueSentimentList = myalchemyapi.ParseNews(articles, startdateStr, enddateStr)

    response = {
        'news' : uniqueSentimentList,
        'startdate' : startdateStr,
        'enddate' : enddateStr,
        'searchterm' : searchterm
    }

    return render_template('report.html', response=response)


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))


