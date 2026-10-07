# mailroom-documentation

**The single source of truth for [The Digital Mailroom](https://mailroom-inc.gitbook.io/the-digital-mailroom/) — the published GitBook site for the LLM-Mailroom constellation.**

This repository is **docs-only**: it holds the site's content (`docs/`) and the GitBook Git Sync configuration that publishes it (`gitbook-docs.yaml` + `docs/.gitbook.yaml`). A merge to `main` republishes the live site. There is no pipeline code here — the pipeline lives in [`Exios66/llm-mailroom`](https://github.com/Exios66/llm-mailroom).

Live site: **https://mailroom-inc.gitbook.io/the-digital-mailroom/**

---

## What this repository is (and is not)

| It **is** | It **is not** |
| --- | --- |
| The source of the published GitBook site | The pipeline source — that is [`Exios66/llm-mailroom`](https://github.com/Exios66/llm-mailroom) |
| Docs-only: Markdown, the site config, and site art | A home for code, notebooks, deploy configs, or CI |
| The **one** GitBook deployment for the whole constellation | A second deployment running alongside `llm-mailroom`'s stale one |
| A standalone repository — direct commits here are expected and correct | A `packages/*` mirror of the monorepo (see [Governance](#governance)) |

> **Root files are repository-only.** GitBook reads **only** `docs/` (the space's `content.directory`). `README.md`, `AGENTS.md`, `gitbook-docs.yaml`, and `.gitattributes` at the root are **never published** — they exist so that whoever opens this repo can orient and ship safely.

---

## Repository layout

```text
mailroom-documentation/
├── gitbook-docs.yaml          # Site-wide Git Sync config. Project directory = repo root.
├── .gitattributes             # `* text=auto` (LF normalization)
├── README.md                  # THIS FILE — repo orientation (not published)
├── AGENTS.md                  # Deployment/update/config law (not published)
└── docs/                       # The entire GitBook space (content.directory: ./docs)
    ├── .gitbook.yaml          # Space content config: root ./, README.md, SUMMARY.md
    ├── README.md              # THE SITE LANDING PAGE (docs/, not root)
    ├── SUMMARY.md             # Table of contents — only listed pages are published
    ├── .gitbook/assets/       # GitBook-referenced images: banner.png, fumi.gif, hoot-icon.png
    ├── assets/                # SOURCE OF TRUTH for site art (the Fumi + Hermes set)
    │   ├── README.md          # Asset inventory
    │   ├── banner.png         # Masthead banner
    │   ├── mailroom-pipeline.svg
    │   ├── fumi/fumi.gif      # GitBook home copy of Fumi
    │   └── mascot/            # fumi.svg · fumi.gif · fumi.png · fumi-icon.png
    │       │                  #   fumi-sheet.png · hoot-icon.png (Hermes)
    │       ├── source/fumi-base.png   # the base sprite everything is built from
    │       └── README.md
    ├── start-here/            # ┐
    ├── the-pipeline-in-depth/ # │
    ├── how-it-fits-together/  # │
    ├── mailroom-dataset/      # ├─ Section folders → the site's sidebar sections
    ├── experiment-reports/    # │
    ├── repository-guides/     # │
    ├── pipeline-reference-llm-mailroom/
    └── about-this-site/       # ┘  maintaining.md = the deep runbook for this site
```

**The `docs/` section folders become the sidebar sections**, in the order defined by `docs/SUMMARY.md`. `docs/README.md` is the landing page (`* [LLM-MAILROOM](README.md)` — the link title becomes the page header).

---

## How the site is deployed

One site, one space, one section. GitBook **Git Sync** reads the repository and publishes straight from `docs/`:

```text
main branch
   │
   ▼
gitbook-docs.yaml  (repository root = GitBook "Project directory")
   │
   └── section-1  (title "The Digital Mailroom", default: true)   ← sections site
         └── space  mailroom-docs  (path: /)                      ← the one space
               └── content.directory: ./docs
                     ├── docs/README.md   → landing page
                     └── docs/SUMMARY.md  → sidebar / navigation
```

`gitbook-docs.yaml` (the exact live config):

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

The three knobs people confuse (only `path` is a URL):

| Knob | Where | Meaning | Correct value |
| --- | --- | --- | --- |
| Project directory | GitBook UI | Where GitBook looks for `gitbook-docs.yaml` | **empty** (repository root) |
| `content.directory` | `gitbook-docs.yaml` | The **folder** the space reads, relative to the Project directory | `./docs` |
| `path` | `gitbook-docs.yaml` | The **URL slug** after the site slug | `/` (site home) |
| space `key` | `gitbook-docs.yaml` | Stable node identity — never change it | `mailroom-docs` |
| section `key` | `gitbook-docs.yaml` | Stable node identity — never change it | `section-1` |

> **The one hard rule:** this is a **sections site**. A site that has a section **cannot** list a space at the top level of `site.structure`. The space must always stay inside `section-1`. Breaking this produces `site.structure: Root-level site spaces can only exist in a non-sections site` and GitBook refuses the whole update. See [Troubleshooting](#troubleshooting-known-failure-modes).

---

## Editing the docs

1. **Every page must be listed in `docs/SUMMARY.md`.** A file that is not listed is not published. This is the single most common "my page is missing" cause.
2. **Use relative links between site pages** (`../mailroom-dataset/mailroom-dataset.md`) and **full GitHub URLs** for anything in another repository.
3. **Link, don't copy.** Each repository's own README/docs stay canonical; a guide here summarizes and links, never duplicates.
4. **Date facts that drift.** Versions, pins, and counts carry an "as of" date.
5. **Assets:** `docs/assets/` is the source of truth; `docs/.gitbook/assets/` holds the copies GitBook pages actually reference. Keep them in sync when art changes.
6. **Never hand-edit the generated Changelog** — regenerate it (recipe below).

### Common tasks

| Task | Do this |
| --- | --- |
| **Add a page** | Create the `.md` under the right `docs/<section>/` folder, add a line to `docs/SUMMARY.md`, push to `main`. |
| **Move/rename a page** | Move the file, update its `SUMMARY.md` line and any relative links, push. (GitBook follows the path, not the file — no redirect is automatic.) |
| **Add or refresh art** | Drop the file in `docs/assets/` (or `docs/assets/mascot/`), copy the GitBook-referenced variant into `docs/.gitbook/assets/`, update the page's relative `src`, push. Regenerating the mascot itself is done in `llm-mailroom` (`src/scripts/build_mascot.py`). |
| **Change the site title** | Edit `site.title` (and the section/first space `title`) in `gitbook-docs.yaml`. Do **not** touch any `key`. |
| **Set the favicon** | GitBook **Customize → site icon** (upload `docs/.gitbook/assets/hoot-icon.png`). It is not a config field. |
| **Bump the dataset pin** | Follow the [Maintaining this site](docs/about-this-site/maintaining.md) guide: `mailroom-dataset/` first, then `Overview` and `Data and corpora`. |
| **Regenerate the Changelog** | In `llm-mailroom`: `PYTHONPATH=src python src/scripts/sync_gitbook_changelog.py` (`--check` is the guard). |

---

## Assets (Fumi + Hermes)

The full mascot library is mirrored here from [`Exios66/llm-mailroom`](https://github.com/Exios66/llm-mailroom)`/docs/assets/` and is the site's art source of truth:

| Path | What it is |
| --- | --- |
| `docs/assets/mascot/fumi.svg` | Animated SVG (bob, blink, heart bubble, sparkles; respects reduced-motion) |
| `docs/assets/mascot/fumi.gif` | Animated GIF, 384×464 — use where SVG won't animate |
| `docs/assets/mascot/fumi.png` · `fumi-icon.png` · `fumi-sheet.png` | Still, square avatar, and the 32-frame sheet |
| `docs/assets/mascot/hoot-icon.png` | **Hermes**, the pixel owl — also the GitBook Customize site icon |
| `docs/assets/mascot/source/fumi-base.png` | The 62×107 base sprite everything is built from |
| `docs/assets/banner.png` · `mailroom-pipeline.svg` · `fumi/fumi.gif` | Masthead, pipeline diagram, home Fumi GIF |
| `docs/.gitbook/assets/` | The three copies pages reference: `banner.png`, `fumi.gif`, `hoot-icon.png` |

GitBook strips scripts and may not animate SVG — on the site use the **GIF**. The home header is **LLM-MAILROOM** only; Fumi appears twice (on duty, then Meet Fumi).

---

## Troubleshooting: known failure modes

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Failed to parse site configuration — site.structure: Root-level site spaces can only exist in a non-sections site` | The `mailroom-docs` space was moved to the **top level** of `site.structure`, but this is a **sections** site. | Put the space back inside `section-1.children` (see [How the site is deployed](#how-the-site-is-deployed)). Do not re-flatten. |
| `Failed to parse site configuration` (general) | GitBook rejected `gitbook-docs.yaml`; the **last good config stays live**, so the site keeps serving but stops updating. | Fix the config and push; GitBook retries on the next sync. |
| A page you added does not appear | It is not listed in `docs/SUMMARY.md`. | Add the `SUMMARY.md` line. |
| The home page header reads **Welcome** instead of **LLM-MAILROOM** | The `SUMMARY.md` landing link title is wrong. | Keep it `* [LLM-MAILROOM](README.md)`. |
| A whole duplicate of the content tree reappears at the repo root (`README.md`, `SUMMARY.md`, section folders, `.gitbook/assets/`) | `content.directory` was pointed at the repository root instead of `./docs`, so GitBook exported the root as the space. | Set `content.directory: ./docs`, delete the stray root export, and delete any `docs/gitbook-docs.yaml` GitBook re-creates. |
| Pages publish at `…/the-digital-mailroom/docs/…` instead of the site root | `path` was set to `docs`. | Keep the **space** `path: /`. `path` is a URL slug, not the content folder. |
| A **second** site titled "Mailroom Inc. Docs" exists | `Exios66/llm-mailroom` also carries a GitBook config and is/was connected to GitBook. | This repo is the **only** deployment. Disconnect the GitBook Git Sync on `llm-mailroom` and retire its config (see `AGENTS.md`). |
| Images render on GitHub but not on the site | The path is repo-relative but GitBook resolves from `docs/`. | Reference `.gitbook/assets/…` from within `docs/`, and keep the file in `docs/.gitbook/assets/`. |

---

## Governance

- **This repository is standalone.** It is **not** a `packages/*` mirror of `LLM-Mailroom-Services/Digital-Mailroom`, so direct commits to `main` are the correct workflow here.
- **`Exios66/llm-mailroom` *is* a monorepo mirror.** Do not hand-edit it. Changes to `llm-mailroom` (including retiring its stale GitBook config) propagate from the monorepo with `scripts/sync_packages.py push --package llm-mailroom` (deletion-bearing deltas — **without** `--patch`). Full law: the monorepo's `AGENTS.md §Sub-package sync`.
- **Deployment and configuration law lives in [`AGENTS.md`](AGENTS.md).** Read it before changing `gitbook-docs.yaml` or the `docs/` tree.

---

## Related files

- [`gitbook-docs.yaml`](gitbook-docs.yaml) — site-wide Git Sync config (repository root = Project directory)
- [`docs/.gitbook.yaml`](docs/.gitbook.yaml) — the `docs/` space's content config
- [`docs/README.md`](docs/README.md) — the published landing page
- [`docs/SUMMARY.md`](docs/SUMMARY.md) — the published table of contents
- [`docs/about-this-site/maintaining.md`](docs/about-this-site/maintaining.md) — the deep, published runbook for this site
- [`docs/assets/README.md`](docs/assets/README.md) · [`docs/assets/mascot/README.md`](docs/assets/mascot/README.md) — asset inventory
- [`AGENTS.md`](AGENTS.md) — how the site is deployed, updated, and configured (and how not to break it)
- [`Exios66/llm-mailroom`](https://github.com/Exios66/llm-mailroom) — the pipeline this site documents
