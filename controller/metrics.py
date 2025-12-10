"""Push-based metrics for Slurm job orchestration.

Metrics are pushed to Cloudflare Worker (D1 database) instead of
exposing a Prometheus endpoint. This eliminates the need for inbound
connections to the FastAPI controller.
"""

import os
from datetime import datetime
from typing import Optional

import httpx


class MetricsClient:
    """Client for pushing metrics to Cloudflare Worker."""

    def __init__(self):
        self.endpoint = os.getenv(
            "METRICS_ENDPOINT", "https://metrics.your-domain.workers.dev/ingest"
        )
        self.token = os.getenv("METRICS_TOKEN", "")
        self.source = "fastapi"
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=5.0)
        return self._client

    async def push(self, metrics: dict[str, float]) -> None:
        """Push metrics to Cloudflare Worker.

        Args:
            metrics: Dictionary of metric names to values

        Note:
            Failures are logged but do not raise exceptions to avoid
            impacting application functionality.
        """
        if not self.token:
            # Silently skip if not configured
            return

        payload = {
            "source": self.source,
            "timestamp": int(datetime.now().timestamp()),
            "metrics": metrics,
        }

        try:
            client = await self._get_client()
            response = await client.post(
                self.endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {self.token}"},
            )
            response.raise_for_status()
        except Exception as e:
            # Don't fail the request if metrics push fails
            print(f"Failed to push metrics: {e}")

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# Global metrics client instance
_metrics_client = MetricsClient()


async def push_metrics(metrics: dict[str, float]) -> None:
    """Push metrics to Cloudflare Worker.

    Args:
        metrics: Dictionary of metric names to values

    Example:
        await push_metrics({
            "slurm_submitted_jobs_total": 1,
            "slurm_submission_latency_seconds": 0.523,
        })
    """
    await _metrics_client.push(metrics)


async def close_metrics_client() -> None:
    """Close metrics client (call on application shutdown)."""
    await _metrics_client.close()


# Convenience functions for common metrics


async def record_job_submission(success: bool, latency: float) -> None:
    """Record job submission attempt."""
    await push_metrics(
        {
            "slurm_submitted_jobs_total": 1,
            "slurm_submission_latency_seconds": latency,
            "slurm_submission_success" if success else "slurm_submission_failure": 1,
        }
    )


async def record_job_failure(error_type: str) -> None:
    """Record job submission failure."""
    await push_metrics(
        {
            f"slurm_submission_failure_{error_type}": 1,
        }
    )


async def record_job_duration(duration: float) -> None:
    """Record job processing duration."""
    await push_metrics({"slurm_job_duration_seconds": duration})


async def record_status_check(latency: float) -> None:
    """Record status check latency."""
    await push_metrics({"slurm_status_check_seconds": latency})


async def record_presigned_url_generation(latency: float) -> None:
    """Record presigned URL generation latency."""
    await push_metrics({"r2_presigned_url_generation_seconds": latency})
