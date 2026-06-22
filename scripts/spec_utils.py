#!/usr/bin/env python3
"""Shared helpers for the dependency-free specification validators."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ALLOWED_SPEC_STATUSES = {"draft", "approved", "implemented", "superseded"}
FEATURE_ID_RE = re.compile(r"^VP-\d{3}$")
REQ_ID_RE = re.compile(r"^(VP-\d{3})-REQ-\d{3}$")
AC_ID_RE = re.compile(r"^(VP-\d{3})-AC-\d{3}$")
QUALITY_ID_RE = re.compile(r"^QUAL-\d{3}$")


class SpecError(ValueError):
    """Raised when a specification cannot be parsed."""


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "null":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith("[") or value.startswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise SpecError(f"invalid JSON-compatible value {value!r}: {exc}") from exc
    return value


def parse_front_matter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SpecError(f"{path}: missing opening front-matter delimiter")

    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise SpecError(f"{path}: missing closing front-matter delimiter") from exc

    metadata: dict[str, Any] = {}
    for line_number, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise SpecError(f"{path}:{line_number}: expected 'key: value'")
        key, raw = line.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            raise SpecError(f"{path}:{line_number}: invalid metadata key {key!r}")
        if key in metadata:
            raise SpecError(f"{path}:{line_number}: duplicate metadata key {key!r}")
        metadata[key] = parse_scalar(raw)

    body = "\n".join(lines[end + 1 :]).strip() + "\n"
    return metadata, body


def heading_ids(body: str, pattern: re.Pattern[str]) -> list[str]:
    ids: list[str] = []
    for line in body.splitlines():
        match = re.match(r"^#{3,6}\s+([^:]+):", line)
        if match:
            candidate = match.group(1).strip()
            if pattern.fullmatch(candidate):
                ids.append(candidate)
    return ids


def load_feature_specs(root: Path) -> dict[str, dict[str, Any]]:
    specs: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "spec" / "features").glob("*.md")):
        metadata, body = parse_front_matter(path)
        spec_id = metadata.get("id")
        if not isinstance(spec_id, str):
            raise SpecError(f"{path}: metadata 'id' must be a string")
        specs[path.relative_to(root).as_posix()] = {
            "metadata": metadata,
            "body": body,
            "requirements": heading_ids(body, REQ_ID_RE),
            "acceptance_criteria": heading_ids(body, AC_ID_RE),
        }
    return specs
