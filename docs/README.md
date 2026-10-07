# LLM-MAILROOM

This site is the one place to learn the Mailroom: the `llm-mailroom` pipeline and every repository built around it.

The Mailroom reads legal and business documents. It identifies the type of each document and extracts the important fields. Then it files the document in an archive with a tamper-evident audit trail. A team of specialist LLM agents does the work, one LangGraph state machine per document. More than a dozen repositories support the pipeline. They include a scoring library, an evaluation harness, corpus builders, and a local sandbox. They also include visualizers, an ML classifier, and the monorepo that connects them.

| If you want to…                                              | Read                                                                          |
| ------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| Understand what the Mailroom is and which repo does what     | [Overview](start-here/overview.md)                                            |
| Get something running in ten minutes                         | [Getting started](start-here/getting-started.md)                              |
| Run, evaluate, or audit the pipeline                         | [Running the pipeline](the-pipeline-in-depth/running.md)                      |
| See every node and routing condition                         | [Pipeline flowchart](the-pipeline-in-depth/flowchart.md)                      |
| Look up a config key, an agent, or an endpoint               | [Pipeline reference](pipeline-reference-llm-mailroom/architecture.md)         |
| Deploy with Docker, Modal, or Railway                        | [Deployment](pipeline-reference-llm-mailroom/deployment/)                     |
| See how data, prompts, scores and traces move between repos  | [The constellation](how-it-fits-together/architecture.md)                     |
| Read the dataset, EDA reports, and figures                   | [Mailroom dataset](mailroom-dataset/mailroom-dataset.md)                      |
| Work on a specific repository                                | [Repository guides](repository-guides/repos/)                                 |
| Look up a term like "Lane A", "STP" or "virtual member"      | [Glossary](start-here/glossary.md)                                            |
| See what changed in each release                             | [Changelog](changelog/README.md)                                              |

Install the pipeline (release v0.8.0, as of 2026-10-07). The last command starts the API, which embeds the inbox watcher:

```bash
git clone https://github.com/Exios66/llm-mailroom.git
cd llm-mailroom
pip install -e ".[dev]"
PYTHONPATH=src python -m api.main
```

<figure><img src=".gitbook/assets/banner.png" alt="Mailroom — a great horned owl postal worker sorting wax-sealed legal documents into bins by lamplight"><figcaption><p>The LLM-Mailroom masthead: the night-shift owl at the sorting desk.</p></figcaption></figure>

## From inbox to archive

The happy path costs two LLM generations. Everything else is procedural, gated, or a human's call.

| Stop         | What happens                                                                                                                                                                                                                                                                                                                        |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Intake**   | The watcher claims the upload by atomic rename into `processing/`, transcribes it, and cleans it. Nothing is ever truncated.                                                                                                                                                                                                        |
| **Classify** | The sorter picks one of five classes. At `0.97` or above it goes straight on. Between `0.88` and `0.97` it gets one re-classification pass, then a second-opinion reviewer agent (Lane A). Below `0.88` it retries, then goes to human review. Contracts, merger agreements and insurance claims use stricter per-class thresholds (`0.98` and `0.90`) because a wrong auto-pass costs more there. |
| **Extract**  | The class specialist fills its schema. Guardrails check the JSON before anything moves forward.                                                                                                                                                                                                                                     |
| **Verify**   | Extractions in the ambiguous confidence band get a judge, then an arbiter. Conflicts go to the boss agent or a human. See the [Pipeline flowchart](the-pipeline-in-depth/flowchart.md).                                                                                                                                             |
| **Archive**  | A procedural report, a catalog row in SQLite, and an archive entry sealed into the hash-chained audit log.                                                                                                                                                                                                                          |

## What ships with it

|                           |                                                                                                                      |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Five document classes** | Contracts, merger agreements, corporate records, correspondence, and insurance claims, each with its own specialist. |
| **Any model provider**    | OpenRouter, Ollama, or vLLM. Agents ask for a role; `taxonomy.yaml` decides the model.                               |
| **Traced end to end**     | Langfuse, Braintrust, or a local Arize Phoenix. The pipeline runs fine with none of them.                            |
| **Evaluation built in**   | A 23-sample pilot with ground truth, deterministic field scoring, LLM judges, and a LegalBench harness.              |

## Meet Fumi

<figure><img src=".gitbook/assets/fumi.gif" alt="Fumi in her postal uniform while Hermes the owl blinks on her shoulder" width="192"><figcaption><p>Fumi (文, "letter") is the mailroom's head maid. She wears a USPS-style carrier uniform, a mini cap, and a leather satchel. Hermes checks postmarks from her shoulder.</p></figcaption></figure>

<figure><img src=".gitbook/assets/hoot-icon.png" alt="Hermes, the pixel owl on Fumi's shoulder" width="96"><figcaption><p>Hermes is the pixel owl on Fumi's shoulder and the night-shift owl's junior colleague on the banner.</p></figcaption></figure>
