import re

# TODO: A better way of avoiding overlaps/duplication is by utilizing the parent 
#       field. See any interactive xbrl page on SEC. Calcs are nested.
class MutualExclusionDetector:
    def __init__(self, facts):
        self.mappings = {
            # MSFT and AIG 2019
            "GainLossOnInvestments": [
                # "ImpairmentOfInvestments",
                "EquitySecuritiesFvNiRealizedGainLoss",
                "EquitySecuritiesFvNiUnrealizedGainLoss",
                "DebtSecuritiesAvailableForSaleRealizedGain",
                "DebtSecuritiesAvailableForSaleRealizedLoss",
                "GainLossOnInvestments(.+)", # AIG
                "ForeignCurrencyTransactionGainLossBeforeTax",
            ],
            # TSLA 2019
            "RestructuringAndOtherExpenses": [
                "BusinessExitCosts1",
                "ImpairmentOfIntangibleAssetsIndefinitelivedExcludingGoodwill",
                "ImpairmentOfIntangibleAssetsExcludingGoodwill",
                "TangibleAssetImpairmentCharges",
                "GainLossOnDispositionOfAssets1",
                "RestructuringCosts",
                "LitigationSettlementExpense",
            ],
            # GE 2020
            "InterestAndOtherFinancialCharges": [
                "GainsLossesOnExtinguishmentOfDebt"
            ],
            "OtherIncome": [
                "NonoperatingIncomeExpense",
                "OtherOperatingIncomeExpenseNet", # AIG 2019
            ],
            "GoodwillImpairmentLoss": [
                "EquitySecurities(.*)",
            ],
            "GainLossOnDispositionOfAssets1": [
                "EquitySecurities(.*)",
                "OtherIncome",
                "GainLossOnSalesOfAssets(.*)",
                "IncomeLossFromEquityMethodInvestments",
                "EquityMethodInvestmentOtherThanTemporaryImpairment", # F 2020
                "DeconsolidationGainOrLossAmount", # F 2020
            ],
            "BenefitCostsNonoperating": [
                "DefinedBenefitPlan(.*)",
            ],
            # GIS 2018
            "RestructuringSettlementAndImpairmentProvisions": [
                "IncomeLossFromEquityMethodInvestments",
                "OtherRestructuringCosts",
                "RestructuringCharges",
                "ImpairmentOfIntangibleAssets(.+)",
            ],
            # GIS 2019, 2020
            "NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent": [
                "OtherComprehensiveIncomeLossAmortizationAdjustment(.+)",
                "DefinedBenefitPlan(.*)",
            ],
            # K 2017
            "RestructuringAndRelatedCostIncurredCost": [
                "RestructuringSettlementAndImpairmentProvisions",
                "DeconsolidationGainOrLossAmount",
            ],
            # QCOM 2020
            "OtherThanTemporaryImpairmentLossesInvestmentsPortionRecognizedInEarningsNet": [
                "ImpairmentOfInvestments",
            ],
            # QCOM 2018
            "OtherOperatingIncomeExpenseNet": [
                "OtherRestructuringCosts",
                "Restructuring(.+)",
                "LossContingencyLossInPeriod",
                "AssetImpairmentCharges",
                "GoodwillImpairmentLoss",
                "SeveranceCosts1",
                "GainLossOnSaleOfPropertyPlantEquipment",
            ],
            # QCOM 2015
            "InvestmentIncomeNonoperating": [
                "InvestmentIncomeInterestAndDividend",
                "IncomeLossFromEquityMethodInvestment",
                "GainLossOnInvestments(.+)",
                "OtherThanTemporaryImpairmentLossesInvestments(.+)",
            ]
        }

        self.concept_map = {}
        for fact in facts:
            self.concept_map[self.concept_id(fact)] = True
    
    def concept_id(self, fact):
        concept_id = fact.concept.xml_id.lower()
        return concept_id.split("_")[1]

    def str_match(self, label, fact):
        match = re.search(label.lower(), self.concept_id(fact))
        return match is not None

    def has_a_summarizing_parent(self, fact):
        for parent, children in self.mappings.items():
            for child in children:
                if self.str_match(child, fact) and parent.lower() in self.concept_map:
                    return True

