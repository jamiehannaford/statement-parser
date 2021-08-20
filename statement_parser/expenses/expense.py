from statement_parser.text_analyser import TextAnalyser

from xbrl_parser.instance import TextFact

BALANCE_TAGS_REVERSAL = [
    "us-gaap_CashDividendsPaidToParentCompanyByConsolidatedSubsidiaries",
]

class Expense:
    def __init__(self, fact, label, text_blocks=None):
        self.fact = fact
        self.cost = float(fact.value)
        self.parent_cost = None 
        self.child_costs = []
        self.validated = False
        self.label = label
        self.text_blocks = text_blocks
        self.custom = self.is_custom()

    def is_custom(self):
        return not self.fact.concept.xml_id.startswith("us-gaap")

    def set_parent(self, cost):
        if self.costs_equal(self.cost, cost.cost):
            return
        
        self.parent_cost = cost

    def add_child(self, cost):
        if self.costs_equal(self.cost, cost.cost):
            return

        for child in self.child_costs:
            if self.costs_equal(child.cost, cost.cost) or self.costs_equal(child.cost, cost.cost * -1):
                return

        self.child_costs.append(cost)

    def __eq__(self, other): 
        if type(self) != type(other):
            return NotImplemented

        names_equal = self.names_equal(other)
        costs_equal = self.costs_equal(self.cost, other.cost) 
        return costs_equal and names_equal

    def names_equal(self, other):
        return self.fact.concept.name == other.fact.concept.name

    def get_name(self):
        return self.fact.concept.name

    def costs_equal(self, a, b):
        return a == b

    def get_cost(self):
        return self.cost / 1000000

    def has_explicit_member_match(self, search):
        for segment in self.fact.context.segments:
            if segment.member.name == search:
                return True 
        return False

    def is_payment(self):
        return self.has_explicit_member_match("otherincome")

    def contains_keywords(self, term, searches):
        for search in searches:
            if search in term:
                return True 
        return False

    def update_for_text_block(self, text_block, terse, reverse_if_positive=True, reverse_if_negative=False):
        ta = TextAnalyser(text_block, terse, self.fact)
        if reverse_if_positive and ta.has_positive():
            # if everything indicates that this debit item is a true expense, it should 
            # be left untouched. but if it's indicated as income, it should be reversed
            self.cost *= -1
        elif reverse_if_negative and ta.has_negative():
            self.cost *= -1

    def update_for_text_blocks(self, terse, reverse_if_positive=True, reverse_if_negative=False):
        for text_block in self.text_blocks:
            self.update_for_text_block(text_block, terse, reverse_if_positive, reverse_if_negative)

    def inspect_all_text_facts_for_match(self, text_facts, reverse_if_positive=True, reverse_if_negative=False):
        terse = self.label.get("terseLabel").lower()
        for fact in text_facts:
            if terse in fact.value:
                self.update_for_text_block(fact, terse, reverse_if_positive, reverse_if_negative)

    def validate(self, text_facts=[]):
        if self.validated:
            return 
        
        self.validated = True 

        balance = self.fact.concept.balance
        concept_id = self.fact.concept.xml_id

        if concept_id in BALANCE_TAGS_REVERSAL:
            self.cost *= -1
            return

        if concept_id.lower().endswith("gains") and balance == "credit":
            self.cost *= -1
            return

        label = self.label.get("label").lower()
        terse = self.label.get("terseLabel").lower()
        negated_terse = self.label.get("negatedTerseLabel").lower()
        docs = self.label.get("documentation").lower()

        if not negated_terse:
            negated_terse = terse

        credit_terms = ["(credits)"]
        if balance == "credit":
            if "PaymentsFor" in concept_id:
                return
                
            if "GrantRecognized" in concept_id and self.cost < 0:
                return

            if self.cost < 0 and any(t in label or t in negated_terse for t in credit_terms):
                return
            
            if "gains" in negated_terse and "loss" not in negated_terse:
                self.cost *= -1
                return

            if self.text_blocks:
                self.update_for_text_blocks(negated_terse, reverse_if_negative=True)
                return

            self.cost *= -1
            return

        # If somebody has indicated that + is gain and - is negative, but this expense has been 
        # marked as a debit, there's a contradiction. 
        credit_terms = ["(losses)", "(cost)"]
        if balance == "debit" and any(t in label or t in negated_terse for t in credit_terms):
            if self.text_blocks:
                self.update_for_text_blocks(negated_terse, reverse_if_positive=True)

        credit_terms = ["cash inflow", "cash received"]
        if balance == "debit" and any(t in docs or t in negated_terse for t in credit_terms):
            self.cost *= -1
            