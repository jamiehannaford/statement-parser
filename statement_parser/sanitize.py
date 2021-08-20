import itertools
import math

from xbrl.linkbase import PresentationArc
from xbrl.instance import NumericFact, Concept, AbstractContext

exclusions = []

class GenericCost:
    def __init__(self, concept_id, value):
        self.cost = value
        self.concept_id = concept_id

        concept = Concept(concept_id, "", "")
        context = AbstractContext("", None)
        self.fact = NumericFact(concept, context, value, None, 0)

def isclose(a, b, sf=None, rel_tol=None):
    results = []

    if sf:
        results.append(math.isclose(a, b, abs_tol=10**-int(sf)))
    else:
        results.append(math.isclose(a, b))

    if rel_tol:
        results.append(math.isclose(a, b, rel_tol=rel_tol))

    return any(results)

def remove_sum_map(input_map):
    input_vals = list(input_map.values())
    values = input_vals.copy()

    initial_sum = sum(values)
    inverse = {v: k for k, v in input_map.items()}
    filtered = dedupe_list_all(list(input_vals))

    if len(filtered) != len(input_vals):
        for item in input_vals:
            if item not in filtered:
                key = inverse[item]
                del input_map[key]

    output_map = {}
    for key, elem in input_map.items():
        if not similar_to(initial_sum, 2*elem):
            output_map[key] = elem
    return output_map

def remove_sum_list(input_list):
    initial_sum = sum(input_list)
    for elem in input_list:
        if similar_to(2*elem, initial_sum):
            input_list.remove(elem)
    return input_list

def dedupe_facts_highest(costs):
    if len(costs) < 3:
        return costs

    costs.sort(key=lambda c: c.value)
    highest = costs.pop()

    if isclose(highest.value, sum(c.value for c in costs), dec(highest)):
        return costs

    if len(costs) > 12:
        return costs

    output = costs.copy()
    for i in range(len(costs), 0, -1):
        for seq in itertools.combinations(costs, i):
            if sum(c.value for c in seq) == highest:
                output = [x for x in output if x not in seq]

    output.append(highest)

    return output

def dedupe_costs_highest(costs):
    if len(costs) < 3:
        return costs

    costs.sort(key=lambda c: c.cost)
    highest = costs.pop()

    if isclose(highest.cost, sum(c.cost for c in costs), dec(highest.fact)):
        return costs

    output = costs.copy()
    for i in range(len(costs), 0, -1):
        for seq in itertools.combinations(costs, i):
            if sum(c.cost for c in seq) == highest:
                output = [x for x in output if x not in seq]

    output.append(highest)

    return output

def dec(cost):
    if cost.decimals is None:
        return 0
    return cost.decimals

def dedupe_facts_all(costs):
    copied_list = costs.copy()
    options = {}
    removed = []

    for cost in costs:
        if cost in removed:
            continue
        
        for elem in [c for c in costs if c != cost and c not in removed]:
            if isclose(cost.value, elem.value, min(dec(cost), dec(elem))):
                copied_list.remove(elem)
                removed.append(elem)

    if len(copied_list) > 10:
        return copied_list

    for i in range(len(copied_list), 1, -1):
        for seq in itertools.combinations(copied_list, i):
            for option in [i for i in copied_list if i not in seq]:
                seq_sum = sum(c.value for c in seq)
                if isclose(seq_sum, option.value, dec(option)):
                    diff = abs(seq_sum - option.value)
                    options[diff] = [x for x in copied_list if x not in seq]

    if options:
        return options[min(options, key=int)]
    
    return copied_list

def dedupe_costs_all(costs):
    copied_list = costs.copy()
    options = {}
    removed = []

    for cost in costs:
        if cost in removed:
            continue
        
        for elem in [c for c in costs if c != cost and c not in removed]:
            if isclose(cost.cost, elem.cost, min(dec(cost.fact), dec(elem.fact))):
                copied_list.remove(elem)
                removed.append(elem)

    if len(copied_list) > 10:
        return copied_list

    for i in range(len(copied_list), 1, -1):
        for seq in itertools.combinations(copied_list, i):
            for option in [i for i in copied_list if i not in seq]:
                seq_sum = sum(c.cost for c in seq)
                if isclose(seq_sum, option.cost, dec(option.fact)):
                    diff = abs(seq_sum - option.cost)
                    options[diff] = [x for x in copied_list if x not in seq]

    if options:
        return options[min(options, key=int)]
    
    return copied_list

def dedupe_facts(costs):
    cost_list = [c.value for c in costs]
    input_sum = sum(cost_list)
    input_len = len(costs)
    if input_sum == 0:
        return costs

    costs = dedupe_facts_highest(costs)
    if len(costs) != input_len:
        return costs

    costs = dedupe_facts_all(costs)
    for elem in costs:
        if elem.value *-1 in cost_list:
            costs.remove(elem)

    return costs

def dedupe_map(input_map):
    costs = []
    for concept_id, value in input_map.items():
        costs.append(GenericCost(concept_id, value))
    
    costs = dedupe_costs(costs)

    return {c.concept_id: c.cost for c in costs}

def dedupe_costs(costs):
    cost_list = [c.cost for c in costs]
    input_sum = sum(cost_list)
    input_len = len(costs)
    if input_sum == 0:
        return costs

    costs = dedupe_costs_highest(costs)
    if len(costs) != input_len:
        return costs

    costs = dedupe_costs_all(costs)
    for elem in costs:
        if elem.cost *-1 in cost_list:
            costs.remove(elem)

    return costs

def nums_within_range(a, b, range_p=0.99, should_abs=True):
    if should_abs:
        a = abs(a)
        b = abs(b)
    return a*range_p <= b <= a*(1-range_p+1)


class Element:
    def __init__(self, concept_id, cost, children = []):
        self.concept_id = concept_id
        self.cost = cost 
        self.children = children

    def process(self):
        if self.children:
            outputs = {}
            has_list = False
            for child in self.children:
                if child:
                    res = child.process()
                    if res:
                        outputs[res] = child
                        if isinstance(res, list):
                            has_list = True
            if outputs:
                if not has_list:
                    items = list(outputs.keys())
                    elem_sum = sum(items)

                    for key, elem in outputs.items():
                        if elem_sum == key*2:
                            items.remove(key)
                            exclusions.append(elem)

                    return sum(items)

                return outputs.keys()

        return self.cost

class Sanitizer:
    def __init__(self, pre_linkbases, total_costs):
        self.pre_linkbases = pre_linkbases
        self.total_costs = total_costs

    def sanitize(self):
        for lb in self.pre_linkbases:
            for el in lb.extended_links:
                for rl in el.root_locators:
                    res = self.recurse_elements(rl, self.total_costs)
                    if res:
                        res.process()

        if exclusions:
            for excl in exclusions:
                if excl.concept_id in self.total_costs:
                    del self.total_costs[excl.concept_id]

        return remove_sum_map(self.total_costs)

    def recurse_elements(self, elem, labels):
        if isinstance(elem, PresentationArc):
            concept_id = elem.to_locator.concept_id
            if concept_id in labels:
                return Element(concept_id, labels[concept_id])
            else:
                return self.recurse_elements(elem.to_locator, labels)

        if len(elem.children) == 0:
            if elem.concept_id in labels:
                return Element(elem.concept_id, labels[elem.concept_id])
            else:
                return None

        children = []
        for child in elem.children:
            res = self.recurse_elements(child, labels)
            children.append(res)
            
        return Element(elem.concept_id, None, children)
