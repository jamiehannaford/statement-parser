from statement_parser.expenses.expese import Expense
from statement_parser.expense_group import ExpenseGroup

TAGS_DEPR_AMORT = [
    "amortizationofintangibleassetsnotassociatedwithsinglefunction",
    'restructuringreserveaccelerateddepreciation',
    "amortizationofinventorystepup",
]

class DepreciationAmortizationExpenseGroup(ExpenseGroup):
    def __init__(self, pre_linkbases):
        super().__init__("depr_amort", TAGS_DEPR_AMORT, pre_linkbases)

    def generate_cost(self, fact):
        return DepreciationAmortization(fact)


class DepreciationAmortizationCost(Expense):
    def __init__(self):
        super().__init__()