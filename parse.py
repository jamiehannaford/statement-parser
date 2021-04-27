import argparse
import glob
import os
import re
import sys
from datetime import date

import pyperclip
from statement_parser.parser import FileParser
from download import Downloader

parser = argparse.ArgumentParser(description='Download SEC filings.')
parser.add_argument('-t', '--ticker', required=True, help='Company ticker')
parser.add_argument('-y', '--year', help='Filing year')
parser.add_argument('-c', '--compare', default=False, action='store_true', help='Compare with reference set')

args = parser.parse_args()

company_dir = f"cache/www.sec.gov/Archives/edgar/data/{args.ticker}"
filings = glob.glob(f"{company_dir}/{args.year}*/*.xml")

if not filings:
    d = Downloader(args.ticker)
    d.download(
        from_date=date(int(args.year)-1, 1, 1).strftime("%Y-%m-%d"), 
        to_date=date(int(args.year)+1, 12, 31).strftime("%Y-%m-%d"))
    filings = glob.glob(f"{company_dir}/{args.year}*/*.xml")

if not filings:
    print(f"{company_dir} filing does not exist, please download it first")
    sys.exit()

for filing in filings:
    exts = ('_cal.xml', '_def.xml', '_lab.xml', '_pre.xml')
    if filing.endswith(exts):
        continue
    
    compare_file = None 
    if args.compare:
        compare_file = f"../stock-data/{args.ticker}.json"

    parser = FileParser(filing, compare_file=compare_file)
    parser.process()

    print("XML file:", filing)
    pyperclip.copy(filing)