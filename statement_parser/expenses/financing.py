from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_FIN

TAGS_FIN = [
    "gainslossesonextinguishmentofdebt",
    "InvestmentIncomeNet".lower(),
]


class FinancingGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_FIN, TAGS_FIN, instance)

    def generate_cost(self, fact):
        return FinancingCost(fact)


class FinancingCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)