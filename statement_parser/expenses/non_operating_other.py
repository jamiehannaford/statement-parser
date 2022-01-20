from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_NOO, NAME_NOUS

from xbrl.instance import NumericFact

TAGS_NON_OP_OTHER = [
    "GainLossOnContractTermination".lower(),
    "LossOnContractTermination".lower(),
    "OtherItemsOtherIncome".lower(),
    "OtherCosts".lower(),
    "COVID19Charges".lower(),
    "UnrealizedGainOnSecurities".lower(),
    "OtherExpenseByFunction".lower(),
    "OtherComprehensiveIncomeLossAmortizationAdjustmentFromAOCIPensionAndOtherPostretirementBenefitPlansForNetPriorServiceCostCreditBeforeTax".lower(),
    "NetFASnonservicePensionBenefitExpense".lower(),
    "DefinedBenefitPlanActuarialGainLossImmediateRecognitionAsComponentInNetPeriodicBenefitCostCredit".lower(),
    "InvestmentPerformanceFees".lower(), # GOOGL 2019
    "EquitySecuritiesFvNiGainLoss".lower(), # GOOGL 2020
    "EquitySecuritiesFvNiUnrealizedGainLoss".lower(), # GOOGL 2019
    "EquitySecuritiesFvNiRealizedGainLoss".lower(), # listed as write-down in GOOGL 2019, but as restructuring in GOOGL 2020
    "GainLossOnMarketableAndNonMarketableInvestmentsNet".lower(), # GOOGL 2018
    "DebtSecuritiesRealizedGainLoss".lower(), # GOOGL 2020
    "NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent".lower(), # GIS 2019, 2020
    "PensionandPostretirementBenefitExpenseExcludingCurrentServiceCost".lower(), # F 2017
    "TaxIndemnifications".lower(), # HPQ 2019
    "NetLossesGainsOnDeferredCompensationPlanAssets".lower(), # QCOM 2020
    "CashContributionExpense".lower(), # KO 2017
    "AvailableForSaleSecuritiesGrossRealizedGains".lower(),
    "RestatementsAndRelatedCosts".lower(),
    "AccountingReviewAndRestatementCosts".lower(),
]

TEXT_BLOCK_TAGS = [
    "us-gaap_OtherIncomeAndOtherExpenseDisclosureTextBlock"
]

class NonOperatingOtherExpenseGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_NOO, TAGS_NON_OP_OTHER, instance, labels=labels, 
            text_blocks=TEXT_BLOCK_TAGS, profile=profile)

    def generate_cost(self, fact, label, text_blocks=None):
        return NonOperatingOtherCost(fact, label, text_blocks)
    
    def supports_sector(self, sector, fact):
        if self.is_sector_financial(sector):
            finance_terms = ["securities", "investment"]
            if any(w in fact.concept.xml_id.lower() for w in finance_terms):
                return False 
            
        return True

    def is_cost(self, fact, label):
        if super().is_cost(fact, label):
            return True
        
        if not isinstance(fact, NumericFact):
            return False
        
        return self.contains_match(terms)

class NonOperatingOtherCost(Expense):
    def __init__(self, fact, label, text_blocks):
        super().__init__(fact, label)
        self.validated = False
        self.text_blocks = text_blocks

# ---

TAGS_NOUS = []

class NonOperatingUnconsolidatedSubExpenseGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_NOUS, TAGS_NOUS, instance, labels=labels, profile=profile)

    def generate_cost(self, fact, label, text_blocks=None):
        return NonOperatingUnconsolidatedSubCost(fact, label)


class NonOperatingUnconsolidatedSubCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)
