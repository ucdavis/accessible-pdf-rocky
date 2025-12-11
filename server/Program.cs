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
        }
    });
});

// Register services
builder.Services.AddHttpClient<IDatabaseApiClient, DatabaseApiClient>();
builder.Services.AddHttpClient<IMetricsClient, MetricsClient>();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors("AllowClient");
app.MapControllers();

app.Run();
