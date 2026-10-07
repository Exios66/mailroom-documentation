# Langfuse

Langfuse is the pipeline's **default tracing backend** — the first stop in the `auto` resolution chain — and the only backend that records structured, per-graph-node spans rather than just LLM calls. It is optional: the pipeline runs identically with tracing off.

The active backend is chosen by `OBSERVABILITY_PROVIDER`, resolved in [`src/observability/tracing.py`](https://github.com/Exios66/llm-mailroom/blob/main/src/observability/tracing.py):

| `OBSERVABILITY_PROVIDER` | Behaviour |
| ------------------------- | --------- |
| `auto` *(default)* | Langfuse if `LANGFUSE_SECRET_KEY` is set → Braintrust if `BRAINTRUST_API_KEY` is set → local [Phoenix](phoenix.md) if enabled → `none` |
| `langfuse` | Force Langfuse |
| `braintrust` | Force Braintrust |
| `phoenix` | Force [Phoenix](phoenix.md) |
| `none` | Disable tracing entirely |

## What Langfuse captures

Two layers, both in [`src/observability/langfuse_setup.py`](https://github.com/Exios66/llm-mailroom/blob/main/src/observability/langfuse_setup.py):

1. **LLM calls.** `get_llm()` in `llm/client.py` passes the OpenAI client through `observability.tracing.instrument_openai_client`, which imports `langfuse.openai` and calls `register_tracing`. That monkeypatches `Completions.create`, so **every chat completion** becomes a `generation` observation carrying model, tokens, cost and latency.
2. **Pipeline structure.** `pipeline_trace()` opens one root **chain** per document — one trace is one unit of work — with `session_id = matter_id` and a deterministic trace id seeded from the file name, so re-running the same file reuses its trace. `observation()` opens typed children (agent / evaluator / retriever / span / generation) with verb-first stable names. Generations created inside a node's observation nest under it automatically.

{% hint style="info" %}
**Structured per-node spans are Langfuse-only.** The Phoenix and Braintrust backends trace LLM calls but **not** `pipeline_trace` / `observation` node spans — those helpers no-op. If you want one trace per document with a visible span for each of the 13 graph nodes, Langfuse is the only backend that provides it. See [Apache Phoenix](phoenix.md) for the exact split.
{% endhint %}

## Configuration

```bash
# Required
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...

# Cloud (default region)
LANGFUSE_HOST=https://us.cloud.langfuse.com
# Self-hosted
# LANGFUSE_HOST=http://localhost:3000
# LANGFUSE_BASE_URL is accepted as an alias for cloud-hosted setups
```

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `LANGFUSE_HOST` | `http://localhost:3000` | Base URL. `LANGFUSE_BASE_URL` is an alias |
| `LANGFUSE_FLUSH_AT` | `512` | SDK batch size (event count) |
| `LANGFUSE_FLUSH_INTERVAL` | `5` s | SDK batch interval |
| `LANGFUSE_RELEASE` | — | Optional release/version label on every observation |
| `OBSERVABILITY_ENVIRONMENT` | — | Environment label; `LANGFUSE_TRACING_ENVIRONMENT` also accepted |

`_resolve_host()` reads `LANGFUSE_HOST`, then `LANGFUSE_BASE_URL`, then falls back to `http://localhost:3000`.

{% hint style="warning" %}
**Short-lived jobs must call `flush()` before exit.** The SDK batches in a background exporter that may not drain before the process ends, so a one-shot script or CI job can exit before its spans are exported. Pipeline runs are long-lived enough that this rarely bites, but ad-hoc scripts and eval batches do need an explicit flush.
{% endhint %}

## Self-hosted Langfuse

Langfuse v2 needs **its own** Postgres (with pgvector) **and** ClickHouse — see [Postgres](postgres.md) for why that store is not the pipeline's own. Both come from [`src/config/docker/docker-compose.yml`](https://github.com/Exios66/llm-mailroom/blob/main/src/config/docker/docker-compose.yml):

| Service | Image | Port | Purpose |
| ------- | ----- | ---- | ------- |
| `langfuse-server` | `langfuse/langfuse:2.93.0` | 3000 | Trace viewer UI |
| `postgres` | `pgvector/pgvector:pg16` | 5432 | Langfuse's relational store |
| `clickhouse` | `clickhouse/clickhouse-server:24.8-alpine` | 8123, 9000 | Langfuse's analytics store |

```bash
# From a repo checkout
docker compose -f src/config/docker/docker-compose.yml \
  up -d postgres clickhouse langfuse-server
```

Required in `.env` before the stack will start:

```bash
NEXTAUTH_SECRET=...      # compose fails fast if unset
SALT=...                 # compose fails fast if unset
POSTGRES_PASSWORD=...
CLICKHOUSE_PASSWORD=...
```

Startup is healthcheck-gated: `langfuse-server` waits on `postgres` **and** `clickhouse` being healthy. Its healthcheck is `wget -qO- http://localhost:3000/api/auth/signin`. `LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES` is set to `"true"`.

**First run:** open `http://localhost:3000`, create an account, then generate API keys and put them in `.env` as `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST`.

{% hint style="info" %}
Use `src/config/docker/docker-compose.yml`, not the Mode G stack. The Mode G [`deploy/docker-compose.full.yml`](https://github.com/Exios66/llm-mailroom/blob/main/deploy/docker-compose.full.yml) does **not** run Langfuse — it wires `LANGFUSE_*` keys for Langfuse **Cloud**, and offers local [Phoenix](phoenix.md) behind a compose profile instead.
{% endhint %}

## Scores in Langfuse

Trace wiring also pushes results, not just calls: [`langfuse_field_scoring.py`](https://github.com/Exios66/llm-mailroom/blob/main/src/observability/langfuse_field_scoring.py) and [`scores.py`](https://github.com/Exios66/llm-mailroom/blob/main/src/observability/scores.py) write per-field and per-document scores onto the active trace. Definitions live in [Scoring and performance](../../the-pipeline-in-depth/scoring-and-metrics.md).

## Pulling traces offline

[`src/scripts/sync_langfuse_logs.py`](https://github.com/Exios66/llm-mailroom/blob/main/src/scripts/sync_langfuse_logs.py) exports traces to `data/langfuse_logs/` for analysis without the UI:

```bash
PYTHONPATH=src python src/scripts/sync_langfuse_logs.py --since 24h
```

| Flag | Default | Meaning |
| ---- | ------- | ------- |
| `--since` | `24h` | Lookback window |
| `--limit` | `100` | Maximum traces |
| `--trace-id` | — | Single trace |
| `--output` | `data/langfuse_logs` | Destination directory |
| `--wait-scores` | — | Block until async scores land |

## Related

* [Apache Phoenix](phoenix.md) — the local, cost-free fallback; what it does *not* capture
* [Postgres](postgres.md) — Langfuse's own pgvector-backed store vs the pipeline catalog
* [Scoring and performance](../../the-pipeline-in-depth/scoring-and-metrics.md) — trace wiring and score definitions
* [Configuration](../configuration.md) — `OBSERVABILITY_PROVIDER`, `LANGFUSE_*`
* [Docker](docker-deployment.md) — compose matrix
* [Deployment](./) — laptop install, Railway, Spaces, backup