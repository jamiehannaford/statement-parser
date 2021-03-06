CREATE TABLE `fundamentals` (
  `ticker` varchar(20) NOT NULL,
  `filing_date` date DEFAULT NULL,
  `reportedCurrency` varchar(20) NOT NULL,
  `fillingDate` date DEFAULT NULL,
  `acceptedDate` date DEFAULT NULL,
  `calendarYear` varchar(4) NOT NULL,
  `period` varchar(20) NOT NULL,
  `revenue` BIGINT NOT NULL,
  `costOfRevenue` BIGINT NOT NULL,
  `grossProfit` BIGINT NOT NULL,
  `grossProfitRatio` DECIMAL(10,10) DEFAULT NULL,
  `researchAndDevelopmentExpenses` BIGINT NOT NULL,
  `generalAndAdministrativeExpenses` DECIMAL(10,10) DEFAULT NULL,
  `sellingAndMarketingExpenses` DECIMAL(10,10) DEFAULT NULL,
  `sellingGeneralAndAdministrativeExpenses` BIGINT NOT NULL,
  `otherExpenses` DECIMAL(10,10) DEFAULT NULL,
  `operatingExpenses` BIGINT NOT NULL,
  `costAndExpenses` BIGINT NOT NULL,
  `interestIncome` BIGINT NOT NULL,
  `interestExpense` BIGINT NOT NULL,
  `depreciationAndAmortization` BIGINT NOT NULL,
  `ebitda` BIGINT NOT NULL,
  `ebitdaratio` DECIMAL(10,10) DEFAULT NULL,
  `operatingIncome` BIGINT NOT NULL,
  `operatingIncomeRatio` DECIMAL(10,10) DEFAULT NULL,
  `totalOtherIncomeExpensesNet` BIGINT NOT NULL,
  `incomeBeforeTax` BIGINT NOT NULL,
  `incomeBeforeTaxRatio` DECIMAL(10,10) DEFAULT NULL,
  `incomeTaxExpense` BIGINT NOT NULL,
  `netIncome` BIGINT NOT NULL,
  `netIncomeRatio` DECIMAL(10,10) DEFAULT NULL,
  `eps` DECIMAL(10,10) DEFAULT NULL,
  `epsdiluted` DECIMAL(10,10) DEFAULT NULL,
  `weightedAverageShsOut` BIGINT NOT NULL,
  `weightedAverageShsOutDil` BIGINT NOT NULL,
  PRIMARY KEY (`ticker`, `filing_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;