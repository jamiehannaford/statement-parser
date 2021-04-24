from xbrl_parser.linkbase import PresentationArc

exclusions = []

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
                    res.process()

        if exclusions:
            for excl in exclusions:
                if excl.concept_id in self.total_costs:
                    del self.total_costs[excl.concept_id]

        return self.total_costs

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