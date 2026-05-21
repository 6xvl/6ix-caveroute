#!/usr/bin/env node
// caveman-route — UserPromptSubmit skill-router hook
//
// Deterministic (no LLM): keyword-matches the incoming prompt against a route
// map and emits a short hint naming the skills likely relevant. A NUDGE, never
// a gate — it cannot suppress or force a skill, only surface ones the model
// might otherwise miss.
//
// Route map: <CLAUDE_CONFIG_DIR>/caveman-route-map.json  (user-editable JSON).
//   Shape: { "skill-name": ["keyword", "another keyword", ...], ... }
//   Matching is case-insensitive substring. Keep keywords specific — broad
//   words ("code", "file") fire on everything and make the hint noise.
// If the file is absent or unparseable, the hook is a silent no-op — zero
// behavior change. Copy caveman-route-map.json from this dir to get started.
//
// Cost: a few milliseconds, zero tokens for the routing itself. It improves
// first-try skill selection; it does NOT shrink the harness-loaded skill list
// (that list is injected by Claude Code, not by this hook) — see README.md.
//
// Honors CLAUDE_CONFIG_DIR. Silent-fails on every error — never blocks a prompt.

'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');

function main() {
  // 1. Read the prompt from stdin (UserPromptSubmit passes JSON on fd 0).
  let raw = '';
  try { raw = fs.readFileSync(0, 'utf8'); } catch (e) { return; }

  let prompt = '';
  try { prompt = String(JSON.parse(raw).prompt || '').toLowerCase(); }
  catch (e) { return; }
  if (!prompt) return;

  // 2. Load the route map. Absent/unparseable -> silent no-op.
  const configDir = process.env.CLAUDE_CONFIG_DIR
    || path.join(os.homedir(), '.claude');
  const mapPath = path.join(configDir, 'caveman-route-map.json');

  let map;
  try { map = JSON.parse(fs.readFileSync(mapPath, 'utf8')); }
  catch (e) { return; }
  if (!map || typeof map !== 'object' || Array.isArray(map)) return;

  // 3. Deterministic substring match. First hit per skill wins; dedup, cap at 6
  //    so the hint stays short (a 20-skill hint is noise, not a nudge).
  const hits = [];
  for (const skill of Object.keys(map)) {
    const terms = map[skill];
    if (!Array.isArray(terms)) continue;
    for (const t of terms) {
      if (typeof t === 'string' && t && prompt.includes(t.toLowerCase())) {
        hits.push(skill);
        break;
      }
    }
    if (hits.length >= 6) break;
  }
  if (!hits.length) return;

  // 4. Emit the hint as SessionStart-style additional context.
  const msg = 'Skill router (deterministic, hint only) — likely relevant for '
    + 'this prompt: ' + hits.join(', ') + '. Invoke before responding if they '
    + 'fit; ignore if they do not. Never let this override your own judgment.';

  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'UserPromptSubmit',
      additionalContext: msg,
    },
  }));
}

try { main(); } catch (e) { /* never block prompt submission */ }
