class Expense:
    def __init__(self, fact):
        self.fact = fact
        self.cost = float(fact.value)
        self.parent_cost = None 
        self.child_costs = []

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

    def validate(self):
        balance = self.fact.concept.balance

        # if balance == "credit":
            # self.cost = abs(self.cost) * -1

        keywords = ["expense", "gainloss"]
        # if self.contains_keywords(self.get_name().lower(), keywords) and balance == "credit" and self.cost < 0:
            # self.cost *= -1

        concept_id = self.fact.concept.xml_id
        if concept_id == "us-gaap_InterestExpense":
            self.cost = abs(self.cost) * -1
        
        if self.is_payment():
            self.cost = 0