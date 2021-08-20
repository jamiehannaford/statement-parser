import argparse
import glob
import os
import re
import sys
from datetime import date
import webbrowser
import json

import pyperclip

from statement_parser.parsers.xml import XMLParser
from download import Downloader

parser = argparse.ArgumentParser(description='Download SEC filings.')
parser.add_argument('-y', '--year', help='Filing year')
parser.add_argument('-c', '--compare', default=False, action='store_true', help='Compare with reference set')
parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbose logging')
parser.add_argument('-f', '--filing-type', default="10-k", help='Type of filing')
parser.add_argument('-t', '--ticker', help='Company ticker')
parser.add_argument('-k', '--cik', help='The CIK')
parser.add_argument('-j', '--json', default=False, action='store_true', help='Output to JSON')

args = parser.parse_args()

if not (args.ticker or args.cik):
    parser.error('No ticker or cik provided')

ticker = args.ticker
d = Downloader(args.ticker, cik=args.cik, filing_type=args.filing_type)

def get_filings(ticker):
    company_dir = f"data/{ticker}"
    return glob.glob(f"{company_dir}/{args.year}*/*.xml")

filings = get_filings(ticker)
if not filings:
    d.download(from_date=f"{args.year}0101", to_date=f"{args.year}1231")
    ticker = d.ticker

filings = get_filings(ticker)
if not filings:
    print(f"filing does not exist, please download it first")
    sys.exit()

for filing in filings:
    exts = ('_cal.xml', '_def.xml', '_lab.xml', '_pre.xml')
    if filing.endswith(exts):
        continue
    
    compare_file = None 
    if args.compare:
        compare_file = f"../stock-data/{args.ticker}.json"

    parser = XMLParser(filing, to_json=args.json, compare_file=compare_file, verbose=args.verbose)
    output = parser.process()

    if args.json:
        print(json.dumps(output))
    else:
        print("XML file:", filing)
        pyperclip.copy(filing)
        print("="*50)
        print()

    break