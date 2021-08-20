from statement_parser.expenses.restructuring import RestructuringExpenseGroup
from statement_parser.expenses.write_down import WriteDownExpenseGroup
from statement_parser.expenses.discontinued_operations import DiscontinuedOperationsExpenseGroup
from statement_parser.sanitize import dedupe_facts, isclose
from statement_parser.labelset import LabelSet

class RestructuringValidator:
    def __init__(self, instance, profile):
        self.instance = instance 
        self.restructuring_group = RestructuringExpenseGroup(self.instance, [], profile)
        self.write_down_group = WriteDownExpenseGroup(self.instance, [], profile)
        self.disc_ops_group = DiscontinuedOperationsExpenseGroup(self.instance, [], profile)
        self.populate_labels()

    def populate_labels(self):
        self.labels = {}
        for lb in self.instance.taxonomy.lab_linkbases:
            for el in lb.extended_links:
                for rl in el.root_locators:
                    for c in rl.children:
                        for l in c.labels:
                            if rl.concept_id not in self.labels:
                                self.labels[rl.concept_id] = LabelSet()
                            self.labels[rl.concept_id].add(l)

    def process(self, elements):
        val_map = {}
        rs_costs = []
        wd_costs = []

        output = []

        for fact in elements:
            label = self.labels[fact.concept.xml_id]
            if self.restructuring_group.is_cost(fact, label):
                rs_costs.append(fact)
            elif self.write_down_group.is_cost(fact, label) or self.disc_ops_group.is_cost(fact, label):
                wd_costs.append(fact)
            else:
                continue
            
            if fact.value not in val_map:
                val_map[fact.value] = 0
            
            val_map[fact.value] += 1
            output.append(fact)

        impairments_processed = False
        excluded_ids = []
        for elem in rs_costs:
            concept_id = elem.concept.xml_id

            if val_map[elem.value] > 1:
                output.remove(elem)
                continue

            for wd_cost in wd_costs:
                if isclose(elem.value, wd_cost.value, rel_tol=0.01):
                    elements = [f for f in elements if f.concept.xml_id != concept_id]
                    output.remove(elem)
                    break

            if elem not in output:
                continue
            
            if concept_id in self.labels:
                ls = self.labels[concept_id]
                terse = ls.get("terseLabel").lower()
                label = ls.get("label").lower()
                if "impairment" in label and "excluding" not in label and not impairments_processed:
                    for wd_elem in wd_costs:
                        elements.remove(wd_elem)
                    impairments_processed = True

        for elem in wd_costs:
            if val_map[elem.value] > 1 and [f for f in rs_costs if f.value == elem.value]:
                output.remove(elem)
                val_map[elem.value] -= 1

        deduped = dedupe_facts(output)
        for elem in output:
            if elem not in deduped and elem in elements:
                elements.remove(elem)

        return elements