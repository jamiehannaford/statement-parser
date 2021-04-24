import argparse
from datetime import date, datetime
import logging
import os 
from pathlib import Path
import shutil

import requests
from xbrl_parser.instance import parse_xbrl, parse_xbrl_url, XbrlInstance
from xbrl_parser.cache import HttpCache
from statement_parser.utils import get_filing_urls_to_download, random_str

cache = HttpCache('./cache/')
logging.getLogger("xbrl_parser.cache").setLevel(logging.WARNING)

parser = argparse.ArgumentParser(description='Download SEC filings.')
parser.add_argument('-c', '--ticker', required=True, help='Company ticker')
parser.add_argument('-t', '--type', help='Type of filing', default='10-K')
args = parser.parse_args()

api_key = os.environ['API_KEY']
if not api_key:
    raise ValueError("API_KEY not set")

def get_cik(ticker, api_key):
    url = f"https://financialmodelingprep.com/api/v4/company-outlook?symbol={ticker}&apikey={api_key}"
    res = requests.get(url).json()
    return res["profile"]["cik"]

def get_urls(ticker, api_key):
    cik = get_cik(ticker, api_key)
    return get_filing_urls_to_download("10-K", cik, 100, 
    date(2016, 1, 1).strftime("%Y-%m-%d"), 
    datetime.now().strftime("%Y-%m-%d"), False)

def download_url(url):
    cache.set_headers({"User-Agent": random_str()})
    parse_xbrl_url(url, cache)

file_dir = f"data/{args.ticker}/10-k"

urls = get_urls(args.ticker, api_key)
if len(urls) == 0:
    raise ValueError("No URLs found")

for url in urls:
    print(f"Downloading {url.period_ending}...")

    updated_url = url.filing_details_xml
    if int(url.period_ending[:4]) >= 2019:
        updated_url = url.filing_details_htm
    try:
        download_url(updated_url)
    except:
        updated_url = f"{url.submission_base_url}/{args.ticker.lower()}-{url.period_ending}.xml"
        download_url(updated_url)

    root_dir = f"cache/www.sec.gov/Archives/edgar/data"
    Path(f"{root_dir}/{args.ticker}").mkdir(parents=True, exist_ok=True)

    old_dir = f"{root_dir}/{url.cik}/{url.accession_number.replace('-', '')}"
    new_dir = f"{root_dir}/{args.ticker}/{url.period_ending}"
    
    if os.path.isdir(new_dir):
        new_dir = f"{root_dir}/{args.ticker}/{url.accession_number.replace('-', '')}"

    try:
        os.rename(old_dir, new_dir)
    except OSError:
        print(f"could not create {new_dir}")
        shutil.rmtree(old_dir)

