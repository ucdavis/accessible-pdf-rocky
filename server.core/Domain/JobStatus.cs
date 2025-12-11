namespace server.core.Domain;

/// <summary>
/// Job processing status enumeration.
/// Serialized as strings via JsonStringEnumConverter (e.g., "Submitted", "Running").
/// Database stores lowercase strings (e.g., "submitted", "running").
/// NOTE: Do not add explicit numeric values - this enum is always serialized as strings.
/// </summary>
public enum JobStatus
{
    Submitted,
    Running,
    Completed,
    Failed
}
