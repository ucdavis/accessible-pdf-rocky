using server.Services;

var builder = WebApplication.CreateBuilder(args);

// Setup configuration sources (last one wins)
builder.Configuration
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
    .AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true, reloadOnChange: true)
    .AddEnvFile(".env", optional: true) // secrets stored here
    .AddEnvFile($".env.{builder.Environment.EnvironmentName}", optional: true) // env-specific secrets
    .AddEnvironmentVariables(); // OS env vars override everything

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure CORS for React client
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowClient", policy =>
    {
        if (builder.Environment.IsDevelopment())
        {
            // In development, allow the React dev server
            policy
                .WithOrigins("http://localhost:5173", "http://127.0.0.1:5173")
                .AllowAnyHeader()
                .AllowAnyMethod();
        }
        else
        {
            // In production, get allowed origins from configuration
            var allowedOrigins = builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>() ?? [];
            if (allowedOrigins.Length > 0)
            {
                policy
                    .WithOrigins(allowedOrigins)
                    .AllowAnyHeader()
                    .AllowAnyMethod();
            }
            else
            {
                // Log warning if no CORS origins configured in non-development
                Console.WriteLine("WARNING: No CORS allowed origins configured. Cross-origin requests will be blocked.");
                Console.WriteLine("         Configure 'Cors:AllowedOrigins' in appsettings.Production.json or environment variables.");
            }
        }
    });
});

// Register services
builder.Services.AddHttpClient<IDatabaseApiClient, DatabaseApiClient>((serviceProvider, client) =>
{
    var config = serviceProvider.GetRequiredService<IConfiguration>();
    var baseUrl = config["DB_API_URL"] ?? config["DatabaseApi:BaseUrl"] ?? "http://localhost:8787";
    var token = config["DB_API_TOKEN"] ?? config["DatabaseApi:Token"] ?? string.Empty;
    
    client.BaseAddress = new Uri(baseUrl.TrimEnd('/'));
    if (!string.IsNullOrEmpty(token))
    {
        client.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);
    }
    client.Timeout = TimeSpan.FromSeconds(30);
});

builder.Services.AddHttpClient<IMetricsClient, MetricsClient>();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}
else
{
    // Global exception handler for production
    app.UseExceptionHandler("/error");
}

// Ensure HTTPS in production
app.UseHttpsRedirection();

app.UseCors("AllowClient");
app.MapControllers();

// Health check endpoint
app.MapGet("/health", () => Results.Ok(new { status = "healthy" }));

// Minimal error endpoint for production exception handling
app.Map("/error", () => Results.Problem(
    title: "An error occurred",
    statusCode: StatusCodes.Status500InternalServerError
));

app.Run();
