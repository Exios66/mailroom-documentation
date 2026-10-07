# Apache Phoenix

Arize Phoenix is the **local, cost-free default fallback** in the tracing chain. When no cloud backend is keyed, `auto` resolves to Phoenix instead of switching tracing off, so every LLM call stays traced with zero spend on top of the API calls. It is a single local process with SQLite/in-memory storage that you can delete when a batch is done — a *pour-in, poke-around, discard* workflow.

Implementation: [`src/observability/phoenix_setup.py`](https://github.com/Exios66/llm-mailroom/blob/main/src/observability/phoenix_setup.py). Backend selection happens in [`src/observability/tracing.py`](https://github.com/Exios66/llm-mailroom/blob/main/src/observability/tracing.py).

## What Phoenix captures — and what it does not

One OpenTelemetry `TracerProvider` is lazily initialised per process and emits spans over OTLP HTTP to `PHOENIX_ENDPOINT`. `instrument_openai_client` uses the OpenInference `OpenAIInstrumentor` (part of the `arize-phoenix` dependency set), so every LLM call lands as a nested span with model, token usage, latency and response.

{% hint style="warning" %}
**Phoenix traces LLM calls but not pipeline structure.** The node-level structured spans (`pipeline_trace` / `observation`) are **Langfuse-only** in the facade. With only Phoenix active, LLM generations still trace and `flush()` force-exports them, while the Langfuse-only helpers no-op — the pipeline runs identically, but you will not see one span per graph node. Choose [Langfuse](langfuse.md) if per-node visibility is the point.
{% endhint %}

## Configuration

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `PHOENIX_TRACING` | `enabled` | Master switch; `1` / `true` / `enabled` / `yes` / `on` are all truthy |
| `PHOENIX_ENDPOINT` | `http://localhost:6006/v1/traces` | OTLP HTTP traces endpoint |
| `PHOENIX_SERVICE_NAME` | `mailroom` | OpenTelemetry service name |
| `PHOENIX_PROJECT` | `mailroom` | OpenInference project name |

`phoenix_enabled()` reads `PHOENIX_TRACING`; set it to a falsy value to disable Phoenix even when another backend would have been selected.

## The Railway guard

`auto` does **not** always fall through to Phoenix. If `RAILWAY_ENVIRONMENT` or `RAILWAY_PROJECT_ID` is set *and* `PHOENIX_ENDPOINT` still points at `localhost` or `127.0.0.1`, resolution returns `none`:

```python
on_railway = bool(os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_PROJECT_ID"))
endpoint = os.environ.get("PHOENIX_ENDPOINT", "http://localhost:6006/v1/traces")
local_only = ("localhost" in endpoint) or ("127.0.0.1" in endpoint)
if on_railway and local_only:
    return "none"
```

Railway has no local `phoenix serve`, so defaulting to Phoenix there would only burn memory against a port nothing is listening on. Set `PHOENIX_ENDPOINT` to a real collector to re-enable it. See [Deployment — Railway](README.md#railway).

## Run it standalone

```bash
pip install arize-phoenix
phoenix serve          # or: python -m phoenix.server.main serve
```

Then open `http://localhost:6006` and confirm traces appear as documents flow. The SQLite database can be deleted when a batch is finished.

Force it even when other backends are keyed:

```bash
OBSERVABILITY_PROVIDER=phoenix
```

## Phoenix in the Mode G stack

[`deploy/docker-compose.full.yml`](https://github.com/Exios66/llm-mailroom/blob/main/deploy/docker-compose.full.yml) ships a `phoenix` service behind a compose profile:

```bash
docker compose -f deploy/docker-compose.full.yml --env-file .env \
  --profile phoenix up -d --build
```

| Setting | Value |
| ------- | ----- |
| Image | `${PHOENIX_IMAGE:-arizephoenix/phoenix:latest}` |
| Port | `127.0.0.1:6006:6006` — **loopback only** |
| Storage | `phoenix_data` volume at `PHOENIX_WORKING_DIR=/mnt/data` |
| App-side endpoint | `PHOENIX_ENDPOINT=http://phoenix:6006/v1/traces` |
| Healthcheck | `GET http://127.0.0.1:6006/healthz`, 12 retries, 20 s start period |

The app declares `depends_on: phoenix: {condition: service_healthy, required: false}`, so it starts with or without the profile active.

{% hint style="warning" %}
`PHOENIX_IMAGE` defaults to `arizephoenix/phoenix:latest` — an **unpinned** tag, unlike the rest of the Mode G stack where Postgres, LiteLLM and the base image are all pinned. A new upstream release can change behaviour without a commit here. Pin it explicitly in `.env` if you rely on Phoenix in production.
{% endhint %}

Because the port binds to `127.0.0.1`, Phoenix is reachable from the host but **not** from other machines. Keep it that way: traces contain document content. To expose it, front it with a reverse proxy that terminates auth — do not publish `6006` directly.

## Graceful degradation

The module is a no-op when `PHOENIX_TRACING` is disabled or provider initialisation failed, so runs continue exactly as if observability were off. `flush_phoenix()` force-flushes the batch processor **without** shutting the provider down; a failure there is logged, not raised.

## Related

* [Langfuse](langfuse.md) — the default backend, and the only one with per-node spans
* [Scoring and performance](../../the-pipeline-in-depth/scoring-and-metrics.md) — provider resolution chain
* [Configuration](../configuration.md) — `OBSERVABILITY_PROVIDER`, `PHOENIX_*`
* [Docker](docker-deployment.md) — Mode G compose matrix
* [Deployment](./) — Railway, troubleshooting "no traces in `auto` mode"