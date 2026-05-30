from __future__ import annotations

from typing import Any, Dict

from ...core.objects.task import TaskObject


def should_escalate(task: TaskObject, verification_state: Dict[str, Any], current_tier: str) -> Dict[str, Any]:
    good_enough = bool(verification_state.get("verification_summary", {}).get("good_enough", False))
    if good_enough:
        return {
            "escalate": False,
            "target_tier": None,
            "reason": "verification judged output good enough",
            "expected_value": 0.0,
            "blockers": [],
        }

    if current_tier == "tier_2":
        return {
            "escalate": False,
            "target_tier": None,
            "reason": "already at premium tier",
            "expected_value": 0.0,
            "blockers": ["premium_ceiling_reached"],
        }

    target = "tier_1" if current_tier == "tier_0" else "tier_2"
    reason = "failed verification and higher tier may improve answer quality"
    if task.criticality_level == "high":
        reason += "; task criticality increases escalation value"

    return {
        "escalate": True,
        "target_tier": target,
        "reason": reason,
        "expected_value": 0.5 if target == "tier_1" else 0.75,
        "blockers": [],
    }
