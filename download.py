import argparse
from datetime import date, datetime
import glob
import logging
from pathlib import Path
import os
import shutil

import requests
from statement_parser.utils import get_filing_urls_to_download, random_str
from xbrl_parser import TaxonomyNotFound
from xbrl_parser.cache import HttpCache
from xbrl_parser.instance import parse_xbrl, parse_xbrl_url, XbrlInstance

logging.getLogger("xbrl_parser.cache").setLevel(logging.WARNING)


class Downloader:
    def __init__(self, ticker, filing_type="10-k"):
        self.cache = HttpCache('./cache/')
        self.ticker = ticker 
        self.filing_type = filing_type
        self.api_key = os.environ['API_KEY']
        if not self.api_key:
            raise ValueError("API_KEY not set")

    def get_cik(self):
        url = f"https://financialmodelingprep.com/api/v4/company-outlook?symbol={self.ticker}&apikey={self.api_key}"
        res = requests.get(url).json()
        return res["profile"]["cik"]

    def get_urls(self, from_date=None, to_date=None):
        if not from_date:
            from_date = date(2015, 1, 1).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        
        cik = self.get_cik()
        return get_filing_urls_to_download("10-K", cik, 100, from_date, to_date, False)

    def download_url(self, url):
        self.cache.set_headers({"User-Agent": random_str()})
        parse_xbrl_url(url, self.cache)

    def download(self, from_date=None, to_date=None):
        file_dir = f"data/{self.ticker}/10-k"
        urls = self.get_urls(from_date, to_date)
        if len(urls) == 0:
            raise ValueError("No URLs found")

        for url in urls:
            root_dir = f"cache/www.sec.gov/Archives/edgar/data"

            if os.path.isdir(f"{root_dir}/{self.ticker}/{url.period_ending}"):
                print(f"{url.period_ending} already exists")
                continue
           
            print(f"Downloading {url.period_ending}...")

            updated_url = url.filing_details_xml
            if int(url.period_ending[:4]) >= 2019:
                updated_url = url.filing_details_htm
            
            try:
                self.download_url(updated_url)
            except TaxonomyNotFound:
                print("taxonomy file not found")
            except:
                updated_url = f"{url.submission_base_url}/{self.ticker.lower()}-{url.period_ending}.xml"
                self.download_url(updated_url)

            Path(f"{root_dir}/{self.ticker}").mkdir(parents=True, exist_ok=True)

            old_dir = f"{root_dir}/{url.cik}/{url.accession_number.replace('-', '')}"
            new_dir = f"{root_dir}/{self.ticker}/{url.period_ending}"
            
            if os.path.isdir(new_dir):
                new_dir = f"{root_dir}/{self.ticker}/{url.accession_number.replace('-', '')}"

            try:
                os.rename(old_dir, new_dir)
            except OSError:
                print(f"could not create {new_dir}")
            
        for old_dir in glob.glob(f"{root_dir}/000*"):
            shutil.rmtree(old_dir)

if __name__ == "__main__":
    logging.getLogger("xbrl_parser.cache").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description='Download SEC filings.')
    parser.add_argument('-t', '--ticker', required=True, help='Company ticker')
    parser.add_argument('-f', '--type', help='Type of filing', default='10-K')
    args = parser.parse_args()

    downloader = Downloader(args.ticker, args.type)
    downloader.download()