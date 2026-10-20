#!/usr/bin/env python3
"""Validate a programmatic SEO page inventory.

The inventory is the human-readable view of the page registry. This script
checks the rules that are easy to break at scale: duplicate paths, published
pages that are not indexable, non-self canonicals, thin unique-fact counts,
template placeholders, duplicate content hashes, and sitemap eligibility.

Usage:
    python3 pseo_lint.py inventory.csv
    python3 pseo_lint.py inventory.csv --json
    python3 pseo_lint.py inventory.csv --strict

Exit codes:
    0  no errors (warnings allowed unless --strict)
    1  validation errors
    2  file or format error
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

REQUIRED_COLUMNS = [
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

OPTIONAL_COLUMNS = ["h1"]

VALID_STATUSES = {"candidate", "eligible", "published", "suppressed", "retired"}
VALID_HTTP_STATUSES = {200, 301, 302, 404, 410}
RESERVED_FIRST_SEGMENTS = {
    "api",
    "_next",
    "admin",
    "sitemap",
    "sitemap.xml",
    "robots",
    "robots.txt",
    "favicon.ico",
}
MAX_PATH_DEPTH = 5
MAX_CANONICAL_HOPS = 10
MAX_REDIRECT_HOPS = 10


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    row: int | None
    path: str
    message: str


@dataclass
class Row:
    row_number: int
    path: str
    status: str
    indexable: bool | None
    http_status: int | None
    canonical_path: str
    redirect_to: str
    page_family: str
    primary_query: str
    title: str
    meta_description: str
    h1: str
    unique_facts: int | None
    content_hash: str
    lastmod_raw: str
    lastmod: date | None
    notes: str


def add(issues: list[Issue], severity: str, code: str, row: Row | None, message: str) -> None:
    issues.append(
        Issue(
            severity=severity,
            code=code,
            row=row.row_number if row else None,
            path=row.path if row else "",
            message=message,
        )
    )


def normalize(value: str | None) -> str:
    return (value or "").strip()


def parse_bool(value: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    return None


def parse_int(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def path_problems(path: str) -> list[tuple[str, str]]:
    """Return (severity, message) pairs for a path."""
    problems: list[tuple[str, str]] = []

    if not path.startswith("/"):
        problems.append(("error", "path must start with /"))
    if "//" in path:
        problems.append(("error", "path contains a double slash"))
    if path != "/" and path.endswith("/"):
        problems.append(("error", "path must not end with a slash"))
    if any(char.isspace() for char in path):
        problems.append(("error", "path contains whitespace"))
    if "?" in path or "#" in path:
        problems.append(("error", "path must not contain a query string or fragment"))
    if path != path.lower():
        problems.append(("warning", "path contains uppercase characters"))

    segments = [segment for segment in path.split("/") if segment]
    if len(segments) > MAX_PATH_DEPTH:
        problems.append(
            ("warning", f"path has {len(segments)} segments; keep the hierarchy shallow")
        )

    for segment in segments:
        if segment in {".", ".."}:
            problems.append(("error", "path contains a traversal segment"))
        elif not re.match(r"^[\w\-~.%]+$", segment, re.UNICODE):
            problems.append(
                ("warning", f"segment {segment!r} contains unusual characters")
            )

    if segments and segments[0].lower() in RESERVED_FIRST_SEGMENTS:
        problems.append(("error", f"first segment {segments[0]!r} is reserved"))

    return problems


def text_problems(value: str, label: str) -> list[tuple[str, str]]:
    problems: list[tuple[str, str]] = []

    if "{" in value or "}" in value:
        problems.append(("error", f"{label} contains a template placeholder"))
    if re.search(r"\b(undefined|null|nan)\b", value, re.IGNORECASE):
        problems.append(("error", f"{label} contains a placeholder value"))

    return problems


def load_rows(path: Path) -> tuple[list[Row], list[Issue], list[str], str | None]:
    issues: list[Issue] = []
    missing_columns: list[str] = []

    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fieldnames = [normalize(name) for name in (reader.fieldnames or [])]
            missing_columns = [
                column for column in REQUIRED_COLUMNS if column not in fieldnames
            ]
            if missing_columns:
                return [], issues, missing_columns, None

            rows: list[Row] = []
            for row_number, raw in enumerate(reader, start=2):
                cleaned = {
                    normalize(key): normalize(value)
                    for key, value in raw.items()
                    if key is not None
                }
                if not any(cleaned.values()):
                    continue

                path_value = cleaned.get("path", "")
                status = cleaned.get("status", "").lower()
                indexable = parse_bool(cleaned.get("indexable", ""))
                http_status = parse_int(cleaned.get("http_status", ""))
                canonical_path = cleaned.get("canonical_path", "")
                redirect_to = cleaned.get("redirect_to", "")
                unique_facts = parse_int(cleaned.get("unique_facts", ""))
                lastmod_raw = cleaned.get("lastmod", "")

                row = Row(
                    row_number=row_number,
                    path=path_value,
                    status=status,
                    indexable=indexable,
                    http_status=http_status,
                    canonical_path=canonical_path or path_value,
                    redirect_to=redirect_to,
                    page_family=cleaned.get("page_family", ""),
                    primary_query=cleaned.get("primary_query", ""),
                    title=cleaned.get("title", ""),
                    meta_description=cleaned.get("meta_description", ""),
                    h1=cleaned.get("h1", ""),
                    unique_facts=unique_facts,
                    content_hash=cleaned.get("content_hash", ""),
                    lastmod_raw=lastmod_raw,
                    lastmod=parse_date(lastmod_raw),
                    notes=cleaned.get("notes", ""),
                )
                rows.append(row)

    except OSError as error:
        return [], issues, [], f"cannot read file: {error}"

    return rows, issues, missing_columns, None


def validate(
    rows: list[Row],
    min_facts: int,
    min_title: int,
    max_title: int,
    min_description: int,
    max_description: int,
    stale_days: int,
) -> list[Issue]:
    issues: list[Issue] = []
    today = date.today()
    seen_paths: dict[str, int] = {}

    for row in rows:
        # Path and core fields.
        if not row.path:
            add(issues, "error", "path.empty", row, "path is required")
        else:
            for severity, message in path_problems(row.path):
                add(issues, severity, "path.invalid", row, message)

            if row.path in seen_paths:
                add(
                    issues,
                    "error",
                    "path.duplicate",
                    row,
                    f"duplicate path; first seen on row {seen_paths[row.path]}",
                )
            else:
                seen_paths[row.path] = row.row_number

        if row.status not in VALID_STATUSES:
            add(
                issues,
                "error",
                "status.invalid",
                row,
                f"status must be one of {sorted(VALID_STATUSES)}",
            )
            continue

        if row.indexable is None:
            add(
                issues,
                "error",
                "indexable.invalid",
                row,
                "indexable must be true or false",
            )

        if row.http_status is None:
            add(
                issues,
                "error",
                "http_status.invalid",
                row,
                "http_status must be an integer",
            )
        elif row.http_status not in VALID_HTTP_STATUSES:
            add(
                issues,
                "error",
                "http_status.invalid",
                row,
                f"http_status must be one of {sorted(VALID_HTTP_STATUSES)}",
            )

        # Text fields.
        for field_name, value in (
            ("title", row.title),
            ("meta_description", row.meta_description),
            ("h1", row.h1),
        ):
            if value:
                for severity, message in text_problems(value, field_name):
                    add(issues, severity, f"{field_name}.placeholder", row, message)

        if row.title:
            if len(row.title) < min_title:
                add(
                    issues,
                    "warning",
                    "title.short",
                    row,
                    f"title is {len(row.title)} characters; target at least {min_title}",
                )
            if len(row.title) > max_title:
                add(
                    issues,
                    "warning",
                    "title.long",
                    row,
                    f"title is {len(row.title)} characters; target at most {max_title}",
                )

        if row.meta_description:
            if len(row.meta_description) < min_description:
                add(
                    issues,
                    "warning",
                    "description.short",
                    row,
                    f"description is {len(row.meta_description)} characters; target at least {min_description}",
                )
            if len(row.meta_description) > max_description:
                add(
                    issues,
                    "warning",
                    "description.long",
                    row,
                    f"description is {len(row.meta_description)} characters; target at most {max_description}",
                )

        if row.h1 and len(row.h1) > 70:
            add(issues, "warning", "h1.long", row, "h1 is longer than 70 characters")

        # Lastmod.
        if row.lastmod_raw and row.lastmod is None:
            add(
                issues,
                "error",
                "lastmod.invalid",
                row,
                f"lastmod {row.lastmod_raw!r} is not an ISO date",
            )
        elif row.lastmod and row.lastmod > today:
            add(issues, "error", "lastmod.future", row, "lastmod is in the future")
        elif (
            row.status == "published"
            and row.lastmod
            and (today - row.lastmod).days > stale_days
        ):
            add(
                issues,
                "warning",
                "lastmod.stale",
                row,
                f"lastmod is older than {stale_days} days; verify the data is still current",
            )

        # Status-specific rules.
        if row.status == "published":
            if row.indexable is not True:
                add(issues, "error", "published.not_indexable", row, "published page must be indexable")
            if row.http_status != 200:
                add(issues, "error", "published.status", row, "published page must return 200")
            if row.canonical_path != row.path:
                add(
                    issues,
                    "error",
                    "published.canonical",
                    row,
                    "published page must be self-canonical",
                )
            if not row.title:
                add(issues, "error", "title.missing", row, "published page needs a title")
            if not row.meta_description:
                add(
                    issues,
                    "error",
                    "description.missing",
                    row,
                    "published page needs a meta description",
                )
            if not row.page_family:
                add(issues, "error", "family.missing", row, "published page needs a page_family")
            if not row.primary_query:
                add(issues, "error", "query.missing", row, "published page needs a primary_query")
            if row.unique_facts is None:
                add(issues, "error", "facts.invalid", row, "unique_facts must be an integer")
            elif row.unique_facts < min_facts:
                add(
                    issues,
                    "error",
                    "facts.thin",
                    row,
                    f"published page has {row.unique_facts} unique facts; minimum is {min_facts}",
                )
            if len(row.content_hash) < 8:
                add(
                    issues,
                    "error",
                    "hash.missing",
                    row,
                    "published page needs a content_hash of at least 8 characters",
                )
            if not row.lastmod:
                add(issues, "error", "lastmod.missing", row, "published page needs a lastmod")

        elif row.status == "suppressed":
            if row.indexable is not False:
                add(issues, "error", "suppressed.indexable", row, "suppressed page must be non-indexable")
            if row.http_status != 200:
                add(issues, "error", "suppressed.status", row, "suppressed page must still return 200")
            if not row.canonical_path:
                add(
                    issues,
                    "warning",
                    "suppressed.canonical",
                    row,
                    "suppressed page should declare a canonical target",
                )
            elif row.canonical_path == row.path:
                add(
                    issues,
                    "warning",
                    "suppressed.self_canonical",
                    row,
                    "suppressed page is self-canonical but noindex; confirm this is intentional",
                )

        elif row.status == "retired":
            if row.indexable is not False:
                add(issues, "error", "retired.indexable", row, "retired page must be non-indexable")
            if row.http_status in (301, 302):
                if not row.redirect_to:
                    add(
                        issues,
                        "error",
                        "retired.redirect_missing",
                        row,
                        "redirected page needs a redirect_to target",
                    )
            elif row.http_status in (404, 410):
                if row.redirect_to:
                    add(
                        issues,
                        "warning",
                        "retired.redirect_ignored",
                        row,
                        "redirect_to is set but the status is 404/410",
                    )
            else:
                add(
                    issues,
                    "error",
                    "retired.status",
                    row,
                    "retired page must be 301, 302, 404, or 410",
                )

        else:  # candidate or eligible
            if row.indexable is True:
                add(
                    issues,
                    "error",
                    "draft.indexable",
                    row,
                    f"{row.status} page must not be indexable",
                )
            if row.status == "eligible":
                if row.unique_facts is None or row.unique_facts < min_facts:
                    add(
                        issues,
                        "warning",
                        "eligible.facts",
                        row,
                        f"eligible page has fewer than {min_facts} unique facts",
                    )
                if not row.title:
                    add(issues, "warning", "eligible.title", row, "eligible page has no title yet")

        # Redirect target sanity.
        if row.redirect_to:
            if row.redirect_to == row.path:
                add(issues, "error", "redirect.self", row, "redirect target is the page itself")
            if row.status != "retired":
                add(
                    issues,
                    "error",
                    "redirect.non_retired",
                    row,
                    "redirect_to is only valid for retired pages",
                )

    # Cross-row checks.
    paths = {row.path: row for row in rows}
    canonical_map = {
        row.path: row.canonical_path
        for row in rows
        if row.canonical_path and row.canonical_path != row.path
    }
    redirect_map = {
        row.path: row.redirect_to for row in rows if row.redirect_to
    }

    for row in rows:
        if row.canonical_path and row.canonical_path != row.path:
            target = paths.get(row.canonical_path)
            if target is None:
                add(
                    issues,
                    "warning",
                    "canonical.unknown",
                    row,
                    "canonical target is not in the inventory; verify it exists and returns 200",
                )
            elif target.status != "published":
                add(
                    issues,
                    "warning",
                    "canonical.not_published",
                    row,
                    f"canonical target is {target.status}, not published",
                )

            chain = follow_chain(row.path, canonical_map, MAX_CANONICAL_HOPS)
            if chain == "cycle":
                add(issues, "error", "canonical.cycle", row, "canonical chain contains a cycle")
            elif chain == "too_long":
                add(
                    issues,
                    "error",
                    "canonical.too_long",
                    row,
                    f"canonical chain exceeds {MAX_CANONICAL_HOPS} hops",
                )
            elif chain > 1:
                add(
                    issues,
                    "warning",
                    "canonical.chain",
                    row,
                    f"canonical chain is {chain} hops; point directly to the final canonical",
                )

        if row.redirect_to:
            target = paths.get(row.redirect_to)
            if target is None:
                add(
                    issues,
                    "warning",
                    "redirect.unknown",
                    row,
                    "redirect target is not in the inventory; verify it returns 200",
                )
            elif target.status == "retired" and target.redirect_to:
                add(
                    issues,
                    "warning",
                    "redirect.chain",
                    row,
                    "redirect target is itself retired; point to the final URL",
                )
            elif target.status != "published":
                add(
                    issues,
                    "warning",
                    "redirect.target_not_published",
                    row,
                    f"redirect target is {target.status}, not published",
                )

            chain = follow_chain(row.path, redirect_map, MAX_REDIRECT_HOPS)
            if chain == "cycle":
                add(issues, "error", "redirect.cycle", row, "redirect chain contains a cycle")
            elif chain == "too_long":
                add(
                    issues,
                    "error",
                    "redirect.too_long",
                    row,
                    f"redirect chain exceeds {MAX_REDIRECT_HOPS} hops",
                )
            elif chain > 1:
                add(
                    issues,
                    "warning",
                    "redirect.chain",
                    row,
                    f"redirect chain is {chain} hops; point directly to the final URL",
                )

    # Duplicate content hashes among published pages.
    published_hashes: dict[str, list[Row]] = defaultdict(list)
    for row in rows:
        if row.status == "published" and len(row.content_hash) >= 8:
            published_hashes[row.content_hash].append(row)
    for content_hash, group in published_hashes.items():
        if len(group) > 1:
            paths_list = ", ".join(item.path for item in group)
            add(
                issues,
                "error",
                "content.duplicate",
                group[0],
                f"duplicate content_hash {content_hash[:12]}… across: {paths_list}",
            )

    # Duplicate titles and descriptions among published pages.
    for label, getter in (
        ("title", lambda item: item.title),
        ("description", lambda item: item.meta_description),
    ):
        groups: dict[str, list[Row]] = defaultdict(list)
        for row in rows:
            value = getter(row)
            if row.status == "published" and value:
                groups[re.sub(r"\s+", " ", value.lower()).strip()].append(row)
        for _, group in groups.items():
            if len(group) > 1:
                paths_list = ", ".join(item.path for item in group)
                add(
                    issues,
                    "warning",
                    f"{label}.duplicate",
                    group[0],
                    f"duplicate {label} across: {paths_list}",
                )

    # Cannibalization signal: same query in the same family.
    query_groups: dict[tuple[str, str], list[Row]] = defaultdict(list)
    for row in rows:
        if row.status == "published" and row.primary_query and row.page_family:
            key = (row.page_family.lower(), row.primary_query.lower())
            query_groups[key].append(row)
    for _, group in query_groups.items():
        if len(group) > 1:
            paths_list = ", ".join(item.path for item in group)
            add(
                issues,
                "warning",
                "query.duplicate",
                group[0],
                f"same primary_query in one family across: {paths_list}",
            )

    return issues


def follow_chain(start: str, mapping: dict[str, str], limit: int) -> int | str:
    """Return hop count, 'cycle', or 'too_long'."""
    seen: set[str] = set()
    current = start
    hops = 0

    while current in mapping:
        if current in seen:
            return "cycle"
        seen.add(current)
        current = mapping[current]
        hops += 1
        if hops > limit:
            return "too_long"

    return hops


def run(args: argparse.Namespace) -> int:
    rows, load_issues, missing_columns, file_error = load_rows(args.inventory)

    if file_error:
        print("pSEO inventory lint", file=sys.stderr)
        print(f"file: {args.inventory}", file=sys.stderr)
        print(file_error, file=sys.stderr)
        return 2

    if missing_columns:
        print("pSEO inventory lint", file=sys.stderr)
        print(f"file: {args.inventory}", file=sys.stderr)
        print("missing required columns:", ", ".join(missing_columns), file=sys.stderr)
        return 2

    if load_issues:
        for issue in load_issues:
            print(f"{issue.severity}: {issue.message}", file=sys.stderr)
        return 2

    if not rows:
        print("pSEO inventory lint", file=sys.stderr)
        print(f"file: {args.inventory}", file=sys.stderr)
        print("no data rows found", file=sys.stderr)
        return 2

    issues = validate(
        rows=rows,
        min_facts=args.min_facts,
        min_title=args.min_title,
        max_title=args.max_title,
        min_description=args.min_description,
        max_description=args.max_description,
        stale_days=args.stale_days,
    )

    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    if args.strict and warnings:
        errors.extend(warnings)
        warnings = []

    status_counts = Counter(row.status for row in rows)
    sitemap_eligible = [
        row
        for row in rows
        if row.status == "published"
        and row.indexable is True
        and row.http_status == 200
        and row.canonical_path == row.path
    ]

    ok = not errors

    if args.json:
        print(
            json.dumps(
                {
                    "ok": ok,
                    "file": str(args.inventory),
                    "rows": len(rows),
                    "status_counts": dict(sorted(status_counts.items())),
                    "sitemap_eligible": len(sitemap_eligible),
                    "errors": [asdict(issue) for issue in errors],
                    "warnings": [asdict(issue) for issue in warnings],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print("pSEO inventory lint")
        print(f"file: {args.inventory}")
        print(f"rows: {len(rows)}")
        print(
            "status: "
            + ", ".join(f"{name}={count}" for name, count in sorted(status_counts.items()))
        )
        print(f"sitemap-eligible: {len(sitemap_eligible)}")
        print(f"errors: {len(errors)}")
        print(f"warnings: {len(warnings)}")

        if errors:
            print("\nERRORS")
            for issue in sorted(errors, key=issue_sort_key):
                row = f"row {issue.row}" if issue.row else "file"
                print(f"  {row:>8}  {issue.path or '-':<45} [{issue.code}] {issue.message}")

        if warnings:
            print("\nWARNINGS")
            for issue in sorted(warnings, key=issue_sort_key):
                row = f"row {issue.row}" if issue.row else "file"
                print(f"  {row:>8}  {issue.path or '-':<45} [{issue.code}] {issue.message}")

        print("\nRESULT:", "PASS" if ok else "FAIL")

    return 0 if ok else 1


def issue_sort_key(issue: Issue) -> tuple[int, str, str]:
    return (issue.row or 0, issue.path, issue.code)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a programmatic SEO page inventory CSV.",
    )
    parser.add_argument("inventory", type=Path, help="Path to the inventory CSV")
    parser.add_argument(
        "--min-facts",
        type=int,
        default=5,
        help="Minimum unique facts for a published page (default: 5)",
    )
    parser.add_argument("--min-title", type=int, default=15)
    parser.add_argument("--max-title", type=int, default=65)
    parser.add_argument("--min-description", type=int, default=50)
    parser.add_argument("--max-description", type=int, default=160)
    parser.add_argument(
        "--stale-days",
        type=int,
        default=730,
        help="Warn when a published page's lastmod is older than this (default: 730)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
