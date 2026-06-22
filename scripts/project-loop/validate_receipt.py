#!/usr/bin/env python3
"""Validate a project-loop receipt without external dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = {
    "schema_version",
    "run_id",
    "actor",
    "runtime",
    "work_item",
    "claim",
    "timestamp",
    "starting_commit",
    "ending_commit",
    "attempts",
    "commands",
    "changed_files",
    "validation_delta",
    "checker_result",
    "stop_reason",
    "next_actor",
    "known_risks",
}

CHECKER_RESULTS = {"not-run", "pass", "fail", "error", "unavailable"}
STOP_REASONS = {
    "no-eligible-work",
    "stage0-selected",
    "malformed-configuration",
    "protected-branch",
    "blocked",
    "human-decision-required",
    "checker-unavailable",
    "verifier-failed",
    "repair-disabled",
    "unchanged-validation-delta",
    "attempt-limit-reached",
    "unexpected-changed-file",
}
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def load_receipt(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read receipt JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("receipt must be a JSON object")
    return data


def require_type(errors: list[str], receipt: dict[str, Any], key: str, expected: type) -> None:
    if key in receipt and not isinstance(receipt[key], expected):
        errors.append(f"{key} must be {expected.__name__}")


def validate_receipt(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_FIELDS - receipt.keys()
    if missing:
        errors.append(f"missing fields: {', '.join(sorted(missing))}")
        return errors

    if receipt.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for key in ("run_id", "actor", "runtime", "timestamp", "starting_commit", "checker_result", "stop_reason", "next_actor"):
        require_type(errors, receipt, key, str)
    if receipt.get("ending_commit") is not None and not isinstance(receipt.get("ending_commit"), str):
        errors.append("ending_commit must be string or null")
    require_type(errors, receipt, "attempts", int)
    for key in ("commands", "changed_files", "validation_delta", "known_risks"):
        require_type(errors, receipt, key, list)

    if isinstance(receipt.get("attempts"), int) and receipt["attempts"] < 0:
        errors.append("attempts must be non-negative")
    if receipt.get("checker_result") not in CHECKER_RESULTS:
        errors.append(f"checker_result must be one of {', '.join(sorted(CHECKER_RESULTS))}")
    if receipt.get("stop_reason") not in STOP_REASONS:
        errors.append(f"stop_reason must be one of {', '.join(sorted(STOP_REASONS))}")
    if isinstance(receipt.get("timestamp"), str) and not TIMESTAMP_RE.fullmatch(receipt["timestamp"]):
        errors.append("timestamp must be UTC format YYYY-MM-DDTHH:MM:SSZ")

    claim = receipt.get("claim")
    if not isinstance(claim, dict):
        errors.append("claim must be an object")
    else:
        for key in ("branch", "starting_commit", "claimed_at"):
            if key not in claim:
                errors.append(f"claim missing {key}")
        if claim.get("branch") is not None and not isinstance(claim.get("branch"), str):
            errors.append("claim.branch must be string or null")
        if not isinstance(claim.get("starting_commit"), str):
            errors.append("claim.starting_commit must be string")
        if not isinstance(claim.get("claimed_at"), str) or not TIMESTAMP_RE.fullmatch(str(claim.get("claimed_at"))):
            errors.append("claim.claimed_at must be UTC format YYYY-MM-DDTHH:MM:SSZ")

    work_item = receipt.get("work_item")
    if work_item is not None:
        if not isinstance(work_item, dict):
            errors.append("work_item must be object or null")
        else:
            for key in ("type", "number", "title"):
                if key not in work_item:
                    errors.append(f"work_item missing {key}")
            if not isinstance(work_item.get("type"), str):
                errors.append("work_item.type must be string")
            if not isinstance(work_item.get("number"), int):
                errors.append("work_item.number must be integer")
            if not isinstance(work_item.get("title"), str):
                errors.append("work_item.title must be string")

    for index, command in enumerate(receipt.get("commands", [])):
        if not isinstance(command, dict):
            errors.append(f"commands[{index}] must be an object")
            continue
        for key in ("command", "exit_code", "summary"):
            if key not in command:
                errors.append(f"commands[{index}] missing {key}")
        if not isinstance(command.get("command"), str):
            errors.append(f"commands[{index}].command must be string")
        if not isinstance(command.get("exit_code"), int):
            errors.append(f"commands[{index}].exit_code must be integer")
        if not isinstance(command.get("summary"), str):
            errors.append(f"commands[{index}].summary must be string")

    if not all(isinstance(path, str) for path in receipt.get("changed_files", [])):
        errors.append("changed_files entries must be strings")
    if not all(isinstance(risk, str) for risk in receipt.get("known_risks", [])):
        errors.append("known_risks entries must be strings")

    stop_reason = receipt.get("stop_reason")
    if stop_reason == "no-eligible-work" and receipt.get("work_item") is not None:
        errors.append("no-eligible-work receipts must have work_item null")
    if stop_reason == "stage0-selected" and receipt.get("work_item") is None:
        errors.append("stage0-selected receipts require a work_item")
    if stop_reason in {"verifier-failed", "unchanged-validation-delta", "attempt-limit-reached", "unexpected-changed-file"}:
        if not receipt.get("validation_delta"):
            errors.append(f"{stop_reason} receipts require validation_delta")
    if stop_reason == "verifier-failed" and receipt.get("checker_result") not in {"fail", "error"}:
        errors.append("verifier-failed receipts require checker_result fail or error")
    if stop_reason in {"unchanged-validation-delta", "attempt-limit-reached"} and receipt.get("attempts", 0) < 1:
        errors.append(f"{stop_reason} receipts require at least one attempt")
    if stop_reason == "repair-disabled":
        if receipt.get("attempts") != 0:
            errors.append("repair-disabled receipts must have zero attempts")
        if receipt.get("changed_files"):
            errors.append("repair-disabled receipts must not change files")
    if stop_reason == "unexpected-changed-file" and not receipt.get("changed_files"):
        errors.append("unexpected-changed-file receipts require changed_files")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validate_receipt.py <receipt.json>", file=sys.stderr)
        return 2
    try:
        receipt = load_receipt(Path(argv[1]))
    except ValueError as exc:
        print(f"Receipt validation failed: {exc}", file=sys.stderr)
        return 1
    errors = validate_receipt(receipt)
    if errors:
        print("Receipt validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Receipt validation passed: schema_version={receipt['schema_version']} stop_reason={receipt['stop_reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
