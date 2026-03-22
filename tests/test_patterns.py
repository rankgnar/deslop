"""Tests for deslop pattern detection."""

from deslop.patterns import check_text, check_line, Match


def test_detects_overused_words():
    """Known AI-overused words should be flagged."""
    text = "Let us delve into the tapestry of this landscape."
    matches = check_text(text)
    matched_words = {m.matched_text.lower() for m in matches}
    assert "delve" in matched_words
    assert "tapestry" in matched_words
    assert "landscape" in matched_words


def test_detects_empty_transitions():
    """Filler transition phrases should be caught."""
    text = "It's worth noting that this approach works well."
    matches = check_text(text)
    pattern_names = {m.pattern_name for m in matches}
    assert "empty transition" in pattern_names


def test_detects_negative_parallelism():
    """'It's not X — it's Y' false-profundity framing should be flagged."""
    text = "It's not a bug — it's a feature that changes everything."
    matches = check_text(text)
    pattern_names = {m.pattern_name for m in matches}
    assert "negative parallelism" in pattern_names


def test_detects_rhetorical_self_question():
    """Self-posed rhetorical questions should be caught."""
    text = "The result? A complete transformation of the industry."
    matches = check_text(text)
    pattern_names = {m.pattern_name for m in matches}
    assert "rhetorical self-question" in pattern_names


def test_detects_closing_platitudes():
    """Generic closing statements should be flagged."""
    text = "Only time will tell whether this approach succeeds."
    matches = check_text(text)
    pattern_names = {m.pattern_name for m in matches}
    assert "closing platitude" in pattern_names


def test_clean_text_returns_no_matches():
    """Plain, normal writing should not trigger patterns."""
    text = (
        "The server crashed at 3am because the disk was full. "
        "We added log rotation and increased the volume size. "
        "After deploying the fix, uptime returned to normal."
    )
    matches = check_text(text)
    assert len(matches) == 0


def test_detects_hedging_overload():
    """Excessive epistemic hedging should be detected."""
    text = "It seems like this could be one of the most important changes."
    matches = check_text(text)
    pattern_names = {m.pattern_name for m in matches}
    assert "hedge overload" in pattern_names


def test_detects_punchy_fragments():
    """Short isolated sentences used for false emphasis should be caught."""
    text = "We built the system from scratch.\n\nAnd it worked.\n\nThe team was excited."
    matches = check_text(text)
    pattern_names = {m.pattern_name for m in matches}
    assert "punchy fragment" in pattern_names


def test_detects_in_conclusion_marker():
    """In-conclusion essay closers should be flagged."""
    text = "In conclusion, this approach works."
    matches = check_text(text)
    pattern_names = {m.pattern_name for m in matches}
    assert "in-conclusion marker" in pattern_names


def test_detects_throat_clearing():
    """Throat-clearing filler openers should be flagged."""
    text = "With that said, let us move on."
    matches = check_text(text)
    pattern_names = {m.pattern_name for m in matches}
    assert "throat-clearing opener" in pattern_names


def test_detects_as_we_can_see():
    """As-we-can-see condescending references should be flagged."""
    text = "As we can see from the results above."
    matches = check_text(text)
    pattern_names = {m.pattern_name for m in matches}
    assert "as-we-can-see" in pattern_names


def test_detects_moving_forward():
    """Moving-forward temporal filler should be flagged."""
    text = "Moving forward, we will focus on growth."
    matches = check_text(text)
    pattern_names = {m.pattern_name for m in matches}
    assert "moving-forward filler" in pattern_names


def test_match_contains_line_number():
    """Matches should report correct line numbers."""
    text = "Line one is fine.\nThis line will delve into things."
    matches = check_text(text)
    delve_matches = [m for m in matches if m.matched_text.lower() == "delve"]
    assert len(delve_matches) == 1
    assert delve_matches[0].line_number == 2
