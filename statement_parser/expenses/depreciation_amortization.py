from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_DEPR_AMORT
from xbrl_parser.instance import NumericFact

TAGS_DEPR_AMORT = [
    "AmortizationOfIntangibleAssets".lower(), # ABT 2020

    "amortizationofintangibleassetsnotassociatedwithsinglefunction",
    # 'restructuringreserveaccelerateddepreciation',
    # "amortizationofinventorystepup",
    "DepreciationAndAmortization".lower(),
    "DepreciationDepletionAndAmortization".lower(),
    "DeferredPolicyAcquisitionCostAmortizationExpense".lower(), # AIG 2019
    "CostOfGoodsAndServicesSoldDepreciation".lower(), # CAR 2020
    # "Depreciation".lower(),
    "OtherDepreciationAndAmortization".lower(),
    "AcquisitionRelatedAmortizationExpense".lower(),
    "AmortizationOfAcquisition".lower(),
]

# TODO: Some companies are allowed to use DepreciationDepletionAndAmortization, like ABC and ALK,
# but others are not, like AAPL. Is there a difference here?

DA_PR_TAG = [
    # "us-gaap_DepreciationDepletionAndAmortization".lower(),
    # "us-gaap_DepreciationAndAmortization".lower(),
    "us-gaap_AmortizationOfIntangibleAssets".lower(),
]

class DepreciationAmortizationExpenseGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_DEPR_AMORT, TAGS_DEPR_AMORT, instance,
            precedent_tags=DA_PR_TAG, labels=labels, profile=profile)

    def generate_cost(self, fact, label, text_blocks=None):
        return DepreciationAmortizationCost(fact, label)

    def group_specific_processing(self, costs):
        return self.filter_by_highest_term(["Amortization"], costs)

    def is_cost(self, fact, label):
        if super().is_cost(fact, label):
            return True 
        
        if not isinstance(fact, NumericFact):
            return False

        concept_id = fact.concept.xml_id.lower()
        terms = ["DepreciationAmortization", "VehicleDepreciation", "RelatedDepreciationAndAmortization"]
        if any(w.lower() in concept_id for w in terms):
            return True

class DepreciationAmortizationCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)