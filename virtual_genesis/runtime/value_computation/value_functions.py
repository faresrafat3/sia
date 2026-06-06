"""
Value Functions — GENESIS
==========================
Concrete implementations of the Cognitive Economy value functions.

Each function takes measurable inputs and produces a number in [0, 1]
representing the expected value of that cognitive investment.

Design Principles:
    1. All values are in [0, 1] for comparability
    2. All functions are pure (no side effects)
    3. All functions degrade gracefully with missing data
    4. All functions are deterministic (same input → same output)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValueOfComputation:
    """
    VoC = What is the expected benefit of additional reasoning?
    
    From Cognitive Economy Theory §11.1:
    "ما فائدة تفكير إضافي مقارنة بتكلفته؟"
    
    Computation:
    VoC = P(improve_answer | more_thinking) × utility_of_improvement - cost_of_thinking
    
    Simplified: VoC = max(0, current_uncertainty × marginal_improvement_rate - thinking_cost)
    """
    
    @staticmethod
    def compute(
        current_confidence: float,
        estimated_difficulty: float,
        thinking_cost: float = 0.01,
        diminishing_returns_factor: float = 0.5,
    ) -> float:
        """
        Compute the value of additional computation.
        
        Args:
            current_confidence: [0, 1] how confident are we in current answer?
            estimated_difficulty: [0, 1] how hard is this task?
            thinking_cost: [0, 1] normalized cost of additional thinking
            diminishing_returns_factor: how quickly returns diminish
        
        Returns:
            VoC in [0, 1]
        """
        # Uncertainty = room for improvement
        uncertainty = 1.0 - current_confidence
        
        # Marginal improvement decreases as confidence increases
        marginal_improvement = uncertainty * diminishing_returns_factor
        
        # Difficulty amplifies the value (harder problems benefit more from thinking)
        difficulty_multiplier = 0.5 + 0.5 * estimated_difficulty
        
        # Expected value
        value = marginal_improvement * difficulty_multiplier - thinking_cost
        
        return max(0.0, min(1.0, value))


@dataclass
class ValueOfInformation:
    """
    VoI = What is the expected benefit of retrieving additional information?
    
    From Cognitive Economy Theory §11.2:
    "ما فائدة جمع evidence أو retrieval إضافي؟"
    
    Computation:
    VoI depends on:
    - How much the retrieved info could change the answer
    - How likely the info is to be relevant
    - Cost of retrieval
    """
    
    @staticmethod
    def compute(
        info_relevance: float,
        info_novelty: float,
        current_uncertainty: float,
        retrieval_cost: float = 0.005,
    ) -> float:
        """
        Compute the value of information retrieval.
        
        Args:
            info_relevance: [0, 1] how relevant is the expected info?
            info_novelty: [0, 1] how different is it from what we already know?
            current_uncertainty: [0, 1] how uncertain are we?
            retrieval_cost: [0, 1] normalized cost of retrieval
        
        Returns:
            VoI in [0, 1]
        """
        # Info that is both relevant and novel is most valuable
        relevance_novelty = info_relevance * (0.3 + 0.7 * info_novelty)
        
        # More valuable when we're uncertain
        value = relevance_novelty * current_uncertainty - retrieval_cost
        
        return max(0.0, min(1.0, value))


@dataclass
class ValueOfVerification:
    """
    VoV = What is the expected benefit of an additional verification check?
    
    From Cognitive Economy Theory §11.3:
    "ما فائدة check إضافي أو judge إضافي؟"
    
    Computation:
    VoV depends on:
    - Current failure risk (how likely is the answer wrong?)
    - Verification accuracy (how good is the verifier?)
    - Cost of verification
    """
    
    @staticmethod
    def compute(
        current_failure_risk: float,
        verifier_accuracy: float,
        verification_cost: float = 0.003,
        consequence_of_failure: float = 0.5,
    ) -> float:
        """
        Compute the value of verification.
        
        Args:
            current_failure_risk: [0, 1] probability answer is wrong
            verifier_accuracy: [0, 1] how accurate is the verifier
            verification_cost: [0, 1] normalized cost
            consequence_of_failure: [0, 1] how bad is a wrong answer?
        
        Returns:
            VoV in [0, 1]
        """
        # Expected benefit = catching a failure × how bad it would be
        expected_benefit = (
            current_failure_risk * verifier_accuracy * consequence_of_failure
        )
        
        value = expected_benefit - verification_cost
        
        return max(0.0, min(1.0, value))


@dataclass
class ValueOfAbstraction:
    """
    VoA = What is the expected benefit of investing cognition in
    concept/skill/theory formation instead of answering the current task?
    
    From Cognitive Economy Theory §11.4:
    "ما فائدة صرف compute على concept/skill/theory بدل الجواب الحالي فقط؟"
    
    Computation:
    VoA depends on:
    - How many future tasks would benefit from this abstraction?
    - How reusable is the expected abstraction?
    - Cost of abstraction (time + compute diverted from current task)
    """
    
    @staticmethod
    def compute(
        estimated_future_benefit: float,
        reusability_score: float,
        abstraction_cost: float = 0.02,
        immediate_opportunity_cost: float = 0.01,
    ) -> float:
        """
        Compute the value of abstraction.
        
        Args:
            estimated_future_benefit: [0, 1] how much will this help future tasks?
            reusability_score: [0, 1] how generalizable is the expected abstraction?
            abstraction_cost: [0, 1] compute cost of abstraction
            immediate_opportunity_cost: [0, 1] cost of not focusing on current task
        
        Returns:
            VoA in [0, 1]
        """
        # Future benefit × reusability × decay (future is uncertain)
        future_value = estimated_future_benefit * reusability_score * 0.7
        
        value = future_value - abstraction_cost - immediate_opportunity_cost
        
        return max(0.0, min(1.0, value))


@dataclass
class ValueOfReuse:
    """
    VoR = What is the value of reusing an existing artifact?
    
    From Cognitive Economy Theory §11.5:
    "ما فائدة أن يكون الناتج reusable في المستقبل؟"
    
    Computation:
    VoR depends on:
    - How many times has this artifact been reused?
    - How much does reuse save vs. recomputing?
    - How reliable is the artifact?
    """
    
    @staticmethod
    def compute(
        reuse_count: int,
        savings_per_use: float,
        artifact_reliability: float,
    ) -> float:
        """
        Compute the value of reusing an artifact.
        
        Args:
            reuse_count: how many times has it been reused
            savings_per_use: [0, 1] fraction of cost saved per reuse
            artifact_reliability: [0, 1] how reliable is the artifact
        
        Returns:
            VoR in [0, 1]
        """
        # Logarithmic scaling: first few reuses are most valuable
        reuse_value = math.log(1 + reuse_count) / math.log(11)  # Normalized
        
        value = reuse_value * savings_per_use * artifact_reliability
        
        return max(0.0, min(1.0, value))


@dataclass
class CostEntry:
    """A single cost tracking entry."""
    operation: str
    tier: str
    tokens_used: int = 0
    time_seconds: float = 0.0
    api_calls: int = 1
    cost_simulated: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    task_id: str = ""
    domain: str = ""


class CostTracker:
    """
    Tracks actual cognitive costs for ROI computation.
    
    This converts the philosophical "cost" dimension into
    actual tracked numbers.
    """
    
    # Simulated cost per tier (for offline/simulation mode)
    TIER_COSTS = {
        "tier_0": 0.0001,   # Cheap model
        "tier_1": 0.001,    # Standard model
        "tier_2": 0.01,     # Premium model
    }
    
    def __init__(self):
        self.entries: List[CostEntry] = []
    
    def record(
        self,
        operation: str,
        tier: str = "tier_1",
        tokens_used: int = 0,
        time_seconds: float = 0.0,
        api_calls: int = 1,
        task_id: str = "",
        domain: str = "",
    ) -> CostEntry:
        """Record a cost entry."""
        cost = self.TIER_COSTS.get(tier, 0.001) * api_calls
        
        entry = CostEntry(
            operation=operation,
            tier=tier,
            tokens_used=tokens_used,
            time_seconds=time_seconds,
            api_calls=api_calls,
            cost_simulated=cost,
            task_id=task_id,
            domain=domain,
        )
        self.entries.append(entry)
        return entry
    
    def get_total_cost(self, domain: Optional[str] = None) -> float:
        """Get total cost, optionally filtered by domain."""
        if domain:
            return sum(e.cost_simulated for e in self.entries if e.domain == domain)
        return sum(e.cost_simulated for e in self.entries)
    
    def get_total_tokens(self, domain: Optional[str] = None) -> int:
        """Get total tokens used."""
        if domain:
            return sum(e.tokens_used for e in self.entries if e.domain == domain)
        return sum(e.tokens_used for e in self.entries)
    
    def get_cost_by_tier(self) -> Dict[str, float]:
        """Get cost breakdown by tier."""
        breakdown: Dict[str, float] = {}
        for entry in self.entries:
            breakdown[entry.tier] = breakdown.get(entry.tier, 0.0) + entry.cost_simulated
        return breakdown
    
    def get_cost_by_operation(self) -> Dict[str, float]:
        """Get cost breakdown by operation type."""
        breakdown: Dict[str, float] = {}
        for entry in self.entries:
            breakdown[entry.operation] = breakdown.get(entry.operation, 0.0) + entry.cost_simulated
        return breakdown
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cost statistics."""
        if not self.entries:
            return {"total_entries": 0}
        
        return {
            "total_entries": len(self.entries),
            "total_cost": self.get_total_cost(),
            "total_tokens": self.get_total_tokens(),
            "by_tier": self.get_cost_by_tier(),
            "by_operation": self.get_cost_by_operation(),
            "avg_cost_per_entry": self.get_total_cost() / len(self.entries),
        }


class CognitiveReturnCalculator:
    """
    The unified calculator for Expected Cognitive Return.
    
    From Cognitive Economy Theory §12:
    
    Expected Cognitive Return = 
        Immediate Utility Gain + 
        Future Reuse Gain + 
        Learning Gain - 
        Cost - 
        Delay Penalty - 
        Noise Risk
    """
    
    def __init__(self):
        self.cost_tracker = CostTracker()
        self._roi_history: List[Dict[str, Any]] = []
    
    def compute_cognitive_return(
        self,
        # Immediate Utility
        immediate_utility: float,
        task_confidence: float,
        
        # Future Value
        estimated_reuse_benefit: float = 0.0,
        learning_benefit: float = 0.0,
        abstraction_benefit: float = 0.0,
        
        # Costs
        computation_cost: float = 0.0,
        delay_penalty: float = 0.0,
        noise_risk: float = 0.0,
        
        # Context
        task_id: str = "",
        domain: str = "",
        tier: str = "tier_1",
    ) -> Dict[str, Any]:
        """
        Compute the full Expected Cognitive Return.
        
        This is the central economic decision function for GENESIS.
        A positive return means the cognitive investment was worthwhile.
        """
        # Immediate Utility Gain
        immediate_gain = immediate_utility * task_confidence
        
        # Future Value (discounted by 0.7 for uncertainty)
        future_gain = 0.7 * (estimated_reuse_benefit + learning_benefit + abstraction_benefit)
        
        # Total expected return
        total_return = (
            immediate_gain +
            future_gain -
            computation_cost -
            delay_penalty -
            noise_risk
        )
        
        result = {
            "task_id": task_id,
            "domain": domain,
            "tier": tier,
            "immediate_gain": round(immediate_gain, 4),
            "future_gain": round(future_gain, 4),
            "total_return": round(total_return, 4),
            "cost": round(computation_cost, 4),
            "delay_penalty": round(delay_penalty, 4),
            "noise_risk": round(noise_risk, 4),
            "roi": round(total_return / max(0.001, computation_cost), 2) if computation_cost > 0 else 0.0,
            "worthwhile": total_return > 0,
            "timestamp": datetime.now().isoformat(),
        }
        
        self._roi_history.append(result)
        return result
    
    def compute_value_functions(
        self,
        current_confidence: float,
        estimated_difficulty: float,
        current_failure_risk: float,
        info_relevance: float = 0.5,
        info_novelty: float = 0.5,
        verifier_accuracy: float = 0.8,
        future_benefit: float = 0.3,
        reusability: float = 0.5,
    ) -> Dict[str, float]:
        """
        Compute all value functions at once.
        
        Returns a dictionary of all value functions.
        """
        uncertainty = 1.0 - current_confidence
        
        voc = ValueOfComputation.compute(
            current_confidence=current_confidence,
            estimated_difficulty=estimated_difficulty,
        )
        
        voi = ValueOfInformation.compute(
            info_relevance=info_relevance,
            info_novelty=info_novelty,
            current_uncertainty=uncertainty,
        )
        
        vov = ValueOfVerification.compute(
            current_failure_risk=current_failure_risk,
            verifier_accuracy=verifier_accuracy,
        )
        
        voa = ValueOfAbstraction.compute(
            estimated_future_benefit=future_benefit,
            reusability_score=reusability,
        )
        
        return {
            "VoC": round(voc, 4),
            "VoI": round(voi, 4),
            "VoV": round(vov, 4),
            "VoA": round(voa, 4),
            "recommendation": self._recommend_investment(voc, voi, vov, voa),
        }
    
    def _recommend_investment(
        self, voc: float, voi: float, vov: float, voa: float
    ) -> str:
        """Recommend where to invest cognitive resources."""
        values = {
            "more_thinking": voc,
            "information_retrieval": voi,
            "verification": vov,
            "abstraction_building": voa,
        }
        
        best = max(values, key=values.get)
        best_value = values[best]
        
        if best_value < 0.05:
            return "No cognitive investment is justified. Accept current answer."
        
        recommendations = {
            "more_thinking": f"Think more (VoC={voc:.3f})",
            "information_retrieval": f"Retrieve more info (VoI={voi:.3f})",
            "verification": f"Verify answer (VoV={vov:.3f})",
            "abstraction_building": f"Build abstraction (VoA={voa:.3f})",
        }
        
        return f"Best investment: {recommendations[best]}"
    
    def get_roi_history(self) -> List[Dict[str, Any]]:
        """Get ROI computation history."""
        return list(self._roi_history)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        if not self._roi_history:
            return {"total_computations": 0}
        
        returns = [r["total_return"] for r in self._roi_history]
        rois = [r["roi"] for r in self._roi_history if r["roi"] != 0]
        
        return {
            "total_computations": len(self._roi_history),
            "avg_return": round(sum(returns) / len(returns), 4),
            "positive_return_count": sum(1 for r in returns if r > 0),
            "negative_return_count": sum(1 for r in returns if r <= 0),
            "avg_roi": round(sum(rois) / len(rois), 2) if rois else 0,
            "cost_statistics": self.cost_tracker.get_statistics(),
        }


# Singleton
_calculator: Optional[CognitiveReturnCalculator] = None


def get_cognitive_return_calculator() -> CognitiveReturnCalculator:
    """Get the singleton cognitive return calculator."""
    global _calculator
    if _calculator is None:
        _calculator = CognitiveReturnCalculator()
    return _calculator
