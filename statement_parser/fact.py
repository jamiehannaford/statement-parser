from xbrl_parser.instance import NumericFact

class NumericFact(NumericFact):
    def __init__(self, fact):
        super().__init__(fact.id, fact.concept, fact.context, fact.value, fact.unit, fact.decimals)
        self.fact = fact
        self.protected = False