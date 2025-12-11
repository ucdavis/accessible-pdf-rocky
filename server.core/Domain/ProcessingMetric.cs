using System.Text.Json.Serialization;

namespace server.core.Domain;

/// <summary>
/// Processing metric for monitoring and analytics.
/// </summary>
public class ProcessingMetric
{
    [JsonPropertyName("id")]
    public Guid Id { get; set; }

    [JsonPropertyName("jobId")]
    public Guid JobId { get; set; }

    [JsonPropertyName("processingTimeSeconds")]
    public double? ProcessingTimeSeconds { get; set; }

    [JsonPropertyName("pdfPages")]
    public int? PdfPages { get; set; }

    /// <summary>
    /// PDF file size in bytes. Uses long to support files >2GB.
    /// </summary>
    [JsonPropertyName("pdfSizeBytes")]
    public long? PdfSizeBytes { get; set; }

    [JsonPropertyName("success")]
    public bool Success { get; set; }

    [JsonPropertyName("errorMessage")]
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// Timestamp of metric creation. Should be stored and handled as UTC.
    /// </summary>
    [JsonPropertyName("createdAt")]
    public DateTime CreatedAt { get; set; }
}
