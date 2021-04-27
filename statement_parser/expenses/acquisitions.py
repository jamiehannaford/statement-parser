from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_COMPANY_ACQ_MERGER

from xbrl_parser.instance import NumericFact

TAGS_ACQUISITIONS_MERGER = [
    "businesscombinationacquisitionrelatedcosts",
    "businesscombinationintegrationrelatedcosts",
    "businesscombinationacquisitionrelatedcoststransactioncosts",
    "businesscombinationcontingentconsiderationarrangementschangeinamountofcontingentconsiderationliability1",
]


class AcquisitionsMergerGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_COMPANY_ACQ_MERGER, TAGS_ACQUISITIONS_MERGER, instance)
    
    def is_cost(self, fact, profile):
        if super().is_cost(fact, profile):
            return True 
        
        if not isinstance(fact, NumericFact):
            return False

        concept_id = fact.concept.xml_id.lower()
        main_terms = ["acquisition", "transaction", "merger"]
        other_terms = ["charge", "cost", "expense"]
        return all(
            (any(w in concept_id for w in main_terms), 
            any(w in concept_id for w in other_terms)))

    def generate_cost(self, fact):
        return AcquisitionsMergerCost(fact)


class AcquisitionsMergerCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)