# Testing

## Test Structure

```
tests/
├── conftest.py                  # Shared fixtures and mocks
├── test_agents/
│   ├── __init__.py
│   ├── test_base.py             # BaseAgent contract
│   ├── test_sorter.py           # Sorter agent unit tests
│   ├── test_specialists.py      # All specialist + Boss unit tests
│   └── test_prompt_calibration.py
├── test_routing.py              # Confidence-based routing logic
├── test_audit_log.py            # Hash-chain integrity tests
├── test_pipeline_e2e.py         # End-to-end pipeline tests
├── test_bert_intake.py          # ModernBERT fast-path lane (fail-open)
├── test_merger_agreement_specialist.py
├── test_gateway_tiers.py        # Mode G tier routing (LiteLLM + Modal)
├── test_smoke_modal_tiers.py    # network-free tier contract
├── test_status_notify.py        # watchdog / status email
└── ...                          # ~95 modules in total; `pytest --collect-only -q` lists them
└── fixtures/
    ├── contract/                # 3 sample contracts (MSA, NDA, ambiguous)
    ├── corporate_record/        # 2 sample corp records (bylaws, resolution)
    ├── due_diligence/           # retired class (fixtures kept on disk)
    ├── court_opinion/           # retired class (fixtures kept on disk)
    ├── correspondence/          # 2 sample correspondences (demand letter, memo)
    └── insurance_claim/         # FNOL / claim documentation
```

***

## Running Tests

```bash
# All tests
pytest -v

# By test file
pytest src/tests/test_agents/test_sorter.py -v
pytest src/tests/test_agents/test_specialists.py -v
pytest src/tests/test_routing.py -v
pytest src/tests/test_audit_log.py -v
pytest src/tests/test_pipeline_e2e.py -v

# By test name pattern
pytest -v -k "sorter"

# With coverage
pytest --cov=src --cov-report=html --cov-report=term

# With verbose output
pytest -v -s
```

***

## Test Categories

### Agent Unit Tests (`test_agents/`)

**44 test functions across 4 files** (`test_base.py` 12, `test_sorter.py` 14, `test_specialists.py` 16, `test_prompt_calibration.py` 2), covering:

* Sorter: classification across all doc types, low-confidence cases, JSON parse errors, output validation
* Contracts Specialist: extraction accuracy, confidence scoring
* Corporate Records Specialist: entity/record extraction
* Correspondence Specialist: action item extraction
* Merger Agreement Specialist: MAUD consideration, parties, clauses
* Insurance Claims Specialist: claim extraction, parse-error lane
* Boss Agent: adjudication decisions, system metrics analysis

All LLM calls are **mocked** — tests assert schema conformance and confidence-path branching without real API calls.

### Routing Tests (`test_routing.py`)

**38 tests** covering every conditional edge:

* High confidence → proceed
* Low confidence → retry → retry again → human review
* Conflict detection → Boss escalation
* Boss decision → compile\_report or human review
* Human review → approved or failed

### Audit Log Tests (`test_audit_log.py`)

**14 tests** covering:

* Hash computation and chaining
* Chain verification (valid chains)
* Tamper detection (modified hash)
* Broken link detection (wrong prev\_hash)
* Empty chain handling
* Deterministic hashing

### E2E Pipeline Tests (`test_pipeline_e2e.py`)

**6 tests** covering full pipeline runs:

* Happy path: contract document → archived
* Low confidence path: ambiguous document → review
* Medium confidence path: route to human review
* Ingest node: manifest creation and file reading
* Full pipeline with mocked LLM: correspondence → archived
* Ingest: real PDF bytes transcription

These tests spin up a complete LangGraph graph with all 13 nodes and mock the LLM layer, verifying:

* State flows through all nodes correctly
* Files move between bins
* Archive paths are correct
* Manifests are created

***

## Test Fixtures

### Pilot sample set

For live end-to-end pilots (not the unit suite), see `docs/examples/samples/`: 25 legal PDFs on the live manifest (real CC-BY-4.0 CUAD/Atticus contracts + LegalBench MAUD merger agreements + repo-written synthetic text including three `insurance_claim` coverage letters) with a ground-truth `manifest.csv`, built by `scripts/prepare_samples.py` (and `scripts/fetch_external_samples.py` for the external corpus) and evaluated by `scripts/run_pilot.py` (`--mock` for a deterministic run over the live 25-sample set, `--real` for actual LLM accuracy on the 15 real committed documents, `--baseline` to diff two runs, `--source <corpus>` to run one dataset). Real runs are restricted to the actual committed legal documents (CUAD/Atticus PDFs + LegalBench MAUD); the repo-written synthetic `.txt` samples (corporate / correspondence / insurance / ambiguous) are mock-only and are refused by `--real`. See `docs/examples/samples/README.md`. Per-agent isolation eval (no full graph) is `scripts/run_agent_eval.py`.

### Shared Fixtures (`conftest.py`)

| Fixture                      | Description                                                        |
| ---------------------------- | ------------------------------------------------------------------ |
| `temp_base_dir`              | Creates a temporary `MAILROOM_BASE_DIR` with all bin directories   |
| `mock_openai_client`         | Mocks `llm.client.OpenAI` with a high-confidence contract response |
| `mock_low_confidence_client` | Mocks with a low-confidence response                               |
| `sample_*_text`              | Reads fixture files for each doc type                              |
| `all_fixture_files`          | Dictionary of all fixture file contents                            |

### Document Fixtures (`src/tests/fixtures/`)

| Fixture (under `src/tests/fixtures/<class>/`) | Type             | Purpose                                                               |
| --------------------------------------------- | ---------------- | --------------------------------------------------------------------- |
| `contract/sample_msa.txt`                     | Contract         | Full Master Services Agreement — happy path                           |
| `contract/sample_nda.txt`                     | Contract         | NDA — simpler contract variant                                        |
| `contract/ambiguous_doc.txt`                  | Contract         | Deliberately vague — tests low-confidence path                        |
| `corporate_record/sample_bylaws.txt`          | Corporate Record | Full corporate bylaws                                                 |
| `corporate_record/sample_resolution.txt`      | Corporate Record | Board resolution                                                      |
| `correspondence/sample_demand_letter.txt`     | Correspondence   | Formal demand letter — action items                                   |
| `correspondence/ambiguous_memo.txt`           | Correspondence   | Interoffice memo mixing multiple doc types                            |
| `insurance_claim/sample_claim.txt`            | Insurance Claim  | Base insurance-claim document                                         |
| `insurance_claim/sample_claim_approved.txt`   | Insurance Claim  | Local-pack approved hail claim (coverage determination contrast)      |
| `insurance_claim/sample_claim_denied.txt`     | Insurance Claim  | Local-pack auto denial (lapse)                                        |
| `insurance_claim/sample_claim_partial.txt`    | Insurance Claim  | Local-pack partial water + betterment exclusion                       |
| `court_opinion/sample_opinion.txt`            | Court Opinion    | Appellate opinion — exercises suppression + weight-of-evidence issues |
| `due_diligence/sample_dd_report.txt`          | Due Diligence    | Comprehensive DD report with risk flags *(retired class — kept on disk)* |
| `due_diligence/sample_checklist.txt`          | Due Diligence    | Simple DD checklist — tests sparse data *(retired class — kept on disk)* |

Fixtures are grouped **one directory per document class**. There is deliberately **no `compliance_filing/` directory**: the compliance arm (module, schema, prompts, and its eval fixtures) was removed on 2026-09-15 — see [Agents](agents.md). `court_opinion` and `due_diligence` are retired classes whose fixtures are **retained on disk** so their historical suites still run.

***

## Writing New Tests

### Agent Unit Test Pattern

```python
class TestNewAgent:
    def test_extract(self, sample_text, mock_openai_client):
        # Set the mock response
        mock_openai_client.chat.completions.create.return_value \
            .choices[0].message.content = '{"field": "value", "confidence": 0.95}'

        # Import and instantiate
        from agents.new_specialist import NewSpecialist
        agent = NewSpecialist()
        agent.client = mock_openai_client
        agent.model = "test-model"

        # Call and assert
        result = agent.extract(sample_text[:1000])
        assert result.get("confidence", 0) >= 0.80
        assert "value" in result.get("field", "")
```

### Routing Test Pattern

```python
from graph.routing import after_classify

def test_routing_scenario():
    state = {
        "classification_confidence": 0.50,
        "classification_attempts": 1,
        "doc_type": "contract",
    }
    assert after_classify(state) == "retry_classify"
```

### E2E Test Pattern

```python
def test_full_pipeline(self, temp_base_dir, mock_openai_client):
    from graph.build_graph import build_graph

    # Create test file
    inbox = temp_base_dir / "pipeline" / "inbox"
    test_file = inbox / "test.txt"
    test_file.write_text("Document content...")

    # Build graph and run
    graph = build_graph()
    config = {"configurable": {"thread_id": "test-1"}}
    result = graph.invoke(initial_state, config)

    # Assert final state
    assert result["stage"] == "archived"
```

***

## Test Configuration

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["src/tests"]
pythonpath = ["src", "."]
```

Tests auto-discover asyncio fixtures. No `@pytest.mark.asyncio` decorator needed for sync tests — the graph now uses sync nodes.
