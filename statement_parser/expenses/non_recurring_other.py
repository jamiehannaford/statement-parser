from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_NRO

TAGS_NON_RECURRING_OTHER = [
    "deconsolidationgainorlossamount",
    "payrollsupportprogramgrantrecognized",
    "othercostandexpenseoperating",
    "gainlossondispositionofassets1",
]


class NonRecurringOtherExpenseGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_NRO, TAGS_NON_RECURRING_OTHER, instance)

    def generate_cost(self, fact):
        return NonRecurringOtherCost(fact)


class NonRecurringOtherCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)