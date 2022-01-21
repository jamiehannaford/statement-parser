import argparse
import glob
import os
import re
import sys
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import webbrowser
import json

import pyperclip

from statement_parser.parsers.xml import XMLParser
from download import Downloader

parser = argparse.ArgumentParser(description='Download SEC filings.')
parser.add_argument('-y', '--year', help='Filing year')
parser.add_argument('-c', '--compare', default=False, action='store_true', help='Compare with reference set')
parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose logging')
parser.add_argument('-f', '--filing-type', default="10-K", help='Type of filing')
parser.add_argument('-t', '--ticker', help='Company ticker')
parser.add_argument('-k', '--cik', help='The CIK')
parser.add_argument('-j', '--json', default=False, action='store_true', help='Output to JSON')
parser.add_argument('-r', '--ttm', default=False, action='store_true', help='The TTM value for this company')
parser.add_argument('-q', '--quarter', help='The specific quarter')
parser.add_argument('-n', '--num-quarters', type=int, help='The number of quarters from now dating backwards')

args = parser.parse_args()

if not (args.ticker or args.cik):
    parser.error('No ticker or cik provided')

filing_type = args.filing_type
if args.ttm or args.quarter or args.num_quarters:
    filing_type = '10-Q'

from_date = f"{args.year}-01-01"
to_date = f"{args.year}-12-31"

if args.ttm:
    args.num_quarters = 4

if args.num_quarters:
    to_date = datetime.now().strftime("%Y-%m-%d")
    args.json = True
    args.year = datetime.now().year
    from_date = (datetime.now() - relativedelta(months=3*args.num_quarters)).strftime("%Y-%m-%d")

print(filing_type, from_date, to_date)

ticker = args.ticker
d = Downloader(args.ticker, cik=args.cik, filing_type=filing_type, num_quarters=args.num_quarters)
d.download(from_date=from_date, to_date=to_date)

def get_filings(ticker):
    company_dir = f"data/{ticker}"
    time_val = args.year
    if args.quarter:
        time_val += args.quarter

    if args.num_quarters:
        dirs = os.listdir(company_dir)
        dirs.sort()
        files = []
        for _dir in dirs[len(dirs)-args.num_quarters:]:
            files += glob.glob(f"{company_dir}/{_dir}*/*.xml")
        return files

    return glob.glob(f"{company_dir}/{time_val}*/*.xml")

filings = get_filings(ticker)
if not filings:
    print(f"filing does not exist, please download it first")
    sys.exit()

ttm_values = {}

for filing in filings:
    exts = ('_cal.xml', '_def.xml', '_lab.xml', '_pre.xml')
    if filing.endswith(exts):
        continue
    
    compare_file = None 
    if args.compare:
        compare_file = f"../stock-data/{args.ticker}.json"

    parser = XMLParser(filing, to_json=args.json, compare_file=compare_file, verbose=args.verbose)
    output = parser.process()

    if args.num_quarters:
        ttm_values[parser.fd_str] = {'type': parser.filing_type}
        for key, val in output.items():
            ttm_values[parser.fd_str][key] = val
        continue

    if args.json:
        print(json.dumps(output))
    else:
        print("XML file:", filing)
        pyperclip.copy(filing)
        print("="*50)
        print()

if args.num_quarters:
    print(json.dumps(ttm_values))
