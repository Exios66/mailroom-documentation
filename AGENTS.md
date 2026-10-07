# AGENTS.md

**Operating law for `Exios66/mailroom-documentation` — the repository that deploys, updates, and configures [The Digital Mailroom](https://mailroom-inc.gitbook.io/the-digital-mailroom/) GitBook site.**

Read this before touching `gitbook-docs.yaml` or the `docs/` tree. It exists so the site's deployment does not break the way it has before (twice: commits `6ac7930`, `ffc4a3f`).

- **Scope of this repo:** documentation only — the GitBook site content and its Git Sync config. No pipeline code.
- **Companion docs:** `README.md` (repo orientation) and the *published* runbook `docs/about-this-site/maintaining.md`.
- **Pipeline repository:** [`Exios66/llm-mailroom`](https://github.com/Exios66/llm-mailroom) — described by this site, described by this repo.

---

## 0. The golden rules (memorize these)

1. **One site, one space, one section.** This is a **sections** site. The `mailroom-docs` space must **always** live inside `section-1`. **Never** list a space at the top level of `site.structure`.
2. **Never change a `key`.** `mailroom-docs` and `section-1` are permanent node identities. Changing a key makes GitBook delete the old node and import a *new* one — new IDs, broken links, orphaned content.
3. **`content.directory` is a folder; `path` is a URL.** `content.directory: ./docs`, space `path: /`. Never set `path: docs`.
4. **The Project directory is the repository root and must be left empty** in the GitBook UI. `gitbook-docs.yaml` lives at the root.
5. **Only pages listed in `docs/SUMMARY.md` are published.** If you added a page and it is missing, this is why.
6. **This repo is the only GitBook deployment.** `Exios66/llm-mailroom` still carries a stale, broken GitBook config — never connect it.
7. **Direct commits to `main` are correct here.** This repo is standalone, not a `packages/*` mirror. `llm-mailroom`, however, *is* a mirror — propagate to it only via the monorepo (`sync_packages.py`), never by hand.

---

## 1. Startup ritual (every session that touches this repo)

1. `git fetch origin && git status -sb` — confirm you are on `main`, up to date, and aware of any uncommitted work (another writer may share this checkout).
2. Read `gitbook-docs.yaml` and `docs/.gitbook.yaml` **before** editing anything structural.
3. State which harness you are running under and which checkout is canonical.
4. Prefer read-only inspection and validating YAML before pushing.

---

## 2. Deployment model (authoritative)

GitBook **Git Sync** watches `main` and republishes the site on every merge. There is no CI and no build step — the repo *is* the site.

```text
Exios66/mailroom-documentation @ main
   │   GitBook "Project directory" = repository root (leave empty in the UI)
   ▼
gitbook-docs.yaml
   └── section-1   (title "The Digital Mailroom", path the-digital-mailroom, default: true)
         └── space  mailroom-docs  (path: /, default: true)
               └── content.directory: ./docs
                     ├── docs/README.md    → landing page
                     ├── docs/SUMMARY.md   → sidebar
                     └── docs/**/*.md       → pages (only if listed in SUMMARY.md)
```

### The exact live `gitbook-docs.yaml`

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

### Content config — `docs/.gitbook.yaml`

```yaml
root: ./

structure:
  readme: README.md
  summary: SUMMARY.md
```

`root: ./` is relative to the space's mapped directory (`./docs`), so `README.md`/`SUMMARY.md` resolve to `docs/README.md` and `docs/SUMMARY.md`.

### One-time connection (GitBook UI, for the record)

1. Open the site's space (`mailroom-docs`, titled **The Digital Mailroom**).
2. **Configure → GitHub Sync**; install the GitBook GitHub app on **`Exios66/mailroom-documentation`** (this repo — **not** `llm-mailroom`).
3. Branch `main`; **leave Project directory empty** (repository root).
4. First sync: **GitHub → GitBook**.

---

## 3. The one hard rule: sections vs. root spaces

GitBook types a site as either **`sections`** (has ≥1 section; every space lives inside one) or **`siteSpaces`** (flat; spaces at the top level). **Never both.** This site is `sections` (a site is born with a section), so:

> **A space at the top level of `site.structure` is illegal here.**

### The exact error you will see, and the fix

```text
Error while updating site
Failed to parse site configuration — site.structure:
Root-level site spaces can only exist in a non-sections site
```

**What it means:** `gitbook-docs.yaml` declares `mailroom-docs` at the structure root while the site is sections-typed. GitBook **refuses the whole update and keeps the last good config** — the site keeps serving, but stops updating until fixed.

**The fix (exactly what `6ac7930` and `ffc4a3f` did):** nest the space back inside `section-1.children`, using the **unchanged keys** (`section-1`, `mailroom-docs`). Restore the exact YAML in §2.

**Do not** "clean up" by flattening the space to the root. If you genuinely want a flat site, you must first delete the section in the GitBook **Site structure** UI — only then is a root-level space legal — and that is a deliberate, coordinated change, not a docs edit.

---

## 4. Update workflow (shipping a docs change)

1. Edit Markdown under `docs/` only (`docs/README.md` is the landing page).
2. Register every new page in `docs/SUMMARY.md`; keep section order = sidebar order.
3. Use **relative links** between pages (they all live under `docs/`) and **full GitHub URLs** for other repos.
4. Only touch `gitbook-docs.yaml` for a real structural change — and re-read §0/§3 first.
5. Commit with the repo's `GITBOOK-SITE:` style when the change is site-structural.
6. Push to `main`. GitBook re-syncs and republishes (`pages publish at …/the-digital-mailroom/{page}`).
7. Verify on the live site that the page exists, links resolve, and the structure error is absent.

---

## 5. Configuration reference

| File | Role | Contract |
| --- | --- | --- |
| `gitbook-docs.yaml` (root) | Site-wide Git Sync config | Finds the site by the repo root Project directory; declares section `section-1` and space `mailroom-docs` → `./docs`. **Never change a `key`.** |
| `docs/.gitbook.yaml` | Space content config | `root: ./`, `readme: README.md`, `summary: SUMMARY.md`. |
| `.gitattributes` (root) | Line endings | `* text=auto`. |
| `docs/SUMMARY.md` | Site navigation | **Only listed pages publish.** |
| `docs/.gitbook/assets/` | GitBook-referenced images | `banner.png`, `fumi.gif`, `hoot-icon.png` — the copies pages reference. |
| `docs/assets/` | Site art **source of truth** | Full Fumi + Hermes set; see `docs/assets/README.md`. |
| `docs/changelog/` | Release notes (Changelog section) | Generated release notes; regenerate, never hand-edit. |
| `README.md` / `AGENTS.md` (root) | Repo-only | **Never published** (outside `content.directory`). |

### `path` vs `directory` (the usual mix-up)

| Knob | Meaning | Correct value |
| --- | --- | --- |
| Project directory (UI) | where GitBook finds `gitbook-docs.yaml` | **empty** → repository root |
| `content.directory` | the **folder** the space reads | `./docs` |
| `path` | the **URL** after the site slug | `/` (space), `the-digital-mailroom` (section) |
| `key` | stable node identity | `mailroom-docs`, `section-1` — **never change** |

---

## 6. Invariants — DO / DO NOT

**DO**

- Keep the space inside `section-1`; keep `content.directory: ./docs`.
- Keep the site to one space unless a real multi-space change is intended and the YAML is updated to match the UI.
- Keep `docs/assets/` (source) and `docs/.gitbook/assets/` (referenced copies) in sync.
- Set the favicon in GitBook **Customize** (upload `docs/.gitbook/assets/hoot-icon.png`) — it is not a config field.
- Date facts that drift (versions, pins, counts).

**DO NOT**

- List a space at the top level of `site.structure` (→ §3 error).
- Change the `key` of the space or section (→ GitBook deletes + reimports; new IDs; broken links).
- Set `path: docs` (→ home publishes at `…/the-digital-mailroom/docs/`).
- Point `content.directory` at the repository root (`./`) — that re-exports the whole repo as the space.
- Commit a stray root content tree (`README.md`, `SUMMARY.md`, section folders, `.gitbook/assets/` at the root) or a GitBook-recreated `docs/gitbook-docs.yaml` — delete them.
- Change the Project directory away from the repository root.

---

## 7. Troubleshooting matrix

| Symptom | Mechanism | Fix |
| --- | --- | --- |
| `site.structure: Root-level site spaces can only exist in a non-sections site` | Space flattened to the structure root on a sections site | Re-nest under `section-1.children` (§2/§3) |
| `Failed to parse site configuration` (general) | Config rejected; last good config stays live | Fix the YAML, push, let GitBook retry |
| Added page does not appear | Not listed in `docs/SUMMARY.md` | Add the SUMMARY line |
| Home header reads **Welcome** | `SUMMARY.md` landing link title wrong | Keep `* [LLM-MAILROOM](README.md)` |
| Duplicate content tree reappears at repo root | `content.directory` pointed at root | Set `./docs`; delete the stray export + any stray `docs/gitbook-docs.yaml` |
| Pages publish at `…/the-digital-mailroom/docs/…` | `path` set to `docs` | Keep space `path: /` |
| A **second** site "Mailroom Inc. Docs" exists | `llm-mailroom`'s stale GitBook config is connected | Disconnect it and retire its config (§8) |
| Image 404s on the site but renders on GitHub | Path is repo-relative; GitBook resolves from `docs/` | Reference `.gitbook/assets/…`; keep the file under `docs/.gitbook/assets/` |

---

## 8. The `llm-mailroom` duplicate deployment (must stay retired)

`Exios66/llm-mailroom` still contains a **stale** GitBook config for the old *"Mailroom Inc. Docs"* site, including serialized-literal bugs (`path: undefined`, `content.directory: ./undefined`):

- `gitbook-docs.yaml` (root)
- `.gitbook.yaml` (root)
- `docs/gitbook-docs.yaml`
- `docs/.gitbook.yaml`
- `landing/` (the static landing page + duplicated mascot assets)

**Scope warning (verified 2026-10-06).** The mirror's `docs/` also still carries the **old site tree** — `start-here/`, `the-pipeline-in-depth/`, `how-it-fits-together/`, `mailroom-dataset/`, `repository-guides/`, `pipeline-reference-llm-mailroom/`, `about-this-site/`, `changelog/`, `constellation/` — which the monorepo package does **not** (`Exios66/llm-mailroom/docs` = 28 entries vs `packages/llm-mailroom/docs` = 13). The deletion-bearing sync removes **both** the five config entries above *and* that whole tree, so **run `status` first and read the drift before pushing** — never blind-push.

**This repo is the one deployment. `llm-mailroom` must not be connected to GitBook.** Retiring its copy takes two steps — **step 1 is done; step 2 is outstanding** (the mirror still carries all five entries above):

1. **GitBook UI — DONE (2026-10-06).** The operator disconnected the Git Sync integration on the old *"Mailroom Inc. Docs"* site. Never reconnect it.
2. **Config removal (DMR-074 — never hand-edit the mirror):** the monorepo `packages/llm-mailroom` carries **no** GitBook config and **no** `landing/`, so this is a **deletion-bearing** delta. From a `LLM-Mailroom-Services/Digital-Mailroom` checkout:

   ```bash
   python scripts/sync_packages.py status                        # DRY RUN — read the drift first
   python scripts/sync_packages.py push --package llm-mailroom   # WITHOUT --patch (adds deletions)
   ```

   `--patch` refuses deletion-bearing deltas (exit 5) — do not use it here. Then re-baseline the sync cursor. Full law: the monorepo's `AGENTS.md §Sub-package sync`.

Track this as a `general` mission via `orchestrator-governor`; it is a sync unit, so plan it on the board.

---

## 9. Dataset pin & generated content

- **The pinned corpus revision** is a dated fact. Current: Hub tag **`v9.2` → `670e8bc6`** (as of 2026-10-06). It appears in `docs/start-here/overview.md`, `docs/mailroom-dataset/mailroom-dataset.md`, `docs/mailroom-dataset/configs.md`, and cross-references under `how-it-fits-together/` and `repository-guides/`. When it moves, update them together and re-date the fact. As of 2026-10-07 the `llm-mailroom` mirror (`FULL_CORPUS_REVISION`) and the sandbox (`FAMILY_HF_TAG`) still read the predecessor tag `v9.1` (commit `bc9eab28`, data commit `ed7576b6`), and SAND-37/40 results were measured on it — say so wherever a result is quoted.
- **Changelog:** this site has a Changelog section under `docs/changelog/`. It is generated from llm-mailroom `CHANGELOG.md` with `sync_gitbook_changelog.py`. Never hand-edit it, except for the three site fixes in [`docs/about-this-site/maintaining.md#changelog`](docs/about-this-site/maintaining.md#changelog). Do not copy the generator's `SUMMARY.md`, `.gitbook.yaml`, or `.gitbook/` into this repo.

---

## 10. Asset discipline

- `docs/assets/` is the **single source of truth** for site art (the full Fumi + Hermes set). `docs/.gitbook/assets/` holds the three copies pages reference.
- The mascot set is **built** in `llm-mailroom` (`src/scripts/build_mascot.py`, from `docs/assets/mascot/source/fumi-base.png`) and mirrored here — mirror it, don't fork it.
- GitBook strips scripts and may not animate SVG: use `fumi.gif` on the site.
- Full size/hash table: `docs/assets/README.md` and `docs/assets/mascot/README.md`.

---

## 11. Verification & evidence contract

Before reporting a docs change done:

- **YAML is valid and sections-shaped:** the space is inside `section-1`; no top-level space; keys unchanged.
- **Remote matches local:** `gh api repos/Exios66/mailroom-documentation/contents/gitbook-docs.yaml --jq .content | base64 -d | diff - gitbook-docs.yaml`.
- **Structure error is gone** on the live site; the changed page renders and its links resolve.
- **`git status` is clean for your scope** — do not sweep up another writer's uncommitted work; stage only your files.
- Cite the commit SHA(s). No "should work" without verification.

Classify any finding as *harness* | *vendored upstream* | *operator/env* | *content*. If you cannot run commands, list the exact commands and what passing looks like.

---

## 12. Output format (diagnostics & handoffs)

Deliver:

- **Symptom** — what the operator saw (quote the GitBook error verbatim).
- **Root cause** — the mechanism (which node/config line), not vibes.
- **Severity** — blocks sync / silent wrong behavior / docs-only.
- **Fix shape** — the minimal diff to `gitbook-docs.yaml` / the docs tree.
- **Verification** — the commands and the live-site check that must pass.

When dispatching to another subagent, include scope boundaries and the evidence they must produce before you accept the handoff.

---

## 13. Harness awareness (family framework v2)

- **Canonical OpenCode prompt** for any agent here: edit `.opencode/agents/<roster_id>.md` in the agent's `home_package` checkout, then sync — `sandbox subagents sync --harness all --root <checkout>`.
- **Cursor stub**: written to `.cursor/agents/<roster_id>.md` by the same sync.
- **Do not fork** long-lived copies in `~/.config/opencode/agents/` without syncing back — the doctor treats unsynced globals as drift.
- **Profiles in scope**: Cursor (`.cursor/agents`), OpenCode project (`.opencode/agents`), OpenCode global (`~/.config/opencode/agents`), Claude Code / Codex.
- When any harness looks wrong or drifted, launch `harness-doctor` before spending on a deploy.

---

### TL;DR

`docs/` is the site; `SUMMARY.md` is the gate; `gitbook-docs.yaml` at the root maps one space inside one section to `./docs`; **never flatten the space to the root, never change a key**; and `llm-mailroom`'s GitBook copy stays disconnected.
