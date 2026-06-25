from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SELECT = ROOT / "scripts" / "project-loop" / "select_work.py"
VALIDATE = ROOT / "scripts" / "project-loop" / "validate_receipt.py"
FIXTURES = ROOT / "tests" / "project-loop" / "fixtures"


def config_text(tmp_path: Path, run_root: Path | None = None) -> str:
    run_root = run_root or tmp_path / "runs"
    worktree_root = tmp_path / "worktrees"
    return (
        (ROOT / "project-loop.toml")
        .read_text(encoding="utf-8")
        .replace('run_root = ".project-loop/runs"', f'run_root = "{run_root.as_posix()}"')
        .replace('worktree_root = ".project-loop/worktrees"', f'worktree_root = "{worktree_root.as_posix()}"')
    )


def run_select(
    candidates: dict,
    tmp_path: Path,
    feature_list: dict | None = None,
    config: str | None = None,
    output_arg: str | Path | None = None,
) -> subprocess.CompletedProcess[str]:
    candidates_path = tmp_path / "candidates.json"
    candidates_path.write_text(json.dumps(candidates), encoding="utf-8")
    feature_path = tmp_path / "feature_list.json"
    feature_path.write_text(json.dumps(feature_list or {"features": []}), encoding="utf-8")
    config_path = tmp_path / "project-loop.toml"
    config_path.write_text(config if config is not None else config_text(tmp_path), encoding="utf-8")
    output_path = Path(output_arg) if output_arg is not None else tmp_path / "runs" / "receipt.json"
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
    return json.loads((tmp_path / "runs" / "receipt.json").read_text(encoding="utf-8"))


def validate_data(data: dict, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    path = tmp_path / "receipt-under-test.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return subprocess.run([sys.executable, str(VALIDATE), str(path)], cwd=ROOT, text=True, capture_output=True, check=False)


def stage0_receipt(selected: bool) -> dict:
    branch = "codex/selected" if selected else None
    return {
        "schema_version": 1,
        "run_id": "2026-06-22T00:00:00Z-stage0",
        "actor": "codex",
        "runtime": "DGX Spark",
        "work_item": {
            "type": "pull_request",
            "number": 8,
            "title": "Selected PR",
            "branch": branch,
        }
        if selected
        else None,
        "claim": {
            "branch": branch,
            "starting_commit": "abc123",
            "claimed_at": "2026-06-22T00:00:00Z",
        },
        "timestamp": "2026-06-22T00:00:01Z",
        "starting_commit": "abc123",
        "ending_commit": "abc123",
        "attempts": 0,
        "commands": [],
        "changed_files": [],
        "validation_delta": [],
        "checker_result": "not-run",
        "stop_reason": "stage0-selected" if selected else "no-eligible-work",
        "next_actor": "human" if selected else "project-loop",
        "known_risks": [],
    }


def set_nested(data: dict, path: tuple[str, ...], value: object) -> None:
    target = data
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def load_select_module():
    if str(SELECT.parent) not in sys.path:
        sys.path.insert(0, str(SELECT.parent))
    spec = importlib.util.spec_from_file_location("project_loop_select_work", SELECT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def test_issue_and_pr_with_same_number_still_select_exactly_one(tmp_path: Path) -> None:
    candidates = {
        "issues": [
            {
                "type": "issue",
                "number": 7,
                "title": "Ready issue",
                "state": "open",
                "branch": "codex/7-issue",
                "labels": ["ready:project-loop"],
                "dependencies": [],
            }
        ],
        "pull_requests": [valid_candidate(number=7, title="Ready PR", head_branch="codex/7-pr")],
    }
    result = run_select(candidates, tmp_path)
    assert result.returncode == 0, result.stderr
    statuses = [entry["status"] for entry in receipt(tmp_path)["validation_delta"]]
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


def test_output_rejects_tracked_file_even_with_overbroad_run_root(tmp_path: Path) -> None:
    target = ROOT / "AGENTS.md"
    before = target.read_text(encoding="utf-8")
    result = run_select(
        {"pull_requests": []},
        tmp_path,
        config=config_text(tmp_path, run_root=ROOT),
        output_arg=target,
    )
    assert result.returncode != 0
    assert "runtime.run_root" in result.stderr
    assert target.read_text(encoding="utf-8") == before


def test_output_rejects_protected_path_even_with_overbroad_run_root(tmp_path: Path) -> None:
    target = ROOT / ".github" / "secrets" / f"stage0-protected-{tmp_path.name}.json"
    assert not target.exists()
    result = run_select(
        {"pull_requests": []},
        tmp_path,
        config=config_text(tmp_path, run_root=ROOT),
        output_arg=target,
    )
    assert result.returncode != 0
    assert "runtime.run_root" in result.stderr
    assert not target.exists()


def test_output_rejects_root_level_untracked_file_with_repo_run_root(tmp_path: Path) -> None:
    target = ROOT / f"stage0-root-output-{tmp_path.name}.json"
    assert not target.exists()
    result = run_select(
        {"pull_requests": []},
        tmp_path,
        config=config_text(tmp_path, run_root=ROOT),
        output_arg=target,
    )
    assert result.returncode != 0
    assert "runtime.run_root" in result.stderr
    assert not target.exists()


def test_default_in_repo_project_loop_run_root_is_allowed() -> None:
    module = load_select_module()
    config = module.load_config(ROOT / "project-loop.toml")
    output = module.safe_output_path(config, ".project-loop/runs/receipt.json")
    assert output == (ROOT / ".project-loop" / "runs" / "receipt.json").resolve(strict=False)


def test_output_rejects_traversal_outside_run_root(tmp_path: Path) -> None:
    outside = tmp_path / "escape.json"
    result = run_select({"pull_requests": []}, tmp_path, output_arg=f"{tmp_path.as_posix()}/runs/../escape.json")
    assert result.returncode != 0
    assert "runtime.run_root" in result.stderr
    assert not outside.exists()


def test_output_rejects_symlink_escape_from_run_root(tmp_path: Path) -> None:
    run_root = tmp_path / "runs"
    run_root.mkdir()
    outside = tmp_path / "outside.json"
    link = run_root / "receipt.json"
    link.symlink_to(outside)
    result = run_select({"pull_requests": []}, tmp_path, output_arg=link)
    assert result.returncode != 0
    assert "runtime.run_root" in result.stderr
    assert not outside.exists()


def test_malformed_configuration_fails_closed(tmp_path: Path) -> None:
    result = run_select(
        {"pull_requests": [valid_candidate()]},
        tmp_path,
        config="schema_version = 1\n",
    )
    assert result.returncode != 0
    assert "failed closed" in result.stderr
    assert not (tmp_path / "runs" / "receipt.json").exists()


def test_malformed_candidate_container_fails_closed(tmp_path: Path) -> None:
    result = run_select({"pull_requests": "invalid"}, tmp_path)
    assert result.returncode != 0
    assert "pull_requests must be a list" in result.stderr
    assert not (tmp_path / "runs" / "receipt.json").exists()


def test_git_head_fails_closed_when_head_cannot_be_resolved(monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_select_module()

    def fail_check_output(*_args: object, **_kwargs: object) -> str:
        raise subprocess.CalledProcessError(128, ["git", "rev-parse", "HEAD"])

    monkeypatch.setattr(module.subprocess, "check_output", fail_check_output)
    with pytest.raises(RuntimeError, match="cannot resolve git HEAD"):
        module.git_head()


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


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (("attempts",), 1, "attempts 0"),
        (("commands",), [{"command": "./init.sh", "exit_code": 0, "summary": "passed"}], "commands []"),
        (("changed_files",), ["AGENTS.md"], "changed_files []"),
        (("checker_result",), "pass", 'checker_result "not-run"'),
        (("ending_commit",), "def456", "ending_commit equal to starting_commit"),
        (("claim", "starting_commit"), "def456", "claim.starting_commit equal to starting_commit"),
        (("claim", "branch"), "codex/other", "claim.branch equal to work_item.branch"),
        (("work_item", "branch"), None, "work_item.branch"),
    ],
)
def test_stage0_selected_receipt_rejects_mutated_invariants(
    tmp_path: Path,
    path: tuple[str, ...],
    value: object,
    message: str,
) -> None:
    data = copy.deepcopy(stage0_receipt(selected=True))
    set_nested(data, path, value)
    result = validate_data(data, tmp_path)
    assert result.returncode != 0
    assert message in result.stdout


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (("attempts",), 1, "attempts 0"),
        (("commands",), [{"command": "./init.sh", "exit_code": 0, "summary": "passed"}], "commands []"),
        (("changed_files",), ["AGENTS.md"], "changed_files []"),
        (("checker_result",), "pass", 'checker_result "not-run"'),
        (("ending_commit",), "def456", "ending_commit equal to starting_commit"),
        (("claim", "starting_commit"), "def456", "claim.starting_commit equal to starting_commit"),
        (("claim", "branch"), "codex/noop", "claim.branch null"),
    ],
)
def test_stage0_noop_receipt_rejects_mutated_invariants(
    tmp_path: Path,
    path: tuple[str, ...],
    value: object,
    message: str,
) -> None:
    data = copy.deepcopy(stage0_receipt(selected=False))
    set_nested(data, path, value)
    result = validate_data(data, tmp_path)
    assert result.returncode != 0
    assert message in result.stdout


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
