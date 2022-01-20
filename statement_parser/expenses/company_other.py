from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_COMPANY_OTHER

TAGS_COMPANY_OTHER = [
    "investmentincomedividend",
    "OtherNonoperatingIncomeExpense".lower(), # AAPL 2020 lists this
    "NonoperatingIncomeExpense".lower(), # AAPL 2012 only has net
    "OtherExpenseExcludingInterest".lower(), # AIG 2018
    "OtherIncome".lower(),
    "OtherExpenses".lower(),
    "OtherNonoperatingIncome".lower(),
    "Othermiscellaneousexpenseincome".lower(),
    "OtherIncomeExpensesOther".lower(),
    "OtherNonoperatingIncomeExpenseNet".lower(),
    "DeferredTaxAssetsNet".lower(),
]

CDO_TEXT_BLOCKS = [
    "vz_SupplementalIncomeStatementInformationTableTextBlock"
]

class CompanyDefinedOtherGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_COMPANY_OTHER, TAGS_COMPANY_OTHER, instance,
            labels=labels, profile=profile, text_blocks=CDO_TEXT_BLOCKS)

    def group_specific_processing(self, costs):
        return self.filter_by_highest_term(["OtherNonoperating"], costs, allow_protected=False)

    def supports_sector(self, sector, fact):
        # TODO: Make this a bit more specific. If you look at AIG 2016, you can see it 
        # derives lots of "Other Income" from line items whose are actually core earnings.
        if self.is_sector_financial(sector) and fact.concept.xml_id == "us-gaap_OtherIncome":
            return False 
        return True

    def generate_cost(self, fact, label, text_blocks=None):
        return CompanyDefinedOtherCost(fact, label)


class CompanyDefinedOtherCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)
