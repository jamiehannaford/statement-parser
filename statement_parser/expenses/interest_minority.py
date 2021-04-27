from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_INT_MIN

TAGS_INTEREST_MINORITY = [
    "netincomelossattributabletononcontrollinginterest",
    # "incomelossfromcontinuingoperationsattributabletononcontrollingentity"
]

class InterestMinorityExpenseGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_INT_MIN, TAGS_INTEREST_MINORITY, instance)

    def generate_cost(self, fact):
        return InterestMinorityCost(fact)


class InterestMinorityCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)