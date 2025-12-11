using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using server.Controllers;
using server.core.Domain;
using server.Services;
using Xunit;

namespace server.tests;

public class JobControllerTests
{
    private readonly Mock<IDatabaseApiClient> _mockDatabaseClient;
    private readonly Mock<ILogger<JobController>> _mockLogger;
    private readonly JobController _controller;

    public JobControllerTests()
    {
        _mockDatabaseClient = new Mock<IDatabaseApiClient>();
        _mockLogger = new Mock<ILogger<JobController>>();
        _controller = new JobController(_mockDatabaseClient.Object, _mockLogger.Object);
    }

    [Fact]
    public async Task GetStatus_ReturnsJob_WhenJobExists()
    {
        // Arrange
        var jobId = Guid.NewGuid();
        var job = new Job
        {
            Id = jobId,
            Status = JobStatus.Submitted,
            R2Key = "test-key",
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        _mockDatabaseClient
            .Setup(x => x.GetJobAsync(jobId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(job);

        // Act
        var result = await _controller.GetStatus(jobId, CancellationToken.None);

        // Assert
        var okResult = Assert.IsType<OkObjectResult>(result.Result);
        var returnedJob = Assert.IsType<Job>(okResult.Value);
        Assert.Equal(jobId, returnedJob.Id);
    }

    [Fact]
    public async Task GetStatus_ReturnsNotFound_WhenJobDoesNotExist()
    {
        // Arrange
        var jobId = Guid.NewGuid();
        _mockDatabaseClient
            .Setup(x => x.GetJobAsync(jobId, It.IsAny<CancellationToken>()))
            .ThrowsAsync(new HttpRequestException("Not found", null, System.Net.HttpStatusCode.NotFound));

        // Act
        var result = await _controller.GetStatus(jobId, CancellationToken.None);

        // Assert
        Assert.IsType<NotFoundObjectResult>(result.Result);
    }

    [Fact]
    public async Task ListJobs_ReturnsJobs_WhenSuccessful()
    {
        // Arrange
        var jobs = new List<Job>
        {
            new Job { Id = Guid.NewGuid(), Status = JobStatus.Submitted, R2Key = "key1", CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow },
            new Job { Id = Guid.NewGuid(), Status = JobStatus.Running, R2Key = "key2", CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow }
        };

        _mockDatabaseClient
            .Setup(x => x.ListJobsAsync(null, null, 100, It.IsAny<CancellationToken>()))
            .ReturnsAsync(jobs);

        // Act
        var result = await _controller.ListJobs(null, null, 100, CancellationToken.None);

        // Assert
        var okResult = Assert.IsType<OkObjectResult>(result.Result);
        var returnedJobs = Assert.IsType<List<Job>>(okResult.Value);
        Assert.Equal(2, returnedJobs.Count);
    }
}
