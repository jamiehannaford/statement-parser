import math

from statement_parser.expenses.company_other import CompanyDefinedOtherGroup
from statement_parser.expenses.interest import InterestExpenseGroup
from statement_parser.expenses.restructuring import RestructuringExpenseGroup
from statement_parser.sanitize import isclose

# If there's an item marked as "other income" and it matches up exactly to another expense,
# chances are we should remove it to avoid double counting.
class OtherIncomeValidator:
    def __init__(self, instance, labels, profile):
        self.instance = instance
        self.company_defined_other = CompanyDefinedOtherGroup(self.instance, [], profile)
        self.interest = InterestExpenseGroup(self.instance, [], profile)
        self.restructuring = RestructuringExpenseGroup(self.instance, [], profile)
        self.labels = labels
        self.interest_costs = []
        self.restructuring_costs = []
    
    def label_contains_interest_conflict(self, fact):
        if fact.concept.xml_id not in self.labels:
            return False 
        
        label = self.labels[fact.concept.xml_id]
        terse = label.get("terseLabel").lower()
        return "interest" in terse

    def label_contains_restructuring_conflict(self, fact):
        if fact.concept.xml_id not in self.labels:
            return False 
        
        label = self.labels[fact.concept.xml_id]
        terse = label.get("terseLabel").lower()
        return "gains" in terse

    def label_contains_membership(self, fact):
        if fact.concept.xml_id not in self.labels:
            return False 
        
        label = self.labels[fact.concept.xml_id]
        return label.any_contains("membership")

    def process(self, elements):
        value_map = {}
        cdo_map = {}
        cdos = {}
        for elem in elements:
            label = self.labels[elem.fact.concept.xml_id]

            if elem.value not in value_map:
                value_map[elem.value] = 0
            value_map[elem.value] += 1 

            if self.interest.is_cost(elem, label):
                self.interest_costs.append(elem)

            if self.restructuring.is_cost(elem, label):
                self.restructuring_costs.append(elem)

            if self.company_defined_other.is_cost(elem, label):
                if elem.value not in cdo_map:
                    cdo_map[elem.value] = 0
                    
                if elem.concept.xml_id not in cdos:
                    cdos[elem.concept.xml_id] = []

                cdo_map[elem.value] += 1 
                cdos[elem.concept.xml_id].append(elem)
        
        output = []
        for elem in elements:
            label = self.labels[elem.fact.concept.xml_id]
            
            should_append = True
            if self.company_defined_other.is_cost(elem, label):
                if cdo_map[elem.value] > 1:
                    cdo_map[elem.value] -= 1
                    should_append = False
                    continue

                if value_map[elem.value] > 1:
                    continue 
                
                if self.label_contains_interest_conflict(elem): 
                    for interest_cost in self.interest_costs:
                        decs = min(interest_cost.decimals, elem.decimals)
                        if isclose(abs(interest_cost.value), abs(elem.value), sf=decs):
                            should_append = False
                            break

                if self.label_contains_membership(elem):
                    should_append = False

                elif self.label_contains_restructuring_conflict(elem): 
                    for restructuring_cost in self.restructuring_costs:
                        decs = min(restructuring_cost.decimals, elem.decimals)
                        if isclose(abs(restructuring_cost.value), abs(elem.value), sf=decs, rel_tol=0.01):
                            should_append = False
                            break

            if should_append:
                output.append(elem)
                
        return output
