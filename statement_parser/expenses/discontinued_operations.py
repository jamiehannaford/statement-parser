from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_DISC_OPS

TAGS_DISCONTINUED_OPS = [
    "incomelossfromdiscontinuedoperationsnetoftax",
    # 'incomelossfromdiscontinuedoperationsnetoftaxattributabletoreportingentity',

    "disposalgroupnotdiscontinuedoperationgainlossondisposal", # divestitures
    "gainlossondispositionofassets",
]


class DiscontinuedOperationsExpenseGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_DISC_OPS, TAGS_DISCONTINUED_OPS, instance)

    def generate_cost(self, fact):
        return DiscontinuedOperationsCost(fact)

    def group_specific_processing(self):
        dimension_map = {}
        for cost in self.costs:
            num = len(cost.fact.context.segments)
            if num not in dimension_map:
                dimension_map[num] = []
            dimension_map[num].append(cost)
        
        if dimension_map:
            return dimension_map[min(dimension_map, key=int)]
        else:
            return self.costs

class DiscontinuedOperationsCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)