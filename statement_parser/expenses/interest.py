from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_INTEREST

from xbrl.instance import NumericFact

TAGS_INTEREST = [
    "InterestExpense".lower(),
    "InterestIncomeExpenseNonoperatingNet".lower(),
    "interestcostscapitalizedadjustment",
    "InterestRevenueExpenseNet".lower(),
    "interestandotherfinancialcharges",
    "deferredtaximpactuponadoptionofasu201602andimpairmentrouassets",
    "interestincomeexpensenet",
    "InterestIncomeOther".lower(),
    "InterestAndDebtExpense".lower(),
    "InterestExpenseDebt".lower(),
    "VehicleInterestNet".lower(),
    "FinancingInterestExpense".lower(),
    "InterestExpenseOther".lower(),
    "InvestmentIncomeInterest".lower(), # F 2017
]

PREC_INTEREST = [
    "us-gaap_InterestIncomeExpenseNet".lower(),
    "us-gaap_InterestRevenueExpenseNet".lower(),
]

FINANCE_INTEREST = [
    "InterestExpense".lower(),
    "InterestIncomeExpenseNet".lower()
]

# TODO: Some companies have operating segments with finance business models. For example, 
#       GE Capital or Ford Credit. For these types of firms, we should not discount the 
#       full interest income/expense since it's their core earnings.
class InterestExpenseGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_INTEREST, TAGS_INTEREST, instance, labels=labels, 
            precedent_tags=PREC_INTEREST, profile=profile)

    def supports_sector(self, sector, fact):
        if self.is_sector_financial(sector):
            return False

        return True

    def group_specific_processing(self, costs):
        return self.filter_by_highest_term(["Interest(\w+)?Expense"], costs, allow_protected=False)

    def generate_cost(self, fact, label, text_blocks=None):
        return InterestCost(fact, label)

    def is_cost(self, fact, label):
        if not super().is_cost(fact, label):
            return False
        
        if not isinstance(fact, NumericFact):
            return False

        excluded_terms = ["tax", "Merger", "DisposalGroup"]
        if self.contains_excluded(excluded_terms):
            return False
            
        if "InterestExpense".lower() in concept_id and "OfFinancial".lower() not in concept_id:
            return True

        return True
        
class InterestCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)

    def validate(self, text_facts=[]):
        concept_id = self.fact.concept.xml_id
        terms = ["InterestExpense"]
        if any(w in concept_id for w in terms):
            return

        return super().validate(text_facts=text_facts)
