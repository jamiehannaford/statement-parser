from xbrl_parser.linkbase import PresentationArc, CalculationArc
from xbrl_parser.instance import NumericFact

from operator import attrgetter
from datetime import timedelta

from statement_parser.sanitize import dedupe_facts, isclose
from statement_parser.validators.synonyms import SynonymValidator

class ArcValidator:
    def __init__(self, instance, categories, labels):
        self.instance = instance
        self.elem_ids = []
        self.elements = []
        self.removed = []
        self.decreased = []
        self.decreased_parent = []
        self.categories = categories
        self.labels = labels

        for cat in self.categories:
            if cat.name == "company-defined other":
                self.cdo_cat = cat

        self.synonym_validator = SynonymValidator(instance)

    def tag_is_non_standard(self, child_id):
        return child_id.split("_")[0] != "us-gaap"

    def mark_protected(self, child_id):
        for elem in self.elements:
            if elem.concept.xml_id == child_id:
                elem.protected = True

    def find_fact_value(self, concept_id, search_all=False):
        facts = []
        elements = self.elements 
        if search_all:
            elements = self.instance.facts 

        for fact in elements:
            if fact.concept.xml_id == concept_id and isinstance(fact, NumericFact):
                facts.append(fact)

        facts = [f.value for f in dedupe_facts(facts)]
        facts.sort(reverse=True)
        return facts

    def make_cost(self, child_id, amount):
        for fact in self.elements:
            concept_id = fact.concept.xml_id
            label = self.labels[concept_id]
            if concept_id == child_id:
                for cat in self.categories:
                    if cat.is_cost(fact, label):
                        cost = cat.generate_cost(fact, cat.fact_label(fact), text_blocks=cat.fetch_text_blocks())
                        cost.cost = amount
                        cost.validate()
                        return cost.cost

    def filter_over_3m(self, costs):
        output = []
        for cost in costs:
            delta = cost.context.end_date - cost.context.start_date
            if delta > timedelta(weeks=50):
                output.append(cost)
        return output

    def collect_highest_dimension_fact(self, concept_id):
        dimension_map = {}
        elements = []

        for fact in self.elements:
            fact_concept_id = fact.concept.xml_id
            if fact_concept_id == concept_id:
                num = len(fact.context.segments)
                if num not in dimension_map:
                    dimension_map[num] = []
                dimension_map[num].append(fact)
                elements.append(fact_concept_id)

        if dimension_map:
            costs = dimension_map[min(dimension_map, key=int)]
            costs = self.filter_over_3m(costs)
            highest = None 
            for cost in costs:
                if not highest or abs(cost.value) > abs(highest.value):
                    highest = cost
            return [highest]
        else:
            return []
            
    def decrease_fact_value(self, concept_id, amount, child_id):
        if concept_id == child_id:
            return
            
        if self.synonym_validator.has_parent_conflict(concept_id, child_id):
            return

        aggregate_facts = self.collect_highest_dimension_fact(concept_id)
        if len(aggregate_facts) == 0:
            return

        for fact in aggregate_facts:
            if fact not in self.decreased_parent:
                label = self.labels[fact.concept.xml_id]
                for cat in self.categories:
                    if cat.is_cost(fact, label):
                        cost = cat.generate_cost(fact, cat.fact_label(fact), text_blocks=cat.fetch_text_blocks())
                        cost.validate()
                        fact.value = cost.cost

            balance = fact.concept.balance
            cost = self.make_cost(child_id, amount)
            if cost in self.decreased:
                continue

            print(fact, child_id, cost, balance)
            # if fact.concept.balance == "debit":
                # fact.value += cost
            # else:
            fact.value -= cost
            
            self.decreased.append(cost)
            self.decreased_parent.append(fact)

    def remove_elem_from_ids(self, elem_id):
        if elem_id in self.element_ids:
            self.element_ids.remove(elem_id)

    def remove_elem(self, elem_id):
        self.remove_elem_from_ids(elem_id)
        self.elements = [elem for elem in self.elements if elem.concept.xml_id != elem_id]
        self.removed.append(elem_id)

    def is_total_label(self, elem):
        if elem.preferred_label and elem.preferred_label.endswith("totalLabel"):
            return True 

        concept_id = elem.to_locator.concept_id.lower()
        assumed_totals = ["us-gaap_NonoperatingIncomeExpense"]
        return any((w.lower() == concept_id for w in assumed_totals))

    def abstract_concept(self, concept_id):
        return concept_id in self.element_ids and self.element_ids[concept_id].abstract

    def follow_pre_elem(self, elem):
        if isinstance(elem, PresentationArc):
            return self.follow_pre_elem(elem.to_locator)

        if len(elem.children) == 0:
            return elem
    
        # if elem.concept_id in self.element_ids:
        highest_order = max(float(child.order) for child in elem.children)
        last_child = None
        last_child_id = None 

        for child in elem.children:
            if float(child.order) > highest_order and self.is_total_label(child) and len(elem.children) > 2:
                last_child = child 
                last_child_id = child.to_locator.concept_id

        if last_child and last_child_id in self.element_ids and "abstract" not in elem.concept_id.lower():
            removals = []
            
            for child in elem.children:
                child_id = child.to_locator.concept_id
                if child_id == last_child_id:
                    continue

                if child_id not in self.element_ids:
                    if self.tag_is_non_standard(child_id):
                        vals = self.find_fact_value(child_id, search_all=True)
                        for _elem in self.elements:
                            if _elem.value in vals:
                                self.mark_protected(child_id)
                                removals.append(_elem.concept.xml_id)
                else:
                    self.mark_protected(child_id)
                    removals.append(child_id)

            for child_id in removals:
                vals = self.find_fact_value(child_id)
                if len(vals) == 1:
                    self.remove_elem_from_ids(child_id)
                    self.decrease_fact_value(last_child_id, vals[0], child_id)
                else:
                    self.remove_elem(child_id)
      
        for _child in elem.children:
            self.follow_pre_elem(_child)

    def follow_cal_elem(self, elem, parent_matches=False):
        if isinstance(elem, CalculationArc):
            return self.follow_cal_elem(elem.to_locator)

        if len(elem.children) == 0:
            return elem

        for child in elem.children:
            child_id = child.to_locator.concept_id
            elem_matches = elem.concept_id in self.element_ids or elem.concept_id in self.removed
            if child_id in self.element_ids and elem_matches:
                vals = self.find_fact_value(child_id)
                self.mark_protected(child_id)
                if len(vals) == 1:
                    self.remove_elem_from_ids(child_id)
                    self.decrease_fact_value(elem.concept_id, vals[0], child_id)
                else:
                    self.remove_elem(child_id)

            self.follow_cal_elem(child)
            
    def process(self, elements):
        self.elements = elements
        self.element_ids = [elem.concept.xml_id for elem in elements]

        for lb in self.instance.taxonomy.cal_linkbases:
            for el in lb.extended_links:
                for rl in el.root_locators:
                    self.follow_cal_elem(rl)

        for lb in self.instance.taxonomy.pre_linkbases:
            for el in lb.extended_links:
                for rl in el.root_locators:
                    self.follow_pre_elem(rl)

        concept_ids = [f.concept.xml_id for f in self.decreased_parent]
        output = []
        for elem in self.elements:
            if elem.concept.xml_id in concept_ids:
                if elem in self.decreased_parent:
                    output.append(elem)
            else:
                output.append(elem)

        return output