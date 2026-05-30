from __future__ import annotations

from ...core.objects.blackboard import BlackboardMemoryPack, BlackboardObject
from ...core.objects.decision import TierDecisionObject
from ...core.objects.task import TaskObject


def choose_tier(task: TaskObject, blackboard: BlackboardObject, memory_pack: BlackboardMemoryPack) -> TierDecisionObject:
    reason_parts: list[str] = []
    chosen_tier = "tier_1"
    ambiguity = bool((task.meta or {}).get("family_ambiguity", False))

    if task.criticality_level == "high" and task.difficulty_estimate in {"medium", "high"}:
        chosen_tier = "tier_2"
        reason_parts.append("high criticality with non-trivial difficulty")
    elif ambiguity and not memory_pack.concept_refs:
        chosen_tier = "tier_1"
        reason_parts.append("framing ambiguity present; stay in balanced tier pending more evidence")
    elif memory_pack.concept_refs and task.difficulty_estimate != "high":
        chosen_tier = "tier_1"
        reason_parts.append("concept support available, no premium escalation needed initially")
    elif task.difficulty_estimate == "low" and task.task_family in {"procedure", "unknown"} and not ambiguity:
        chosen_tier = "tier_0"
        reason_parts.append("low difficulty and low ambiguity task can start cheap")
    elif memory_pack.memory_noise_risk is not None and memory_pack.memory_noise_risk > 0.5:
        chosen_tier = "tier_1"
        reason_parts.append("avoid cheap path due to memory noise risk")
    else:
        reason_parts.append("default balanced worker tier")

    decision = TierDecisionObject.create(
        task_ref=task.id,
        chosen_tier=chosen_tier,
        reason="; ".join(reason_parts),
    )
    decision.expected_immediate_gain = 0.4 if chosen_tier == "tier_0" else 0.7 if chosen_tier == "tier_1" else 0.9
    decision.expected_reuse_gain = 0.2 if memory_pack.concept_refs else 0.1 if chosen_tier == "tier_0" else 0.25 if chosen_tier == "tier_1" else 0.45
    decision.expected_cost = 0.0 if chosen_tier == "tier_0" else 0.001 if chosen_tier == "tier_1" else 0.01
    decision.expected_delay_penalty = 0.05 if chosen_tier == "tier_2" else (0.02 if ambiguity else 0.0)
    decision.confidence_in_decision = 0.5 if ambiguity else 0.6
    decision.fallback_option = "tier_1" if chosen_tier == "tier_0" else "tier_2"
    return decision
