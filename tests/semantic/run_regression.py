#!/usr/bin/env python3
"""Deterministic regression checks for semantic layer outputs."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from backend.server import app  # type: ignore

ROOT = Path(__file__).resolve().parent
FIXTURE_DIR = ROOT / "fixtures"
EXPECTED_FILE = ROOT / "expected.json"


class RegressionFailure(Exception):
    pass


def load_expected() -> Dict[str, Dict[str, object]]:
    if not EXPECTED_FILE.exists():
        raise RegressionFailure(f"Missing expected file: {EXPECTED_FILE}")
    try:
        return json.loads(EXPECTED_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RegressionFailure(f"Failed to parse {EXPECTED_FILE}: {exc}") from exc


def collect_gate_status(module_payload: Dict[str, object]) -> Tuple[Dict[str, str], Dict[str, str]]:
    failures: Dict[str, str] = {}
    warnings: Dict[str, str] = {}
    gates = (module_payload or {}).get("gates", {})
    if isinstance(gates, dict):
        iterator: Iterable[Tuple[str, Dict[str, object]]] = gates.items()
    else:
        iterator = []
    for gate_id, gate_result in iterator:
        if not isinstance(gate_result, dict):
            continue
        status = (gate_result.get("status") or "").upper()
        message = str(gate_result.get("message") or "")
        if status == "FAIL":
            failures[gate_id] = message
        elif status == "WARNING":
            warnings[gate_id] = message
    return failures, warnings


def evaluate_case(case_id: str, config: Dict[str, object]) -> List[str]:
    modules = list(config.get("modules") or [])
    if not modules:
        return [f"{case_id}: no modules specified in expected.json"]

    fixture_path = FIXTURE_DIR / f"{case_id}.txt"
    if not fixture_path.exists():
        return [f"{case_id}: missing fixture {fixture_path}"]

    text = fixture_path.read_text(encoding="utf-8").strip()
    client = app.test_client()
    resp = client.post(
        "/api/validate-document",
        json={"text": text, "modules": modules},
    )
    if resp.status_code != 200:
        return [f"{case_id}: POST /api/validate-document returned {resp.status_code}"]

    payload = resp.get_json() or {}
    validation = payload.get("validation") or {}
    overall_risk = str(payload.get("risk") or validation.get("overall_risk") or "UNKNOWN").upper()

    issues: List[str] = []
    expected_risk = str(config.get("expected_risk") or "").upper()
    if expected_risk and overall_risk != expected_risk:
        issues.append(f"{case_id}: expected risk {expected_risk}, got {overall_risk}")

    all_failures: Dict[str, str] = {}
    all_warnings: Dict[str, str] = {}
    modules_payload = validation.get("modules") or {}
    if isinstance(modules_payload, dict):
        for module_id, module_payload in modules_payload.items():
            if not isinstance(module_payload, dict):
                continue
            fails, warns = collect_gate_status(module_payload)
            # Use composite key to avoid collisions across modules
            all_failures.update({f"{module_id}:{gate}": msg for gate, msg in fails.items()})
            all_warnings.update({f"{module_id}:{gate}": msg for gate, msg in warns.items()})

    def ensure_subset(label: str, expected: Iterable[str], actual: Dict[str, str]):
        for gate in expected:
            matches = [key for key in actual if key.endswith(f":{gate}")]
            if not matches:
                issues.append(f"{case_id}: expected {label} gate '{gate}' not found (actual {list(actual)})")

    ensure_subset("FAIL", config.get("must_fail", []), all_failures)
    ensure_subset("WARNING", config.get("must_warn", []), all_warnings)

    max_fail = config.get("max_fail")
    if isinstance(max_fail, int) and len(all_failures) > max_fail:
        issues.append(f"{case_id}: fail count {len(all_failures)} exceeds max_fail {max_fail}")

    max_warn = config.get("max_warn")
    if isinstance(max_warn, int) and len(all_warnings) > max_warn:
        issues.append(f"{case_id}: warning count {len(all_warnings)} exceeds max_warn {max_warn}")

    semantic = validation.get("semantic") or {}
    total_hits = int(semantic.get("total_hits") or 0)
    needs_review = int(semantic.get("needs_review") or 0)

    min_hits = config.get("min_semantic_hits")
    if isinstance(min_hits, int) and total_hits < min_hits:
        issues.append(f"{case_id}: semantic hits {total_hits} below minimum {min_hits}")

    max_hits = config.get("max_semantic_hits")
    if isinstance(max_hits, int) and total_hits > max_hits:
        issues.append(f"{case_id}: semantic hits {total_hits} exceed maximum {max_hits}")

    min_review = config.get("min_review_flags")
    if isinstance(min_review, int) and needs_review < min_review:
        issues.append(f"{case_id}: review flags {needs_review} below minimum {min_review}")

    max_review = config.get("max_review_flags")
    if isinstance(max_review, int) and needs_review > max_review:
        issues.append(f"{case_id}: review flags {needs_review} exceed maximum {max_review}")

    return issues


def main() -> int:
    try:
        expected = load_expected()
    except RegressionFailure as exc:
        print(f"[regression] {exc}")
        return 1

    failures: List[str] = []
    for case_id, config in expected.items():
        if not isinstance(config, dict):
            failures.append(f"{case_id}: config entry must be object")
            continue
        failures.extend(evaluate_case(case_id, config))

    if failures:
        print("Semantic regression failures detected:\n")
        for item in failures:
            print(f" - {item}")
        return 1

    print("Semantic regression passed for all fixtures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
