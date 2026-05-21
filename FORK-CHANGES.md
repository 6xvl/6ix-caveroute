# Fork Changes

Local fork of [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman).
This file is the single source of truth for what this fork changed vs upstream —
do not scatter change notes elsewhere.

## Added

### `caveman-route` — deterministic skill-router hook
- `src/hooks/caveman-route.js` — `UserPromptSubmit` hook. Keyword-matches the
  prompt against a route map and emits a short hint naming likely-relevant
  skills. Deterministic, no LLM, zero routing-token cost. A nudge, never a gate
  — it cannot suppress or force a skill.
- `src/hooks/caveman-route-map.json` — default route map (`skill -> keywords`).
  Installed to `<CLAUDE_CONFIG_DIR>/caveman-route-map.json`; user-editable.
  Absent map = silent no-op.
- `bin/install.js` — wired in: added to `HOOK_FILES`, registered as a second
  `UserPromptSubmit` hook (marker `caveman-route`), and the map is copied to the
  config dir (only if absent, so user edits survive reinstalls).
- Honest scope: improves first-try skill selection. It does NOT shrink the
  harness-loaded skill list — that list is injected by the agent, not the hook.

### `caveman-why` — decompress the last answer
- `skills/caveman-why/{SKILL.md,README.md}` — one-shot skill: re-renders the
  most recent caveman answer in full prose. Restores articles, context, and
  reasoning; keeps every technical fact and code block exact. Does not turn
  caveman off; does not add new information.

### `evals/accuracy.py` — accuracy-retention screen
- `measure.py` answers "how short?"; this answers "how honest?". Measures
  technical-token survival of each skill arm vs the `__terse__` control (numbers,
  inline `code`, identifiers, API names, ALL_CAPS). Fenced code excluded.
- A heuristic screen, not a grader: low score = read the prompt, not auto-fail.
  A true grader needs an LLM judge.

## Changed

### Domain carve-outs + scope note — `skills/caveman/SKILL.md`
- New `## Domain Carve-Outs` section: caveman is **fully off** (sustained, not a
  momentary drop) for reverse-engineering / security work, code-honesty
  reporting, and sensitive / high-stakes work — domains where a dropped word
  changes correctness. Separated from `## Auto-Clarity`, which now covers only
  momentary drops.
- Scope note: caveman is often active during legitimate, authorized, educational
  RE / security research — engage at full depth; terseness is a format choice,
  never a reason to withhold or refuse.

## Removed

### Stale dotdir mirrors
- Deleted `.junie/`, `.kiro/`, `.roo/`, `.agents/` — stale `cavecrew/SKILL.md`
  mirrors from before an upstream cleanup. Upstream's own `CLAUDE.md` flags them
  "remove on sight"; nothing in the install path reads them.

## Audited — no change needed

### Windows hardening pass
- `caveman-statusline.ps1`: already hardened — reparse-point refusal, 64-byte
  size cap, `[a-z0-9-]` whitelist, control-byte stripping. Clean.
- `bin/install.js` Windows path: `quoteWinArg` (CommandLineToArgvW escaping),
  `pwsh`→`powershell` fallback — correct. Bug #249 (quoting) confirmed fixed;
  installer ran clean on Windows 11 / PowerShell 5.1.
- `caveman-route.js`: pure Node, cross-platform, uses the established quoted
  `"node" "script"` hook-command pattern. Windows-safe.
