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
    private readonly string _baseUrl;
    private readonly string _token;

    public DatabaseApiClient(HttpClient httpClient, IConfiguration configuration, ILogger<DatabaseApiClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        
        _baseUrl = configuration["DB_API_URL"] 
                   ?? configuration["DatabaseApi:BaseUrl"] 
                   ?? "http://localhost:8787";
        
        _token = configuration["DB_API_TOKEN"] 
                 ?? configuration["DatabaseApi:Token"] 
                 ?? string.Empty;

        _httpClient.BaseAddress = new Uri(_baseUrl.TrimEnd('/'));
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_token}");
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
            ["status"] = "submitted"
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
        var queryParams = new List<string> { $"limit={limit}" };
        
        if (status.HasValue)
            queryParams.Add($"status={status.Value.ToString().ToLowerInvariant()}");
        if (userId.HasValue)
            queryParams.Add($"user_id={userId}");

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

        return new Job
        {
            Id = Guid.Parse(data["id"].GetString() ?? throw new InvalidOperationException("Job ID is required")),
            SlurmId = data.ContainsKey("slurm_id") && data["slurm_id"].ValueKind != JsonValueKind.Null 
                ? data["slurm_id"].GetString() 
                : null,
            Status = Enum.Parse<JobStatus>(data["status"].GetString() ?? "Submitted", ignoreCase: true),
            R2Key = data["r2_key"].GetString() ?? string.Empty,
            CreatedAt = data.ContainsKey("created_at") && data["created_at"].ValueKind != JsonValueKind.Null
                ? DateTimeOffset.FromUnixTimeSeconds(data["created_at"].GetInt64()).UtcDateTime
                : now,
            UpdatedAt = data.ContainsKey("updated_at") && data["updated_at"].ValueKind != JsonValueKind.Null
                ? DateTimeOffset.FromUnixTimeSeconds(data["updated_at"].GetInt64()).UtcDateTime
                : now,
            ResultsUrl = data.ContainsKey("results_url") && data["results_url"].ValueKind != JsonValueKind.Null
                ? data["results_url"].GetString()
                : null,
            UserId = data.ContainsKey("user_id") && data["user_id"].ValueKind != JsonValueKind.Null
                ? Guid.Parse(data["user_id"].GetString()!)
                : null,
            Error = null
        };
    }
}
