from bs4 import BeautifulSoup
import html

class TextAnalyser:
    def __init__(self, text_fact, label, number_fact):
        self.text_fact = text_fact
        self.number_fact = number_fact
        self.label = label
        self.soup = BeautifulSoup(html.unescape(self.text_fact.value), "lxml")

    def format_number(self):
        divisor = 1000000
        if "in thousands" in self.text_fact.value:
            divisor = 1000

        divided = abs(self.number_fact.value) / divisor
        return "{:,.0f}".format(divided)

    def has_positive(self):
        number = self.format_number()

        for row in self.soup.find_all("tr"):
            cells = row.find_all("td")
            
            label_match = False
            value_match = False

            for cell in cells:
                if self.label in cell.text.lower():
                    label_match = True 
                elif number in cell.text:
                    if "(" in cell.text or ")" in cell.text:
                        value_match = False
                        continue
                    value_match = True
            
            # print(label_match, number, value_match)
            if label_match and value_match:
                return value_match

    def has_negative(self):
        number = self.format_number()

        for row in self.soup.find_all("tr"):
            cells = row.find_all("td")
            
            label_match = False
            value_match = False

            for cell in cells:
                if self.label.lower() in cell.text.lower():
                    label_match = True 
                elif number in cell.text:
                    if "(" not in cell.text and ")" not in cell.text:
                        continue
                    value_match = True
            
            # print(number, label_match, value_match)
            if label_match and value_match:
                return value_match