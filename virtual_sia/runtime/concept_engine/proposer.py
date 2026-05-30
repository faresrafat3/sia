from __future__ import annotations

from ...core.objects.concept import ConceptCandidate, ConceptCard
from ...core.objects.memory import MemoryUnit
from .registry import InMemoryConceptRegistry


def _family_contrast_candidate(family: str, successes: list[MemoryUnit], failures: list[MemoryUnit]) -> ConceptCandidate:
    if family == "comparison":
        name = "Evidence Sufficiency Contrast"
        definition = "Comparison tasks often fail when the answer states differences without enough supporting evidence anchors."
    elif family == "synthesis":
        name = "Ungrounded Synthesis Risk"
        definition = "Synthesis tasks often fail when multiple snippets are merged without explicit grounding of claims to evidence fragments."
    elif family == "procedure":
        name = "Stable Procedure Reuse Opportunity"
        definition = "Some procedure tasks repeatedly benefit from reusing a consistent workflow instead of reasoning from scratch."
    else:
        name = f"{family.title()} Pattern Contrast"
        definition = f"The {family} family shows a recurring contrast between successful and failed episodes worth abstracting."

    candidate = ConceptCandidate.create(name, definition)
    candidate.contrastive_basis = [
        f"{len(successes)} successful episodes",
        f"{len(failures)} failed episodes",
    ]
    candidate.supporting_episode_refs = [m.id for m in successes[:3] + failures[:3]]
    candidate.candidate_scope.task_families = [family]
    candidate.candidate_scope.positive_conditions = [f"task_family == {family}"]
    candidate.candidate_scope.negative_conditions = ["insufficient supporting examples outside family"]
    candidate.candidate_value = 0.6
    candidate.recommendation = "validate_as_concept"
    return candidate


def _property_gap_candidate(family: str, prop: str, successes: list[MemoryUnit], failures: list[MemoryUnit]) -> ConceptCandidate:
    name = f"{family.title()} {prop.title()} Gap"
    definition = f"{family.title()} tasks become unreliable when the required property `{prop}` is not satisfied consistently."
    candidate = ConceptCandidate.create(name, definition)
    candidate.contrastive_basis = [
        f"property={prop}",
        f"{len(successes)} passing episodes",
        f"{len(failures)} failing episodes",
    ]
    candidate.supporting_episode_refs = [m.id for m in successes[:2] + failures[:4]]
    candidate.candidate_scope.task_families = [family]
    candidate.candidate_scope.positive_conditions = [f"task_family == {family}", f"requires_property == {prop}"]
    candidate.candidate_scope.negative_conditions = ["do not over-apply outside matching evaluation contract"]
    candidate.candidate_value = 0.7 if len(failures) >= 2 else 0.55
    candidate.recommendation = "validate_as_concept"
    return candidate


def _shortcut_gap_candidate(family: str, shortcut: str, successes: list[MemoryUnit], failures: list[MemoryUnit]) -> ConceptCandidate:
    name = f"{family.title()} {shortcut.title()} Avoidance"
    definition = f"{family.title()} tasks frequently fail when the shortcut `{shortcut}` is triggered; successful handling must explicitly avoid this pattern."
    candidate = ConceptCandidate.create(name, definition)
    candidate.contrastive_basis = [
        f"shortcut={shortcut}",
        f"{len(successes)} shortcut-free episodes",
        f"{len(failures)} shortcut-violating episodes",
    ]
    candidate.supporting_episode_refs = [m.id for m in successes[:2] + failures[:4]]
    candidate.candidate_scope.task_families = [family]
    candidate.candidate_scope.positive_conditions = [f"task_family == {family}", f"avoid_shortcut == {shortcut}"]
    candidate.candidate_scope.negative_conditions = ["may be irrelevant when shortcut is structurally impossible"]
    candidate.candidate_value = 0.75 if len(failures) >= 2 else 0.55
    candidate.recommendation = "validate_as_concept"
    return candidate


def propose_concepts_from_groups(groups: list[dict]) -> list[ConceptCandidate]:
    candidates: list[ConceptCandidate] = []
    for group in groups:
        family = group["family"]
        successes = group["successes"]
        failures = group["failures"]
        group_type = group["group_type"]
        prop = group.get("property_name")
        shortcut = group.get("shortcut_name")

        if group_type == "family_contrast":
            candidate = _family_contrast_candidate(family, successes, failures)
        elif group_type == "property_gap" and prop is not None:
            candidate = _property_gap_candidate(family, prop, successes, failures)
        elif group_type == "shortcut_gap" and shortcut is not None:
            candidate = _shortcut_gap_candidate(family, shortcut, successes, failures)
        else:
            continue
        candidates.append(candidate)
    return candidates


def _operational_meaning_for_candidate(candidate: ConceptCandidate) -> str:
    name = candidate.proposed_name.lower()
    if "evidence sufficiency contrast" in name:
        return "When comparing options, force an explicit evidence-backed contrast instead of a generic preference."
    if "ungrounded synthesis risk" in name:
        return "When synthesizing fragments, anchor every major conclusion to observed evidence and avoid unsupported merging."
    if "stable procedure reuse opportunity" in name:
        return "Prefer a stable checklist or field-oriented workflow instead of regenerating the structure from scratch."
    if "gap" in name and "comparison" in name:
        return "Make the comparison criterion explicit and tie the preferred option to evidence, not just wording."
    if "gap" in name and "synthesis" in name:
        return "Separate observations from inference and preserve at least one explicit evidence hook for the conclusion."
    if "avoidance" in name and "summary without distinction" in name:
        return "Do not collapse the answer into a generic summary; preserve the decisive distinction and the evidence behind it."
    if "avoidance" in name and "generic preference without evidence" in name:
        return "Avoid choosing an option without stating why the evidence makes it stronger or safer."
    return "Use this concept to influence retrieval, verification emphasis, or procedural reuse decisions."


def promote_candidate(registry: InMemoryConceptRegistry, candidate_id: str) -> ConceptCard | None:
    candidate = registry.get_candidate(candidate_id)
    if not candidate:
        return None
    concept = ConceptCard.from_candidate(
        candidate,
        operational_meaning=_operational_meaning_for_candidate(candidate),
    )
    concept.activation_conditions = candidate.candidate_scope.positive_conditions.copy()
    concept.confidence_score = 0.6
    concept.transfer_score = 0.3
    registry.add_concept(concept)
    return concept
