import itertools
from xbrl_parser.linkbase import PresentationArc

exclusions = []

def similar_to(a, b, allowance=0.995):
    return a*allowance <= b <= a*(1-allowance+1)

def remove_sum_map(input_map):
    initial_sum = sum(input_map.values())
    output_map = {}
    for key, elem in input_map.items():
        if initial_sum != 2*elem:
            output_map[key] = elem
    return output_map

def remove_sum_list(input_list):
    initial_sum = sum(input_list)
    for elem in input_list:
        if similar_to(2*elem, initial_sum):
            input_list.remove(elem)
    return input_list

def dedupe_list_highest(input_list):
    input_list.sort()
    highest = input_list[-1]
    input_list.pop()

    output = input_list.copy()
    for i in range(len(input_list), 0, -1):
        for seq in itertools.combinations(input_list, i):
            if sum(seq) == highest:
                output = [x for x in output if x not in seq]

    return output + [highest]

def dedupe_list_all(input_list):
    copied_list = input_list.copy()
    for i in range(len(copied_list), 0, -1):
        for seq in itertools.combinations(copied_list, i):
            for option in [i for i in copied_list if i not in seq]:
                if nums_within_range(sum(seq), option, 0.92):
                    copied_list = [x for x in copied_list if x not in seq]
    return copied_list

def dedupe_list(input_list):
    attempt1 = dedupe_list_highest(input_list)
    if len(attempt1) != len(input_list):
        input_list = attempt1
    return dedupe_list_all(input_list)

def nums_within_range(a, b, range_p=0.99):
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