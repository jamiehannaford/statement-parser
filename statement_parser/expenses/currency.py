from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_CURRENCY

TAGS_CURRENCY = [
    "foreigncurrencytransactiongainlossbeforetax",
]


class CurrencyGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_CURRENCY, TAGS_CURRENCY, instance)

    def generate_cost(self, fact):
        return CurrencyCost(fact)


class CurrencyCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)