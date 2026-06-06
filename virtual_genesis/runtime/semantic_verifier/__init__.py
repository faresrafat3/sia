"""
Semantic Verifier Module — GENESIS
====================================
The missing "Lean Compiler" equivalent for GENESIS.

LEAP succeeds because the Lean compiler provides:
    - Binary correctness (pass/fail)
    - Localized error messages
    - Deterministic verification
    - Automatic regression detection

GENESIS needs an equivalent for scientific MCQ reasoning.
This module provides:
    1. ReasoningPathValidator — checks internal consistency of reasoning
    2. ConfidenceCalibrator — aligns confidence with actual accuracy
    3. TheoryFalsificationEngine — tests theories against data
    4. SemanticVerifier — the unified verification interface
"""

from .verifier import (
    VerificationVerdict,
    ReasoningPathValidator,
    ConfidenceCalibrator,
    TheoryFalsificationEngine,
    SemanticVerifier,
    get_semantic_verifier,
)

__all__ = [
    "VerificationVerdict",
    "ReasoningPathValidator",
    "ConfidenceCalibrator",
    "TheoryFalsificationEngine",
    "SemanticVerifier",
    "get_semantic_verifier",
]
