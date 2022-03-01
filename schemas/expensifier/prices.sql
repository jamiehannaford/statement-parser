CREATE TABLE `prices` (
  `ticker` varchar(20) NOT NULL,
  `date` date DEFAULT NULL,
  `price` DECIMAL(12,1) NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ticker`, `date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;