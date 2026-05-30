from __future__ import annotations

from typing import Any, Dict, Iterable, Sequence


FAMILY_EVIDENCE_MARKERS = {
    "comparison": [
        "supported by",
        "grounded by",
        "contrast",
        "difference",
        "better supported",
        "decisive",
    ],
    "synthesis": [
        "supported by",
        "grounded by",
        "evidence",
        "merge",
        "integrate",
        "observed",
        "inferred",
    ],
    "procedure": [
        "checklist",
        "labeled",
        "field",
        "structured",
        "layout",
        "operator",
        "handoff",
    ],
}


def _markers_for_family(family: str) -> list[str]:
    return FAMILY_EVIDENCE_MARKERS.get(family, [])


def _markers_for_secondary(families: Sequence[str]) -> list[str]:
    markers: list[str] = []
    for family in families:
        markers.extend(FAMILY_EVIDENCE_MARKERS.get(family, []))
    seen = set()
    dedup = []
    for marker in markers:
        if marker not in seen:
            seen.add(marker)
            dedup.append(marker)
    return dedup


def verify_output(
    task_family: str,
    output_text: str,
    framing_candidates: Iterable[str] | None = None,
    task_contract: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    normalized = output_text.lower()
    schema_ok = isinstance(output_text, str) and len(output_text.strip()) > 0

    candidate_families = list(framing_candidates or [])
    primary_markers = _markers_for_family(task_family)
    secondary_markers = _markers_for_secondary([f for f in candidate_families if f != task_family])

    primary_hit = any(marker in normalized for marker in primary_markers) if primary_markers else len(output_text) > 25
    secondary_hit = any(marker in normalized for marker in secondary_markers) if secondary_markers else False

    required_properties = (task_contract or {}).get("required_properties", [])
    forbidden_shortcuts = (task_contract or {}).get("forbidden_shortcuts", [])

    property_hits = {prop: _property_check(prop, normalized) for prop in required_properties}
    required_ok = all(property_hits.values()) if property_hits else primary_hit

    shortcut_hits = {shortcut: _shortcut_check(shortcut, normalized) for shortcut in forbidden_shortcuts}
    shortcuts_ok = not any(shortcut_hits.values())

    if task_family == "unknown" and not required_properties:
        evidence_ok = len(output_text) > 25
    else:
        evidence_ok = required_ok and primary_hit

    rule_ok = True
    good_enough = schema_ok and evidence_ok and rule_ok and shortcuts_ok
    return {
        "schema_checks": {"passed": schema_ok},
        "evidence_checks": {
            "passed": evidence_ok,
            "primary_hit": primary_hit,
            "secondary_hit": secondary_hit,
            "framing_candidates_used": candidate_families,
        },
        "property_checks": property_hits,
        "shortcut_checks": shortcut_hits,
        "rule_checks": {"passed": rule_ok},
        "verification_summary": {
            "good_enough": good_enough,
            "task_family": task_family,
        },
    }


def _property_check(prop: str, normalized: str) -> bool:
    mapping = {
        "explicit comparison": any(k in normalized for k in ["contrast", "difference", "better", "safer", "stronger"]),
        "evidence-backed choice": any(k in normalized for k in ["supported by", "grounded by", "evidence"]),
        "handoff-usable structure": any(k in normalized for k in ["checklist", "field", "structured", "layout"]),
        "evidence-grounded conclusion": any(k in normalized for k in ["supported by", "grounded by", "evidence"]),
        "fact vs inference separation": any(k in normalized for k in ["observed", "inferred"]),
        "stable structured layout": any(k in normalized for k in ["checklist", "field", "structured", "layout"]),
    }
    return mapping.get(prop, True)


def _shortcut_check(shortcut: str, normalized: str) -> bool:
    if shortcut == "generic preference without evidence":
        return ("better" in normalized or "safer" in normalized) and not any(k in normalized for k in ["supported by", "grounded by", "evidence"])
    if shortcut == "summary without distinction":
        summary_like = any(k in normalized for k in ["summary", "answer", "conclusion"])
        evidence_structure = any(k in normalized for k in ["supported by", "grounded by", "observed", "inferred", "contrast", "difference"])
        return summary_like and not evidence_structure
    if shortcut == "structure without a decision":
        return any(k in normalized for k in ["checklist", "field", "structured"]) and not any(k in normalized for k in ["better", "safer", "stronger", "contrast", "difference"])
    if shortcut == "decision without structure":
        return any(k in normalized for k in ["better", "safer", "stronger"]) and not any(k in normalized for k in ["checklist", "field", "structured", "layout"])
    return False


def is_good_enough(verification_state: Dict[str, Any]) -> bool:
    return bool(verification_state.get("verification_summary", {}).get("good_enough", False))
