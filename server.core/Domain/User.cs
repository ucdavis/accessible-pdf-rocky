using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace server.core.Domain;

/// <summary>
/// User model for authentication and tracking.
/// </summary>
public class User
{
    [JsonPropertyName("id")]
    public Guid Id { get; set; }

    [Required]
    [EmailAddress]
    [JsonPropertyName("email")]
    public string Email { get; set; } = string.Empty;

    [JsonPropertyName("name")]
    public string? Name { get; set; }

    [JsonPropertyName("organization")]
    public string? Organization { get; set; }

    [JsonPropertyName("createdAt")]
    public DateTime CreatedAt { get; set; }

    [JsonPropertyName("isActive")]
    public bool IsActive { get; set; }
}
