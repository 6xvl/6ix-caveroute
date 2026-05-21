---
name: caveman-why
description: >
  Expand the most recent caveman-compressed answer back into full, normal prose.
  Use when a terse reply was ambiguous, dropped needed context, or the user says
  "caveman-why", "explain that fully", "expand that", "decompress", "what did
  that mean", or invokes /caveman-why. One-shot — does not change caveman mode.
---

Re-render your most recent response in full, uncompressed prose.

## What to do

Take the answer you just gave in caveman mode and rewrite it as if caveman mode
were off:

- Restore articles, conjunctions, and complete sentences.
- Restore the context and reasoning that compression dropped — the *why*, not
  just the *what*.
- Expand abbreviations back to full words (DB -> database, fn -> function).
- Keep every technical fact, value, code block, and error string **exactly** as
  it was. Code and quoted output were never compressed — leave them untouched.

## Hard rules

- **Decompress only. Do not add new information.** If the terse answer was
  wrong or incomplete, say so plainly — do not silently "fix" it under cover of
  expanding it.
- **Do not re-run tools or re-derive anything.** This is a rewrite of an answer
  already given, not a fresh attempt.
- If there is no recent caveman answer to expand (caveman was off, or this is
  the first turn), say so and ask what the user wants explained.
- This is **one-shot**. It does not turn caveman off — the next answer returns
  to the active caveman level. To actually disable caveman, the user says
  "stop caveman" / "normal mode".

## Why this exists

caveman trades words for tokens. Usually that is fine. Occasionally a fragment
is genuinely ambiguous, or the reader needs the dropped reasoning. `/caveman-why`
is the escape hatch: it recovers the full explanation without losing the token
savings on every *other* turn.
