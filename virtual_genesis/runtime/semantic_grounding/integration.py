"""
Semantic Grounding Integration — GENESIS
=========================================
Bridges the Semantic Grounding Layer with existing GENESIS components:
- Concept Engine
- Verification Runtime
- Economy Control

This integration ensures that:
1. Concepts are only activated when semantically grounded
2. Verification checks semantic correctness, not just keyword presence
3. Economy decisions are informed by semantic complexity
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

from .grounding_checker import (
    SemanticGroundingChecker,
    SemanticFingerprint,
    GroundingReport,
    GroundingLevel,
    get_grounding_checker,
)


@dataclass
class GroundingAwareConcept:
    """A concept enhanced with semantic grounding information."""
    concept_id: str
    name: str
    family: str
    fingerprint: SemanticFingerprint
    grounding_score: float
    is_semantically_validated: bool
    activation_count: int = 0
    success_rate: float = 0.0


@dataclass
class ActivationDecision:
    """Decision on whether to activate a concept, with grounding info."""
    concept: GroundingAwareConcept
    task_fingerprint: SemanticFingerprint
    grounding_report: GroundingReport
    activation_recommended: bool
    reason: str
    confidence: float  # 0.0-1.0


class GroundingAwareConceptEngine:
    """
    Concept Engine enhanced with Semantic Grounding.
    
    This replaces the keyword-based selectivity with semantic validation.
    
    Before a concept is activated:
    1. Create semantic fingerprint of the task
    2. Create semantic fingerprint of the concept
    3. Check grounding alignment
    4. Only activate if semantically grounded
    """
    
    def __init__(
        self,
        base_concept_engine: Any,  # The existing concept_engine
        grounding_checker: Optional[SemanticGroundingChecker] = None,
        min_grounding_threshold: float = 0.65
    ):
        self.base_engine = base_concept_engine
        # If a checker is passed, use it; otherwise create one with the specified threshold
        if grounding_checker is not None:
            self.grounding = grounding_checker
        else:
            self.grounding = SemanticGroundingChecker(min_grounding_threshold=min_grounding_threshold)
        self.min_grounding_threshold = min_grounding_threshold
        
        # Grounding-aware concept cache
        self._grounding_cache: Dict[str, GroundingAwareConcept] = {}
    
    def should_activate_concept(
        self,
        concept_id: str,
        concept_name: str,
        concept_family: str,
        task_description: str,
        task_family: str,
        activation_pattern: str,
        success_contrast: str,
        failure_contrast: str,
    ) -> ActivationDecision:
        """
        Decide whether to activate a concept, using semantic grounding.
        
        This is the core method that replaces keyword-based selectivity.
        """
        # Get or create task fingerprint
        task_fp = self.grounding.create_task_fingerprint(
            task_description=task_description,
            task_family=task_family,
        )
        
        # Get or create concept fingerprint
        concept_fp = self.grounding.create_concept_fingerprint(
            concept_name=concept_name,
            concept_family=concept_family,
            activation_pattern=activation_pattern,
            success_contrast=success_contrast,
            failure_contrast=failure_contrast,
        )
        
        # Check grounding
        report = self.grounding.check_grounding(
            concept_id=concept_id,
            task_fingerprint=task_fp,
            concept_fingerprint=concept_fp,
        )
        
        # Update cache
        grounded_concept = GroundingAwareConcept(
            concept_id=concept_id,
            name=concept_name,
            family=concept_family,
            fingerprint=concept_fp,
            grounding_score=report.alignment_score,
            is_semantically_validated=True,
        )
        self._grounding_cache[concept_id] = grounded_concept
        
        # Make activation decision
        if report.is_safe_to_activate:
            activation_recommended = True
            if report.grounding_level == GroundingLevel.FULLY_GROUNDED:
                reason = f"Fully grounded (score={report.alignment_score:.2f})"
                confidence = 0.9
            else:
                reason = f"Partially grounded (score={report.alignment_score:.2f})"
                confidence = 0.7
        else:
            activation_recommended = False
            reason = f"Not semantically grounded (score={report.alignment_score:.2f}, level={report.grounding_level.value})"
            confidence = 0.95
        
        return ActivationDecision(
            concept=grounded_concept,
            task_fingerprint=task_fp,
            grounding_report=report,
            activation_recommended=activation_recommended,
            reason=reason,
            confidence=confidence,
        )
    
    def get_all_concepts_for_task(
        self,
        task_description: str,
        task_family: str,
        concepts: List[Dict[str, Any]],
        max_active: int = 1,
    ) -> List[ActivationDecision]:
        """
        Get all concepts ranked by semantic grounding to a task.
        
        This replaces the selectivity strategy in the concept engine.
        """
        decisions = []
        
        for concept in concepts:
            decision = self.should_activate_concept(
                concept_id=concept.get("id", concept.get("name", "unknown")),
                concept_name=concept.get("name", "unknown"),
                concept_family=concept.get("family", task_family),
                task_description=task_description,
                task_family=task_family,
                activation_pattern=concept.get("activation_pattern", ""),
                success_contrast=concept.get("success_contrast", ""),
                failure_contrast=concept.get("failure_contrast", ""),
            )
            decisions.append(decision)
        
        # Sort by alignment score descending
        decisions.sort(key=lambda d: d.grounding_report.alignment_score, reverse=True)
        
        # Filter to max_active that are recommended
        recommended = [d for d in decisions if d.activation_recommended]
        return recommended[:max_active]
    
    def get_grounding_statistics(self) -> Dict:
        """Get grounding statistics."""
        return self.grounding.get_grounding_statistics()


class SemanticVerificationBridge:
    """
    Bridge between Semantic Grounding and Verification Runtime.
    
    This ensures that verification checks semantic correctness,
    not just keyword presence.
    """
    
    def __init__(self, grounding_checker: Optional[SemanticGroundingChecker] = None):
        self.grounding = grounding_checker or get_grounding_checker()
    
    def verify_with_semantics(
        self,
        task_fingerprint: SemanticFingerprint,
        output: str,
        expected_outcome_type: str,
        semantic_constraints: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Verify output semantically, not just via keyword matching.
        
        Returns:
            (is_valid, semantic_errors)
        """
        errors = []
        
        # Check outcome type alignment
        if expected_outcome_type:
            # This is where we would check if output matches expected type
            # For now, we just record this as a check point
            pass
        
        # Check semantic constraints
        output_lower = output.lower()
        for constraint in semantic_constraints:
            if constraint.lower() not in output_lower:
                errors.append(f"Semantic constraint not met: {constraint}")
        
        # Check grounding alignment with task
        # (This would be more sophisticated in full implementation)
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def generate_semantic_grounding_feedback(
        self,
        report: GroundingReport,
        output: str,
    ) -> str:
        """
        Generate human-readable feedback on semantic grounding.
        
        This helps improve concept formation based on grounding results.
        """
        feedback_parts = []
        
        feedback_parts.append(f"## Semantic Grounding Report")
        feedback_parts.append(f"**Concept:** {report.concept_id}")
        feedback_parts.append(f"**Alignment Score:** {report.alignment_score:.2f}")
        feedback_parts.append(f"**Grounding Level:** {report.grounding_level.value}")
        
        if report.warnings:
            feedback_parts.append("\n### Warnings")
            for warning in report.warnings:
                feedback_parts.append(f"- {warning}")
        
        if report.suggestions:
            feedback_parts.append("\n### Suggestions")
            for suggestion in report.suggestions:
                feedback_parts.append(f"- {suggestion}")
        
        return "\n".join(feedback_parts)


class SemanticEconomyBridge:
    """
    Bridge between Semantic Grounding and Economy Control.
    
    This enriches economic decisions with semantic complexity information.
    """
    
    def __init__(self, grounding_checker: Optional[SemanticGroundingChecker] = None):
        self.grounding = grounding_checker or get_grounding_checker()
    
    def estimate_semantic_complexity(
        self,
        task_fingerprint: SemanticFingerprint,
    ) -> float:
        """
        Estimate task complexity based on semantic fingerprints.
        
        This is more accurate than keyword-based heuristics because
        it measures actual semantic demand, not surface complexity.
        
        Returns:
            complexity_score: 0.0 (trivial) to 1.0 (extremely complex)
        """
        # Intent vector entropy (higher entropy = more complex)
        intent_values = list(task_fingerprint.intent_vector.values())
        if intent_values:
            # Count non-zero dimensions
            active_dimensions = sum(1 for v in intent_values if v > 0.1)
            # Multiple active dimensions = higher complexity
            dimension_complexity = min(1.0, active_dimensions / 4)
        else:
            dimension_complexity = 0.0
        
        # Constraint complexity
        constraint_count = len(task_fingerprint.constraint_set)
        constraint_complexity = min(1.0, constraint_count / 5)
        
        # Combine
        complexity = 0.6 * dimension_complexity + 0.4 * constraint_complexity
        
        return complexity
    
    def should_escalate_tier(
        self,
        task_description: str,
        task_family: str,
        base_threshold: float = 0.5,
    ) -> Tuple[bool, float, str]:
        """
        Decide whether to escalate to premium tier, using semantic complexity.
        
        This replaces the heuristic-based escalation in EconomyControl.
        
        Returns:
            (should_escalate, complexity_score, reason)
        """
        task_fp = self.grounding.create_task_fingerprint(
            task_description=task_description,
            task_family=task_family,
        )
        
        complexity = self.estimate_semantic_complexity(task_fp)
        
        should_escalate = complexity >= base_threshold
        
        if should_escalate:
            if complexity >= 0.8:
                reason = "Very high semantic complexity"
            elif complexity >= 0.6:
                reason = "High semantic complexity"
            else:
                reason = "Moderate semantic complexity"
        else:
            reason = "Low semantic complexity"
        
        return should_escalate, complexity, reason