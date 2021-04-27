from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_RESTRUCT

from xbrl_parser.instance import NumericFact

TAGS_RESTRUCTURING = [
    'restructuringcharges', 
    'restructuringandotheractionrelatedcharges', 
    # 'restructuringsettlementandimpairmentprovisions',
    'otherrestructuringcosts',
    "restructuringcosts",
    # "restructuringandrelatedcostincurredcost",
    # "paymentsforrestructuring",
    "restructuringandrelatedcostexpectedcost1",
    "transformationalcostmanagement",
    "restructureandimpairmentcharges",
    "restructuringandotheractionrelatedcharges",
    # "restructuringchargesandacquisitionrelatedcosts",
    "businessalignmentcosts",
    "restructuringassetimpairmentcharges",
    'severancecosts1',
    "onetimeterminationbenefits",
    "gainlossonsaleofbusiness",
    "businessexitcosts1",
    "gainlossoninvestments",
    "DebtSecuritiesRealizedGainLoss".lower(),
    "EquitySecuritiesFvNiRealizedGainLoss".lower(),
    "RestructuringCostsAndAssetImpairmentCharges".lower(),
]

PREC_RESTR_TAG = [
    # "us-gaap_restructuringcharges"
]

class RestructuringExpenseGroup(ExpenseGroup):
    def __init__(self, instance):
        super().__init__(NAME_RESTRUCT, TAGS_RESTRUCTURING, instance,
            precedent_tags=PREC_RESTR_TAG, strict_mode=True)

    def is_cost(self, fact, profile):
        if super().is_cost(fact, profile):
            return True 
        
        if not isinstance(fact, NumericFact):
            return False

        concept_id = fact.concept.xml_id.lower()
        other_terms = ["charge", "cost", "expense"]
        return "restructuring" in concept_id and any(w in concept_id for w in other_terms)

    def generate_cost(self, fact):
        return RestructuringCost(fact)


class RestructuringCost(Expense):
    def __init__(self, fact):
        super().__init__(fact)