from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_INT_MIN

from xbrl_parser.instance import TimeFrameContext

TAGS_INTEREST_MINORITY = [
    "NetIncomeLossAttributableToNoncontrollingInterest".lower(),
    "IncomeLossFromContinuingOperationsAttributableToNoncontrollingEntity".lower(), # AIG 2019
    "ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest".lower(),
    "NetIncomeLossAttributableToNonredeemableNoncontrollingInterest".lower(),
]

PREC_IM_TAGS = [
    "us-gaap_NetIncomeLossAttributableToNoncontrollingInterest".lower()
]

class InterestMinorityExpenseGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_INT_MIN, TAGS_INTEREST_MINORITY, instance, 
            precedent_tags=PREC_IM_TAGS, labels=labels, profile=profile)

    def is_cost(self, fact, label):
        parent_tags = [
            "us-gaap_ProfitLoss",
            "us-gaap_IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest",
        ]
        if fact.concept.xml_id in parent_tags:
            for segment in fact.context.segments:
                if "NoncontrollingInterestMember" in segment.member.name:
                    return True 
            return False
        
        return super().is_cost(fact, label)

    def generate_cost(self, fact, label, text_blocks=None):
        return InterestMinorityCost(fact, label)

class InterestMinorityCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)

    def validate(self, text_facts=[]):
        super().validate(text_facts=text_facts)