from statement_parser.expenses.expese import Expense
from statement_parser.expense_group import ExpenseGroup

TAGS_RESTRUCTURING = [
    'restructuringcharges', 
    'restructuringandotheractionrelatedcharges', 
    'restructuringsettlementandimpairmentprovisions',
    'otherrestructuringcosts',
    "restructuringcosts",
    "restructuringandrelatedcostincurredcost",
    "paymentsforrestructuring",
    "restructuringandrelatedcostexpectedcost1",
    "transformationalcostmanagement",
    "restructureandimpairmentcharges",
    "restructuringandotheractionrelatedcharges",
    "businessexitcosts1",
    "businesscombinationintegrationrelatedcosts",
    "restructuringchargesandacquisitionrelatedcosts",
    "businessalignmentcosts",
    "restructuringassetimpairmentcharges",
    "businesscombinationacquisitionrelatedcoststransactioncosts",
    'severancecosts1',
    "onetimeterminationbenefits",
]

class RestructuringExpenseGroup(ExpenseGroup):
    def __init__(self, pre_linkbases):
        super().__init__("restructuring", TAGS_RESTRUCTURING, pre_linkbases)

    def generate_cost(self, fact):
        return RestructuringCost(fact)


class RestructuringCost(Expense):
    def __init__(self):
        super().__init__()