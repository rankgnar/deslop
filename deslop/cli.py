"""
deslop CLI entry point.

Commands:
    deslop check <file>         — show detected slop patterns with line numbers
    deslop check --stdin        — read from stdin (pipe-friendly)
    deslop score <file>         — print humanness score 0–100
    deslop fix <file>           — placeholder for future LLM rewrite
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click

from .patterns import check_text, Match
from .scorer import score_text, score_label

# ─── ANSI colour helpers (no extra deps) ────────────────────────────────────

def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
DIM    = "\033[2m"
ORANGE = "\033[38;5;208m"


def _color(text: str, *codes: str) -> str:
    if not _supports_color():
        return text
    return "".join(codes) + text + RESET


def _severity_color(severity: int) -> str:
    return {1: YELLOW, 2: ORANGE, 3: RED}.get(severity, YELLOW)


def _print_match(m: Match, filename: str = "") -> None:
    prefix = f"{filename}:{m.line_number}" if filename else str(m.line_number)
    prefix_colored = _color(prefix, BOLD, CYAN)

    # Highlight the matched text within the line
    line_display = m.line_text
    if m.matched_text and m.matched_text in line_display:
        highlight = _color(m.matched_text, BOLD, _severity_color(m.severity))
        line_display = line_display.replace(m.matched_text, highlight, 1)

    click.echo(f"{prefix_colored} — \"{line_display}\"")

    pattern_colored = _color(m.pattern_name, BOLD, _severity_color(m.severity))
    desc_colored = _color(m.pattern_description, DIM)
    click.echo(f"  └─ Pattern: {pattern_colored}  {desc_colored}")
    click.echo()


def _print_score(score: int, match_count: int) -> None:
    label = score_label(score)
    if score >= 85:
        color = GREEN
    elif score >= 60:
        color = YELLOW
    else:
        color = RED

    score_str = _color(f"{score}/100", BOLD, color)
    label_str = _color(f"({label})", color)
    issues_str = _color(str(match_count), BOLD)
    click.echo(f"Score: {score_str} {label_str}  —  {issues_str} issue(s) found")


# ─── CLI ─────────────────────────────────────────────────────────────────────

@click.group()
@click.version_option(package_name="deslop")
def cli() -> None:
    """deslop — detect AI writing patterns (slop) in text."""


@cli.command()
@click.argument("file", required=False, type=click.Path(exists=True, readable=True))
@click.option("--stdin", "use_stdin", is_flag=True, help="Read text from stdin.")
@click.option("--no-score", is_flag=True, help="Skip printing the score summary.")
@click.option(
    "--min-severity",
    type=click.IntRange(1, 3),
    default=1,
    show_default=True,
    help="Only show patterns at or above this severity (1=mild, 2=moderate, 3=severe).",
)
def check(
    file: Optional[str],
    use_stdin: bool,
    no_score: bool,
    min_severity: int,
) -> None:
    """Analyze a file (or stdin) and show detected slop patterns."""
    if use_stdin:
        text = sys.stdin.read()
        filename = "<stdin>"
    elif file:
        text = Path(file).read_text(encoding="utf-8", errors="replace")
        filename = file
    else:
        raise click.UsageError("Provide a FILE argument or use --stdin.")

    score, matches = score_text(text)
    filtered = [m for m in matches if m.severity >= min_severity]

    if not filtered:
        click.echo(_color("✓ No slop patterns detected.", BOLD, GREEN))
    else:
        # Deduplicate for display: group by (line_number, pattern_name)
        seen_display: set[tuple] = set()
        display_matches = []
        for m in sorted(filtered, key=lambda x: (x.line_number, x.pattern_name)):
            key = (m.line_number, m.pattern_name)
            if key not in seen_display:
                seen_display.add(key)
                display_matches.append(m)
        for m in display_matches:
            _print_match(m, filename)

    if not no_score:
        _print_score(score, len(matches))

    # Exit code: 0 = clean, 1 = slop found
    sys.exit(0 if not matches else 1)


@cli.command()
@click.argument("file", required=False, type=click.Path(exists=True, readable=True))
@click.option("--stdin", "use_stdin", is_flag=True, help="Read text from stdin.")
def score(file: Optional[str], use_stdin: bool) -> None:
    """Give a humanness score (0–100) for the text."""
    if use_stdin:
        text = sys.stdin.read()
    elif file:
        text = Path(file).read_text(encoding="utf-8", errors="replace")
    else:
        raise click.UsageError("Provide a FILE argument or use --stdin.")

    s, matches = score_text(text)
    _print_score(s, len(matches))


@cli.command()
@click.argument("file", type=click.Path(exists=True, readable=True))
def fix(file: str) -> None:
    """(Future) Rewrite file with an LLM to remove slop. Placeholder for now."""
    click.echo(_color("⚠  fix command not yet implemented.", BOLD, YELLOW))
    click.echo(
        "  The `fix` command will use an LLM to suggest rewrites for detected patterns.\n"
        "  For now, use `deslop check` to identify issues manually."
    )
    sys.exit(0)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
