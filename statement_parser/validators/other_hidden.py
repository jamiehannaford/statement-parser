

# Sometimes items are bundled into "Other income" but only disclosed in the footnotes. 
# This validator checks for basic textual references and removes line items if necessary.
class OtherHiddenValidator:
    def __init__(self, instance, file_parser, labels):
        self.instance = instance
        self.file_parser = file_parser
        self.labels = labels
        
    def process(self, elements):
        if not self.file_parser:
            return elements

        return self.file_parser.filter_hidden_refs(self.instance, elements, self.labels)