-- Metrics table
CREATE TABLE IF NOT EXISTS metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  timestamp INTEGER NOT NULL,
  metric_name TEXT NOT NULL,
  metric_value REAL NOT NULL,
  created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_metrics_source_timestamp 
  ON metrics(source, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
  ON metrics(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_metrics_name 
  ON metrics(metric_name);

CREATE INDEX IF NOT EXISTS idx_metrics_source_name_timestamp 
  ON metrics(source, metric_name, timestamp DESC);

-- Optional: Create a view for latest metrics
CREATE VIEW IF NOT EXISTS latest_metrics AS
SELECT 
  m1.source,
  m1.metric_name,
  m1.metric_value,
  m1.timestamp
FROM metrics m1
INNER JOIN (
  SELECT source, metric_name, MAX(timestamp) as max_timestamp
  FROM metrics
  WHERE timestamp > strftime('%s', 'now', '-1 hour')
  GROUP BY source, metric_name
) m2 ON m1.source = m2.source 
  AND m1.metric_name = m2.metric_name 
  AND m1.timestamp = m2.max_timestamp;
