using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Moq.Protected;
using server.Services;
using System.Net;
using System.Text.Json;
using Xunit;

namespace server.tests;

public class MetricsClientTests
{
    private readonly Mock<ILogger<MetricsClient>> _mockLogger;
    private readonly Mock<HttpMessageHandler> _mockHttpMessageHandler;
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _configuration;

    public MetricsClientTests()
    {
        _mockLogger = new Mock<ILogger<MetricsClient>>();
        _mockHttpMessageHandler = new Mock<HttpMessageHandler>();
        _httpClient = new HttpClient(_mockHttpMessageHandler.Object);

        var config = new Dictionary<string, string?>
        {
            ["METRICS_ENDPOINT"] = "http://localhost:8788/ingest",
            ["METRICS_TOKEN"] = "test-token",
            ["Metrics:Source"] = "test-source"
        };
        _configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(config)
            .Build();
    }

    [Fact]
    public async Task PushAsync_SendsCorrectPayload_WhenTokenConfigured()
    {
        // Arrange
        var client = new MetricsClient(_httpClient, _configuration, _mockLogger.Object);
        var metrics = new Dictionary<string, double>
        {
            ["test_metric"] = 123.45
        };

        _mockHttpMessageHandler
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == HttpMethod.Post &&
                    req.RequestUri!.ToString() == "http://localhost:8788/ingest" &&
                    req.Headers.Authorization!.Scheme == "Bearer" &&
                    req.Headers.Authorization!.Parameter == "test-token"),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.OK
            });

        // Act
        await client.PushAsync(metrics, CancellationToken.None);

        // Assert
        _mockHttpMessageHandler.Protected().Verify(
            "SendAsync",
            Times.Once(),
            ItExpr.IsAny<HttpRequestMessage>(),
            ItExpr.IsAny<CancellationToken>());
    }

    [Fact]
    public async Task PushAsync_SkipsRequest_WhenTokenNotConfigured()
    {
        // Arrange
        var config = new Dictionary<string, string?>
        {
            ["METRICS_ENDPOINT"] = "http://localhost:8788/ingest"
        };
        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(config)
            .Build();

        var client = new MetricsClient(_httpClient, configuration, _mockLogger.Object);
        var metrics = new Dictionary<string, double>
        {
            ["test_metric"] = 123.45
        };

        // Act
        await client.PushAsync(metrics, CancellationToken.None);

        // Assert
        _mockHttpMessageHandler.Protected().Verify(
            "SendAsync",
            Times.Never(),
            ItExpr.IsAny<HttpRequestMessage>(),
            ItExpr.IsAny<CancellationToken>());
    }

    [Fact]
    public async Task PushAsync_DoesNotThrow_WhenHttpRequestFails()
    {
        // Arrange
        var client = new MetricsClient(_httpClient, _configuration, _mockLogger.Object);
        var metrics = new Dictionary<string, double>
        {
            ["test_metric"] = 123.45
        };

        _mockHttpMessageHandler
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ThrowsAsync(new HttpRequestException("Network error"));

        // Act & Assert - Should not throw
        await client.PushAsync(metrics, CancellationToken.None);
    }

    [Fact]
    public async Task RecordJobSubmissionAsync_CallsPushWithCorrectMetrics_WhenSuccess()
    {
        // Arrange
        var client = new MetricsClient(_httpClient, _configuration, _mockLogger.Object);
        HttpRequestMessage? capturedRequest = null;

        _mockHttpMessageHandler
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .Callback<HttpRequestMessage, CancellationToken>((req, _) => capturedRequest = req)
            .ReturnsAsync(new HttpResponseMessage { StatusCode = HttpStatusCode.OK });

        // Act
        await client.RecordJobSubmissionAsync(success: true, latency: 1.23, CancellationToken.None);

        // Assert
        Assert.NotNull(capturedRequest);
        var content = await capturedRequest!.Content!.ReadAsStringAsync();
        var payload = JsonSerializer.Deserialize<JsonElement>(content);
        var metricsObj = payload.GetProperty("metrics");

        Assert.Equal(1, metricsObj.GetProperty("slurm_submitted_jobs_total").GetDouble());
        Assert.Equal(1.23, metricsObj.GetProperty("slurm_submission_latency_seconds").GetDouble(), precision: 5);
        Assert.Equal(1, metricsObj.GetProperty("slurm_submission_success").GetDouble());
        Assert.False(metricsObj.TryGetProperty("slurm_submission_failure", out _));
    }

    [Fact]
    public async Task RecordJobSubmissionAsync_CallsPushWithCorrectMetrics_WhenFailure()
    {
        // Arrange
        var client = new MetricsClient(_httpClient, _configuration, _mockLogger.Object);
        HttpRequestMessage? capturedRequest = null;

        _mockHttpMessageHandler
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .Callback<HttpRequestMessage, CancellationToken>((req, _) => capturedRequest = req)
            .ReturnsAsync(new HttpResponseMessage { StatusCode = HttpStatusCode.OK });

        // Act
        await client.RecordJobSubmissionAsync(success: false, latency: 2.34, CancellationToken.None);

        // Assert
        Assert.NotNull(capturedRequest);
        var content = await capturedRequest!.Content!.ReadAsStringAsync();
        var payload = JsonSerializer.Deserialize<JsonElement>(content);
        var metricsObj = payload.GetProperty("metrics");

        Assert.Equal(1, metricsObj.GetProperty("slurm_submitted_jobs_total").GetDouble());
        Assert.Equal(2.34, metricsObj.GetProperty("slurm_submission_latency_seconds").GetDouble(), precision: 5);
        Assert.Equal(1, metricsObj.GetProperty("slurm_submission_failure").GetDouble());
        Assert.False(metricsObj.TryGetProperty("slurm_submission_success", out _));
    }

    [Fact]
    public async Task RecordJobFailureAsync_CallsPushWithCorrectMetrics()
    {
        // Arrange
        var client = new MetricsClient(_httpClient, _configuration, _mockLogger.Object);
        HttpRequestMessage? capturedRequest = null;

        _mockHttpMessageHandler
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .Callback<HttpRequestMessage, CancellationToken>((req, _) => capturedRequest = req)
            .ReturnsAsync(new HttpResponseMessage { StatusCode = HttpStatusCode.OK });

        // Act
        await client.RecordJobFailureAsync("timeout", CancellationToken.None);

        // Assert
        Assert.NotNull(capturedRequest);
        var content = await capturedRequest!.Content!.ReadAsStringAsync();
        var payload = JsonSerializer.Deserialize<JsonElement>(content);
        var metricsObj = payload.GetProperty("metrics");

        Assert.Equal(1, metricsObj.GetProperty("slurm_submission_failure_timeout").GetDouble());
    }

    [Fact]
    public async Task RecordJobDurationAsync_CallsPushWithCorrectMetrics()
    {
        // Arrange
        var client = new MetricsClient(_httpClient, _configuration, _mockLogger.Object);
        HttpRequestMessage? capturedRequest = null;

        _mockHttpMessageHandler
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .Callback<HttpRequestMessage, CancellationToken>((req, _) => capturedRequest = req)
            .ReturnsAsync(new HttpResponseMessage { StatusCode = HttpStatusCode.OK });

        // Act
        await client.RecordJobDurationAsync(456.78, CancellationToken.None);

        // Assert
        Assert.NotNull(capturedRequest);
        var content = await capturedRequest!.Content!.ReadAsStringAsync();
        var payload = JsonSerializer.Deserialize<JsonElement>(content);
        var metricsObj = payload.GetProperty("metrics");

        Assert.Equal(456.78, metricsObj.GetProperty("slurm_job_duration_seconds").GetDouble(), precision: 5);
    }

    [Fact]
    public async Task RecordStatusCheckAsync_CallsPushWithCorrectMetrics()
    {
        // Arrange
        var client = new MetricsClient(_httpClient, _configuration, _mockLogger.Object);
        HttpRequestMessage? capturedRequest = null;

        _mockHttpMessageHandler
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .Callback<HttpRequestMessage, CancellationToken>((req, _) => capturedRequest = req)
            .ReturnsAsync(new HttpResponseMessage { StatusCode = HttpStatusCode.OK });

        // Act
        await client.RecordStatusCheckAsync(0.123, CancellationToken.None);

        // Assert
        Assert.NotNull(capturedRequest);
        var content = await capturedRequest!.Content!.ReadAsStringAsync();
        var payload = JsonSerializer.Deserialize<JsonElement>(content);
        var metricsObj = payload.GetProperty("metrics");

        Assert.Equal(0.123, metricsObj.GetProperty("slurm_status_check_seconds").GetDouble(), precision: 5);
    }

    [Fact]
    public void MetricsClient_UsesDefaultValues_WhenConfigNotProvided()
    {
        // Arrange
        var emptyConfig = new ConfigurationBuilder().Build();

        // Act
        var client = new MetricsClient(_httpClient, emptyConfig, _mockLogger.Object);

        // Assert - Constructor should not throw
        Assert.NotNull(client);
    }
}
