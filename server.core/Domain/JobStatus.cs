namespace server.core.Domain;

/// <summary>
/// Job processing status enumeration.
/// </summary>
public enum JobStatus
{
    Submitted,
    Running,
    Completed,
    Failed
}
