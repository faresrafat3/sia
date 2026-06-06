"""
Ladder Ascent Engine — GENESIS
===============================
Core engine for detecting and executing phase transitions on the
Ladder of Abstraction.

The Key Insight: Phase transitions are NOT gradual. They are triggered
when epistemic entropy exceeds a critical threshold, forcing the system
to compress its current knowledge into a higher-level representation.

From physics analogy:
    - Ice → Water at 0°C  (phase transition at critical temp)
    - Level 2 → Level 4 when entropy > threshold (cognitive phase transition)

The transition criteria:
    Level 0→1: ≥1 trace with outcome
    Level 1→2: ≥3 episodes with recurring features
    Level 2→3: ≥3 patterns that suggest a reusable rule
    Level 3→4: Heuristic fails on ≥2 near-domain tasks → Concept formation triggered
    Level 4→5: Concept works across ≥3 domains without modification
    Level 5→6: ≥2 invariants connected by a shared prediction
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import IntEnum
from datetime import datetime
import math
import logging

logger = logging.getLogger(__name__)


class LadderLevel(IntEnum):
    """Levels on the Ladder of Abstraction."""
    OBSERVATION = 0
    EPISODE = 1
    PATTERN = 2
    HEURISTIC = 3
    CONCEPT = 4
    INVARIANT = 5
    THEORY = 6

    @property
    def label(self) -> str:
        labels = {
            0: "Observation",
            1: "Episode",
            2: "Pattern",
            3: "Heuristic",
            4: "Concept",
            5: "Invariant",
            6: "Theory",
        }
        return labels.get(self.value, "Unknown")

    @property
    def description(self) -> str:
        descriptions = {
            0: "Raw traces, no structure applied",
            1: "Grouped traces with outcome labels",
            2: "Recurring episodes identified",
            3: "Actionable rule extracted from patterns",
            4: "Named, scoped abstraction with counterexamples",
            5: "Stable regularity across multiple domains",
            6: "Network of invariants with testable predictions",
        }
        return descriptions.get(self.value, "")


@dataclass
class PhaseTransitionCriterion:
    """
    Criterion for transitioning between two levels.
    
    Each transition has:
    - minimum_evidence: Minimum number of evidence items needed
    - minimum_success_rate: Minimum success rate at current level
    - failure_trigger: Whether transition is triggered BY failure (crisis-induced)
    - entropy_threshold: Epistemic entropy above which transition is forced
    """
    from_level: LadderLevel
    to_level: LadderLevel
    minimum_evidence: int
    minimum_success_rate: float
    failure_trigger: bool = False
    entropy_threshold: float = 0.7
    minimum_domains: int = 1  # Minimum domains for cross-domain levels
    description: str = ""


# The canonical transition criteria for GENESIS
CANONICAL_TRANSITIONS: List[PhaseTransitionCriterion] = [
    PhaseTransitionCriterion(
        from_level=LadderLevel.OBSERVATION,
        to_level=LadderLevel.EPISODE,
        minimum_evidence=1,
        minimum_success_rate=0.0,
        entropy_threshold=0.3,
        description="Any trace with outcome → Episode grouping"
    ),
    PhaseTransitionCriterion(
        from_level=LadderLevel.EPISODE,
        to_level=LadderLevel.PATTERN,
        minimum_evidence=3,
        minimum_success_rate=0.0,
        entropy_threshold=0.5,
        description="≥3 episodes with recurring features → Pattern"
    ),
    PhaseTransitionCriterion(
        from_level=LadderLevel.PATTERN,
        to_level=LadderLevel.HEURISTIC,
        minimum_evidence=3,
        minimum_success_rate=0.5,
        entropy_threshold=0.6,
        description="≥3 patterns → Heuristic rule"
    ),
    PhaseTransitionCriterion(
        from_level=LadderLevel.HEURISTIC,
        to_level=LadderLevel.CONCEPT,
        minimum_evidence=2,
        minimum_success_rate=0.0,
        failure_trigger=True,
        entropy_threshold=0.7,
        description="Heuristic fails on ≥2 near-domain tasks → Concept formation (crisis-induced)"
    ),
    PhaseTransitionCriterion(
        from_level=LadderLevel.CONCEPT,
        to_level=LadderLevel.INVARIANT,
        minimum_evidence=5,
        minimum_success_rate=0.6,
        minimum_domains=3,
        entropy_threshold=0.8,
        description="Concept stable across ≥3 domains → Invariant"
    ),
    PhaseTransitionCriterion(
        from_level=LadderLevel.INVARIANT,
        to_level=LadderLevel.THEORY,
        minimum_evidence=2,
        minimum_success_rate=0.5,
        minimum_domains=2,
        entropy_threshold=0.85,
        description="≥2 invariants connected by shared prediction → Theory"
    ),
]


@dataclass
class EpistemicEntropy:
    """
    Measurement of disorder in the epistemic state.
    
    High entropy = lots of unorganized evidence, many contradictions,
    unclear patterns. The system is "confused."
    
    Low entropy = well-organized knowledge, clear patterns,
    consistent predictions. The system is "stable."
    
    Phase transitions happen when entropy crosses a threshold,
    forcing reorganization (compression into higher abstraction).
    """
    level: LadderLevel
    evidence_count: int
    success_count: int
    failure_count: int
    contradiction_count: int
    domain_count: int
    unique_pattern_count: int
    
    def compute(self) -> float:
        """
        Compute epistemic entropy on [0, 1].
        
        H = H_evidence + H_outcome + H_contradiction + H_complexity
        
        Where:
        - H_evidence: entropy from unorganized evidence
        - H_outcome: entropy from mixed success/failure outcomes
        - H_contradiction: entropy from unresolved contradictions
        - H_complexity: entropy from high domain/pattern count
        """
        # Evidence entropy: more evidence without organization = higher entropy
        if self.evidence_count <= 0:
            return 0.0
        
        evidence_entropy = min(1.0, self.evidence_count / 20.0)
        
        # Outcome entropy: balanced success/failure = maximum uncertainty
        total = self.success_count + self.failure_count
        if total > 0:
            p_success = self.success_count / total
            p_failure = self.failure_count / total
            # Binary entropy: H = -p*log(p) - (1-p)*log(1-p)
            outcome_entropy = 0.0
            if p_success > 0:
                outcome_entropy -= p_success * math.log2(p_success + 1e-9)
            if p_failure > 0:
                outcome_entropy -= p_failure * math.log2(p_failure + 1e-9)
            outcome_entropy /= 1.0  # Normalize to [0, 1] (max is 1.0 for 50/50)
        else:
            outcome_entropy = 0.0
        
        # Contradiction entropy: more contradictions = more pressure
        contradiction_entropy = min(1.0, self.contradiction_count / 5.0)
        
        # Complexity entropy: many domains/patterns without organization
        complexity_entropy = min(1.0, (self.domain_count + self.unique_pattern_count) / 10.0)
        
        # Weighted combination
        weights = {
            LadderLevel.OBSERVATION: (0.3, 0.2, 0.1, 0.4),
            LadderLevel.EPISODE: (0.25, 0.3, 0.15, 0.3),
            LadderLevel.PATTERN: (0.2, 0.25, 0.25, 0.3),
            LadderLevel.HEURISTIC: (0.15, 0.2, 0.35, 0.3),
            LadderLevel.CONCEPT: (0.1, 0.15, 0.4, 0.35),
            LadderLevel.INVARIANT: (0.1, 0.1, 0.4, 0.4),
            LadderLevel.THEORY: (0.1, 0.1, 0.3, 0.5),
        }
        w = weights.get(self.level, (0.25, 0.25, 0.25, 0.25))
        
        total_entropy = (
            w[0] * evidence_entropy +
            w[1] * outcome_entropy +
            w[2] * contradiction_entropy +
            w[3] * complexity_entropy
        )
        
        return min(1.0, total_entropy)


@dataclass
class AbstractionForgettingTrigger:
    """
    Determines what to "forget" when climbing the ladder.
    
    Key principle from Productive Forgetting Theory:
    When ascending from Level N to Level N+1, the details of Level N
    should be compressed, not retained in full. This prevents context
    bloat (Theory-10 interaction).
    
    What gets forgotten:
    - Level 0→1: Raw trace details (keep outcome only)
    - Level 1→2: Individual episode details (keep pattern summary)
    - Level 2→3: Episode references (keep heuristic rule)
    - Level 3→4: Heuristic application details (keep concept scope)
    - Level 4→5: Domain-specific examples (keep invariant statement)
    - Level 5→6: Individual invariants (keep theory network)
    """
    from_level: LadderLevel
    to_level: LadderLevel
    
    def get_forgetting_policy(self) -> Dict[str, Any]:
        """Get what should be forgotten/compressed at this transition."""
        policies = {
            (LadderLevel.OBSERVATION, LadderLevel.EPISODE): {
                "forget": ["raw_trace_details", "timing_data"],
                "compress": ["trace_content → outcome_label"],
                "retain": ["outcome", "task_id", "timestamp"],
                "retention_ratio": 0.3,  # Keep 30% of detail
            },
            (LadderLevel.EPISODE, LadderLevel.PATTERN): {
                "forget": ["individual_episode_content"],
                "compress": ["episode_details → pattern_summary"],
                "retain": ["pattern_features", "frequency", "success_rate"],
                "retention_ratio": 0.2,
            },
            (LadderLevel.PATTERN, LadderLevel.HEURISTIC): {
                "forget": ["pattern_occurrence_details"],
                "compress": ["patterns → rule_statement"],
                "retain": ["rule", "applicable_families", "confidence"],
                "retention_ratio": 0.15,
            },
            (LadderLevel.HEURISTIC, LadderLevel.CONCEPT): {
                "forget": ["heuristic_application_cases"],
                "compress": ["heuristic → concept_definition"],
                "retain": ["concept_name", "scope", "counterexamples", "prediction"],
                "retention_ratio": 0.1,
            },
            (LadderLevel.CONCEPT, LadderLevel.INVARIANT): {
                "forget": ["domain_specific_examples"],
                "compress": ["concept_applications → invariant_statement"],
                "retain": ["invariant", "domains", "stability_score"],
                "retention_ratio": 0.1,
            },
            (LadderLevel.INVARIANT, LadderLevel.THEORY): {
                "forget": ["individual_invariant_proofs"],
                "compress": ["invariants → theory_network"],
                "retain": ["theory", "predictions", "falsification_conditions"],
                "retention_ratio": 0.1,
            },
        }
        return policies.get(
            (self.from_level, self.to_level),
            {"forget": [], "compress": [], "retain": ["all"], "retention_ratio": 1.0}
        )


@dataclass
class LadderState:
    """
    Current state on the Ladder of Abstraction for a given knowledge area.
    """
    area_id: str  # e.g., task_family, domain, or concept_id
    current_level: LadderLevel = LadderLevel.OBSERVATION
    last_transition_at: Optional[datetime] = None
    transition_count: int = 0
    
    # Evidence tracking at each level
    evidence_at_level: Dict[int, int] = field(default_factory=dict)
    successes_at_level: Dict[int, int] = field(default_factory=dict)
    failures_at_level: Dict[int, int] = field(default_factory=dict)
    contradictions_at_level: Dict[int, int] = field(default_factory=dict)
    domains_at_level: Dict[int, Set[str]] = field(default_factory=dict)
    patterns_at_level: Dict[int, int] = field(default_factory=dict)
    
    # Entropy history
    entropy_history: List[Tuple[datetime, float]] = field(default_factory=list)
    
    def record_evidence(
        self,
        success: bool,
        domain: str = "default",
        contradiction: bool = False,
        pattern_count: int = 0,
    ) -> None:
        """Record new evidence at the current level."""
        level = int(self.current_level)
        self.evidence_at_level[level] = self.evidence_at_level.get(level, 0) + 1
        if success:
            self.successes_at_level[level] = self.successes_at_level.get(level, 0) + 1
        else:
            self.failures_at_level[level] = self.failures_at_level.get(level, 0) + 1
        if contradiction:
            self.contradictions_at_level[level] = self.contradictions_at_level.get(level, 0) + 1
        if level not in self.domains_at_level:
            self.domains_at_level[level] = set()
        self.domains_at_level[level].add(domain)
        self.patterns_at_level[level] = self.patterns_at_level.get(level, 0) + pattern_count
    
    def compute_current_entropy(self) -> float:
        """Compute current epistemic entropy."""
        level = int(self.current_level)
        entropy = EpistemicEntropy(
            level=self.current_level,
            evidence_count=self.evidence_at_level.get(level, 0),
            success_count=self.successes_at_level.get(level, 0),
            failure_count=self.failures_at_level.get(level, 0),
            contradiction_count=self.contradictions_at_level.get(level, 0),
            domain_count=len(self.domains_at_level.get(level, set())),
            unique_pattern_count=self.patterns_at_level.get(level, 0),
        )
        value = entropy.compute()
        self.entropy_history.append((datetime.now(), value))
        return value


class LadderAscentEngine:
    """
    Engine for detecting when a phase transition should occur
    and executing the transition with proper abstraction forgetting.
    
    Usage:
        engine = LadderAscentEngine()
        state = engine.create_state("comparison_tasks")
        
        # Record evidence from task execution
        state.record_evidence(success=True, domain="physics")
        state.record_evidence(success=False, domain="chemistry")
        
        # Check if transition is warranted
        result = engine.check_transition(state)
        if result.should_transition:
            engine.execute_transition(state, result)
    """
    
    def __init__(
        self,
        transitions: Optional[List[PhaseTransitionCriterion]] = None,
        custom_thresholds: Optional[Dict[int, float]] = None,
    ):
        self.transitions = transitions or CANONICAL_TRANSITIONS
        self.custom_thresholds = custom_thresholds or {}
        self._states: Dict[str, LadderState] = {}
        self._transition_log: List[Dict[str, Any]] = []
    
    def create_state(self, area_id: str) -> LadderState:
        """Create a new ladder state for a knowledge area."""
        state = LadderState(area_id=area_id)
        self._states[area_id] = state
        return state
    
    def get_state(self, area_id: str) -> Optional[LadderState]:
        """Get existing state for a knowledge area."""
        return self._states.get(area_id)
    
    def get_or_create_state(self, area_id: str) -> LadderState:
        """Get or create state."""
        return self._states.get(area_id) or self.create_state(area_id)
    
    def check_transition(self, state: LadderState) -> 'TransitionResult':
        """
        Check whether a phase transition is warranted for this state.
        
        A transition is warranted when:
        1. Evidence count meets minimum
        2. Success rate meets minimum (or failure trigger is active)
        3. Epistemic entropy exceeds threshold
        4. Domain diversity meets minimum (for higher levels)
        """
        current_level = state.current_level
        
        # Find applicable transition
        transition = None
        for t in self.transitions:
            if t.from_level == current_level:
                transition = t
                break
        
        if transition is None:
            return TransitionResult(
                should_transition=False,
                reason=f"No transition defined from level {current_level.label}",
                from_level=current_level,
                to_level=current_level,
                entropy=0.0,
                entropy_threshold=1.0,
                evidence_met=False,
                success_rate_met=False,
                domain_met=False,
            )
        
        level = int(current_level)
        
        # Compute current entropy
        entropy = state.compute_current_entropy()
        
        # Check evidence count
        evidence_count = state.evidence_at_level.get(level, 0)
        evidence_met = evidence_count >= transition.minimum_evidence
        
        # Check success rate
        successes = state.successes_at_level.get(level, 0)
        failures = state.failures_at_level.get(level, 0)
        total = successes + failures
        success_rate = successes / max(1, total)
        
        if transition.failure_trigger:
            # For crisis-induced transitions, high FAILURE rate triggers
            success_rate_met = failures >= transition.minimum_evidence
        else:
            success_rate_met = success_rate >= transition.minimum_success_rate
        
        # Check domain diversity
        domains = state.domains_at_level.get(level, set())
        domain_met = len(domains) >= transition.minimum_domains
        
        # Check entropy threshold (allow custom overrides)
        threshold = self.custom_thresholds.get(
            int(current_level), transition.entropy_threshold
        )
        entropy_met = entropy >= threshold
        
        # Determine if transition should happen
        # All criteria must be met (with flexibility)
        if transition.failure_trigger:
            # Crisis transitions: failure + entropy sufficient
            should_transition = evidence_met and success_rate_met and (entropy_met or failures >= transition.minimum_evidence * 2)
        else:
            # Normal transitions: evidence + success_rate + entropy
            should_transition = evidence_met and success_rate_met and entropy_met and domain_met
        
        reason_parts = []
        if should_transition:
            reason_parts.append(f"All criteria met for {current_level.label} → {transition.to_level.label}")
        else:
            if not evidence_met:
                reason_parts.append(f"Need ≥{transition.minimum_evidence} evidence, have {evidence_count}")
            if not success_rate_met:
                if transition.failure_trigger:
                    reason_parts.append(f"Need ≥{transition.minimum_evidence} failures, have {failures}")
                else:
                    reason_parts.append(f"Need ≥{transition.minimum_success_rate:.0%} success rate, have {success_rate:.1%}")
            if not entropy_met:
                reason_parts.append(f"Need entropy ≥{threshold:.2f}, have {entropy:.2f}")
            if not domain_met:
                reason_parts.append(f"Need ≥{transition.minimum_domains} domains, have {len(domains)}")
        
        return TransitionResult(
            should_transition=should_transition,
            reason="; ".join(reason_parts),
            from_level=current_level,
            to_level=transition.to_level if should_transition else current_level,
            entropy=entropy,
            entropy_threshold=threshold,
            evidence_met=evidence_met,
            success_rate_met=success_rate_met,
            domain_met=domain_met,
            transition=transition,
        )
    
    def execute_transition(
        self,
        state: LadderState,
        result: 'TransitionResult',
    ) -> 'TransitionExecution':
        """
        Execute a phase transition with abstraction forgetting.
        """
        if not result.should_transition:
            return TransitionExecution(
                state=state,
                executed=False,
                reason="Transition not warranted",
                forgetting_policy={},
            )
        
        from_level = state.current_level
        to_level = result.to_level
        
        # Get forgetting policy
        trigger = AbstractionForgettingTrigger(from_level, to_level)
        forgetting_policy = trigger.get_forgetting_policy()
        
        # Execute the transition
        old_level = state.current_level
        state.current_level = to_level
        state.last_transition_at = datetime.now()
        state.transition_count += 1
        
        # Apply forgetting: reset evidence counters for new level
        # (old level data is preserved in history but not counted for new level)
        
        # Log the transition
        log_entry = {
            "area_id": state.area_id,
            "from_level": old_level.label,
            "to_level": to_level.label,
            "entropy_at_transition": result.entropy,
            "evidence_at_transition": state.evidence_at_level.get(int(old_level), 0),
            "forgetting_retention_ratio": forgetting_policy.get("retention_ratio", 1.0),
            "timestamp": datetime.now().isoformat(),
        }
        self._transition_log.append(log_entry)
        
        logger.info(
            f"Ladder transition: {state.area_id} "
            f"{old_level.label} → {to_level.label} "
            f"(entropy={result.entropy:.2f})"
        )
        
        return TransitionExecution(
            state=state,
            executed=True,
            reason=result.reason,
            forgetting_policy=forgetting_policy,
            from_level=old_level,
            to_level=to_level,
        )
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get overview of all ladder states."""
        overview = {}
        for area_id, state in self._states.items():
            entropy = state.compute_current_entropy()
            overview[area_id] = {
                "current_level": state.current_level.label,
                "current_level_int": int(state.current_level),
                "transition_count": state.transition_count,
                "entropy": round(entropy, 3),
                "total_evidence": sum(state.evidence_at_level.values()),
            }
        return overview
    
    def get_transition_log(self) -> List[Dict[str, Any]]:
        """Get the full transition log."""
        return list(self._transition_log)


@dataclass
class TransitionResult:
    """Result of checking whether a transition should happen."""
    should_transition: bool
    reason: str
    from_level: LadderLevel
    to_level: LadderLevel
    entropy: float
    entropy_threshold: float
    evidence_met: bool
    success_rate_met: bool
    domain_met: bool
    transition: Optional[PhaseTransitionCriterion] = None


@dataclass
class TransitionExecution:
    """Result of executing a transition."""
    state: LadderState
    executed: bool
    reason: str
    forgetting_policy: Dict[str, Any]
    from_level: LadderLevel = LadderLevel.OBSERVATION
    to_level: LadderLevel = LadderLevel.OBSERVATION


# Singleton
_engine: Optional[LadderAscentEngine] = None


def get_ladder_engine() -> LadderAscentEngine:
    """Get or create the default ladder ascent engine instance.

    NOTE: Prefer direct LadderAscentEngine() construction for test isolation.
    This function exists for backward compatibility.
    """
    global _engine
    if _engine is None:
        _engine = LadderAscentEngine()
    return _engine


def reset_ladder_engine() -> None:
    """Reset the singleton ladder engine. Use in test teardown."""
    global _engine
    _engine = None


def create_ladder_engine(
    transitions: Optional[List[PhaseTransitionCriterion]] = None,
    custom_thresholds: Optional[Dict[int, float]] = None,
) -> LadderAscentEngine:
    """Factory function for creating fresh LadderAscentEngine instances.

    Replaces singleton pattern. Use for new code and tests.
    """
    return LadderAscentEngine(
        transitions=transitions,
        custom_thresholds=custom_thresholds,
    )
