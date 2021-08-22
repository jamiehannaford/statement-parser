import argparse
import glob
import json
import os
import random

import pandas as pd
from tabulate import tabulate
from statement_parser.parsers.xml import XMLParser

def find_filing(ticker, fiscal_year):
    for filing in glob.glob(f"data/{ticker}/{fiscal_year}*/*.xml"):
        exts = ('_cal.xml', '_def.xml', '_lab.xml', '_pre.xml')
        if filing.endswith(exts):
            continue
        return filing
    return None

def process_filing(filing_path):
    parser = XMLParser(filing_path, to_json=True)
    return parser.process()

def format_int(a):
    return round(a/1000000, 2)

def emoji(a, b):
    if a == b:
        return u"\u2705"
    else:
        return u"\u274C"

def run_random(count, save):
    lst = []
    for res_file in glob.glob(f"tests/results/*.json"):
        ticker = os.path.basename(res_file.replace(".json", ""))
        with open(res_file) as f:
            data = json.load(f)
            for y in data:
                lst.append(f"{ticker.lower()}_{y}")
    
    for choice in random.choices(lst, k=int(count)):
        parts = choice.split("_")
        print(f"running {choice}")
        run_test(parts[0], parts[1], save)

def run_test(ticker, year, save):
    search_query = "stock-data/*.json"
    if ticker:
        search_query = f"stock-data/{ticker.lower()}.json"

    for ticker_file in glob.glob(search_query):
        if ticker_file.endswith("10q.json"):
            continue
        ticker = os.path.basename(ticker_file.replace(".json", ""))

        ticker_results = {}
        compare_cache = False
        cache_file = f"tests/results/{ticker}.json"

        if os.path.isfile(cache_file):
            with open(cache_file) as f:
                compare_cache = True
                ticker_results = json.load(f)

        with open(ticker_file) as json_file:
            data = json.load(json_file)
            
            for filing in data:
                end_year = filing['periodEndDate'].split("-")[0]
                if year and end_year != year:
                    continue

                filing_path = find_filing(ticker, end_year)
                if not filing_path:
                    continue

                print("="*50)
                print(f"{ticker.upper()} {end_year} - {filing_path}")
                print()

                result = process_filing(filing_path)
                if not result:
                    print("Skipping")
                    continue

                if save:
                    ticker_results[end_year] = result

                correct = 0

                keys = []
                exps = []
                acts = []
                cached = []

                total_exp = 0
                total_act = 0
                total_cached = 0

                for key, val in result.items():
                    total_exp += filing[key]
                    total_act += val 

                    if filing[key] == val:
                        correct += 1

                    keys.append(key)
                    exps.append(f"{emoji(filing[key], val)} {format_int(filing[key])}")
                    acts.append(format_int(val))

                    if compare_cache:
                        cache_res = ticker_results[end_year][key]
                        total_cached += cache_res
                        cached.append(f"{emoji(cache_res, val)} {format_int(cache_res)}")

                keys.append("")
                exps.append("")
                acts.append("")
                cached.append("")

                keys.append("TOTAL")
                acts.append(format_int(total_act))
                exps.append(f"{emoji(total_exp, total_act)} {format_int(total_exp)}")
                cached.append(f"{emoji(total_cached, total_act)} {format_int(total_cached)}")

                keys.append("TOTAL (NO AMORTIZATION)")

                total_exp_non_dep = total_exp-filing['expensesDepreciationAndAmortization']
                total_act_non_dep = total_act-result['expensesDepreciationAndAmortization']
                acts.append(format_int(total_act_non_dep))
                exps.append(f"{emoji(total_exp_non_dep, total_act_non_dep)} {format_int(total_exp_non_dep)}")

                if total_cached:
                    total_act_non_cached = total_cached-ticker_results[end_year]['expensesDepreciationAndAmortization']
                    cached.append(f"{emoji(total_act_non_cached, total_act_non_dep)} {format_int(total_act_non_cached)}")

                if compare_cache:
                    df = pd.DataFrame({"expense": keys, "reference": exps, "expected": cached, "actual": acts})
                else:
                    df = pd.DataFrame({"expense": keys, "expected": exps, "actual": acts})

                print(tabulate(df, showindex=False, headers=df.columns))
                print(f"Correct {correct}/{len(result)}")

            if save:
                output_file = f"tests/results/{ticker}.json"
                with open(output_file, "w") as f:
                    f.write(json.dumps(ticker_results, indent=3))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download SEC filings.')
    parser.add_argument('-t', '--ticker', help='Company ticker')
    parser.add_argument('-s', '--save', default=False, action='store_true', help='Save results for later tests')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--all', action='store_true', help="Run all tests")
    group.add_argument('-n', '--num', help="Run n random tests")
    
    args = parser.parse_args()

    if args.all:
        run_test(args.ticker, "", args.save)
    else:
        run_random(args.num, args.save)
