"""
Cognitive Bridge — GENESIS Orchestrator
========================================
Bridge between the Orchestrator (real LLM agent) and Virtual-GENESIS cognitive pipeline.

This addresses the CRITICAL gap: Orchestrator works blindfolded without concepts,
memory, and theory guidance.

The bridge ensures:
1. Concepts are used to guide prompt construction
2. Memory context is injected into LLM calls
3. Theory-informed reasoning is applied
4. Economy decisions are informed by real task complexity
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re


class BridgeMode(Enum):
    """Operating modes for the cognitive bridge."""
    DISABLED = "disabled"           # No cognitive enhancement
    CONCEPTS_ONLY = "concepts_only" # Only concept-guided prompting
    FULL = "full"                   # Full cognitive pipeline integration


@dataclass
class CognitiveContext:
    """
    Context for a cognitive operation, including all relevant artifacts.
    """
    # Task information
    task_id: str = ""
    task_description: str = ""
    task_family: str = ""
    
    # Active concepts for this task
    active_concepts: List[Dict[str, Any]] = field(default_factory=list)
    
    # Memory context
    relevant_memories: List[Dict[str, Any]] = field(default_factory=list)
    
    # Theory guidance
    applicable_theories: List[Dict[str, Any]] = field(default_factory=list)
    
    # Economy decision
    tier_recommended: str = "standard"  # standard or premium
    complexity_score: float = 0.0
    
    # Verification hints
    expected_outcome: str = ""
    verification_criteria: List[str] = field(default_factory=list)


@dataclass
class CognitivePrompt:
    """
    A prompt enhanced with cognitive artifacts.
    """
    system_prompt: str = ""
    user_prompt: str = ""
    concept_injection: str = ""
    memory_context: str = ""
    theory_guidance: str = ""
    verification_hint: str = ""
    
    def to_messages(self) -> List[Dict[str, str]]:
        """Convert to OpenAI-style message format."""
        messages = []
        
        if self.concept_injection or self.memory_context or self.theory_guidance:
            system_with_context = self.system_prompt + "\n\n" + self._build_context_section()
            messages.append({"role": "system", "content": system_with_context})
        else:
            messages.append({"role": "system", "content": self.system_prompt})
        
        if self.verification_hint:
            enhanced_user = self.user_prompt + "\n\n" + self.verification_hint
            messages.append({"role": "user", "content": enhanced_user})
        else:
            messages.append({"role": "user", "content": self.user_prompt})
        
        return messages
    
    def _build_context_section(self) -> str:
        """Build the cognitive context section for system prompt."""
        parts = []
        
        if self.concept_injection:
            parts.append(f"## Active Concepts\n{self.concept_injection}")
        
        if self.memory_context:
            parts.append(f"## Relevant Memory\n{self.memory_context}")
        
        if self.theory_guidance:
            parts.append(f"## Theory Guidance\n{self.theory_guidance}")
        
        if parts:
            return "\n\n".join(parts)
        return ""


class CognitiveBridge:
    """
    Bridge between Orchestrator and Virtual-GENESIS cognitive pipeline.
    
    This is the core integration point that makes the cognitive artifacts
    (concepts, memory, theories) usable by the real LLM.
    """
    
    def __init__(
        self,
        mode: BridgeMode = BridgeMode.DISABLED,
        include_concepts: bool = True,
        include_memory: bool = True,
        include_theories: bool = True,
        include_verification: bool = True,
    ):
        self.mode = mode
        self.include_concepts = include_concepts
        self.include_memory = include_memory
        self.include_theories = include_theories
        self.include_verification = include_verification
        
        # Cache for concepts/memory (in real impl, would connect to actual systems)
        self._concept_cache: Dict[str, List[Dict]] = {}
        self._memory_cache: Dict[str, List[Dict]] = {}
    
    def build_cognitive_context(
        self,
        task_description: str,
        task_family: str,
        task_id: str = "",
    ) -> CognitiveContext:
        """
        Build cognitive context for a task.
        
        This connects to Virtual-GENESIS components:
        - Concept Engine: for selecting relevant concepts
        - Memory OS: for retrieving relevant memories
        - Theory Runtime: for applicable theories
        - Economy Control: for tier decisions
        """
        context = CognitiveContext(
            task_id=task_id,
            task_description=task_description,
            task_family=task_family,
        )
        
        if self.mode == BridgeMode.DISABLED:
            return context
        
        # Get concepts for this task family
        if self.include_concepts:
            context.active_concepts = self._get_concepts_for_task(task_description, task_family)
            context.concept_injection = self._format_concepts(context.active_concepts)
        
        # Get relevant memories
        if self.include_memory:
            context.relevant_memories = self._get_relevant_memories(task_description, task_family)
            context.memory_context = self._format_memory(context.relevant_memories)
        
        # Get applicable theories
        if self.include_theories:
            context.applicable_theories = self._get_theories_for_task(task_description, task_family)
            context.theory_guidance = self._format_theories(context.applicable_theories)
        
        # Estimate complexity for economy decision
        context.complexity_score = self._estimate_complexity(task_description, task_family)
        context.tier_recommended = "premium" if context.complexity_score > 0.6 else "standard"
        
        # Get verification hints
        if self.include_verification:
            context.verification_criteria = self._get_verification_criteria(task_family)
            context.verification_hint = self._format_verification_hint(context.verification_criteria)
            context.expected_outcome = self._infer_expected_outcome(task_family)
        
        return context
    
    def enhance_prompt(
        self,
        base_system_prompt: str,
        base_user_prompt: str,
        context: CognitiveContext,
    ) -> CognitivePrompt:
        """
        Enhance a prompt with cognitive artifacts.
        
        This is the main entry point for the orchestrator.
        """
        prompt = CognitivePrompt(
            system_prompt=base_system_prompt,
            user_prompt=base_user_prompt,
        )
        
        if self.mode == BridgeMode.DISABLED:
            return prompt
        
        # Inject concepts
        if context.concept_injection:
            prompt.concept_injection = context.concept_injection
        
        # Inject memory
        if context.memory_context:
            prompt.memory_context = context.memory_context
        
        # Inject theory guidance
        if context.theory_guidance:
            prompt.theory_guidance = context.theory_guidance
        
        # Inject verification hint
        if context.verification_hint:
            prompt.verification_hint = context.verification_hint
        
        return prompt
    
    def _get_concepts_for_task(
        self,
        task_description: str,
        task_family: str,
    ) -> List[Dict[str, Any]]:
        """
        Get concepts from Virtual-GENESIS concept engine.
        
        In real implementation, this would call the actual concept engine.
        For now, it uses cached concepts based on family.
        """
        # Check cache first
        cache_key = f"{task_family}"
        if cache_key in self._concept_cache:
            return self._concept_cache[cache_key]
        
        # Default concepts by family (in real impl, would come from concept engine)
        default_concepts = {
            "comparison": [
                {
                    "name": "Evidence Sufficiency Contrast",
                    "description": "When comparing options, ensure each has sufficient evidence.",
                    "activation_hint": "For tasks asking to compare, evaluate, or judge between options."
                },
                {
                    "name": "Dimensional Comparison",
                    "description": "Compare across multiple dimensions, not just one.",
                    "activation_hint": "When comparing requires multi-dimensional analysis."
                }
            ],
            "synthesis": [
                {
                    "name": "Information Integration",
                    "description": "Combine information from multiple sources coherently.",
                    "activation_hint": "For tasks requiring synthesis of multiple sources."
                }
            ],
            "procedure": [
                {
                    "name": "Stepwise Execution",
                    "description": "Follow procedure steps in correct order.",
                    "activation_hint": "For tasks requiring executing a procedure."
                }
            ]
        }
        
        concepts = default_concepts.get(task_family, [])
        self._concept_cache[cache_key] = concepts
        return concepts
    
    def _get_relevant_memories(
        self,
        task_description: str,
        task_family: str,
    ) -> List[Dict[str, Any]]:
        """Get relevant memories from Memory OS."""
        # In real implementation, would query Memory OS
        # For now, return empty (placeholder)
        return []
    
    def _get_theories_for_task(
        self,
        task_description: str,
        task_family: str,
    ) -> List[Dict[str, Any]]:
        """Get applicable theories from Theory Runtime."""
        # In real implementation, would query Theory Runtime
        # For now, return empty (placeholder)
        return []
    
    def _estimate_complexity(
        self,
        task_description: str,
        task_family: str,
    ) -> float:
        """
        Estimate task complexity for economy decision.
        
        Uses heuristic based on description length and complexity indicators.
        """
        base_complexity = 0.3  # Default base
        
        # Length factor
        if len(task_description) > 200:
            base_complexity += 0.1
        if len(task_description) > 500:
            base_complexity += 0.1
        
        # Complexity indicators
        complex_words = [
            "analyze", "evaluate", "compare", "synthesize", "design",
            "develop", "create", "optimize", "improve", "investigate"
        ]
        word_count = sum(1 for word in complex_words if word in task_description.lower())
        base_complexity += min(0.3, word_count * 0.05)
        
        # Family-based adjustment
        family_complexity = {
            "comparison": 0.2,
            "synthesis": 0.4,
            "procedure": 0.1,
            "analysis": 0.5,
            "generation": 0.6,
            "planning": 0.7,
        }
        base_complexity += family_complexity.get(task_family, 0.2)
        
        return min(1.0, base_complexity)
    
    def _get_verification_criteria(self, task_family: str) -> List[str]:
        """Get verification criteria for task family."""
        criteria_map = {
            "comparison": [
                "Answer should explicitly compare the options",
                "Should address key differentiating factors",
                "Should provide clear conclusion or recommendation"
            ],
            "synthesis": [
                "Should integrate information from multiple sources",
                "Should maintain coherence across sources",
                "Should add value beyond mere concatenation"
            ],
            "procedure": [
                "Should list steps in correct order",
                "Should be actionable and complete",
                "Should cover all necessary steps"
            ]
        }
        return criteria_map.get(task_family, [])
    
    def _format_concepts(self, concepts: List[Dict[str, Any]]) -> str:
        """Format concepts for injection into prompt."""
        if not concepts:
            return ""
        
        lines = []
        for concept in concepts:
            lines.append(f"### {concept['name']}")
            lines.append(f"{concept.get('description', '')}")
            if concept.get('activation_hint'):
                lines.append(f"When to use: {concept['activation_hint']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_memory(self, memories: List[Dict[str, Any]]) -> str:
        """Format memories for injection into prompt."""
        if not memories:
            return ""
        
        lines = ["### Relevant Past Experiences"]
        for memory in memories[:3]:  # Limit to 3 most relevant
            lines.append(f"- {memory.get('summary', memory.get('description', ''))}")
        
        return "\n".join(lines)
    
    def _format_theories(self, theories: List[Dict[str, Any]]) -> str:
        """Format theories for injection into prompt."""
        if not theories:
            return ""
        
        lines = ["### Applicable Principles"]
        for theory in theories[:2]:  # Limit to 2 most relevant
            lines.append(f"- {theory.get('name', '')}: {theory.get('description', '')}")
        
        return "\n".join(lines)
    
    def _format_verification_hint(self, criteria: List[str]) -> str:
        """Format verification criteria as a hint."""
        if not criteria:
            return ""
        
        lines = ["\n## Verification Checklist"]
        for i, criterion in enumerate(criteria, 1):
            lines.append(f"{i}. {criterion}")
        
        return "\n".join(lines)
    
    def _infer_expected_outcome(self, task_family: str) -> str:
        """Infer expected outcome type from task family."""
        outcomes = {
            "comparison": "A clear comparison with conclusion or recommendation",
            "synthesis": "An integrated summary that adds value",
            "procedure": "A step-by-step plan that is actionable",
            "analysis": "A structured breakdown with insights",
            "generation": "New content that meets the requirements",
            "classification": "Correct categorization with reasoning",
        }
        return outcomes.get(task_family, "A complete and accurate response")


class OrchestratorCognitiveIntegration:
    """
    Integration layer for connecting orchestrator with cognitive pipeline.
    
    This provides a clean API for the orchestrator to access cognitive features.
    """
    
    def __init__(self, bridge_mode: BridgeMode = BridgeMode.FULL):
        self.bridge = CognitiveBridge(mode=bridge_mode)
    
    def prepare_task(
        self,
        task_description: str,
        task_family: str,
        base_system_prompt: str,
        base_user_prompt: str,
        task_id: str = "",
    ) -> Tuple[List[Dict[str, str]], CognitiveContext]:
        """
        Prepare a task for execution with cognitive enhancement.
        
        Returns:
            (messages, context) - ready for LLM call
        """
        # Build cognitive context
        context = self.bridge.build_cognitive_context(
            task_description=task_description,
            task_family=task_family,
            task_id=task_id,
        )
        
        # Enhance prompt
        enhanced_prompt = self.bridge.enhance_prompt(
            base_system_prompt=base_system_prompt,
            base_user_prompt=base_user_prompt,
            context=context,
        )
        
        # Convert to messages
        messages = enhanced_prompt.to_messages()
        
        return messages, context
    
    def get_tier_recommendation(self, context: CognitiveContext) -> str:
        """Get tier recommendation based on cognitive complexity."""
        return context.tier_recommended
    
    def record_outcome(
        self,
        context: CognitiveContext,
        success: bool,
        output: str,
    ) -> None:
        """
        Record the outcome of a task for learning.
        
        This feeds back into the concept engine and memory system.
        """
        # In real implementation, would update:
        # - Concept activation history
        # - Memory with new experience
        # - Theory validation
        pass