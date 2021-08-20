class DimensionValidator:
    def __init__(self, instance):
        self.instance = instance

    def process(self, elements):
        concept_map = {}
        for elem in elements:
            concept_id = elem.concept.xml_id 
            if concept_id not in concept_map:
                concept_map[concept_id] = []
            concept_map[concept_id].append(elem)

        output = []
        for concept, costs in concept_map.items():
            highest_dim_costs = self.filter_per_dimension(costs)
            output.extend(highest_dim_costs)
        return output

    def filter_per_dimension(self, costs):
        dimension_map = {}
        for cost in costs:
            num = len(cost.context.segments)
            if num not in dimension_map:
                dimension_map[num] = []
            dimension_map[num].append(cost)

        if dimension_map:
            key = min(dimension_map, key=int)
            return dimension_map[key]
        else:
            return costs