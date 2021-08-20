import argparse
from datetime import date, datetime
import glob
import logging
from pathlib import Path
import os
import shutil
import zipfile
from threading import Thread
from queue import Queue
import sys

from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError
from statement_parser.utils import get_filing_urls_to_download, random_str
from xbrl_parser import TaxonomyNotFound
from xbrl_parser.cache import HttpCache
from xbrl_parser.instance import parse_xbrl, parse_xbrl_url, XbrlInstance
from secedgar.filings.filing import Filing
from secedgar.filings.filing_types import FilingType

import warnings
warnings.filterwarnings('ignore')

logging.getLogger("xbrl_parser.cache").setLevel(logging.WARNING)

class Downloader:
    root_dir = "data"

    def __init__(self, ticker, cik=None, filing_type="10-K"):
        self.cache = HttpCache('./cache/')

        self.filing_type = filing_type
        self.api_key = os.environ['API_KEY']
        if not self.api_key:
            raise ValueError("API_KEY not set")

        self.set_ticker(ticker, cik)
        self.set_cik(cik, ticker)

    def set_ticker(self, ticker, cik):
        if not ticker:
            cik = cik.zfill(10)
            url = f"https://financialmodelingprep.com/api/v4/standard_industrial_classification?cik={cik}&apikey={self.api_key}"
            res = requests.get(url).json()
            ticker = res[0]["symbol"]
        self.ticker = ticker

    def get_cik_sic(self, ticker):
        url = f"https://financialmodelingprep.com/api/v4/standard_industrial_classification?symbol={ticker}&apikey={self.api_key}"
        res = requests.get(url).json()
        return res[0]["cik"]

    def get_cik_prof(self, ticker):
        url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={self.api_key}"
        res = requests.get(url).json()
        return res[0]["cik"]    

    def set_cik(self, cik, ticker):
        if not cik:
            try:
                cik = self.get_cik_sic(ticker)
            except IndexError:
                cik = self.get_cik_prof(ticker)

        self.cik = cik.zfill(10)

    def get_urls(self, from_date=None, to_date=None):
        now = datetime.now()
        if not from_date:
            from_date = date(now.year-5, 1, 1).strftime("%Y-%m-%d")
        if not to_date:
            to_date = now.strftime("%Y-%m-%d")

        count = int(to_date[:4]) - int(from_date[:4])
        if count <= 0:
            count = 1

        return get_filing_urls_to_download(self.filing_type, self.cik, count, from_date, to_date, False)

    def download_url(self, url):
        self.cache.set_headers({"User-Agent": random_str()})
        parse_xbrl_url(url, self.cache)

    def download_zip(self, url, path):
        Path(path).mkdir(parents=True, exist_ok=True)
        zip_path = f"{path}.zip"
        self.download_file(url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(path)
        os.remove(zip_path)

    def download_file(self, url, save_path, chunk_size=128):
        r = requests.get(url, stream=True, headers={"User-Agent": random_str()})
        r.raise_for_status()
        with open(save_path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)

    def attempt_htm_download(self, filing_dir, url, htm_xml_filename):
        htm_xml_url = os.path.join(os.path.dirname(url), htm_xml_filename)
        self.download_file(htm_xml_url, os.path.join(filing_dir, htm_xml_filename))

    def process_url(self, q, only_html):
        while True:
            url = q.get()
            try:
                self.fetch_url(url, only_html)
            except Exception as e:
                print(f"Error: {str(e)}")
            q.task_done()

    def download_url(self, url):
        self.cache.set_headers({"User-Agent": random_str()})
        parse_xbrl_url(url, self.cache)

    def fetch_url(self, url_map, only_html):
        filing_dir = os.path.join(self.root_dir, self.ticker, url_map.period_ending)

        download_path_htm = os.path.join(filing_dir, os.path.basename(url_map.filing_details_url))
        
        if only_html:
            self.download_file(url_map.filing_details_url, download_path_htm)
            return

        if glob.glob(f"{filing_dir}*"):
            print(f"{filing_dir} already exists")
            return
        
        print(f"Downloading {url_map.zip_url}...")
        try:
            self.download_zip(url_map.zip_url, filing_dir)
        except HTTPError:
            shutil.rmtree(filing_dir)
            print("could not download zip, skipping...")
            return

        for unneeded_file in glob.glob(f"{filing_dir}/*"):
            if unneeded_file.endswith((".xml", ".xsd")):
                continue 
            os.remove(unneeded_file)
        
        updated_url = url_map.filing_details_xml
        if int(url_map.period_ending[:4]) >= 2019:
            updated_url = url_map.filing_details_htm

        download_path_xml = os.path.join(filing_dir, os.path.basename(updated_url))

        # Download HTML iXBRL file
        self.download_file(url_map.filing_details_url, download_path_htm)

        # Download XML instance file
        try:
            self.download_file(updated_url, download_path_xml)
        except:
            updated_url = f"{url_map.submission_base_url}/{self.ticker.lower()}-{url_map.period_ending}.xml"
            self.download_file(updated_url, download_path_xml)

    def download(self, last=None, from_date=None, to_date=None, only_html=False):
        file_dir = f"data/{self.ticker}/10-k"

        if last:
            from_date = f"{int(datetime.now().year) - int(last)}-01-01"

        urls = []

        retries = 0
        while retries <= 5 and len(urls) == 0:
            urls = self.get_urls(from_date=from_date, to_date=to_date)
            retries += 1

        if len(urls) == 0:
            raise ValueError("No URLs found")

        num_fetch_threads = 5
        enclosure_queue = Queue()

        for i in range(num_fetch_threads):
            worker = Thread(target=self.process_url, args=(enclosure_queue,only_html))
            worker.setDaemon(True)
            worker.start()

        for url in urls:
            enclosure_queue.put(url)

        enclosure_queue.join()

if __name__ == "__main__":
    logging.getLogger("xbrl_parser.cache").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description='Download SEC filings.')
    parser.add_argument('-t', '--ticker', required=True, help='Company ticker')
    parser.add_argument('-f', '--type', help='Type of filing', default='10-K')
    
    parser.add_argument('--last', help='Last n filings', default=None)
    parser.add_argument('--from', dest="from_date", help='From date', default=None)
    parser.add_argument('--to', dest="to_date", help='To date', default=None)

    args = parser.parse_args()

    if len([x for x in (args.from_date, args.to_date) if x is not None]) == 1:
        raise ValueError("Both --from and --to must be provided together")
    
    if args.last and (args.from_date or args.to_date):
        raise ValueError("--last cannot be used with either --from or --to")

    downloader = Downloader(args.ticker, filing_type=args.type)
    downloader.download(last=args.last, from_date=args.from_date, to_date=args.to_date)