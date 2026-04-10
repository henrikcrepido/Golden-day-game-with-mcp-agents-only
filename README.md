# Golden-day-game-with-mcp-agents-only

A collection of browser games built entirely by MCP coding agents, with full
action logs and reusable instructions saved as Markdown for future sessions.

---

## 🎮 Games

| Game | File | How to play |
|------|------|-------------|
| Minesweeper | [`minesweeper.html`](minesweeper.html) | Open the file in any browser — no build step needed |
| Pinball Breaker | [`pinball-breaker.html`](pinball-breaker.html) | Mouse/touch to move the paddle; smash bricks and hit bumpers for a score multiplier |
| Dungeon of Echoes | [`mod-adventure.html`](mod-adventure.html) | A D&D-style MOD text adventure — explore, fight monsters, and claim the Dragon's Hoard |
| Support Hero | [`support-hero.html`](support-hero.html) | Handle IBM MQ/MSMQ backout queues, restart services & IIS app pools, escalate correctly — reach Black Belt Support Master! |
| AR Crystal Surge | [`ar-crystal-surge.html`](ar-crystal-surge.html) | AR.js gem collector — point your camera at the Hiro marker and tap floating crystals; combo multipliers up to ×4. Works without a camera in holographic Demo Mode! |
| Ture & Selma – Hitta Orden! | [`ture-selma.html`](ture-selma.html) | Swedish platformer for young kids — play as Ture (5) or Selma (3), jump to collect items and learn to spell each word in Swedish (arrows + Space; touch buttons on mobile) |
| Ski Slalom | [`ski-slalom.html`](ski-slalom.html) | Race through 20 slalom gates as fast as you can! Steer left & right with arrow keys (or A/D). Miss a gate = +2 s penalty. Best time is saved as your record. |
| Asteroid Shield | [`asteroid-shield.html`](asteroid-shield.html) | Pilot your spaceship around Earth and blast incoming asteroids before they crash into the planet! Asteroids split on impact — survive wave after wave! |

---

## 📄 Documentation

| File | Purpose |
|------|---------|
| [`AGENT_LOG.md`](AGENT_LOG.md) | Timestamped log of every action taken during the Minesweeper build session, including decision rationale |
| [`INSTRUCTIONS.md`](INSTRUCTIONS.md) | Reusable step-by-step instructions for future agents building standalone browser games |

---

## 🚀 Running locally (Python)

```bash
python3 server.py 8080
# then open http://localhost:8080/index.html
```

The Python server also provides the shared highscores API (`/api/highscores/<key>`)
that syncs scores between all users connected to the same server.

---

## 🖥 Hosting on IIS (no Python required)

Two approaches are available depending on what is installed on your IIS server:

| Approach | Requirements | Recommended? |
|----------|-------------|--------------|
| **[.NET 8 minimal API](#option-a--net-8-minimal-api-recommended)** | .NET 8 Runtime on the server | ✅ Recommended |
| **[PHP handler](#option-b-php-fastcgi-handler)** | PHP 7.x / 8.x via FastCGI | Alternative |

Both approaches mirror the Python `server.py` API exactly — no changes to the
HTML game files are required.

---

## Option A — .NET 8 Minimal API (recommended)

The `HighscoresApi/` folder contains a .NET 8 ASP.NET Core minimal API
project. When published it produces a single self-contained folder that IIS
hosts directly via the built-in `AspNetCoreModuleV2`. **No PHP, no URL Rewrite
module, and no manual `web.config` editing are required.**

### Prerequisites

| Requirement | Notes |
|-------------|-------|
| **.NET 8 SDK** (build machine) | [Download](https://dotnet.microsoft.com/download/dotnet/8.0) — only needed to build, not on the server |
| **.NET 8 Runtime / Hosting Bundle** (server) | [Download the Hosting Bundle](https://dotnet.microsoft.com/download/dotnet/8.0) — installs the ASP.NET Core runtime **and** the IIS `AspNetCoreModuleV2` in one step |
| **IIS 7+** | Windows Server 2008 R2+ or Windows 10/11 with IIS feature enabled |

### Step 1 — Enable IIS on Windows

**Windows 10 / 11:**
1. Open *Control Panel → Programs → Turn Windows features on or off*.
2. Tick **Internet Information Services**.
3. Click OK and wait for installation to finish.

**Windows Server:**
1. Open *Server Manager → Add Roles and Features*.
2. Select **Web Server (IIS)** and complete the wizard.

### Step 2 — Install the .NET 8 Hosting Bundle on the server

1. Download the **ASP.NET Core Runtime 8 — Hosting Bundle** from
   <https://dotnet.microsoft.com/download/dotnet/8.0>.
2. Run the installer — it installs the runtime *and* registers
   `AspNetCoreModuleV2` in IIS automatically.
3. Restart IIS after installation:
   ```bat
   iisreset
   ```

### Step 3 — Publish the project

On your **build machine** (where the .NET 8 SDK is installed), run:

```powershell
cd HighscoresApi
dotnet publish -c Release -o C:\publish\goldendaygames
```

`dotnet publish` automatically:
- Compiles the app
- Copies all HTML game files into `wwwroot\`
- Generates a ready-to-use `web.config` (using `AspNetCoreModuleV2`)

### Step 4 — Deploy to IIS

1. **Copy** the publish output to your server, e.g.:
   ```bat
   xcopy /E /I /Y "C:\publish\goldendaygames" "C:\inetpub\wwwroot\goldendaygames"
   ```

2. **Create a site** in IIS Manager (or use an existing one):
   - Right-click *Sites → Add Website…*
   - Set *Physical path* to `C:\inetpub\wwwroot\goldendaygames`
   - Choose a port (e.g. 8080) and click OK

3. **Grant write access** to the `data\` folder for the application-pool
   identity. Open PowerShell as Administrator:
   ```powershell
   icacls "C:\inetpub\wwwroot\goldendaygames\data" /grant "IIS AppPool\DefaultAppPool:(OI)(CI)M"
   ```
   *(Replace `DefaultAppPool` with the actual app-pool name shown in IIS
   Manager if it differs.)*

4. **Browse** to `http://localhost:8080/` — the games load immediately and
   the leaderboard API is ready.

### How it works

| File / Folder | Purpose |
|---------------|---------|
| `HighscoresApi/Program.cs` | Minimal API: serves static HTML files + `GET`/`POST /api/highscores/{key}` |
| `HighscoresApi/HighscoresApi.csproj` | SDK project — includes all `*.html` files as `wwwroot` content on publish |
| `data/` (created at runtime) | One `.json` file per score key, written atomically |
| `web.config` (auto-generated on publish) | Configures IIS to use `AspNetCoreModuleV2`; no manual editing needed |

---

## Option B — PHP FastCGI handler

If you have PHP installed on IIS but **not** .NET, the `api/highscores.php`
handler and root `web.config` provide an equivalent solution.

### Prerequisites

| Requirement | Notes |
|-------------|-------|
| **IIS 7+** | Windows Server 2008 R2 or later, or Windows 10/11 with IIS feature enabled |
| **URL Rewrite module** | [Download from Microsoft](https://www.iis.net/downloads/microsoft/url-rewrite) |
| **PHP (any 7.x / 8.x)** | [Install guide for IIS](https://www.php.net/manual/en/install.windows.iis7.php) |

### Enable IIS (if not already enabled)

**Windows 10 / 11:** *Control Panel → Programs → Turn Windows features on or
off* → tick **Internet Information Services** (also tick
**Application Development Features → CGI**).

**Windows Server:** *Server Manager → Add Roles and Features → Web Server
(IIS)*, include the **CGI** role service.

### Install the URL Rewrite module

1. Download from <https://www.iis.net/downloads/microsoft/url-rewrite>
2. Run the `.msi` installer then run `iisreset`

### Install PHP and register it in IIS

1. Download the **Non-Thread Safe (NTS) x64** ZIP from <https://windows.php.net/download/>
2. Extract to `C:\PHP`
3. Copy `php.ini-production` → `php.ini`
4. In IIS Manager → server node → **Handler Mappings → Add Module Mapping…**

   | Field | Value |
   |-------|-------|
   | Request path | `*.php` |
   | Module | `FastCgiModule` |
   | Executable | `C:\PHP\php-cgi.exe` |
   | Name | `PHP_via_FastCGI` |

### Deploy

1. Copy the entire repository to `C:\inetpub\wwwroot\goldendaygames`
2. Create an IIS site pointing to that folder
3. Grant write access to `data\`:
   ```powershell
   icacls "C:\inetpub\wwwroot\goldendaygames\data" /grant "IIS AppPool\DefaultAppPool:(OI)(CI)M"
   ```
4. Browse to `http://localhost:<port>/`

### How it works (PHP)

| File | Purpose |
|------|---------|
| `web.config` | URL Rewrite: `/api/highscores/{key}` → `api/highscores.php`; blocks `data/` browsing |
| `api/highscores.php` | PHP handler — reads/writes `data/{key}.json`; mirrors the Python API |
| `data/` | JSON files written here at runtime |
