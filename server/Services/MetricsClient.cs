using System.Text;
using System.Text.Json;

namespace server.Services;

public interface IMetricsClient
{
    Task PushAsync(Dictionary<string, double> metrics, CancellationToken cancellationToken = default);
    Task RecordJobSubmissionAsync(bool success, double latency, CancellationToken cancellationToken = default);
    Task RecordJobFailureAsync(string errorType, CancellationToken cancellationToken = default);
    Task RecordJobDurationAsync(double duration, CancellationToken cancellationToken = default);
    Task RecordStatusCheckAsync(double latency, CancellationToken cancellationToken = default);
}

/// <summary>
/// Client for pushing metrics to Cloudflare Worker.
/// Push-based metrics for job orchestration - eliminates need for inbound connections.
/// </summary>
public class MetricsClient : IMetricsClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<MetricsClient> _logger;
    private readonly string _endpoint;
    private readonly string _token;
    private readonly string _source;

    public MetricsClient(HttpClient httpClient, IConfiguration configuration, ILogger<MetricsClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;

        _endpoint = configuration["METRICS_ENDPOINT"]
                    ?? configuration["Metrics:Endpoint"]
                    ?? "http://localhost:8788/ingest";

        _token = configuration["METRICS_TOKEN"]
                 ?? configuration["Metrics:Token"]
                 ?? string.Empty;

        _source = configuration["Metrics:Source"] ?? "dotnet-server";

        _httpClient.Timeout = TimeSpan.FromSeconds(5);

        if (_endpoint.Contains("your-domain"))
        {
            _logger.LogWarning(
                "METRICS_ENDPOINT is using placeholder value. " +
                "Set METRICS_ENDPOINT environment variable to your actual Cloudflare Worker URL.");
        }
    }

    public async Task PushAsync(Dictionary<string, double> metrics, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(_token))
        {
            _logger.LogDebug("Metrics push skipped: METRICS_TOKEN not configured");
            return;
        }

        var payload = new
        {
            source = _source,
            timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
            metrics = metrics
        };

        try
        {
            var json = JsonSerializer.Serialize(payload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var request = new HttpRequestMessage(HttpMethod.Post, _endpoint)
            {
                Content = content
            };
            request.Headers.Add("Authorization", $"Bearer {_token}");

            var response = await _httpClient.SendAsync(request, cancellationToken);
            response.EnsureSuccessStatusCode();
        }
        catch (Exception ex)
        {
            // Don't fail the request if metrics push fails
            _logger.LogError(ex, "Failed to push metrics");
        }
    }

    public async Task RecordJobSubmissionAsync(bool success, double latency, CancellationToken cancellationToken = default)
    {
        var metrics = new Dictionary<string, double>
        {
            ["slurm_submitted_jobs_total"] = 1,
            ["slurm_submission_latency_seconds"] = latency
        };

        if (success)
            metrics["slurm_submission_success"] = 1;
        else
            metrics["slurm_submission_failure"] = 1;

        await PushAsync(metrics, cancellationToken);
    }

    public async Task RecordJobFailureAsync(string errorType, CancellationToken cancellationToken = default)
    {
        var metrics = new Dictionary<string, double>
        {
            [$"slurm_submission_failure_{errorType}"] = 1
        };

        await PushAsync(metrics, cancellationToken);
    }

    public async Task RecordJobDurationAsync(double duration, CancellationToken cancellationToken = default)
    {
        var metrics = new Dictionary<string, double>
        {
            ["slurm_job_duration_seconds"] = duration
        };

        await PushAsync(metrics, cancellationToken);
    }

    public async Task RecordStatusCheckAsync(double latency, CancellationToken cancellationToken = default)
    {
        var metrics = new Dictionary<string, double>
        {
            ["slurm_status_check_seconds"] = latency
        };

        await PushAsync(metrics, cancellationToken);
    }
}
