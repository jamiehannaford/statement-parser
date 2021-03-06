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
import time

from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError
from xbrl import TaxonomyNotFound
from xbrl.cache import HttpCache
from xbrl.instance import parse_xbrl, parse_xbrl_url, XbrlInstance
from secedgar.filings.filing import Filing
from secedgar.filings.filing_types import FilingType
from faker import Faker
import mysql.connector

import warnings
warnings.filterwarnings('ignore')

logging.getLogger("xbrl.cache").setLevel(logging.WARNING)

class Downloader:
    root_dir = "data"

    def __init__(self, ticker, cik=None, filing_type="10-K", num_quarters=4):
        self.cache = HttpCache('./cache/')

        self.filing_type = filing_type
        self.api_key = os.environ['FMP_API_KEY']
        if not self.api_key:
            raise ValueError("FMP_API_KEY not set")

        self.set_ticker(ticker, cik)
        self.set_cik(cik, ticker)
        self.num_quarters = num_quarters

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

    def user_agent(self):
        fake = Faker()
        return f"{fake.first_name()} {fake.last_name()} {fake.email()}"

    def set_cik(self, cik, ticker):
        if not cik:
            try:
                cik = self.get_cik_sic(ticker)
            except (KeyError, IndexError):
                cik = self.get_cik_prof(ticker)

        self.cik = cik.zfill(10)

    def get_from_date(self):
        now = datetime.now()
        if self.filing_type == '10-K':
            return date(now.year-5, 1, 1).strftime("%Y-%m-%d")
        else:
            return date(now.year-1, 1, 1).strftime("%Y-%m-%d")

    def get_urls(self, from_date=None, to_date=None):
        now = datetime.now()
        if not from_date:
            from_date = self.get_from_date()
        if not to_date:
            to_date = now.strftime("%Y-%m-%d")

        count = int(to_date[:4]) - int(from_date[:4])
        if count <= 0:
            count = 1
        if self.filing_type == '10-Q':
            count = self.num_quarters

        db = mysql.connector.connect(       
            host=os.environ['MYSQL_HOST'],
            user=os.environ['MYSQL_USER'],
            password=os.environ['MYSQL_PASS'],
            port=os.environ['MYSQL_PORT'],
            database='expensifier'
        )
        cur = db.cursor()

        query = "SELECT filing_date, accession_number, filing_type FROM filing_meta WHERE cik = %s AND filing_date BETWEEN %s and %s"
        values = (self.cik, from_date, to_date)
        cur.execute(query, values) 
        res = cur.fetchall()

        cur.close()
        db.close()

        return res

    def download_url(self, url):
        self.cache.set_headers({"User-Agent": self.user_agent()})
        parse_xbrl_url(url, self.cache)

    def download_zip(self, url, path):
        Path(path).mkdir(parents=True, exist_ok=True)
        zip_path = f"{path}.zip"
        self.download_file(url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(path)
        os.remove(zip_path)

    def download_file(self, url, save_path, chunk_size=128):
        r = requests.get(url, stream=True, headers={"User-Agent": self.user_agent()})
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
                time.sleep(1) # avoid rate limiting
            except Exception as e:
                print(f"Error: {str(e)}")
            q.task_done()

    def download_url(self, url):
        self.cache.set_headers({"User-Agent": random_str()})
        parse_xbrl_url(url, self.cache)

    def fetch_url(self, url_map, only_html):
        date_formatted = url_map[0].strftime("%Y%m%d")
        filing_dir = os.path.join(self.root_dir, self.ticker, date_formatted)
        
        if glob.glob(f"{filing_dir}*/*.xml"):
            print(f"{filing_dir} already exists")
            return

        an_formatted = url_map[1].replace("-", "")
        zip_url = f"https://www.sec.gov/Archives/edgar/data/{self.cik}/{an_formatted}/{url_map[1]}-xbrl.zip"

        print(f"Downloading {zip_url}...")
        try:
            self.download_zip(zip_url, filing_dir)
        except HTTPError:
            shutil.rmtree(filing_dir)
            print("could not download zip, skipping...")
            return

        for unneeded_file in glob.glob(f"{filing_dir}/*"):
            if unneeded_file.endswith((".xml", ".xsd")):
                continue 
            os.remove(unneeded_file)

        res = requests.get(f"https://www.sec.gov/Archives/edgar/data/{self.cik}/{an_formatted}", headers={"User-Agent": self.user_agent()})
        soup = BeautifulSoup(res.text, "html.parser")
        link = soup.findAll("a", href=lambda x: x and x.endswith("_htm.xml"))
        if link:
            htm_path = link[0].attrs['href'].strip("/")
            html_url = f"https://www.sec.gov/{htm_path}"
            self.download_file(html_url, os.path.join(filing_dir, os.path.basename(htm_path)))

    def download(self, last=None, from_date=None, to_date=None, only_html=False):
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
    logging.getLogger("xbrl.cache").setLevel(logging.WARNING)

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