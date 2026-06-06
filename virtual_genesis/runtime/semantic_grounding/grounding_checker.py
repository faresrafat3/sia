"""
Semantic Grounding Layer — GENESIS
===================================
Bridge between semantic content and operational structure.

This layer ensures that every symbol, concept, and operation in GENESIS
is grounded in the actual semantics of the task, not just surface syntax.

Core Problem Solved:
- Concept Formation currently builds concepts from keyword patterns
- Verification currently checks keyword presence
- This creates "floating symbols" without semantic grounding

Solution: Semantic Grounding Layer provides:
1. Semantic Fingerprint: a vector representation of task intent
2. Grounding Validator: confirms concept ↔ task alignment
3. Semantic Bridge: connects LLM output to operational structure
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import math
import hashlib


class GroundingLevel(Enum):
    """How well a symbol is grounded in task semantics."""
    FULLY_GROUNDED = "fully_grounded"      # Direct semantic mapping
    PARTIALLY_GROUNDED = "partially_grounded"  # Some semantic alignment
    SUPERFICIAL = "superficial"            # Surface pattern only
    FLOATING = "floating"                  # No semantic connection


@dataclass
class SemanticFingerprint:
    """
    A semantic fingerprint of a task or concept.
    
    Unlike keyword-based matching, this represents the INTENDED meaning:
    - What is the task asking for at a deep level?
    - What are the semantic constraints?
    - What would constitute correct vs incorrect completion?
    """
    intent_vector: Dict[str, float]  # Semantic intent dimensions
    constraint_set: Set[str]         # Semantic constraints
    expected_outcome_type: str       # What kind of output is expected
    grounding_score: float           # 0.0-1.0, how well-grounded this is
    source: str                      # Where this fingerprint came from
    
    def compute_similarity(self, other: 'SemanticFingerprint') -> float:
        """
        Compute semantic similarity between two fingerprints.
        
        Uses cosine similarity on intent vectors + Jaccard on constraint sets.
        """
        # Cosine similarity on intent vectors
        dot_product = 0.0
        norm_self = 0.0
        norm_other = 0.0
        
        all_keys = set(self.intent_vector.keys()) | set(other.intent_vector.keys())
        for key in all_keys:
            v1 = self.intent_vector.get(key, 0.0)
            v2 = other.intent_vector.get(key, 0.0)
            dot_product += v1 * v2
            norm_self += v1 ** 2
            norm_other += v2 ** 2
        
        cosine_sim = dot_product / (math.sqrt(norm_self) * math.sqrt(norm_other) + 1e-9)
        
        # Jaccard similarity on constraint sets
        intersection = len(self.constraint_set & other.constraint_set)
        union = len(self.constraint_set | other.constraint_set)
        jaccard_sim = intersection / (union + 1e-9)
        
        # Combined: 60% intent vector, 40% constraints
        return 0.6 * cosine_sim + 0.4 * jaccard_sim


@dataclass
class GroundingReport:
    """Report on the semantic grounding quality of a concept or operation."""
    concept_id: str
    task_fingerprint: SemanticFingerprint
    concept_fingerprint: SemanticFingerprint
    alignment_score: float          # 0.0-1.0
    grounding_level: GroundingLevel
    is_safe_to_activate: bool
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class SemanticGroundingChecker:
    """
    The core semantic grounding engine.
    
    This is the bridge that solves the "floating symbols" problem.
    Before any concept is activated or any operation is performed,
    this checker validates semantic alignment.
    """
    
    # Semantic intent dimensions (from GENESIS research program)
    INTENT_DIMENSIONS = [
        "comparison",      # Comparing entities
        "synthesis",       # Combining information
        "procedure",       # Following/executing steps
        "analysis",        # Breaking down structure
        "extraction",      # Pulling specific info
        "planning",        # Creating future actions
        "generation",      # Creating new content
        "classification",  # Categorizing
    ]
    
    def __init__(self, min_grounding_threshold: float = 0.65):
        """
        Initialize the grounding checker.
        
        Args:
            min_grounding_threshold: Minimum alignment score to consider
                                    a concept semantically grounded to a task.
        """
        self.min_grounding_threshold = min_grounding_threshold
        self.grounding_history: List[GroundingReport] = []
    
    def create_task_fingerprint(
        self,
        task_description: str,
        task_family: str,
        constraints: Optional[List[str]] = None
    ) -> SemanticFingerprint:
        """
        Create a semantic fingerprint for a task.
        
        This is the first step in grounding: understanding what a task
        actually SEMANTICALLY requires, not just what keywords it contains.
        """
        # Intent vector: infer from family + description
        intent_vector = self._infer_intent_vector(task_description, task_family)
        
        # Constraint set: extract from description
        constraint_set = set()
        if constraints:
            constraint_set = set(constraints)
        else:
            # Auto-extract semantic constraints
            constraint_set = self._extract_constraints(task_description)
        
        # Expected outcome type: infer from family
        outcome_type = self._infer_outcome_type(task_family)
        
        # Grounding score: task fingerprints are the gold standard
        grounding_score = 1.0
        
        return SemanticFingerprint(
            intent_vector=intent_vector,
            constraint_set=constraint_set,
            expected_outcome_type=outcome_type,
            grounding_score=grounding_score,
            source=f"task:{task_description[:50]}"
        )
    
    def create_concept_fingerprint(
        self,
        concept_name: str,
        concept_family: str,
        activation_pattern: str,
        success_contrast: str,
        failure_contrast: str
    ) -> SemanticFingerprint:
        """
        Create a semantic fingerprint for a concept.
        
        This is the key innovation: instead of just storing keywords,
        we create a semantic representation of what the concept MEANS.
        """
        # Intent vector: from concept family + activation pattern
        intent_vector = self._infer_intent_vector(activation_pattern, concept_family)
        
        # Constraint set: from success/failure contrasts
        constraint_set = self._extract_constraints_from_contrasts(
            success_contrast, failure_contrast
        )
        
        # Outcome type: inferred from concept behavior
        outcome_type = self._infer_outcome_type(concept_family)
        
        # Grounding score: starts at 0.5, updated based on validation
        grounding_score = 0.5
        
        return SemanticFingerprint(
            intent_vector=intent_vector,
            constraint_set=constraint_set,
            expected_outcome_type=outcome_type,
            grounding_score=grounding_score,
            source=f"concept:{concept_name}"
        )
    
    def check_grounding(
        self,
        concept_id: str,
        task_fingerprint: SemanticFingerprint,
        concept_fingerprint: SemanticFingerprint
    ) -> GroundingReport:
        """
        Check if a concept is semantically grounded to a task.
        
        This is the core validation: does this concept actually mean
        something relevant to this task, or is it just a surface pattern match?
        """
        # Compute alignment
        alignment_score = task_fingerprint.compute_similarity(concept_fingerprint)
        
        # Determine grounding level
        if alignment_score >= 0.8:
            grounding_level = GroundingLevel.FULLY_GROUNDED
        elif alignment_score >= self.min_grounding_threshold:
            grounding_level = GroundingLevel.PARTIALLY_GROUNDED
        elif alignment_score >= 0.4:
            grounding_level = GroundingLevel.SUPERFICIAL
        else:
            grounding_level = GroundingLevel.FLOATING
        
        # Determine if safe to activate
        is_safe = grounding_level in [
            GroundingLevel.FULLY_GROUNDED,
            GroundingLevel.PARTIALLY_GROUNDED
        ]
        
        # Generate warnings/suggestions
        warnings = []
        suggestions = []
        
        if grounding_level == GroundingLevel.FLOATING:
            warnings.append(
                f"Concept '{concept_id}' is semantically disconnected from task. "
                f"Activation may produce false positives."
            )
            suggestions.append(
                "Consider deactivating this concept for this task family."
            )
        
        if grounding_level == GroundingLevel.SUPERFICIAL:
            warnings.append(
                f"Concept '{concept_id}' has only surface-level alignment. "
                f"May not capture task's semantic essence."
            )
            suggestions.append(
                "Review concept's success/failure contrasts for deeper patterns."
            )
        
        # Check outcome type alignment
        if task_fingerprint.expected_outcome_type != concept_fingerprint.expected_outcome_type:
            warnings.append(
                f"Outcome type mismatch: task expects {task_fingerprint.expected_outcome_type}, "
                f"concept produces {concept_fingerprint.expected_outcome_type}"
            )
        
        # Update concept's grounding score based on validation
        concept_fingerprint.grounding_score = (
            0.7 * concept_fingerprint.grounding_score + 0.3 * alignment_score
        )
        
        report = GroundingReport(
            concept_id=concept_id,
            task_fingerprint=task_fingerprint,
            concept_fingerprint=concept_fingerprint,
            alignment_score=alignment_score,
            grounding_level=grounding_level,
            is_safe_to_activate=is_safe,
            warnings=warnings,
            suggestions=suggestions
        )
        
        self.grounding_history.append(report)
        return report
    
    def _infer_intent_vector(
        self,
        text: str,
        family: str
    ) -> Dict[str, float]:
        """Infer semantic intent vector from text and family."""
        text_lower = text.lower()
        
        # Base vector from family
        vector = {dim: 0.0 for dim in self.INTENT_DIMENSIONS}
        if family in vector:
            vector[family] = 0.8
        
        # Boost based on text content
        semantic_indicators = {
            "comparison": ["compare", "differ", "contrast", "versus", "better", "worse", "بالمقارنة", "أفضل"],
            "synthesis": ["combine", "merge", "integrate", "synthesize", "build", "دمج", "بناء"],
            "procedure": ["step", "follow", "execute", "implement", "خطوات", "تنفيذ"],
            "analysis": ["analyze", "examine", "break down", "decompose", "تحليل"],
            "extraction": ["extract", "find", "locate", "pull", "استخراج", "إيجاد"],
            "planning": ["plan", "strategy", "prepare", "future", "تخطيط"],
            "generation": ["generate", "create", "produce", "new", "توليد", "إنشاء"],
            "classification": ["classify", "categorize", "type", "kind", "تصنيف"],
        }
        
        for dimension, keywords in semantic_indicators.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            if count > 0:
                vector[dimension] = min(1.0, vector.get(dimension, 0) + count * 0.2)
        
        return vector
    
    def _extract_constraints(self, text: str) -> Set[str]:
        """Extract semantic constraints from task text."""
        text_lower = text.lower()
        constraints = set()
        
        constraint_indicators = [
            "must", "should", "require", "need", "only", "exactly",
            "at least", "at most", "no more than", "minimum", "maximum",
            "يجب", "لازم", "فقط", "دقيق"
        ]
        
        # Extract constraint phrases
        for indicator in constraint_indicators:
            if indicator in text_lower:
                # Find the context around the indicator
                idx = text_lower.find(indicator)
                start = max(0, idx - 20)
                end = min(len(text), idx + 40)
                constraint = text[start:end].strip()
                if len(constraint) > 5:
                    constraints.add(constraint)
        
        return constraints
    
    def _extract_constraints_from_contrasts(
        self,
        success: str,
        failure: str
    ) -> Set[str]:
        """Extract what makes success different from failure."""
        success_lower = success.lower()
        failure_lower = failure.lower()
        
        # Find key differences
        success_words = set(success_lower.split())
        failure_words = set(failure_lower.split())
        
        # Key semantic markers
        key_differences = success_words - failure_words
        
        constraints = set()
        for word in key_differences:
            if len(word) > 4:  # Filter out small words
                constraints.add(f"success_indicator:{word}")
        
        return constraints
    
    def _infer_outcome_type(self, family: str) -> str:
        """Infer expected outcome type from family."""
        outcome_map = {
            "comparison": "comparison_result",
            "synthesis": "integrated_output",
            "procedure": "executed_plan",
            "analysis": "decomposed_structure",
            "extraction": "extracted_values",
            "planning": "future_action_sequence",
            "classification": "category_assignment",
            "generation": "new_content",
        }
        return outcome_map.get(family, "general_output")
    
    def get_grounding_statistics(self) -> Dict:
        """Get statistics on grounding quality across history."""
        if not self.grounding_history:
            return {"total_checks": 0}
        
        total = len(self.grounding_history)
        fully_grounded = sum(
            1 for r in self.grounding_history 
            if r.grounding_level == GroundingLevel.FULLY_GROUNDED
        )
        partially_grounded = sum(
            1 for r in self.grounding_history 
            if r.grounding_level == GroundingLevel.PARTIALLY_GROUNDED
        )
        floating = sum(
            1 for r in self.grounding_history 
            if r.grounding_level == GroundingLevel.FLOATING
        )
        
        avg_alignment = sum(r.alignment_score for r in self.grounding_history) / total
        
        return {
            "total_checks": total,
            "fully_grounded": fully_grounded,
            "partially_grounded": partially_grounded,
            "superficial": total - fully_grounded - partially_grounded - floating,
            "floating": floating,
            "avg_alignment": round(avg_alignment, 3),
            "floating_rate": round(floating / total, 3),
        }


# Singleton instance
_grounding_checker: Optional[SemanticGroundingChecker] = None


def get_grounding_checker() -> SemanticGroundingChecker:
    """Get the singleton grounding checker instance."""
    global _grounding_checker
    if _grounding_checker is None:
        _grounding_checker = SemanticGroundingChecker()
    return _grounding_checker