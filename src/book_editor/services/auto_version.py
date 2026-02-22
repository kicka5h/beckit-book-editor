"""Classify a chapter edit as major, minor, patch, or None (trivial) using local diff heuristics."""

import difflib
import re
from collections import Counter
from typing import Optional


def classify_change(old_text: str, new_text: str) -> Optional[str]:
    """Return 'major', 'minor', 'patch', or None (no meaningful change).

    Rules (first match wins):
      None  — word_delta < 5 AND changed_line_ratio < 0.05
      major — H1/H2 heading set changed  OR  word_delta > 20% of old word count
               OR a Title-Case word appearing ≥3 times is introduced or removed
                  (heuristic for new/removed character)
      minor — word_delta > 30  OR  changed_line_ratio > 0.15
      patch — any other meaningful edit
    """
    old_words = old_text.split()
    new_words = new_text.split()
    word_delta = abs(len(new_words) - len(old_words))

    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()

    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
    changed_lines = sum(
        1 for line in diff
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    )
    total_lines = max(len(old_lines), len(new_lines), 1)
    changed_line_ratio = changed_lines / total_lines

    # ── None threshold ────────────────────────────────────────────────────────
    if word_delta < 5 and changed_line_ratio < 0.05:
        return None

    # ── Major: H1/H2 heading structure changed ────────────────────────────────
    old_headings = frozenset(l for l in old_lines if re.match(r"^#{1,2} ", l))
    new_headings = frozenset(l for l in new_lines if re.match(r"^#{1,2} ", l))
    if old_headings != new_headings:
        return "major"

    # ── Major: >20% word count change ─────────────────────────────────────────
    if old_words and word_delta > len(old_words) * 0.20:
        return "major"

    # ── Major: new or removed recurring Title-Case word (character heuristic) ─
    def _recurring_proper_nouns(words):
        return {
            w for w, count in Counter(words).items()
            if count >= 3 and w[0].isupper() and w.isalpha()
        }

    if _recurring_proper_nouns(old_words).symmetric_difference(
        _recurring_proper_nouns(new_words)
    ):
        return "major"

    # ── Minor ─────────────────────────────────────────────────────────────────
    if word_delta > 30 or changed_line_ratio > 0.15:
        return "minor"

    # ── Patch ─────────────────────────────────────────────────────────────────
    return "patch"
