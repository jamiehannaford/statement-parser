from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_DERIVATIVE

TAGS_DERIVATIVE = [
    "gainlossonderivativeinstrumentsnetpretax",
    "embeddedderivativegainlossonembeddedderivativenet",
]


class DerivativeGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_DERIVATIVE, TAGS_DERIVATIVE, instance)

    def generate_cost(self, fact):
        return DerivativeCost(fact)


class DerivativeCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)