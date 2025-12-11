using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Mvc;
using server.core.Domain;
using server.Services;

namespace server.Controllers;

[ApiController]
[Route("api/[controller]")]
public class JobController : ControllerBase
{
    private readonly IDatabaseApiClient _databaseClient;
    private readonly ILogger<JobController> _logger;

    public JobController(IDatabaseApiClient databaseClient, ILogger<JobController> logger)
    {
        _databaseClient = databaseClient;
        _logger = logger;
    }

    /// <summary>
    /// Get job status from database.
    /// </summary>
    /// <param name="jobId">The job ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Job with camelCase field names for frontend compatibility</returns>
    [HttpGet("status/{jobId}")]
    [ProducesResponseType(typeof(Job), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status503ServiceUnavailable)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<Job>> GetStatus(Guid jobId, CancellationToken cancellationToken)
    {
        try
        {
            var job = await _databaseClient.GetJobAsync(jobId, cancellationToken);
            return Ok(job);
        }
        catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
        {
            return NotFound(new ErrorResponse { Detail = "Job not found" });
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Database service error for job {JobId}", jobId);
            return StatusCode(StatusCodes.Status503ServiceUnavailable, 
                new ErrorResponse { Detail = $"Database service unavailable: {ex.Message}" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error getting job status for {JobId}", jobId);
            return StatusCode(StatusCodes.Status500InternalServerError, 
                new ErrorResponse { Detail = "An unexpected error occurred" });
        }
    }

    /// <summary>
    /// List jobs with optional filters.
    /// </summary>
    /// <param name="status">Filter by status</param>
    /// <param name="userId">Filter by user ID</param>
    /// <param name="limit">Maximum number of jobs to return (1-1000)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of jobs</returns>
    [HttpGet]
    [ProducesResponseType(typeof(List<Job>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<List<Job>>> ListJobs(
        [FromQuery] JobStatus? status = null,
        [FromQuery] Guid? userId = null,
        [FromQuery] [Range(1, 1000)] int limit = 100,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var jobs = await _databaseClient.ListJobsAsync(status, userId, limit, cancellationToken);
            return Ok(jobs);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error listing jobs");
            return StatusCode(StatusCodes.Status500InternalServerError, 
                new ErrorResponse { Detail = "An unexpected error occurred" });
        }
    }
}
