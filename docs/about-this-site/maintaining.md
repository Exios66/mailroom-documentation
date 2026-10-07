# Maintaining this site

**This repository — [Exios66/mailroom-documentation](https://github.com/Exios66/mailroom-documentation) — is the source of [The Digital Mailroom](https://mailroom-inc.gitbook.io/the-digital-mailroom/).** GitBook [Git Sync](https://gitbook.com/docs/getting-started/git-sync) publishes the site straight from the `docs/` folder of this repo. The pipeline the site documents still lives in [Exios66/llm-mailroom](https://github.com/Exios66/llm-mailroom); only the published documentation moved here.

Git Sync reads its site config from [`gitbook-docs.yaml`](https://github.com/Exios66/mailroom-documentation/blob/main/gitbook-docs.yaml) at the **repository root**. The repository root is also GitBook's default **Project directory**, so the config is found with no hidden setting to keep in sync. The site holds a **single space** (`mailroom-docs`) reading `content.directory: ./docs` — the whole `docs/` folder is one GitBook book: `docs/README.md` is the landing page and `docs/SUMMARY.md` is the table of contents. The space is mounted at `path: /` **inside the site's single section** (`section-1`, the default section, which serves the site from the root URL), so pages publish at `…/the-digital-mailroom/{page}` and a merge to `main` replaces the site. The space **must stay inside the section**: once a site has a section, GitBook rejects any space listed at the top level of `site.structure` (`Root-level site spaces can only exist in a non-sections site`). The `docs` folder itself never appears as a navigation entry — the sidebar is just the book's own sections.

## How it is built

| File / path | Role |
| --- | --- |
| `gitbook-docs.yaml` (repository root) | The live site-wide Git Sync config, at the root of the Git Sync **project directory** (the repository root — GitBook's default). Declares the site title (**The Digital Mailroom**) and one **section** (`section-1`, `default: true`) wrapping a single space (`mailroom-docs`, `path: /`) whose `content.directory` is `./docs` — the whole `docs/` folder. A site that has a section must keep its spaces inside one; never list a space at the top level of `site.structure`. Do not change the space or section `key`. |
| `docs/.gitbook.yaml` | The `docs/` space's content config: sets the content root to `./docs` itself and names `README.md` (landing page) and `SUMMARY.md` (table of contents). |
| `docs/README.md` | The GitBook landing page. Page header is **LLM-MAILROOM** only (GitBook uses the H1 / `SUMMARY.md` title — no Fumi in the header), owl banner below the badges, two `fumi.gif`s (Postal Worker Fumi (文, "letter") on duty after the masthead, then Meet Fumi), tags, install, pipeline walk-through, and docs shelf. GitBook's own type; it does not load any static landing page's display font. GitBook strips scripts, so the idle TUI stays off the page. |
| `docs/SUMMARY.md` | The table of contents. Only pages listed here are published. |
| `docs/.gitbook/assets/` | GitBook-referenced site images (`banner.png`, `fumi.gif`, `hoot-icon.png`), referenced with relative paths such as `.gitbook/assets/banner.png`. |
| `docs/assets/` | The **single source of truth** for the site's art — the full Fumi + Hermes mascot set (`mascot/`: `fumi.svg`, `fumi.gif`, `fumi.png`, `fumi-icon.png`, `fumi-sheet.png`, `hoot-icon.png`, and `source/fumi-base.png`), the masthead `banner.png`, `fumi/fumi.gif`, and `mailroom-pipeline.svg`. See `docs/assets/README.md` and `docs/assets/mascot/README.md`. |
| Section folders under `docs/` (`start-here/`, `the-pipeline-in-depth/`, `how-it-fits-together/`, `mailroom-dataset/`, `repository-guides/`, `pipeline-reference-llm-mailroom/`, `about-this-site/`) | Site content, grouped by the sections defined in `docs/SUMMARY.md`. |

The site **content** lives entirely in the `docs/` folder — `docs/README.md` (landing), `docs/SUMMARY.md` (TOC), `docs/.gitbook/assets/`, `docs/assets/` (the Fumi + Hermes art), `docs/.gitbook.yaml` (the space's content config), and the section folders. The **repository root holds the site config (`gitbook-docs.yaml`) and `.gitattributes`** — nothing else. There is no `landing/` or root-level `assets/` folder in this repo; the site art lives under `docs/assets/` and `docs/.gitbook/assets/`.

The **Changelog** section reflects the pipeline repository [`Exios66/llm-mailroom`](https://github.com/Exios66/llm-mailroom)'s `CHANGELOG.md` — it is generated, so never hand-edit it. Regenerate it with `PYTHONPATH=src python src/scripts/sync_gitbook_changelog.py` in `llm-mailroom`; `--check` is the guard.

## Connecting the GitBook site (one-time)

1. In GitBook, open the site's space (the `mailroom-docs` space, titled **The Digital Mailroom**).
2. Open the space's **Configure** menu, choose **GitHub Sync**, and install the GitBook GitHub app on **`Exios66/mailroom-documentation`** (this repo — *not* `llm-mailroom`).
3. Pick the `main` branch and **leave the Project directory empty** (it defaults to the repository root, where `gitbook-docs.yaml` lives). If an earlier setup put `docs` here, clear it — the config moved to the repository root.
4. Choose **GitHub to GitBook** for the first sync so the repository content is imported rather than overwritten.

After that, a merge to `main` updates the site. Edits made in the GitBook editor come back as commits.

Mermaid diagrams render on GitHub; in GitBook they need the Mermaid integration enabled on the space, otherwise they show as code blocks.

## `path` vs `directory` (this is the usual mix-up)

The Project directory, `content.directory`, and `path` are three different knobs. Only `path` is a URL slug:

| Knob | File | Meaning | Correct value here |
| --- | --- | --- | --- |
| Git Sync **Project directory** (GitBook UI) | — | Where GitBook looks for `gitbook-docs.yaml` | **empty** (repository root) — the config sits at `gitbook-docs.yaml` |
| `content.directory` | `gitbook-docs.yaml` | Git folder the space reads, relative to the Project directory | `./docs` (this repo's `docs/` folder) |
| `path` | `gitbook-docs.yaml` | URL after the site slug | `/` (site home) |
| space `key` | `gitbook-docs.yaml` | Stable identifier for the `mailroom-docs` space | `mailroom-docs` — **never change it** |

`content.directory` is a **folder**; `path` is a **URL**. With the config at the repository root (the default Project directory), `content.directory: ./docs` points the space at the whole `docs/` book. Do not set `path: docs` — that would publish the home at `…/the-digital-mailroom/docs/` instead of the site root.

GitBook also replaces the markdown H1 with the `SUMMARY.md` link title. Keep that link as `* [LLM-MAILROOM](README.md)` so the GitBook page header reads **LLM-MAILROOM** and matches the `# LLM-MAILROOM` heading in `docs/README.md` (the previous `* [Welcome](README.md)` title is why the live home used to read **Welcome**).

GitBook's published favicon is the site icon in **Customize** ([icons, colors, and themes](https://gitbook.com/docs/manage-your-site/customization/icons-colors-and-themes)). Git Sync cannot set it: `gitbook-docs.yaml` has no favicon field. Upload `docs/.gitbook/assets/hoot-icon.png` (Hermes, the pixel owl).

## Rules for editing

* **Link, don't copy.** Each repository's own README and docs stay canonical. A guide here summarizes what a newcomer needs to orient, then links to the source. This follows the llm-mailroom rule that docs content is never duplicated.
* **Every new page goes in `docs/SUMMARY.md`.** A page that is not listed is not published. Operator recipes that belong on this site (Docker compose matrix, Modal + vLLM) live under `docs/` in their section folder and are listed here — `deploy/README.md` is a file index, not a GitBook page. Sandbox run reports and visuals are nested under the [local-mailroom-sandbox](../repository-guides/repos/local-mailroom-sandbox/) guide. The canonical corpus has its own top-level section ([Mailroom dataset](../mailroom-dataset/mailroom-dataset.md)); static PNGs stay on `Exios66/Mailroom-Corpus-EDA` `main` (`raw.githubusercontent.com`) and the live dashboard / Plotly charts / Hub viewer are iframes from `exios66.github.io/Mailroom-Corpus-EDA`.
* **Use relative links between pages on this site** (`pipeline-reference-llm-mailroom/architecture.md`, `../mailroom-dataset/mailroom-dataset.md`) and full GitHub URLs for anything in another repository. Every site page lives under `docs/`, so relative links stay within `docs/`.
* **Date facts that drift.** Versions, pins and counts carry an "as of" date; when a release moves them, update [Overview](../start-here/overview.md) and the affected guide.
* **Reference the pipeline in `llm-mailroom`, don't relocate it.** The pipeline source, its `src/`, `deploy/`, notebooks and `CHANGELOG.md` live in [Exios66/llm-mailroom](https://github.com/Exios66/llm-mailroom) — GitHub URLs under `Exios66/llm-mailroom/...` and paths such as `pipeline-reference-llm-mailroom/...` describe the pipeline and stay as they are. Only the *published documentation site* is sourced from this repo.
* **Keep the GitHub wiki separate.** The `llm-mailroom` repository's own `docs/wiki/` remains wiki-only and is not mirrored on this site.
* **Keep the GitBook Changelog in sync.** The site's Changelog section mirrors `llm-mailroom`'s `CHANGELOG.md`; after that file changes, run `PYTHONPATH=src python src/scripts/sync_gitbook_changelog.py` in `llm-mailroom`.

## When a repository changes

| Change | Update |
| --- | --- |
| New repository joins the constellation | Add a guide under `docs/repository-guides/repos/`, list it in `docs/SUMMARY.md`, [Overview](../start-here/overview.md), [Repository index](../how-it-fits-together/repo-index.md) and `repository-guides/repos/README.md` |
| Repository archived or superseded | Move it to the copies or earlier-monorepos table in the [Repository index](../how-it-fits-together/repo-index.md) |
| A release changes versions or pins | [Overview](../start-here/overview.md) version table, the repo's guide, the [dependency table](../how-it-fits-together/architecture.md#dependency-summary) |
| Dataset revision changes | [Mailroom dataset](../mailroom-dataset/mailroom-dataset.md) first (counts, strata, EDA figures), then [Data and corpora](../how-it-fits-together/data-and-corpora.md) |
| Pipeline nodes or classes change | The pipeline reference pages first; then [Architecture](../how-it-fits-together/architecture.md) and [Glossary](../start-here/glossary.md) if terms changed |
| Compose matrix, Mode G, or Modal vLLM knobs change | [Docker](../pipeline-reference-llm-mailroom/deployment/docker-deployment.md) and [Modal + vLLM](../pipeline-reference-llm-mailroom/deployment/modal-vllm.md) first; keep `deploy/README.md` as an index that links those pages |
| Sandbox run reports or figures change | [Run reports](../repository-guides/repos/local-mailroom-sandbox/local-mailroom-sandbox-reports.md) and [Visuals](../repository-guides/repos/local-mailroom-sandbox/local-mailroom-sandbox-visuals.md); keep image URLs on `Exios66/local-mailroom-sandbox` `main` |
| Mailroom-Corpus-EDA figures or SUMMARY\_REPORT change | [EDA reports](../mailroom-dataset/eda-reports.md) and [Visualizations](../mailroom-dataset/visualizations.md); keep PNG URLs on `Exios66/Mailroom-Corpus-EDA` `main` and iframe URLs on `exios66.github.io/Mailroom-Corpus-EDA` |
| Fumi's or Hermes's artwork changes | The full mascot set is built in the `llm-mailroom` repository (`src/scripts/build_mascot.py`, from `source/fumi-base.png`) and mirrored here under `docs/assets/mascot/` — plus `docs/assets/banner.png` and `docs/assets/fumi/fumi.gif`. Refresh the GitBook-referenced copies in `docs/.gitbook/assets/` (`banner.png`, `fumi.gif`, `hoot-icon.png`) to match. GitBook strips scripts and may not animate SVG, so the GIF is the one to use on this page. The GitBook home header is **LLM-MAILROOM** only; Fumi appears twice as `fumi.gif` after the masthead (Postal Worker Fumi (文, "letter") on duty, then Meet Fumi). The owl banner, title, and badges stay the masthead. Re-upload `hoot-icon.png` in GitBook Customize if the Hermes sprite changes. |
| `llm-mailroom` `CHANGELOG.md` changes | Run `PYTHONPATH=src python src/scripts/sync_gitbook_changelog.py` in the `llm-mailroom` repository so the site's Changelog section matches. `--check` is the guard. |
