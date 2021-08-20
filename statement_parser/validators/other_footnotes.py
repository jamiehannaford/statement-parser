from bs4 import BeautifulSoup
import html
import re

class OtherFootnotesValidator:
    def __init__(self, instance, file_parser):
        self.instance = instance
        self.file_parser = file_parser
        self.text_block_labels = ["us-gaap_OtherIncomeAndOtherExpenseDisclosureTextBlock"]

    def get_hidden_facts(self, fact_id):
        facts = []

        if self.file_parser is None:
            return facts

        footnotes = self.file_parser.retrieve_footnotes(fact_id)
        if len(footnotes) == 0:
            return facts

        for footnote in footnotes:
            cross_elems = footnote.child_tags()
            facts.extend(cross_elems) 

        return facts

    def process(self, elements):
        # id_map = {}
        concept_map = {}
        for elem in elements:
            # id_map[elem.id] = elem
            concept_id = elem.concept.xml_id
            if concept_id not in concept_map:
                concept_map[concept_id] = []
            concept_map[concept_id].append(elem)

        removed = []
        for elem in elements:
            facts = self.get_hidden_facts(elem)
            if len(facts) == 0:
                continue
            
            for fact in facts: 
                stripped = fact.name.replace(":", "_")
                if stripped not in concept_map:
                    continue 
                
                potential_matches = concept_map[stripped]

                has_ctx_match = False 
                for potential_match in potential_matches:
                    if fact.context_ref == potential_match.context.xml_id:
                        has_ctx_match = True 
                        break

                # if fact.id in id_map or has_ctx_match:
                if has_ctx_match:
                    removed.append(fact)

        for removal in removed:
            stripped = removal.name.replace(":", "_")
            for elem in elements:
                if elem.context.xml_id == removal.context_ref and elem.concept.xml_id == stripped:
                    elements.remove(elem)
        
        return elements
