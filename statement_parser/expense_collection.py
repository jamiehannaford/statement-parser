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

from statement_parser.validators.arcs import ArcValidator
from statement_parser.validators.dimensions import DimensionValidator
from statement_parser.validators.total import TotalValidator
from statement_parser.validators.segment import SegmentValidator
from statement_parser.validators.synonyms import SynonymValidator
from statement_parser.validators.other_income import OtherIncomeValidator
from statement_parser.validators.restructuring import RestructuringValidator
from statement_parser.validators.gain_loss import GainLossValidator
from statement_parser.validators.other_footnotes import OtherFootnotesValidator
from statement_parser.validators.other_hidden import OtherHiddenValidator

from statement_parser.labelset import LabelSet
from statement_parser.fact import NumericFact

from xbrl.instance import TextFact

field_mapping = {
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

class Expenses:
    def __init__(self, instance, ticker, api_key, file_parser, verbose=False):
        self.ticker = ticker
        self.api_key = api_key
        self.profile = self.get_profile()
        self.verbose = verbose
        self.instance = instance
        self.populate_labels()
        self.categories = [
            RestructuringExpenseGroup(instance, self.labels, self.profile),
            DepreciationAmortizationExpenseGroup(instance, self.labels, self.profile),
            DiscontinuedOperationsExpenseGroup(instance, self.labels, self.profile),
            WriteDownExpenseGroup(instance, self.labels, self.profile),
            NonRecurringOtherExpenseGroup(instance, self.labels, self.profile),
            InterestExpenseGroup(instance, self.labels, self.profile),
            InterestMinorityExpenseGroup(instance, self.labels, self.profile),
            LegalExpenseGroup(instance, self.labels, self.profile),
            CompanyDefinedOtherGroup(instance, self.labels, self.profile),
            AcquisitionsMergerGroup(instance, self.labels, self.profile),
            DerivativeGroup(instance, self.labels, self.profile),
            CurrencyGroup(instance, self.labels, self.profile),
            NonOperatingOtherExpenseGroup(instance, self.labels, self.profile),
            NonOperatingUnconsolidatedSubExpenseGroup(instance, self.labels, self.profile),
            FinancingGroup(instance, self.labels, self.profile),
        ]
        self.text_facts = []
        self.facts = []

        self.process_map = {}
        for cat in self.categories:
            self.process_map[cat.name] = []

        self.file_parser = file_parser
        if file_parser:
            self.file_parser.profile = self.profile 

    def populate_labels(self):
        self.labels = {}
        for lb in self.instance.taxonomy.lab_linkbases:
            for el in lb.extended_links:
                for rl in el.root_locators:
                    for c in rl.children:
                        for l in c.labels:
                            if rl.concept_id not in self.labels:
                                self.labels[rl.concept_id] = LabelSet()

                            self.labels[rl.concept_id].add(l)
    
    def get_yahoo_profile(self):
        try:
            url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{self.ticker}?modules=summaryProfile"
            res = requests.get(url).json()
            return res["quoteSummary"]["result"][0]["summaryProfile"]
        except KeyError:
            return None

    def get_profile(self):
        try:
            url = f"https://financialmodelingprep.com/api/v4/company-outlook?symbol={self.ticker}&apikey={self.api_key}"
            res = requests.get(url).json()
            return res["profile"]
        except KeyError:
            return self.get_yahoo_profile()

    def inspect_fact(self, validator, name):
        print(validator.__class__.__name__)
        for fact in self.facts:
            if name in fact.concept.xml_id:
                print(fact)

    def process_facts(self):
        validation_chain = [
            RestructuringValidator(self.instance, self.profile),
            SegmentValidator(self.instance, self.profile),
            TotalValidator(self.instance),
            DimensionValidator(self.instance),
            OtherIncomeValidator(self.instance, self.labels, self.profile),
            ArcValidator(self.instance, self.categories, self.labels),
            SynonymValidator(self.instance),
            GainLossValidator(self.instance, self.profile),
            OtherFootnotesValidator(self.instance, self.file_parser),
            OtherHiddenValidator(self.instance, self.file_parser, self.labels),
        ]

        for validator in validation_chain:
            self.facts = validator.process(self.facts)
            # self.inspect_fact(validator, "GoodwillImpairmentLoss")

        cat_map = {}
        for category in self.categories:
            cat_map[category.name] = category

        for category_name, facts in self.process_map.items():
            for fact in facts:
                if fact in self.facts:
                    cat_map[category_name].add(fact)

    def add_fact(self, fact):
        if isinstance(fact, TextFact):
            self.text_facts.append(fact)
            return

        for category in self.categories:
            if category.is_cost(fact, self.labels[fact.concept.xml_id]):
                fact = NumericFact(fact)
                self.process_map[category.name].append(fact)
                self.facts.append(fact)

    def output_json(self):
        self.process_facts()
        
        inverse_fields = {v: k for k, v in field_mapping.items()}

        output = {}
        for category in self.categories:
            subtotal, logs = category.output(self.verbose, text_facts=self.text_facts, shorten=False)
            json_key = inverse_fields[category.name]
            output[json_key] = subtotal

        return output

    def output_all(self):
        self.process_facts()

        total = 0
        for category in self.categories:
            subtotal, logs = category.output(self.verbose, text_facts=self.text_facts)
            total += subtotal
            print("\n".join(logs))
            print("="*40)

        print(f"GRAND TOTAL {total}")
    
    def perc(self, a, b):
        return round((min(a, b) / max(a, b)) * 100, 2)

    def output_comparison(self, filing_year, compare_file):
        self.process_facts()

        with open(compare_file, "r") as json_file:
            data = json.load(json_file)
        
        filing = None
        for f in data:
            if f["periodEndDate"].startswith(f"{filing_year}-"):
                filing = f

        if filing is None:
            for f in data:
                if str(f["fiscalYear"]).startswith(f"{filing_year}-"):
                    filing = f

        if filing is None:
            raise ValueError(f"{filing_year} filing date not found in JSON")

        categories = {}
        for category in self.categories:
            categories[category.name] = category

        actual_total = 0
        expected_total = 0

        for key, name in field_mapping.items():
            category = categories[name]
            filing_val = round(filing[key] / 1000000, 2)
            subtotal, logs = category.output(self.verbose, text_facts=self.text_facts)
            
            actual_total += subtotal
            expected_total += filing_val

            subtotal = round(float(subtotal), 2)
            title = name.upper()
            correct = filing_val == subtotal

            if correct:
                emoji = u"\u2705"
            else:
                emoji = u"\u274C"

            print(emoji, title, f"expected={filing_val}", f"actual={subtotal}")
            if not correct and logs:
                print("\n".join(logs[1:-1]))
            
            print("="*40)

        
        print(f"EXPECTED {expected_total} ACTUAL {actual_total} ({self.perc(expected_total, actual_total)}%)")