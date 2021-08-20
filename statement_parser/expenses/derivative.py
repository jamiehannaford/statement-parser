from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_DERIVATIVE

TAGS_DERIVATIVE = [
    "gainlossonderivativeinstrumentsnetpretax",
    "embeddedderivativegainlossonembeddedderivativenet",
    "DerivativeGainLossOnDerivativeNet".lower(), # Disabled for GS, but this may be a general thing worth disabling?
]

class DerivativeGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_DERIVATIVE, TAGS_DERIVATIVE, instance, labels=labels, profile=profile)

    def supports_sector(self, sector, fact):
        for segment in fact.context.segments:
            if segment.dimension.name == "BusinessGroupAxis" and "financial" in segment.member.name.lower():
                return False

        return not self.is_sector_financial(sector)

    def generate_cost(self, fact, label, text_blocks=None):
        return DerivativeCost(fact, label)

class DerivativeCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)