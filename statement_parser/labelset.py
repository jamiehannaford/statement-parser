
class LabelSet:
    def __init__(self):
        self.labels = {} 
    
    def add(self, label):
        ltype = label.label_type.split("/")[-1]
        self.labels[ltype] = label

    def get(self, label_type):
        if label_type in self.labels:
            return self.labels[label_type].text
        return ""

    def any_contains(self, search):
        for label in self.labels.values():
            if not label.text:
                continue
            if search.lower() in label.text.lower():
                return True 
        return False