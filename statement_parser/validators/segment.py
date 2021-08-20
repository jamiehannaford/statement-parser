from statement_parser.expenses.interest import InterestExpenseGroup

# This class allows for expenses to be handled differently across business segments.
# For example, interest expense should not be deducted from operating earnings for 
# segments whose primary business model or sector is financial services. For other 
# business segments, it can be deducted because it's orthogonal to the core earnings.
# Some examples: GE has a GE Capital, F has Ford Credit, etc.


# Step 1: Find tags which exist as a collection segment expenses that sum up to a 
#         consolidated expense.
# Step 2: If any of the business segments are found to be "operating" in nature, 
#         exclude that expense along with the consolidated total. 


# TODO Fix for CRON
class SegmentValidator:
    def __init__(self, instance, profile):
        self.instance = instance 
        self.profile = profile
        self.groups = [
            InterestExpenseGroup(self.instance, [], profile)
        ]
    
    def fact_matches(self, fact):
        for group in self.groups:
            if group.is_cost(fact, None):
                return True
        return False

    def dimension_is_business_segment(self, dim):
        approved_dimensions = ["StatementBusinessSegmentsAxis", "ProductOrServiceAxis"]
        return dim.name in approved_dimensions

    def contains_financial_term(self, fact):
        invalid_terms = ["credit", "capital"]

        matches = []
        for s in fact.context.segments:
            if not self.dimension_is_business_segment(s.dimension):
                continue
            if not any(t in s.member.name.lower() for t in invalid_terms) \
                and not s.member.name.lower().startswith("financial"):
                continue
            matches.append(s)

        return len(matches) > 0

    def is_business_segment_item(self, fact):
        matches = []
        for s in fact.context.segments:
            if self.dimension_is_business_segment(s.dimension):
                matches.append(s)

        return len(matches) > 0

    def is_consolidation_item(self, fact):
        matches = []
        for s in fact.context.segments:
            if s.dimension.name != "ConsolidationItemsAxis":
                continue 
            if self.dimension_is_business_segment(s.dimension):
                continue
            if s.member.name == "ReportableLegalEntitiesMember":
                continue 
            if "Eliminations" in s.member.name:
                continue
            matches.append(s)

        return len(matches) > 0

    def is_parent_item(self, fact):
        return len(fact.context.segments) == 0

    def is_operating_segment_item(self, fact):
        if self.contains_financial_term(fact):
            return True
        
        matches = [s for s in fact.context.segments if s.member.name == "OperatingSegmentsMember"]
        return len(matches) > 0

    def process(self, elements):
        matches = {}
        for elem in elements:
            if not self.fact_matches(elem):
                continue 
            
            concept_id = elem.concept.xml_id
            if concept_id not in matches:
                matches[concept_id] = []
            
            matches[concept_id].append(elem)

        for concept_id, concept_elems in matches.items():
            consolidation_items = []
            concept_elem = None
            parent_item = None
            for concept_elem in concept_elems:
                if self.is_consolidation_item(concept_elem) or self.is_business_segment_item(concept_elem):
                    consolidation_items.append(concept_elem)
                elif self.is_parent_item(concept_elem):
                    parent_item = concept_elem
            
            operating_segment_values = []
            for consolidation_item in consolidation_items:
                if self.is_operating_segment_item(consolidation_item):
                    operating_segment_values.append(consolidation_item.value)
            
            if len(operating_segment_values) > 0:
                removal_count = 1
                # Since consolidation items marked as "operating" should be left in 
                # core earnings, we remove them from the list of deductions
                for concept_elem in concept_elems:
                    should_remove = False
                    if concept_elem.value in operating_segment_values:
                        should_remove = True
                    if parent_item and concept_elem.value == parent_item.value:
                        should_remove = True
                    if not self.is_consolidation_item(concept_elem) and not self.is_business_segment_item(concept_elem):
                        should_remove = True
                    
                    if should_remove:
                        removal_count += 1
                        if removal_count < len(concept_elems):
                            elements.remove(concept_elem)

        return elements