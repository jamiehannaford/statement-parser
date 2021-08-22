import re

from statement_parser.expenses.expense import Expense
from statement_parser.expense_group import ExpenseGroup
from statement_parser.expenses.constants import NAME_WRITE_DOWN

from xbrl.instance import NumericFact

TAGS_ASSET_IMPAIRMENTS = [
    'inventorywritedown', # not sure about this?
    'OtherAssetImpairmentCharges'.lower(), 
    'impairmentofoilandgasproperties', 
    'impairmentofintangibleassetsexcludinggoodwill', 
    'tangibleassetimpairmentcharges',
    'AssetImpairmentCharges'.lower(),
    'goodwillandintangibleassetimpairment',
    'GoodwillImpairmentLoss'.lower(),
    "ImpairmentOfIntangibleAssetsIndefinitelivedExcludingGoodwill".lower(),
    'impairmentchargesonminorityinvestments', # investment?
    "definiteandindefinitelivedintangibleassetimpairment",
    "OtherThanTemporaryImpairmentLossesInvestmentsPortionRecognizedInEarningsNet".lower(),
    "flightequipmentoperatingleaseandinventoryimpairmentloss",
    "ImpairmentOfInvestments".lower(),
    "SpecialItemsImpairmentChargesAndOther".lower(),
    # "impairmentofintangibleassetsfinitelived",
    "GainLossOnSalesOfAssetsAndAssetImpairmentCharges".lower(),
    "BusinessCombinationProvisionalInformationInitialAccountingIncompleteAdjustmentInventory".lower(),
    "ImpairmentOfLongLivedAssetsToBeDisposedOf".lower(),
    "AccretionExpense".lower(),
    "ResearchAndDevelopmentInProcessIncludingImpairment".lower(),
    "GoodwillAndIndefiniteLivedIntangibleAssetImpairment".lower(),
    "ImpairmentOfLongLivedAssetsHeldForUse".lower(),
    "AssetImpairmentAndAbandonmentCharges".lower(),

    'EquityMethodInvestmentOtherThanTemporaryImpairment'.lower(), # disabling for now
    "ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff".lower(),
    "ImpairmentOfRealEstate".lower(),
]

# TODO Find a way to eliminate this
WD_PRE = [
    "alk_SpecialItemsImpairmentChargesAndOther".lower()
]

class WriteDownExpenseGroup(ExpenseGroup):
    def __init__(self, instance, labels, profile):
        super().__init__(NAME_WRITE_DOWN, TAGS_ASSET_IMPAIRMENTS, instance, 
            strict_mode=True, labels=labels, precedent_tags=WD_PRE, profile=profile)
        
        self.stripped_concepts = []

    def filter_by_highest_intangible(self, costs):
        intangibles = []
        highest_intangible = None

        for cost in costs:
            if self.is_intangible_cost(cost.fact) or self.label_contains_intangible(cost):
                if not highest_intangible or cost.cost > highest_intangible.cost:
                    highest_intangible = cost 
                intangibles.append(cost)
        
        for intangible in intangibles:
            if intangible != highest_intangible:
                costs.remove(intangible)
        
        return costs

    def label_contains_intangible(self, cost):
        terse = cost.label.get("terseLabel").lower()
        terms = ["intangible", "goodwill"]
        return any(w in terse for w in terms)

    def group_specific_processing(self, costs):
        costs = self.filter_by_highest_term(["ImpairmentCharges", "AssetImpairment", "LongLivedAsset"], costs)
        costs = self.filter_by_highest_intangible(costs)
        return costs

    def generate_cost(self, fact, label, text_blocks=None):
        return WriteDownCost(fact, label)

    def is_intangible_cost(self, fact):
        name = fact.concept.xml_id.lower()
        terms = ["intangible", "goodwill", "investment"]
        return any(w in name for w in terms)

    def supports_sector(self, sector, fact):
        if self.is_sector_financial(sector) and self.is_intangible_cost(fact):
            return False
        return True

    def is_cost(self, fact, label):
        if super().is_cost(fact, label):
            return True

        if not isinstance(fact, NumericFact):
            return False
        
        concept_id = fact.concept.xml_id.lower()
        excluded_terms = ["netoftax", "amortization"]
        if any(w in concept_id for w in excluded_terms):
            return False

        main_terms = ["inventory", "asset"]
        other_terms = ["impairments", "stepup"]
        return all(
            (any(w in concept_id for w in main_terms), 
            any(w in concept_id for w in other_terms)))

class WriteDownCost(Expense):
    def __init__(self, fact, label):
        super().__init__(fact, label)
