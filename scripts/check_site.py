"""Check the GitBook site source before you push.

Run from the repository root:

    uv run --no-project --with pyyaml python3 scripts/check_site.py

It checks:
  1. gitbook-docs.yaml and docs/.gitbook.yaml parse, and the site keeps its
     sections shape (section-1 -> mailroom-docs, path /, directory ./docs).
  2. Every docs/SUMMARY.md entry points at a file, and every page under docs/
     is listed in SUMMARY.md (assets/ and .gitbook/ excepted).
  3. Every relative link and image (src and srcset) in a published page resolves to a file.
  4. Every #anchor matches a heading id on the LIVE GitBook page. GitBook
     builds its own heading ids (not GitHub's), so the live page is the truth.
     A missing anchor is an ERROR when the target page is unchanged against
     origin/main (so the live page is current). It is UNVERIFIED only when the
     target page changed on this branch (a heading not live yet), or when the
     live page could not be fetched.

Exit code 0 = no errors (UNVERIFIED lines can remain). Exit code 1 = errors.
Pass --offline to skip the live anchor check (all anchors become UNVERIFIED).
"""

import pathlib
import re
import shutil
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is missing. Run: uv run --no-project --with pyyaml python3 scripts/check_site.py")

SITE = "https://mailroom-inc.gitbook.io/the-digital-mailroom/"
DOCS = pathlib.Path("docs")
OFFLINE = "--offline" in sys.argv
errors, unverified = [], []

if not DOCS.is_dir():
    sys.exit("Run this from the repository root (the folder that holds docs/).")

# 1. Site config shape.
with open("gitbook-docs.yaml") as fh:
    cfg = yaml.safe_load(fh)
with open("docs/.gitbook.yaml") as fh:
    space_cfg = yaml.safe_load(fh) or {}
top = cfg["site"]["structure"]
if len(top) != 1 or top[0].get("type") != "section" or top[0].get("key") != "section-1":
    errors.append("gitbook-docs.yaml: the only top-level node must be the section with key section-1")
elif not isinstance(top[0].get("children"), list) or len(top[0]["children"]) != 1 \
        or not isinstance(top[0]["children"][0], dict):
    errors.append("gitbook-docs.yaml: section-1 must have exactly one child, the space mailroom-docs")
else:
    space = top[0]["children"][0]
    got = (space.get("type"), space.get("key"), space.get("path"), (space.get("content") or {}).get("directory"))
    if got != ("space", "mailroom-docs", "/", "./docs"):
        errors.append(f"gitbook-docs.yaml: space must be (space, mailroom-docs, /, ./docs), found {got}")
# The rest of this script reads docs/README.md and docs/SUMMARY.md, so the space config must point there.
structure = space_cfg.get("structure") or {}
got = (space_cfg.get("root"), structure.get("readme"), structure.get("summary"))
if got != ("./", "README.md", "SUMMARY.md"):
    errors.append(f"docs/.gitbook.yaml: must be (root ./, readme README.md, summary SUMMARY.md), found {got}")

# 2. SUMMARY.md <-> files.
# A link destination, with an optional <...> wrapper and an optional "title".
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)")

summary = (DOCS / "SUMMARY.md").read_text()
listed = {m.partition("#")[0] for m in LINK.findall(summary)
          if "://" not in m and m.partition("#")[0].endswith(".md")}
for page in sorted(listed):
    if not (DOCS / page).is_file():
        errors.append(f"SUMMARY.md lists a missing file: {page}")
for f in sorted(DOCS.rglob("*.md")):
    rel = f.relative_to(DOCS).as_posix()
    if rel != "SUMMARY.md" and not rel.startswith(("assets/", ".gitbook/")) and rel not in listed:
        errors.append(f"not listed in SUMMARY.md, so it will not publish: docs/{rel}")


# 3 + 4. Links, images, anchors.
def live_url(page: pathlib.Path) -> str:
    rel = page.resolve().relative_to(DOCS.resolve()).as_posix()
    return SITE + re.sub(r"(/?README)?\.md$", "", rel)


live_ids: dict[str, set[str] | None] = {}
CURL = shutil.which("curl")


def ids_on_live_page(page: pathlib.Path) -> set[str] | None:
    """The heading ids on the live page, or None when the page cannot be fetched."""
    url = live_url(page)
    if url not in live_ids:
        live_ids[url] = None
        if CURL:
            try:
                res = subprocess.run([CURL, "-sL", "--max-time", "20", "-w", "\n%{http_code}", url],
                                     capture_output=True, text=True, timeout=30, check=False)
                html, _, code = res.stdout.rpartition("\n")
                if res.returncode == 0 and code.strip() == "200":
                    live_ids[url] = set(re.findall(r'id="([^"]+)"', html))
            except subprocess.TimeoutExpired:
                pass
    return live_ids[url]


def changed_on_branch(page: pathlib.Path) -> bool:
    """True when the page differs from origin/main, so its live copy can be out of date."""
    res = subprocess.run(["git", "diff", "--quiet", "origin/main", "--", str(page)],
                         capture_output=True, check=False)
    return res.returncode != 0  # 1 = differs; >1 = no origin/main or untracked: treat as changed


for f in sorted([DOCS / "README.md"] + [DOCS / p for p in listed]):
    text = re.sub(r"```.*?```", "", f.read_text(), flags=re.S)  # ignore code blocks
    text = re.sub(r"`[^`\n]*`", "", text)  # ignore inline code
    targets = LINK.findall(text) + re.findall(r'(?:src|srcset)="([^"\s]+)"', text)
    for target in targets:
        if re.match(r"[a-z]+:", target):  # https:, mailto:, ...
            continue
        path, _, frag = target.partition("#")
        dest = (f.parent / path).resolve() if path else f.resolve()
        if dest.is_dir():
            dest = dest / "README.md"
        if not dest.exists():
            errors.append(f"{f}: broken link {target}")
            continue
        if not frag or dest.suffix != ".md":
            continue
        if OFFLINE:
            unverified.append(f"{f}: anchor {target} (offline)")
            continue
        ids = ids_on_live_page(dest)
        rel = dest.relative_to(pathlib.Path.cwd())
        if ids is None:
            unverified.append(f"{f}: anchor {target}: could not fetch {live_url(dest)}")
        elif frag in ids:
            continue
        elif changed_on_branch(rel):
            # The target page changed on this branch, so the heading may not be live yet.
            unverified.append(f"{f}: anchor {target} is not on {live_url(dest)} (page changed on this branch)")
        else:
            errors.append(f"{f}: anchor {target} is not on {live_url(dest)}, and the page is unchanged")

for line in unverified:
    print("UNVERIFIED", line)
for line in errors:
    print("ERROR", line)
print("CHECK-OK" if not errors else f"{len(errors)} error(s)")
sys.exit(1 if errors else 0)
