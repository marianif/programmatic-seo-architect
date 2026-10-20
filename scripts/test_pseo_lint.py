#!/usr/bin/env python3
"""Tests for pseo_lint.py. Run with:

    python3 -m unittest scripts/test_pseo_lint.py
"""

from __future__ import annotations

import csv
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pseo_lint  # noqa: E402

HEADERS = [
    "path",
    "status",
    "indexable",
    "http_status",
    "canonical_path",
    "redirect_to",
    "page_family",
    "primary_query",
    "title",
    "meta_description",
    "unique_facts",
    "content_hash",
    "lastmod",
    "notes",
]


def base_row(**overrides: str) -> dict[str, str]:
    row = {
        "path": "/fattura/designer/forfettario",
        "status": "published",
        "indexable": "true",
        "http_status": "200",
        "canonical_path": "/fattura/designer/forfettario",
        "redirect_to": "",
        "page_family": "fattura",
        "primary_query": "fattura designer forfettario",
        "title": "Fattura per designer forfettario — calcolo e modello",
        "meta_description": (
            "Calcola la fattura per un designer in regime forfettario: "
            "aliquota, contributi, ritenuta e modello pronto."
        ),
        "unique_facts": "8",
        "content_hash": "a1b2c3d4e5f6",
        "lastmod": date.today().isoformat(),
        "notes": "",
    }
    row.update(overrides)
    return row


def lint(rows: list[dict[str, str]], *args: str) -> tuple[int, str, str]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "inventory.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(rows)

        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = pseo_lint.main([str(path), *args])
        return code, stdout.getvalue(), stderr.getvalue()


class PseoLintTests(unittest.TestCase):
    def test_valid_published_page_passes(self) -> None:
        code, output, _ = lint([base_row()])
        self.assertEqual(code, 0, output)
        self.assertIn("RESULT: PASS", output)

    def test_duplicate_path_fails(self) -> None:
        rows = [
            base_row(),
            base_row(
                primary_query="altra query",
                content_hash="ffffffffffff",
            ),
        ]
        code, output, _ = lint(rows)
        self.assertEqual(code, 1)
        self.assertIn("path.duplicate", output)

    def test_published_page_must_be_self_canonical(self) -> None:
        code, output, _ = lint(
            [base_row(canonical_path="/fattura/designer")]
        )
        self.assertEqual(code, 1)
        self.assertIn("published.canonical", output)

    def test_published_page_needs_unique_facts(self) -> None:
        code, output, _ = lint([base_row(unique_facts="2")])
        self.assertEqual(code, 1)
        self.assertIn("facts.thin", output)

    def test_candidate_cannot_be_indexable(self) -> None:
        code, output, _ = lint(
            [
                base_row(
                    status="candidate",
                    indexable="true",
                    canonical_path="",
                )
            ]
        )
        self.assertEqual(code, 1)
        self.assertIn("draft.indexable", output)

    def test_canonical_cycle_fails(self) -> None:
        rows = [
            base_row(
                path="/a",
                status="suppressed",
                indexable="false",
                canonical_path="/b",
                title="A page title that is long enough",
                meta_description=(
                    "A description that is long enough to avoid a warning "
                    "and is still useful for the reader."
                ),
                content_hash="aaaaaaaaaaaa",
                primary_query="query a",
            ),
            base_row(
                path="/b",
                status="suppressed",
                indexable="false",
                canonical_path="/a",
                title="B page title that is long enough",
                meta_description=(
                    "B description that is long enough to avoid a warning "
                    "and is still useful for the reader."
                ),
                content_hash="bbbbbbbbbbbb",
                primary_query="query b",
            ),
        ]
        code, output, _ = lint(rows)
        self.assertEqual(code, 1)
        self.assertIn("canonical.cycle", output)

    def test_template_placeholder_fails(self) -> None:
        code, output, _ = lint(
            [base_row(title="Fattura per {entity} in regime forfettario")]
        )
        self.assertEqual(code, 1)
        self.assertIn("title.placeholder", output)

    def test_duplicate_content_hash_fails(self) -> None:
        rows = [
            base_row(),
            base_row(
                path="/fattura/designer/ordinario",
                canonical_path="/fattura/designer/ordinario",
                primary_query="fattura designer ordinario",
                title="Fattura per designer ordinario — calcolo e modello",
                meta_description=(
                    "Calcola la fattura per un designer in regime ordinario: "
                    "IVA, contributi, ritenuta e modello pronto."
                ),
                content_hash="a1b2c3d4e5f6",
            ),
        ]
        code, output, _ = lint(rows)
        self.assertEqual(code, 1)
        self.assertIn("content.duplicate", output)

    def test_retired_redirect_needs_target(self) -> None:
        code, output, _ = lint(
            [
                base_row(
                    status="retired",
                    indexable="false",
                    http_status="301",
                    redirect_to="",
                    canonical_path="",
                )
            ]
        )
        self.assertEqual(code, 1)
        self.assertIn("retired.redirect_missing", output)

    def test_published_page_cannot_have_redirect(self) -> None:
        code, output, _ = lint([base_row(redirect_to="/fattura/designer")])
        self.assertEqual(code, 1)
        self.assertIn("redirect.non_retired", output)

    def test_missing_file_returns_format_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.csv"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = pseo_lint.main([str(missing)])
        self.assertEqual(code, 2)
        self.assertIn("cannot read file", stderr.getvalue())

    def test_json_output(self) -> None:
        code, output, _ = lint([base_row()], "--json")
        self.assertEqual(code, 0, output)
        self.assertIn('"ok": true', output)
        self.assertIn('"sitemap_eligible": 1', output)

    def test_strict_turns_warnings_into_errors(self) -> None:
        # A short title is a warning, not an error.
        code, output, _ = lint([base_row(title="Fattura")])
        self.assertEqual(code, 0, output)
        self.assertIn("title.short", output)

        code, output, _ = lint([base_row(title="Fattura")], "--strict")
        self.assertEqual(code, 1)
        self.assertIn("RESULT: FAIL", output)


if __name__ == "__main__":
    unittest.main()
