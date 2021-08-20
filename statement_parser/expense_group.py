from statement_parser.sanitize import dedupe_costs, isclose, dedupe_map
from numpy import mean
import math
import re
from operator import attrgetter

from xbrl.instance import TimeFrameContext, NumericFact, SimpleUnit

class ExpenseGroup:
    def __init__(self, name, tags, instance, labels=None, precedent_tags=None, strict_mode=False, 
        text_blocks=None, profile=None):
        self.name = name
        self.costs = []
        self.backup_costs = []
        self.tags = tags
        self.pre_linkbases = instance.taxonomy.pre_linkbases
        self.instance = instance 
        self.precedent_tags = precedent_tags
        self.processed_precendent_tags = False
        self.strict_mode = strict_mode
        self.root_concepts = self.load_root_concepts()
        self.labels = labels
        self.text_blocks = text_blocks
        self.filter_highest_only = False
        self.profile = profile

    def load_root_concepts(self):
        root_concept_ids = []
        for elr in self.instance.taxonomy.link_roles:
            if elr.calculation_link is None or len(elr.calculation_link.root_locators) == 0:
                continue
            for loc in elr.calculation_link.root_locators:
                for child in loc.children:
                    root_concept_ids.append(child.to_locator.concept_id)
        return root_concept_ids

    def fact_label(self, fact):
        if self.labels and fact.concept.xml_id in self.labels:
            return self.labels[fact.concept.xml_id]
        else:
            return None

    def valid_unit(self, unit):
        for unit_id, known_unit in self.instance.unit_map.items():
            if unit_id != unit.unit_id:
                continue 
            if not isinstance(known_unit, SimpleUnit):
                continue
            return "usd" in known_unit.unit.lower() or known_unit.unit_id.lower()
        return False

    def is_sector_financial(self, sector):
        return sector == "Financial Services"

    def is_sector_real_estate(self, sector):
        return sector == "Real Estate"

    def get_sector(self):
        if not self.profile:
            return None
        
        return self.profile["sector"]

    def supports_sector(self, sector, fact):
        return True

    def is_cost(self, fact, label):
        if not isinstance(fact, NumericFact):
            return False

        if not self.valid_unit(fact.unit):
            return False

        if fact.concept.name.lower() not in self.tags:
            return False
        
        sector = self.get_sector()
        if sector and not self.supports_sector(sector, fact):
            return False

        return True

    def fetch_text_blocks(self):
        if not self.text_blocks:
            return None 
        
        text_blocks = []
        for fact in self.instance.facts:
            if fact.concept.xml_id in self.text_blocks:
                text_blocks.append(fact)

        return text_blocks 

    def add(self, fact, backup=False):
        rc = self.generate_cost(fact, self.fact_label(fact), text_blocks=self.fetch_text_blocks())

        if rc in self.costs or rc.cost == 0:
            return

        if backup:
            self.backup_costs.append(rc)
        else:
            self.costs.append(rc)

    def contains_similar_context(self, input_cost, costs):
        for cost in costs:
            if input_cost.fact.context.xml_id.startswith(cost.fact.context.xml_id) and \
                isclose(input_cost.cost, cost.cost, input_cost.fact.decimals):
                return True
        return False

    def group_specific_processing(self, costs):
        return costs

    def back_up_permitted(self, concepts, concept_id):
        return concept_id not in concepts

    def process_concepts(self, costs, text_facts=[]):
        vals = []
        concepts = {}
        for cost in costs:
            cost.validate(text_facts=text_facts)
            if cost.cost == 0 or cost.cost in vals:
                continue
            
            concept_id = cost.fact.concept.xml_id
            
            if concept_id not in concepts:
                concepts[concept_id] = []

            if self.contains_similar_context(cost, concepts[concept_id]):
                continue

            concepts[concept_id].append(cost)
            vals.append(cost.cost)

        return concepts

    def filter_by_highest_term(self, search_terms, costs, allow_protected=True):
        highest_costs = {}
        
        for cost in costs:
            for search_term in search_terms:
                if search_term not in highest_costs:
                    highest_costs[search_term] = 0

                res = re.search(search_term.lower(), cost.fact.concept.xml_id.lower(), re.IGNORECASE)
                if res and abs(cost.cost) > abs(highest_costs[search_term]):
                    highest_costs[search_term] = cost.cost
        
        output = []
        excluded = []

        for cost in costs:
            if allow_protected and cost.fact.protected:
                output.append(cost)
                continue 
            
            for search_term in search_terms:
                if cost in excluded:
                    continue                
                
                res = re.search(search_term.lower(), cost.fact.concept.xml_id.lower(), re.IGNORECASE)
                if res and cost.cost != highest_costs[search_term]:
                    excluded.append(cost)
                    continue
                
                output.append(cost)

        return [c for c in output if c not in excluded]

    # For a given collection of tags with the same concept/tag name:
    # - Iterate overfgroup_specific_processing their contexts
    # - Group by dimension and find subtotals
    # - Remove any duplicative subtotals
    # - Add this deduped value to the total costs 
    def organise_costs(self, verbose, text_facts=[], shorten=True):
        # print([c.cost for c in self.costs])
        costs = self.group_specific_processing(self.costs)
        # print([c.cost for c in costs])
        costs = self.process_precedence_tags(costs)
        # print([c.cost for c in costs])
        concepts = self.process_concepts(costs, text_facts=text_facts)

        if self.backup_costs and not self.processed_precendent_tags:
            for backup_cost in self.backup_costs:
                concept_id = backup_cost.fact.concept.xml_id
                if self.back_up_permitted(concepts, concept_id):
                    costs.append(backup_cost)
                    concepts[concept_id] = [backup_cost]

            costs = self.group_specific_processing(costs)
            concepts = self.process_concepts(costs, text_facts=text_facts)

        cost_map = {}
        dec_map = {}

        for concept_id, costs in concepts.items():
            if self.filter_highest_only:
                costs = [max(costs, key=attrgetter('cost'))]
                
            costs = dedupe_costs(costs)

            # If we have a 12 month expense, that should trump a 3 month expense
            costs = self.filter_time_spans(costs)

            cost_list = [c.cost for c in costs]
            subtotal = sum(cost_list)
            average_decimals = mean([int(c.fact.decimals) for c in costs if c.fact.decimals is not None])
            if math.isnan(average_decimals):
                average_decimals = 0.0

            has_conflict = False
            for existing_cost in dec_map.values():
                sf = min(int(existing_cost["dec"]), int(average_decimals))
                if math.isclose(existing_cost["val"], subtotal, abs_tol=10**-sf):
                    has_conflict = True
                    break
                
            if has_conflict:
                continue
            
            if verbose:
                print(concept_id, cost_list)
                
            dec_map[concept_id] = {"dec": average_decimals, "val": subtotal}
            cost_map[concept_id] = costs

        # Now we need to de-dupe this use case:
        # Cost1: [249,000, 10,000]
        # Cost2: [250,000]
        # We need to go through each of the sub-costs and de-dupe the global list 
        all_costs = []
        for concept_id, costs in cost_map.items():
            should_break = False
            for potential_conflict in all_costs:
                if math.isclose(subtotal, potential_conflict.cost, rel_tol=0.025):
                    cost_map[concept_id] = []
                    should_break = True
                    break

            if should_break:
                continue

            for cost in costs:
                should_append = True
                for potential_conflict in all_costs:
                    if potential_conflict.fact.decimals is None:
                        continue
                    decs = min(cost.fact.decimals, potential_conflict.fact.decimals)
                    if isclose(cost.cost, potential_conflict.cost, sf=decs, rel_tol=0.025):
                        costs.remove(cost)
                        should_append = False
                        break

                if should_append:
                    all_costs.append(cost)

        updated_cost_map = {}
        for k, costs in cost_map.items():
            subtotal = sum([c.cost for c in costs])
            if shorten:
                subtotal /= 1000000
                
            updated_cost_map[k] = subtotal

        return dedupe_map(updated_cost_map)

    def diff_month(self, d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month

    def filter_time_spans(self, costs):
        time_map = {}
        for cost in costs:
            ctx = cost.fact.context
            if not isinstance(ctx, TimeFrameContext):
                continue

            delta = self.diff_month(ctx.end_date, ctx.start_date)
            if delta not in time_map:
                time_map[delta] = []
            time_map[delta].append(cost)

        if time_map:
            return time_map[max(time_map, key=int)]
        else:
            return costs

    def process_precedence_tags(self, input_costs):
        if not self.precedent_tags:
            return input_costs

        has_pt = False
        for cost in input_costs:
            concept_id = cost.fact.concept.xml_id.lower()
            if concept_id in self.precedent_tags:
                has_pt = True

        if not has_pt:
            return input_costs

        costs = []
        for cost in input_costs:
            concept_id = cost.fact.concept.xml_id.lower()
            if concept_id in self.precedent_tags or cost.fact.protected or cost.custom:
                costs.append(cost)

        self.processed_precendent_tags= True

        return costs

    def output(self, verbose, text_facts=[], shorten=True):
        costs = self.organise_costs(verbose, text_facts=text_facts, shorten=shorten)

        log_outputs = [f"{self.name.upper()}"]

        total = 0
        for name, cost in costs.items():
            if cost == 0:
                continue
            log_outputs.append(f"- {name} {cost}")
            total += cost
        
        log_outputs.append(f"TOTAL {total}")

        return total, log_outputs

    def filter_dimension(self, costs):
        concepts = {}
        for cost in costs:
            concept_id = cost.fact.concept.xml_id 
            if concept_id not in concepts:
                concepts[concept_id] = []
            concepts[concept_id].append(cost)

        output = []
        for concept, costs in concepts.items():
            highest_dim_costs = self.filter_per_dimension(costs)
            output.extend(highest_dim_costs)
        return output

    def filter_per_dimension(self, costs):
        dimension_map = {}
        for cost in costs:
            num = len(cost.fact.context.segments)
            if num not in dimension_map:
                dimension_map[num] = []
            dimension_map[num].append(cost)

        if dimension_map:
            return dimension_map[min(dimension_map, key=int)]
        else:
            return costs

    def dedupe_prefixes(self, costs):
        concept_map = {}
        for cost in costs:
            concept_id = cost.fact.concept.xml_id
            if concept_id not in concept_map:
                concept_map[concept_id] = []
            concept_map[concept_id].append(cost)
        
        keys = concept_map.copy().keys()
        for concept_id in keys:
            for potential_conflict in [k for k in keys if k != concept_id]:
                if potential_conflict.startswith(concept_id):
                    for cost in concept_map[concept_id]:
                        costs.remove(cost)
                    break

        return costs