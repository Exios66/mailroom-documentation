"""Report Simplified Technical English (ASD-STE100) issues in site pages.

Run from the repository root:

    python3 scripts/check_style.py                 # summary per page
    python3 scripts/check_style.py docs/x.md -v    # every finding in one page

It reads the prose of each published page. It skips code blocks, inline
code, tables, headings, HTML, and GitBook blocks. It skips docs/changelog/
(generated). It reports:

  LONG     a sentence longer than 25 words (STE: 20 for steps, 25 for text)
  CONTRACT a contraction ("don't"): write "do not"
  FUTURE   "will" or "would": write the present tense
  VAGUE    a word with no fixed meaning ("simply", "just", "easily", ...)
  MODAL    "should" or "might": state the rule or the condition

This is a style report, not a gate. It always exits 0. Fix what you touch.
"""

import pathlib
import re
import sys

DOCS = pathlib.Path("docs")
VERBOSE = "-v" in sys.argv
targets = [pathlib.Path(a) for a in sys.argv[1:] if not a.startswith("-")]

RULES = {
    "CONTRACT": re.compile(r"\b\w+(?:n't|'re|'ll|'ve|'d)\b|\b(?:it's|that's|there's|let's|here's|what's)\b", re.I),
    "FUTURE": re.compile(r"\b(?:will|would)\b", re.I),
    "VAGUE": re.compile(r"\b(?:simply|just|easily|obviously|basically|various|etc\.?)\b", re.I),
    "MODAL": re.compile(r"\b(?:should|might)\b", re.I),
}


def prose(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"{%.*?%}", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    lines = [ln for ln in text.splitlines()
             if ln.strip() and not ln.lstrip().startswith(("|", "#", "---", "***", "> "))]
    text = "\n".join(lines)
    text = re.sub(r"`[^`\n]*`", "CODE", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)  # images and badges are not prose
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # keep link text only
    text = re.sub(r"https?://\S+", "URL", text)
    return text


def sentences(text: str) -> list[str]:
    out = []
    for block in text.splitlines():  # one paragraph or list item per line
        block = re.sub(r"^\s*(?:[*-]|\d+\.)\s+(?:\[[ x]\]\s+)?", "", block)
        if block.count(" · ") >= 3:  # a stat ribbon, not a sentence
            continue
        # Split after . ! ? (and a closing ** or `) when a new sentence starts.
        out += [s for s in re.split(r"(?<=[.!?])(?:\*\*|`)?\s+(?=[A-Z*`(\"])", block) if s]
    return out


def findings(path: pathlib.Path) -> list[tuple[str, str]]:
    found = []
    for s in sentences(prose(path.read_text())):
        words = len(re.findall(r"[\w'’-]+", s))
        if words > 25:
            found.append(("LONG", f"{words} words: {s[:110]}…"))
        unquoted = re.sub(r'"[^"]*"|“[^”]*”', " ", s)  # a quoted word is an example, not usage
        for rule, rx in RULES.items():
            for m in rx.finditer(unquoted):
                found.append((rule, f"'{m.group(0)}': {s[:110]}"))
    return found


pages = targets or sorted(p for p in DOCS.rglob("*.md")
                          if not p.relative_to(DOCS).as_posix().startswith(("changelog/", "assets/", ".gitbook/"))
                          and p.name != "SUMMARY.md")
totals: dict[str, int] = {}
rows = []
for page in pages:
    f = findings(page)
    counts = {r: sum(1 for k, _ in f if k == r) for r in ("LONG", "CONTRACT", "FUTURE", "VAGUE", "MODAL")}
    for r, n in counts.items():
        totals[r] = totals.get(r, 0) + n
    rows.append((sum(counts.values()), page, counts))
    if VERBOSE:
        for rule, msg in f:
            print(f"{rule:8} {page}: {msg}")

if not VERBOSE:
    print(f"{'total':>5}  LONG CONTR FUTUR VAGUE MODAL  page")
    for n, page, c in sorted(rows, key=lambda r: -r[0]):
        if n:
            print(f"{n:5}  {c['LONG']:4} {c['CONTRACT']:5} {c['FUTURE']:5} {c['VAGUE']:5} {c['MODAL']:5}  {page}")
print("STYLE totals:", ", ".join(f"{k} {v}" for k, v in totals.items()))
