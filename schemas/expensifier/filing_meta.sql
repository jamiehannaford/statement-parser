CREATE TABLE `filing_meta` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `cik` varchar(20) NOT NULL,
  `filing_date` date DEFAULT NULL,
  `filing_type` varchar(10) NOT NULL,
  `accession_number` varchar(20) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `cik` (`cik`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;