# deslop

**CLI tool to detect and remove AI writing patterns ("slop") from text.**

Catches the telltale signs of AI-generated prose: overused buzzwords, false profundity structures, rhetorical self-questions, empty transitions, and more — based on the tropes catalogued at [tropes.fyi](https://tropes.fyi).

---

## Install

```bash
pip install deslop
# or with uv:
uv tool install deslop
```

Or install from source:

```bash
git clone https://github.com/rankgnar/deslop
cd deslop
pip install -e .
```

---

## Usage

### Check a file

```bash
deslop check article.md
```

```
article.md:12 — "It's not about speed — it's about precision"
  └─ Pattern: negative parallelism  The "It's not X — it's Y" false-profundity frame

article.md:34 — "Let's delve into the details"
  └─ Pattern: overused word  AI vocabulary — these words appear at absurd rates in AI-generated text

article.md:58 — "It's worth noting that the API is deprecated"
  └─ Pattern: empty transition  Filler phrases that pad text without adding meaning

Score: 62/100 (needs work)  —  3 issue(s) found
```

### Check from stdin (pipe-friendly)

```bash
cat article.md | deslop check --stdin
echo "We need to leverage robust frameworks." | deslop check --stdin
```

### Score only

```bash
deslop score article.md
# → Score: 74/100 (mostly clean)  —  2 issue(s) found
```

### Filter by severity

```bash
# Only show moderate/severe issues (severity ≥ 2)
deslop check article.md --min-severity 2
```

### Fix (coming soon)

```bash
deslop fix article.md
# ⚠  fix command not yet implemented.
```

---

## Detected Patterns

| Pattern | Severity | Example |
|---|---|---|
| **overused word** | moderate | "delve", "tapestry", "leverage", "robust", "certainly" |
| **magic adverb** | mild | "quietly", "deeply", "truly", "simply" |
| **negative parallelism** | severe | "It's not X — it's Y", "not because X, but Y" |
| **dramatic countdown** | moderate | "Not a bug. Not a feature. A design flaw." |
| **rhetorical self-question** | moderate | "The result? Devastating." |
| **empty transition** | mild | "It's worth noting", "Here's the thing", "Here's the kicker" |
| **serves-as dodge** | mild | "serves as a reminder", "stands as a testament" |
| **tricolon abuse** | moderate | Three-item lists used 3+ times in the same document |
| **punchy fragment** | mild | Very short isolated sentences used as standalone paragraphs |
| **anaphora abuse** | moderate | Repeated sentence openings ("They could… They could… They could…") |
| **hedge overload** | mild | "perhaps the most", "one might argue" |
| **closing platitude** | mild | "only time will tell", "the future remains uncertain" |

---

## Score Interpretation

| Score | Label |
|---|---|
| 85–100 | looks human ✓ |
| 70–84 | mostly clean |
| 50–69 | needs work |
| 30–49 | heavy slop |
| 0–29 | robot detected 🤖 |

---

## Exit Codes

- `0` — no patterns detected (clean)
- `1` — one or more patterns detected

This makes `deslop check` usable in CI pipelines:

```bash
deslop check docs/blog-post.md || echo "Slop detected, please review"
```

---

## Roadmap

- [ ] `deslop fix` — LLM-assisted rewrite of flagged phrases
- [ ] `--format json` — machine-readable output
- [ ] `--ignore pattern_name` — suppress specific pattern types
- [ ] `.desloprc` config file
- [ ] Pre-commit hook integration

---

## Sources

Patterns based on [tropes.fyi/tropes-md](https://tropes.fyi/tropes-md) — a catalogue of common AI writing tropes.
