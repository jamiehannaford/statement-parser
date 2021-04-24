from statement_parser.sanitize import Sanitizer

class ExpenseGroup:
    def __init__(self, name, tags, pre_linkbases):
        self.costs = []
        self.tags = []
        self.pre_linkbases = pre_linkbases

    def is_cost(self, fact):
        return fact.concept.name.lower() in self.tags

    def add(self, fact):
        rc = self.generate_cost(fact)

        if rc in self.costs or rc.cost == 0:
            return

        self.costs.append(rc)

    # For a given collection of tags with the same concept/tag name:
    # - Iterate over their contexts
    # - Group by dimension and find subtotals
    # - Remove any duplicative subtotals
    # - Add this deduped value to the total costs 
    def organise_costs(self):
        # first group costs by their tag name
        named_map = {}
        id_map = {}

        for cost in self.costs:

            # print(cost.fact)
            cost.validate()
            if cost.cost == 0:
                continue
            
            name = cost.fact.concept.name
            concept_id = cost.fact.concept.xml_id 
            
            if name not in named_map:
                named_map[name] = []
            if concept_id not in id_map:
                id_map[concept_id] = []

            id_map[concept_id].append(cost)
            named_map[name].append(cost)

        # now start grouping costs by their dimension and adding to the main dict
        total_costs = {}
        global_dimensions = {}
        for concept_name, costs in named_map.items():
            # first we group by dimension. very often different line items that make 
            # up the same overall cost are included separately, so we need to de-duplicate
            dimensions = {}
            for cost in costs:
                concept_id = cost.fact.concept.xml_id
                # print(cost.fact, cost.fact.context.xml_id)
                # if a cost doesn't have dimensions just add its concept name
                if len(cost.fact.context.segments) == 0:
                    total_costs[concept_id] = cost.get_cost()
                    continue
                
                # sum through all the different dimensions to get the subtotal
                for segment in cost.fact.context.segments:
                    dimension_name = segment.dimension.name
                    # print(dimension_name)
                    if dimension_name not in dimensions:
                        dimensions[dimension_name] = []
                    if dimension_name not in global_dimensions:
                        global_dimensions[dimension_name] = []
                    dimensions[dimension_name].append(cost.get_cost())
                
            # once we have the dimension subtotals, remove duplicate values
            
            dimension_costs = []
            subtotals = []

            for dimension, cost_list in dimensions.items():
                if sum(cost_list) in subtotals:
                    continue 
                subtotals.append(sum(cost_list))
                for cost in cost_list:
                    if cost not in dimension_costs and cost not in global_dimensions[dimension]:
                        dimension_costs.append(cost)
                        global_dimensions[dimension].append(cost)

            if concept_id not in total_costs:
                total_costs[concept_id] = sum(dimension_costs)
        
        s = Sanitizer(self.pre_linkbases, total_costs)
        return s.sanitize()

    def output(self):
        costs = self.organise_costs()

        total = 0
        for name, cost in costs.items():
            if cost == 0:
                continue
            print(f"- {name} {cost}")
            total += cost
        
        print(f"TOTAL {total}")
        return total