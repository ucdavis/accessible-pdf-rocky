# Monitoring Setup Guide

This document describes the Prometheus observability stack for the accessible PDF system.

## Overview

We monitor three layers:

1. **FastAPI Controller** — Job submission, R2 URLs, queue depth
2. **HPC SLURM** — Job states, node availability, queue backlog
3. **Infrastructure** — System resources via Node Exporter

## Architecture

```mermaid
flowchart TD
    Prometheus["Prometheus + Grafana<br/>Scrapes every 15-60s"] -->|/metrics| FastAPI
    Prometheus -->|/metrics| HPC
    Prometheus -->|:9100| NodeExporter
    
    FastAPI["FastAPI Controller<br/>/metrics endpoint<br/>• Job submission stats<br/>• Queue depth<br/>• R2 URL generation"]
    
    HPC["HPC SLURM<br/>/metrics via Node Exporter<br/>• Job states<br/>• Queue backlog<br/>• Node availability"]
    
    NodeExporter["Node Exporter<br/>:9100<br/>• System resources<br/>• CPU/Memory/Disk<br/>• Network stats"]
    
    style Prometheus fill:#ffeb99,stroke:#cc9900,stroke-width:3px,color:#000
    style FastAPI fill:#90ee90,stroke:#228b22,stroke-width:3px,color:#000
    style HPC fill:#ff9999,stroke:#cc0000,stroke-width:3px,color:#000
    style NodeExporter fill:#e6ccff,stroke:#9933ff,stroke-width:3px,color:#000
```

## FastAPI Controller Metrics

### FastAPI Setup

```bash
# Install Prometheus client
cd controller
uv add prometheus-client
```

The `/metrics` endpoint is already configured in `controller/main.py`.

### Available Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `slurm_submitted_jobs_total` | Counter | Total jobs submitted (labels: status) |
| `slurm_submission_failures_total` | Counter | Failed submissions (labels: error_type) |
| `slurm_submission_latency_seconds` | Histogram | Time to submit job |
| `slurm_pending_jobs` | Gauge | Jobs in PENDING state |
| `slurm_running_jobs` | Gauge | Jobs in RUNNING state |
| `slurm_completed_jobs` | Gauge | Jobs in COMPLETED state |
| `slurm_failed_jobs` | Gauge | Jobs in FAILED state |
| `slurm_job_duration_seconds` | Histogram | Time from submit to complete |
| `slurm_status_check_seconds` | Histogram | Time to query job status |
| `r2_presigned_url_generation_seconds` | Histogram | Time to generate URLs |
| `cloudflare_queue_depth` | Gauge | Messages in Cloudflare Queue |

### Test Endpoint

```bash
curl http://localhost:8000/metrics
```

Expected output:

```
# HELP slurm_submitted_jobs_total Total number of jobs submitted to Slurm
# TYPE slurm_submitted_jobs_total counter
slurm_submitted_jobs_total{status="success"} 42.0
...
```

## HPC SLURM Metrics

### Installation (on HPC login node)

```bash
# 1. Install Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
tar xvfz node_exporter-*.tar.gz
sudo cp node_exporter-*/node_exporter /usr/local/bin/
sudo chown root:root /usr/local/bin/node_exporter

# 2. Create textfile collector directory
sudo mkdir -p /var/lib/node_exporter/textfile_collector
sudo chown nobody:nobody /var/lib/node_exporter/textfile_collector

# 3. Install SLURM metrics export script
sudo cp controller/hpc/scripts/export_slurm_metrics.sh /usr/local/bin/
sudo chmod 755 /usr/local/bin/export_slurm_metrics.sh
sudo chown root:root /usr/local/bin/export_slurm_metrics.sh

# 4. Add to cron (run every minute)
sudo crontab -e
# Add line:
* * * * * /usr/local/bin/export_slurm_metrics.sh

# 5. Create systemd service for Node Exporter
sudo tee /etc/systemd/system/node_exporter.service <<EOF
[Unit]
Description=Prometheus Node Exporter
After=network.target

[Service]
Type=simple
User=nobody
ExecStart=/usr/local/bin/node_exporter \\
  --collector.textfile.directory=/var/lib/node_exporter/textfile_collector
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 6. Start Node Exporter
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

### Available SLURM Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `slurm_pending_jobs` | Gauge | Jobs waiting in queue |
| `slurm_running_jobs` | Gauge | Jobs currently running |
| `slurm_completed_jobs_1h` | Gauge | Completed in last hour |
| `slurm_failed_jobs_1h` | Gauge | Failed in last hour |
| `slurm_gpu_pending_jobs` | Gauge | GPU jobs waiting |
| `slurm_gpu_running_jobs` | Gauge | GPU jobs running |
| `slurm_nodes_idle` | Gauge | Idle compute nodes |
| `slurm_nodes_allocated` | Gauge | Allocated compute nodes |
| `slurm_nodes_down` | Gauge | Down/offline nodes |

### Test Metrics

```bash
# Check metrics file
cat /var/lib/node_exporter/textfile_collector/slurm_metrics.prom

# Test Node Exporter endpoint
curl http://hpc-login:9100/metrics | grep slurm_
```

## Prometheus Configuration

### Prometheus Setup

```bash
# On monitoring server
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
sudo cp prometheus-*/prometheus /usr/local/bin/
sudo cp prometheus-*/promtool /usr/local/bin/
```

### prometheus.yml

```yaml
global:
  scrape_interval: 30s
  evaluation_interval: 30s

scrape_configs:
  # FastAPI Controller
  - job_name: 'fastapi'
    static_configs:
      - targets: ['fastapi.internal:8000']
    metrics_path: '/metrics'

  # HPC SLURM (via Node Exporter)
  - job_name: 'hpc-slurm'
    static_configs:
      - targets: ['hpc-login.ucdavis.edu:9100']

  # Additional node exporters (optional)
  - job_name: 'node'
    static_configs:
      - targets: ['fastapi.internal:9100']
```

### Start Prometheus

```bash
# Test configuration
promtool check config prometheus.yml

# Run Prometheus
prometheus --config.file=prometheus.yml --storage.tsdb.path=./data
```

Access Prometheus UI: `http://localhost:9090`

## Alerting Rules

Create `alerts.yml`:

```yaml
groups:
  - name: slurm_alerts
    interval: 1m
    rules:
      # High failure rate
      - alert: HighJobFailureRate
        expr: rate(slurm_submission_failures_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High SLURM job failure rate"
          description: "More than 10% of jobs failing in last 5 minutes"

      # Long queue backlog
      - alert: LongQueueBacklog
        expr: slurm_pending_jobs > 100
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Large number of pending jobs"
          description: "{{ $value }} jobs pending for >10 minutes"

      # All nodes down
      - alert: AllNodesDown
        expr: slurm_nodes_idle + slurm_nodes_allocated == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "No SLURM nodes available"
          description: "All compute nodes are down"

      # Slow job submission
      - alert: SlowJobSubmission
        expr: histogram_quantile(0.95, rate(slurm_submission_latency_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow job submission latency"
          description: "95th percentile submission time >5s"

      # FastAPI down
      - alert: FastAPIDown
        expr: up{job="fastapi"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "FastAPI controller is down"
          description: "FastAPI /metrics endpoint unreachable"
```

Load alerts:

```bash
prometheus --config.file=prometheus.yml \
  --storage.tsdb.path=./data \
  --web.enable-lifecycle
```

## Grafana Dashboards

### Grafana Setup

```bash
# Install Grafana
wget https://dl.grafana.com/oss/release/grafana-10.2.2.linux-amd64.tar.gz
tar -zxvf grafana-10.2.2.linux-amd64.tar.gz
cd grafana-10.2.2
./bin/grafana-server
```

Access Grafana: `http://localhost:3000` (admin/admin)

### Add Prometheus Data Source

1. Settings → Data Sources → Add data source
2. Select "Prometheus"
3. URL: `http://localhost:9090`
4. Save & Test

### Dashboard Panels

#### Panel 1: Job Submission Rate

```promql
rate(slurm_submitted_jobs_total[5m])
```

#### Panel 2: Job States

```promql
slurm_pending_jobs
slurm_running_jobs
slurm_completed_jobs
slurm_failed_jobs
```

#### Panel 3: Submission Latency (95th percentile)

```promql
histogram_quantile(0.95, rate(slurm_submission_latency_seconds_bucket[5m]))
```

#### Panel 4: Node Availability

```promql
slurm_nodes_idle
slurm_nodes_allocated
slurm_nodes_down
```

#### Panel 5: Failure Rate

```promql
rate(slurm_submission_failures_total[5m])
```

### Import Dashboard JSON

A complete dashboard JSON is available in `docs/grafana-dashboard.json`.

## Query Examples

### Jobs submitted in last hour

```promql
increase(slurm_submitted_jobs_total[1h])
```

### Average job duration

```promql
rate(slurm_job_duration_seconds_sum[1h]) / rate(slurm_job_duration_seconds_count[1h])
```

### Success rate

```promql
rate(slurm_submitted_jobs_total{status="success"}[5m]) / rate(slurm_submitted_jobs_total[5m])
```

### GPU utilization

```promql
slurm_gpu_running_jobs / (slurm_gpu_running_jobs + slurm_gpu_pending_jobs)
```

## Maintenance

### Log Rotation

Prometheus data grows over time. Set retention:

```bash
prometheus --storage.tsdb.retention.time=30d
```

### Backup Metrics

```bash
# Backup Prometheus data
tar czf prometheus-backup-$(date +%Y%m%d).tar.gz ./data
```

### Testing

```bash
# Check if metrics are being collected
curl -s http://localhost:9090/api/v1/query?query=up

# Test alert evaluation
promtool check rules alerts.yml
```

## Troubleshooting

### No metrics from FastAPI

```bash
# Check if /metrics endpoint works
curl http://fastapi.internal:8000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets'
```

### No SLURM metrics

```bash
# Check if script is running
sudo crontab -l | grep export_slurm_metrics

# Check if metrics file exists
ls -la /var/lib/node_exporter/textfile_collector/

# Test script manually
sudo /usr/local/bin/export_slurm_metrics.sh
```

### High cardinality warnings

If too many unique label combinations:

```promql
# Check series count
count({__name__=~".+"})

# Identify high-cardinality metrics
topk(10, count by (__name__)({__name__=~".+"}))
```

## Security

### Network Security

- Prometheus should not be exposed to the internet
- Use internal network or VPN
- Consider BasicAuth or OAuth proxy if needed

### Access Control

```yaml
# prometheus.yml
basic_auth:
  username: prometheus
  password: <bcrypt-hash>
```

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Node Exporter](https://github.com/prometheus/node_exporter)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
