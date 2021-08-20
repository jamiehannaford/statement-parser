import re 

from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_RESTRUCT

from xbrl_parser.instance import NumericFact

TAGS_RESTRUCTURING = [
    'RestructuringCharges'.lower(), 
    'restructuringandotheractionrelatedcharges',
    "restructuringcosts",
    'OtherRestructuringCosts'.lower(),
    # "paymentsforrestructuring",
    "restructuringandrelatedcostexpectedcost1",
    "transformationalcostmanagement",
    "restructureandimpairmentcharges",
    "restructuringandotheractionrelatedcharges",
    # "restructuringchargesandacquisitionrelatedcosts",
    "businessalignmentcosts",
    "restructuringassetimpairmentcharges",
    'SeveranceCosts1'.lower(),
    "onetimeterminationbenefits",
    "BusinessExitCosts".lower(),
    "businessexitcosts1",
    # "RestructuringReserveAcceleratedDepreciation".lower(
    "ImpairmentOfLongLivedAssetsAndOtherCharges".lower(),
    "GainLossOnInvestmentsExcludingOtherThanTemporaryImpairments".lower(),
    "GainOrLossOnSaleOfPreviouslyUnissuedStockByEquityInvestee".lower(),

    # TODO: Should we really include this? do some researching
    # "IncomeLossFromEquityMethodInvestments".lower(), # GOOGL 2018
    "GainLossOnDispositionOfAssets1".lower(), # TSLA 2019
    "DeconsolidationGainOrLossAmount".lower(),
    "RestructuringSettlementAndImpairmentProvisions".lower(), # GIS 2018
    "GainLossOnSaleOfBusiness".lower(),
    "RestructuringCostsAndAssetImpairmentCharges".lower(),
    "GainLossOnInvestments".lower(), # F 2020
    # "EquityMethodInvestmentRealizedGainLossOnDisposal".lower(),
    "DisposalGroupNotDiscontinuedOperationGainLossOnDisposal".lower(), # divestitures
    "PurchasesAndSalesOfBusinessInterests".lower(),
    "RestructuringandOtherCharges".lower(),
    "RestructuringImpairmentPlantClosingAndTransitionCosts".lower(),
    "ImpairmentIntegrationAndRestructuringExpenses".lower(),
    "RestructuringTransactionAndIntegrationCost".lower(),
]

PREC_RESTR_TAG = [
    # "us-gaap_GainLossOnDispositionOfAssets1".lower(),
    # "us-gaap_RestructuringCharges".lower(),
    # "us-gaap_RestructuringSettlementAndImpairmentProvision".lower(), # AVGO 2019
    # "us-gaap_RestructuringSettlementAndImpairmentProvisions".lower(), # GIS 2018
]

RESTR_BACKUPS = [
    "us-gaap_RestructuringCostsAndAssetImpairmentCharges".lower(),
]

# TODO: Should equity method investments be included? For now we've disabled.

# TODO: Some tags, like the following:
# - IncomeLossFromEquityMethodInvestments
# - InvestmentIncomeInterest
# - CashDividendsPaidToParentCompanyByConsolidatedSubsidiaries
# - GainLossOnInvestments
# - OtherExpenseExcludingInterest
#
# don't make sense for some companies, like AIG in 2018, because their core business model
# is investments (or they're holding companies). Whereas GOOGL in 2007 lists $156m for 
# IncomeLossFromEquityMethodInvestments since back then it wasn't (before Alphabet).
# Is there any way to look up if the company is a holding company and not discount these 
# expenses if so? Another option is counting all of the operating business segments in the contexts.
class RestructuringExpenseGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_RESTRUCT, TAGS_RESTRUCTURING, instance,
            precedent_tags=PREC_RESTR_TAG, strict_mode=True, labels=labels, profile=profile) 

    def supports_sector(self, sector, fact):
        if self.is_sector_financial(sector) and "investment" in fact.concept.xml_id.lower():
            return False 
        return True

    def group_specific_processing(self, costs):
        terms = ["(Restructuring|Transformation)\w*(Charge|Cost)", "GainLoss"]
        return self.filter_by_highest_term(terms, costs)

    def is_cost(self, fact, label):
        if super().is_cost(fact, label):
            return True
        
        if not isinstance(fact, NumericFact):
            return False
        
        concept_id = fact.concept.xml_id.lower()
        excluded_terms = ["incurredcost", "incomeloss", "paymentsfor", "netoftax", "assetimpairment"]   
        if any(w in concept_id for w in excluded_terms):
            return False

        if self.matches_custom_pattern(fact):
            return True

    def matches_custom_pattern(self, fact):
        concept_id = fact.concept.xml_id.lower()

        if "GainLossOnSaleOfInvestment".lower() in concept_id:
            return True

        main_terms = ["restructuring", "deconsolidation", "realignment", "employeetermination"]
        other_terms = ["charges?", "costs?", "expenses?"]
        regex_patt = "(" + "|".join(main_terms) + ')(.*)(' + "|".join(other_terms) + ")$"
        
        res = re.search(regex_patt, concept_id)
        # return res is not None
        return False

    def generate_cost(self, fact, label, text_blocks=None):
        return RestructuringCost(fact, label)

class RestructuringCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)