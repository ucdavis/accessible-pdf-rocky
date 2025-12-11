using System.Text.Json.Serialization;

namespace server.core.Domain;

/// <summary>
/// Standard error response for API endpoints.
/// </summary>
public class ErrorResponse
{
    [JsonPropertyName("detail")]
    public string Detail { get; set; } = string.Empty;
}
