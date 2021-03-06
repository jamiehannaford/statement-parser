from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_FIN
from xbrl.instance import NumericFact

TAGS_FIN = [
    "InvestmentIncomeNet".lower(),
    "ImpairmentLossesRelatedToFinancialInstruments".lower(),
    "investmentincomeinterestanddividend", # AAPL 2020 lists this as financing
    "GainsLossesOnExtinguishmentOfDebt".lower(), # F 2019 
    "InvestmentIncomeNonoperating".lower(), # QCOM 2015
    "AvailableForSaleSecuritiesGrossRealizedGainLossNet".lower(),
]

class FinancingGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_FIN, TAGS_FIN, instance, labels=labels, profile=profile)

    def is_cost(self, fact, label):
        if super().is_cost(fact, label):
            return True 
        
        if not isinstance(fact, NumericFact):
            return False

        terms = ["financecosts"]
        return self.contains_match(terms)

    def supports_sector(self, sector, fact):
        return not self.is_sector_financial(sector)

    def generate_cost(self, fact, label, text_blocks=None):
        return FinancingCost(fact, label)


class FinancingCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)
