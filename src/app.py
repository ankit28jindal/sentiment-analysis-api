import os
import json
from flask import Flask
from flask_restful import Api, Resource, reqparse
import tweepy
from textblob import TextBlob


with open(os.environ['config_file_path'], 'r') as file:
    config: dict = json.load(file)

auth = tweepy.OAuthHandler(config['Twitter']['consumer_key'], config['Twitter']['consumer_secret'])
auth.set_access_token(config['Twitter']['access_token'], config['Twitter']['access_token_secret'])
t_api = tweepy.API(auth)

app = Flask(__name__)
api = Api(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Access-Control-Allow-Origin, Access-Control-Allow-Methods')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

class ApiKey(Resource):
    def get(self):
        return config['NewsAPI']['api_key']

class User(Resource):
    def get(self, name, number_of_tweets):
        polarity: str
        ptweets: list = []
        neutweets: list = []
        negtweets: list = []

        result = tweepy.Cursor(t_api.search, q=name, lang='en').items(number_of_tweets)
        d: list = []
        for r in result:
            analysis = TextBlob(r.text)
            if analysis.polarity > 0:
                ptweets.append(r.text)
            elif analysis.polarity == 0:
                neutweets.append(r.text)
            else:
                negtweets.append(r.text)
            
        d.append({
            'name': 'Positive',
            'data': ptweets
        })
        d.append({
            'name': 'Neutral',
            'data': neutweets
        })
        d.append({
            'name': 'Negative',
            'data': negtweets,
        })

        return {
            "Positive Tweets Percentage": (100*len(ptweets)/number_of_tweets),
            "Neutral Tweets Percentage": (100*len(neutweets)/number_of_tweets),
            "Negative Tweets Percentage": (100*len(negtweets)/number_of_tweets),
            "Tweets": d
        }

api.add_resource(User, '/user/<string:name>/<int:number_of_tweets>')
api.add_resource(ApiKey, '/apikey')
app.run()
