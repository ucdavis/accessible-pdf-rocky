using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using server.core.Domain;

namespace server.Services;

public interface IDatabaseApiClient
{
    Task<Job> GetJobAsync(Guid jobId, CancellationToken cancellationToken = default);
    Task<Job> CreateJobAsync(Guid jobId, string r2Key, string? slurmId = null, Guid? userId = null, CancellationToken cancellationToken = default);
    Task<Job> UpdateJobAsync(Guid jobId, JobStatus? status = null, string? slurmId = null, string? resultsUrl = null, CancellationToken cancellationToken = default);
    Task DeleteJobAsync(Guid jobId, CancellationToken cancellationToken = default);
    Task<List<Job>> ListJobsAsync(JobStatus? status = null, Guid? userId = null, int limit = 100, CancellationToken cancellationToken = default);
}

/// <summary>
/// HTTP client for D1 database API worker.
/// </summary>
public class DatabaseApiClient : IDatabaseApiClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<DatabaseApiClient> _logger;

    public DatabaseApiClient(HttpClient httpClient, IConfiguration configuration, ILogger<DatabaseApiClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        
        var baseUrl = configuration["DB_API_URL"] 
                      ?? configuration["DatabaseApi:BaseUrl"] 
                      ?? "http://localhost:8787";
        
        var token = configuration["DB_API_TOKEN"] 
                    ?? configuration["DatabaseApi:Token"] 
                    ?? string.Empty;

        _httpClient.BaseAddress = new Uri(baseUrl.TrimEnd('/'));
        
        // Only set authorization if token is provided
        if (!string.IsNullOrEmpty(token))
        {
            _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
        }
        
        _httpClient.Timeout = TimeSpan.FromSeconds(30);
    }

    public async Task<Job> GetJobAsync(Guid jobId, CancellationToken cancellationToken = default)
    {
        var response = await _httpClient.GetAsync($"/jobs/{jobId}", cancellationToken);
        response.EnsureSuccessStatusCode();

        var content = await response.Content.ReadAsStringAsync(cancellationToken);
        var jobData = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(content)
            ?? throw new InvalidOperationException("Failed to deserialize job data");

        return MapToJob(jobData);
    }

    public async Task<Job> CreateJobAsync(Guid jobId, string r2Key, string? slurmId = null, Guid? userId = null, CancellationToken cancellationToken = default)
    {
        var data = new Dictionary<string, object>
        {
            ["id"] = jobId.ToString(),
            ["r2_key"] = r2Key,
            ["status"] = JobStatus.Submitted.ToString().ToLowerInvariant()
        };

        if (slurmId != null)
            data["slurm_id"] = slurmId;
        if (userId.HasValue)
            data["user_id"] = userId.Value.ToString();

        var json = JsonSerializer.Serialize(data);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _httpClient.PostAsync("/jobs", content, cancellationToken);
        response.EnsureSuccessStatusCode();

        var responseContent = await response.Content.ReadAsStringAsync(cancellationToken);
        var jobData = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(responseContent)
            ?? throw new InvalidOperationException("Failed to deserialize job data");

        return MapToJob(jobData);
    }

    public async Task<Job> UpdateJobAsync(Guid jobId, JobStatus? status = null, string? slurmId = null, string? resultsUrl = null, CancellationToken cancellationToken = default)
    {
        var data = new Dictionary<string, object>();

        if (status.HasValue)
            data["status"] = status.Value.ToString().ToLowerInvariant();
        if (slurmId != null)
            data["slurm_id"] = slurmId;
        if (resultsUrl != null)
            data["results_url"] = resultsUrl;

        var json = JsonSerializer.Serialize(data);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _httpClient.PutAsync($"/jobs/{jobId}", content, cancellationToken);
        response.EnsureSuccessStatusCode();

        var responseContent = await response.Content.ReadAsStringAsync(cancellationToken);
        var jobData = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(responseContent)
            ?? throw new InvalidOperationException("Failed to deserialize job data");

        return MapToJob(jobData);
    }

    public async Task DeleteJobAsync(Guid jobId, CancellationToken cancellationToken = default)
    {
        var response = await _httpClient.DeleteAsync($"/jobs/{jobId}", cancellationToken);
        response.EnsureSuccessStatusCode();
    }

    public async Task<List<Job>> ListJobsAsync(JobStatus? status = null, Guid? userId = null, int limit = 100, CancellationToken cancellationToken = default)
    {
        var queryParams = new List<string> { $"limit={Uri.EscapeDataString(limit.ToString())}" };
        
        if (status.HasValue)
            queryParams.Add($"status={Uri.EscapeDataString(status.Value.ToString().ToLowerInvariant())}");
        if (userId.HasValue)
            queryParams.Add($"user_id={Uri.EscapeDataString(userId.Value.ToString())}");

        var query = string.Join("&", queryParams);
        var response = await _httpClient.GetAsync($"/jobs?{query}", cancellationToken);
        response.EnsureSuccessStatusCode();

        var content = await response.Content.ReadAsStringAsync(cancellationToken);
        var jobsData = JsonSerializer.Deserialize<List<Dictionary<string, JsonElement>>>(content)
            ?? new List<Dictionary<string, JsonElement>>();

        return jobsData.Select(MapToJob).ToList();
    }

    private Job MapToJob(Dictionary<string, JsonElement> data)
    {
        var now = DateTime.UtcNow;

        try
        {
            // Required fields
            if (!data.TryGetValue("id", out var idElement))
            {
                _logger.LogError("Missing required field 'id' in job data");
                throw new InvalidOperationException("Job data is missing required 'id' field");
            }
            
            if (!data.TryGetValue("status", out var statusElement))
            {
                _logger.LogError("Missing required field 'status' in job data");
                throw new InvalidOperationException("Job data is missing required 'status' field");
            }
            
            if (!data.TryGetValue("r2_key", out var r2KeyElement))
            {
                _logger.LogError("Missing required field 'r2_key' in job data");
                throw new InvalidOperationException("Job data is missing required 'r2_key' field");
            }

            return new Job
            {
                Id = Guid.Parse(idElement.GetString() ?? throw new InvalidOperationException("Job ID cannot be null")),
                SlurmId = data.TryGetValue("slurm_id", out var slurmIdElement) && slurmIdElement.ValueKind != JsonValueKind.Null 
                    ? slurmIdElement.GetString() 
                    : null,
                Status = Enum.Parse<JobStatus>(statusElement.GetString() ?? "Submitted", ignoreCase: true),
                R2Key = r2KeyElement.GetString() ?? throw new InvalidOperationException("r2_key cannot be null"),
                CreatedAt = data.TryGetValue("created_at", out var createdAtElement) && createdAtElement.ValueKind != JsonValueKind.Null
                    ? DateTimeOffset.FromUnixTimeSeconds(createdAtElement.GetInt64()).UtcDateTime
                    : now,
                UpdatedAt = data.TryGetValue("updated_at", out var updatedAtElement) && updatedAtElement.ValueKind != JsonValueKind.Null
                    ? DateTimeOffset.FromUnixTimeSeconds(updatedAtElement.GetInt64()).UtcDateTime
                    : now,
                ResultsUrl = data.TryGetValue("results_url", out var resultsUrlElement) && resultsUrlElement.ValueKind != JsonValueKind.Null
                    ? resultsUrlElement.GetString()
                    : null,
                UserId = data.TryGetValue("user_id", out var userIdElement) && userIdElement.ValueKind != JsonValueKind.Null
                    ? Guid.Parse(userIdElement.GetString()!)
                    : null,
                Error = null
            };
        }
        catch (Exception ex) when (ex is not InvalidOperationException)
        {
            _logger.LogError(ex, "Failed to map job data from database API response");
            throw new InvalidOperationException("Failed to deserialize job data from database API", ex);
        }
    }
}
