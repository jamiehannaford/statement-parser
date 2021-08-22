import unittest 
import datetime

from statement_parser.parsers.xml import XMLParser

from xbrl.instance import TimeFrameContext, ExplicitMember
from xbrl.taxonomy import Concept

class TestXMLParser(unittest.TestCase): 
    def test_invalid_path(self):
        with self.assertRaises(FileNotFoundError) as context:
            XMLParser("foo")
        
        self.assertTrue("No such file or directory" in str(context.exception))

    def test_invalid_compare_file(self):
        with self.assertRaises(ValueError) as context:
            XMLParser("data/AAPL/20200926/aapl-20200926_htm.xml", compare_file="foo")
        
        self.assertTrue("foo does not exist" in str(context.exception))

    def generate_ctx(self, year):
        start = datetime.date(year, 1, 1)
        end = datetime.date(year, 8, 31)
        return TimeFrameContext("", "", start, end)

    def test_valid_range(self):
        p = XMLParser("data/AAPL/20200926/aapl-20200926_htm.xml")
        
        self.assertFalse(p.valid_range(self.generate_ctx(2016)))
        self.assertTrue(p.valid_range(self.generate_ctx(2020)))

    def test_is_a_forecast(self):
        p = XMLParser("data/AAPL/20200926/aapl-20200926_htm.xml")
        
        ctx1 = self.generate_ctx(2020)
        ctx1.segments.append(ExplicitMember(Concept("", "", "StatementScenarioAxis"), Concept("", "", "RandomForecastFoo")))
        self.assertTrue(p.is_a_forecast(ctx1))

        ctx2 = self.generate_ctx(2020)
        ctx2.segments.append(ExplicitMember(Concept("", "", "foo"), Concept("", "", "bar")))
        self.assertFalse(p.is_a_forecast(ctx2))
