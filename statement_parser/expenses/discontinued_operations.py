from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_DISC_OPS

TAGS_DISCONTINUED_OPS = [
    # "incomelossfromdiscontinuedoperationsnetoftax",
    # 'incomelossfromdiscontinuedoperationsnetoftaxattributabletoreportingentity',

    "gainlossondispositionofassets",
    # "DiscontinuedOperationGainLossOnDisposalOfDiscontinuedOperationNetOfTax".lower(),
    # "DiscontinuedOperationIncomeLossFromDiscontinuedOperationDuringPhaseOutPeriodNetOfTax".lower(),

    "GainLossOnSaleOfProperties".lower(),
    "GainLossOnSaleOfPropertyPlantEquipment".lower(),
    "GainOnDivestmentOfInterestsInAssociatedCompanies".lower(),
    "DisposalGroupIncludingDiscontinuedOperationDeferredTaxLiabilities".lower(),
]

class DiscontinuedOperationsExpenseGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_DISC_OPS, TAGS_DISCONTINUED_OPS, instance, labels=labels, profile=profile)

    def supports_sector(self, sector, fact):
        return not self.is_sector_real_estate(sector)

    def group_specific_processing(self, costs):
        return self.filter_by_highest_term(["GainLossOn"], costs)

    def generate_cost(self, fact, label, text_blocks=None):
        return DiscontinuedOperationsCost(fact, label)

class DiscontinuedOperationsCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)