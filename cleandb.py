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
speeches.delete_many({})
statements.delete_many({})
events.delete_many({})
gpgkeys.delete_many({})


