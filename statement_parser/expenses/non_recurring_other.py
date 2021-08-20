from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_NRO

from xbrl_parser.instance import NumericFact

TAGS_NON_RECURRING_OTHER = [
    "payrollsupportprogramgrantrecognized",
    # "othercostandexpenseoperating",
    "ReductionOfRightUseAssetsAndAccretionOfLeaseLiabilities".lower(),
    # "IncomeTaxExpenseBenefitContinuingOperationsAdjustmentOfDeferredTaxAssetLiability".lower(),
    "SeverancePensionAndBenefitCharges".lower(),
    "PayrollSupportProgramOneGrant".lower(),
    "GainOnSaleOfInvestments".lower(),
    "GainLossOnSaleOfStockInSubsidiaryOrEquityMethodInvestee".lower(),
    "Nonoperatingpensionandotherpostretirementemployeebenefitexpenseincome".lower(),
    "IncompleteAccountingTransitionTaxForAccumulatedForeignEarningsNetProvisionalIncomeTaxExpenseBenefit".lower(),
    # "IncomeTaxReconciliationRepatriationOfForeignEarnings".lower(),
    "IncomeTaxReconciliationChangeInEnactedTaxRate".lower(),
    "TaxCutsAndJobsActOf2017IncomeTaxExpenseBenefit".lower(),
    "AdjustmentOfWarrantsGrantedForServices".lower(),
    "ProceedsFromStockPlans".lower(), # QCOM 2020 -- not sure if this is correct
    "UnusualOrInfrequentItemNetGainLoss".lower(),
]

class NonRecurringOtherExpenseGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_NRO, TAGS_NON_RECURRING_OTHER, instance, labels=labels, profile=profile)

    def generate_cost(self, fact, label, text_blocks=None):
        return NonRecurringOtherCost(fact, label)

    def is_cost(self, fact, label):
        if super().is_cost(fact, label):
            return True
        
        if not isinstance(fact, NumericFact):
            return False
        
        concept_id = fact.concept.xml_id.lower()
        excluded_terms = ["SaleOfBusiness", "aftertax", "netoftax", "DeferredIncome", "TransitionTaxExpense"]
        if any((w.lower() in concept_id for w in excluded_terms)):
            return False
        
        terms = ["withdrawalobligation", "DeconsolidationCharge", "SpecialItemGainLoss", 
            "Retirementplansmarktomarketadjustment"]
        return any((w.lower() in concept_id for w in terms))


class NonRecurringOtherCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)