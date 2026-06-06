"""
Ladder Ascent Module — GENESIS
===============================
Implements the mechanism for climbing the Ladder of Abstraction.

Ladder Levels (from GENESIS_Concept_Formation_Theory_AR.md §4):
    Level 0: Observation    — Raw traces, no structure
    Level 1: Episode        — Grouped traces with outcome
    Level 2: Pattern        — Recurring episodes
    Level 3: Heuristic      — Actionable rule from patterns
    Level 4: Concept        — Named, scoped, with counterexamples
    Level 5: Invariant      — Stable across domains
    Level 6: Theory         — Network of concepts + invariants + claims

This module answers: WHEN should the system climb? HOW does it know?
It implements:
    1. Current level detection
    2. Phase transition criteria
    3. Epistemic entropy measurement
    4. Abstraction forgetting trigger (compression on ascent)
"""

from .engine import (
    LadderLevel,
    LadderState,
    LadderAscentEngine,
    PhaseTransitionCriterion,
    EpistemicEntropy,
    AbstractionForgettingTrigger,
    get_ladder_engine,
)

__all__ = [
    "LadderLevel",
    "LadderState",
    "LadderAscentEngine",
    "PhaseTransitionCriterion",
    "EpistemicEntropy",
    "AbstractionForgettingTrigger",
    "get_ladder_engine",
]
