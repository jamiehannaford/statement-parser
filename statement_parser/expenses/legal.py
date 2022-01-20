from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_LEGAL

from xbrl.instance import NumericFact

TAGS_LEGAL = [
    "GainLossRelatedToLitigationSettlement".lower(),
    "LossContingencyLossInPeriod".lower(),
    "PaymentsForLegalSettlements".lower(),
    "LitigationSettlementExpense".lower(),
    "DefinedBenefitPlanRecognizedNetGainLossDueToSettlements1".lower(),
]

class LegalExpenseGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_LEGAL, TAGS_LEGAL, instance, labels=labels, profile=profile)
        self.filter_highest_only = True

    def is_cost(self, fact, label):
        if super().is_cost(fact, label):
            return True
        
        if not isinstance(fact, NumericFact):
            return False

        terms = ["TaxIndemnificationArrangement", "LitigationExpense"]
        return self.contains_match(terms)

    def generate_cost(self, fact, label, text_blocks=None):
        return LegalCost(fact, label)

class LegalCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)
