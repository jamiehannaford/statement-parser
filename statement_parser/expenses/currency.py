from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_CURRENCY

TAGS_CURRENCY = [
    "ForeignCurrencyTransactionGainLossBeforeTax".lower(),
    "ForeignCurrencyTransactionGainLossUnrealized".lower(),
]

class CurrencyGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_CURRENCY, TAGS_CURRENCY, instance, labels=labels, profile=profile)
    
    def supports_sector(self, sector, fact):
        return not self.is_sector_financial(sector)

    def generate_cost(self, fact, label, text_blocks=None):
        return CurrencyCost(fact, label)


class CurrencyCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)
