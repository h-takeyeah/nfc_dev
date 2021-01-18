USE accessdb;
CREATE TABLE IF NOT EXISTS `access_log` (
  `student_id` int unsigned NOT NULL,
  `entered_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `exited_at` datetime DEFAULT NULL,
  PRIMARY KEY (`student_id`, `entered_at`)
);
