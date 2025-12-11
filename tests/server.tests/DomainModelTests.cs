using System.Text.Json;
using server.core.Domain;
using Xunit;

namespace server.tests;

public class JobTests
{
    [Fact]
    public void Job_SerializesToJson_WithCorrectPropertyNames()
    {
        // Arrange
        var job = new Job
        {
            Id = Guid.Parse("550e8400-e29b-41d4-a716-446655440000"),
            SlurmId = "12345",
            Status = JobStatus.Running,
            R2Key = "test-key",
            CreatedAt = new DateTime(2025, 1, 1, 0, 0, 0, DateTimeKind.Utc),
            UpdatedAt = new DateTime(2025, 1, 2, 0, 0, 0, DateTimeKind.Utc),
            ResultsUrl = "https://example.com/results",
            UserId = Guid.Parse("660e8400-e29b-41d4-a716-446655440000"),
            Error = "Test error"
        };

        // Act
        var json = JsonSerializer.Serialize(job);

        // Assert
        Assert.Contains("\"id\":", json);
        Assert.Contains("\"slurmId\":", json);
        Assert.Contains("\"status\":", json);
        Assert.Contains("\"r2Key\":", json);
        Assert.Contains("\"Running\"", json);
    }

    [Fact]
    public void Job_DeserializesFromJson_WithCorrectPropertyNames()
    {
        // Arrange
        var json = """
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "slurmId": "12345",
                "status": "Running",
                "r2Key": "test-key",
                "createdAt": "2025-01-01T00:00:00Z",
                "updatedAt": "2025-01-02T00:00:00Z",
                "resultsUrl": "https://example.com/results",
                "userId": "660e8400-e29b-41d4-a716-446655440000",
                "error": "Test error"
            }
            """;

        // Act
        var job = JsonSerializer.Deserialize<Job>(json);

        // Assert
        Assert.NotNull(job);
        Assert.Equal(Guid.Parse("550e8400-e29b-41d4-a716-446655440000"), job.Id);
        Assert.Equal("12345", job.SlurmId);
        Assert.Equal(JobStatus.Running, job.Status);
        Assert.Equal("test-key", job.R2Key);
        Assert.Equal("https://example.com/results", job.ResultsUrl);
        Assert.Equal(Guid.Parse("660e8400-e29b-41d4-a716-446655440000"), job.UserId);
        Assert.Equal("Test error", job.Error);
    }

    [Fact]
    public void Job_HandlesNullableProperties()
    {
        // Arrange
        var job = new Job
        {
            Id = Guid.NewGuid(),
            Status = JobStatus.Submitted,
            R2Key = "test-key",
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        // Assert
        Assert.Null(job.SlurmId);
        Assert.Null(job.ResultsUrl);
        Assert.Null(job.UserId);
        Assert.Null(job.Error);
    }
}

public class UserTests
{
    [Fact]
    public void User_SerializesToJson_WithCorrectPropertyNames()
    {
        // Arrange
        var user = new User
        {
            Id = Guid.Parse("550e8400-e29b-41d4-a716-446655440000"),
            Email = "test@example.com",
            Name = "Test User",
            Organization = "Test Org",
            CreatedAt = new DateTime(2025, 1, 1, 0, 0, 0, DateTimeKind.Utc),
            IsActive = true
        };

        // Act
        var json = JsonSerializer.Serialize(user);

        // Assert
        Assert.Contains("\"id\":", json);
        Assert.Contains("\"email\":", json);
        Assert.Contains("\"name\":", json);
        Assert.Contains("\"organization\":", json);
        Assert.Contains("\"createdAt\":", json);
        Assert.Contains("\"isActive\":", json);
        Assert.Contains("test@example.com", json);
    }

    [Fact]
    public void User_DeserializesFromJson_WithCorrectPropertyNames()
    {
        // Arrange
        var json = """
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "test@example.com",
                "name": "Test User",
                "organization": "Test Org",
                "createdAt": "2025-01-01T00:00:00Z",
                "isActive": true
            }
            """;

        // Act
        var user = JsonSerializer.Deserialize<User>(json);

        // Assert
        Assert.NotNull(user);
        Assert.Equal(Guid.Parse("550e8400-e29b-41d4-a716-446655440000"), user.Id);
        Assert.Equal("test@example.com", user.Email);
        Assert.Equal("Test User", user.Name);
        Assert.Equal("Test Org", user.Organization);
        Assert.True(user.IsActive);
    }

    [Fact]
    public void User_HandlesNullableProperties()
    {
        // Arrange
        var user = new User
        {
            Id = Guid.NewGuid(),
            Email = "test@example.com",
            CreatedAt = DateTime.UtcNow,
            IsActive = true
        };

        // Assert
        Assert.Null(user.Name);
        Assert.Null(user.Organization);
    }
}

public class ProcessingMetricTests
{
    [Fact]
    public void ProcessingMetric_SerializesToJson_WithCorrectPropertyNames()
    {
        // Arrange
        var metric = new ProcessingMetric
        {
            Id = Guid.Parse("550e8400-e29b-41d4-a716-446655440000"),
            JobId = Guid.Parse("660e8400-e29b-41d4-a716-446655440000"),
            ProcessingTimeSeconds = 123.45,
            PdfPages = 10,
            PdfSizeBytes = 1024000,
            Success = true,
            ErrorMessage = null,
            CreatedAt = new DateTime(2025, 1, 1, 0, 0, 0, DateTimeKind.Utc)
        };

        // Act
        var json = JsonSerializer.Serialize(metric);

        // Assert
        Assert.Contains("\"id\":", json);
        Assert.Contains("\"jobId\":", json);
        Assert.Contains("\"processingTimeSeconds\":", json);
        Assert.Contains("\"pdfPages\":", json);
        Assert.Contains("\"pdfSizeBytes\":", json);
        Assert.Contains("\"success\":", json);
        Assert.Contains("123.45", json);
    }

    [Fact]
    public void ProcessingMetric_DeserializesFromJson_WithCorrectPropertyNames()
    {
        // Arrange
        var json = """
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "jobId": "660e8400-e29b-41d4-a716-446655440000",
                "processingTimeSeconds": 123.45,
                "pdfPages": 10,
                "pdfSizeBytes": 1024000,
                "success": true,
                "errorMessage": "Test error",
                "createdAt": "2025-01-01T00:00:00Z"
            }
            """;

        // Act
        var metric = JsonSerializer.Deserialize<ProcessingMetric>(json);

        // Assert
        Assert.NotNull(metric);
        Assert.Equal(Guid.Parse("550e8400-e29b-41d4-a716-446655440000"), metric.Id);
        Assert.Equal(Guid.Parse("660e8400-e29b-41d4-a716-446655440000"), metric.JobId);
        Assert.Equal(123.45, metric.ProcessingTimeSeconds);
        Assert.Equal(10, metric.PdfPages);
        Assert.Equal(1024000, metric.PdfSizeBytes);
        Assert.True(metric.Success);
        Assert.Equal("Test error", metric.ErrorMessage);
    }

    [Fact]
    public void ProcessingMetric_HandlesNullableProperties()
    {
        // Arrange
        var metric = new ProcessingMetric
        {
            Id = Guid.NewGuid(),
            JobId = Guid.NewGuid(),
            Success = false,
            CreatedAt = DateTime.UtcNow
        };

        // Assert
        Assert.Null(metric.ProcessingTimeSeconds);
        Assert.Null(metric.PdfPages);
        Assert.Null(metric.PdfSizeBytes);
        Assert.Null(metric.ErrorMessage);
    }

    [Fact]
    public void ProcessingMetric_SuccessFalse_WithErrorMessage()
    {
        // Arrange
        var metric = new ProcessingMetric
        {
            Id = Guid.NewGuid(),
            JobId = Guid.NewGuid(),
            Success = false,
            ErrorMessage = "Processing failed",
            CreatedAt = DateTime.UtcNow
        };

        // Assert
        Assert.False(metric.Success);
        Assert.Equal("Processing failed", metric.ErrorMessage);
    }
}

public class JobStatusTests
{
    [Fact]
    public void JobStatus_HasExpectedValues()
    {
        // Assert
        Assert.Equal(0, (int)JobStatus.Submitted);
        Assert.Equal(1, (int)JobStatus.Running);
        Assert.Equal(2, (int)JobStatus.Completed);
        Assert.Equal(3, (int)JobStatus.Failed);
    }

    [Fact]
    public void JobStatus_CanParseFromString()
    {
        // Act & Assert
        Assert.Equal(JobStatus.Submitted, Enum.Parse<JobStatus>("Submitted"));
        Assert.Equal(JobStatus.Running, Enum.Parse<JobStatus>("Running"));
        Assert.Equal(JobStatus.Completed, Enum.Parse<JobStatus>("Completed"));
        Assert.Equal(JobStatus.Failed, Enum.Parse<JobStatus>("Failed"));
    }

    [Fact]
    public void JobStatus_CanParseFromString_IgnoreCase()
    {
        // Act & Assert
        Assert.Equal(JobStatus.Submitted, Enum.Parse<JobStatus>("submitted", ignoreCase: true));
        Assert.Equal(JobStatus.Running, Enum.Parse<JobStatus>("RUNNING", ignoreCase: true));
        Assert.Equal(JobStatus.Completed, Enum.Parse<JobStatus>("completed", ignoreCase: true));
        Assert.Equal(JobStatus.Failed, Enum.Parse<JobStatus>("failed", ignoreCase: true));
    }
}
