using System.Text.Json.Serialization;

namespace server.core.Domain;

/// <summary>
/// Job model for tracking PDF processing.
/// </summary>
public class Job
{
    [JsonPropertyName("id")]
    public Guid Id { get; set; }

    [JsonPropertyName("slurmId")]
    public string? SlurmId { get; set; }

    [JsonPropertyName("status")]
    [JsonConverter(typeof(JsonStringEnumConverter))]
    public JobStatus Status { get; set; }

    [JsonPropertyName("r2Key")]
    public string R2Key { get; set; } = string.Empty;

    [JsonPropertyName("createdAt")]
    public DateTime CreatedAt { get; set; }

    [JsonPropertyName("updatedAt")]
    public DateTime UpdatedAt { get; set; }

    [JsonPropertyName("resultsUrl")]
    public string? ResultsUrl { get; set; }

    [JsonPropertyName("userId")]
    public Guid? UserId { get; set; }

    [JsonPropertyName("error")]
    public string? Error { get; set; }
}
