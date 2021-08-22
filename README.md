# SEC statement parser

This tool allows you to extract all of the non-operating, hidden and non-recurrings costs in a 10-K filing to get a picture of company's true [Core Earnings]([Core Earnings](https://www.investopedia.com/terms/c/coreearnings.asp). 

Very often companies will hide these expenses into operating line items and footnotes, which ends up distorting key metrics like net income. This tool searches through all areas of a 10-K filing, including the footnotes, and removes these costs. To do this, the program will download the filing directly from the SEC, parse its XBRL instance and schema files, and then output a categorised list of expenses that should be excluded from Core Earnings.

## Why?

There are two main reasons why Core Earnings are important.

- *Value investing*. Core Earnings allow investors to ascertain the profitability of the underlying business, which is one of the key factors when deciding to invest in a given security.

- *Trading strategy*. According to [researchers from Harvard Business School](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3467814), trading strategies that exploit non-core earnings produce **abnormal returns of 8% per year**.

## Installation

You must first generate a free API key with [financialmodelingprep.com](https://financialmodelingprep.com/developer/docs) and then run:

```bash
$ export FMP_API_KEY="$KEY"
$ git clone https://github.com/jamiehannaford/statement-parser
$ cd statement-parser
```

## Viewing expenses

To see a table-formatted list of expenses:

```bash
$ python ./parse.py -t TSLA -y 2020
```

As you can see, including depreciation and amortization, Tesla has around $3.7 billion in hidden expenses for 2020.

You can also generate JSON:

```bash
$ python ./parse.py -t GOOGL -y 2020 --json
```
```json
{
   "expensesRestructuring":0,
   "expensesDepreciationAndAmortization":774000000.0,
   "expensesDiscontinuedOperations":0,
   "expensesWriteDown":0,
   "expensesNonRecurringOther":0,
   "expensesInterest":-1730000000.0,
   "expensesInterestMinority":0,
   "expensesLegalRegulatoryInsurance":0,
   "expensesNonOperatingCompanyDefinedOther":1038000000.0,
   "expensesAcquisitionMerger":0,
   "expensesDerivative":-144000000.0,
   "expensesForeignCurrency":344000000.0,
   "expensesNonOperatingOther":-5708000000.0,
   "expensesNonOperatingSubsidiaryUnconsolidated":0,
   "expensesOtherFinancing":0
}
```

## Download filing and XBRL data

To download the last 10 filings of a company:

```bash
python ./download.py -t MSFT --last 10
```

You can also specify a date range with `--from` and `--to`. 

## Opening a filing on the SEC's website

To open a filing and view with iXBRL:

```bash
python ./open.py -t GOOGL -y 2020
```

Note: The year is when the statement was filed, not necessarily the filing period.

## Testing the data

This tool's output was tested against [IEX Cloud's Fundamentals data](https://iexcloud.io/docs/api/#fundamentals), which includes expenses that appear in the IS, BS or CF sections of a 10-K. Because this API does not include expenses hidden in footnotes and annotations, it will diverge at times from this tool's output. Where possible I've tried to manually verify the results, but could use a second pair of eyes if anybody would like to help verify.

## To dos

- Support 10-Q filings
- Add test suite (both unit and integration tests) and hook up CI
- Add more documentation
- Refactor codebase (DRY up and improve performance)
