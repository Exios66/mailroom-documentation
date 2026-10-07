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
     An anchor to a heading that is not live yet is reported as UNVERIFIED.

Exit code 0 = no errors (UNVERIFIED lines can remain). Exit code 1 = errors.
Pass --offline to skip the live anchor check (all anchors become UNVERIFIED).
"""

import pathlib
import re
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
cfg = yaml.safe_load(open("gitbook-docs.yaml"))
yaml.safe_load(open("docs/.gitbook.yaml"))
top = cfg["site"]["structure"]
if len(top) != 1 or top[0].get("type") != "section" or top[0].get("key") != "section-1":
    errors.append("gitbook-docs.yaml: the only top-level node must be the section with key section-1")
else:
    space = top[0]["children"][0]
    got = (space.get("type"), space.get("key"), space.get("path"), space["content"].get("directory"))
    if got != ("space", "mailroom-docs", "/", "./docs"):
        errors.append(f"gitbook-docs.yaml: space must be (space, mailroom-docs, /, ./docs), found {got}")

# 2. SUMMARY.md <-> files.
summary = (DOCS / "SUMMARY.md").read_text()
listed = {m for m in re.findall(r"\]\(([^)]+\.md)\)", summary) if "://" not in m}
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


live_ids: dict[str, set[str]] = {}


def ids_on_live_page(page: pathlib.Path) -> set[str]:
    url = live_url(page)
    if url not in live_ids:
        html = subprocess.run(["curl", "-sL", url], capture_output=True, text=True).stdout
        live_ids[url] = set(re.findall(r'id="([^"]+)"', html))
    return live_ids[url]


for f in sorted([DOCS / "README.md"] + [DOCS / p for p in listed]):
    text = re.sub(r"```.*?```", "", f.read_text(), flags=re.S)  # ignore code blocks
    text = re.sub(r"`[^`\n]*`", "", text)  # ignore inline code
    targets = re.findall(r"\]\(([^)\s]+)\)", text) + re.findall(r'(?:src|srcset)="([^"\s]+)"', text)
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
        elif frag not in ids_on_live_page(dest):
            # Not on the live page. A brand-new heading is not live yet; anything else is wrong.
            unverified.append(f"{f}: anchor {target} is not on {live_url(dest)}")

for line in unverified:
    print("UNVERIFIED", line)
for line in errors:
    print("ERROR", line)
print("CHECK-OK" if not errors else f"{len(errors)} error(s)")
sys.exit(1 if errors else 0)
