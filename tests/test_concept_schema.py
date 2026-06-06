"""
Tests for Concept Object Schema — GENESIS
==========================================
"""

import pytest
from datetime import datetime, timedelta
from virtual_genesis.core.concept_schema import (
    Concept,
    ConceptStatus,
    ConceptSignature,
    ConceptEvidence,
    ConceptActivationContext,
    SemanticDimension,
    ConceptRegistry,
)


class TestConceptSignature:
    """Tests for ConceptSignature."""
    
    def test_signature_creation(self):
        """Test basic signature creation."""
        sig = ConceptSignature(
            primary_dimension=SemanticDimension.COMPARISON,
            secondary_dimensions={SemanticDimension.ANALYSIS},
            semantic_constraints={"must compare"},
            expected_outcome_type="comparison_result"
        )
        
        assert sig.primary_dimension == SemanticDimension.COMPARISON
        assert SemanticDimension.ANALYSIS in sig.secondary_dimensions
        assert "must compare" in sig.semantic_constraints
    
    def test_signature_overlap_same(self):
        """Test that identical signatures have maximum overlap."""
        sig1 = ConceptSignature(
            primary_dimension=SemanticDimension.COMPARISON,
            secondary_dimensions={SemanticDimension.ANALYSIS},
            semantic_constraints={"must compare", "must evaluate"}
        )
        sig2 = ConceptSignature(
            primary_dimension=SemanticDimension.COMPARISON,
            secondary_dimensions={SemanticDimension.ANALYSIS},
            semantic_constraints={"must compare", "must evaluate"}
        )
        
        overlap = sig1.compute_overlap(sig2)
        assert overlap > 0.9, f"Same signatures should have overlap > 0.9, got {overlap}"
    
    def test_signature_overlap_different(self):
        """Test that different signatures have lower overlap."""
        sig1 = ConceptSignature(
            primary_dimension=SemanticDimension.COMPARISON,
            semantic_constraints={"must compare"}
        )
        sig2 = ConceptSignature(
            primary_dimension=SemanticDimension.GENERATION,
            semantic_constraints={"must create"}
        )
        
        overlap = sig1.compute_overlap(sig2)
        assert overlap < 0.3, f"Different signatures should have overlap < 0.3, got {overlap}"
    
    def test_signature_overlap_partial(self):
        """Test partial overlap between signatures."""
        sig1 = ConceptSignature(
            primary_dimension=SemanticDimension.COMPARISON,
            secondary_dimensions={SemanticDimension.ANALYSIS},
            semantic_constraints={"must compare"}
        )
        sig2 = ConceptSignature(
            primary_dimension=SemanticDimension.COMPARISON,
            secondary_dimensions={SemanticDimension.SYNTHESIS},  # Different secondary
            semantic_constraints={"must evaluate"}  # Different constraints
        )
        
        # Primary matches, but secondary and constraints differ
        overlap = sig1.compute_overlap(sig2)
        assert 0.3 < overlap < 0.7, f"Partial overlap should be between 0.3 and 0.7, got {overlap}"


class TestConceptEvidence:
    """Tests for ConceptEvidence."""
    
    def test_evidence_creation(self):
        """Test evidence initialization."""
        evidence = ConceptEvidence(
            success_cases=["task1", "task2"],
            failure_cases=["task3"],
            success_pattern="Clear comparison with evidence",
            failure_pattern="Missing evidence"
        )
        
        assert evidence.total_cases == 3
        assert evidence.success_rate == 2/3
        assert evidence.failure_rate == 1/3
    
    def test_evidence_empty(self):
        """Test empty evidence."""
        evidence = ConceptEvidence()
        
        assert evidence.total_cases == 0
        assert evidence.success_rate == 0.0


class TestConcept:
    """Tests for Concept object."""
    
    def test_concept_creation(self):
        """Test basic concept creation."""
        sig = ConceptSignature(
            primary_dimension=SemanticDimension.COMPARISON,
            semantic_constraints={"must compare"}
        )
        
        concept = Concept(
            name="Comparison Contrast",
            signature=sig,
            family="comparison",
            creation_trigger="Task requiring comparison"
        )
        
        assert concept.name == "Comparison Contrast"
        assert concept.status == ConceptStatus.EMBRYONIC
        assert concept.activation_count == 0
    
    def test_concept_activation(self):
        """Test concept activation recording."""
        concept = Concept(
            name="Test Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
            family="comparison"
        )
        
        context = ConceptActivationContext(
            task_id="task_123",
            task_description="Compare A and B",
            task_family="comparison",
            activation_timestamp=datetime.now(),
            grounding_score=0.75,
            was_successful=True
        )
        
        concept.record_activation(context)
        
        assert concept.activation_count == 1
        assert concept.last_activated_at is not None
        assert "task_123" in concept.evidence.success_cases
    
    def test_concept_should_activate(self):
        """Test activation decision."""
        concept = Concept(
            name="Comparison Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
            family="comparison"
        )
        
        task_sig = ConceptSignature(primary_dimension=SemanticDimension.COMPARISON)
        
        should_activate, score = concept.should_activate_for("comparison", task_sig)
        
        assert should_activate is True
        assert score > 0.0
    
    def test_concept_should_not_activate_wrong_family(self):
        """Test that concepts don't activate for wrong families."""
        concept = Concept(
            name="Comparison Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
            family="comparison"
        )
        
        task_sig = ConceptSignature(primary_dimension=SemanticDimension.GENERATION)
        
        should_activate, score = concept.should_activate_for("generation", task_sig)
        
        assert should_activate is False
    
    def test_concept_maturity_score(self):
        """Test maturity score calculation."""
        concept = Concept(
            name="Mature Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
            family="comparison"
        )
        
        # Add activations
        for i in range(10):
            concept.record_activation(ConceptActivationContext(
                task_id=f"task_{i}",
                task_description="Test",
                task_family="comparison",
                activation_timestamp=datetime.now() - timedelta(days=i),
                grounding_score=0.8,
                was_successful=True
            ))
        
        maturity = concept.get_maturity_score()
        
        assert 0.0 <= maturity <= 1.0
        assert maturity > 0.5, f"Mature concept should have maturity > 0.5, got {maturity}"
    
    def test_concept_ready_for_theory(self):
        """Test theory readiness check."""
        concept = Concept(
            name="Theory-Ready Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
            family="comparison"
        )
        
        # Add enough successful cases
        for i in range(6):
            concept.record_activation(ConceptActivationContext(
                task_id=f"task_{i}",
                task_description="Test",
                task_family="comparison",
                activation_timestamp=datetime.now(),
                grounding_score=0.8,
                was_successful=True
            ))
        
        ready = concept.is_ready_for_theory()
        
        assert ready is True, "Concept with 6 successes should be ready for theory"
    
    def test_concept_not_ready_for_theory_insufficient_cases(self):
        """Test theory readiness requires sufficient cases."""
        concept = Concept(
            name="Not Ready Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
            family="comparison"
        )
        
        # Add only 2 cases
        for i in range(2):
            concept.record_activation(ConceptActivationContext(
                task_id=f"task_{i}",
                task_description="Test",
                task_family="comparison",
                activation_timestamp=datetime.now(),
                grounding_score=0.8,
                was_successful=True
            ))
        
        ready = concept.is_ready_for_theory()
        
        assert ready is False, "Concept with only 2 cases should not be ready for theory"
    
    def test_concept_to_dict(self):
        """Test concept serialization."""
        concept = Concept(
            name="Test Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
            family="comparison"
        )
        
        data = concept.to_dict()
        
        assert "id" in data
        assert "name" in data
        assert "primary_dimension" in data
        assert "status" in data
        assert "maturity_score" in data


class TestConceptRegistry:
    """Tests for ConceptRegistry."""
    
    def test_registry_creation(self):
        """Test registry initialization."""
        registry = ConceptRegistry()
        
        assert len(registry.get_all()) == 0
    
    def test_registry_register(self):
        """Test concept registration."""
        registry = ConceptRegistry()
        
        concept = Concept(
            name="New Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
            family="comparison"
        )
        
        result = registry.register(concept)
        
        assert result is True
        assert registry.get(concept.id) is not None
    
    def test_registry_reject_duplicate(self):
        """Test that duplicate concepts are rejected."""
        registry = ConceptRegistry()
        
        sig = ConceptSignature(
            primary_dimension=SemanticDimension.COMPARISON,
            secondary_dimensions={SemanticDimension.ANALYSIS},
            semantic_constraints={"must compare", "must evaluate"}
        )
        
        concept1 = Concept(name="Concept 1", signature=sig, family="comparison")
        concept2 = Concept(name="Concept 2", signature=sig, family="comparison")
        
        registry.register(concept1)
        result = registry.register(concept2)
        
        assert result is False, "Duplicate concept should be rejected"
    
    def test_registry_find_similar(self):
        """Test finding similar concepts."""
        registry = ConceptRegistry()
        
        comparison_concept = Concept(
            name="Comparison Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
            family="comparison"
        )
        generation_concept = Concept(
            name="Generation Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.GENERATION),
            family="generation"
        )
        
        registry.register(comparison_concept)
        registry.register(generation_concept)
        
        # Search for comparison-like concept
        search_sig = ConceptSignature(primary_dimension=SemanticDimension.COMPARISON)
        similar = registry.find_similar(search_sig, threshold=0.5)
        
        assert len(similar) >= 1
        assert comparison_concept in similar
        assert generation_concept not in similar
    
    def test_registry_get_active_concepts(self):
        """Test filtering active concepts."""
        registry = ConceptRegistry()
        
        active = Concept(
            name="Active Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
            family="comparison"
        )
        active.status = ConceptStatus.ACTIVE
        
        dormant = Concept(
            name="Dormant Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.SYNTHESIS),
            family="synthesis"
        )
        dormant.status = ConceptStatus.DORMANT
        
        registry.register(active)
        registry.register(dormant)
        
        active_list = registry.get_active_concepts()
        assert active in active_list
        assert dormant not in active_list
        
        # Filter by family
        comparison_active = registry.get_active_concepts(family="comparison")
        assert active in comparison_active
    
    def test_registry_statistics(self):
        """Test registry statistics."""
        registry = ConceptRegistry()
        
        for i in range(5):
            concept = Concept(
                name=f"Concept {i}",
                signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
                family="comparison"
            )
            if i < 3:
                concept.status = ConceptStatus.ACTIVE
            registry.register(concept)
        
        stats = registry.get_statistics()
        
        assert stats["total_concepts"] == 5
        assert stats["status_breakdown"]["active"] == 3
        assert "avg_maturity" in stats


class TestConceptLifecycle:
    """Tests for concept lifecycle transitions."""
    
    def test_embryonic_to_active(self):
        """Test embryonic concept becomes active."""
        concept = Concept(
            name="Growing Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
            family="comparison"
        )
        
        assert concept.status == ConceptStatus.EMBRYONIC
        
        # Add successful activations
        for i in range(3):
            concept.record_activation(ConceptActivationContext(
                task_id=f"task_{i}",
                task_description="Test",
                task_family="comparison",
                activation_timestamp=datetime.now(),
                grounding_score=0.8,
                was_successful=True
            ))
        
        assert concept.status == ConceptStatus.ACTIVE
    
    def test_concept_lineage(self):
        """Test concept lineage tracking."""
        parent = Concept(
            name="Parent Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
            family="comparison"
        )
        
        child = Concept(
            name="Child Concept",
            signature=ConceptSignature(primary_dimension=SemanticDimension.COMPARISON),
            family="comparison",
            lineage=parent.id
        )
        
        assert child.lineage == parent.id


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])