import argparse
import glob
import os
import re
import sys

from statement_parser.parser import FileParser

parser = argparse.ArgumentParser(description='Download SEC filings.')
parser.add_argument('-c', '--ticker', required=True, help='Company ticker')
parser.add_argument('-y', '--year', help='Filing year')
args = parser.parse_args()

company_dir = f"cache/www.sec.gov/Archives/edgar/data/{args.ticker}"

if not os.path.isdir(company_dir):
    print(f"{company_dir} filing does not exist, please download it first")
    sys.exit()

for filing in glob.glob(f"{company_dir}/{args.year}*/*.xml"):
    exts = ('_cal.xml', '_def.xml', '_lab.xml', '_pre.xml')
    if filing.endswith(exts):
        continue
    
    parser = FileParser(filing)
    parser.process()