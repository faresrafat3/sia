"""
GENESIS Enhanced Pipeline Bridge — Layer 4
==========================================
Connects the orchestrator's outer loop to the inner virtual_genesis
enhanced pipeline signals that were previously built but never wired.

What was built but disconnected:
  - enhanced_pipeline/enhanced_run.py → LadderAscent + SemanticVerifier
    + ValueComputation + TheoryTesting
  - All 4 produce rich signals per-task — none of them reached feedback agent

What this bridge does:
  1. Reads enhanced pipeline signals from agent_execution artifacts
  2. Builds a structured LadderState summary per generation
  3. Saves ladder_state.json to gen_dir
  4. Produces a feedback section injected into Feedback Agent prompt
  5. Enables Enhanced Pipeline in the META_AGENT_PROMPT template

Architecture decision:
  We do NOT re-run the enhanced pipeline here — the target agent already
  ran it internally. We extract its outputs from the artifacts it left.
  This avoids double-computation and preserves the isolation principle.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ─── Constants ─────────────────────────────────────────────────────────────────
LADDER_STATE_FILENAME = "ladder_state.json"
ENHANCED_SIGNALS_FILENAME = "enhanced_signals.json"

# Ladder levels mapping (from LadderAscentEngine)
LADDER_LEVELS = {
    0: "FOUNDATION",
    1: "PATTERN_RECOGNITION",
    2: "THEORY_FORMATION",
    3: "PREDICTIVE_POWER",
    4: "PARADIGM_MASTERY",
}


# ─── Data Classes ──────────────────────────────────────────────────────────────
@dataclass
class LadderStateSummary:
    """
    Summary of LadderAscent state extracted from enhanced pipeline output.
    Sent to Feedback Agent to guide next-generation strategy.
    """
    gen: int
    task_family: str
    current_level: str           # FOUNDATION → PARADIGM_MASTERY
    current_level_int: int       # 0-4
    entropy: float               # low=stable, high=unstable
    transition_possible: bool    # should we try to advance?
    evidence_count: int          # total evidence seen
    transition_count: int        # how many level transitions happened
    semantic_verdict: str        # VERIFIED | UNCERTAIN | REJECTED
    semantic_score: float        # 0-1
    value_cognitive_return: float  # economic signal: is this tier worth it?
    theory_results: dict         # which theories hold/fail
    is_enhanced: bool = True
    extracted_from: str = ""     # which file this came from

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> "LadderStateSummary":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    @classmethod
    def empty(cls, gen: int) -> "LadderStateSummary":
        """Placeholder when no enhanced signals found."""
        return cls(
            gen=gen, task_family="unknown",
            current_level="FOUNDATION", current_level_int=0,
            entropy=0.0, transition_possible=False,
            evidence_count=0, transition_count=0,
            semantic_verdict="UNKNOWN", semantic_score=0.0,
            value_cognitive_return=0.0, theory_results={},
            is_enhanced=False, extracted_from="none",
        )

    def to_feedback_section(self) -> str:
        """
        Format as section for Feedback Agent prompt.
        Tells the agent: here's what the internal pipeline observed.
        """
        if not self.is_enhanced:
            return ""

        lines = [
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "🔬 ENHANCED PIPELINE SIGNALS (Ladder + Semantics + Value)",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"Ladder Level: {self.current_level} ({self.current_level_int}/4)",
            f"Entropy: {self.entropy:.3f} — {'UNSTABLE (consider regime change)' if self.entropy > 0.7 else 'stable'}",
            f"Transition possible: {'YES — agent is ready to advance to next level' if self.transition_possible else 'NO — consolidate current level'}",
            f"Evidence count: {self.evidence_count} | Transitions so far: {self.transition_count}",
            "",
            f"Semantic Verification: {self.semantic_verdict} (score: {self.semantic_score:.2f})",
            f"Cognitive Return: {self.value_cognitive_return:.3f} — {'positive (tier justified)' if self.value_cognitive_return > 0 else 'negative (reconsider tier)'}",
        ]

        if self.theory_results:
            passed = [t for t, v in self.theory_results.items() if v.get("holds", False)]
            failed = [t for t, v in self.theory_results.items() if not v.get("holds", False)]
            if passed:
                lines.append(f"Theories holding: {', '.join(passed[:3])}")
            if failed:
                lines.append(f"Theories failing: {', '.join(failed[:3])}")

        lines += [
            "",
            "WHAT THIS MEANS FOR NEXT GENERATION:",
        ]

        if self.current_level_int == 0:
            lines.append("  → Agent is at FOUNDATION level. Focus on getting basic outputs right first.")
        elif self.current_level_int == 1:
            lines.append("  → Agent recognizes patterns. Push it to form explicit theories, not just patterns.")
        elif self.current_level_int == 2:
            lines.append("  → Agent forms theories. Test them with edge cases in next gen.")
        elif self.current_level_int >= 3:
            lines.append("  → Agent has predictive power. Challenge with adversarial cases.")

        if self.entropy > 0.7:
            lines.append("  → HIGH ENTROPY: Consider paradigm fork — current approach is unstable.")
        if self.semantic_verdict == "REJECTED":
            lines.append("  → Semantic verification REJECTED: Agent's reasoning is internally inconsistent.")
        if self.value_cognitive_return < 0:
            lines.append("  → Negative cognitive return: Current tier costs more than it's worth. Downgrade tier.")

        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return "\n".join(lines)


# ─── Signal Extraction ─────────────────────────────────────────────────────────
def extract_enhanced_signals_from_gen(gen_dir: str) -> dict:
    """
    Extract enhanced pipeline signals from what the target agent left behind.

    Searches for:
      1. agent_execution.json — may contain enhanced pipeline result
      2. agent_execution/ directory — multi-trajectory runs
      3. enhanced_signals.json — explicit enhanced output (future)

    Returns raw signal dict or {}.
    """
    # Check for explicit enhanced signals file first
    enhanced_path = os.path.join(gen_dir, ENHANCED_SIGNALS_FILENAME)
    if os.path.exists(enhanced_path):
        try:
            with open(enhanced_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not read {enhanced_path}: {e}")

    # Try agent_execution.json
    exec_path = os.path.join(gen_dir, "agent_execution.json")
    if os.path.exists(exec_path):
        try:
            with open(exec_path, encoding="utf-8") as f:
                data = json.load(f)
            # Check if it has enhanced pipeline fields
            if "ladder_tracking" in data or "semantic_verification" in data:
                return data
        except Exception:
            pass

    # Try multi-trajectory: pick first execution
    exec_dir = os.path.join(gen_dir, "agent_execution")
    if os.path.isdir(exec_dir):
        for fname in sorted(os.listdir(exec_dir)):
            if fname.endswith(".json"):
                try:
                    with open(os.path.join(exec_dir, fname), encoding="utf-8") as f:
                        data = json.load(f)
                    if "ladder_tracking" in data or "semantic_verification" in data:
                        return data
                except Exception:
                    pass

    return {}


def build_ladder_state_summary(
    gen_dir: str,
    gen: int,
    signals: dict | None = None,
) -> LadderStateSummary:
    """
    Build LadderStateSummary from extracted signals.
    Falls back to empty summary if no enhanced signals found.
    """
    if signals is None:
        signals = extract_enhanced_signals_from_gen(gen_dir)

    if not signals:
        return LadderStateSummary.empty(gen)

    ladder = signals.get("ladder_tracking", {})
    semantic = signals.get("semantic_verification", {})
    value = signals.get("value_computation", {})
    theory = signals.get("theory_testing", {})

    # Extract task family
    task = signals.get("task", {})
    task_family = task.get("task_family", "unknown")

    # Cognitive return: primary value signal
    cog_return_data = value.get("cognitive_return", {})
    cog_return = 0.0
    if isinstance(cog_return_data, dict):
        cog_return = float(cog_return_data.get("net_return", 0.0))
    elif isinstance(cog_return_data, (int, float)):
        cog_return = float(cog_return_data)

    # Semantic score
    sem_score = 0.0
    sem_verdict = "UNKNOWN"
    if isinstance(semantic, dict):
        sem_score = float(semantic.get("verification_score", 0.0))
        sem_verdict = semantic.get("verdict", "UNKNOWN")

    # Theory results
    theory_results = {}
    if isinstance(theory, dict):
        for name, result in theory.items():
            if isinstance(result, dict):
                theory_results[name] = result

    level_int = int(ladder.get("current_level_int", 0))
    level_label = ladder.get("current_level", LADDER_LEVELS.get(level_int, "FOUNDATION"))

    summary = LadderStateSummary(
        gen=gen,
        task_family=task_family,
        current_level=level_label,
        current_level_int=level_int,
        entropy=float(ladder.get("entropy", 0.0)),
        transition_possible=bool(ladder.get("transition_possible", False)),
        evidence_count=int(ladder.get("evidence_count", 0)),
        transition_count=int(ladder.get("transition_count", 0)),
        semantic_verdict=sem_verdict,
        semantic_score=sem_score,
        value_cognitive_return=cog_return,
        theory_results=theory_results,
        is_enhanced=True,
        extracted_from=gen_dir,
    )

    return summary


# ─── Per-Run History ──────────────────────────────────────────────────────────
def build_ladder_history(run_dir: str, max_gen: int) -> list[LadderStateSummary]:
    """
    Build LadderState history across all generations in a run.
    Used by Feedback Agent to see progression.
    """
    history = []
    for gen in range(1, max_gen + 1):
        gen_dir = os.path.join(run_dir, f"gen_{gen}")
        if not os.path.isdir(gen_dir):
            break

        # Check cache first
        cache_path = os.path.join(gen_dir, LADDER_STATE_FILENAME)
        if os.path.exists(cache_path):
            try:
                summary = LadderStateSummary.load(cache_path)
                history.append(summary)
                continue
            except Exception:
                pass

        # Extract fresh
        summary = build_ladder_state_summary(gen_dir, gen)
        if summary.is_enhanced:
            summary.save(cache_path)
        history.append(summary)

    return history


# ─── Orchestrator Integration ─────────────────────────────────────────────────
def run_enhanced_pipeline_check(
    run_dir: str,
    current_gen: int,
    gen_dir: str,
) -> tuple[LadderStateSummary, str]:
    """
    Main entry point for orchestrator Section 5a (post-run).

    Extracts enhanced pipeline signals from just-completed generation
    and returns (summary, feedback_section_text).

    Args:
        run_dir: path to run directory
        current_gen: current generation number
        gen_dir: path to current gen directory

    Returns:
        (LadderStateSummary, feedback_section_str)
    """
    signals = extract_enhanced_signals_from_gen(gen_dir)
    summary = build_ladder_state_summary(gen_dir, current_gen, signals)

    if summary.is_enhanced:
        cache_path = os.path.join(gen_dir, LADDER_STATE_FILENAME)
        try:
            summary.save(cache_path)
            logger.info(
                f"Enhanced signals extracted: level={summary.current_level} "
                f"entropy={summary.entropy:.3f} "
                f"semantic={summary.semantic_verdict}"
            )
        except Exception as e:
            logger.warning(f"Could not save ladder state: {e}")
    else:
        logger.info("No enhanced pipeline signals found in gen output — agent used minimal pipeline")

    feedback_section = summary.to_feedback_section()
    return summary, feedback_section


# ─── Enhanced Pipeline META_AGENT_PROMPT Snippet ─────────────────────────────
ENHANCED_PIPELINE_SNIPPET = """
# ═══════════════════════════════════════════════════════════════════
# 🔬 ENHANCED PIPELINE (GENESIS Layer 4 — Full Cognitive Stack)
# ═══════════════════════════════════════════════════════════════════
# UPGRADE: Use run_enhanced_pipeline instead of run_minimal_pipeline
# for richer cognitive signals (LadderAscent + Semantic + Value).
#
# Add this import at the top:
#   from virtual_genesis.runtime.enhanced_pipeline.enhanced_run import run_enhanced_pipeline
#
# Replace run_minimal_pipeline call with:
#
# result = run_enhanced_pipeline(
#     raw_task=task_text,
#     store=store,
#     ledger_store=ledger_store,
#     concept_registry=concept_registry,
#     theory_registry=theory_registry,
#     use_semantic_verification=True,
#     use_value_computation=True,
#     use_ladder_tracking=True,
#     use_theory_testing=True,
# )
#
# Additional signals in result:
#   result["ladder_tracking"]       — LadderAscent state (level 0-4)
#   result["semantic_verification"] — verdict: VERIFIED/UNCERTAIN/REJECTED
#   result["value_computation"]     — cognitive return (positive = tier justified)
#   result["theory_testing"]        — which theories hold/fail
#
# SAVE enhanced signals for Feedback Agent:
#   import json
#   with open(os.path.join(WORKING_DIR, "enhanced_signals.json"), "w") as f:
#       # Save only serializable parts
#       enhanced_out = {
#           "task": result.get("task", {}),
#           "ladder_tracking": result.get("ladder_tracking", {}),
#           "semantic_verification": result.get("semantic_verification", {}),
#           "value_computation": {
#               "cognitive_return": result.get("value_computation", {})
#                                       .get("cognitive_return", {}),
#           },
#           "theory_testing": result.get("theory_testing", {}),
#       }
#       json.dump(enhanced_out, f, default=str)
#
# Ladder levels: 0=FOUNDATION → 1=PATTERN → 2=THEORY → 3=PREDICTIVE → 4=MASTERY
# Use ladder level to guide reasoning depth in your task answers.
"""


def get_enhanced_pipeline_snippet(enabled: bool = True) -> str:
    """Return the META_AGENT_PROMPT snippet for enhanced pipeline."""
    return ENHANCED_PIPELINE_SNIPPET if enabled else ""
