-- Jobs table for tracking PDF processing
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    slurm_id TEXT,
    status TEXT NOT NULL DEFAULT 'submitted',
    r2_key TEXT NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    results_url TEXT,
    user_id TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_jobs_slurm_id ON jobs(slurm_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_r2_key ON jobs(r2_key);
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);

-- Users table for authentication and tracking
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    organization TEXT,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Processing metrics for monitoring and analytics
CREATE TABLE IF NOT EXISTS processing_metrics (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    processing_time_seconds REAL,
    pdf_pages INTEGER,
    pdf_size_bytes INTEGER,
    success INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

CREATE INDEX IF NOT EXISTS idx_metrics_job_id ON processing_metrics(job_id);
CREATE INDEX IF NOT EXISTS idx_metrics_created_at ON processing_metrics(created_at);
