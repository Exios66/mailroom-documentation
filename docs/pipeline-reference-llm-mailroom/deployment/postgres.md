# Postgres

Postgres is **optional**. The catalog, audit log and relations are plain SQLite files by default and the pipeline is designed to run with no database server at all. Postgres matters in two separate places, and they are not the same database — confusing them is the most common source of wasted effort here.

## Two distinct roles

| | **Langfuse's store** | **The mailroom catalog** |
| - | ------------------ | ------------------------ |
| Who uses it | [Langfuse](langfuse.md) tracing UI | The pipeline: catalog, audit log, relations |
| Compose file | [`src/config/docker/docker-compose.yml`](https://github.com/Exios66/llm-mailroom/blob/main/src/config/docker/docker-compose.yml) | [`deploy/docker-compose.full.yml`](https://github.com/Exios66/llm-mailroom/blob/main/deploy/docker-compose.full.yml) (Mode G) |
| Image | `pgvector/pgvector:pg16` | `${POSTGRES_IMAGE:-postgres:16-alpine}` |
| Why that image | Langfuse v2 **requires** pgvector | Plain Postgres — no vector extension needed |
| Default | Only started if you ask for Langfuse | Started automatically in Mode G |
| Published port | `5432:5432` | **not** published — internal only |

The pipeline catalog does **not** need pgvector. If you want Langfuse and the catalog in one stack, point Langfuse's `DATABASE_URL` at the pgvector service rather than swapping the catalog onto it.

## The URL scheme

`DATABASE_URL` is an async SQLAlchemy URL. SQLite by default; set a Postgres URL to switch:

| Scheme | When |
| ------ | ---- |
| `sqlite+aiosqlite:///<MAILROOM_BASE_DIR>/mailroom.db` | Default. No server, file created on first use |
| `postgresql+psycopg://mailroom:mailroom@localhost:5432/mailroom` | Postgres |

{% hint style="warning" %}
Use **`postgresql+psycopg`**, not `postgresql+asyncpg`. Upstream declares exactly one Postgres driver — `psycopg[binary]>=3.1`, in the `postgres` extra of [`pyproject.toml`](https://github.com/Exios66/llm-mailroom/blob/main/pyproject.toml) — and `asyncpg` is not a dependency at all. A `+asyncpg` URL fails at connect time with a missing-driver error. SQLAlchemy 2.0's `postgresql+psycopg` dialect drives psycopg 3 in async mode, so the URL and the declared dependency agree. (An earlier revision of this site's Deployment page suggested `+asyncpg`; that has been corrected.)
{% endhint %}

Install the driver:

```bash
pip install -e ".[postgres]"
```

The extra is `psycopg[binary]>=3.1`. Core install is `sqlalchemy[asyncio]>=2.0`, which is what makes the SQLite default async.

## Local setup

```bash
# Start the server
docker compose -f src/config/docker/docker-compose.yml up -d postgres

# Point the pipeline at it
# DATABASE_URL=postgresql+psycopg://mailroom:mailroom@localhost:5432/mailroom

# Create the schema
python -c "import asyncio; from storage.db import init_db; asyncio.run(init_db())"
```

Tables are otherwise auto-created on first use, exactly as with SQLite.

## Mode G service

```yaml
postgres:
  image: "${POSTGRES_IMAGE:-postgres:16-alpine}"
  environment:
    POSTGRES_USER: "${POSTGRES_USER:-mailroom}"
    POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"     # required — image refuses to init without it
    POSTGRES_DB: "${POSTGRES_DB:-mailroom}"
  volumes:
    - pgdata:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U \"$$POSTGRES_USER\" -d \"$$POSTGRES_DB\""]
```

Every mailroom process in the stack inherits the same URL through the shared env anchor:

```yaml
DATABASE_URL: "postgresql+psycopg://${POSTGRES_USER:-mailroom}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-mailroom}"
```

`POSTGRES_PASSWORD` is **required**: the compose file refuses to come up half-configured. The port is deliberately not published — only the compose network reaches it. Uncomment `ports: ["127.0.0.1:5432:5432"]` if you want `psql` from the host.

The image also needs the driver at build time, which Mode G wires through the build extra:

```yaml
args:
  PIP_EXTRAS: "${MAILROOM_PIP_EXTRAS:-bert,postgres}"   # postgres: psycopg async driver
```

The `app` healthcheck allows 60 s of `start_period` for schema creation and score-config warm-up, and `ops-monitor` reads Postgres directly.

## What stays on SQLite even in Mode G

The LangGraph **checkpointer is never Postgres**. `MAILROOM_CHECKPOINTER` selects `sqlite` (writing `/data/checkpoints.db` on the shared volume, so review resume survives restarts) and otherwise falls back to `MemorySaver`. Choosing Postgres for the catalog does not move checkpoint state.

Named volumes (`pgdata`, and `mailroom_data` for `/data`) mean data survives `docker compose down`. Unnamed volumes do not — do not drop them during a restart cycle.

## Backup

SQLite's online backup is the default path; for Postgres use `pg_dump`:

```bash
pg_dump -h localhost -U mailroom mailroom > backup/mailroom-$(date +%F).sql
```

Restoring Postgres is the commented `psql` line in the restore procedure. The full sequence — stop the writer first, restore the DB *and* `/archive` and `/manifests` from the same point in time, then verify the audit chain — is in [Deployment — Backup & Restore](README.md#backup--restore). A restored catalog that disagrees with restored manifests breaks the hash chain, and `/v1/audit/<doc_id>` will report `chain_valid: false`.

Backups contain confidential client documents: encrypt at rest and keep them off-host.

## Related

* [Langfuse](langfuse.md) — why its store needs pgvector and yours does not
* [LiteLLM gateway](litellm-gateway.md) — the other required Mode G service
* [Configuration](../configuration.md) — `DATABASE_URL`, `MAILROOM_CHECKPOINTER`
* [Deployment](./) — laptop install, backup and restore, Railway
* [Operational procedure](../operational-procedure.md) — what the catalog and audit tables hold