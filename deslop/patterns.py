"""
Pattern definitions for detecting AI "slop" writing patterns.
Based on tropes documented at https://tropes.fyi/tropes-md
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Match:
    """A detected slop pattern in text."""
    line_number: int
    line_text: str
    pattern_name: str
    pattern_description: str
    matched_text: str
    severity: int = 1  # 1=mild, 2=moderate, 3=severe


@dataclass
class Pattern:
    """A pattern rule for detecting slop."""
    name: str
    description: str
    severity: int = 1
    regexes: list = field(default_factory=list)
    words: list = field(default_factory=list)  # for simple word matching

    def find_matches(self, line: str, line_number: int) -> list[Match]:
        matches = []
        for pattern in self.regexes:
            for m in re.finditer(pattern, line, re.IGNORECASE):
                matches.append(Match(
                    line_number=line_number,
                    line_text=line.strip(),
                    pattern_name=self.name,
                    pattern_description=self.description,
                    matched_text=m.group(0),
                    severity=self.severity,
                ))
        for word in self.words:
            pattern = r'\b' + re.escape(word) + r'\b'
            for m in re.finditer(pattern, line, re.IGNORECASE):
                matches.append(Match(
                    line_number=line_number,
                    line_text=line.strip(),
                    pattern_name=self.name,
                    pattern_description=self.description,
                    matched_text=m.group(0),
                    severity=self.severity,
                ))
        return matches


# ─── Pattern Definitions ─────────────────────────────────────────────────────

PATTERNS: list[Pattern] = [

    # 1. Overused words ("Delve and Friends")
    Pattern(
        name="overused word",
        description='AI vocabulary — these words appear at absurd rates in AI-generated text',
        severity=2,
        words=[
            "delve", "delving", "tapestry", "landscape", "leverage",
            "robust", "certainly", "arguably", "remarkably", "fundamentally",
            "utilize", "streamline", "harness", "paradigm", "synergy",
            "ecosystem", "framework", "holistic", "nuanced", "comprehensive",
            "pivotal", "crucial", "essential", "notable", "noteworthy",
            "groundbreaking", "revolutionary", "transformative", "innovative",
            "cutting-edge", "state-of-the-art",
        ],
    ),

    # 2. Magic adverbs
    Pattern(
        name="magic adverb",
        description='Adverbs used to imply understated profundity — "quietly", "deeply", etc.',
        severity=1,
        words=[
            "quietly", "deeply", "truly", "simply", "gently", "softly",
            "subtly", "profoundly",
        ],
    ),

    # 3. Negative parallelism ("It's not X — it's Y")
    Pattern(
        name="negative parallelism",
        description='False profundity framing — "It\'s not X — it\'s Y" or "not because X, but Y"',
        severity=3,
        regexes=[
            r"it'?s\s+not\s+\w[\w\s]*[—–-]+\s*it'?s\s+\w",
            r"not\s+because\s+.{5,60},?\s+but\s+because",
            r"not\s+about\s+.{5,60}[—–-]+\s*it'?s\s+about",
        ],
    ),

    # 4. "Not X. Not Y. Just Z." countdown pattern
    Pattern(
        name="dramatic countdown",
        description='"Not X. Not Y. Just Z." — AI builds false tension by negating things before the reveal',
        severity=2,
        regexes=[
            r'\bnot\s+\w[\w\s]*\.\s+not\s+\w[\w\s]*\.\s+(just|only|but)\s+\w',
            r'\bnot\s+\w[\w\s]*,\s+not\s+\w[\w\s]*,\s+(?:just|only|but)\s+\w',
        ],
    ),

    # 5. Rhetorical self-questions ("The X? A Y.")
    Pattern(
        name="rhetorical self-question",
        description='Self-posed questions answered immediately for false drama — "The result? Devastating."',
        severity=2,
        regexes=[
            r'\b(?:the\s+result|the\s+worst\s+part|the\s+best\s+part|the\s+scary\s+part|the\s+surprising\s+part|the\s+real\s+issue|the\s+problem|the\s+catch|the\s+twist)\?',
            r'\b(?:why\s+does\s+it\s+matter|what\s+does\s+this\s+mean|so\s+what\s+happens)\?',
        ],
    ),

    # 6. Empty transitions
    Pattern(
        name="empty transition",
        description='Filler phrases that pad text without adding meaning',
        severity=1,
        regexes=[
            r"\bit'?s\s+worth\s+noting\b",
            r"\bhere'?s\s+the\s+thing\b",
            r"\bhere'?s\s+the\s+kicker\b",
            r"\bhere'?s\s+the\s+deal\b",
            r"\bthe\s+bottom\s+line\s+is\b",
            r"\bat\s+the\s+end\s+of\s+the\s+day\b",
            r"\bthe\s+truth\s+is\b",
            r"\bmake\s+no\s+mistake\b",
            r"\blet'?s\s+be\s+honest\b",
            r"\bin\s+today'?s\s+(?:fast-paced|rapidly\s+evolving|modern)\b",
            r"\bin\s+the\s+(?:ever-evolving|fast-paced)\b",
        ],
    ),

    # 7. "Serves as" dodge
    Pattern(
        name="serves-as dodge",
        description='Pompous copula replacement — "serves as", "stands as", "marks", "represents" instead of "is"',
        severity=1,
        regexes=[
            r'\bserves\s+as\s+(?:a|an|the)\b',
            r'\bstands\s+as\s+(?:a|an|the)\b',
            r'\bmarks\s+a\s+(?:pivotal|critical|important|significant|key)\b',
            r'\brepresents\s+(?:a|an|the)\s+(?:pivotal|critical|important|significant|key|major)\b',
        ],
    ),

    # 8. Anaphora abuse (repeated sentence openings)
    Pattern(
        name="anaphora abuse",
        description='Repeating the same sentence opener multiple times for hollow rhythm',
        severity=2,
        regexes=[
            r'(?:^|\n)\s*they\s+(?:could|should|would|can|will|must|need to)\s+.+\.\s*\n\s*they\s+(?:could|should|would|can|will|must|need to)',
            r'(?:^|\n)\s*we\s+(?:could|should|would|can|will|must|need to)\s+.+\.\s*\n\s*we\s+(?:could|should|would|can|will|must|need to)',
        ],
    ),

    # 9. Hedging overload
    Pattern(
        name="hedge overload",
        description='Excessive epistemic hedging stacked together',
        severity=1,
        regexes=[
            r'\b(?:it\s+(?:seems|appears|looks)\s+(?:like|as\s+if|that)|(?:one\s+might|you\s+might)\s+(?:say|argue|think|consider))\b',
            r'\bperhaps\s+(?:the\s+most|one\s+of\s+the\s+most|even)\b',
        ],
    ),

    # 10. Closing platitudes
    Pattern(
        name="closing platitude",
        description='Generic wrap-up statements that add no value',
        severity=1,
        regexes=[
            r'\bonly\s+time\s+will\s+tell\b',
            r'\bthe\s+future\s+(?:remains|is)\s+(?:uncertain|to\s+be\s+seen|bright)\b',
            r'\bone\s+thing\s+is\s+(?:clear|certain|for\s+sure)\b',
            r"\bwhat'?s\s+clear\s+is\s+that\b",
        ],
    ),

    # 11. Punchy fragments (very short lines used as "paragraphs")
    # This is handled separately in the scorer since it needs multi-line context

    # 12. In-conclusion markers
    Pattern(
        name="in-conclusion marker",
        description='AI-style essay closers that signal a formulaic wrap-up',
        severity=2,
        words=['in conclusion', 'to summarize', 'in summary', 'to wrap up', 'in closing'],
        regexes=[
            r'\bin\s+conclusion\b',
            r'\bto\s+summarize\b',
            r'\bin\s+summary\b',
            r'\bto\s+wrap\s+up\b',
            r'\bin\s+closing\b',
        ],
    ),

    # 13. Throat-clearing openers
    Pattern(
        name="throat-clearing opener",
        description='Filler openers that delay getting to the point',
        severity=2,
        regexes=[
            r'\bwithout\s+further\s+ado\b',
            r'\bwith\s+that\s+(?:said|being\s+said)\b',
            r'\bthat\s+being\s+said\b',
            r'\bhaving\s+said\s+that\b',
            r'\bwith\s+that\s+out\s+of\s+the\s+way\b',
        ],
    ),

    # 14. As-we-can-see
    Pattern(
        name="as-we-can-see",
        description='Condescending references to what was just said or is obvious',
        severity=1,
        regexes=[
            r'\bas\s+we\s+can\s+see\b',
            r'\bas\s+(?:mentioned|noted|discussed)\s+(?:above|earlier|previously|before)\b',
            r'\bas\s+(?:you\s+(?:can\s+see|may\s+know|probably\s+know))\b',
        ],
    ),

    # 15. Moving-forward filler
    Pattern(
        name="moving-forward filler",
        description='Vague temporal filler that pads without adding meaning',
        severity=1,
        regexes=[
            r'\bmoving\s+forward\b',
            r'\bgoing\s+forward\b',
            r'\bin\s+this\s+day\s+and\s+age\b',
            r'\bin\s+the\s+modern\s+(?:era|world|age|landscape)\b',
        ],
    ),
]


def check_line(line: str, line_number: int) -> list[Match]:
    """Check a single line against all patterns."""
    matches = []
    for pattern in PATTERNS:
        matches.extend(pattern.find_matches(line, line_number))
    return matches


def check_text(text: str) -> list[Match]:
    """Check full text and return all matches."""
    all_matches = []
    lines = text.splitlines()

    for i, line in enumerate(lines, start=1):
        if line.strip():  # skip blank lines
            all_matches.extend(check_line(line, i))

    # Multi-line: detect punchy fragment paragraphs
    all_matches.extend(_detect_punchy_fragments(lines))

    # Multi-line: detect tricolon abuse
    all_matches.extend(_detect_tricolon(lines))

    return all_matches


def _detect_punchy_fragments(lines: list[str]) -> list[Match]:
    """Detect very short isolated lines used as punchy emphasis paragraphs."""
    matches = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        # A "punchy fragment" is a very short line (< 8 words) surrounded by blank lines
        # or at the end/beginning of the text
        word_count = len(stripped.split())
        if 0 < word_count <= 6 and stripped.endswith('.'):
            prev_blank = (i == 0) or not lines[i - 1].strip()
            next_blank = (i == len(lines) - 1) or not lines[i + 1].strip()
            if prev_blank and next_blank:
                matches.append(Match(
                    line_number=i + 1,
                    line_text=stripped,
                    pattern_name="punchy fragment",
                    pattern_description='Short isolated sentence used as a standalone paragraph for false emphasis',
                    matched_text=stripped,
                    severity=1,
                ))
    return matches


def _detect_tricolon(lines: list[str]) -> list[Match]:
    """Detect tricolon abuse — lists of exactly three items used repeatedly."""
    matches = []
    # Look for comma-separated lists of three (X, Y, and Z)
    tricolon_pattern = re.compile(
        r'\b[\w\s]+,\s+[\w\s]+,\s+and\s+[\w\s]+\b',
        re.IGNORECASE,
    )
    tricolon_count = 0
    tricolon_lines = []

    for i, line in enumerate(lines, start=1):
        if tricolon_pattern.search(line):
            tricolon_count += 1
            tricolon_lines.append((i, line.strip()))

    # Flag if more than 2 tricolons in the document
    if tricolon_count >= 3:
        for line_number, line_text in tricolon_lines:
            matches.append(Match(
                line_number=line_number,
                line_text=line_text,
                pattern_name="tricolon abuse",
                pattern_description=f'Lists of three items used {tricolon_count}× in the document — a classic AI rhythm crutch',
                matched_text=tricolon_pattern.search(line_text).group(0) if tricolon_pattern.search(line_text) else line_text,
                severity=2,
            ))

    return matches
