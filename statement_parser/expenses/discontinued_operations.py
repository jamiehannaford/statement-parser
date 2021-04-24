from statement_parser.expenses.expese import Expense
from statement_parser.expense_group import ExpenseGroup

TAGS_DISCONTINUED_OPS = [
    "incomelossfromdiscontinuedoperationsnetoftax",
    'incomelossfromdiscontinuedoperationsnetoftaxattributabletoreportingentity',

    "disposalgroupnotdiscontinuedoperationgainlossondisposal", # divestitures
    "gainlossondispositionofassets",
    "deconsolidationgainorlossamount",
]

class DiscontinuedOperationsExpenseGroup(ExpenseGroup):
    def __init__(self, pre_linkbases):
        super().__init__("discontinued_ops", TAGS_DISCONTINUED_OPS, pre_linkbases)

    def generate_cost(self, fact):
        return DiscontinuedOperations(fact)


class DiscontinuedOperationsCost(Expense):
    def __init__(self):
        super().__init__()