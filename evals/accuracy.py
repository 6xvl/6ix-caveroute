"""
Accuracy-retention screen for caveman compression.

evals/measure.py answers "how many tokens did the skill save?" It does NOT
answer "did the answer stay correct?". A skill that compresses 90% but drops a
function name, a number, or a config key has not saved tokens; it has produced
a wrong answer cheaply.

This script is a *screen*, not a grader. It measures how many of the technical
tokens (numbers, inline `code` spans, snake_case / camelCase / PascalCase
identifiers, API names, ALL_CAPS terms) found in the **terse control** answer
also appear in the skill's answer.

Why the terse control, not the verbose baseline? The baseline is long and
mentions everything; a correct *concise* answer legitimately omits detail, so
scoring against baseline would punish conciseness, not error. The terse arm
("Answer concisely.") is already concise — so a technical token the terse arm
kept but the skill dropped is the skill's *compression* losing content, not
mere brevity.

Fenced ``` code blocks are excluded: caveman keeps code verbatim by rule, and
prose is where compression actually risks dropping facts.

This is a heuristic. A low score is a signal to READ the prompt, not an
automatic failure — the skill may phrase the same fact with a different token.
A true grader needs an LLM judge; this screen only points. Pair it with
measure.py: measure.py = how short, this = how honest.

Run: uv run python evals/accuracy.py   (stdlib only)
"""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

SNAPSHOT = Path(__file__).parent / "snapshots" / "results.json"

# Screening line. Prompts below are listed for human review — NOT auto-failed.
THRESHOLD = 0.80

_FENCE = re.compile(r"```.*?```", re.DOTALL)
_PATTERNS = [
    re.compile(r"`[^`\n]+`"),                        # inline `code` spans
    re.compile(r"\b\d+(?:\.\d+)?\b"),                # numbers
    re.compile(r"\b[A-Za-z]+_[A-Za-z0-9_]+\b"),      # snake_case / SCREAMING
    re.compile(r"\b[a-z]+[A-Z][A-Za-z0-9]*\b"),      # camelCase
    re.compile(r"\b[A-Z][a-z]+[A-Z][A-Za-z0-9]*\b"), # PascalCase
    re.compile(r"\b[A-Z]{2,}\b"),                    # ALL_CAPS terms (>= 2)
]


def technical_tokens(text: str) -> set[str]:
    """Technical tokens in the PROSE of text (fenced code blocks excluded)."""
    prose = _FENCE.sub(" ", text)
    toks: set[str] = set()
    for pat in _PATTERNS:
        for m in pat.findall(prose):
            t = m.strip("`").strip().lower()
            if t:
                toks.add(t)
    return toks


def retention(reference: str, compressed: str) -> tuple[float, set[str]]:
    """Fraction of the reference's technical tokens surviving in compressed."""
    ref = technical_tokens(reference)
    if not ref:
        return 1.0, set()
    dropped = ref - technical_tokens(compressed)
    return (len(ref) - len(dropped)) / len(ref), dropped


def main() -> None:
    if not SNAPSHOT.exists():
        print(f"No snapshot at {SNAPSHOT}. Run `python evals/llm_run.py` first.")
        return

    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    arms = data["arms"]
    terse = arms.get("__terse__")
    if not terse:
        print("No __terse__ control arm in results.json — cannot screen.")
        return

    print("# Accuracy-retention screen — technical-token survival vs the terse control")
    print()
    print(f"_n = {len(terse)} prompts. Reference = `__terse__` arm. Fenced code "
          f"excluded. Screening line {THRESHOLD * 100:.0f}% — below = review, "
          f"not fail._")
    print()
    print("| Skill | Median | Mean | Min | Below line |")
    print("|-------|--------|------|-----|------------|")

    flagged: list[str] = []
    for skill, outputs in arms.items():
        if skill in ("__baseline__", "__terse__"):
            continue
        rates: list[float] = []
        for i, out in enumerate(outputs):
            if i >= len(terse):
                break
            rate, dropped = retention(terse[i], out)
            rates.append(rate)
            if rate < THRESHOLD:
                shown = sorted(dropped)[:12]
                more = f" (+{len(dropped) - 12} more)" if len(dropped) > 12 else ""
                flagged.append(
                    f"  - {skill} / prompt {i}: {rate * 100:.0f}% — dropped: "
                    f"{', '.join(shown)}{more}"
                )
        if not rates:
            continue
        below = sum(1 for r in rates if r < THRESHOLD)
        print(f"| **{skill}** | {statistics.median(rates) * 100:.0f}% | "
              f"{statistics.mean(rates) * 100:.0f}% | {min(rates) * 100:.0f}% | "
              f"{below} |")

    print()
    if flagged:
        print("## Below the screening line — read these prompts")
        print()
        print("\n".join(flagged))
        print()
        print("For each: open the prompt's terse vs skill answer. If a dropped "
              "token was load-bearing, compression lost correctness. If the "
              "skill merely used a synonym, the flag is a false positive — this "
              "screen only points; confirming needs a human or an LLM judge.")
    else:
        print("Nothing below the screening line — compression kept the terse "
              "control's technical tokens.")
    print()
    print(f"_Source: {SNAPSHOT.name}. Heuristic screen — pair with measure.py._")


if __name__ == "__main__":
    main()
