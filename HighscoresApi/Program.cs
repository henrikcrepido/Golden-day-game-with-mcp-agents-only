using System.Text.Json;
using System.Text.RegularExpressions;

var builder = WebApplication.CreateBuilder(args);

// ── Build ─────────────────────────────────────────────────────────────────────
var app = builder.Build();

// Serve index.html for requests to "/"
app.UseDefaultFiles();

// Serve .html / .json / etc. from wwwroot/
app.UseStaticFiles();

// ── Shared configuration ──────────────────────────────────────────────────────

// Same key constraint as server.py and api/highscores.php
var keyPattern = new Regex(@"^[a-zA-Z0-9_-]{1,64}$", RegexOptions.Compiled);

// data/ folder lives alongside the published DLL (i.e. the IIS site root)
var dataDir = Path.Combine(app.Environment.ContentRootPath, "data");
Directory.CreateDirectory(dataDir);

// ── GET /api/highscores/{key} ─────────────────────────────────────────────────
app.MapGet("/api/highscores/{key}", (string key) =>
{
    if (!keyPattern.IsMatch(key))
        return Results.BadRequest(new { error = "Invalid key" });

    var filePath = Path.Combine(dataDir, $"{key}.json");

    if (!File.Exists(filePath))
        return Results.Ok(Array.Empty<object>());

    var json = File.ReadAllText(filePath);
    return Results.Content(json, "application/json");
});

// ── POST /api/highscores/{key} ────────────────────────────────────────────────
app.MapPost("/api/highscores/{key}", async (string key, HttpRequest request) =>
{
    if (!keyPattern.IsMatch(key))
        return Results.BadRequest(new { error = "Invalid key" });

    JsonDocument body;
    try
    {
        body = await JsonDocument.ParseAsync(request.Body);
    }
    catch (JsonException)
    {
        return Results.BadRequest(new { error = "Invalid JSON" });
    }

    if (body.RootElement.ValueKind != JsonValueKind.Array)
        return Results.BadRequest(new { error = "Payload must be a JSON array" });

    // Serialize back to indented JSON (matches server.py output style)
    var formatted = JsonSerializer.Serialize(
        JsonSerializer.Deserialize<JsonElement[]>(body.RootElement),
        new JsonSerializerOptions { WriteIndented = true });

    // Atomic write: write to temp file then rename to avoid partial reads
    var filePath = Path.Combine(dataDir, $"{key}.json");
    var tmpPath  = filePath + ".tmp";

    await File.WriteAllTextAsync(tmpPath, formatted);
    File.Move(tmpPath, filePath, overwrite: true);

    return Results.Ok(new { ok = true });
});

app.Run();
