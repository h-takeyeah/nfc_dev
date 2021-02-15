USE accessdb;
CREATE EVENT IF NOT EXISTS e_reset
  ON SCHEDULE
    EVERY 1 DAY STARTS CONCAT(CURDATE(), ' ', '23:59:30')
  COMMENT 'Processing of people who forgot to leave the room.'
  DO
    UPDATE access_log SET exited_at=CONCAT(CURDATE(), ' ', '23:59:59')
      WHERE exited_at IS NULL
