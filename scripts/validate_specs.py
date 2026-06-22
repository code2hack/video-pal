#!/usr/bin/env python3
"""Validate the structure, lifecycle, and stable IDs in spec/."""

from __future__ import annotations

import sys
from pathlib import Path

from spec_utils import (
    ALLOWED_SPEC_STATUSES,
    FEATURE_ID_RE,
    QUALITY_ID_RE,
    REQ_ID_RE,
    AC_ID_RE,
    SpecError,
    heading_ids,
    parse_front_matter,
)

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    ROOT / "spec" / "README.md",
    ROOT / "spec" / "product.md",
    ROOT / "spec" / "quality.md",
    ROOT / "spec" / "templates" / "feature-spec.md",
]
COMMON_META = {"id", "title", "status", "revision", "decision_owner", "approval_ref"}
FEATURE_META = COMMON_META | {"depends_on", "supersedes", "superseded_by"}
REQUIRED_FEATURE_SECTIONS = [
    "Problem",
    "Goals",
    "Non-goals",
    "Functional requirements",
    "Acceptance criteria",
    "Edge cases",
    "Verification matrix",
    "Open questions",
]


def error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_lifecycle(path: Path, meta: dict, errors: list[str]) -> None:
    missing = COMMON_META - meta.keys()
    if missing:
        error(errors, f"{path}: missing metadata: {', '.join(sorted(missing))}")
        return

    status = meta.get("status")
    if status not in ALLOWED_SPEC_STATUSES:
        error(errors, f"{path}: invalid status {status!r}")
    if not isinstance(meta.get("revision"), int) or meta["revision"] < 1:
        error(errors, f"{path}: revision must be a positive integer")
    if meta.get("decision_owner") != "human":
        error(errors, f"{path}: decision_owner must be 'human'")
    if status in {"approved", "implemented"} and not meta.get("approval_ref"):
        error(errors, f"{path}: {status} specs require approval_ref")
    if status == "superseded" and not meta.get("superseded_by"):
        error(errors, f"{path}: superseded specs require superseded_by")


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED_FILES:
        if not path.is_file():
            error(errors, f"missing required file: {path.relative_to(ROOT)}")

    if errors:
        print("Specification validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    seen_specs: dict[str, Path] = {}
    seen_normative_ids: dict[str, Path] = {}

    for path in [ROOT / "spec" / "product.md", ROOT / "spec" / "quality.md"]:
        try:
            meta, body = parse_front_matter(path)
        except SpecError as exc:
            error(errors, str(exc))
            continue
        validate_lifecycle(path.relative_to(ROOT), meta, errors)
        spec_id = meta.get("id")
        if spec_id in seen_specs:
            error(errors, f"duplicate specification id {spec_id}: {path} and {seen_specs[spec_id]}")
        elif isinstance(spec_id, str):
            seen_specs[spec_id] = path

        if path.name == "quality.md":
            quality_ids = heading_ids(body, QUALITY_ID_RE)
            for quality_id in quality_ids:
                if quality_id in seen_normative_ids:
                    error(errors, f"duplicate normative id {quality_id}")
                seen_normative_ids[quality_id] = path
            if meta.get("status") in {"approved", "implemented"} and not quality_ids:
                error(errors, f"{path.relative_to(ROOT)}: approved quality spec needs at least one QUAL-NNN heading")
            if meta.get("status") in {"approved", "implemented"} and "TBD" in body.upper():
                error(errors, f"{path.relative_to(ROOT)}: approved quality spec contains TBD")

    feature_paths = sorted((ROOT / "spec" / "features").glob("*.md"))
    if not feature_paths:
        error(errors, "spec/features must contain at least one feature specification")

    for path in feature_paths:
        rel = path.relative_to(ROOT)
        try:
            meta, body = parse_front_matter(path)
        except SpecError as exc:
            error(errors, str(exc))
            continue

        missing = FEATURE_META - meta.keys()
        if missing:
            error(errors, f"{rel}: missing metadata: {', '.join(sorted(missing))}")
        validate_lifecycle(rel, meta, errors)

        spec_id = meta.get("id")
        if not isinstance(spec_id, str) or not FEATURE_ID_RE.fullmatch(spec_id):
            error(errors, f"{rel}: feature id must match VP-NNN")
            continue
        if spec_id in seen_specs:
            error(errors, f"duplicate specification id {spec_id}: {rel} and {seen_specs[spec_id].relative_to(ROOT)}")
        else:
            seen_specs[spec_id] = path

        for list_key in ("depends_on", "supersedes"):
            if not isinstance(meta.get(list_key), list):
                error(errors, f"{rel}: {list_key} must be an inline list")

        for section in REQUIRED_FEATURE_SECTIONS:
            if f"## {section}" not in body:
                error(errors, f"{rel}: missing section '## {section}'")

        requirements = heading_ids(body, REQ_ID_RE)
        criteria = heading_ids(body, AC_ID_RE)
        for identifier in requirements + criteria:
            if not identifier.startswith(f"{spec_id}-"):
                error(errors, f"{rel}: {identifier} does not belong to {spec_id}")
            if identifier in seen_normative_ids:
                error(errors, f"duplicate normative id {identifier}: {rel} and {seen_normative_ids[identifier].relative_to(ROOT)}")
            else:
                seen_normative_ids[identifier] = path

        if meta.get("status") in {"approved", "implemented"}:
            if not requirements:
                error(errors, f"{rel}: approved feature spec needs at least one requirement")
            if not criteria:
                error(errors, f"{rel}: approved feature spec needs at least one acceptance criterion")
            if "TBD" in body.upper():
                error(errors, f"{rel}: approved feature spec contains TBD")

    if errors:
        print("Specification validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print(f"Specification validation passed: {len(seen_specs)} specs, {len(seen_normative_ids)} normative IDs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
