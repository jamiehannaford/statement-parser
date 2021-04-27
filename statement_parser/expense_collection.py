import json

import requests

from statement_parser.expenses.constants import *
from statement_parser.expenses.company_other import CompanyDefinedOtherGroup
from statement_parser.expenses.discontinued_operations import DiscontinuedOperationsExpenseGroup
from statement_parser.expenses.depreciation_amortization import DepreciationAmortizationExpenseGroup
from statement_parser.expenses.restructuring import RestructuringExpenseGroup
from statement_parser.expenses.write_down import WriteDownExpenseGroup
from statement_parser.expenses.non_recurring_other import NonRecurringOtherExpenseGroup
from statement_parser.expenses.interest import InterestExpenseGroup
from statement_parser.expenses.interest_minority import InterestMinorityExpenseGroup
from statement_parser.expenses.legal import LegalExpenseGroup
from statement_parser.expenses.acquisitions import AcquisitionsMergerGroup
from statement_parser.expenses.derivative import DerivativeGroup
from statement_parser.expenses.currency import CurrencyGroup
from statement_parser.expenses.non_operating_other import NonOperatingOtherExpenseGroup, NonOperatingUnconsolidatedSubExpenseGroup
from statement_parser.expenses.financing import FinancingGroup

class Expenses:
    def __init__(self, instance, ticker, api_key):
        self.ticker = ticker
        self.api_key = api_key
        self.profile = self.get_profile()

        self.categories = [
            RestructuringExpenseGroup(instance),
            # DepreciationAmortizationExpenseGroup(instance),
            DiscontinuedOperationsExpenseGroup(instance),
            WriteDownExpenseGroup(instance),
            NonRecurringOtherExpenseGroup(instance),
            InterestExpenseGroup(instance),
            InterestMinorityExpenseGroup(instance),
            LegalExpenseGroup(instance),
            CompanyDefinedOtherGroup(instance),
            AcquisitionsMergerGroup(instance),
            DerivativeGroup(instance),
            CurrencyGroup(instance),
            NonOperatingOtherExpenseGroup(instance),
            NonOperatingUnconsolidatedSubExpenseGroup(instance),
            FinancingGroup(instance),
        ]
    
    def get_profile(self):
        url = f"https://financialmodelingprep.com/api/v4/company-outlook?symbol={self.ticker}&apikey={self.api_key}"
        res = requests.get(url).json()
        return res["profile"]

    def process_fact(self, fact):
        for category in self.categories:
            if category.is_cost(fact, self.profile):
                category.add(fact)

    def output_all(self):
        total = 0
        for category in self.categories:
            subtotal, logs = category.output()
            total += subtotal
            print("\n".join(logs))
            print("="*40)

        print(f"GRAND TOTAL {total}")
    
    def output_comparison(self, filing_year, compare_file):
        with open(compare_file, "r") as json_file:
            data = json.load(json_file)
        
        filing = None
        for f in data:
            if f["periodEndDate"].startswith(f"{filing_year}-"):
                filing = f

        if filing is None:
            for f in data:
                if f["fiscalYear"].startswith(f"{filing_year}-"):
                    filing = f

        if filing is None:
            raise ValueError(f"{filing_date} filing date not found in JSON")
        
        mapping = {
            "expensesAcquisitionMerger": NAME_COMPANY_ACQ_MERGER,
            "expensesDepreciationAndAmortization": NAME_DEPR_AMORT,
            "expensesDerivative": NAME_DERIVATIVE,
            "expensesDiscontinuedOperations": NAME_DISC_OPS,
            "expensesForeignCurrency": NAME_CURRENCY,
            "expensesInterest": NAME_INTEREST,
            "expensesInterestMinority": NAME_INT_MIN,
            "expensesLegalRegulatoryInsurance": NAME_LEGAL,
            "expensesNonOperatingCompanyDefinedOther": NAME_COMPANY_OTHER,
            "expensesNonOperatingOther": NAME_NOO,
            "expensesNonOperatingSubsidiaryUnconsolidated": NAME_NOUS,
            "expensesNonRecurringOther": NAME_NRO,
            "expensesOtherFinancing": NAME_FIN,
            "expensesRestructuring": NAME_RESTRUCT,
            "expensesWriteDown": NAME_WRITE_DOWN
        }

        categories = {}
        for category in self.categories:
            categories[category.name] = category

        for key, name in mapping.items():
            category = categories[name]
            filing_val = round(filing[key] / 1000000, 2)
            total, logs = category.output()

            total = round(float(total), 2)
            title = name.upper()
            diff = abs(abs(total) - abs(filing_val))
            
            if int(diff) == 0:
                perc = 1
            elif diff > 0 and (int(filing_val) == 0 or int(total) == 0):
                perc = 0
            else:
                perc = abs(diff / filing_val)

            if perc == 1:
                emoji = u"\u2705"
            else:
                emoji = u"\u274C"

            print(emoji, title, f"expected={filing_val}", f"actual={total}")
            if diff > 0 and logs:
                print("\n".join(logs[1:-1]))
            
            print("="*40)