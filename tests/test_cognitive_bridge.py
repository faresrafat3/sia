"""
Tests for Cognitive Bridge — GENESIS
=====================================
"""

import pytest
from genesis.cognitive_bridge import (
    CognitiveBridge,
    BridgeMode,
    CognitiveContext,
    CognitivePrompt,
    OrchestratorCognitiveIntegration,
)


class TestCognitiveBridge:
    """Tests for CognitiveBridge."""
    
    def test_bridge_disabled_mode(self):
        """Test that disabled bridge returns empty context."""
        bridge = CognitiveBridge(mode=BridgeMode.DISABLED)
        
        context = bridge.build_cognitive_context(
            task_description="Test task",
            task_family="comparison",
            task_id="test_123"
        )
        
        assert context.task_description == "Test task"
        assert context.task_family == "comparison"
        # Disabled mode should not populate concepts
        assert len(context.active_concepts) == 0
        # Tier should still be estimated even in disabled mode
        assert context.complexity_score >= 0
    
    def test_bridge_full_mode(self):
        """Test that full mode includes all cognitive artifacts."""
        bridge = CognitiveBridge(mode=BridgeMode.FULL)
        
        context = bridge.build_cognitive_context(
            task_description="Compare the efficiency of algorithm A and algorithm B",
            task_family="comparison",
            task_id="test_123"
        )
        
        # Should have concepts
        assert len(context.active_concepts) > 0
        assert context.concept_injection != ""
        
        # Should have complexity score
        assert context.complexity_score > 0
        assert context.tier_recommended in ["standard", "premium"]
        
        # Should have verification criteria
        assert len(context.verification_criteria) > 0
    
    def test_estimate_complexity(self):
        """Test complexity estimation."""
        bridge = CognitiveBridge(mode=BridgeMode.DISABLED)
        
        # Simple task
        simple = bridge._estimate_complexity("Compare A and B", "comparison")
        assert 0.0 <= simple <= 1.0
        
        # Complex task
        complex_desc = """
        Analyze the performance characteristics of multiple machine learning algorithms
        including their time complexity, space complexity, and practical runtime behavior
        on large datasets. Compare their efficiency across different problem sizes.
        """
        complex_task = bridge._estimate_complexity(complex_desc, "analysis")
        assert complex_task > simple, "Complex task should have higher complexity"
    
    def test_format_concepts(self):
        """Test concept formatting."""
        bridge = CognitiveBridge(mode=BridgeMode.DISABLED)
        
        concepts = [
            {
                "name": "Test Concept",
                "description": "A test concept for comparison tasks",
                "activation_hint": "Use when comparing options"
            }
        ]
        
        formatted = bridge._format_concepts(concepts)
        
        assert "Test Concept" in formatted
        assert "A test concept" in formatted
        assert "Use when comparing" in formatted
    
    def test_format_verification_hint(self):
        """Test verification hint formatting."""
        bridge = CognitiveBridge(mode=BridgeMode.DISABLED)
        
        criteria = [
            "Should explicitly compare options",
            "Should address key factors"
        ]
        
        hint = bridge._format_verification_hint(criteria)
        
        assert "Verification Checklist" in hint
        assert "Should explicitly compare" in hint
        assert "1." in hint or "①" in hint
    
    def test_infer_expected_outcome(self):
        """Test expected outcome inference."""
        bridge = CognitiveBridge(mode=BridgeMode.DISABLED)
        
        comparison_outcome = bridge._infer_expected_outcome("comparison")
        assert "comparison" in comparison_outcome.lower() or "compare" in comparison_outcome.lower()
        
        generation_outcome = bridge._infer_expected_outcome("generation")
        assert "new" in generation_outcome.lower() or "content" in generation_outcome.lower()


class TestCognitivePrompt:
    """Tests for CognitivePrompt."""
    
    def test_prompt_to_messages_empty(self):
        """Test empty prompt conversion."""
        prompt = CognitivePrompt(
            system_prompt="You are a helpful assistant.",
            user_prompt="Hello, how are you?"
        )
        
        messages = prompt.to_messages()
        
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
    
    def test_prompt_to_messages_with_context(self):
        """Test prompt with cognitive context."""
        prompt = CognitivePrompt(
            system_prompt="You are a helpful assistant.",
            user_prompt="Compare A and B",
            concept_injection="Use comparison concept",
            memory_context="Past similar task completed",
            theory_guidance="Apply evidence principle"
        )
        
        messages = prompt.to_messages()
        
        assert len(messages) == 2
        assert "Active Concepts" in messages[0]["content"]
        assert "Use comparison concept" in messages[0]["content"]
        assert "Relevant Memory" in messages[0]["content"]
    
    def test_prompt_to_messages_with_verification(self):
        """Test prompt with verification hint."""
        prompt = CognitivePrompt(
            system_prompt="You are a helpful assistant.",
            user_prompt="Compare A and B",
            verification_hint="Check: 1. Explicit comparison 2. Key factors"
        )
        
        messages = prompt.to_messages()
        
        assert len(messages) == 2
        assert "Check:" in messages[1]["content"] or "Verification" in messages[1]["content"]


class TestOrchestratorCognitiveIntegration:
    """Tests for OrchestratorCognitiveIntegration."""
    
    def test_prepare_task_disabled(self):
        """Test task preparation with disabled bridge."""
        integration = OrchestratorCognitiveIntegration(bridge_mode=BridgeMode.DISABLED)
        
        messages, context = integration.prepare_task(
            task_description="Test comparison task",
            task_family="comparison",
            base_system_prompt="You are an AI assistant.",
            base_user_prompt="Compare X and Y",
            task_id="task_1"
        )
        
        # Should return basic messages without enhancement
        assert len(messages) == 2
        assert "Compare X and Y" in messages[1]["content"]
    
    def test_prepare_task_full(self):
        """Test task preparation with full bridge."""
        integration = OrchestratorCognitiveIntegration(bridge_mode=BridgeMode.FULL)
        
        messages, context = integration.prepare_task(
            task_description="Compare the performance of machine learning algorithms",
            task_family="comparison",  # Use comparison which has default concepts
            base_system_prompt="You are an AI assistant.",
            base_user_prompt="Compare the following algorithms",
            task_id="task_2"
        )
        
        # Should have cognitive context
        assert len(context.active_concepts) > 0
        assert context.complexity_score > 0
        
        # Messages should be enhanced
        assert len(messages) >= 2
        # System prompt should include context
        assert "AI assistant" in messages[0]["content"]
    
    def test_get_tier_recommendation(self):
        """Test tier recommendation."""
        integration = OrchestratorCognitiveIntegration(bridge_mode=BridgeMode.FULL)
        
        context = CognitiveContext(
            task_description="Complex analysis task",
            task_family="analysis",
            complexity_score=0.8,
            tier_recommended="premium"
        )
        
        tier = integration.get_tier_recommendation(context)
        
        assert tier == "premium"
    
    def test_get_tier_recommendation_low_complexity(self):
        """Test tier recommendation for low complexity."""
        integration = OrchestratorCognitiveIntegration(bridge_mode=BridgeMode.FULL)
        
        context = CognitiveContext(
            task_description="Simple task",
            task_family="comparison",
            complexity_score=0.3,
            tier_recommended="standard"
        )
        
        tier = integration.get_tier_recommendation(context)
        
        assert tier == "standard"


class TestBridgeModeComparison:
    """Tests comparing different bridge modes."""
    
    def test_concepts_only_vs_full(self):
        """Test that concepts_only mode has fewer features than full."""
        concepts_bridge = CognitiveBridge(mode=BridgeMode.CONCEPTS_ONLY)
        full_bridge = CognitiveBridge(mode=BridgeMode.FULL)
        
        task_desc = "Compare A and B with analysis"
        
        concepts_context = concepts_bridge.build_cognitive_context(
            task_description=task_desc,
            task_family="comparison"
        )
        
        full_context = full_bridge.build_cognitive_context(
            task_description=task_desc,
            task_family="comparison"
        )
        
        # Full mode should have at least as much content
        assert len(full_context.concept_injection) >= len(concepts_context.concept_injection)
        assert len(full_context.verification_criteria) >= len(concepts_context.verification_criteria)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])