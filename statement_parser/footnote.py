class Footnote:
    def __init__(self, tag):
        self.id = tag.get("id")
        self.tag = tag

    def child_tags(self):
        facts = []
        for elem in self.tag.find_all("ix:nonfraction"):
            facts.append(FootnoteFact(elem))
        return facts


class FootnoteFact:
    def __init__(self, tag):
        self.context_ref = tag.get("contextref")
        self.decimals = tag.get("decimals")
        self.id = tag.get("id")
        self.name = tag.get("name")
        self.value = tag.text
