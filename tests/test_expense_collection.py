import unittest 
import datetime
import io
import contextlib

from xbrl.cache import HttpCache 
from xbrl.instance import parse_xbrl

from statement_parser.expense_collection import Expenses
from statement_parser.labelset import LabelSet

class TestXMLParser(unittest.TestCase): 

    def test_parse_labels(self):
        cache = HttpCache("cache")
        instance = parse_xbrl("tests/data/example.xml", cache)
        expenses = Expenses(instance, "", "", None)
        
        ls = expenses.labels['example_Assets']
        self.assertIsInstance(ls, LabelSet)
        self.assertTrue(ls.any_contains("Assets, total"))
        self.assertFalse(ls.any_contains("foo"))

    def test_output_json(self):
        cache = HttpCache("cache")
        instance = parse_xbrl("tests/data/example.xml", cache)
        expenses = Expenses(instance, "", "", None)
        expenses.add_fact(instance.facts[0])

        expected = {
            'expensesRestructuring': 500000000.0, 
            'expensesDepreciationAndAmortization': 0, 
            'expensesDiscontinuedOperations': 0, 
            'expensesWriteDown': 0, 
            'expensesNonRecurringOther': 0, 
            'expensesInterest': 0, 
            'expensesInterestMinority': 0, 
            'expensesLegalRegulatoryInsurance': 0, 
            'expensesNonOperatingCompanyDefinedOther': 0, 
            'expensesAcquisitionMerger': 0, 
            'expensesDerivative': 0, 
            'expensesForeignCurrency': 0, 
            'expensesNonOperatingOther': 0, 
            'expensesNonOperatingSubsidiaryUnconsolidated': 0, 
            'expensesOtherFinancing': 0}

        actual = expenses.output_json()
        self.assertEqual(actual, expected)

    def test_output_all(self):
        cache = HttpCache("cache")
        instance = parse_xbrl("tests/data/example.xml", cache)
        expenses = Expenses(instance, "", "", None)
        expenses.add_fact(instance.facts[0])

        expected = """
RESTRUCTURING
- us-gaap_SeveranceCosts1 500.0
TOTAL 500.0
========================================
DEPRECIATION AMORTIZATION
TOTAL 0
========================================
DISCONTINUED OPERATIONS
TOTAL 0
========================================
WRITE DOWNS
TOTAL 0
========================================
NON-RECURRING OTHER
TOTAL 0
========================================
INTEREST
TOTAL 0
========================================
MINORITY INTEREST
TOTAL 0
========================================
LEGAL, REGULATORY AND INSURANCE
TOTAL 0
========================================
COMPANY-DEFINED OTHER
TOTAL 0
========================================
ACQUISITIONS AND MERGER
TOTAL 0
========================================
DERIVATIVES
TOTAL 0
========================================
FOREIGN CURRENCY
TOTAL 0
========================================
NON-OPERATING OTHER
TOTAL 0
========================================
NON-OPERATING UNCONSOLIDATED SUBSIDIARIES
TOTAL 0
========================================
OTHER FINANCING
TOTAL 0
========================================
GRAND TOTAL 500.0
"""

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            expenses.output_all()
        
        self.assertEqual(f.getvalue().strip(), expected.strip())

