"""Tests for deslop scoring logic."""

from deslop.scorer import score_text, score_label, word_count


def test_sloppy_text_scores_lower_than_clean():
    """Text full of AI patterns should score much lower than normal writing."""
    sloppy = (
        "It is worth noting that we must delve into the tapestry of this landscape. "
        "The result? A robust, comprehensive, and holistic framework. "
        "It's not a tool — it's a paradigm shift. "
        "Only time will tell if this groundbreaking ecosystem succeeds."
    )
    clean = (
        "The database migration took four hours. We updated the schema, "
        "ran the backfill script, and verified row counts matched. "
        "No data was lost during the process."
    )
    sloppy_score, sloppy_matches = score_text(sloppy)
    clean_score, clean_matches = score_text(clean)
    assert sloppy_score < clean_score
    assert len(sloppy_matches) > len(clean_matches)


def test_empty_string_scores_perfect():
    """Empty input should return a perfect score with no matches."""
    score, matches = score_text("")
    assert score == 100
    assert matches == []


def test_single_word():
    """A single non-slop word should score perfectly."""
    score, matches = score_text("Hello")
    assert score == 100
    assert matches == []


def test_long_clean_text_scores_high():
    """A longer piece of normal writing should still score high."""
    paragraphs = [
        "The API returns JSON responses with standard HTTP status codes.",
        "Error responses include a message field describing what went wrong.",
        "Authentication uses bearer tokens passed in the Authorization header.",
        "Rate limiting is set to 100 requests per minute per API key.",
        "The SDK handles retries automatically with exponential backoff.",
        "Pagination uses cursor-based tokens returned in the response body.",
    ]
    text = " ".join(paragraphs)
    score, matches = score_text(text)
    assert score >= 85


def test_score_label_ranges():
    """score_label should return the correct label for each range."""
    assert "human" in score_label(90)
    assert "clean" in score_label(75)
    assert "needs work" in score_label(55)
    assert "heavy slop" in score_label(35)
    assert "robot" in score_label(10)


def test_word_count_basic():
    """word_count should count space-separated tokens."""
    assert word_count("one two three") == 3
    assert word_count("") == 0
    assert word_count("single") == 1
