from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_INTEREST

TAGS_INTEREST = [
    "interestexpense",
    "investmentincomeinterest",
    "interestincomeexpensenonoperatingnet",
    "interestcostscapitalizedadjustment",
    "investmentincomeinterestanddividend",
    "interestrevenueexpensenet",
    "interestandotherfinancialcharges",
    "deferredtaximpactuponadoptionofasu201602andimpairmentrouassets",
    "interestincomeexpensenet",
    "interestincomeother",

    # "interestanddividendincomeoperating", # ms
]

class InterestExpenseGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_INTEREST, TAGS_INTEREST, instance)

    def generate_cost(self, fact):
        return InterestCost(fact)


class InterestCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)