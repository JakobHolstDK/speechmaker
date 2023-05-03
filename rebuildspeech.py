#!/usr/bin/env python

import openai
import redis
import os
import datetime
import time
import random
import requests
import numpy
import sys
import redis
import textwrap
import math
import uuid
from pymongo import MongoClient


openai.api_key = os.getenv("OPENAI_API_KEY")
client = MongoClient('mongodb://192.168.123.33:27017/')
db = client['speechmaker']
statements = db['statements']
speeches = db['speeches']
events = db['events']
gpgkeys = db['gpgkeys']

def setstatementused(id):  
  url = 'https://speechmakerapi.openknowit.com/statements/' +  id 
  headers = {'Content-Type': 'application/json'}
  data = {
           "used": True
        }
  response = requests.put(url, headers=headers, json=data)


def createspeechcontext(token):
  event = events.find_one({'token': token})
  ai_assistant="The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and friendly."
  ai_situation=event['situation']
  context = ai_assistant + "\n" + ai_situation + "\n"
  query = {"token": "1"}
  for statement in statements.find():
    statement['_id'] = str(statement['_id'])
    addme = statement['sender'] + ", " + statement['relation'] + " is saying the following about " + statement['target'] + " : " + statement['text'] + "\n"
    context = context + addme
    setstatementused(statement['_id'])
  context = context + "\nHuman: Please create a long speech with at least 2000 words to them at their wedding base on all these statements? \nAI:"
  return context



def createspeech( prompt ):
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


context =  createcontext(")
speech = createspeech(context)
url = 'https://speechmakerapi.openknowit.com/speeches'
headers = {'Content-Type': 'application/json'}
data = {
           "text": speech,
           "token": "1",
           "context": context
        }
response = requests.post(url, headers=headers, json=data)

print(speech)


