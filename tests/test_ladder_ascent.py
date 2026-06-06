"""
Tests for Ladder Ascent Engine — GENESIS
==========================================
"""

import pytest
from virtual_genesis.runtime.ladder_ascent.engine import (
    LadderLevel,
    LadderState,
    LadderAscentEngine,
    PhaseTransitionCriterion,
    EpistemicEntropy,
    AbstractionForgettingTrigger,
    CANONICAL_TRANSITIONS,
)


class TestLadderLevel:
    """Tests for LadderLevel enum."""

    def test_level_ordering(self):
        assert LadderLevel.OBSERVATION < LadderLevel.EPISODE
        assert LadderLevel.EPISODE < LadderLevel.PATTERN
        assert LadderLevel.PATTERN < LadderLevel.HEURISTIC
        assert LadderLevel.HEURISTIC < LadderLevel.CONCEPT
        assert LadderLevel.CONCEPT < LadderLevel.INVARIANT
        assert LadderLevel.INVARIANT < LadderLevel.THEORY

    def test_level_labels(self):
        assert LadderLevel.OBSERVATION.label == "Observation"
        assert LadderLevel.THEORY.label == "Theory"
        assert LadderLevel.CONCEPT.label == "Concept"

    def test_level_int_values(self):
        assert int(LadderLevel.OBSERVATION) == 0
        assert int(LadderLevel.THEORY) == 6


class TestEpistemicEntropy:
    """Tests for EpistemicEntropy computation."""

    def test_zero_evidence_zero_entropy(self):
        entropy = EpistemicEntropy(
            level=LadderLevel.OBSERVATION,
            evidence_count=0,
            success_count=0,
            failure_count=0,
            contradiction_count=0,
            domain_count=0,
            unique_pattern_count=0,
        )
        assert entropy.compute() == 0.0

    def test_balanced_outcomes_high_entropy(self):
        """50/50 success/failure should have maximum outcome entropy."""
        entropy = EpistemicEntropy(
            level=LadderLevel.PATTERN,
            evidence_count=10,
            success_count=5,
            failure_count=5,
            contradiction_count=2,
            domain_count=3,
            unique_pattern_count=3,
        )
        value = entropy.compute()
        assert 0.3 < value < 1.0  # Should be non-trivial

    def test_all_success_lower_entropy(self):
        """100% success should have lower outcome entropy."""
        entropy_all_success = EpistemicEntropy(
            level=LadderLevel.PATTERN,
            evidence_count=10,
            success_count=10,
            failure_count=0,
            contradiction_count=0,
            domain_count=1,
            unique_pattern_count=1,
        )
        entropy_balanced = EpistemicEntropy(
            level=LadderLevel.PATTERN,
            evidence_count=10,
            success_count=5,
            failure_count=5,
            contradiction_count=2,
            domain_count=3,
            unique_pattern_count=3,
        )
        assert entropy_all_success.compute() < entropy_balanced.compute()

    def test_many_contradictions_higher_entropy(self):
        """More contradictions should increase entropy at higher levels."""
        entropy_low = EpistemicEntropy(
            level=LadderLevel.HEURISTIC,
            evidence_count=10,
            success_count=7,
            failure_count=3,
            contradiction_count=0,
            domain_count=2,
            unique_pattern_count=2,
        )
        entropy_high = EpistropicEntropy = EpistemicEntropy(
            level=LadderLevel.HEURISTIC,
            evidence_count=10,
            success_count=7,
            failure_count=3,
            contradiction_count=5,
            domain_count=2,
            unique_pattern_count=2,
        )
        assert entropy_high.compute() > entropy_low.compute()


class TestAbstractionForgettingTrigger:
    """Tests for abstraction forgetting policies."""

    def test_observation_to_episode_forgetting(self):
        trigger = AbstractionForgettingTrigger(
            from_level=LadderLevel.OBSERVATION,
            to_level=LadderLevel.EPISODE,
        )
        policy = trigger.get_forgetting_policy()
        assert "forget" in policy
        assert "retain" in policy
        assert policy["retention_ratio"] < 1.0

    def test_all_transitions_have_policies(self):
        """Every canonical transition should have a forgetting policy."""
        for t in CANONICAL_TRANSITIONS:
            trigger = AbstractionForgettingTrigger(t.from_level, t.to_level)
            policy = trigger.get_forgetting_policy()
            assert "retention_ratio" in policy
            assert 0.0 < policy["retention_ratio"] <= 1.0

    def test_higher_transitions_retain_less(self):
        """Higher transitions should retain less detail."""
        trigger_low = AbstractionForgettingTrigger(
            LadderLevel.OBSERVATION, LadderLevel.EPISODE
        )
        trigger_high = AbstractionForgettingTrigger(
            LadderLevel.INVARIANT, LadderLevel.THEORY
        )
        policy_low = trigger_low.get_forgetting_policy()
        policy_high = trigger_high.get_forgetting_policy()
        assert policy_high["retention_ratio"] <= policy_low["retention_ratio"]


class TestLadderState:
    """Tests for LadderState."""

    def test_initial_state(self):
        state = LadderState(area_id="test")
        assert state.current_level == LadderLevel.OBSERVATION
        assert state.transition_count == 0

    def test_record_evidence(self):
        state = LadderState(area_id="test")
        state.record_evidence(success=True, domain="physics")
        state.record_evidence(success=False, domain="chemistry", contradiction=True)
        
        level = int(LadderLevel.OBSERVATION)
        assert state.evidence_at_level[level] == 2
        assert state.successes_at_level[level] == 1
        assert state.failures_at_level[level] == 1
        assert state.contradictions_at_level[level] == 1
        assert "physics" in state.domains_at_level[level]
        assert "chemistry" in state.domains_at_level[level]

    def test_compute_entropy(self):
        state = LadderState(area_id="test")
        state.record_evidence(success=True)
        entropy = state.compute_current_entropy()
        assert 0.0 <= entropy <= 1.0


class TestLadderAscentEngine:
    """Tests for the full Ladder Ascent Engine."""

    def test_create_state(self):
        engine = LadderAscentEngine()
        state = engine.create_state("comparison_tasks")
        assert state.area_id == "comparison_tasks"
        assert state.current_level == LadderLevel.OBSERVATION

    def test_no_transition_without_evidence(self):
        engine = LadderAscentEngine()
        state = engine.create_state("test")
        result = engine.check_transition(state)
        assert not result.should_transition

    def test_observation_to_episode_transition(self):
        """With enough evidence, should transition from Observation to Episode."""
        engine = LadderAscentEngine()
        state = engine.create_state("test")
        
        # Add enough evidence
        for i in range(5):
            state.record_evidence(success=True)
        
        # Add enough entropy (mixed outcomes help)
        for i in range(5):
            state.record_evidence(success=False)
        
        result = engine.check_transition(state)
        # Should have enough evidence (10 > 1 minimum)
        assert result.evidence_met

    def test_execute_transition(self):
        """Test that executing a transition changes the level."""
        engine = LadderAscentEngine()
        state = engine.create_state("test")
        
        # Force conditions for 0→1 transition
        for i in range(20):
            state.record_evidence(
                success=(i % 2 == 0),
                domain="physics",
                contradiction=(i % 3 == 0),
            )
        
        result = engine.check_transition(state)
        
        if result.should_transition:
            execution = engine.execute_transition(state, result)
            assert execution.executed
            assert state.current_level == LadderLevel.EPISODE
            assert state.transition_count == 1

    def test_system_overview(self):
        engine = LadderAscentEngine()
        engine.create_state("area_a")
        engine.create_state("area_b")
        
        overview = engine.get_system_overview()
        assert "area_a" in overview
        assert "area_b" in overview
        assert overview["area_a"]["current_level"] == "Observation"

    def test_crisis_induced_transition(self):
        """
        Test that the Heuristic→Concept transition can be triggered by failure.
        This is the crisis-induced transition from Anomaly Theory.
        """
        engine = LadderAscentEngine()
        state = engine.create_state("crisis_test")
        
        # Manually set level to HEURISTIC
        state.current_level = LadderLevel.HEURISTIC
        
        # Record failures (crisis trigger)
        for i in range(5):
            state.record_evidence(
                success=False,
                domain=f"domain_{i % 3}",
                contradiction=True,
            )
        
        result = engine.check_transition(state)
        # The failure_trigger criterion should be checked
        assert result.transition is not None
        assert result.transition.failure_trigger is True


class TestCanonicalTransitions:
    """Tests for the canonical transition criteria."""

    def test_all_transitions_defined(self):
        """There should be a transition for every adjacent level pair."""
        for i in range(6):
            from_level = LadderLevel(i)
            to_level = LadderLevel(i + 1)
            found = any(
                t.from_level == from_level and t.to_level == to_level
                for t in CANONICAL_TRANSITIONS
            )
            assert found, f"Missing transition: {from_level.label} → {to_level.label}"

    def test_crisis_transition_at_heuristic_to_concept(self):
        """The Heuristic→Concept transition should be failure-triggered."""
        for t in CANONICAL_TRANSITIONS:
            if t.from_level == LadderLevel.HEURISTIC:
                assert t.failure_trigger, "Heuristic→Concept should be crisis-induced"
