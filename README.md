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

---

## 📄 Documentation

| File | Purpose |
|------|---------|
| [`AGENT_LOG.md`](AGENT_LOG.md) | Timestamped log of every action taken during the Minesweeper build session, including decision rationale |
| [`INSTRUCTIONS.md`](INSTRUCTIONS.md) | Reusable step-by-step instructions for future agents building standalone browser games |

---

## 🚀 Running a game locally

```bash
python3 -m http.server 8080
# then open http://localhost:8080/minesweeper.html
```

Or simply double-click the `.html` file — it works from `file://` too.
