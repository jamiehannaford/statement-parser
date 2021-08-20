from bs4 import BeautifulSoup

from statement_parser.footnote import Footnote
from statement_parser.expenses.company_other import CompanyDefinedOtherGroup

class HTMParser:
    def __init__(self, htm_path, xml_path):
        self.profile = None

        content = open(htm_path, "r")
        self.htm_soup = BeautifulSoup(content, "lxml")

        xml_content = open(xml_path, "r")
        self.xml_soup = BeautifulSoup(xml_content, "xml")

    def retrieve_footnotes(self, fact_id):
        to_ids = []
        for loc in self.xml_soup.find_all("link:footnoteArc"):
            if fact_id == loc.get("xlink:from"):
                to_ids.append(loc.get("xlink:to"))

        footnotes = []
        for tag in self.htm_soup.find_all("ix:footnote"):
            if tag.get("id") not in to_ids:
                continue

            footnotes.append(Footnote(tag))
            
        return footnotes

    def find_parent_with_elems(self, tag):
        if len(tag.parent.findAll()) > 1:
            return tag
        
        return self.find_parent_with_elems(tag.parent)

    def filter_hidden_refs(self, instance, elements, labels):
        cdo_costs = []
        cdo_validator = CompanyDefinedOtherGroup(instance, [], self.profile)
        
        elem_names = {}
        for elem in elements:
            label = labels[elem.concept.xml_id]
            if cdo_validator.is_cost(elem, label):
                cdo_costs.append(elem)
            elem_names[elem.concept.xml_id] = True

        removals = []
        for nf in self.htm_soup.find_all("ix:nonfraction"):
            name = nf.get("name").replace(":", "_")
            if name not in elem_names:
                continue 
            
            following_text = nf.next_sibling
            if following_text is None:
                continue

            for cdo_cost in cdo_costs:
                ls = labels[cdo_cost.fact.concept.xml_id]
                phrase = "included in " + ls.get("terseLabel")
                if phrase in following_text:
                    removals.append(name)

        output = []
        for e in elements:
            if e.concept.xml_id in removals and not e.protected:
                continue 
            output.append(e)
        return output