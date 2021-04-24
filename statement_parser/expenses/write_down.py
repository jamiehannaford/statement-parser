from statement_parser.expenses.expese import Expense
from statement_parser.expense_group import ExpenseGroup

TAGS_ASSET_IMPAIRMENTS = [
    'inventorywritedown', # not sure about this?
    'otherassetimpairmentcharges', 
    'impairmentofoilandgasproperties', 
    'impairmentofintangibleassetsexcludinggoodwill', 
    'tangibleassetimpairmentcharges',
    'assetimpairmentcharges',
    'goodwillandintangibleassetimpairment',
    'goodwillimpairmentloss',
    "impairmentofintangibleassetsindefinitelivedexcludinggoodwill",
    'equitymethodinvestmentotherthantemporaryimpairment',
    'impairmentchargesonminorityinvestments', # investment?
    "definiteandindefinitelivedintangibleassetimpairment",
    "otherthantemporaryimpairmentlossesinvestmentsportionrecognizedinearningsnet",
    "flightequipmentoperatingleaseandinventoryimpairmentloss",
]

class WriteDownExpenseGroup(ExpenseGroup):
    def __init__(self, pre_linkbases):
        super().__init__("write_downs", TAGS_ASSET_IMPAIRMENTS, pre_linkbases)

    def generate_cost(self, fact):
        return WriteDownCost(fact)


class WriteDownCost(Expense):
    def __init__(self):
        super().__init__()