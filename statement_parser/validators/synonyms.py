
# Somethings one tag may incorporate other tags across different categories. In this case, it 
# makes sense to favour the parent tag and remove the disaggregations tags.
class SynonymValidator:
    def __init__(self, instance):
        self.instance = instance 
        self.element_map = {}
    
    def has_parent_conflict(self, parent_id, element_id):
        strict_conflicts = {
            "us-gaap_EquitySecuritiesFvNiGainLoss": [
                "us-gaap_EquitySecuritiesFvNiRealizedGainLoss",
                "us-gaap_EquitySecuritiesFvNiUnrealizedGainLoss"
            ],
        }

        for parent, children in strict_conflicts.items():
            if parent == parent_id and element_id in children:
                return True

        return False

    def has_conflict(self, element):
        conflicts = {
            "us-gaap_RestructuringCostsAndAssetImpairmentCharges": [
                "us-gaap_GoodwillImpairmentLoss",
                "us-gaap_RestructuringCharges"
            ],
            "us-gaap_InvestmentIncomeInterestAndDividend": [
                "us-gaap_InvestmentIncomeNonoperating"
            ],
            "us-gaap_ImpairmentOfInvestments": [
                "us-gaap_EquityMethodInvestmentOtherThanTemporaryImpairment",
                "us-gaap_ImpairmentOfIntangibleAssetsIndefinitelivedExcludingGoodwill"
            ],
            "us-gaap_IncomeLossFromDiscontinuedOperationsNetOfTax": [
                "us-gaap_GainLossOnSaleOfBusiness"
            ],
            "us-gaap_GainLossOnInvestments": [
                "us-gaap_GainLossOnInvestmentsExcludingOtherThanTemporaryImpairments",
                "us-gaap_GainOnSaleOfInvestments",
                "us-gaap_GainLossOnSaleOfInvestments",
                "us-gaap_AvailableForSaleSecuritiesGrossRealizedGainLossNet",
                "us-gaap_DisposalGroupNotDiscontinuedOperationGainLossOnDisposal",
                "us-gaap_UnrealizedGainOnSecurities",
                "us-gaap_ImpairmentOfInvestments",
                "us-gaap_EquitySecuritiesFvNiRealizedGainLoss",
                "us-gaap_EquitySecuritiesFvNiUnrealizedGainLoss",
                "us-gaap_AvailableForSaleSecuritiesGrossRealizedGains"
            ],
            "us-gaap_DepreciationAndAmortization": [
                "us-gaap_DepreciationDepletionAndAmortization",
                "us-gaap_AmortizationOfIntangibleAssets",
            ],
            "us-gaap_RestructuringCharges": [
                "us-gaap_SeveranceCosts1",
            ],
            "us-gaap_GainLossOnSaleOfBusiness": [
                "us-gaap_DisposalGroupNotDiscontinuedOperationGainLossOnDisposal",
            ],
            "us-gaap_GainLossOnDispositionOfAssets": [
                "us-gaap_GainLossOnSaleOfPropertyPlantEquipment",
            ],
            "us-gaap_GainLossOnSaleOfPropertyPlantEquipment": [
                "us-gaap_DisposalGroupNotDiscontinuedOperationGainLossOnDisposal",
            ],
            # "us-gaap_AssetImpairmentCharges": [
            #     "us-gaap_ImpairmentOfIntangibleAssetsExcludingGoodwill",
            #     "us-gaap_GoodwillImpairmentLoss",
            #     "us-gaap_ImpairmentOfLongLivedAssetsToBeDisposedOf",
            # ],
            "us-gaap_ImpairmentOfIntangibleAssetsExcludingGoodwill": [
                "us-gaap_GoodwillAndIntangibleAssetImpairment"
            ],
            "us-gaap_InterestExpense": [
                "us-gaap_InterestExpenseDebt",
                # "us-gaap_InterestIncomeExpenseNonoperatingNet",
                "us-gaap_InterestExpenseBorrowings",
                # "us-gaap_InterestIncomeExpenseNet",
            ],
            "us-gaap_InterestRevenueExpenseNet": [
                "us-gaap_InterestExpense"
            ],
            "us-gaap_RestructuringSettlementAndImpairmentProvisions": [
                "us-gaap_RestructuringCostsAndAssetImpairmentCharges",
                "us-gaap_ImpairmentOfIntangibleAssetsExcludingGoodwill",
            ],
            "us-gaap_DepreciationDepletionAndAmortization": [
                "us-gaap_AmortizationOfIntangibleAssets"
            ],
            "us-gaap_BusinessCombinationStepAcquisitionEquityInterestInAcquireeRemeasurementGainOrLoss": [
                "us-gaap_GainLossOnSaleOfInvestments"
            ],
            "us-gaap_GainLossOnDispositionOfAssets1": [
                "us-gaap_GainLossOnSaleOfPropertyPlantEquipment",
                "us-gaap_DeconsolidationGainOrLossAmount"
            ],
            "us-gaap_OtherNonoperatingIncomeExpense": [
                "us-gaap_DisposalGroupNotDiscontinuedOperationGainLossOnDisposal"
            ],
            "us-gaap_OtherIncome": [
                "us-gaap_NonoperatingIncomeExpense"
            ]
        }

        for parent, children in conflicts.items():
            if parent not in self.element_map:
                continue
            if self.element_map[parent].value == 0:
                continue
            for child in children:
                if element.concept.xml_id == child and not element.protected:
                    return True
        
        return False

    def parent_exceeds(self, parent, child):
        if parent.value < 0:
            return parent.value <= child.value 
        else:
            return parent.value >= child.value

    def init_element_map(self, elements):
        for elem in elements:
            self.element_map[elem.concept.xml_id] = elem

    def process(self, elements):
        self.init_element_map(elements)

        output = []
        for elem in elements:
            if not self.has_conflict(elem):
                output.append(elem)

        return output
