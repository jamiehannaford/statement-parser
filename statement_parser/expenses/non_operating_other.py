from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_NOO, NAME_NOUS

TAGS_NON_OP_OTHER = [
    "othernonoperatingincomeexpense",
    "IncomeLossFromEquityMethodInvestments".lower(),
    "OtherIncome".lower(),
    "GainLossOnContractTermination".lower(),
]

class NonOperatingOtherExpenseGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_NOO, TAGS_NON_OP_OTHER, instance)

    def generate_cost(self, fact):
        return NonOperatingOtherCost(fact)

class NonOperatingOtherCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)

# ---

TAGS_NOUS = []

class NonOperatingUnconsolidatedSubExpenseGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_NOUS, TAGS_NOUS, instance)

    def generate_cost(self, fact):
        return NonOperatingUnconsolidatedSubCost(fact)


class NonOperatingUnconsolidatedSubCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)