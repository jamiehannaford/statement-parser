from statement_parser.sanitize import Sanitizer, remove_sum_list, dedupe_list, nums_within_range

class ExpenseGroup:
    def __init__(self, name, tags, instance, precedent_tags=None, strict_mode=False):
        self.name = name
        self.costs = []
        self.backup_costs = []
        self.tags = tags
        self.pre_linkbases = instance.taxonomy.pre_linkbases
        self.instance = instance 
        self.precedent_tags = precedent_tags

        self.strict_mode = strict_mode
        self.root_concepts = self.load_root_concepts()

    def load_root_concepts(self):
        root_concept_ids = []
        for elr in self.instance.taxonomy.link_roles:
            if elr.calculation_link is None or len(elr.calculation_link.root_locators) == 0:
                continue
            for loc in elr.calculation_link.root_locators:
                for child in loc.children:
                    root_concept_ids.append(child.to_locator.concept_id)
        return root_concept_ids

    def is_cost(self, fact, profile):
        # todo: make this more pluggable, and also permit certain tags to be added
        if self.name == "interest" and profile["sector"] == "Financial Services":
            return False

        if fact.concept.name.lower() not in self.tags:
            return False

        if self.strict_mode and fact.concept.xml_id not in self.root_concepts:
            self.add(fact, backup=True)
            return False

        return True

    # sometimes companies (notably KO) will specify the impact of a cost on both 
    # the operating and non-operating income. if left unvalidated, this will lead
    # to double-counting
    # def validate_operating_axis(self, fact):
    def add(self, fact, backup=False):
        rc = self.generate_cost(fact)
        if rc in self.costs or rc.cost == 0:
            return

        if backup:
            self.backup_costs.append(rc)
        else:
            self.costs.append(rc)

    def contains_similar_context(self, input_cost, costs):
        for cost in costs:
            if input_cost.fact.context.xml_id.startswith(cost.fact.context.xml_id) and \
                nums_within_range(input_cost.cost, cost.cost, 0.95):
                return True
        return False

    def group_specific_processing(self):
        return self.costs

    def back_up_permitted(self, concepts, concept_id):
        return concept_id not in concepts

    # For a given collection of tags with the same concept/tag name:
    # - Iterate over their contexts
    # - Group by dimension and find subtotals
    # - Remove any duplicative subtotals
    # - Add this deduped value to the total costs 
    def organise_costs(self):
        costs = self.group_specific_processing()

        precedent_vals = self.process_precedence_tags(costs)
        if precedent_vals:
            return precedent_vals

        vals = []
        concepts = {}
        for cost in costs:
            cost.validate()
            if cost.cost == 0 or cost.cost in vals:
                continue
            
            concept_id = cost.fact.concept.xml_id
            
            if concept_id not in concepts:
                concepts[concept_id] = []

            if self.contains_similar_context(cost, concepts[concept_id]):
                continue

            concepts[concept_id].append(cost)
            vals.append(cost.cost)

        for backup_cost in self.backup_costs:
            concept_id = backup_cost.fact.concept.xml_id
            if self.back_up_permitted(concepts, concept_id):
                concepts[concept_id] = [backup_cost]

        total_costs = {}
        total_values = []
        for concept_id, costs in concepts.items():
            subtotal = 0
            contexts = {}

            costs = dedupe_list([c.get_cost() for c in costs])
            subtotal = sum(costs)

            has_conflict = False
            for potential_conflict in total_values:
                if nums_within_range(potential_conflict, subtotal, 0.93):
                    has_conflict = True 
                    break
                    
            if has_conflict:
                continue

            total_values.append(subtotal)
            total_costs[concept_id] = subtotal

        s = Sanitizer(self.pre_linkbases, total_costs)
        return s.sanitize()

    def process_precedence_tags(self, costs):
        if not self.precedent_tags:
            return
        
        for cost in costs:
            concept_id = cost.fact.concept.xml_id
            if concept_id.lower() in self.precedent_tags:
                return {concept_id: cost.get_cost()}

    def output(self):
        costs = self.organise_costs()

        log_outputs = [f"{self.name.upper()}"]

        total = 0
        for name, cost in costs.items():
            if cost == 0:
                continue
            log_outputs.append(f"- {name} {cost}")
            total += cost
        
        log_outputs.append(f"TOTAL {total}")

        return total, log_outputs