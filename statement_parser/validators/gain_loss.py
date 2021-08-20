import math 

from statement_parser.expenses.restructuring import RestructuringExpenseGroup

class GainLossValidator:
    def __init__(self, instance, profile):
        self.instance = instance 
        self.restructuring_group = RestructuringExpenseGroup(self.instance, [], profile)
    
    def is_cost(self, fact):
        return "GainLossOn" in fact.concept.xml_id and self.restructuring_group.is_cost(fact, None) 

    def process(self, elements):
        gain_loss_facts = []
        removals = []

        for fact in elements:
            if not self.is_cost(fact):
                continue
            
            should_append = True
            for existing_fact in gain_loss_facts:
                if math.isclose(existing_fact.value, fact.value, rel_tol=0.025):
                    should_append = False 
                    removals.append(fact)
                    break

            if should_append:
                gain_loss_facts.append(fact)
        
        return [e for e in elements if e not in removals]