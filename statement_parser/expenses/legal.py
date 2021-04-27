from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_LEGAL

TAGS_LEGAL = [
    "gainlossrelatedtolitigationsettlement",
    "LossContingencyLossInPeriod".lower(),
]


class LegalExpenseGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_LEGAL, TAGS_LEGAL, instance)

    def generate_cost(self, fact):
        return LegalCost(fact)


class LegalCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)