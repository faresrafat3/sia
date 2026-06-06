"""
Value Computation Module — GENESIS
====================================
Implements the ACTUAL computation of Cognitive Economy value functions.

Before this module, VoC/VoI/VoV/VoA etc. were philosophical names.
Now they are computable functions with real numbers.

From Cognitive Economy Theory §12:
    Expected Cognitive Return = 
        Immediate Utility Gain + 
        Future Reuse Gain + 
        Learning Gain - 
        Cost - 
        Delay Penalty - 
        Noise Risk

This module computes each term.
"""

from .value_functions import (
    ValueOfComputation,
    ValueOfInformation,
    ValueOfVerification,
    ValueOfAbstraction,
    ValueOfReuse,
    CognitiveReturnCalculator,
    CostTracker,
    get_cognitive_return_calculator,
)

__all__ = [
    "ValueOfComputation",
    "ValueOfInformation",
    "ValueOfVerification",
    "ValueOfAbstraction",
    "ValueOfReuse",
    "CognitiveReturnCalculator",
    "CostTracker",
    "get_cognitive_return_calculator",
]
