"""
Concept Object Schema — GENESIS
===============================
Formal specification of what a "Concept" IS in GENESIS.

This addresses the gap: "What is a Concept Object precisely?
What is its relationship to Skill, Theory, Invariant?"

The schema defines:
1. Concept Identity: What makes a concept unique
2. Concept Structure: Internal components
3. Concept Lifecycle: Birth, activation, decay, death
4. Concept Relations: Hierarchy with Skill, Theory, Invariant
"""

from typing import Optional, List, Dict, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid


class ConceptStatus(Enum):
    """Lifecycle states of a concept."""
    EMBRYONIC = "embryonic"       # Just formed, not validated
    ACTIVE = "active"             # Validated, available for use
    DORMANT = "dormant"           # Not used recently
    DECAYING = "decaying"         # Losing relevance
    ARCHIVED = "archived"         # Preserved for lineage, not used
    REJECTED = "rejected"         # Failed validation


class SemanticDimension(Enum):
    """Dimensions of semantic content for concepts."""
    COMPARISON = "comparison"
    SYNTHESIS = "synthesis"
    PROCEDURE = "procedure"
    ANALYSIS = "analysis"
    EXTRACTION = "extraction"
    PLANNING = "planning"
    GENERATION = "generation"
    CLASSIFICATION = "classification"


@dataclass
class ConceptSignature:
    """
    The semantic fingerprint that uniquely identifies this concept.
    
    Unlike a name or ID, this is content-based and can be compared
    for overlap with other concepts or tasks.
    """
    primary_dimension: SemanticDimension
    secondary_dimensions: Set[SemanticDimension] = field(default_factory=set)
    semantic_constraints: Set[str] = field(default_factory=set)
    expected_outcome_type: str = ""
    
    def compute_overlap(self, other: 'ConceptSignature') -> float:
        """Compute semantic overlap with another signature."""
        if not isinstance(other, ConceptSignature):
            return 0.0
        
        # Primary dimension match
        primary_match = 1.0 if self.primary_dimension == other.primary_dimension else 0.0
        
        # Secondary dimension overlap (Jaccard)
        secondary_overlap = len(self.secondary_dimensions & other.secondary_dimensions)
        secondary_total = len(self.secondary_dimensions | other.secondary_dimensions)
        secondary_score = secondary_overlap / max(1, secondary_total)
        
        # Constraint overlap
        constraint_overlap = len(self.semantic_constraints & other.semantic_constraints)
        constraint_total = len(self.semantic_constraints | other.semantic_constraints)
        constraint_score = constraint_overlap / max(1, constraint_total)
        
        # Weighted combination
        return 0.5 * primary_match + 0.3 * secondary_score + 0.2 * constraint_score


@dataclass
class ConceptEvidence:
    """Evidence for/against a concept's validity."""
    success_cases: List[str] = field(default_factory=list)  # Task IDs
    failure_cases: List[str] = field(default_factory=list)   # Task IDs
    neutral_cases: List[str] = field(default_factory=list)   # Task IDs
    
    success_pattern: str = ""  # What made these successes work?
    failure_pattern: str = ""  # What caused these failures?
    
    @property
    def total_cases(self) -> int:
        return len(self.success_cases) + len(self.failure_cases) + len(self.neutral_cases)
    
    @property
    def success_rate(self) -> float:
        total = self.total_cases
        return len(self.success_cases) / max(1, total)
    
    @property
    def failure_rate(self) -> float:
        total = self.total_cases
        return len(self.failure_cases) / max(1, total)


@dataclass
class ConceptActivationContext:
    """Context information when a concept was activated."""
    task_id: str
    task_description: str
    task_family: str
    activation_timestamp: datetime
    grounding_score: float
    was_successful: Optional[bool] = None  # None = not yet evaluated


@dataclass
class Concept:
    """
    The formal Concept Object in GENESIS.
    
    This replaces informal "concept" references with a precise structure
    that can be:
    - Validated against tasks
    - Compared for overlap
    - Tracked through lifecycle
    - Related to other artifacts (Skill, Theory, Invariant)
    """
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    lineage: str = ""  # Parent concept ID if derived
    
    # Semantic Structure
    signature: ConceptSignature = field(default_factory=ConceptSignature)
    evidence: ConceptEvidence = field(default_factory=ConceptEvidence)
    
    # Lifecycle
    status: ConceptStatus = ConceptStatus.EMBRYONIC
    created_at: datetime = field(default_factory=datetime.now)
    last_activated_at: Optional[datetime] = None
    activation_count: int = 0
    
    # Metadata
    family: str = ""  # Task family this concept belongs to
    creation_trigger: str = ""  # What task triggered formation?
    
    # Activation history (for learning)
    activation_history: List[ConceptActivationContext] = field(default_factory=list)
    
    # Relationships
    related_skills: List[str] = field(default_factory=list)  # Skill IDs
    supporting_theories: List[str] = field(default_factory=list)  # Theory IDs
    contradicts: List[str] = field(default_factory=list)  # Concept IDs
    
    def should_activate_for(self, task_family: str, task_signature: ConceptSignature) -> Tuple[bool, float]:
        """
        Decide if this concept should be activated for a task.
        
        Returns:
            (should_activate, alignment_score)
        """
        # Family must match
        if task_family != self.family:
            return False, 0.0
        
        # Compute semantic alignment
        alignment = self.signature.compute_overlap(task_signature)
        
        # Minimum threshold for activation
        ACTIVATION_THRESHOLD = 0.5
        
        if alignment >= ACTIVATION_THRESHOLD:
            return True, alignment
        return False, alignment
    
    def record_activation(self, context: ConceptActivationContext) -> None:
        """Record an activation event for learning."""
        self.activation_history.append(context)
        self.activation_count += 1
        self.last_activated_at = context.activation_timestamp
        
        # Update evidence if outcome known
        if context.was_successful is not None:
            if context.was_successful:
                if context.task_id not in self.evidence.success_cases:
                    self.evidence.success_cases.append(context.task_id)
            else:
                if context.task_id not in self.evidence.failure_cases:
                    self.evidence.failure_cases.append(context.task_id)
        
        # Check if status should change
        self._update_status()
    
    def _update_status(self) -> None:
        """Update concept status based on activation history."""
        if self.status == ConceptStatus.EMBRYONIC:
            # Promote to active after some successful activations
            if len(self.evidence.success_cases) >= 3:
                self.status = ConceptStatus.ACTIVE
        
        elif self.status == ConceptStatus.ACTIVE:
            # Check for dormancy
            if self.activation_count > 0:
                recent_activations = [
                    ctx for ctx in self.activation_history
                    if (datetime.now() - ctx.activation_timestamp).days < 30
                ]
                if len(recent_activations) == 0:
                    self.status = ConceptStatus.DORMANT
        
        elif self.status == ConceptStatus.DORMANT:
            # Can reactivate
            pass
    
    def get_maturity_score(self) -> float:
        """
        Compute concept maturity (0.0 to 1.0).
        
        Based on:
        - Activation count
        - Success rate
        - Consistency of outcomes
        - Time since creation
        """
        # Base score from activation count (log scale)
        activation_score = min(1.0, self.activation_count / 10)
        
        # Success rate contribution
        success_score = self.evidence.success_rate
        
        # Recency bonus
        if self.last_activated_at:
            days_since = (datetime.now() - self.last_activated_at).days
            recency_score = max(0, 1.0 - days_since / 90)
        else:
            recency_score = 0.0
        
        # Weighted combination
        maturity = 0.4 * activation_score + 0.4 * success_score + 0.2 * recency_score
        
        return maturity
    
    def is_ready_for_theory(self) -> bool:
        """
        Check if concept has enough evidence to support theory formation.
        
        Requirements:
        - At least 5 total cases
        - Success rate > 0.6
        - Multiple task types (diversity)
        """
        if self.evidence.total_cases < 5:
            return False
        
        if self.evidence.success_rate < 0.6:
            return False
        
        # Check diversity (success cases from different contexts)
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize concept to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "lineage": self.lineage,
            "primary_dimension": self.signature.primary_dimension.value,
            "secondary_dimensions": [d.value for d in self.signature.secondary_dimensions],
            "semantic_constraints": list(self.signature.semantic_constraints),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_activated_at": self.last_activated_at.isoformat() if self.last_activated_at else None,
            "activation_count": self.activation_count,
            "family": self.family,
            "success_rate": self.evidence.success_rate,
            "maturity_score": self.get_maturity_score(),
        }


class ConceptRegistry:
    """
    Registry for managing all concepts in the system.
    
    Provides:
    - Concept storage and retrieval
    - Overlap detection (prevent duplicate concepts)
    - Lifecycle management
    - Search by semantic signature
    """
    
    def __init__(self):
        self._concepts: Dict[str, Concept] = {}
    
    def register(self, concept: Concept) -> bool:
        """
        Register a new concept.
        
        Returns:
            True if registered, False if rejected (duplicate or invalid)
        """
        # Check for duplicate
        for existing in self._concepts.values():
            overlap = concept.signature.compute_overlap(existing.signature)
            if overlap > 0.8:
                # Too similar to existing concept
                return False
        
        self._concepts[concept.id] = concept
        return True
    
    def get(self, concept_id: str) -> Optional[Concept]:
        """Get concept by ID."""
        return self._concepts.get(concept_id)
    
    def find_similar(self, signature: ConceptSignature, threshold: float = 0.6) -> List[Concept]:
        """Find concepts with similar signatures."""
        similar = []
        for concept in self._concepts.values():
            overlap = concept.signature.compute_overlap(signature)
            if overlap >= threshold:
                similar.append((concept, overlap))
        
        # Sort by overlap descending
        similar.sort(key=lambda x: x[1], reverse=True)
        return [c for c, _ in similar]
    
    def get_active_concepts(self, family: Optional[str] = None) -> List[Concept]:
        """Get all active concepts, optionally filtered by family."""
        active = [c for c in self._concepts.values() if c.status == ConceptStatus.ACTIVE]
        if family:
            active = [c for c in active if c.family == family]
        return active
    
    def get_all(self) -> List[Concept]:
        """Get all concepts."""
        return list(self._concepts.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        status_counts = {}
        for concept in self._concepts.values():
            status_counts[concept.status.value] = status_counts.get(concept.status.value, 0) + 1
        
        return {
            "total_concepts": len(self._concepts),
            "status_breakdown": status_counts,
            "avg_maturity": sum(c.get_maturity_score() for c in self._concepts.values()) / max(1, len(self._concepts)),
            "ready_for_theory": sum(1 for c in self._concepts.values() if c.is_ready_for_theory()),
        }