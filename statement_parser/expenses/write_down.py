from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_WRITE_DOWN

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
    "impairmentofinvestments",
    "specialitemsimpairmentchargesandother",
    "impairmentofintangibleassetsfinitelived",
    "GainLossOnSalesOfAssetsAndAssetImpairmentCharges".lower(),
]

WRITE_DOWN_PRECEDENCE_TAG = [
    # "us-gaap_assetimpairmentcharges", 
    # "us-gaap_goodwillimpairmentloss",
    # "us-gaap_impairmentofintangibleassetsindefinitelivedexcludinggoodwill", #questionable
]

class WriteDownExpenseGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_WRITE_DOWN, TAGS_ASSET_IMPAIRMENTS, instance, 
            precedent_tags=WRITE_DOWN_PRECEDENCE_TAG, strict_mode=True)

    def generate_cost(self, fact):
        return WriteDownCost(fact)

    def back_up_permitted(self, concepts, concept_id):
        permitted_backups = [
            "us-gaap_goodwillimpairmentloss",
        ]
        return concept_id not in concepts 
            # and concept_id.lower() in permitted_backups

class WriteDownCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)