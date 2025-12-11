using Microsoft.Extensions.Diagnostics.HealthChecks;
using server.Services;

namespace server.HealthChecks;

/// <summary>
/// Health check for Database API connectivity.
/// </summary>
public class DatabaseApiHealthCheck : IHealthCheck
{
    private readonly IDatabaseApiClient _dbClient;
    private readonly ILogger<DatabaseApiHealthCheck> _logger;

    public DatabaseApiHealthCheck(IDatabaseApiClient dbClient, ILogger<DatabaseApiHealthCheck> logger)
    {
        _dbClient = dbClient;
        _logger = logger;
    }

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // Perform a lightweight connectivity check
            await _dbClient.ListJobsAsync(limit: 1, cancellationToken: cancellationToken);
            return HealthCheckResult.Healthy("Database API is accessible");
        }
        catch (HttpRequestException ex)
        {
            _logger.LogWarning(ex, "Database API health check failed: HTTP request error");
            return HealthCheckResult.Unhealthy("Database API is not accessible", ex);
        }
        catch (TaskCanceledException ex)
        {
            _logger.LogWarning(ex, "Database API health check failed: Timeout");
            return HealthCheckResult.Unhealthy("Database API request timed out", ex);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Database API health check failed: Unexpected error");
            return HealthCheckResult.Unhealthy("Database API check failed", ex);
        }
    }
}
