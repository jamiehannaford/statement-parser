#!/usr/bin/env python

from redis import Redis
from rq import Retry, Queue
from parse import Parser
import requests
import os

r = Redis(host='redis', port=6379, db=0)
q = Queue(connection=r)

api_key = os.environ["FMP_API_KEY"]
r = requests.get(f"https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={api_key}")

for entry in r.json():
    p = Parser(ticker=entry['symbol'], num_quarters=20, save_mysql=True)
    q.enqueue(p.process, retry=Retry(max=3, interval=[10, 30, 60]))