#!/usr/bin/env python3
"""Check feature_list.json references and implementation evidence traceability."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from spec_utils import SpecError, load_feature_specs

ROOT = Path(__file__).resolve().parents[1]
FEATURE_LIST = ROOT / "feature_list.json"
ALLOWED_KINDS = {"governance", "product-definition", "implementation", "documentation", "handoff"}
ALLOWED_STATUSES = {"not-started", "in-progress", "blocked", "done", "cancelled"}
REQUIRED_FIELDS = {
    "id",
    "kind",
    "name",
    "description",
    "spec_ref",
    "spec_revision",
    "requirements",
    "acceptance_criteria",
    "dependencies",
    "status",
    "branch",
    "pull_request",
    "blockers",
    "evidence",
}


def main() -> int:
    errors: list[str] = []
    try:
        data = json.loads(FEATURE_LIST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Traceability validation failed: cannot read feature_list.json: {exc}")
        return 1

    if data.get("schema_version") != 2:
        errors.append("feature_list.json schema_version must be 2")
    features = data.get("features")
    if not isinstance(features, list):
        errors.append("feature_list.json 'features' must be a list")
        features = []

    try:
        specs = load_feature_specs(ROOT)
    except SpecError as exc:
        errors.append(str(exc))
        specs = {}

    by_id: dict[str, dict[str, Any]] = {}
    for feature in features:
        if not isinstance(feature, dict):
            errors.append("every feature entry must be an object")
            continue
        feature_id = feature.get("id")
        if not isinstance(feature_id, str):
            errors.append("feature entry has missing or non-string id")
            continue
        if feature_id in by_id:
            errors.append(f"duplicate feature id {feature_id}")
        by_id[feature_id] = feature

        missing = REQUIRED_FIELDS - feature.keys()
        if missing:
            errors.append(f"{feature_id}: missing fields: {', '.join(sorted(missing))}")
        if feature.get("kind") not in ALLOWED_KINDS:
            errors.append(f"{feature_id}: invalid kind {feature.get('kind')!r}")
        if feature.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{feature_id}: invalid status {feature.get('status')!r}")
        for key in ("requirements", "acceptance_criteria", "dependencies", "blockers", "evidence"):
            if not isinstance(feature.get(key), list):
                errors.append(f"{feature_id}: {key} must be a list")

    for feature_id, feature in by_id.items():
        for dependency in feature.get("dependencies", []):
            if dependency == feature_id:
                errors.append(f"{feature_id}: cannot depend on itself")
            elif dependency not in by_id:
                errors.append(f"{feature_id}: unknown dependency {dependency}")

        spec_ref = feature.get("spec_ref")
        spec_data = None
        if spec_ref is not None:
            if not isinstance(spec_ref, str) or not spec_ref.startswith("spec/features/"):
                errors.append(f"{feature_id}: spec_ref must be null or a path under spec/features/")
            elif spec_ref not in specs:
                errors.append(f"{feature_id}: referenced spec does not exist: {spec_ref}")
            else:
                spec_data = specs[spec_ref]
                revision = spec_data["metadata"].get("revision")
                if feature.get("spec_revision") != revision:
                    errors.append(f"{feature_id}: spec_revision {feature.get('spec_revision')!r} does not match {revision!r}")
                known_requirements = set(spec_data["requirements"])
                known_criteria = set(spec_data["acceptance_criteria"])
                for req in feature.get("requirements", []):
                    if req not in known_requirements:
                        errors.append(f"{feature_id}: unknown requirement {req} in {spec_ref}")
                for criterion in feature.get("acceptance_criteria", []):
                    if criterion not in known_criteria:
                        errors.append(f"{feature_id}: unknown acceptance criterion {criterion} in {spec_ref}")

        if spec_ref is None and feature.get("spec_revision") is not None:
            errors.append(f"{feature_id}: spec_revision must be null when spec_ref is null")

        if feature.get("kind") == "implementation":
            if spec_data is None:
                errors.append(f"{feature_id}: implementation work requires a feature spec")
            else:
                spec_status = spec_data["metadata"].get("status")
                if spec_status not in {"approved", "implemented"}:
                    errors.append(f"{feature_id}: implementation requires an approved or implemented spec, found {spec_status!r}")
            if not feature.get("requirements"):
                errors.append(f"{feature_id}: implementation work requires requirement references")
            if not feature.get("acceptance_criteria"):
                errors.append(f"{feature_id}: implementation work requires acceptance criteria")

        if feature.get("status") == "in-progress" and not feature.get("branch"):
            errors.append(f"{feature_id}: in-progress work requires a branch")
        if feature.get("status") == "done" and not feature.get("evidence"):
            errors.append(f"{feature_id}: done work requires evidence")

        evidence = feature.get("evidence", [])
        passing_criteria: set[str] = set()
        for index, record in enumerate(evidence):
            if not isinstance(record, dict):
                errors.append(f"{feature_id}: evidence[{index}] must be an object")
                continue
            for key in ("summary", "command", "result", "environment", "commit", "acceptance_criteria"):
                if key not in record:
                    errors.append(f"{feature_id}: evidence[{index}] missing {key}")
            if not isinstance(record.get("acceptance_criteria"), list):
                errors.append(f"{feature_id}: evidence[{index}].acceptance_criteria must be a list")
            if str(record.get("result", "")).lower() in {"pass", "passed", "success"}:
                passing_criteria.update(record.get("acceptance_criteria", []))

        if feature.get("kind") == "implementation" and feature.get("status") == "done":
            for criterion in feature.get("acceptance_criteria", []):
                if criterion not in passing_criteria:
                    errors.append(f"{feature_id}: completed criterion {criterion} lacks passing evidence")

    if errors:
        print("Traceability validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print(f"Traceability validation passed: {len(by_id)} features, {len(specs)} feature specs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
