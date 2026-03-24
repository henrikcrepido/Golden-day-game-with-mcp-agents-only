# Instructions — Building a Standalone Browser Game with MCP Agents

> Derived from the Minesweeper build session (2026-03-21).  
> Use this document as a step-by-step guide when an MCP coding agent is asked to build a self-contained browser game.

---

## 1 · Understand the Requirement First

Before writing any code:

1. Read the full problem statement and any linked issues or comments.
2. List what "standalone in a browser" means concretely:
   - Single file preferred (`*.html` with embedded CSS + JS).
   - No build step, no package manager, no CDN.
   - Must open directly from `file://` **or** a plain HTTP server.
3. Identify the **core game mechanics** you must implement (e.g. for Minesweeper: reveal, flag, flood-fill, chord, win/lose).
4. Explore the repository — check for existing files, linting, build, or test tooling before touching anything.

---

## 2 · Plan Before Coding

Use `report_progress` with a checklist **before making any file changes**.  
A good checklist for a browser game contains:

```
- [ ] Create `<game>.html` with embedded CSS + JS
- [ ] Core game logic (board init, mine placement, reveal algorithm)
- [ ] User interaction (click handlers, context menu for flags)
- [ ] Win/lose detection and display
- [ ] HUD (score, timer, lives, etc.)
- [ ] Difficulty / configuration options
- [ ] New Game / restart
- [ ] Visual verification (screenshot)
- [ ] Code review
- [ ] Security scan
```

---

## 3 · Architecture for a Single-File Browser Game

Structure the HTML file in this order:

```
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Game Name</title>
  <style>
    /* All CSS here */
  </style>
</head>
<body>
  <!-- All HTML markup here -->
  <script>
    /* ── Configuration constants ───────────────────── */
    /* ── Game state variables ──────────────────────── */
    /* ── DOM references (cached at top of script) ──── */
    /* ── Helper / utility functions ────────────────── */
    /* ── Game initialisation ────────────────────────── */
    /* ── Core game logic ────────────────────────────── */
    /* ── Event handlers ─────────────────────────────── */
    /* ── Boot ───────────────────────────────────────── */
    initGame();
  </script>
</body>
</html>
```

Key rules:
- Cache **all** `document.getElementById` calls in `const` variables at the top of `<script>`.
- Keep state in module-level variables (not inside DOM).
- Separate *logic* (pure functions) from *rendering* (DOM updates).
- Never call `innerHTML` with user-supplied input — use `textContent` or `createElement`.

---

## 4 · Implementing Core Mechanics

### 4a · Grid / Board Initialisation

- Build a 2-D array of cell objects (e.g. `{ mine, revealed, flagged, adjacent, el }`).
- Create DOM elements in a second pass and attach them to the data objects via `cell.el = el`.
- Use CSS Grid for layout: `grid-template-columns: repeat(${cols}, ${cellSize}px)`.

### 4b · Randomised Placement (mines, obstacles, etc.)

- **Safe first click**: defer random placement until after the first player interaction.
- Mark a "safe zone" (usually a 3×3 around the clicked cell) before placing hazards.
- Use a `Set` of linear indices (`row * cols + col`) for O(1) safe-zone lookup.

### 4c · Flood-Fill / Cascade Reveal

```js
function revealCell(r, c) {
  const cell = grid[r][c];
  if (cell.revealed || cell.flagged) return;
  cell.revealed = true;
  // update DOM …
  if (cell.adjacentCount === 0) {
    for (let dr = -1; dr <= 1; dr++)
      for (let dc = -1; dc <= 1; dc++) {
        const nr = r + dr, nc = c + dc;
        if (inBounds(nr, nc)) revealCell(nr, nc);
      }
  }
}
```

This is safe for grids up to ~32×32 (recursion depth stays below 1 000).

### 4d · Win / Lose Detection

- Check win after every reveal: `revealedCount === rows * cols - hazardCount`.
- Trigger lose immediately when a hazard cell is revealed.
- Add a short `setTimeout` (e.g. 600 ms) before showing a win/lose overlay so the player sees the final board state first.

---

## 5 · Styling — Modern 3D Look-and-Feel

To achieve a modern dark-theme 3D game aesthetic with pure CSS — no images required:

```css
/* ── Background ───────────────────────────────────────── */
body {
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}

/* ── 3D raised tile (unrevealed cell) ─────────────────── */
.cell {
  background: linear-gradient(145deg, #5a52b0 0%, #3d3690 40%, #2e2870 100%);
  box-shadow:
    0 4px 0 rgba(0,0,0,0.55),          /* hard bottom shadow = depth */
    inset 0 1px 0 rgba(255,255,255,0.25),  /* top highlight */
    inset -1px -1px 0 rgba(0,0,0,0.3); /* bottom-right inner shadow */
  border-radius: 5px;
  transition: transform 0.08s ease, box-shadow 0.08s ease;
}

/* Hover: lift with glow */
.cell:not(.revealed):hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow:
    0 7px 0 rgba(0,0,0,0.5),
    0 0 12px rgba(99,179,237,0.4),
    inset 0 1px 0 rgba(255,255,255,0.35);
}

/* Press: depress */
.cell:not(.revealed):active {
  transform: translateY(2px) scale(0.97);
  box-shadow: 0 1px 0 rgba(0,0,0,0.6), inset 0 2px 4px rgba(0,0,0,0.4);
}

/* ── Key animations ────────────────────────────────────── */
@keyframes revealFlip {
  0%   { transform: rotateX(90deg) scale(0.85); opacity: 0; }
  60%  { transform: rotateX(-10deg) scale(1.05); opacity: 1; }
  100% { transform: rotateX(0deg) scale(1); }
}

@keyframes flagBounce {
  0%   { transform: scale(0) rotate(-30deg); }
  50%  { transform: scale(1.3) rotate(10deg); }
  100% { transform: scale(1) rotate(0deg); }
}

@keyframes mineBlast {
  0%   { transform: scale(1);    background: #ff4444; }
  40%  { transform: scale(1.35); background: #ff8800; box-shadow: 0 0 0 14px rgba(255,80,0,0.4); }
  100% { transform: scale(1);    background: #cc2200; }
}
```

Number colours — vivid with matching `text-shadow` glow:
1=`#63b3ed`, 2=`#68d391`, 3=`#fc8181`, 4=`#b794f4`, 5=`#f6ad55`, 6=`#4fd1c5`, 7=`#f687b3`, 8=`#a0aec0`

Apply `perspective: 800px` to `#board` so child elements can participate in 3D space.

### Classic Look-and-Feel (original Windows 95 style)

To reproduce the Windows 3.x / classic Minesweeper aesthetic with pure CSS — no images required:

```css
/* Raised panel (button, container) */
.raised {
  background: #c0c0c0;
  border-top:   3px solid #fff;
  border-left:  3px solid #fff;
  border-right: 3px solid #808080;
  border-bottom: 3px solid #808080;
}

/* Sunken / revealed cell */
.sunken {
  border-top:   1px solid #999;
  border-left:  1px solid #999;
  border-right: 1px solid #bbb;
  border-bottom: 1px solid #bbb;
}

/* LED-style display */
.led-display {
  background: #000;
  color: #f00;
  font-family: 'Courier New', monospace;
  font-weight: bold;
  padding: 2px 6px;
  border-top:   2px solid #808080;
  border-left:  2px solid #808080;
  border-right: 2px solid #fff;
  border-bottom: 2px solid #fff;
}
```

Classic number colours for Minesweeper: 1=blue, 2=green, 3=red, 4=dark-blue, 5=dark-red, 6=teal, 7=black, 8=grey.

---

## 6 · Testing & Verification

Since there is no existing test infrastructure in this repo, perform manual verification:

1. **Start a local HTTP server** (avoids `file://` CORS issues):
   ```bash
   python3 -m http.server 8765 --directory .
   ```
2. **Navigate with Playwright** to `http://localhost:8765/<game>.html`.
3. **Take a screenshot** immediately after load (initial state).
4. **Simulate a click** via `page.evaluate()` and confirm:
   - State variables updated (`revealedCount`, `gameState`).
   - DOM reflects new state (classes, text content).
   - Timer started.
5. **Take a second screenshot** after the click (mid-game state).
6. **Test win/lose paths** by manipulating state in `evaluate()` if needed.

---

## 7 · Code Review & Security

Before finalising:

1. Call `code_review` — address all naming-clarity, logic, and style comments.
2. Call `codeql_checker` — fix any flagged alerts; pure HTML/JS files may show "no languages analysed" which is expected and acceptable.
3. Grep for any stale references left by renames.

---

## 8 · Commit & Push

Use `report_progress` with a final checklist:

```markdown
- [x] `<game>.html` created (embedded CSS + JS, no dependencies)
- [x] Core mechanics implemented and verified
- [x] Visual verification (screenshots taken)
- [x] Code review feedback addressed
- [x] Security scan clean
```

Commit message format:  
`Add standalone <GameName> game (<filename>.html)`

---

## 9 · Timing Reference (from Minesweeper session)

| Phase | Approx. Time |
|-------|-------------|
| Understand requirements + explore repo | 1–2 min |
| Plan + first `report_progress` | 30 s |
| Write complete game code (600 lines) | 1.5 min |
| Browser verification (2 rounds) | 1 min |
| Code review + apply fixes | 1.5 min |
| Security scan | 15 s |
| Final commit + push | 15 s |
| **Total** | **~5–6 min** |

---

## 10 · Checklist Template (copy-paste for new sessions)

```markdown
- [ ] Explore repo (README, existing files, tooling)
- [ ] Report initial plan
- [ ] Create `<game>.html` — embedded CSS + JS, no dependencies
- [ ] Board/grid initialisation
- [ ] Randomised placement with first-click safety
- [ ] Core reveal / action logic (flood-fill if applicable)
- [ ] Win/lose detection
- [ ] HUD (score, timer, counters)
- [ ] Difficulty / config options
- [ ] New Game / restart button
- [ ] Visual verification — screenshot initial state
- [ ] Gameplay test — simulate interaction, screenshot result
- [ ] Code review (`code_review` tool)
- [ ] Apply review feedback
- [ ] Security scan (`codeql_checker`)
- [ ] Final commit + push (`report_progress`)
```


---

## Appendix — IIS Deployment Guide (added 2026-03-24)

The `/api/highscores/{key}` REST API is provided by `server.py` when running
locally with Python.  For IIS hosting:

1. Ensure the IIS URL Rewrite module and PHP FastCGI handler are installed.
2. Deploy all files to the IIS site root (no build step needed).
3. Grant the application-pool identity **Modify** access to the `data\` folder.
4. The `web.config` in the repository root takes care of routing and MIME types.

### Key files

| File | Role |
|------|------|
| `web.config` | IIS configuration (URL Rewrite, defaultDocument, security) |
| `api/highscores.php` | PHP replacement for the Python highscores API |
| `data/` | Runtime JSON files written here (one per score key) |

### URL contract (unchanged)

```
GET  /api/highscores/{key}   → 200 application/json  ([] if not found)
POST /api/highscores/{key}   → 200 {"ok":true}        (body: JSON array)
```

Both the Python server and the PHP handler honour the same contract, so no
changes to the HTML game files are required when switching between the two.
