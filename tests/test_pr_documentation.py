"""Offline acceptance tests for the documentation changed in PR #1.

This repository contains no pipeline implementation. These tests validate the
published content and example contracts, not upstream runtime behavior. They
use only the Python standard library and never execute documentation snippets,
contact external services, or require Git history.

From the repository root: python3 -B -m unittest discover -s tests -v
"""

import ast
import configparser
from decimal import Decimal
from pathlib import Path
import re
import shlex
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REFERENCE = "pipeline-reference-llm-mailroom/"
DEPLOYMENT = REFERENCE + "deployment/README.md"

# Explicit scope from PR #1, head 5503921c26c1e63d42bdb930e8cc61c110b30e1e.
# Keeping this list independent of Git makes tests work in source archives too.
CHANGED_PAGES = (
    "README.md",
    "about-this-site/maintaining.md",
    "experiment-reports/experiment-reports.md",
    "how-it-fits-together/architecture.md",
    "how-it-fits-together/data-and-corpora.md",
    "how-it-fits-together/governance.md",
    "how-it-fits-together/repo-index.md",
    "mailroom-dataset/classes-and-strata.md",
    "mailroom-dataset/configs.md",
    "mailroom-dataset/eda-reports.md",
    "mailroom-dataset/mailroom-dataset.md",
    REFERENCE + "agents.md",
    REFERENCE + "api.md",
    REFERENCE + "architecture.md",
    REFERENCE + "configuration.md",
    DEPLOYMENT,
    REFERENCE + "deployment/docker-deployment.md",
    REFERENCE + "deployment/langfuse.md",
    REFERENCE + "deployment/litellm-gateway.md",
    REFERENCE + "deployment/llamafiles.md",
    REFERENCE + "deployment/modal-vllm.md",
    REFERENCE + "deployment/phoenix.md",
    REFERENCE + "deployment/postgres.md",
    REFERENCE + "gmail-intake.md",
    REFERENCE + "local-models.md",
    REFERENCE + "operational-procedure.md",
    REFERENCE + "sister-repos.md",
    REFERENCE + "testing.md",
    "repository-guides/repos/README.md",
    "repository-guides/repos/local-mailroom-sandbox/README.md",
    "repository-guides/repos/local-mailroom-sandbox/local-mailroom-sandbox-docs.md",
    "repository-guides/repos/local-mailroom-sandbox/local-mailroom-sandbox-reports.md",
    "start-here/getting-started.md",
    "start-here/glossary.md",
    "start-here/overview.md",
    "the-pipeline-in-depth/extraction-schemas.md",
    "the-pipeline-in-depth/flowchart.md",
    "the-pipeline-in-depth/running.md",
    "the-pipeline-in-depth/scoring-and-metrics.md",
)

# The pages use triple-backtick fences and inline Markdown links. This is a
# deliberately bounded reader for those forms, not a general Markdown parser.
FENCE = re.compile(r"^[ \t]*```([^\n]*)\n(.*?)^[ \t]*```[ \t]*$", re.M | re.S)
LINK = re.compile(r"\[[^\]\n]*\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")


def read_page(name):
    return (DOCS / name).read_text(encoding="utf-8")


def code_blocks(text, language):
    return [body for kind, body in FENCE.findall(text) if kind.strip() == language]


def section(text, heading):
    """Return one section, excluding the next heading of equal or lesser depth."""
    level = len(heading) - len(heading.lstrip("#"))
    match = re.search(r"^" + re.escape(heading) + r"\s*$", text, re.M)
    if match is None:
        raise AssertionError("Missing section: " + heading)
    return re.split(r"^#{1," + str(level) + r"} ", text[match.end():], maxsplit=1, flags=re.M)[0]


def local_target(source, destination):
    url = urlsplit(destination.strip("<>"))
    if url.scheme or url.netloc:
        return None
    target = (source.parent / unquote(url.path)).resolve() if url.path else source
    return target / "README.md" if target.is_dir() else target


class NavigationAcceptanceTests(unittest.TestCase):
    def test_every_changed_page_is_published_once(self):
        summary = DOCS / "SUMMARY.md"
        targets = [local_target(summary, link) for link in LINK.findall(read_page("SUMMARY.md"))]
        for name in CHANGED_PAGES:
            with self.subTest(page=name):
                self.assertTrue((DOCS / name).is_file())
                self.assertEqual(targets.count(DOCS / name), 1, "Missing or duplicate sidebar entry")

    def test_changed_pages_link_to_existing_local_files_inside_the_book(self):
        for name in CHANGED_PAGES:
            source = DOCS / name
            prose = FENCE.sub("", read_page(name))
            # HTML image tags are used alongside Markdown image links.
            destinations = LINK.findall(prose) + re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', prose)
            for destination in destinations:
                with self.subTest(page=name, link=destination):
                    target = local_target(source, destination)
                    if target is None:
                        continue
                    self.assertIn(DOCS, target.parents, "Link escapes the published content directory")
                    self.assertTrue(target.is_file(), "Broken local link: " + str(target))

    def test_new_schema_navigation_matches_heading_fragments(self):
        text = read_page("the-pipeline-in-depth/extraction-schemas.md")
        guide = section(text, "## Find what you need")
        fragments = [link[1:] for link in LINK.findall(guide) if link.startswith("#")]
        self.assertGreaterEqual(len(fragments), 9)
        # These headings have plain words, inline code, and parentheses; no
        # duplicate headings or custom GitBook IDs need slug disambiguation.
        headings = re.findall(r"^#{1,6} (.+)$", FENCE.sub("", text), re.M)
        slugs = {re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-") for heading in headings}
        for fragment in fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, slugs)


class DatasetExampleAcceptanceTests(unittest.TestCase):
    def setUp(self):
        blocks = code_blocks(read_page("mailroom-dataset/configs.md"), "python")
        self.assertEqual(len(blocks), 1, "Identify the blind/ground-truth example explicitly")
        self.tree = ast.parse(blocks[0])

    def test_both_configs_use_the_same_fixed_revision_and_test_split(self):
        assignments = [node for node in self.tree.body if isinstance(node, ast.Assign)]
        constants = next(node for node in assignments if isinstance(node.targets[0], ast.Tuple))
        self.assertEqual([item.id for item in constants.targets[0].elts], ["REPO", "REV"])
        self.assertEqual(ast.literal_eval(constants.value), ("Lucius-Morningstar/mailroom-dataset", "v9.2"))
        calls = [node for node in ast.walk(self.tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name) and node.func.id == "load_dataset"]
        self.assertEqual(len(calls), 2)
        configs = set()
        for call in calls:
            with self.subTest(call=ast.unparse(call)):
                self.assertEqual(len(call.args), 2)
                self.assertEqual(call.args[0].id, "REPO")
                configs.add(ast.literal_eval(call.args[1]))
                keywords = {item.arg: item.value for item in call.keywords}
                self.assertEqual(keywords["revision"].id, "REV")
                self.assertEqual(ast.literal_eval(keywords["split"]), "test")
        self.assertEqual(configs, {"default", "ground_truth"})

    def test_join_uses_filename_and_keeps_document_text_out_of_scored_labels(self):
        assignments = {node.targets[0].id: node.value for node in self.tree.body
                       if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)}
        # Catch a swapped blind/GT source, not just the presence of both configs.
        for name, config in (("blind", "default"), ("gt", "ground_truth")):
            with self.subTest(frame=name):
                loader = assignments[name].func.value
                self.assertEqual(ast.literal_eval(loader.args[1]), config)
        merge = assignments["scored"]
        self.assertEqual(merge.func.attr, "merge")
        self.assertEqual(merge.func.value.value.id, "blind")
        self.assertEqual(ast.literal_eval(merge.func.value.slice), ["filename"])
        self.assertEqual(len(merge.args), 1)
        self.assertEqual(merge.args[0].value.id, "gt")
        self.assertEqual(ast.literal_eval(merge.args[0].slice), ["filename", "expected", "expected_subclass"])
        self.assertEqual({item.arg: ast.literal_eval(item.value) for item in merge.keywords}, {"on": "filename"})


class DeploymentExampleAcceptanceTests(unittest.TestCase):
    def test_process_managers_set_environment_separately_from_the_executable(self):
        examples = code_blocks(read_page(DEPLOYMENT), "ini")
        self.assertEqual(len(examples), 2)
        for example, name, directory, environment, command in (
            (examples[0], "Service", "WorkingDirectory", "Environment", "ExecStart"),
            (examples[1], "program:watcher", "directory", "environment", "command"),
        ):
            with self.subTest(manager=name):
                config = configparser.ConfigParser(interpolation=None)
                config.read_string(example)
                settings = config[name]
                self.assertEqual(shlex.split(settings[environment]), ["PYTHONPATH=src"])
                argv = shlex.split(settings[command])
                self.assertEqual(argv, [settings[directory] + "/.venv/bin/python", "-m", "pipeline.watcher"])
                self.assertNotIn("=", argv[0], "An environment assignment is not an executable")

    def test_restore_uses_one_snapshot_and_moves_existing_directories_before_copying(self):
        restore = section(read_page(DEPLOYMENT), "### Restore procedure")
        commands = [shlex.split(line, comments=True)
                    for block in code_blocks(restore, "bash") for line in block.splitlines()]
        commands = [command for command in commands if command]
        copies = [command for command in commands if command[0] == "cp"]
        self.assertEqual(len(copies), 4)
        for artifact in ("mailroom.db", "checkpoints.db", "archive", "manifests"):
            with self.subTest(artifact=artifact):
                expected = ["cp"] + (["-R"] if artifact in ("archive", "manifests") else [])
                expected += ["backup/<date>/" + artifact, "data/" + artifact]
                self.assertIn(expected, copies, "Restore must use the same dated snapshot")
                if artifact in ("archive", "manifests"):
                    move = ["mv", "data/" + artifact, "data/" + artifact + ".pre-restore"]
                    self.assertIn(move, commands)
                    self.assertLess(commands.index(move), commands.index(expected),
                                    "Copying first nests the backup and retains stale files")


class ScoringExampleAcceptanceTests(unittest.TestCase):
    def setUp(self):
        text = read_page("the-pipeline-in-depth/scoring-and-metrics.md")
        self.example = text.split("**A worked example.**", 1)[1].split("> **Note on `type_bands`.**", 1)[0]
        self.rows = {}
        for line in self.example.splitlines():
            if line.startswith("| `"):
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                self.assertEqual(len(cells), 5)
                field = cells[0].strip("`")
                self.assertNotIn(field, self.rows, "Duplicate field changes the mean")
                self.rows[field] = cells
        self.assertEqual(set(self.rows), {"effective_date", "governing_law", "parties", "term_length"})

    def test_reported_mean_includes_the_missing_field(self):
        scores = [Decimal(cells[-1]) for cells in self.rows.values()]
        reported = re.search(r"/\s*4\s*=\s*\*\*([0-9.]+)\*\*", self.example)
        self.assertIsNotNone(reported)
        self.assertEqual(sum(scores) / len(scores), Decimal(reported.group(1)))
        missing = self.rows["term_length"]
        self.assertEqual(missing[3], "(missing)")
        self.assertEqual(Decimal(missing[-1]), Decimal("0"))

    def test_partial_party_match_is_the_inclusive_lower_boundary(self):
        parties = self.rows["parties"]
        expected = {value.strip() for value in parties[2].split(";")}
        predicted = {value.strip() for value in parties[3].split(";")}
        self.assertEqual(len(expected), 2)
        self.assertEqual(len(predicted), 1)
        recall = Decimal(len(expected & predicted)) / len(expected)
        self.assertEqual(Decimal(parties[-1]), recall)
        band = re.search(r"ambiguous band \(([0-9.]+) to ([0-9.]+), inclusive\)", self.example)
        self.assertIsNotNone(band)
        self.assertEqual(recall, Decimal(band.group(1)))
        self.assertLess(recall, Decimal(band.group(2)))
        self.assertIn("`ambiguous_fields`", self.example)
        self.assertIn("`needs_judge_review` is true", self.example)


if __name__ == "__main__":
    unittest.main()
