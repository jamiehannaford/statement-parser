from datetime import date, timedelta
from dateutil import parser as dateparser
from dateutil.relativedelta import relativedelta
import re
import os
import logging

from xbrl_parser.cache import HttpCache
from xbrl_parser.instance import parse_xbrl, TimeFrameContext, InstantContext
from xbrl_parser.linkbase import PresentationArc

from statement_parser.expenses import Expenses
from statement_parser.utils import same_month_year

logging.getLogger("xbrl_parser.cache").setLevel(logging.WARNING)


class FileParser:
    def __init__(self, path, cache_dir = "./cache/"):
        cache = HttpCache(cache_dir)
        self.instance = parse_xbrl(path, cache, os.path.dirname(path))
        self.fd_str = os.path.basename(os.path.dirname(path))

        fd_y = self.fd_str[:4]
        fd_m = self.fd_str[4:6]
        fd_d = self.fd_str[6:]
        self.filing_date_end = date(int(fd_y), int(fd_m), int(fd_d))
        self.filing_date_start = self.filing_date_end - relativedelta(years=1, months=1)

    def tag_name(self, name):
        if self.is_xbrli:
            name = f"xbrli:{name}"
        return name

    def lookup(self, linkbases, search):
        for locator in linkbases.extended_links[0].root_locators:
            if search.lower() not in locator.concept_id.lower(): continue
            # Here you have the label
            label: str = locator.children[0].labels[0].text
            print(label)

    def populate_labels(self):
        labels = {}
        for lb in self.instance.taxonomy.lab_linkbases:
            for el in lb.extended_links:
                for rl in el.root_locators:
                    for c in rl.children:
                        for l in c.labels:
                            if l.label_type.endswith("/label"):
                                labels[rl.concept_id] = l.text
        return labels

    def follow_pres_elem(self, elem, indent):
        print(" " * indent * 2, elem)

        if isinstance(elem, PresentationArc):
            print(" " * indent * 2, "order", elem.order) 
            return self.follow_pres_elem(elem.to_locator, indent + 1)

        if len(elem.children) == 0:
            return elem
        
        for i, child in enumerate(elem.children):
            self.follow_pres_elem(child, indent+1)

    def populate_pre_map(self):
        pres = {}
        for lb in self.instance.taxonomy.pre_linkbases:
            for el in lb.extended_links:
                for rl in el.root_locators:
                    self.follow_pres_elem(rl, 0)
        return pres

    def valid_range(self, ctx):
        if ctx.end_date - ctx.start_date <= timedelta(10 * 30):
            return False

        grace_period = timedelta(40)
        ends_before_filing = ctx.end_date <= (self.filing_date_end + grace_period)
        starts_after_filing = ctx.start_date >= (self.filing_date_start - grace_period)

        return starts_after_filing and ends_before_filing

    def process(self):
        expenses = Expenses(self.instance.taxonomy.pre_linkbases)

        root_concept_ids = []
        for elr in self.instance.taxonomy.link_roles:
            if elr.calculation_link is None or len(elr.calculation_link.root_locators) == 0:
                continue
            for loc in elr.calculation_link.root_locators:
                for child in loc.children:
                    # print(child.to_locator)
                    root_concept_ids.append(child.to_locator.concept_id)

        contexts = {}
        for ctx_id, ctx in self.instance.context_map.items():
            should_append = False

            if isinstance(ctx, TimeFrameContext) and self.valid_range(ctx):
                should_append = True
            
            if "cumulativetodate" in ctx_id.lower():
                should_append = False

            if should_append:
                contexts[ctx_id] = ctx

        all_concepts = {}
        for fact in self.instance.facts:
            concept_id = fact.concept.xml_id
            if concept_id not in all_concepts:
                all_concepts[concept_id] = []
            existing_vals = [f for f in all_concepts[concept_id] if f.value == fact.value]
            if fact.context.xml_id in contexts and len(existing_vals) == 0:
                all_concepts[concept_id].append(fact)

        allowed_concepts = [
            # "us-gaap_DeconsolidationGainOrLossAmount",
            # "pfe_AmortizationOfIntangibleAssetsNotAssociatedWithSingleFunction"
        ]

        for concept_id, facts in all_concepts.items():
            for fact in facts:
                if fact.context.xml_id not in contexts:
                    continue
                if concept_id not in root_concept_ids:
                    continue
                expenses.process_fact(fact)

        expenses.output_all()

        # for concept_id, facts in all_concepts.items():
        #     for fact in facts:
                # if fact.context.xml_id not in contexts:
                #     continue
                # if restructuring_costs.is_cost(fact):
                    # restructuring_costs.add(fact)
        # restructuring_costs.output()