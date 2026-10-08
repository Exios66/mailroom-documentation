# AGENTS.md

**Operating law for `Exios66/mailroom-documentation`. This repository is the source of [The Digital Mailroom](https://mailroom-inc.gitbook.io/the-digital-mailroom/) GitBook site.**

Read this whole file before you change anything. It is written so that any agent, of any size, can ship a correct change without asking a question. If a step here is unclear, follow it literally and report what happened.

The site's deployment broke twice before this file existed (commits `6ac7930` and `ffc4a3f`). Every rule below exists to stop a known failure.

| Fact | Value |
| --- | --- |
| This repository | <https://github.com/Exios66/mailroom-documentation> (branch `main`) |
| Live site | <https://mailroom-inc.gitbook.io/the-digital-mailroom/> |
| What the site describes | The `llm-mailroom` pipeline ([`Exios66/llm-mailroom`](https://github.com/Exios66/llm-mailroom)) and the repositories around it |
| Publishing mechanism | GitBook **Git Sync**. A merge to `main` republishes the site. There is no build step and no CI. |
| Scope of this repository | Documentation only: Markdown pages, the Git Sync config, site art, generated charts, and three scripts (site checker, style report, chart builder). No pipeline code. |
| Companion files | `README.md` (repository orientation) and the *published* runbook [`docs/about-this-site/maintaining.md`](docs/about-this-site/maintaining.md) |

---

## 0. The golden rules (memorize these)

1. **One site, one section, one space.** This is a **sections** site. The space `mailroom-docs` must **always** be inside the section `section-1`. **Never** put a space at the top level of `site.structure`.
2. **Never change a `key`.** `section-1` and `mailroom-docs` are permanent identities. A new key makes GitBook delete the old node and import a new one. The result is new IDs, broken links, and lost content.
3. **`content.directory` is a folder. `path` is a URL.** Keep `content.directory: ./docs` and space `path: /`. Never set `path: docs`.
4. **The GitBook Project directory is the repository root.** Leave it empty in the GitBook UI. `gitbook-docs.yaml` stays at the repository root.
5. **Only pages listed in `docs/SUMMARY.md` publish.** A page that is not listed does not exist on the site.
6. **This repository is the only GitBook deployment.** `Exios66/llm-mailroom` still carries a stale GitBook config. Never connect it (§16).
7. **Direct commits to `main` are allowed here.** This repository is standalone. It is not a `packages/*` mirror of the monorepo. `llm-mailroom` **is** a mirror: never edit it by hand (§16).
8. **Never hand-edit `docs/changelog/`.** It is generated. Regenerate it (§10.7).
9. **Run the checker before every push:** `uv run --no-project --with pyyaml python3 scripts/check_site.py` (§11).
10. **Anchors use GitBook heading ids, not GitHub ids.** Copy the id from the live page (§7.3).

---

## 1. Find your task

| I want to… | Go to |
| --- | --- |
| Start a session in this repository | §2 |
| Understand how the site is built and deployed | §3, §4 |
| Know which URL a file publishes at | §5 |
| Write or edit a page | §6 |
| Add a link, an image, or an anchor | §7 |
| Change a version, pin, count, or other fact | §8, §9 |
| Add, move, rename, or delete a page | §10.1 – §10.3 |
| Add a sidebar section | §10.4 |
| Add or change art | §10.5 |
| Add or update a chart | §10.9 |
| Bump a version or dataset pin | §10.6 |
| Regenerate the Changelog | §10.7 |
| Check my change before I push | §11 |
| Commit, push, or open a pull request | §12 |
| Check the live site after a merge | §13 |
| Fix a GitBook error or a missing page | §15 |
| Report or hand off work | §18 |

---

## 2. Startup ritual (every session)

Run these commands from the repository root. Read every output.

```bash
git fetch origin
git status -sb
git log --oneline -5 origin/main
```

| Check | Pass | If it fails |
| --- | --- | --- |
| Branch and sync | You are on `main` (or your own branch) and not behind `origin/main` | `git pull --ff-only` on `main`, or rebase your branch |
| Working tree | Clean, or only your own files changed | Another writer may share this checkout. Do not stage, discard, or commit their files. |
| GitBook editor commits | You know about any new commit from GitBook (see §12.4) | Pull before you edit, or you will conflict with it |

Then:

1. Read `gitbook-docs.yaml` and `docs/.gitbook.yaml` before any structural change. Compare `gitbook-docs.yaml` with §3.1 and `docs/.gitbook.yaml` with §3.2. Each file must match its example exactly.
2. Run the checker once (§11) so you know the starting state.
3. State which harness you run under (Claude Code, Codex, Cursor, OpenCode, …) and which checkout you treat as canonical.
4. Use read-only inspection until you know what to change.

---

## 3. Deployment model (authoritative)

GitBook Git Sync watches `main`. Every merge to `main` republishes the site, usually within a few minutes.

```text
Exios66/mailroom-documentation @ main
   │   GitBook "Project directory" = repository root (left empty in the UI)
   ▼
gitbook-docs.yaml
   └── section-1   (title "The Digital Mailroom", path the-digital-mailroom, default: true)
         └── space  mailroom-docs  (path: /, default: true)
               └── content.directory: ./docs
                     ├── docs/README.md     → landing page
                     ├── docs/SUMMARY.md    → sidebar (table of contents)
                     └── docs/**/*.md        → pages (only if listed in SUMMARY.md)
```

### 3.1 The exact live `gitbook-docs.yaml`

Do not change this file for a content change. Do not reformat it.

```yaml
$schema: https://api.gitbook.com/gitbook-docs.yaml
site:
  title: The Digital Mailroom
  structure:
    - type: section
      key: section-1
      title: The Digital Mailroom
      path: the-digital-mailroom
      default: true
      children:
        - type: space
          key: mailroom-docs
          title: The Digital Mailroom
          path: /
          default: true
          content:
            directory: ./docs
            language: en
```

### 3.2 The space content config: `docs/.gitbook.yaml`

```yaml
root: ./

structure:
  readme: README.md
  summary: SUMMARY.md
```

`root: ./` is relative to the space directory (`./docs`). So `README.md` means `docs/README.md` and `SUMMARY.md` means `docs/SUMMARY.md`.

### 3.3 One-time connection (GitBook UI, for the record)

This is already done. Repeat it only if the integration is lost.

1. Open the space `mailroom-docs` (titled **The Digital Mailroom**).
2. **Configure → GitHub Sync.** Install the GitBook GitHub app on **`Exios66/mailroom-documentation`**. Do **not** pick `llm-mailroom`.
3. Pick branch `main`. **Leave Project directory empty** (repository root).
4. For the first sync, pick **GitHub → GitBook**.

---

## 4. The one hard rule: sections vs. root spaces

A GitBook site has one of two shapes. A **sections** site has one or more sections, and every space is inside a section. A **siteSpaces** site is flat: its spaces are at the top level. A site is never both. This site is a sections site. So:

> **A space at the top level of `site.structure` is illegal here.**

### The exact error, and the fix

```text
Error while updating site
Failed to parse site configuration — site.structure:
Root-level site spaces can only exist in a non-sections site
```

**Meaning:** `gitbook-docs.yaml` puts `mailroom-docs` at the top level. GitBook refuses the whole update and keeps the last good config. The site keeps serving the old content but stops updating.

**Fix (what `6ac7930` and `ffc4a3f` did):** put the space back inside `section-1.children`, with the **unchanged keys**. Restore the exact YAML in §3.1.

**Do not** "simplify" by moving the space to the top level. A flat site needs the section deleted first in the GitBook **Site structure** UI. That is a deliberate, coordinated change, never a docs edit.

---

## 5. How a file becomes a page

### 5.1 File path → live URL

Site base: `https://mailroom-inc.gitbook.io/the-digital-mailroom/`

| File in this repository | Live URL |
| --- | --- |
| `docs/README.md` | `<base>` (the home page) |
| `docs/start-here/overview.md` | `<base>start-here/overview` |
| `docs/repository-guides/repos/README.md` | `<base>repository-guides/repos` |
| `docs/changelog/2026/v0-8-0.md` | `<base>changelog/2026/v0-8-0` |

Rules: drop `docs/`, drop `.md`, and a folder's `README.md` publishes at the folder URL. The folder `docs/` never appears in a URL.

Two machine-readable views exist on the live site:

* Append `.md` to any page URL to get its Markdown, for example `<base>start-here/overview.md`.
* `<base>llms.txt` lists every published page.

### 5.2 `docs/SUMMARY.md` syntax

`SUMMARY.md` is the sidebar. Its order is the sidebar order. Its syntax is strict:

```markdown
# Table of contents

* [LLM-MAILROOM](README.md)

## Start here

* [Overview](start-here/overview.md)
* [Getting started](start-here/getting-started.md)

## Repository guides

* [All repositories](repository-guides/repos/README.md)
  * [llm-mailroom](repository-guides/repos/llm-mailroom.md)
  * [reports/ on GitHub](https://github.com/Exios66/local-mailroom-sandbox/tree/main/reports)
```

* Keep the first line `# Table of contents`.
* A `## Heading` starts a sidebar group.
* Each entry is `* [Sidebar title](path/from/docs.md)`. Paths are relative to `docs/`. Never start a path with `docs/` or `/`.
* Indent a child entry by exactly two spaces under its parent.
* An entry may be a full `https://` URL. It shows as an external link.
* **The sidebar title becomes the page header on the site.** GitBook replaces the page's `# H1` with it. Keep the two the same.
* **Keep the home entry exactly `* [LLM-MAILROOM](README.md)`.** Another title (for example `Welcome`) changes the home page header.

### 5.3 Where content goes (section folders)

| Sidebar group | Folder | Holds |
| --- | --- | --- |
| (home) | `docs/README.md` | Landing page: masthead, badges, Fumi, walk-through, docs shelf |
| Start here | `docs/start-here/` | Overview, Getting started, Glossary |
| The pipeline in depth | `docs/the-pipeline-in-depth/` | Running, flowchart, extraction schemas, scoring |
| How it fits together | `docs/how-it-fits-together/` | The constellation, data and corpora, governance, repository index |
| Mailroom dataset | `docs/mailroom-dataset/` | The Hub dataset: classes, configs, source corpora, EDA, figures |
| Experiment reports | `docs/experiment-reports/` | Report indexes (the sandbox reports page lives under `repository-guides/`) |
| Repository guides | `docs/repository-guides/repos/` | One guide per repository |
| Pipeline reference (llm-mailroom) | `docs/pipeline-reference-llm-mailroom/` | Canonical pipeline reference: architecture, agents, configuration, API, Gmail, deployment, operations |
| API reference | `docs/api-reference/` | Interactive endpoint reference: `mailroom-openapi.yaml` plus one page per tag |
| Changelog | `docs/changelog/` | **Generated** release notes. Never hand-edit (§10.7). |
| About this site | `docs/about-this-site/` | `maintaining.md`, the published runbook |

Files under `docs/assets/` and `docs/.gitbook/` are not pages. They are never listed in `SUMMARY.md`.

---

## 6. Writing a page

### 6.1 Page skeleton

Copy this for a new page. There is no front matter (no `---` block) on normal pages. Only generated Changelog pages carry front matter.

```markdown
# Page title

One or two sentences that say what this page covers and who it is for.

## First topic

Short paragraphs. Imperative steps. Tables for reference facts.

## Second topic

…
```

* Exactly one `#` H1, as the first line. It must equal the page's `SUMMARY.md` title.
* Use `##` and `###` for sections. Do not skip levels.
* Keep heading text short. Every punctuation mark changes the anchor id (§7.3).

### 6.2 Allowed formatting

Plain Markdown: paragraphs, lists, tables, fenced code blocks with a language tag (`bash`, `yaml`, `python`, `text`), and links.

GitBook blocks: use only the ones that neighbouring pages already use. The exact syntax:

```markdown
{% hint style="info" %}
Text of the note.
{% endhint %}

{% hint style="warning" %}
Text of the warning.
{% endhint %}

{% embed url="https://exios66.github.io/Mailroom-Corpus-EDA/" %}
```

* `{% updates %}` and `{% update date="…" %}` blocks belong only to the generated Changelog. Do not use them elsewhere.
* Mermaid diagrams (a fenced block tagged `mermaid`) are used on several pages. They render on the site only if the Mermaid integration is on for the space; otherwise they show as code.
* HTML is allowed only in the forms already in use: `<figure><img …><figcaption>…</figcaption></figure>` and the home page's `<table data-header-hidden>` layout.
* GitBook strips `<script>`. Do not add scripts or interactive HTML.

### 6.3 Writing style

The CodeRabbit review (`.coderabbit.yaml`) checks these:

* Simplified Technical English: short sentences, present tense, imperative steps, no contractions ("do not", not "don't").
* One fact, one source. **Link, do not copy.** A repository's own README and docs are canonical. A page here summarizes and links.
* Every fact that drifts (version, pin, count, test total, model name, dataset revision) carries an "as of" date (§8.3).
* Say what is unverified. Remove or correct a wrong claim. Do not soften it.
* Every step has its prerequisite. Every command has its expected result. No "TODO", "TBD", or "see below" without a target.

Measure the style of each page you edit:

```bash
python3 scripts/check_style.py docs/<page>.md -v
```

It prints one line per finding: `LONG` (a sentence over 25 words), `CONTRACT`, `FUTURE` ("will", "would"), `VAGUE` ("simply", "etc."), `MODAL` ("should", "might"). It is a report, not a gate. Fix every finding in the sentences you add or change. Run it with no arguments for a per-page summary.

How to fix a `LONG` sentence:

* Split it into two or three sentences. Keep one idea per sentence.
* Turn a list inside a sentence ("a, b, c, d and e") into a bulleted list.
* Turn a set of numbers inside a sentence into a table.
* Put a condition first: "If X, do Y."

---

## 7. Links, images, and anchors

### 7.1 Links

| Link to | Write | Example |
| --- | --- | --- |
| Another page on this site | A relative path from the current file to the target `.md` file | From `docs/start-here/overview.md`: `[Scoring](../the-pipeline-in-depth/scoring-and-metrics.md)` |
| A section folder's landing page | The folder's `README.md`, or the folder path ending in `/` | `[Repository guides](repository-guides/repos/)` |
| A heading on another page | Path + `#` + the GitBook id (§7.3) | `[Mode A](docker-deployment.md#mode-a-ollama-offline)` |
| A heading on the same page | `#` + the GitBook id | `[Pipeline at a glance](#id-1.-pipeline-at-a-glance)` |
| A file in another repository | A full GitHub URL that names a ref | `https://github.com/Exios66/llm-mailroom/blob/main/CHANGELOG.md` |
| A specific released version | A tag URL | `https://github.com/Exios66/llm-dojo-scoring/releases/tag/v0.21.0` |

Never:

* start a relative link with `docs/` or `/`;
* link to a page with a `https://mailroom-inc.gitbook.io/…` URL from inside this site (use the relative path);
* use a relative link to a file in another repository (it resolves inside this repository and breaks);
* link to a folder that has no `README.md` page.

### 7.2 Images

| Image | Where it lives | How to reference it |
| --- | --- | --- |
| Site art used by pages (`banner.png`, `fumi.gif`, `hoot-icon.png`) | `docs/.gitbook/assets/` | A relative path from the page. From `docs/README.md`: `.gitbook/assets/banner.png`. From a page one folder deep: `../.gitbook/assets/banner.png`. |
| Dataset EDA figures | `Exios66/Mailroom-Corpus-EDA` `main` | `https://raw.githubusercontent.com/Exios66/Mailroom-Corpus-EDA/main/reports/figures/<file>.png` |
| Sandbox report figures | `Exios66/local-mailroom-sandbox` `main` | A full `raw.githubusercontent.com` URL on `main` |
| Interactive charts and dashboards | `exios66.github.io/Mailroom-Corpus-EDA` | `{% embed url="…" %}`. GitBook renders it as a frame. Do not write raw `<iframe>` HTML. |
| Site charts built from page data | `docs/.gitbook/assets/chart-<name>-light.svg` and `-dark.svg`, written by `scripts/build_charts.py` | The `<picture>` form below. Never hand-edit the SVG. Follow §10.9. |

Always give an image `alt` text. Use the `<figure>` form when the image needs a caption:

```html
<figure><img src="../.gitbook/assets/banner.png" alt="What the image shows"><figcaption><p>Caption.</p></figcaption></figure>
```

A site chart has a light and a dark file. Use the `<picture>` form, so GitBook shows the file that matches the reader's theme. Write the whole element on one line:

```html
<figure><picture><source srcset="../.gitbook/assets/chart-<name>-dark.svg" media="(prefers-color-scheme: dark)"><img src="../.gitbook/assets/chart-<name>-light.svg" alt="What the chart shows, with the key values"></picture><figcaption><p>Caption. The table above holds the same values.</p></figcaption></figure>
```

The `alt` text states the finding and the key values. A reader with a screen reader gets the chart from it.

### 7.3 Anchors: GitBook ids are not GitHub ids

GitBook builds its own heading ids. They differ from GitHub's. A link that works in the GitHub file view can scroll nowhere on the live site. **The live site wins.**

Observed GitBook rules (verified on the live site, 2026-10-07):

| Heading | GitBook id | GitHub id (do not use) |
| --- | --- | --- |
| `## Backup & Restore` | `backup-and-restore` | `backup--restore` |
| `## Mode A — Ollama (offline)` | `mode-a-ollama-offline` | `mode-a--ollama-offline` |
| `## Mode G — full stack (LiteLLM + Modal GPU tiers)` | `mode-g-full-stack-litellm--modal-gpu-tiers` | `mode-g--full-stack-litellm--modal-gpu-tiers` |
| ``## `insurance_claim` — 1,100 rows (33.3%)`` | `insurance_claim-1-100-rows-33.3` | `insurance_claim--1100-rows-333` |
| `## 1. Pipeline at a glance` | `id-1.-pipeline-at-a-glance` | `1-pipeline-at-a-glance` |
| ``### `free_quota` `` | `free_quota` | `free_quota` |

In short:

* Letters become lower-case.
* `&` becomes `and`.
* A run of dashes or spaces becomes one `-`, but `+` leaves `--`.
* A comma inside a number becomes `-`.
* Periods and underscores stay.
* A heading that starts with a digit gets the prefix `id-`.

**Do not guess an id. Copy it from the live page:**

```bash
curl -sL https://mailroom-inc.gitbook.io/the-digital-mailroom/<page-url> | grep -oE 'id="[^"]+"' | sort -u
```

For a heading you add in this change, the id is not live yet. Write your best id from the rules above, then confirm it after the merge (§13). The checker marks such anchors `UNVERIFIED`, because the target page differs from `origin/main`.

---

## 8. Facts, sources, and dates

### 8.1 Where the truth lives

This site describes other repositories. Every technical claim must match the upstream source at a named ref.

| Topic | Source of truth |
| --- | --- |
| Pipeline code, config keys, env vars, CLI flags, CHANGELOG | [`Exios66/llm-mailroom`](https://github.com/Exios66/llm-mailroom) |
| Scoring engine, field types, prompt catalog | [`Exios66/llm-dojo-scoring`](https://github.com/Exios66/llm-dojo-scoring) |
| Dataset composition and revisions | [`Lucius-Morningstar/mailroom-dataset`](https://huggingface.co/datasets/Lucius-Morningstar/mailroom-dataset) on the Hugging Face Hub |
| EDA figures | [`Exios66/Mailroom-Corpus-EDA`](https://github.com/Exios66/Mailroom-Corpus-EDA) |
| Sandbox results | [`Exios66/local-mailroom-sandbox`](https://github.com/Exios66/local-mailroom-sandbox) |
| Monorepo and sync law | [`LLM-Mailroom-Services/Digital-Mailroom`](https://github.com/LLM-Mailroom-Services/Digital-Mailroom) |

### 8.2 How to verify a fact (read-only)

Read upstream files at a ref. Never check out, edit, or commit in another repository's checkout to check a fact.

```bash
git -C <llm-mailroom checkout> fetch origin --tags
git -C <llm-mailroom checkout> show origin/main:pyproject.toml | grep llm-dojo-scoring
git -C <llm-mailroom checkout> show v0.8.0:src/pipeline/gmail_intake.py | grep -n MAILROOM_GMAIL_
git -C <llm-mailroom checkout> grep -n "FULL_CORPUS_REVISION *=" origin/main -- src
```

With no local checkout, use the GitHub API:

```bash
gh api repos/Exios66/llm-mailroom/contents/pyproject.toml --jq .content | base64 -d | grep llm-dojo-scoring
```

Record the ref you read (a tag or a 7-character commit) in your commit message or handoff.

### 8.3 Dating and labelling rules

* Write a drifting fact with its date: "v0.21.0 (as of 2026-10-07)".
* A released feature names its release: "since v0.8.0".
* A feature that is merged on `llm-mailroom` `main` but not in a release reads: "unreleased on llm-mailroom `main` (after v0.8.0, as of 2026-10-07)". The short form "(unreleased on `main`)" is fine inside a page that already states the full form.
* When a release ships an unreleased feature, remove the "unreleased" label everywhere it appears (`git grep -n "unreleased on" -- docs ':!docs/changelog'`).

---

## 9. Current pins (as of 2026-10-07)

These are the facts that move most often. When one moves, update **every** file in its row in the same change, and re-date it.

| Fact | Current value | Files that state it |
| --- | --- | --- |
| llm-mailroom release | `v0.8.0`; `main` carries unreleased work (site swept against `main` `c6476f7`) | `docs/README.md`, `docs/start-here/overview.md`, `docs/repository-guides/repos/llm-mailroom.md`, `docs/pipeline-reference-llm-mailroom/configuration.md`, `docs/pipeline-reference-llm-mailroom/gmail-intake.md`, `docs/SUMMARY.md` (Changelog block) |
| llm-dojo-scoring pin | `v0.21.0` (latest tag; llm-mailroom `pyproject.toml` pins it) | `docs/start-here/overview.md`, `docs/start-here/getting-started.md`, `docs/start-here/glossary.md`, `docs/how-it-fits-together/architecture.md`, `docs/the-pipeline-in-depth/running.md`, `docs/the-pipeline-in-depth/scoring-and-metrics.md`, `docs/pipeline-reference-llm-mailroom/agents.md`, `docs/pipeline-reference-llm-mailroom/configuration.md`, `docs/pipeline-reference-llm-mailroom/operational-procedure.md`, `docs/pipeline-reference-llm-mailroom/sister-repos.md`, `docs/repository-guides/repos/llm-dojo-scoring.md` |
| Dataset pin (site) | Hub tag `v9.2` → commit `670e8bc6` | `docs/start-here/overview.md`, `docs/mailroom-dataset/mailroom-dataset.md`, `docs/mailroom-dataset/configs.md`, `docs/how-it-fits-together/architecture.md`, `docs/how-it-fits-together/data-and-corpora.md`, `docs/experiment-reports/experiment-reports.md`, `docs/pipeline-reference-llm-mailroom/sister-repos.md`, `docs/repository-guides/repos/mailroom-corpus-eda.md` |
| Dataset pin (code) | `llm-mailroom` `FULL_CORPUS_REVISION` and the sandbox `FAMILY_HF_TAG` still read `v9.1` (tag commit `bc9eab28`, data commit `ed7576b6`). SAND-37/40 results were measured on `v9.1`. Say so wherever such a result is quoted. | The `v9.2` files above, plus `docs/repository-guides/repos/eval-environment.md`, `docs/repository-guides/repos/mailroom-ml.md`, `docs/repository-guides/repos/local-mailroom-sandbox/local-mailroom-sandbox-reports.md` |

Find every copy before you change one:

```bash
git grep -n -F "v0.21.0" -- docs ':!docs/changelog'
```

Do not change version numbers inside `docs/changelog/`. They are history.

---

## 10. Recipes

Every recipe ends with §11 (check), §12 (commit and push), and §13 (verify live).

### 10.1 Add a page

1. Pick the section folder from §5.3. Create `docs/<folder>/<kebab-case-name>.md` from the skeleton in §6.1.
2. Add `* [Title](<folder>/<kebab-case-name>.md)` to `docs/SUMMARY.md` under the right `##` group, in sidebar order. The title must equal the page's H1.
3. Link to the new page from at least one related page (relative link, §7.1).
4. Run the checker. It must not report `not listed in SUMMARY.md`.

### 10.2 Move or rename a page

1. `git mv docs/<old>.md docs/<new>.md`.
2. Update its line in `docs/SUMMARY.md`.
3. Find and fix every link to the old path: `git grep -n "<old-file-name>.md" -- docs`.
4. GitBook makes **no automatic redirect**. The old URL returns 404. Say so in your handoff.

### 10.3 Delete a page

1. Remove its line from `docs/SUMMARY.md`.
2. `git rm docs/<page>.md`.
3. Remove or retarget every link to it: `git grep -n "<page-file-name>.md" -- docs`.

### 10.4 Add a sidebar section

1. Create the folder `docs/<new-section>/` and its pages.
2. Add a `## Section title` group to `docs/SUMMARY.md` at the right position, with its entries.
3. Add the folder to the layout tree in `README.md` and to the table in §5.3.

A sidebar group is **not** a GitBook *section*. Never add a section or space to `gitbook-docs.yaml` for this.

### 10.5 Add or change art

1. Put the source file in `docs/assets/` (mascot art in `docs/assets/mascot/`). `docs/assets/` is the single source of truth.
2. Copy the variant a page uses into `docs/.gitbook/assets/`. Pages reference only that copy.
3. Use `fumi.gif`, not `fumi.svg`, on the site. GitBook strips scripts and may not animate SVG.
4. The mascot set is **built** in `llm-mailroom` (`src/scripts/build_mascot.py`, from `docs/assets/mascot/source/fumi-base.png`). Mirror it here; do not fork it.
5. The favicon is set in GitBook **Customize → site icon** (upload `docs/.gitbook/assets/hoot-icon.png`). It is not a config field.

Inventories: `docs/assets/README.md` and `docs/assets/mascot/README.md`.

### 10.6 Bump a version or dataset pin

1. Verify the new value upstream (§8.2). Record the ref.
2. Update every file in the fact's row in §9. Re-date each sentence.
3. Update the table in §9 itself.
4. For the dataset pin: update `docs/mailroom-dataset/` first (counts, strata, EDA figures), then Overview and Data and corpora.
5. Remove "unreleased" labels for features that the new release ships (§8.3).

### 10.7 Regenerate the Changelog

The Changelog section (`docs/changelog/`) is generated from llm-mailroom `CHANGELOG.md` by llm-mailroom `src/scripts/sync_gitbook_changelog.py`. The full recipe, including the **four site fixes** (the only hand edits allowed), is in [`docs/about-this-site/maintaining.md#changelog`](docs/about-this-site/maintaining.md#changelog). Follow it step by step. In short:

1. Make a throwaway `git worktree` of `llm-mailroom` at the commit you mirror. Never use your own `llm-mailroom` checkout.
2. Run the generator and its `--check` in the worktree.
3. Copy `README.md`, `unreleased.md`, and `2026/*.md` into `docs/changelog/`. Never copy the generator's `SUMMARY.md`, `.gitbook.yaml`, or `.gitbook/`.
4. Apply the four site fixes.
5. Add new release pages to the Changelog block of `docs/SUMMARY.md`, newest first.
6. Remove the worktree with `git worktree remove --force` (only that worktree).

### 10.8 Change the site title

Edit `site.title`, and the section and space `title`, in `gitbook-docs.yaml`. Change nothing else in that file. Never change a `key`. Read §3 and §4 first.

### 10.9 Add or update a chart

Charts are static SVG files. GitBook strips scripts, so a chart cannot have hover tooltips. The Markdown table next to the chart is its table view. Keep that table.

When a value in a charted table changes:

1. Change the value in the page table.
2. Change the same value in the data block of `scripts/build_charts.py`. The block names its source page.
3. Run `python3 scripts/build_charts.py`. Expected: one `wrote …` line for each light and dark file.
4. Open both SVG files and look at them. Labels must not overlap or run past the edge.
5. Commit the page, the script, and the SVG files together.

To add a chart:

1. Chart only data that a page table already holds. A chart never carries a fact that the page text does not.
2. Pick the form first: bars for amounts, bands for ranges, small multiples for metrics on different scales. Never two y-axes.
3. Add a function and a data block to `scripts/build_charts.py`, and add it to `CHARTS`. Copy the existing functions: the same palette, fonts, gridlines, and legend rules.
4. Use only the palette steps in `THEMES`. They passed the dataviz `validate_palette.js` checks for both modes. A new color needs a new validator run.
5. Put the `<picture>` element (§7.2) on the page, after the table it draws.
6. Run §11. The checker confirms that the `src` and `srcset` files exist.

---

## 11. Check before you push

Run from the repository root:

```bash
uv run --no-project --with pyyaml python3 scripts/check_site.py
```

Without `uv`: `python3 -m pip install pyyaml`, then `python3 scripts/check_site.py`.

It checks:

1. `gitbook-docs.yaml` and `docs/.gitbook.yaml` parse, and the site keeps its shape (`section-1` → `mailroom-docs`, `path: /`, `./docs`).
2. Every `SUMMARY.md` entry points at a file, and every page under `docs/` is listed (`docs/assets/` and `docs/.gitbook/` excepted).
3. Every relative link and image (`src` and `srcset`) in a published page resolves to a file.
4. Every `#anchor` exists as an id on the **live** page. A missing id on a page that is unchanged against `origin/main` is an `ERROR`.

| Output | Meaning | Action |
| --- | --- | --- |
| `CHECK-OK` as the last line, exit code 0 | No errors | Continue |
| `ERROR …` lines, exit code 1 | A real defect | Fix every one. Never push with an `ERROR`. |
| `ERROR … anchor … is not on <url>, and the page is unchanged` | The target page is already live, and the id is not on it | The anchor is wrong. Copy the real id (§7.3). |
| `UNVERIFIED … (page changed on this branch)` | The target page changed in your branch, so the heading may not be live yet | Confirm it after the merge (§13). |
| `UNVERIFIED … could not fetch <url>` | The live page did not load (network, timeout, or HTTP error) | Run the checker again. If it persists, open the URL by hand. |

`--offline` skips the network. All anchors then show as `UNVERIFIED`.

Then run the style report on each page you changed (§6.3):

```bash
python3 scripts/check_style.py docs/<page>.md -v
```

Then review your own diff:

```bash
git status --short
git diff
```

* Every changed file is one you meant to change.
* `gitbook-docs.yaml` and `docs/.gitbook.yaml` are unchanged, unless the task is structural.
* No stray root content (`SUMMARY.md`, section folders, or `.gitbook/assets/` at the root; `docs/gitbook-docs.yaml`).

---

## 12. Commit, push, and pull requests

### 12.1 Stage by name

Stage only the files you changed, by name:

```bash
git add docs/start-here/overview.md docs/SUMMARY.md
```

Never use `git add -A`, `git add .`, or `git commit -a`. Another writer may share the checkout.

### 12.2 Commit messages

| Prefix | Use for |
| --- | --- |
| `GITBOOK-SITE:` | Site structure: `SUMMARY.md`, `gitbook-docs.yaml`, `docs/.gitbook.yaml`, the Changelog, site config, or the checker |
| `docs:` | Page content changes |

Write the subject in the imperative, under about 72 characters. Explain *why* in the body. Name the upstream ref you verified against. End with the attribution trailer your harness requires.

### 12.3 Direct push or pull request

* **Small content fixes:** commit to `main` and push. This is allowed (golden rule 7).
* **Larger or structural changes:** push a branch (`docs/<topic>`) and open a pull request into `main`. Mark it ready for review.

On a pull request these checks run:

| Check | Pass |
| --- | --- |
| `GitBook (./docs)` | GitBook parsed the config and the content. A failure here means the site will not update. |
| CodeRabbit | Reviews links, references, staleness, and style per `.coderabbit.yaml`. Answer every finding: fix it, or reply with the reason it stands. |
| GitGuardian | No secrets. |

Merge only when all checks pass and every review thread is resolved.

### 12.4 Edits from the GitBook editor

An edit in the GitBook web editor comes back to `main` as a commit (older ones read `GitBook: …`). Always pull before you edit. If such a commit conflicts with yours, keep the content that matches the upstream source, and keep every rule in this file.

---

## 13. Verify after the merge

GitBook republishes within a few minutes. Then:

1. **The remote config equals the local one:**

   ```bash
   git switch main && git pull --ff-only
   gh api repos/Exios66/mailroom-documentation/contents/gitbook-docs.yaml --jq .content | base64 -d | diff - gitbook-docs.yaml && echo REMOTE-OK
   ```

   Pass: `REMOTE-OK`.

2. **Each changed page is live with your change:**

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" https://mailroom-inc.gitbook.io/the-digital-mailroom/<page-url>
   curl -sL https://mailroom-inc.gitbook.io/the-digital-mailroom/<page-url>.md | grep -n "<a phrase you added>"
   ```

   Pass: `200`, and the grep prints your phrase. A `404` for a page you added means it is not in `SUMMARY.md`.

3. **Anchors you added resolve:** run the checker again (§11). Pass: no `UNVERIFIED` lines.
4. **No structure error:** the GitBook check on the merge commit is green, and the site shows your change.

---

## 14. Configuration reference

| File | Published? | Role and contract |
| --- | --- | --- |
| `gitbook-docs.yaml` (root) | No | Site-wide Git Sync config. Declares section `section-1` and space `mailroom-docs` → `./docs`. **Never change a `key`.** |
| `docs/.gitbook.yaml` | No | Space content config: `root: ./`, `readme: README.md`, `summary: SUMMARY.md` |
| `docs/SUMMARY.md` | Sidebar | **Only listed pages publish.** |
| `docs/README.md` | Yes (home) | Landing page. Header **LLM-MAILROOM** (from `SUMMARY.md`). |
| `docs/**/*.md` | Yes, if listed | Pages |
| `docs/changelog/` | Yes | Generated release notes. Regenerate, never hand-edit (four site fixes excepted). |
| `docs/.gitbook/assets/` | Served | The images pages reference: `banner.png`, `fumi.gif`, `hoot-icon.png`, and the generated `chart-*-light.svg` / `chart-*-dark.svg` files |
| `docs/assets/` | No (not listed) | Site art **source of truth** (full Fumi + Hermes set) |
| `scripts/check_site.py` | No | The pre-push checker (§11) |
| `scripts/check_style.py` | No | The STE style report (§6.3). Not a gate. |
| `scripts/build_charts.py` | No | Writes the chart SVGs from its data blocks (§10.9) |
| `plans/` | No | Implementation plans for docs work. Historical; not law. |
| `.coderabbit.yaml` | No | CodeRabbit review rules for pull requests |
| `.gitattributes` | No | `* text=auto` |
| `README.md`, `AGENTS.md` (root) | No | Repository orientation and this law |
| `.superpowers/` | No (untracked) | Local agent scratch. Never commit it. |

### `path` vs `directory` (the usual mix-up)

| Knob | Where | Meaning | Correct value |
| --- | --- | --- | --- |
| Project directory | GitBook UI | Where GitBook finds `gitbook-docs.yaml` | **empty** → repository root |
| `content.directory` | `gitbook-docs.yaml` | The **folder** the space reads | `./docs` |
| `path` | `gitbook-docs.yaml` | The **URL** after the site slug | `/` (space), `the-digital-mailroom` (section) |
| `key` | `gitbook-docs.yaml` | Stable node identity | `mailroom-docs`, `section-1`. **Never change.** |

---

## 15. Invariants and troubleshooting

### 15.1 DO

* Keep the space inside `section-1`. Keep `content.directory: ./docs`.
* Keep the site to one space.
* Keep `docs/assets/` (source) and `docs/.gitbook/assets/` (referenced copies) in sync.
* Date facts that drift.
* Run the checker before every push.

### 15.2 DO NOT

* Put a space at the top level of `site.structure` (→ §4 error).
* Change the `key` of the space or the section.
* Set `path: docs` (the home then publishes at `…/the-digital-mailroom/docs/`).
* Point `content.directory` at the repository root (`./`). That exports the whole repository as the space.
* Commit a stray root content tree (`README.md`/`SUMMARY.md` copies, section folders, `.gitbook/assets/` at the root) or a GitBook-created `docs/gitbook-docs.yaml`. Delete them.
* Change the Project directory away from the repository root.
* Hand-edit `docs/changelog/` (except the four site fixes).
* Edit, commit, or push in `llm-mailroom`, `llm-dojo-scoring`, or another repository to fix this site.
* Connect `llm-mailroom` to GitBook.

### 15.3 Troubleshooting matrix

| Symptom | Cause | Fix |
| --- | --- | --- |
| `site.structure: Root-level site spaces can only exist in a non-sections site` | Space moved to the structure root on a sections site | Put it back under `section-1.children` (§3.1, §4) |
| `Failed to parse site configuration` (general) | GitBook rejected the YAML; the last good config stays live | Fix the YAML (compare with §3.1), push, let GitBook retry |
| `GitBook (./docs)` check fails on a pull request | The config or the content does not parse | Open the check's details; fix what it names; run §11 |
| An added page does not appear (404) | Not listed in `docs/SUMMARY.md` | Add the `SUMMARY.md` line (§10.1) |
| A link to a heading scrolls nowhere | The anchor uses a GitHub id, not the GitBook id | Copy the live id (§7.3) |
| A link works on GitHub but 404s on the site | Path starts with `docs/` or `/`, or points at a file in another repository | Use a relative path from the current file, or a full GitHub URL (§7.1) |
| Image 404s on the site but renders on GitHub | Path is not relative to the page, or the file is not under `docs/` | Reference `.gitbook/assets/…` with the right `../` depth (§7.2) |
| Page header differs from its H1 | `SUMMARY.md` title differs from the H1 | Make them equal |
| Home header reads **Welcome** | Wrong `SUMMARY.md` home title | Keep `* [LLM-MAILROOM](README.md)` |
| Mermaid shows as a code block | Mermaid integration off for the space | Enable it in GitBook; the Markdown is correct |
| Duplicate content tree at the repository root | `content.directory` pointed at the root | Set `./docs`; delete the stray export and any `docs/gitbook-docs.yaml` |
| Pages publish at `…/the-digital-mailroom/docs/…` | `path` set to `docs` | Keep space `path: /` |
| A **second** site "Mailroom Inc. Docs" appears | `llm-mailroom`'s stale config is connected again | Disconnect it (§16) |

---

## 16. The `llm-mailroom` duplicate deployment (must stay retired)

`Exios66/llm-mailroom` still carries a **stale** GitBook config for the old *"Mailroom Inc. Docs"* site, with serialized-literal bugs (`path: undefined`, `content.directory: ./undefined`). Verified present on `origin/main` `c6476f7` (2026-10-07):

* `gitbook-docs.yaml` (root)
* `.gitbook.yaml` (root)
* `docs/gitbook-docs.yaml`
* `docs/.gitbook.yaml`
* `landing/` (the static landing page and duplicated mascot assets)

The mirror's `docs/` also still carries the **old site tree** (`start-here/`, `the-pipeline-in-depth/`, `how-it-fits-together/`, `mailroom-dataset/`, `repository-guides/`, `pipeline-reference-llm-mailroom/`, `about-this-site/`, `changelog/`, `constellation/`). The monorepo package does not (verified 2026-10-06: `Exios66/llm-mailroom/docs` has 28 entries, `packages/llm-mailroom/docs` has 13).

Retiring it takes two steps:

1. **GitBook UI: DONE (2026-10-06).** The operator disconnected Git Sync on the old site. Never reconnect it.
2. **Config removal: OUTSTANDING (DMR-074).** Never hand-edit the mirror. The monorepo `packages/llm-mailroom` has no GitBook config and no `landing/`, so the sync is **deletion-bearing**. It removes the five entries above **and** the old docs tree. From a `LLM-Mailroom-Services/Digital-Mailroom` checkout:

   ```bash
   python scripts/sync_packages.py status                        # dry run: read the drift first
   python scripts/sync_packages.py push --package llm-mailroom   # WITHOUT --patch (it carries deletions)
   ```

   `--patch` refuses deletion-bearing deltas (exit 5). Do not use it here. Re-baseline the sync cursor afterwards. Full law: the monorepo's `AGENTS.md §Sub-package sync`. Track it as a `general` mission via `orchestrator-governor`; plan it on the board. Never blind-push.

---

## 17. Verification and evidence contract

Before you report a change as done, you have, in this session:

* Run the checker: last line `CHECK-OK`, no `ERROR` lines (§11).
* Confirmed the YAML is sections-shaped and the keys are unchanged.
* Confirmed `REMOTE-OK` after the merge (§13).
* Opened each changed page on the live site and seen your change (§13).
* Left `git status` clean for your scope, without touching another writer's files.
* Cited the commit SHA(s) and the upstream ref(s) you verified against.

No "should work". If you could not run a command, list it and say what passing looks like.

Classify any finding as *harness* | *vendored upstream* | *operator/env* | *content*.

---

## 18. Output format (diagnostics and handoffs)

Deliver:

* **Symptom:** what the operator saw. Quote the GitBook error verbatim.
* **Root cause:** the mechanism (which file, line, or node), not a guess.
* **Severity:** blocks sync / silent wrong behavior / docs-only.
* **Fix shape:** the minimal diff to `gitbook-docs.yaml` or the `docs/` tree.
* **Verification:** the commands run, their output, and the live-site check.

When you dispatch another agent, give it three things:

* this file;
* the scope boundaries (which files it may touch);
* the evidence it must return (checker output, SHAs, live URLs).

Accept its work only with that evidence. Re-run the checker yourself on its result.

---

## 19. Harness awareness (family framework v2)

These rules apply to agent definitions across the family, not to files in this repository. This repository has no `.opencode/` or `.cursor/` folder.

* **Canonical OpenCode prompt:** edit `.opencode/agents/<roster_id>.md` in the agent's `home_package` checkout, then sync: `sandbox subagents sync --harness all --root <checkout>`.
* **Cursor stub:** the same sync writes `.cursor/agents/<roster_id>.md`.
* **Do not fork** long-lived copies in `~/.config/opencode/agents/` without syncing back. The doctor treats unsynced globals as drift.
* **Profiles in scope:** Cursor (`.cursor/agents`), OpenCode project (`.opencode/agents`), OpenCode global (`~/.config/opencode/agents`), Claude Code, Codex.
* When a harness looks wrong or drifted, launch `harness-doctor` before you spend on a deploy.

---

### TL;DR

`docs/` is the site. `SUMMARY.md` decides what publishes. `gitbook-docs.yaml` at the root maps one space inside one section to `./docs`: **never move the space to the top level, never change a key.** Anchors use GitBook ids from the live page. The Changelog is generated. Charts come from `scripts/build_charts.py`. Run `scripts/check_site.py` before every push, and check the live page after every merge. `llm-mailroom`'s GitBook copy stays disconnected.
