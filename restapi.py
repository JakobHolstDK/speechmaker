from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from pymongo import MongoClient
import pprint
import gnupg
import tempfile
import requests
import openai
import redis
import os
import pygame
import time
import random
import numpy
import sys
import redis
import textwrap
import math
import uuid




gpg = gnupg.GPG()
app = Flask(__name__)

client = MongoClient('mongodb://192.168.123.33:27017/')
db = client['speechmaker']
statements = db['statements']
speeches = db['speeches']
events = db['events']
gpgkeys = db['gpgkeys']

openai.api_key = os.getenv("OPENAI_API_KEY")


#speeches.delete_many({})
#statements.delete_many({})
#events.delete_many({})
#gpgkeys.delete_many({})
def setstatementused(id):
   url = 'https://speechmakerapi.openknowit.com/statements/' +  id
   headers = {'Content-Type': 'application/json'}
   data = {
           "used": True
   }
   response = requests.put(url, headers=headers, json=data)

def randomstatement(token):
    event = events.find_one({'token': token})
    ai_assistant="The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and friendly."
    ai_situation="\n" + event['situation'] + "\n"
    context = ai_assistant + "\n" + ai_situation + "\n"
    context = context + "\nHuman: Please create a made up history about the bride, groom or both told by a frind or relative at the wedding. The story should be an anecdote and should start with a made up name and relation to the newly weds, seperate the speaker, the relation, who it is about and the history with semicolons, the story can be either the groom, the bride or the pair, before the speaker write SPEAKER: ? The AI:"
    statement = askai(context)

    item = statement.split(';')

    url = 'https://speechmakerapi.openknowit.com/statements'
    headers = {'Content-Type': 'application/json'}
    data = {
                "text": item[3],
                "sender": item[0].split("SPEAKER:")[1],
                "relation" : item[1].split(":")[1],
                "token": token,
                "target": item[2].split(":")[1] 
                        }
    response = requests.post(url, headers=headers, json=data)
    statement = statement.replace("\\","").replace('"','')

    return(statement)

def createspeech(token, trigger):
  event = events.find_one({'token': token})
  ai_assistant="The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and friendly."
  ai_situation=event['situation']
  context = ai_assistant + "\n" + ai_situation + "\n"
  query = {"token": token}
  for statement in statements.find():
    statement['_id'] = str(statement['_id'])
    addme = statement['sender'] + ", " + statement['relation'] + " is saying the following about " + statement['target'] + " : " + statement['text'] + "\n"
    context = context + addme
    setstatementused(statement['_id'])
  context = context + "\nHuman: Please create a long speech with at least 2000 words to them at their wedding base on all these statements? \nAI:"
  speech = askai(context)
  url = 'https://speechmakerapi.openknowit.com/speeches'
  headers = {'Content-Type': 'application/json'}
  data = {
       "text": speech,
       "trigger": trigger,
       "token": token,
       "context": context
       }
  response = requests.post(url, headers=headers, json=data)

def askai( prompt ):
      response = openai.Completion.create(
      model="text-davinci-003",
      prompt=prompt,
      temperature=0.9,
      max_tokens=1500,
      top_p=1,
      frequency_penalty=0.0,
      presence_penalty=0.6,
      stop=[" Human:", " AI:"]
      )
      return(response['choices'][0]['text'])








@app.route('/gpgkeys', methods=['GET'])
def get_gpgkeys():
   result = []
   for gpgkey in gpgkeys.find():
     gpgkey['_id'] = str(gpgkey['_id'])
     result.append(gpgkey)
   return jsonify(result)

@app.route('/randomstatement/<string:event_id>', methods=['PUT'])
def createrandomstatement(event_id):
   print(event_id)
   result = randomstatement(event_id)
   result = result.replace('\n','')
   return jsonify(result)





##############################
# speeches
##############################

@app.route('/events', methods=['GET'])
def get_events():
    result = []
    for event in events.find():
        event['_id'] = str(event['_id'])
        result.append(event)
    return jsonify(result)

@app.route('/events', methods=['POST'])
def create_event():
    data = request.get_json()
    token = data['token']
    name = data['name']
    situation = data['situation']
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    event = events.find_one({'token': token})
    if event is not None:
        return jsonify({'error': 'Event aleredy exists'}), 404
    else:
        event = {'token': token, 'name': name, 'situation': situation ,  'time': time}
        result = events.insert_one(event)
        event['_id'] = str(result.inserted_id)
        return jsonify(event)

@app.route('/events/<string:event_id>', methods=['PUT'])
def update_event(event_id):
    event = events.find_one({'_id': event_id})
    if event:
        data = request.get_json()
        events.update_one({'_id': event_id}, {'$set': data})
        event.update(data)
        return jsonify(event)
    else:
        return jsonify({'error': 'Event not found'}), 404

@app.route('/events/<string:event_id>', methods=['DELETE'])
def delete_event(event_id):
    result = events.delete_one({'_id': event_id})
    if result.deleted_count > 0:
        return jsonify({'message': 'Event deleted'})
    else:
        return jsonify({'error': 'Event not found'}), 404








##############################
# speeches
##############################
@app.route('/speeches', methods=['GET'])
def get_speeches():
    result = []
    for speech in speeches.find():
        speech['_id'] = str(speech['_id'])
        result.append(speech)
    return jsonify(result)

@app.route('/speeches', methods=['POST'])
def create_speech():
    data = request.get_json()
    text = data['text']
    trigger = data['trigger']
    token = data['token']
    context = data['context']
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    speech = {'text': text, "trigger": trigger, "token": token, 'context': context, 'time': time}
    result = speeches.insert_one(speech)
    speech['_id'] = str(result.inserted_id)
    return jsonify(speech)

@app.route('/speeches/<string:speech_id>', methods=['PUT'])
def update_speech(speech_id):
    speech = speeches.find_one({'_id': speech_id})
    if speech:
        data = request.get_json()
        speeches.update_one({'_id': speech_id}, {'$set': data})
        speech.update(data)
        return jsonify(speech)
    else:
        return jsonify({'error': 'Speech not found'}), 404

@app.route('/speeches/<string:speech_id>', methods=['DELETE'])
def delete_speech(speech_id):
    result = speeches.delete_one({'_id': speech_id})
    if result.deleted_count > 0:
        return jsonify({'message': 'Speech deleted'})
    else:
        return jsonify({'error': 'Speech not found'}), 404






##################################
# Statements
######################################

@app.route('/statements', methods=['GET'])
def get_statements():
    result = []
    for statement in statements.find():
        statement['_id'] = str(statement['_id'])
        result.append(statement)
    return jsonify(result)

@app.route('/statements', methods=['POST'])
def create_statement():
    data = request.get_json()
    text = data['text']
    used = False
    sender = data['sender']
    token = data['token']
    target = data['target']
    relation = data['relation']
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    statement = {'text': text, 'token': token, 'sender': sender, 'relation': relation, 'target': target, 'time': time, 'used': used }
    result = statements.insert_one(statement)
    statement['_id'] = str(result.inserted_id)
    createspeech(token, statement['_id'])
    return jsonify(statement)

@app.route('/statements/<string:statement_id>', methods=['PUT'])
def update_statement(statement_id):
    statement = statements.find_one({'_id': statement_id})
    if statement:
        data = request.get_json()
        statements.update_one({'_id': statement_id}, {'$set': data})
        statement.update(data)
        return jsonify(statement)
    else:
        return jsonify({'error': 'Statement not found'}), 404

@app.route('/statements/<string:statement_id>', methods=['DELETE'])
def delete_statement(statement_id):
    result = statements.delete_one({'_id': statement_id})
    if result.deleted_count > 0:
        return jsonify({'message': 'Statement deleted'})
    else:
        return jsonify({'error': 'Statement not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

