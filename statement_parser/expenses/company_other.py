from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_COMPANY_OTHER

TAGS_COMPANY_OTHER = [
    "investmentincomedividend",
    # "paymentstoacquireintangibleassets",
    "insurancerecoveries",
    # "incomelossfromcontinuingoperationsincludingportionattributabletononcontrollinginterest",

    "OtherOperatingIncomeExpenseNet".lower(),
    # "NonoperatingIncomeExpense".lower(),
]

PREC_CDO = [
    "us-gaap_othernonoperatingincomeexpense",
]

# TODO Look up label tag for better detection
class CompanyDefinedOtherGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_COMPANY_OTHER, TAGS_COMPANY_OTHER, instance,
            precedent_tags=PREC_CDO)

    def generate_cost(self, fact):
        return CompanyDefinedOtherCost(fact)


class CompanyDefinedOtherCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)