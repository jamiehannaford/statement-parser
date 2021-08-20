import argparse
from datetime import date
import webbrowser
import time

from download import Downloader

parser = argparse.ArgumentParser(description='Download SEC filings.')

parser.add_argument('-t', '--ticker', required=True, help='Company ticker')
parser.add_argument('-f', '--type', help='Type of filing', default='10-K')
parser.add_argument('-y', '--year', required=True, type=int, help='Year of filing')

args = parser.parse_args()

from_d = date(args.year, 1, 1).strftime("%Y-%m-%d")
to_d = date(args.year+1, 1, 1).strftime("%Y-%m-%d")

d = Downloader(args.ticker, filing_type=args.type)
urls = d.get_urls(from_date=from_d, to_date=to_d)

for url in urls:
    html_url = url.filing_details_url.replace("https://www.sec.gov", "")
    url = f"https://www.sec.gov/ix?doc={html_url}"

    chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    webbrowser.get(chrome_path).open(url)