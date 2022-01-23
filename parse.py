import argparse
import glob
import os
import re
import sys
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import webbrowser
import json
import mysql.connector

import pyperclip

from statement_parser.parsers.xml import XMLParser
from download import Downloader

class Parser:
    def __init__(self, ticker, num_quarters=4, year=False, compare=False, verbose=False, filing_type='10-K',
        cik='', json=False, ttm=False, quarter=False, save_mysql=False):
        self.ticker = ticker 
        self.num_quarters = num_quarters
        self.year = year
        self.compare = compare
        self.verbose = verbose
        self.filing_type = filing_type
        self.cik = cik
        self.json = json
        self.ttm = ttm
        self.quarter = quarter
        self.save_mysql = save_mysql
        
        if not (self.ticker or self.cik):
            raise RuntimeError('No ticker or cik provided')
    
    def process(self):
        if self.ttm or self.quarter or self.num_quarters:
            self.filing_type = "10-Q"
        
        from_date = f"{self.year}-01-01"
        to_date = f"{int(self.year)+1}-12-31" # necessary because providing 2020 would result in 2019 filing (filed in 2020)

        if self.ttm:
            self.num_quarters = 4

        if self.num_quarters:
            self.json = True
            self.year = datetime.now().year
            to_date = datetime.now().strftime("%Y-%m-%d")
            from_date = (datetime.now() - relativedelta(months=3*self.num_quarters)).strftime("%Y-%m-%d")

        d = Downloader(self.ticker, cik=self.cik, filing_type=self.filing_type, num_quarters=self.num_quarters)
        d.download(from_date=from_date, to_date=to_date)

        filings = self.get_filings()
        if not filings:
            print(f"filing does not exist, please download it first")
            sys.exit()

        ttm_values = {}

        for filing in filings:
            exts = ('_cal.xml', '_def.xml', '_lab.xml', '_pre.xml')
            if filing.endswith(exts):
                continue
            
            compare_file = None 
            if self.compare:
                compare_file = f"../stock-data/{self.ticker}.json"

            parser = XMLParser(filing, to_json=self.json, compare_file=compare_file, verbose=self.verbose)
            output = parser.process()

            if self.num_quarters:
                ttm_values[parser.fd_str] = {'type': parser.filing_type}
                for key, val in output.items():
                    ttm_values[parser.fd_str][key] = val
                continue

            if self.json:
                print(json.dumps(output))
            else:
                print("XML file:", filing)
                pyperclip.copy(filing)
                print("="*50)
                print()

        if self.num_quarters:
            if self.save_mysql:
                self.persist(parser, output)
            else: 
                print(json.dumps(ttm_values))

    def persist(self, parser, output):
        db = mysql.connector.connect(
            host=os.environ['MYSQL_HOST'],
            user=os.environ['MYSQL_USER'],
            password=os.environ['MYSQL_PASS'],
            database='expensifier'
        )

        query = """
        INSERT INTO filings (
            ticker, filing_date, filing_type,
            expenses_restructuring,
            expenses_depreciation_amortization,
            expenses_discontinued_operations,
            expenses_write_down,
            expenses_non_recurring_other,
            expenses_interest,
            expenses_interest_minority,
            expenses_legal_regulatory_insurance,
            expenses_non_operating_company_defined_other,
            expenses_acquisitions_mergers,
            expenses_derivative,
            expenses_foreign_currency,
            expenses_non_operating_other,
            expenses_non_operating_other_subsidiary_unconsolidated,
            expenses_other_financing
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        vals = (
            parser.ticker, parser.fd_str, parser.filing_type,
            output['expensesRestructuring'],
            output['expensesDepreciationAndAmortization'],
            output['expensesDiscontinuedOperations'],
            output['expensesWriteDown'],
            output['expensesNonRecurringOther'],
            output['expensesInterest'],
            output['expensesInterestMinority'],
            output['expensesLegalRegulatoryInsurance'],
            output['expensesNonOperatingCompanyDefinedOther'],
            output['expensesAcquisitionMerger'],
            output['expensesDerivative'],
            output['expensesForeignCurrency'],
            output['expensesNonOperatingOther'],
            output['expensesNonOperatingSubsidiaryUnconsolidated'],
            output['expensesOtherFinancing'],
        )
        curs = db.cursor()
        curs.execute(query, vals)
        db.commit()
        curs.close()
        db.close()

    def get_filings(self):
        company_dir = f"data/{self.ticker}"
        time_val = self.year
        if self.quarter:
            time_val += self.quarter

        if self.num_quarters:
            dirs = os.listdir(company_dir)
            dirs.sort()
            files = []
            for _dir in dirs[len(dirs)-self.num_quarters:]:
                files += glob.glob(f"{company_dir}/{_dir}*/*.xml")
            return files

        return glob.glob(f"{company_dir}/{time_val}*/*.xml")


if __name__ == "__main__":
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

    p = Parser(**vars(args))
    p.process()