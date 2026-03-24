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
on any IIS 7+ server without Python.

### Prerequisites

| Requirement | Notes |
|-------------|-------|
| **IIS 7+** | Windows Server 2008 R2 or later, or Windows 10/11 with IIS feature enabled |
| **URL Rewrite module** | [Download from Microsoft](https://www.iis.net/downloads/microsoft/url-rewrite) |
| **PHP (any 7.x / 8.x)** | [Install guide for IIS](https://www.php.net/manual/en/install.windows.iis7.php) |

### Deployment steps

1. **Copy** the entire repository folder to your IIS site root (e.g.
   `C:\inetpub\wwwroot\goldendaygames`).

2. **Create the site** in IIS Manager (or use an existing one) pointing to
   that folder.

3. **Grant write access** to the `data\` sub-folder for the application-pool
   identity (e.g. `IIS AppPool\DefaultAppPool`):
   ```powershell
   icacls "C:\inetpub\wwwroot\goldendaygames\data" /grant "IIS AppPool\DefaultAppPool:(OI)(CI)M"
   ```

4. **Verify** the URL Rewrite module is installed — open IIS Manager and look
   for the *URL Rewrite* icon on the server or site level.

5. Browse to `http://<your-server>/index.html`.

### How it works

| File | Purpose |
|------|---------|
| `web.config` | Tells IIS to route `/api/highscores/{key}` → `api/highscores.php` and blocks direct access to `data/` |
| `api/highscores.php` | PHP handler — reads/writes `data/{key}.json`; mirrors the Python server API |
| `data/` | JSON files written here (one file per score key) |

The `web.config` also registers `index.html` as the default document and adds
the correct MIME type for `.json` files.

> **Note:** If PHP is not available on your IIS server you can still run
> the Python server locally, or adapt `api/highscores.php` to an ASP /
> ASP.NET handler following the same GET / POST contract.
