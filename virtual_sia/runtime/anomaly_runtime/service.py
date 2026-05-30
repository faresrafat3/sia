from __future__ import annotations

from typing import Any, Dict, List

from ...core.objects.anomaly import AnomalyCandidate


def extract_anomaly_candidates(task_result: dict) -> List[AnomalyCandidate]:
    task = task_result.get("task", {})
    blackboard = task_result.get("blackboard", {})
    verification = blackboard.get("verification_state", {})
    contradictions = blackboard.get("contradictions", []) or []
    task_family = task.get("task_family", "unknown")

    candidates: List[AnomalyCandidate] = []

    property_checks = verification.get("property_checks", {}) or {}
    shortcut_checks = verification.get("shortcut_checks", {}) or {}
    good_enough = bool(verification.get("verification_summary", {}).get("good_enough", False))

    # Candidate A: repeated contract failure signal
    if not good_enough and property_checks and not all(property_checks.values()):
        failed_props = [k for k, v in property_checks.items() if not v]
        candidates.append(
            AnomalyCandidate.create(
                task_family=task_family,
                source_type="property_gap",
                summary=f"Task failed required properties: {failed_props}",
                supporting_refs=failed_props,
                severity=0.6,
                recommended_action="consider concept or theory refinement around required-property failure",
            )
        )

    # Candidate B: shortcut-trigger anomaly
    if any(shortcut_checks.values()):
        hit_shortcuts = [k for k, v in shortcut_checks.items() if v]
        candidates.append(
            AnomalyCandidate.create(
                task_family=task_family,
                source_type="shortcut_pattern",
                summary=f"Forbidden shortcuts triggered: {hit_shortcuts}",
                supporting_refs=hit_shortcuts,
                severity=0.7,
                recommended_action="strengthen anti-shortcut concept leverage or evaluation pressure",
            )
        )

    # Candidate C: contradiction-driven anomaly candidates
    for contradiction in contradictions:
        ctype = contradiction.get("contradiction_type", "unknown")
        if ctype in {"sufficient_evidence_but_failure", "framing_overlap_failure", "framing_mismatch"}:
            candidates.append(
                AnomalyCandidate.create(
                    task_family=task_family,
                    source_type="contradiction_pattern",
                    summary=f"Contradiction-derived anomaly candidate: {ctype}",
                    supporting_refs=[contradiction.get("id", "")],
                    severity=contradiction.get("severity", 0.5),
                    recommended_action="track recurrence across tasks before promoting to anomaly object",
                )
            )

    return candidates
