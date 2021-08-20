import re

from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_COMPANY_ACQ_MERGER

from xbrl.instance import NumericFact

TAGS_ACQUISITIONS_MERGER = [
    "BusinessCombinationAcquisitionRelatedCosts".lower(),
    "businesscombinationacquisitionrelatedcoststransactioncosts",
    "BusinessCombinationTerminationFeeSpecifiedCircumstancesPayabletoTarget".lower(),
    "BusinessCombinationStepAcquisitionEquityInterestInAcquireeRemeasurementGainOrLoss".lower(),
    "BusinessCombinationContingentConsiderationArrangementsChangeInAmountOfContingentConsiderationLiability1".lower(), # HUN 2019
]

class AcquisitionsMergerGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_COMPANY_ACQ_MERGER, TAGS_ACQUISITIONS_MERGER, instance, 
            labels=labels, profile=profile)
        
    def group_specific_processing(self, costs):
        return self.filter_by_highest_term(["BusinessCombination", "Acquisition", "transaction", "RelatedCosts"], costs)

    def is_cost(self, fact, label):
        if super().is_cost(fact, label):
            return True 
        
        if not isinstance(fact, NumericFact):
            return False

        concept_id = fact.concept.xml_id.lower()
        excluded_terms = ["restructuring", "gainloss", "amortization", "proceedsfrom", 
            "policyacquisition", "PolicyBenefitReserves", "relatedparty", "unallocated", 
            "stepup", "hedges", "potential"]   
        if any(w.lower() in concept_id for w in excluded_terms):
            return False

        main_terms = ["acquisition", "transaction", "merger", "businesscombination"]
        other_terms = ["charges?", "costs?", "expenses?", "fees?"]
        regex_patt = "(" + "|".join(main_terms) + ')(.*)(' + "|".join(other_terms) + ")$"
        res = re.search(regex_patt, concept_id)
        return res is not None

    def generate_cost(self, fact, label, text_blocks=None):
        return AcquisitionsMergerCost(fact, label)


class AcquisitionsMergerCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)