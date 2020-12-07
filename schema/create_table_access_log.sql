USE accessdb;
CREATE TABLE IF NOT EXISTS `access_log` (
  `member_id` int unsigned NOT NULL,
  `entered_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `exited_at` datetime DEFAULT NULL,
  PRIMARY KEY (`member_id`, `entered_at`)
);
