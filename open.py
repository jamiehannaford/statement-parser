import argparse
from datetime import date
import webbrowser

from statement_parser.utils import get_filing_urls_to_download

parser = argparse.ArgumentParser(description='Download SEC filings.')

parser.add_argument('-c', '--ticker', required=True, help='Company ticker')
parser.add_argument('-t', '--type', help='Type of filing', default='10-K')
parser.add_argument('-y', '--year', required=True, type=int, help='Year of filing')

args = parser.parse_args()

count = 1
if args.type == "10-Q":
    count = 4

urls = get_filing_urls_to_download(args.type, args.ticker, count, 
    date(args.year, 1, 1).strftime("%Y-%m-%d"), 
    date(args.year, 12, 31).strftime("%Y-%m-%d"), False)

for url in urls:
    html_url = url.filing_details_url.replace("https://www.sec.gov", "")
    url = f"https://www.sec.gov/ix?doc={html_url}"

    chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    webbrowser.get(chrome_path).open(url)