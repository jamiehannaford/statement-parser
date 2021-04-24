import statement_parser.expenses.discontinued_ops import DiscontinuedOpsExpenseCategory
import statement_parser.expenses.restructuring import RestructuringExpenseGroup
import statement_parser.expenses.write_downs import WriteDownExpenseGroup

CATEGORY_RESTRUCTURING    = "restructuring"
CATEGORY_DEPREC_AMORTORT  = "deprec_amort"
CATEGORY_DISCONTINUED_OPS = "discontinued_ops"
CATEGORY_WRITE_DOWNS      = "write_downs"

class Expenses:
    def __init__(self, pre_linkbases):
        self.pre_linkbases = pre_linkbases
        self.categories = {
            CATEGORY_RESTRUCTURING: RestructuringExpenseGroup(),
            CATEGORY_DEPREC_AMORTORT: DepreciationAmortizationExpenseGroup(),
            CATEGORY_DISCONTINUED_OPS: DiscontinuedOpsExpenseCategory(),
            CATEGORY_WRITE_DOWNS: WriteDownExpenseGroup(),
        }

    def process_fact(self, fact):
        for category in self.categories:
            if category.is_cost(fact)
                category.add(fact)

    def output_all(self):
        for category in self.categories:
            category.output()