from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELECT = ROOT / "scripts" / "project-loop" / "select_work.py"
VALIDATE = ROOT / "scripts" / "project-loop" / "validate_receipt.py"
FIXTURES = ROOT / "tests" / "project-loop" / "fixtures"


def run_select(candidates: dict, tmp_path: Path, feature_list: dict | None = None, config_text: str | None = None) -> subprocess.CompletedProcess[str]:
    candidates_path = tmp_path / "candidates.json"
    candidates_path.write_text(json.dumps(candidates), encoding="utf-8")
    feature_path = tmp_path / "feature_list.json"
    feature_path.write_text(json.dumps(feature_list or {"features": []}), encoding="utf-8")
    config_path = tmp_path / "project-loop.toml"
    config_path.write_text(config_text or (ROOT / "project-loop.toml").read_text(encoding="utf-8"), encoding="utf-8")
    output_path = tmp_path / "receipt.json"
    return subprocess.run(
        [
            sys.executable,
            str(SELECT),
            "--config",
            str(config_path),
            "--candidates",
            str(candidates_path),
            "--feature-list",
            str(feature_path),
            "--output",
            str(output_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def receipt(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "receipt.json").read_text(encoding="utf-8"))


def valid_candidate(**overrides: object) -> dict:
    data: dict[str, object] = {
        "type": "pull_request",
        "number": 10,
        "title": "Ready PR",
        "state": "open",
        "head_branch": "codex/ready-pr",
        "labels": ["ready:project-loop"],
        "dependencies": [],
    }
    data.update(overrides)
    return data


def test_zero_eligible_items_returns_successful_noop(tmp_path: Path) -> None:
    result = run_select({"pull_requests": [], "issues": []}, tmp_path)
    assert result.returncode == 0, result.stderr
    data = receipt(tmp_path)
    assert data["stop_reason"] == "no-eligible-work"
    assert data["work_item"] is None
    assert data["changed_files"] == []


def test_multiple_candidates_selects_exactly_one_deterministically(tmp_path: Path) -> None:
    candidates = json.loads((FIXTURES / "eligible_candidates.json").read_text(encoding="utf-8"))
    result = run_select(candidates, tmp_path)
    assert result.returncode == 0, result.stderr
    data = receipt(tmp_path)
    assert data["stop_reason"] == "stage0-selected"
    assert data["work_item"]["number"] == 7
    statuses = [entry["status"] for entry in data["validation_delta"]]
    assert statuses.count("eligible") == 1
    assert statuses.count("not-selected") == 1


def test_blocked_dependency_and_draft_spec_are_rejected(tmp_path: Path) -> None:
    feature_list = {"features": [{"id": "feat-x", "status": "blocked"}]}
    candidates = {
        "pull_requests": [
            valid_candidate(number=1, dependencies=["feat-x"]),
            valid_candidate(number=2, spec_status="draft", requires_approved_spec=True),
        ]
    }
    result = run_select(candidates, tmp_path, feature_list=feature_list)
    assert result.returncode == 0, result.stderr
    reasons = [reason for item in receipt(tmp_path)["validation_delta"] for reason in item["reasons"]]
    assert "dependency not done: feat-x" in reasons
    assert "required specification is not approved" in reasons
    assert receipt(tmp_path)["stop_reason"] == "no-eligible-work"


def test_active_claim_and_conflicting_writer_are_rejected(tmp_path: Path) -> None:
    candidates = {
        "pull_requests": [
            valid_candidate(number=1, active_claim=True),
            valid_candidate(number=2, conflicting_writer=True),
        ]
    }
    result = run_select(candidates, tmp_path)
    assert result.returncode == 0, result.stderr
    reasons = [reason for item in receipt(tmp_path)["validation_delta"] for reason in item["reasons"]]
    assert "active claim exists" in reasons
    assert "conflicting writer exists" in reasons


def test_protected_branch_is_rejected(tmp_path: Path) -> None:
    candidates = {"pull_requests": [valid_candidate(head_branch="main")]}
    result = run_select(candidates, tmp_path)
    assert result.returncode == 0, result.stderr
    assert "protected branch: main" in receipt(tmp_path)["validation_delta"][0]["reasons"]


def test_malformed_configuration_fails_closed(tmp_path: Path) -> None:
    result = run_select(
        {"pull_requests": [valid_candidate()]},
        tmp_path,
        config_text="schema_version = 1\n",
    )
    assert result.returncode != 0
    assert "failed closed" in result.stderr
    assert not (tmp_path / "receipt.json").exists()


def test_malformed_receipt_is_rejected() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATE), str(FIXTURES / "malformed_receipt.json")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert "missing fields" in result.stdout


def test_verifier_failure_receipt_records_delta_and_stop() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATE), str(FIXTURES / "verifier_failure_receipt.json")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_unchanged_delta_and_attempt_limit_receipts_are_valid(tmp_path: Path) -> None:
    base = json.loads((FIXTURES / "verifier_failure_receipt.json").read_text(encoding="utf-8"))
    for stop_reason in ("unchanged-validation-delta", "attempt-limit-reached"):
        data = dict(base)
        data["stop_reason"] = stop_reason
        data["attempts"] = 3
        path = tmp_path / f"{stop_reason}.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        result = subprocess.run([sys.executable, str(VALIDATE), str(path)], cwd=ROOT, text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stdout + result.stderr


def test_repair_disabled_rejects_repair_without_file_edits(tmp_path: Path) -> None:
    candidates = {"pull_requests": [valid_candidate(requested_action="repair")]}
    result = run_select(candidates, tmp_path)
    assert result.returncode == 0, result.stderr
    data = receipt(tmp_path)
    assert data["stop_reason"] == "no-eligible-work"
    assert data["attempts"] == 0
    assert data["changed_files"] == []
    assert "repair disabled" in data["validation_delta"][0]["reasons"]


def test_unexpected_changed_file_receipt_requires_delta_and_changed_files(tmp_path: Path) -> None:
    data = json.loads((FIXTURES / "verifier_failure_receipt.json").read_text(encoding="utf-8"))
    data["stop_reason"] = "unexpected-changed-file"
    data["checker_result"] = "error"
    data["changed_files"] = ["AGENTS.md"]
    path = tmp_path / "unexpected.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = subprocess.run([sys.executable, str(VALIDATE), str(path)], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
