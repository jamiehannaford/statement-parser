from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_DEPR_AMORT

TAGS_DEPR_AMORT = [
    "amortizationofintangibleassets",
    "amortizationofintangibleassetsnotassociatedwithsinglefunction",
    # 'restructuringreserveaccelerateddepreciation',
    "amortizationofinventorystepup",
    "depreciationandamortization",
    "depreciationdepletionandamortization",
    "deferredpolicyacquisitioncostamortizationexpense",
]

DA_PR_TAG = [
    "us-gaap_depreciationandamortization",
    "us-gaap_depreciationdepletionandamortization",
    "us-gaap_amortizationofintangibleassets",
]

class DepreciationAmortizationExpenseGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_DEPR_AMORT, TAGS_DEPR_AMORT, instance,
            precedent_tags=DA_PR_TAG)

    def generate_cost(self, fact):
        return DepreciationAmortizationCost(fact)


class DepreciationAmortizationCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)