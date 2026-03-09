"""
Scoring logic for deslop.

Score = 0–100 where 100 is "very human" and 0 is "pure slop".
Penalizes based on the number and severity of pattern matches relative
to document length.
"""

from __future__ import annotations

from .patterns import Match, check_text


# Severity weights for penalty calculation
SEVERITY_WEIGHT = {1: 1, 2: 3, 3: 6}

# Penalty per 100 words for a single hit (by severity)
PENALTY_PER_100_WORDS = {1: 2.0, 2: 5.0, 3: 10.0}


def word_count(text: str) -> int:
    return len(text.split())


def score_text(text: str) -> tuple[int, list[Match]]:
    """
    Compute humanness score (0–100) and return (score, matches).

    Algorithm:
    1. Count all matches by severity
    2. Compute weighted penalty per 100 words
    3. Map to 0–100 scale (starts at 100, subtract penalties, floor at 0)
    """
    matches = check_text(text)
    wc = max(word_count(text), 1)

    # Deduplicate: same line+pattern counts once
    seen = set()
    unique_matches = []
    for m in matches:
        key = (m.line_number, m.pattern_name, m.matched_text.lower()[:30])
        if key not in seen:
            seen.add(key)
            unique_matches.append(m)

    # Calculate raw penalty
    total_penalty = 0.0
    for m in unique_matches:
        weight = PENALTY_PER_100_WORDS.get(m.severity, 1.0)
        # Normalize by document length: a 1000-word doc with 5 hits is worse
        # than a 5000-word doc with 5 hits
        total_penalty += weight * (100 / wc)

    # Scale: a penalty of 100 (10 severe hits in a 100-word doc) → score of 0
    # Cap at 100 penalty points → 0 score
    score = max(0, round(100 - total_penalty * 4))
    score = min(100, score)

    return score, unique_matches


def score_label(score: int) -> str:
    if score >= 85:
        return "looks human ✓"
    elif score >= 70:
        return "mostly clean"
    elif score >= 50:
        return "needs work"
    elif score >= 30:
        return "heavy slop"
    else:
        return "robot detected 🤖"
