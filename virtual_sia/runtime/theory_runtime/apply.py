from __future__ import annotations

from typing import Iterable, List

from ...core.objects.theory import LocalTheoryObject


def select_applicable_theories(task_family: str, theories: Iterable[LocalTheoryObject], limit: int = 1) -> List[LocalTheoryObject]:
    selected: List[LocalTheoryObject] = []
    for theory in theories:
        if task_family in theory.scope.task_families:
            selected.append(theory)
        if len(selected) >= limit:
            break
    return selected


def build_theory_hints(theories: Iterable[LocalTheoryObject]) -> list[str]:
    hints: list[str] = []
    for theory in theories:
        mechanism = theory.mechanism_claims[0] if theory.mechanism_claims else ""
        prescription = theory.prescriptive_implications[0] if theory.prescriptive_implications else ""
        hints.append(f"{theory.name}: {mechanism} {prescription}".strip())
    return hints
