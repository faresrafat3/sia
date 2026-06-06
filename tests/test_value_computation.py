"""
Tests for Value Computation Layer — GENESIS
=============================================
"""

import pytest
from virtual_genesis.runtime.value_computation.value_functions import (
    ValueOfComputation,
    ValueOfInformation,
    ValueOfVerification,
    ValueOfAbstraction,
    ValueOfReuse,
    CognitiveReturnCalculator,
    CostTracker,
)


class TestValueOfComputation:
    """Tests for VoC."""

    def test_high_confidence_low_voc(self):
        """When already confident, more thinking has low value."""
        voc = ValueOfComputation.compute(current_confidence=0.95, estimated_difficulty=0.5)
        assert voc < 0.3

    def test_low_confidence_higher_voc(self):
        """When uncertain, more thinking has higher value."""
        voc_low = ValueOfComputation.compute(current_confidence=0.95, estimated_difficulty=0.5)
        voc_high = ValueOfComputation.compute(current_confidence=0.3, estimated_difficulty=0.5)
        assert voc_high > voc_low

    def test_difficult_task_amplifies_voc(self):
        """Harder tasks benefit more from additional thinking."""
        voc_easy = ValueOfComputation.compute(current_confidence=0.5, estimated_difficulty=0.2)
        voc_hard = ValueOfComputation.compute(current_confidence=0.5, estimated_difficulty=0.8)
        assert voc_hard > voc_easy

    def test_voc_always_in_range(self):
        for conf in [0.0, 0.25, 0.5, 0.75, 1.0]:
            for diff in [0.0, 0.5, 1.0]:
                voc = ValueOfComputation.compute(current_confidence=conf, estimated_difficulty=diff)
                assert 0.0 <= voc <= 1.0


class TestValueOfInformation:
    """Tests for VoI."""

    def test_irrelevant_info_low_voi(self):
        voi = ValueOfInformation.compute(
            info_relevance=0.1, info_novelty=0.5, current_uncertainty=0.5
        )
        assert voi < 0.2

    def test_relevant_novel_info_high_voi(self):
        voi = ValueOfInformation.compute(
            info_relevance=0.9, info_novelty=0.9, current_uncertainty=0.8
        )
        assert voi > 0.1

    def test_no_uncertainty_low_voi(self):
        """When already certain, info retrieval has low value."""
        voi = ValueOfInformation.compute(
            info_relevance=0.9, info_novelty=0.9, current_uncertainty=0.05
        )
        assert voi < 0.2

    def test_voi_range(self):
        for rel in [0.0, 0.5, 1.0]:
            for nov in [0.0, 0.5, 1.0]:
                for unc in [0.0, 0.5, 1.0]:
                    voi = ValueOfInformation.compute(
                        info_relevance=rel, info_novelty=nov, current_uncertainty=unc
                    )
                    assert 0.0 <= voi <= 1.0


class TestValueOfVerification:
    """Tests for VoV."""

    def test_low_risk_low_vov(self):
        """When answer is likely correct, verification has low value."""
        vov = ValueOfVerification.compute(
            current_failure_risk=0.05, verifier_accuracy=0.9
        )
        assert vov < 0.3

    def test_high_risk_high_vov(self):
        """When answer is likely wrong, verification has high value."""
        vov = ValueOfVerification.compute(
            current_failure_risk=0.8, verifier_accuracy=0.9, consequence_of_failure=0.9
        )
        assert vov > 0.3

    def test_bad_verifier_reduces_vov(self):
        """Poor verifier accuracy reduces verification value."""
        vov_good = ValueOfVerification.compute(
            current_failure_risk=0.5, verifier_accuracy=0.95
        )
        vov_bad = ValueOfVerification.compute(
            current_failure_risk=0.5, verifier_accuracy=0.3
        )
        assert vov_good >= vov_bad

    def test_vov_range(self):
        for risk in [0.0, 0.5, 1.0]:
            for acc in [0.0, 0.5, 1.0]:
                vov = ValueOfVerification.compute(
                    current_failure_risk=risk, verifier_accuracy=acc
                )
                assert 0.0 <= vov <= 1.0


class TestValueOfAbstraction:
    """Tests for VoA."""

    def test_high_future_benefit_high_voa(self):
        voa = ValueOfAbstraction.compute(
            estimated_future_benefit=0.9, reusability_score=0.8
        )
        assert voa > 0.1

    def test_low_future_benefit_low_voa(self):
        voa = ValueOfAbstraction.compute(
            estimated_future_benefit=0.1, reusability_score=0.2
        )
        assert voa < 0.3

    def test_cost_reduces_voa(self):
        voa_low_cost = ValueOfAbstraction.compute(
            estimated_future_benefit=0.5, reusability_score=0.5, abstraction_cost=0.01
        )
        voa_high_cost = ValueOfAbstraction.compute(
            estimated_future_benefit=0.5, reusability_score=0.5, abstraction_cost=0.1
        )
        assert voa_low_cost >= voa_high_cost


class TestValueOfReuse:
    """Tests for VoR."""

    def test_no_reuse_low_vor(self):
        vor = ValueOfReuse.compute(reuse_count=0, savings_per_use=0.5, artifact_reliability=0.9)
        assert vor == 0.0

    def test_many_reuses_high_vor(self):
        vor = ValueOfReuse.compute(reuse_count=50, savings_per_use=0.8, artifact_reliability=0.9)
        assert vor > 0.3

    def test_unreliable_artifact_reduces_vor(self):
        vor_reliable = ValueOfReuse.compute(
            reuse_count=10, savings_per_use=0.5, artifact_reliability=0.95
        )
        vor_unreliable = ValueOfReuse.compute(
            reuse_count=10, savings_per_use=0.5, artifact_reliability=0.3
        )
        assert vor_reliable > vor_unreliable

    def test_logarithmic_scaling(self):
        """Reuse value should grow logarithmically, not linearly."""
        vor_1 = ValueOfReuse.compute(reuse_count=1, savings_per_use=0.5, artifact_reliability=0.9)
        vor_10 = ValueOfReuse.compute(reuse_count=10, savings_per_use=0.5, artifact_reliability=0.9)
        vor_100 = ValueOfReuse.compute(reuse_count=100, savings_per_use=0.5, artifact_reliability=0.9)
        
        # All values should be positive and increasing
        assert vor_1 > 0
        assert vor_10 > vor_1
        assert vor_100 > vor_10
        
        # But growth rate should slow down (logarithmic)
        # gain_1_to_10 vs gain_10_to_100 scaled per unit
        gain_per_unit_1_10 = (vor_10 - vor_1) / 9
        gain_per_unit_10_100 = (vor_100 - vor_10) / 90
        assert gain_per_unit_10_100 < gain_per_unit_1_10


class TestCostTracker:
    """Tests for CostTracker."""

    def test_record_and_total(self):
        tracker = CostTracker()
        tracker.record("reasoning", tier="tier_1", tokens_used=1000)
        tracker.record("verification", tier="tier_0", tokens_used=200)
        
        assert tracker.get_total_cost() > 0
        assert tracker.get_total_tokens() == 1200

    def test_domain_filtering(self):
        tracker = CostTracker()
        tracker.record("reasoning", tier="tier_1", domain="physics")
        tracker.record("reasoning", tier="tier_2", domain="chemistry")
        
        physics_cost = tracker.get_total_cost(domain="physics")
        chemistry_cost = tracker.get_total_cost(domain="chemistry")
        total = tracker.get_total_cost()
        
        assert physics_cost < total
        assert chemistry_cost < total
        assert abs(physics_cost + chemistry_cost - total) < 1e-10

    def test_cost_by_tier(self):
        tracker = CostTracker()
        tracker.record("task", tier="tier_0")
        tracker.record("task", tier="tier_1")
        tracker.record("task", tier="tier_2")
        
        breakdown = tracker.get_cost_by_tier()
        assert "tier_0" in breakdown
        assert "tier_1" in breakdown
        assert "tier_2" in breakdown
        assert breakdown["tier_2"] > breakdown["tier_0"]

    def test_empty_statistics(self):
        tracker = CostTracker()
        stats = tracker.get_statistics()
        assert stats["total_entries"] == 0


class TestCognitiveReturnCalculator:
    """Tests for the full cognitive return calculator."""

    def test_positive_return(self):
        calc = CognitiveReturnCalculator()
        result = calc.compute_cognitive_return(
            immediate_utility=0.8,
            task_confidence=0.9,
            computation_cost=0.01,
        )
        assert result["worthwhile"]
        assert result["total_return"] > 0

    def test_negative_return(self):
        calc = CognitiveReturnCalculator()
        result = calc.compute_cognitive_return(
            immediate_utility=0.1,
            task_confidence=0.2,
            computation_cost=0.5,
            delay_penalty=0.3,
            noise_risk=0.2,
        )
        assert not result["worthwhile"]

    def test_future_benefit_included(self):
        calc = CognitiveReturnCalculator()
        result_no_future = calc.compute_cognitive_return(
            immediate_utility=0.3,
            task_confidence=0.5,
            computation_cost=0.1,
        )
        
        calc2 = CognitiveReturnCalculator()
        result_with_future = calc2.compute_cognitive_return(
            immediate_utility=0.3,
            task_confidence=0.5,
            computation_cost=0.1,
            estimated_reuse_benefit=0.5,
            learning_benefit=0.3,
        )
        
        assert result_with_future["future_gain"] > result_no_future["future_gain"]

    def test_roi_computation(self):
        calc = CognitiveReturnCalculator()
        result = calc.compute_cognitive_return(
            immediate_utility=0.8,
            task_confidence=0.9,
            computation_cost=0.01,
        )
        assert result["roi"] > 0

    def test_value_functions_computation(self):
        calc = CognitiveReturnCalculator()
        values = calc.compute_value_functions(
            current_confidence=0.6,
            estimated_difficulty=0.5,
            current_failure_risk=0.4,
        )
        assert "VoC" in values
        assert "VoI" in values
        assert "VoV" in values
        assert "VoA" in values
        assert "recommendation" in values
        assert len(values["recommendation"]) > 0

    def test_statistics(self):
        calc = CognitiveReturnCalculator()
        calc.compute_cognitive_return(0.8, 0.9, computation_cost=0.01)
        calc.compute_cognitive_return(0.1, 0.2, computation_cost=0.5)
        
        stats = calc.get_statistics()
        assert stats["total_computations"] == 2
        assert "avg_return" in stats

    def test_cost_tracker_integration(self):
        calc = CognitiveReturnCalculator()
        calc.cost_tracker.record("test_op", tier="tier_1", tokens_used=500)
        
        stats = calc.get_statistics()
        assert stats["total_computations"] == 0  # No cognitive return computed yet
        assert calc.cost_tracker.get_statistics()["total_entries"] == 1
