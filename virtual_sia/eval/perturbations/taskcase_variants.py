from __future__ import annotations

from copy import deepcopy
from typing import Iterable, List

from ...core.objects.base import make_id
from ...core.objects.task_case import TaskCase


def clone_case(case: TaskCase) -> TaskCase:
    new_case = deepcopy(case)
    new_case.id = make_id("task_case")
    new_case.meta = dict(new_case.meta or {})
    new_case.meta["source_case_id"] = case.meta.get("source_case_id", case.id) if case.meta else case.id
    return new_case


def lexical_soften(case: TaskCase) -> TaskCase:
    new_case = clone_case(case)
    replacements = {
        "compare": "determine",
        "difference": "distinction",
        "checklist": "operator-ready note",
        "fields": "details",
        "summary": "note",
    }
    text = new_case.prompt_text
    for old, new in replacements.items():
        text = text.replace(old, new).replace(old.title(), new.title())
    new_case.prompt_text = text
    new_case.tags.append("perturb_lexical_soften")
    new_case.meta["perturbation_type"] = "lexical_soften"
    return new_case


def inject_brevity_lure(case: TaskCase) -> TaskCase:
    new_case = clone_case(case)
    new_case.prompt_text += " Keep the final answer extremely brief."
    if new_case.expected_primary_family == "comparison":
        if "generic preference without evidence" not in new_case.forbidden_shortcuts:
            new_case.forbidden_shortcuts.append("generic preference without evidence")
    if new_case.expected_primary_family == "synthesis":
        if "summary without distinction" not in new_case.forbidden_shortcuts:
            new_case.forbidden_shortcuts.append("summary without distinction")
    new_case.tags.append("perturb_brevity_lure")
    new_case.meta["perturbation_type"] = "brevity_lure"
    return new_case


def inject_light_overlap(case: TaskCase, secondary_family: str) -> TaskCase:
    new_case = clone_case(case)
    if secondary_family not in new_case.expected_secondary_families:
        new_case.expected_secondary_families.append(secondary_family)
    new_case.family_overlap_type = f"light_{new_case.expected_primary_family}_{secondary_family}_overlap"
    if secondary_family == "procedure":
        new_case.prompt_text += " Present the result in a handoff-ready form."
    elif secondary_family == "comparison":
        new_case.prompt_text += " Make the decisive contrast clear."
    elif secondary_family == "synthesis":
        new_case.prompt_text += " Keep the answer as one coherent grounded note."
    new_case.tags.append(f"perturb_overlap_{secondary_family}")
    new_case.meta["perturbation_type"] = f"overlap_{secondary_family}"
    return new_case


def tighten_contract(case: TaskCase, extra_property: str | None = None, extra_shortcut: str | None = None) -> TaskCase:
    new_case = clone_case(case)
    if extra_property and extra_property not in new_case.required_properties:
        new_case.required_properties.append(extra_property)
    if extra_shortcut and extra_shortcut not in new_case.forbidden_shortcuts:
        new_case.forbidden_shortcuts.append(extra_shortcut)
    new_case.tags.append("perturb_tight_contract")
    new_case.meta["perturbation_type"] = "tight_contract"
    return new_case


def build_curriculum_levels(case: TaskCase) -> list[TaskCase]:
    base = clone_case(case)
    base.tags.append("curriculum_level_0")
    base.meta["curriculum_level"] = 0
    levels = [base]

    l1 = lexical_soften(case)
    l1.tags.append("curriculum_level_1")
    l1.meta["curriculum_level"] = 1
    levels.append(l1)

    l2 = inject_brevity_lure(l1)
    l2.tags.append("curriculum_level_2")
    l2.meta["curriculum_level"] = 2
    levels.append(l2)

    overlap_target = "procedure" if case.expected_primary_family != "procedure" else "synthesis"
    l3 = inject_light_overlap(l2, overlap_target)
    l3 = tighten_contract(
        l3,
        extra_property="evidence-grounded conclusion" if case.expected_primary_family != "procedure" else "stable structured layout",
    )
    l3.tags.append("curriculum_level_3")
    l3.meta["curriculum_level"] = 3
    levels.append(l3)

    return levels


def build_curriculum_from_cases(cases: Iterable[TaskCase], limit_per_case: int = 4) -> List[TaskCase]:
    all_cases: List[TaskCase] = []
    for case in cases:
        levels = build_curriculum_levels(case)
        all_cases.extend(levels[:limit_per_case])
    return all_cases
