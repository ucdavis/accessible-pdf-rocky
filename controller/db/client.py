"""HTTP client for D1 database API."""

import os
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

# Configuration
DB_API_URL = os.getenv("DB_API_URL", "http://localhost:8787")
DB_API_TOKEN = os.getenv("DB_API_TOKEN", "")

# Fail fast if token is missing in production
if not DB_API_TOKEN and os.getenv("ENVIRONMENT", "development") == "production":
    raise ValueError(
        "DB_API_TOKEN must be set in production. "
        "Set the DB_API_TOKEN environment variable."
    )

# Timeout configuration
TIMEOUT = httpx.Timeout(30.0, connect=5.0)


class DatabaseClient:
    """HTTP client for database operations via D1 API worker."""

    def __init__(self, base_url: str = DB_API_URL, token: str = DB_API_TOKEN):
        """Initialize database client.

        Args:
            base_url: Base URL of the D1 API worker
            token: Bearer token for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for connection pooling.

        Returns:
            Async HTTP client
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=TIMEOUT, headers=self.headers)
        return self._client

    async def close(self) -> None:
        """Close the HTTP client and clean up connections."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, str]] = None,
    ) -> Union[dict[str, Any], list[dict[str, Any]]]:
        """Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path
            json: JSON body for POST/PUT requests
            params: Query parameters

        Returns:
            Response JSON (dict or list)

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        client = await self._get_client()
        url = f"{self.base_url}{path}"
        response = await client.request(method, url, json=json, params=params)
        response.raise_for_status()

        if response.status_code == 204:  # No content
            return {}

        return response.json()

    # Job operations
    async def create_job(
        self,
        job_id: UUID,
        r2_key: str,
        status: str = "submitted",
        slurm_id: Optional[str] = None,
        user_id: Optional[UUID] = None,
    ) -> dict[str, Any]:
        """Create a new job.

        Args:
            job_id: Unique job identifier
            r2_key: R2 storage key for the PDF
            status: Job status (default: submitted)
            slurm_id: SLURM job ID (optional)
            user_id: User ID (optional)

        Returns:
            Created job data
        """
        data = {
            "id": str(job_id),
            "r2_key": r2_key,
            "status": status,
        }
        if slurm_id:
            data["slurm_id"] = slurm_id
        if user_id:
            data["user_id"] = str(user_id)

        result = await self._request("POST", "/jobs", json=data)
        return cast(dict[str, Any], result)

    async def get_job(self, job_id: UUID) -> dict[str, Any]:
        """Get job by ID.

        Args:
            job_id: Job identifier

        Returns:
            Job data

        Raises:
            httpx.HTTPStatusError: If job not found (404)
        """
        result = await self._request("GET", f"/jobs/{job_id}")
        return cast(dict[str, Any], result)

    async def list_jobs(
        self,
        status: Optional[str] = None,
        user_id: Optional[UUID] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """List jobs with optional filters.

        Args:
            status: Filter by status
            user_id: Filter by user ID
            limit: Maximum number of jobs to return

        Returns:
            List of job data
        """
        params = {"limit": str(limit)}
        if status:
            params["status"] = status
        if user_id:
            params["user_id"] = str(user_id)

        result = await self._request("GET", "/jobs", params=params)
        # API returns a list for this endpoint
        return result if isinstance(result, list) else []

    async def update_job(
        self,
        job_id: UUID,
        status: Optional[str] = None,
        slurm_id: Optional[str] = None,
        results_url: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update job fields.

        Args:
            job_id: Job identifier
            status: New status (optional)
            slurm_id: SLURM job ID (optional)
            results_url: URL to results (optional)

        Returns:
            Updated job data
        """
        data = {}
        if status is not None:
            data["status"] = status
        if slurm_id is not None:
            data["slurm_id"] = slurm_id
        if results_url is not None:
            data["results_url"] = results_url

        result = await self._request("PUT", f"/jobs/{job_id}", json=data)
        return cast(dict[str, Any], result)

    async def delete_job(self, job_id: UUID) -> None:
        """Delete a job.

        Args:
            job_id: Job identifier
        """
        await self._request("DELETE", f"/jobs/{job_id}")

    # User operations
    async def create_user(
        self,
        user_id: UUID,
        email: str,
        name: Optional[str] = None,
        organization: Optional[str] = None,
        is_active: bool = True,
    ) -> dict[str, Any]:
        """Create a new user.

        Args:
            user_id: Unique user identifier
            email: User email address
            name: User name (optional)
            organization: User organization (optional)
            is_active: Whether user is active

        Returns:
            Created user data
        """
        data = {
            "id": str(user_id),
            "email": email,
            "is_active": 1 if is_active else 0,
        }
        if name:
            data["name"] = name
        if organization:
            data["organization"] = organization

        result = await self._request("POST", "/users", json=data)
        return cast(dict[str, Any], result)

    async def get_user(self, user_id: UUID) -> dict[str, Any]:
        """Get user by ID.

        Args:
            user_id: User identifier

        Returns:
            User data

        Raises:
            httpx.HTTPStatusError: If user not found (404)
        """
        result = await self._request("GET", f"/users/{user_id}")
        return cast(dict[str, Any], result)

    # Processing metrics operations
    async def create_processing_metric(
        self,
        metric_id: UUID,
        job_id: UUID,
        success: bool = False,
        processing_time_seconds: Optional[float] = None,
        pdf_pages: Optional[int] = None,
        pdf_size_bytes: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create processing metrics for a job.

        Args:
            metric_id: Unique metric identifier
            job_id: Associated job ID
            success: Whether processing succeeded
            processing_time_seconds: Time taken to process (optional)
            pdf_pages: Number of pages in PDF (optional)
            pdf_size_bytes: Size of PDF in bytes (optional)
            error_message: Error message if failed (optional)

        Returns:
            Created metric data
        """
        data: dict[str, Any] = {
            "id": str(metric_id),
            "job_id": str(job_id),
            "success": 1 if success else 0,
        }
        if processing_time_seconds is not None:
            data["processing_time_seconds"] = processing_time_seconds
        if pdf_pages is not None:
            data["pdf_pages"] = pdf_pages
        if pdf_size_bytes is not None:
            data["pdf_size_bytes"] = pdf_size_bytes
        if error_message:
            data["error_message"] = error_message

        result = await self._request("POST", "/metrics", json=data)
        return cast(dict[str, Any], result)


# Singleton instance
_db_client: Optional[DatabaseClient] = None


def get_db_client() -> DatabaseClient:
    """Get or create database client singleton.

    Returns:
        Database client instance
    """
    global _db_client
    if _db_client is None:
        _db_client = DatabaseClient()
    return _db_client


async def close_db_client() -> None:
    """Close database client and clean up connections."""
    global _db_client
    if _db_client is not None:
        await _db_client.close()
        _db_client = None
