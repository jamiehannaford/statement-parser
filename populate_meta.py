#!/usr/bin/env python

from redis import Redis
from rq import Retry, Queue
from statement_parser.filing_urls import UrlRetriever
import requests
import os
import mysql.connector


r = Redis(host='redis', port=6379, db=0)
q = Queue(connection=r)

api_key = os.environ["FMP_API_KEY"]
r = requests.get(f"https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={api_key}")

for entry in r.json():
    p = UrlRetriever(entry['cik'])
    q.enqueue(p.get_all_years, retry=Retry(max=3, interval=[10, 30, 60]))