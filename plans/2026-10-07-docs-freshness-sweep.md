# Docs Freshness Sweep (dojo v0.21.0 + llm-mailroom post-v0.8.0) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring every page of The Digital Mailroom GitBook site in line with llm-dojo-scoring v0.21.0 and llm-mailroom `main` as of 2026-10-07, on top of the open Changelog PR (Exios66/mailroom-documentation#4), then merge that PR.

**Architecture:** Docs-only edits under `docs/` plus the repo-law files (`AGENTS.md`, `README.md`). All work lands as commits on the PR #4 branch `docs/add-changelog`; the PR merges to `main` at the end and GitBook Git Sync republishes. There is no build; "tests" are grep/diff/YAML checks with exact expected output.

**Tech Stack:** Markdown (GitBook flavour), GitBook Git Sync, `git`, `gh`, `grep`/`rg`, Python 3.11 (only to run llm-mailroom's changelog generator and a YAML check).

**Spec:** The user request in this session (2026-10-07): "scan the GitBook site, identify all stale claims, out-of-date references, docs out of date with the new version pins of llm-mailroom and llm-dojo-scoring, and the most recent enhancements and commits; build on the Changelog PR and merge it when done." The scan findings below are the spec's concrete content. `AGENTS.md` (repo root) is binding law for every task.

## Source pins (read upstream facts ONLY from these)

| Repo | Ref | How to read |
| --- | --- | --- |
| llm-mailroom | `origin/main` = `578db29` (version `0.8.0`, 64 commits past tag `v0.8.0`; pins dojo `v0.21.0`) | `git -C /Users/luciusjmorningstar/Downloads/llm-mailroom show 578db29:<path>` |
| llm-dojo-scoring | tag `v0.21.0` (release commit `cc0817c`, `main` tip `6a3053c`) | `git -C /Users/luciusjmorningstar/Downloads/llm-dojo-scoring show v0.21.0:<path>` |

Both local checkouts are on unrelated feature branches. **Never** check out, edit, or commit in them; read with `git show <ref>:<path>` only.

## Global Constraints

- Work on branch `docs/add-changelog` in `/Users/luciusjmorningstar/Downloads/mailroom-documentation`. Do not commit to `main` directly in this plan.
- Never touch `gitbook-docs.yaml` or `docs/.gitbook.yaml`. Never change a `key`.
- Every new or moved page is listed in `docs/SUMMARY.md`.
- Relative links between site pages; full GitHub URLs for other repos. GitHub links to a version use the tag in the URL (`blob/v0.21.0/...`).
- Dated facts carry "as of 2026-10-07".
- Features merged to llm-mailroom `main` after `v0.8.0` are described as **"unreleased on llm-mailroom `main` (after v0.8.0, as of 2026-10-07)"** — never as part of v0.8.0.
- llm-mailroom version stays **v0.8.0** everywhere (no new tag exists). Corpus pin facts stay as they are (`v9.2` → `670e8bc6` published; llm-mailroom `FULL_CORPUS_REVISION = "v9.1"`, verified at `578db29`).
- Other repos' dojo pins are unchanged and verified 2026-10-07: llm-entity-extraction `v0.16.0`, agent-mailroom `v0.16.0`, eval-environment `v0.15.0` (transitive), local-mailroom-sandbox `v0.15.0`. Do not bump them.
- Writing style (from `.coderabbit.yaml`): Simplified Technical English — imperative steps, short sentences, present tense, no contractions. Use GitBook blocks only where neighbouring pages already do.
- Stage only the files the task names (`git add <paths>`, never `git add -A`). The plan file `plans/2026-10-07-docs-freshness-sweep.md` lands in its own PR; implementers never edit or stage it.
- Commit messages: `docs: …` for content; `GITBOOK-SITE: …` for site-structural changes (SUMMARY, repo law). End every commit message with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Historical vs current version strings.** A blind `v0.19.1 → v0.21.0` replace corrupts history (changelog entries, "v0.19.1 added …" bullets, eval runs that resolved v0.15.0). Expected: only *current-state* claims move; Task 2's grep allowlist pins which `0.19.1` hits may remain.
2. **Unreleased features presented as released.** Gmail hardening and the free-quota breaker are on `main`, not in v0.8.0. Expected: every new section carries the unreleased label (Tasks 4, 5 check with grep).
3. **Relative links from nested changelog pages.** `docs/changelog/2026/*.md` is two levels deep; a link copied from `docs/changelog/README.md` breaks. Expected: Task 1 replaces the generator hint with plain text (no relative link) and Task 6 link-checks every relative link.
4. **Repo law contradicting the merged site.** `AGENTS.md` §6/§9, `README.md`, and `maintaining.md` say "no Changelog section". Expected: after merge, no law file forbids what the site contains (Task 1 grep).
5. **Upstream doc text copied with upstream-only paths.** llm-mailroom docs link `docs/…` paths and `../src/…` relative files that do not exist here. Expected: ported text uses this site's relative pages and full `https://github.com/Exios66/llm-mailroom/blob/main/src/...` URLs (Task 6 link check).

---

### Task 0: Branch setup (no commit)

- [ ] **Step 1:** Run
  ```bash
  cd /Users/luciusjmorningstar/Downloads/mailroom-documentation && git fetch origin && git status -sb && git switch docs/add-changelog && git pull --ff-only && git merge-base --is-ancestor origin/main HEAD && echo BASE-OK
  ```
  Expected: clean tree, on `docs/add-changelog`, prints `BASE-OK`. If `BASE-OK` is missing, run `git merge origin/main` (no rebase; the PR is public) and resolve; report to the reviewer.

---

### Task 1: Changelog section — regenerate from current CHANGELOG.md and make repo law allow it

The PR copied `docs/changelog/` from llm-mailroom's generated pages, which lag `CHANGELOG.md` at `578db29` (the Unreleased page lacks the dojo v0.21.0 pin entry and the `bump_dojo_scoring.py` / `test_dojo_v019_wiring.py` fixes). Its hint tells readers to run a script in another repo, and its README links the retired *Mailroom Inc. Docs* URL.

**Files:**
- Modify: `docs/changelog/README.md`, `docs/changelog/unreleased.md`, `docs/changelog/2026/*.md` (regenerated)
- Modify: `docs/SUMMARY.md` (only if the generated page set differs from the current Changelog block, lines 88–106)
- Modify: `AGENTS.md` §5 table, §6 DO NOT bullet "Add a `docs/changelog/` tree…", §9 "Changelog" bullet, TL;DR if needed
- Modify: `README.md` lines ~121 and ~133 (Changelog rules/recipe)
- Modify: `docs/about-this-site/maintaining.md` line ~43 paragraph, the section-folders row (~line 39), the "`llm-mailroom` `CHANGELOG.md` changes" row (~line 95)

**Interfaces:**
- Produces: a `## Changelog` heading in `docs/about-this-site/maintaining.md` (anchor `#changelog`) holding the regeneration recipe below. Task 2 and Task 6 rely on it.

- [ ] **Step 1: Generate into a throwaway worktree**
  ```bash
  S=/private/tmp/claude-501/-Users-luciusjmorningstar-Downloads-mailroom-documentation/89d9f1be-ed48-4bba-9e9c-142a66a0a964/scratchpad
  git -C /Users/luciusjmorningstar/Downloads/llm-mailroom worktree add --detach $S/mr-578 578db29
  cd $S/mr-578 && PYTHONPATH=src python3 src/scripts/sync_gitbook_changelog.py && PYTHONPATH=src python3 src/scripts/sync_gitbook_changelog.py --check
  ```
  Expected: `wrote N pages under docs/changelog/` then `ok: N GitBook changelog pages match CHANGELOG.md`.

- [ ] **Step 2: Copy pages, skipping the nested-space files**
  Copy `README.md`, `unreleased.md`, and `2026/*.md` from `$S/mr-578/docs/changelog/` into `docs/changelog/`. Do **not** copy `SUMMARY.md`, `.gitbook.yaml`, or `.gitbook/`.

- [ ] **Step 3: Apply the two site fixes (the only edits ever made to generated pages)**
  ```bash
  cd /Users/luciusjmorningstar/Downloads/mailroom-documentation
  find docs/changelog -name '*.md' -exec sed -i '' \
    -e 's#^pages\. Regenerate with `PYTHONPATH=src python src/scripts/sync_gitbook_changelog.py`\.$#pages. To regenerate them, follow "Changelog" in the Maintaining this site page.#' \
    -e 's#Pipeline docs: \[https://mailroom-inc.gitbook.io/mailroom-inc.-docs/\](https://mailroom-inc.gitbook.io/mailroom-inc.-docs/)#Pipeline docs: [The Digital Mailroom](https://mailroom-inc.gitbook.io/the-digital-mailroom/)#' {} +
  ```
  Release-entry text that mentions *Mailroom Inc. Docs* is history from `CHANGELOG.md`; leave it.

- [ ] **Step 4: Verify content**
  ```bash
  S=/private/tmp/claude-501/-Users-luciusjmorningstar-Downloads-mailroom-documentation/89d9f1be-ed48-4bba-9e9c-142a66a0a964/scratchpad
  grep -c 'v0.21.0' docs/changelog/unreleased.md          # expect >= 1
  grep -rn 'Regenerate with `PYTHONPATH' docs/changelog    # expect no output
  grep -n 'Pipeline docs:' docs/changelog/README.md        # expect the-digital-mailroom URL
  ls docs/changelog/2026 | sed 's/\.md$//' | sort > $S/gen; grep -oE 'changelog/2026/[^)]+' docs/SUMMARY.md | sed 's#changelog/2026/##;s/\.md$//' | sort > $S/sum; diff $S/gen $S/sum   # expect no output
  ```

- [ ] **Step 5: Update repo law**
  - `AGENTS.md`: delete the §6 DO NOT bullet about `docs/changelog/`; rewrite the §9 Changelog bullet to: the site has a Changelog section under `docs/changelog/`, generated from llm-mailroom `CHANGELOG.md`, never hand-edited except the two fixes in `docs/about-this-site/maintaining.md#changelog`; add a §5 table row `docs/changelog/` → "Generated release notes; regenerate, never hand-edit".
  - `docs/about-this-site/maintaining.md`: replace the "no Changelog section" paragraph with a `## Changelog` section holding Steps 1–3 above as the recipe (worktree at the llm-mailroom `main` commit being mirrored, generate, copy without `SUMMARY.md`/`.gitbook*`, apply the two fixes, update the SUMMARY Changelog block when a release page is added). Add `changelog/` to the section-folders list. Change the "`CHANGELOG.md` changes" row to "Regenerate the Changelog section (see Changelog)".
  - `README.md`: rule 6 links the recipe in `docs/about-this-site/maintaining.md#changelog`; the "Regenerate the Changelog" row states the same recipe in one line, not "In llm-mailroom: …".

- [ ] **Step 6: Verify law is consistent**
  ```bash
  grep -niE 'no changelog|has no changelog|do(es)? not exist' AGENTS.md README.md docs/about-this-site/maintaining.md   # expect no output
  ```

- [ ] **Step 7: Clean up and commit**
  ```bash
  S=/private/tmp/claude-501/-Users-luciusjmorningstar-Downloads-mailroom-documentation/89d9f1be-ed48-4bba-9e9c-142a66a0a964/scratchpad
  git -C /Users/luciusjmorningstar/Downloads/llm-mailroom worktree remove $S/mr-578
  git add docs/changelog docs/SUMMARY.md AGENTS.md README.md docs/about-this-site/maintaining.md
  git commit -m "GITBOOK-SITE: regenerate Changelog from llm-mailroom 578db29 and make repo law cover it"
  ```

---

### Task 2: Version pins — dojo v0.19.1 → v0.21.0 in current-state claims

**Files (each hit found 2026-10-07; re-grep before editing):**
- `docs/start-here/overview.md:89` — row becomes `v0.21.0 latest; llm-mailroom pins v0.21.0`. Add to the llm-mailroom row: `v0.8.0 (main carries unreleased changes; see [Changelog](../changelog/unreleased.md))`.
- `docs/start-here/getting-started.md:114` — `@v0.21.0`
- `docs/the-pipeline-in-depth/running.md:47` — `@v0.21.0`
- `docs/the-pipeline-in-depth/scoring-and-metrics.md:30, 41, 68, 286, 365, 416` — current pin `v0.21.0`; links `blob/v0.19.1/…` → `blob/v0.21.0/…`. Keep every "eval-environment resolved v0.15.0" statement.
- `docs/how-it-fits-together/architecture.md:120` — `` git pin `@v0.21.0` (as of 2026-10-07), auto-bumped ``. Rows 122 and 126 stay `@v0.16.0`.
- `docs/repository-guides/repos/llm-dojo-scoring.md:9, 30` — Latest `v0.21.0 (llm-mailroom pins v0.21.0; entity-extraction and agent-mailroom pin v0.16.0; as of 2026-10-07)`; install line `@v0.21.0`.
- `docs/pipeline-reference-llm-mailroom/sister-repos.md:3, 60, 89, 96` — current pin `v0.21.0`; line 89 command `--apply --tag v0.21.0`; line 96 "dojo v0.21.0 suites". Above the existing `v0.12.2` bullet (line 61) add two bullets, newest first:
  - **v0.21.0** — re-synced the six `production` classification prompts from llm-mailroom `6ddde73` (the five-class doctrine no longer names the MAUD/CUAD corpora); catalog `version: 0.21.0`.
  - **v0.20.0** — `production` family re-vendored from live llm-mailroom (`scripts/sync_production_prompts.py`); five specialists equal the frozen `production_prompts` v1 bytes; `reporter` is `kind: deterministic`; rows record `source_commit`; adds `llm_dojo_scoring.intents` and the exact-match `label` field type.
- `docs/pipeline-reference-llm-mailroom/agents.md:196, 270` — "Honest gap (dojo v0.21.0)".

**Interfaces:**
- Consumes: Task 1's `docs/changelog/unreleased.md` (link target in overview).

- [ ] **Step 1: Baseline** — `grep -rn '0\.19\.1' docs --include='*.md' | grep -v '^docs/changelog/'` lists the hits above.
- [ ] **Step 2: Edit** each file as listed.
- [ ] **Step 3: Verify**
  ```bash
  grep -rn '0\.19\.1' docs --include='*.md' | grep -v '^docs/changelog/'
  ```
  Expected: no output, **except** a line that states history (e.g. "v0.19.1 added…"); list any remaining line in the task report with its reason.
  ```bash
  grep -rn 'v0\.21\.0' docs --include='*.md' | grep -v '^docs/changelog/' | wc -l   # expect >= 14
  ```
- [ ] **Step 4: Commit** — `git add` the eight files; `git commit -m "docs: bump current dojo pin claims to v0.21.0 (llm-mailroom 578db29)"`.

---

### Task 3: Dojo-sync content — `label` field type, intent vocabulary, prompt catalog

Source facts (verify with `git show`): llm-mailroom `578db29:src/config/taxonomy.yaml` sets `intent: label` for `corporate_record`, `correspondence`, `insurance_claim` and keeps `intent: name` for `merger_agreement`; dojo `v0.21.0:llm_dojo_scoring/field_scoring.py` `score_label_field` = exact match after canonicalization, no partial credit; `578db29:src/llm/frozen_v1/__init__.py` and `README.md` (served from the dojo `production_prompts` catalog; `.txt` files superseded and not packaged); commit `54e246a` (classification prompts describe merger/contract classes without corpus names).

**Files:**
- `docs/the-pipeline-in-depth/extraction-schemas.md` — scoring-type column of the `intent` rows at lines ~154, ~188, ~230 → `` `label` ``; line ~119 (merger) stays `` `name` ``. In the intent hardening note (~line 396) add one sentence: the scorer canonicalizes `intent` on both sides through `normalize_intent` because the field type is `label` (dojo ≥ v0.20.0).
- `docs/the-pipeline-in-depth/scoring-and-metrics.md` — add `intent: label` to the example field-type block (~line 43–60) and a `label` row to the per-field rule table (~line 70): "Canonicalize both sides, then exact match. No partial credit. `score_label_field`."
- `docs/repository-guides/repos/llm-dojo-scoring.md` — add a `label` row to the field-type table; under "What it does" add one sentence on `llm_dojo_scoring.intents` (`INTENT_LABELS`, `normalize_intent`) and the `production` / `production_prompts` prompt catalog.
- `docs/pipeline-reference-llm-mailroom/agents.md` — line ~75: frozen v1 text is served from the dojo `production_prompts` catalog pinned in `pyproject.toml`; `src/llm/frozen_v1/lineage.json` records each prompt's sha256 and length; the `.txt` files are superseded and not packaged. Same correction wherever lines ~139 and ~168 say the prompt is read from `llm/frozen_v1/` files. In the Sorter section add: the shared five-class doctrine describes `merger_agreement` and `contract` by what they are, without naming the MAUD/CUAD corpora (llm-mailroom#102), as of 2026-10-07.
- `docs/the-pipeline-in-depth/extraction-schemas.md:44` (and any row naming `llm/frozen_v1/<file>.txt`) — same served-from-catalog correction.

- [ ] **Step 1: Baseline**
  ```bash
  grep -nE '^\| `intent`' docs/the-pipeline-in-depth/extraction-schemas.md
  grep -rnE 'frozen_v1/[a-z_]+\.txt|frozen_v1/co' docs --include='*.md' | grep -v '^docs/changelog/'
  ```
- [ ] **Step 2: Edit** as listed.
- [ ] **Step 3: Verify**
  ```bash
  grep -nE '^\| `intent`' docs/the-pipeline-in-depth/extraction-schemas.md | grep -c '`label`'   # expect 3
  grep -nE '^\| `label`' docs/the-pipeline-in-depth/scoring-and-metrics.md docs/repository-guides/repos/llm-dojo-scoring.md | wc -l   # expect 2
  grep -rn 'production_prompts' docs/pipeline-reference-llm-mailroom/agents.md | wc -l   # expect >= 1
  grep -rnE 'frozen_v1/[a-z_]+\.txt' docs --include='*.md' | grep -v '^docs/changelog/'   # expect no output unless the line says the files are superseded
  ```
- [ ] **Step 4: Commit** — `git commit -m "docs: document label field type, intent vocabulary and dojo-served frozen v1 prompts"`.

---

### Task 4: Gmail intake hardening (unreleased on main)

Source: `578db29:docs/gmail-intake.md` (sections 1, 2, 3 "Common path", 4) and `578db29:docs/configuration.md` lines 337–359, plus `CHANGELOG.md` `[Unreleased]`. None of these terms exist on the site today: DMARC, outbox, quarantine, IDLE, BODYSTRUCTURE, acknowledgment, digest.

**Files:**
- `docs/pipeline-reference-llm-mailroom/gmail-intake.md`
- `docs/pipeline-reference-llm-mailroom/configuration.md` (Gmail env-var table, ~lines 353–369, and the upload table ~385)
- `docs/the-pipeline-in-depth/flowchart.md` (only where it describes echo dedup/retry; check lines containing `echo`)

**Exact values to state:**

| Item | Value |
| --- | --- |
| `MAILROOM_GMAIL_REQUIRE_DMARC` | default `1`; allowlisted sender needs Gmail's `dmarc=pass` (topmost `Authentication-Results` from `mx.google.com` only; else fail closed) |
| `MAILROOM_GMAIL_MAX_ATTEMPTS` | default `3`; then quarantine: marked `\Seen`, labelled `mailroom/failed` |
| `MAILROOM_GMAIL_MAX_REPLIES_PER_HOUR` | default `20`; caps reject, acknowledgment, digest replies per address; echoes not capped |
| `MAILROOM_GMAIL_ACKS` | default `1` |
| `MAILROOM_GMAIL_IDLE` | default `0`; opt-in IMAP IDLE; falls back to polling on any error |
| `MAILROOM_GMAIL_ALLOW_SELF` | default `0` |
| `MAILROOM_GMAIL_ALLOWED_SENDERS` | exact, case-insensitive bare address; `+tag` variants do not match (replaces "lowercased comparison") |
| Outbox | `<base>/mail_outbox.sqlite` (WAL); keys `echo:<doc_id>:<stage>`, `ack:<message_id>`, `reject:<message_id>`, `digest:<message_id>`; backoff `min(3600, 30*2^attempts)` s; `dead` after 8 attempts, never auto-revived; 300 s lease; at-least-once |
| Digest | one per multi-document email when all documents finish; partial "incomplete" digest after 6 hours |
| Skips (no reply) | auto-replies, DSN bounces, mailing-list mail, `Precedence: bulk/list/junk`, null `Return-Path`, daemon senders, own address |
| Poll-report counters | `skipped_automated`, `skipped_auth`, `quarantined`, `echoes_dead` |
| Staging | `<inbox>.staging/*.part`, no-clobber link, copy fallback on `EXDEV`; orphan `.part` older than 1 h swept |

- [ ] **Step 1: Write** an "Unreleased on `main` (after v0.8.0, as of 2026-10-07)" GitBook `{% hint %}` near the top of `gmail-intake.md` linking `../../changelog/unreleased.md`, then update sections 1, 2, 3 and 4 to carry the values above, following the upstream page's structure. Replace the "Echoes are deduped per `(doc_id, stage)`; a failed send is retried by the next terminal event" sentence (~line 252) and the "Echo never arrives" troubleshooting row (~line 283) with the outbox behaviour. Add the "Allowlisted sender ignored" troubleshooting row. Re-check the "Message-ID dedup" claim (~line 129) against upstream and keep it only if upstream still states it.
- [ ] **Step 2: Add** the six env-var rows to `configuration.md` and fix the `ALLOWED_SENDERS` description.
- [ ] **Step 3: Verify**
  ```bash
  for k in DMARC mail_outbox MAILROOM_GMAIL_MAX_ATTEMPTS MAILROOM_GMAIL_IDLE MAILROOM_GMAIL_ACKS MAILROOM_GMAIL_ALLOW_SELF MAILROOM_GMAIL_MAX_REPLIES_PER_HOUR mailroom/failed skipped_auth echoes_dead; do printf '%s %s\n' $k $(grep -lF -- "$k" docs/pipeline-reference-llm-mailroom/gmail-intake.md docs/pipeline-reference-llm-mailroom/configuration.md | wc -l); done   # every count >= 1
  grep -n 'retried by the next terminal event\|lowercased comparison\|(lowercased)' docs/pipeline-reference-llm-mailroom/*.md   # expect no output
  grep -n 'Unreleased' docs/pipeline-reference-llm-mailroom/gmail-intake.md   # expect >= 1
  ```
- [ ] **Step 4: Commit** — `git commit -m "docs: document unreleased Gmail intake hardening (llm-mailroom 578db29)"`.

---

### Task 5: LLM layer — free-quota breaker, models fallback, served models, result cache (unreleased on main)

Source: `578db29:src/config/taxonomy.yaml` (`free_quota:` block), `src/llm/quota.py`, `src/llm/retry.py`, `src/llm/result_cache.py`, `CHANGELOG.md` `[Unreleased]` "Free-model resilience" and "Gmail intake performance".

**Files:**
- `docs/pipeline-reference-llm-mailroom/configuration.md` — new `free_quota` subsection next to the retry section (~line 252), and a `MAILROOM_LLM_CACHE` env-var row.
- `docs/pipeline-reference-llm-mailroom/gmail-intake.md` — Pathway A: the lane answers with its deterministic header pass (`degraded: free_quota`) when the breaker is open; the triage result cache.

**Exact values:** `free_quota.trip_after: 3`, `free_quota.cooldown_s: 300` (doubles per consecutive trip; a positive `Retry-After` is used as given; either way capped at 3600 s); raises `FreeQuotaExhausted`; paid models never touch the breaker. Free OpenRouter calls send the rest of the `free_model_swarm` chain as the `models` array with `provider.require_parameters` when the chain has more than one entry; `model` stays the primary. `usage_summary()` records `served_models` per agent. Cache: `<base>/llm_result_cache.sqlite`, 30-day TTL, key covers the full request, `MAILROOM_LLM_CACHE=0` disables (default on).

- [ ] **Step 1: Write** both edits, each labelled unreleased on `main` as of 2026-10-07.
- [ ] **Step 2: Verify**
  ```bash
  for k in free_quota trip_after cooldown_s FreeQuotaExhausted served_models MAILROOM_LLM_CACHE llm_result_cache.sqlite 'degraded: free_quota'; do printf '%s %s\n' "$k" $(grep -rlF -- "$k" docs/pipeline-reference-llm-mailroom | wc -l); done   # every count >= 1
  ```
- [ ] **Step 3: Commit** — `git commit -m "docs: document free-quota breaker, models fallback and triage result cache"`.

---

### Task 6: Whole-site consistency, links, push, merge

**Files:** any page a check below flags; `docs/README.md` docs shelf (add a Changelog link if the shelf lists sections); `docs/repository-guides/repos/llm-mailroom.md` (one line: main carries unreleased Gmail hardening and LLM resilience; link the Changelog Unreleased page).

- [ ] **Step 1: Relative-link check** — for every `](relative.md#anchor)` in changed files, confirm the file exists and the anchor matches a heading.
  ```bash
  git diff --name-only origin/main...HEAD -- docs README.md | grep '\.md$' | xargs python3 -c 'import re,os,sys; bad=[(f,m) for f in sys.argv[1:] for m in re.findall(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)", open(f,encoding="utf-8").read()) if not m.startswith("http") and not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f),m)))]; [print(f,"->",m) for f,m in bad]; sys.exit(1 if bad else 0)'
  ```
  Expected: exit 0, no output. Check `#anchor` targets by eye for links added in this plan.
- [ ] **Step 2: Stale-claim sweep** — expect no output from each:
  ```bash
  grep -rn 'pins v0\.19\|@v0\.19\.1\|dojo v0\.19' docs --include='*.md' | grep -v '^docs/changelog/'
  grep -rn 'mailroom-inc.-docs' docs --include='*.md' | grep -v '^docs/changelog/2026/'
  ```
- [ ] **Step 3: Config untouched** — `git diff --quiet origin/main...HEAD -- gitbook-docs.yaml docs/.gitbook.yaml && echo CONFIG-OK` → `CONFIG-OK`.
- [ ] **Step 4: Commit any fixes, then push** — `git push origin docs/add-changelog`. Update the PR body (`gh pr edit 4 --body-file …`) to list Tasks 1–5 and keep the existing CodeRabbit block untouched.
- [ ] **Step 5: Review gate** — wait for CodeRabbit and GitGuardian on PR #4; the reviewer (Opus) triages every CodeRabbit finding: fix, or reply with the file:line that refutes it.
- [ ] **Step 6: Merge** — `gh pr merge 4 --merge` (merge commit; no squash, so per-task commits stay citable). Then:
  ```bash
  git switch main && git pull --ff-only
  gh api repos/Exios66/mailroom-documentation/contents/gitbook-docs.yaml --jq .content | base64 -d | diff - gitbook-docs.yaml && echo REMOTE-OK
  ```
- [ ] **Step 7: Live check** — after Git Sync, open `https://mailroom-inc.gitbook.io/the-digital-mailroom/changelog/unreleased`, `…/start-here/overview`, and `…/pipeline-reference-llm-mailroom/gmail-intake`. Expected: pages render, no "Failed to parse site configuration" error, the Unreleased page mentions `v0.21.0`. Report merge SHA and per-task commit SHAs.
