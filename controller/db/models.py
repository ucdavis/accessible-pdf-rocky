"""Database models for job tracking."""

# TODO: Implement database models using SQLAlchemy or similar ORM
# Required models:
# - Job: track PDF processing jobs
#   - id (UUID)
#   - slurm_id (string)
#   - status (enum: submitted, running, completed, failed)
#   - r2_key (string)
#   - created_at (timestamp)
#   - updated_at (timestamp)
#   - results_url (string, nullable)
# - User: track users/organizations
# - ProcessingMetrics: track processing statistics


class Job:
    """
    Job model for tracking PDF processing.

    TODO: Implement as SQLAlchemy model or Pydantic schema
    """

    pass


class User:
    """
    User model for authentication and tracking.

    TODO: Implement user authentication model
    """

    pass


class ProcessingMetrics:
    """
    Processing metrics for monitoring and analytics.

    TODO: Implement metrics tracking
    """

    pass
