import math
from xbrl.instance import NumericFact

class TotalValidator:
    def __init__(self, instance):
        self.instance = instance

    def isclose(self, a, b, sf=None):
        if sf:
            return math.isclose(a, b, abs_tol=10**-sf)
        else:
            return math.isclose(a, b)

    def check_list_sums_to_n(self, elems, n):
        elem_sum = sum(elem.value for elem in elems)
        return self.isclose(n.value, elem_sum, n.decimals)

    def process(self, elements):
        concept_map = {}
        concept_val = {}

        for elem in elements:
            concept_id = elem.concept.xml_id 
            if concept_id not in concept_map:
                concept_map[concept_id] = []
                concept_val[concept_id] = []
            
            if elem.value in concept_val[concept_id]:
                continue

            concept_map[concept_id].append(elem)
            concept_val[concept_id].append(elem.value)

        output = []
        for concept, elems in concept_map.items():
            elems.sort(key=lambda elem: elem.value)

            # check highest
            if isinstance(elems[-1], NumericFact) and self.check_list_sums_to_n(elems[:-1], elems[-1]):
                output.append(elems[-1])
                continue

            # check lowest
            if isinstance(elems[0], NumericFact) and self.check_list_sums_to_n(elems[1:], elems[0]):
                output.append(elems[0])
                continue

            output.extend(elems)
            
        return output