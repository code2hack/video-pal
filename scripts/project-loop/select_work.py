#!/usr/bin/env python3
"""Stage 0 project-loop dry-run selector."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_receipt import validate_receipt

ROOT = Path(__file__).resolve().parents[2]


class ConfigError(ValueError):
    """Raised when project-loop.toml is missing required safety settings."""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: cannot read JSON: {exc}") from exc


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def load_config(path: Path) -> dict[str, Any]:
    try:
        config = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"{path}: cannot read TOML: {exc}") from exc

    required_top = ["schema_version", "repository", "default_branch", "dry_run", "repair_enabled", "receipt_schema_version"]
    missing = [key for key in required_top if key not in config]
    if missing:
        raise ConfigError(f"{path}: missing required keys: {', '.join(missing)}")
    if config["schema_version"] != 1:
        raise ConfigError("schema_version must be 1")
    if config["receipt_schema_version"] != 1:
        raise ConfigError("receipt_schema_version must be 1")
    if config.get("dry_run") is not True:
        raise ConfigError("Stage 0 requires dry_run = true")
    if config.get("repair_enabled") is not False:
        raise ConfigError("Stage 0 requires repair_enabled = false")

    for section in ("protected", "eligibility", "runtime", "commands", "maker", "checker", "budgets", "github", "receipt"):
        if section not in config or not isinstance(config[section], dict):
            raise ConfigError(f"missing [{section}] section")

    if not config["eligibility"].get("ready_markers"):
        raise ConfigError("eligibility.ready_markers must not be empty")
    if not config["protected"].get("branches"):
        raise ConfigError("protected.branches must not be empty")
    if config["budgets"].get("max_work_items_per_cycle") != 1:
        raise ConfigError("Stage 0 requires budgets.max_work_items_per_cycle = 1")
    if config["github"].get("receipt_comments_enabled") is not False:
        raise ConfigError("Stage 0 requires github.receipt_comments_enabled = false")
    if config["github"].get("allowed_mutations", []) != []:
        raise ConfigError("Stage 0 requires github.allowed_mutations = []")
    return config


def load_features(path: Path) -> dict[str, dict[str, Any]]:
    data = load_json(path)
    features = data.get("features", []) if isinstance(data, dict) else []
    return {
        item["id"]: item
        for item in features
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def candidate_items(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict) and isinstance(data.get("candidates"), list):
        raw = data["candidates"]
    elif isinstance(data, dict):
        raw = []
        for key, item_type in (("pull_requests", "pull_request"), ("issues", "issue")):
            for item in data.get(key, []):
                if isinstance(item, dict):
                    copy = dict(item)
                    copy.setdefault("type", item_type)
                    raw.append(copy)
    else:
        raise ValueError("candidate file must be an object or list")
    return [dict(item) for item in raw if isinstance(item, dict)]


def names(values: Any) -> set[str]:
    result: set[str] = set()
    if not isinstance(values, list):
        return result
    for value in values:
        if isinstance(value, str):
            result.add(value)
        elif isinstance(value, dict) and isinstance(value.get("name"), str):
            result.add(value["name"])
    return result


def is_protected_branch(branch: str | None, protected: list[str]) -> bool:
    if not branch:
        return False
    for pattern in protected:
        if pattern.endswith("/*") and branch.startswith(pattern[:-1]):
            return True
        if branch == pattern:
            return True
    return False


def reject(reason: str, reasons: list[str]) -> None:
    if reason not in reasons:
        reasons.append(reason)


def evaluate(candidate: dict[str, Any], config: dict[str, Any], features: dict[str, dict[str, Any]]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    item_type = candidate.get("type")
    number = candidate.get("number")
    if item_type not in {"issue", "pull_request"}:
        reject("candidate type must be issue or pull_request", reasons)
    if not isinstance(number, int):
        reject("candidate number must be an integer", reasons)

    state = str(candidate.get("state", "open")).lower()
    if state != "open":
        reject(f"state is {state}", reasons)

    labels = names(candidate.get("labels", []))
    markers = labels | names(candidate.get("markers", []))
    ready_markers = set(config["eligibility"].get("ready_markers", []))
    if not (markers & ready_markers or candidate.get("ready") is True):
        reject("missing ready marker", reasons)

    terminal_markers = set(config["eligibility"].get("terminal_markers", []))
    terminal_hits = markers & terminal_markers
    if terminal_hits:
        reject(f"terminal marker present: {', '.join(sorted(terminal_hits))}", reasons)

    if candidate.get("draft") is True and config["eligibility"].get("allow_draft_prs") is not True:
        reject("draft pull request is not eligible", reasons)

    branch = candidate.get("head_branch") or candidate.get("branch")
    if not branch:
        reject("missing work branch", reasons)
    if is_protected_branch(branch, config["protected"].get("branches", [])) or candidate.get("protected_branch") is True:
        reject(f"protected branch: {branch}", reasons)

    if candidate.get("active_claim") is True or candidate.get("has_active_claim") is True:
        reject("active claim exists", reasons)
    if candidate.get("conflicting_writer") is True:
        reject("conflicting writer exists", reasons)
    if candidate.get("human_blocked") is True or candidate.get("human_decision_required") is True:
        reject("human decision required", reasons)
    blockers = candidate.get("blockers", [])
    if isinstance(blockers, list) and blockers:
        reject("candidate has blockers", reasons)

    for dependency in candidate.get("dependencies", []):
        if isinstance(dependency, str):
            feature = features.get(dependency)
            if feature is None:
                reject(f"unknown dependency: {dependency}", reasons)
            elif feature.get("status") != "done":
                reject(f"dependency not done: {dependency}", reasons)
        elif isinstance(dependency, dict):
            dep_name = dependency.get("id") or dependency.get("name") or dependency.get("number") or "dependency"
            if dependency.get("status") != "done":
                reject(f"dependency not done: {dep_name}", reasons)
        else:
            reject("dependency must be a string or object", reasons)

    spec_status = candidate.get("spec_status")
    if spec_status == "draft" or (candidate.get("requires_approved_spec") is True and spec_status not in {"approved", "implemented"}):
        reject("required specification is not approved", reasons)

    if candidate.get("requested_action") == "repair" and config.get("repair_enabled") is not True:
        reject("repair disabled", reasons)

    return not reasons, reasons


def work_item(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": str(candidate["type"]),
        "number": int(candidate["number"]),
        "title": str(candidate.get("title", "")),
        "branch": candidate.get("head_branch") or candidate.get("branch"),
    }


def sort_key(candidate: dict[str, Any]) -> tuple[int, str, int, str]:
    number = candidate.get("number") if isinstance(candidate.get("number"), int) else 999999
    return (
        int(candidate.get("priority", 1000)),
        str(candidate.get("type", "")),
        number,
        str(candidate.get("title", "")),
    )


def build_receipt(config: dict[str, Any], selected: dict[str, Any] | None, results: list[dict[str, Any]]) -> dict[str, Any]:
    now = utc_now()
    head = git_head()
    if selected is None:
        stop_reason = "no-eligible-work"
        next_actor = "project-loop"
        item = None
        branch = None
    else:
        stop_reason = "stage0-selected"
        next_actor = "human"
        item = work_item(selected)
        branch = item.get("branch")

    return {
        "schema_version": 1,
        "run_id": f"{now}-stage0",
        "actor": config["maker"].get("name", "codex"),
        "runtime": config["maker"].get("runtime", "DGX Spark"),
        "work_item": item,
        "claim": {
            "branch": branch,
            "starting_commit": head,
            "claimed_at": now,
        },
        "timestamp": now,
        "starting_commit": head,
        "ending_commit": head,
        "attempts": 0,
        "commands": [],
        "changed_files": [],
        "validation_delta": results,
        "checker_result": "not-run",
        "stop_reason": stop_reason,
        "next_actor": next_actor,
        "known_risks": [
            "Stage 0 performs dry-run selection only",
            "GitHub mutations are disabled by configuration",
            "Repair mode is disabled",
        ],
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 0 project-loop dry-run selection.")
    parser.add_argument("--config", default="project-loop.toml")
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--feature-list", default="feature_list.json")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    try:
        config = load_config(resolve_path(args.config))
        features = load_features(resolve_path(args.feature_list))
        candidates = candidate_items(load_json(resolve_path(args.candidates)))
    except (ConfigError, ValueError) as exc:
        print(f"project-loop selection failed closed: {exc}", file=sys.stderr)
        return 2

    results: list[dict[str, Any]] = []
    eligible: list[dict[str, Any]] = []
    for candidate in candidates:
        ok, reasons = evaluate(candidate, config, features)
        result = {
            "item": {
                "type": candidate.get("type"),
                "number": candidate.get("number"),
                "title": candidate.get("title", ""),
            },
            "status": "eligible" if ok else "rejected",
            "reasons": reasons,
        }
        results.append(result)
        if ok:
            eligible.append(candidate)

    selected = sorted(eligible, key=sort_key)[0] if eligible else None
    if selected is not None:
        selected_number = selected.get("number")
        for result in results:
            if result["status"] == "eligible" and result["item"].get("number") != selected_number:
                result["status"] = "not-selected"
                result["reasons"] = ["another eligible item sorted first"]

    receipt = build_receipt(config, selected, results)
    errors = validate_receipt(receipt)
    if errors:
        print("project-loop selection produced invalid receipt:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
