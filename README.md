# 6ix-caveroute

> **caveman, plus a deterministic skill router and domain carve-outs.**
> Cut AI-agent output tokens by ~65% — *without* compressing the things that
> must stay precise.

A fork of **[caveman](https://github.com/JuliusBrussee/caveman)** by Julius
Brussee. caveman makes AI coding agents (Claude Code, Codex, Gemini CLI, Cursor,
and 30+ others) answer in compressed "caveman" prose — roughly 65% fewer output
tokens at full technical accuracy, per upstream's measured benchmarks.
`6ix-caveroute` keeps every bit of that and adds four things caveman didn't have.

---

## What this fork adds

### 🧭 caveman-route — a deterministic skill router

Every coding agent ships dozens of skills, and the model has to notice which one
applies. `caveman-route` is a `UserPromptSubmit` hook that keyword-matches each
prompt against a route map and emits a short hint naming the likely-relevant
skills.

- **Deterministic** — no LLM call, no token cost for the routing itself.
- **A nudge, never a gate** — it surfaces skills the model might miss; it cannot
  suppress or force one.
- **Silent when it has nothing to say** — no route map, or no match, means no
  output and zero behavior change.

```
prompt: "reverse engineer this packed binary and find the offset"
  -> hint: likely relevant — re, decompiling-protected-binaries
```

The route map (`caveman-route-map.json`) is plain, user-editable JSON: skill
name → keywords. Ships with a sensible default; tune it to your own skill set.

### 🛡️ Domain carve-outs — never compress what must stay precise

Compression is lossy by design. `6ix-caveroute` makes that explicit: caveman is
turned **fully off** — sustained, not a momentary drop — for the domains where a
dropped word changes correctness:

- **Reverse-engineering & security** — full evidence depth: offsets, raw bytes,
  citations, step-by-step reasoning.
- **Code-honesty reporting** — test results, what a change actually does vs. what
  was claimed, verification output, error messages. Quoted in full.
- **Sensitive / high-stakes work** — anywhere an omitted word flips the answer.

Everywhere else, caveman runs as normal and saves the tokens.

### 📊 Accuracy-retention eval

Upstream's `evals/measure.py` answers *how short?*. The new `evals/accuracy.py`
answers *how honest?* — it measures technical-token survival (identifiers,
numbers, API names) against the terse control, so a compression that quietly
drops a function name shows up instead of hiding behind a great token score.
A heuristic screen, not a grader — pair the two.

### 🔎 /caveman-why

One-shot escape hatch: expand the most recent compressed answer back into full
prose, restoring the dropped context and reasoning — without losing the token
savings on every other turn.

---

## Install

```bash
git clone https://github.com/6xvl/6ix-caveroute.git
cd 6ix-caveroute
node bin/install.js --only claude --with-hooks
```

Node ≥ 18 required. The installer wires the hooks (including `caveman-route`)
into Claude Code and copies the route map to your config dir. Works on macOS,
Linux, and Windows. `caveman-route` stays a silent no-op until a
`caveman-route-map.json` exists in your Claude config directory — the installer
seeds one for you.

To remove: `node bin/install.js --uninstall`.

For the full caveman feature set — intensity levels, the per-agent install
matrix for 30+ tools, and the upstream token benchmarks — see the
[upstream caveman repo](https://github.com/JuliusBrussee/caveman).

See [`FORK-CHANGES.md`](./FORK-CHANGES.md) for the complete, file-by-file diff
against upstream.

---

## Credits & license

`6ix-caveroute` is a fork of [**caveman**](https://github.com/JuliusBrussee/caveman)
by **Julius Brussee** — all credit for caveman, its compression engine, hook
architecture, and multi-agent installer goes to the upstream project.

Licensed under the **MIT License** — the upstream `LICENSE` (Copyright © Julius
Brussee) is retained in full. The fork's additions are released under the same
MIT terms.

If caveman saves you tokens, [support the upstream
author](https://github.com/sponsors/safishamsi).

---

<sub>Tags: claude code · claude skills · ai agents · token optimization · llm ·
prompt engineering · codex · gemini cli · cursor</sub>
