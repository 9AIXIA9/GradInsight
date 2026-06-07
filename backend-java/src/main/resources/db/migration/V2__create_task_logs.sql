-- Flyway migration: create task_logs table
CREATE TABLE IF NOT EXISTS task_logs (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  task_id VARCHAR(64),
  status INT,
  message TEXT,
  created_at DATETIME
);

