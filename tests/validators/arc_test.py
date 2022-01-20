import unittest 
import datetime

from xbrl.cache import HttpCache
from xbrl.instance import NumericFact, TimeFrameContext, AbstractUnit, parse_xbrl
from xbrl.taxonomy import Concept

from statement_parser.validators.arcs import ArcValidator

class TestArcValidator(unittest.TestCase):
    def fact(self, xml_id, costs):
        concept = Concept(xml_id, "", "")
        context = TimeFrameContext("", "", "", "")
        unit = AbstractUnit("")
        return NumericFact(concept, context, costs, unit, 1)

    def test_tag_is_non_standard(self):
        a = ArcValidator(None, [], [])
        self.assertFalse(a.tag_is_non_standard("us-gaap_Depreciation"))
        self.assertFalse(a.tag_is_non_standard("us-gaap_Depreciation"))
        self.assertTrue(a.tag_is_non_standard("googl_Depreciation"))
        self.assertTrue(a.tag_is_non_standard("vz_Depreciation"))

    def test_mark_protected(self):
        a = ArcValidator(None, [], [])
        a.elements = [self.fact("foo", 10)]
        a.mark_protected("foo")
        self.assertTrue(a.elements[0].protected)

    def test_process(self):
        cache = HttpCache("cache")
        instance = parse_xbrl("tests/data/example.xml", cache)
        
        cost1 = self.fact("BusinessExistCosts1", 30000000)
        cost2 = self.fact("SeveranceCosts1", 70000000)
        cost3 = self.fact("RestructuringCosts", 100000000)

        expected = [cost3]
        input_costs = [cost1, cost2, cost3]
        a = ArcValidator(instance, [], [])
        actual = a.process(input_costs)

        print(actual)

        self.assertEquals(expected, actual)

if __name__ == '__main__':
    unittest.main()
