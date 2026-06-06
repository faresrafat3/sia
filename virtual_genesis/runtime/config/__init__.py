"""
Configuration Module — GENESIS
================================
Centralized locked values and configuration constants.

All empirical anchors from PAPER.md are stored here.
DO NOT change these values without new run + F. authorization.
"""

from .locked_values import (
    LOCKED_VALUES,
    get_locked_value,
    get_evidence_dict,
    LockedValuesConfig,
)

__all__ = [
    "LOCKED_VALUES",
    "get_locked_value",
    "get_evidence_dict",
    "LockedValuesConfig",
]
