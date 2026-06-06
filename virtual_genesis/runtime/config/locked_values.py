"""
Locked Values Configuration — GENESIS
=======================================
Single source of truth for all empirical anchors locked in PAPER.md.

⚠️  DO NOT change any value in this file without:
    1. A new benchmark run authorized by Fares
    2. Fares's explicit authorization to update

These values are referenced in:
    - PAPER.md §5 (Experiments), §6 (Results), §7 (Analysis)
    - CONTRIBUTION_LEDGER.md §5 (locked numbers)
    - PROJECT_README.md §4 (LOCKED table)
    - AGENT_OPERATING_MANUAL.md §5 (locked numbers)

Source: run_57 (pure baseline + GENESIS post-fix), run_58 (A3 ablation)
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class LockedValuesConfig:
    """
    Immutable configuration holding all locked empirical values.

    Frozen to prevent accidental mutation. Every field corresponds to
    a value in PAPER.md that has been measured and locked.
    """

    # ─── Model Card ────────────────────────────────────────────
    gpt_oss_120b_gpqa_diamond_official: float = 80.1  # NVIDIA model card

    # ─── Run 57 (n=20, GPQA Diamond 20-question subset) ────────
    pure_baseline_accuracy: float = 75.00             # No pipeline, direct prompt
    genesis_post_fix_gen1: float = 65.00              # GENESIS Generation 1
    genesis_post_fix_gen2: float = 65.00              # GENESIS Generation 2
    genesis_pre_fix_run53: float = 30.30              # Run 53, buggy (n=198)

    # ─── Run 58 (A3 no_pipeline ablation) ──────────────────────
    a3_no_pipeline_gen1: float = 70.00                # Without pipeline, Gen 1
    a3_no_pipeline_gen2: float = 60.00                # Without pipeline, Gen 2

    # ─── Reasoning Saturation (run_57 analysis) ────────────────
    median_correct_tokens: int = 989                  # Median tokens for correct answers
    median_incorrect_tokens: int = 6836               # Median tokens for incorrect answers

    # ─── Empty Content Rate (run_57) ──────────────────────────
    genesis_empty_content_rate: float = 0.35           # 7/20 responses were empty
    baseline_empty_content_rate: float = 0.35          # Same model, baseline condition

    # ─── LEAP Comparison ──────────────────────────────────────
    leap_putnam_2025_improvement: int = 100            # 0% → 100% on Putnam 2025
    leap_vs_genesis_gap: int = 110                     # Points gap

    # ─── External Validation ──────────────────────────────────
    t594_length_accuracy_correlation: float = -0.54    # Chen et al. GPT-OSS + GPQA

    # ─── Project Statistics ───────────────────────────────────
    sample_size: int = 20                              # n=20 for all locked runs
    epistemic_artifacts_count: int = 11                # 4 theories + 1 phil + 4 thefts + 2 ideas
    foundational_docs_total: int = 122                 # GENESIS_*_AR.md files
    foundational_docs_re_read: int = 9                 # Re-read in S12 + S13

    def get(self, key: str, default: Any = None) -> Any:
        """Get a locked value by name."""
        return getattr(self, key, default)


# ─── Singleton Instance ────────────────────────────────────────────
LOCKED_VALUES = LockedValuesConfig()


def get_locked_value(key: str, default: Any = None) -> Any:
    """
    Retrieve a locked empirical value by name.

    Usage:
        baseline = get_locked_value("pure_baseline_accuracy")  # 75.00
        sat_tokens = get_locked_value("median_correct_tokens") # 989

    Raises AttributeError if key doesn't exist and no default provided.
    """
    value = getattr(LOCKED_VALUES, key, default)
    if value is None and not hasattr(LOCKED_VALUES, key):
        raise AttributeError(
            f"No locked value named '{key}'. "
            f"Available: {[f.name for f in LOCKED_VALUES.__dataclass_fields__.values()]}"
        )
    return value


def get_evidence_dict() -> Dict[str, Any]:
    """
    Build evidence dictionary for theory testing.

    Returns all locked values as a flat dict, suitable for passing
    to TheoryExecutable.test() and evaluate_all_theories().
    """
    return {
        # T07 evidence
        "standard_gen1_accuracy": LOCKED_VALUES.genesis_post_fix_gen1,
        "no_pipeline_gen1_accuracy": LOCKED_VALUES.a3_no_pipeline_gen1,

        # T08 evidence
        "gen1_accuracy": LOCKED_VALUES.genesis_post_fix_gen1,
        "gen2_accuracy": LOCKED_VALUES.genesis_post_fix_gen2,
        "a3_gen1_accuracy": LOCKED_VALUES.a3_no_pipeline_gen1,
        "a3_gen2_accuracy": LOCKED_VALUES.a3_no_pipeline_gen2,

        # T10 evidence
        "median_correct_tokens": LOCKED_VALUES.median_correct_tokens,
        "median_incorrect_tokens": LOCKED_VALUES.median_incorrect_tokens,
        "genesis_empty_content_rate": LOCKED_VALUES.genesis_empty_content_rate,
        "baseline_empty_content_rate": LOCKED_VALUES.baseline_empty_content_rate,

        # LEAP evidence
        "leap_improvement": LOCKED_VALUES.leap_putnam_2025_improvement,
        "leap_genesis_gap": LOCKED_VALUES.leap_vs_genesis_gap,

        # External validation
        "t594_correlation": LOCKED_VALUES.t594_length_accuracy_correlation,

        # Model card
        "model_card_accuracy": LOCKED_VALUES.gpt_oss_120b_gpqa_diamond_official,

        # Sample size
        "sample_size": LOCKED_VALUES.sample_size,
    }
