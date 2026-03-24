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

The repository ships a `web.config` and a PHP API handler so the app can run
on any IIS 7+ server without Python and **without .NET Core or ASP.NET**.

> **TL;DR — just drop the files in `wwwroot`?**  
> Yes. Copy the whole folder to `C:\inetpub\wwwroot\goldendaygames`, point an
> IIS site at it, and the games load immediately. The two extra steps (URL
> Rewrite module + PHP) are only needed for the shared leaderboard API.

---

### Step 1 — Enable IIS on Windows

**Windows 10 / 11:**
1. Open *Control Panel → Programs → Turn Windows features on or off*.
2. Tick **Internet Information Services** (expand it and also tick
   **World Wide Web Services → Application Development Features → CGI**).
3. Click OK and wait for installation to finish.

**Windows Server:**
1. Open *Server Manager → Add Roles and Features*.
2. Select **Web Server (IIS)** and on the *Role Services* page also tick
   **Application Development → CGI**.
3. Complete the wizard.

---

### Step 2 — Install the URL Rewrite module

> Required for the `/api/highscores/…` routes. Skip this step if you only
> need the games to load (leaderboards will silently fall back to local
> browser storage).

1. Download the installer from
   <https://www.iis.net/downloads/microsoft/url-rewrite>.
2. Run the `.msi` and follow the prompts.
3. Restart IIS: open a command prompt as Administrator and run
   ```bat
   iisreset
   ```

---

### Step 3 — Install PHP

> Also required for the leaderboard API. Skip if not needed.

1. Download the **Non-Thread Safe (NTS) x64** ZIP from <https://windows.php.net/download/>.
2. Extract to `C:\PHP` (or any folder without spaces).
3. Copy `php.ini-production` to `php.ini` inside that folder.
4. Register PHP as a FastCGI handler in IIS:
   - Open **IIS Manager** → select your server node → double-click
     **Handler Mappings** → click *Add Module Mapping…*
   - Fill in:
     | Field | Value |
     |-------|-------|
     | Request path | `*.php` |
     | Module | `FastCgiModule` |
     | Executable | `C:\PHP\php-cgi.exe` |
     | Name | `PHP_via_FastCGI` |
   - Click OK and confirm adding the FastCGI application when prompted.

---

### Step 4 — Deploy the application

1. **Copy** the entire repository folder to your IIS site root, e.g.:
   ```bat
   xcopy /E /I /Y "C:\path\to\repo" "C:\inetpub\wwwroot\goldendaygames"
   ```

2. **Create a site** (or use *Default Web Site*):
   - In IIS Manager right-click *Sites → Add Website…*
   - Set *Physical path* to `C:\inetpub\wwwroot\goldendaygames`.
   - Choose a port (e.g. 8080) and click OK.

3. **Grant write access** to the `data\` folder for the application-pool
   identity. Open PowerShell as Administrator:
   ```powershell
   icacls "C:\inetpub\wwwroot\goldendaygames\data" /grant "IIS AppPool\DefaultAppPool:(OI)(CI)M"
   ```
   *(Replace `DefaultAppPool` with the actual app-pool name shown in IIS
   Manager if it differs.)*

4. **Browse** to `http://localhost:8080/` (or your configured port).

---

### How it works

| File | Purpose |
|------|---------|
| `web.config` | Routes `/api/highscores/{key}` → `api/highscores.php`; sets default document; adds JSON MIME type; blocks access to `data/` |
| `api/highscores.php` | PHP handler — reads/writes `data/{key}.json`; mirrors the Python server API |
| `data/` | JSON files written here at runtime (one file per score key) |

No .NET Core or ASP.NET runtime is needed — `web.config` only uses native
IIS modules (URL Rewrite, static content handler, request filtering).

> **Without PHP?** The games still load and store scores in the browser's
> `localStorage`. The leaderboard API calls will silently fail (404) and
> each browser will keep its own local copy — same behaviour as opening the
> `.html` files directly from disk.
