from datetime import date, timedelta
from dateutil import parser as dateparser
from dateutil.relativedelta import relativedelta
import re
import os
import logging
import glob

from xbrl.cache import HttpCache
from xbrl.instance import parse_xbrl, TimeFrameContext, InstantContext
from xbrl.linkbase import PresentationArc, CalculationArc

from statement_parser.parsers.htm import HTMParser
from statement_parser.expense_collection import Expenses
from statement_parser.utils import same_month_year

logging.getLogger("xbrl.cache").setLevel(logging.WARNING)


class XMLParser:
    def __init__(self, path, cache_dir="./cache/", compare_file=None, verbose=False, to_json=False):
        cache = HttpCache(cache_dir)
        self.instance = parse_xbrl(path, cache)
        self.compare_file = compare_file
        self.api_key = os.environ["FMP_API_KEY"]
        self.verbose = verbose
        self.to_json = to_json

        self.htm_parser = None
        self.load_htm_parser(path)
        
        if compare_file and not os.path.isfile(compare_file):
            raise ValueError(f"{compare_file} does not exist")

        self.fd_str = os.path.basename(os.path.dirname(path))
        self.ticker = os.path.basename(os.path.dirname(os.path.dirname(path))).upper()

        self.fd_y = self.fd_str[:4]
        self.fd_m = self.fd_str[4:6]
        self.fd_d = self.fd_str[6:]
        self.filing_date_end = date(int(self.fd_y), int(self.fd_m), int(self.fd_d))

        self.filing_type = '10-K'
        for f in self.instance.facts:
            if "DocumentType" in f.concept.xml_id:
                self.filing_type = f.value

        if self.filing_type == '10-K':
            self.filing_date_start = self.filing_date_end - relativedelta(years=1, months=1)
        else:
            self.filing_date_start = self.filing_date_end - relativedelta(months=3, weeks=1)

    def load_htm_parser(self, path):
        res = glob.glob(f"{os.path.dirname(path)}/*.htm")
        if len(res) == 0:
            return 

        with open(res[0]) as f:
            if 'ix:footnote' not in f.read():
                return
        
        self.htm_parser = HTMParser(res[0], path)

    def valid_range(self, ctx):
        grace_period = timedelta(40)
        ends_before_filing = ctx.end_date <= (self.filing_date_end + grace_period)
        starts_after_filing = ctx.start_date >= (self.filing_date_start - grace_period)
        return starts_after_filing and ends_before_filing

    def is_a_forecast(self, ctx):
        for segment in ctx.segments:
            if segment.dimension.name == "StatementScenarioAxis" and "Forecast" in segment.member.name:
                return True 
        return False

    def process(self):
        expenses = Expenses(self.instance, self.ticker, self.api_key, self.htm_parser, verbose=self.verbose)

        dimension_map = {}
        segment_maps = {}

        contexts = instant_contexts = {}

        for ctx_id, ctx in self.instance.context_map.items():
            should_append = False

            if isinstance(ctx, TimeFrameContext) and self.valid_range(ctx):
                should_append = True
            
            if "cumulativetodate" in ctx_id.lower():
                should_append = False

            if self.is_a_forecast(ctx):
                should_append = False

            if should_append:
                contexts[ctx_id] = ctx

        for fact in self.instance.facts:
            if fact.context.xml_id not in contexts:
                continue

            expenses.add_fact(fact)

        if self.compare_file:
            expenses.output_comparison(self.fd_y, self.compare_file)
        elif self.to_json:
            return expenses.output_json()
        else:
            expenses.output_all()
