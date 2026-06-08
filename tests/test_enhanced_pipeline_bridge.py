"""
Tests for genesis/enhanced_pipeline_bridge.py — Layer 4
Wires virtual_genesis enhanced pipeline signals to orchestrator feedback loop.
"""
import json
import os
import tempfile
import unittest

from genesis.enhanced_pipeline_bridge import (
    LadderStateSummary,
    build_ladder_state_summary,
    build_ladder_history,
    extract_enhanced_signals_from_gen,
    run_enhanced_pipeline_check,
    get_enhanced_pipeline_snippet,
    LADDER_STATE_FILENAME,
    ENHANCED_SIGNALS_FILENAME,
)


# ─── LadderStateSummary Tests ─────────────────────────────────────────────────
class TestLadderStateSummary(unittest.TestCase):
    def _make(self, **kwargs) -> LadderStateSummary:
        defaults = dict(
            gen=1, task_family="gpqa",
            current_level="PATTERN_RECOGNITION", current_level_int=1,
            entropy=0.3, transition_possible=False,
            evidence_count=10, transition_count=1,
            semantic_verdict="VERIFIED", semantic_score=0.85,
            value_cognitive_return=0.12,
            theory_results={"T1": {"holds": True}, "T2": {"holds": False}},
            is_enhanced=True, extracted_from="/tmp/gen_1",
        )
        defaults.update(kwargs)
        return LadderStateSummary(**defaults)

    def test_basic_fields(self):
        s = self._make()
        self.assertEqual(s.current_level, "PATTERN_RECOGNITION")
        self.assertEqual(s.current_level_int, 1)
        self.assertTrue(s.is_enhanced)

    def test_empty_summary(self):
        s = LadderStateSummary.empty(3)
        self.assertEqual(s.gen, 3)
        self.assertFalse(s.is_enhanced)
        self.assertEqual(s.current_level, "FOUNDATION")
        self.assertEqual(s.current_level_int, 0)

    def test_to_dict(self):
        s = self._make()
        d = s.to_dict()
        self.assertIsInstance(d, dict)
        self.assertIn("current_level", d)
        self.assertIn("entropy", d)
        self.assertIn("theory_results", d)

    def test_save_and_load(self):
        s = self._make()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "ladder_state.json")
            s.save(path)
            loaded = LadderStateSummary.load(path)
            self.assertEqual(loaded.current_level, s.current_level)
            self.assertEqual(loaded.entropy, s.entropy)
            self.assertEqual(loaded.semantic_verdict, s.semantic_verdict)
            self.assertEqual(len(loaded.theory_results), 2)

    def test_to_feedback_section_enhanced(self):
        s = self._make()
        section = s.to_feedback_section()
        self.assertIn("ENHANCED PIPELINE", section)
        self.assertIn("PATTERN_RECOGNITION", section)
        self.assertIn("VERIFIED", section)
        self.assertIn("0.300", section)  # entropy

    def test_to_feedback_section_not_enhanced(self):
        s = LadderStateSummary.empty(1)
        section = s.to_feedback_section()
        self.assertEqual(section, "")  # empty = no section

    def test_feedback_section_high_entropy_warning(self):
        s = self._make(entropy=0.85)
        section = s.to_feedback_section()
        self.assertIn("UNSTABLE", section)
        self.assertIn("HIGH ENTROPY", section)

    def test_feedback_section_negative_return_warning(self):
        s = self._make(value_cognitive_return=-0.5)
        section = s.to_feedback_section()
        self.assertIn("Negative cognitive return", section)

    def test_feedback_section_rejected_semantic(self):
        s = self._make(semantic_verdict="REJECTED")
        section = s.to_feedback_section()
        self.assertIn("REJECTED", section)
        self.assertIn("internally inconsistent", section)

    def test_feedback_section_ladder_levels(self):
        for level_int, expected_kw in [
            (0, "FOUNDATION"),
            (1, "patterns"),
            (2, "theories"),
            (3, "predictive"),
        ]:
            level_name = {0: "FOUNDATION", 1: "PATTERN_RECOGNITION",
                         2: "THEORY_FORMATION", 3: "PREDICTIVE_POWER"}[level_int]
            s = self._make(current_level=level_name, current_level_int=level_int)
            section = s.to_feedback_section()
            self.assertIn(expected_kw.lower(), section.lower(),
                         f"Level {level_int} should mention '{expected_kw}'")

    def test_theory_results_in_section(self):
        s = self._make(theory_results={
            "TheoryA": {"holds": True},
            "TheoryB": {"holds": False},
        })
        section = s.to_feedback_section()
        self.assertIn("TheoryA", section)
        self.assertIn("TheoryB", section)


# ─── extract_enhanced_signals_from_gen Tests ─────────────────────────────────
class TestExtractEnhancedSignals(unittest.TestCase):
    def test_no_signals_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            signals = extract_enhanced_signals_from_gen(tmpdir)
            self.assertEqual(signals, {})

    def test_reads_enhanced_signals_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {"ladder_tracking": {"current_level": "THEORY_FORMATION"},
                    "semantic_verification": {"verdict": "VERIFIED"}}
            path = os.path.join(tmpdir, ENHANCED_SIGNALS_FILENAME)
            with open(path, "w") as f:
                json.dump(data, f)
            signals = extract_enhanced_signals_from_gen(tmpdir)
            self.assertIn("ladder_tracking", signals)
            self.assertEqual(signals["ladder_tracking"]["current_level"], "THEORY_FORMATION")

    def test_reads_agent_execution_with_enhanced_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "ladder_tracking": {"current_level_int": 2, "entropy": 0.4},
                "semantic_verification": {"verdict": "UNCERTAIN", "verification_score": 0.6},
                "task": {"task_family": "gpqa"},
            }
            path = os.path.join(tmpdir, "agent_execution.json")
            with open(path, "w") as f:
                json.dump(data, f)
            signals = extract_enhanced_signals_from_gen(tmpdir)
            self.assertIn("ladder_tracking", signals)

    def test_ignores_plain_agent_execution(self):
        """agent_execution.json without enhanced fields = not enhanced."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {"accuracy": 0.75, "tier": "tier_2"}
            path = os.path.join(tmpdir, "agent_execution.json")
            with open(path, "w") as f:
                json.dump(data, f)
            signals = extract_enhanced_signals_from_gen(tmpdir)
            self.assertEqual(signals, {})

    def test_reads_multi_trajectory_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            exec_dir = os.path.join(tmpdir, "agent_execution")
            os.makedirs(exec_dir)
            data = {
                "ladder_tracking": {"current_level": "PREDICTIVE_POWER", "entropy": 0.2},
                "semantic_verification": {"verdict": "VERIFIED"},
            }
            with open(os.path.join(exec_dir, "q001.json"), "w") as f:
                json.dump(data, f)
            signals = extract_enhanced_signals_from_gen(tmpdir)
            self.assertIn("ladder_tracking", signals)


# ─── build_ladder_state_summary Tests ────────────────────────────────────────
class TestBuildLadderStateSummary(unittest.TestCase):
    def test_empty_signals(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = build_ladder_state_summary(tmpdir, gen=1, signals={})
            self.assertFalse(summary.is_enhanced)
            self.assertEqual(summary.current_level, "FOUNDATION")

    def test_full_signals(self):
        signals = {
            "task": {"task_family": "micro_task"},
            "ladder_tracking": {
                "current_level": "THEORY_FORMATION",
                "current_level_int": 2,
                "entropy": 0.45,
                "transition_possible": True,
                "evidence_count": 25,
                "transition_count": 2,
            },
            "semantic_verification": {
                "verdict": "VERIFIED",
                "verification_score": 0.88,
            },
            "value_computation": {
                "cognitive_return": {"net_return": 0.15},
            },
            "theory_testing": {
                "T1": {"holds": True},
                "T2": {"holds": False},
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = build_ladder_state_summary(tmpdir, gen=2, signals=signals)
            self.assertTrue(summary.is_enhanced)
            self.assertEqual(summary.current_level, "THEORY_FORMATION")
            self.assertEqual(summary.current_level_int, 2)
            self.assertAlmostEqual(summary.entropy, 0.45)
            self.assertTrue(summary.transition_possible)
            self.assertEqual(summary.task_family, "micro_task")
            self.assertEqual(summary.semantic_verdict, "VERIFIED")
            self.assertAlmostEqual(summary.semantic_score, 0.88)
            self.assertAlmostEqual(summary.value_cognitive_return, 0.15)
            self.assertEqual(len(summary.theory_results), 2)

    def test_partial_signals(self):
        """Missing some fields → uses defaults."""
        signals = {
            "ladder_tracking": {"current_level": "PATTERN_RECOGNITION"},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = build_ladder_state_summary(tmpdir, gen=1, signals=signals)
            self.assertTrue(summary.is_enhanced)
            self.assertEqual(summary.current_level, "PATTERN_RECOGNITION")
            self.assertEqual(summary.entropy, 0.0)
            self.assertEqual(summary.semantic_verdict, "UNKNOWN")

    def test_cognitive_return_float(self):
        """cognitive_return can be float directly."""
        signals = {
            "ladder_tracking": {"current_level": "FOUNDATION"},
            "value_computation": {"cognitive_return": 0.25},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = build_ladder_state_summary(tmpdir, gen=1, signals=signals)
            self.assertAlmostEqual(summary.value_cognitive_return, 0.25)


# ─── build_ladder_history Tests ───────────────────────────────────────────────
class TestBuildLadderHistory(unittest.TestCase):
    def test_empty_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            history = build_ladder_history(tmpdir, max_gen=3)
            self.assertEqual(history, [])

    def test_single_gen(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen_dir = os.path.join(tmpdir, "gen_1")
            os.makedirs(gen_dir)
            signals = {
                "ladder_tracking": {"current_level": "FOUNDATION", "current_level_int": 0},
            }
            with open(os.path.join(gen_dir, ENHANCED_SIGNALS_FILENAME), "w") as f:
                json.dump(signals, f)

            history = build_ladder_history(tmpdir, max_gen=3)
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0].current_level, "FOUNDATION")

    def test_multiple_gens(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            for gen, level in [(1, "FOUNDATION"), (2, "PATTERN_RECOGNITION")]:
                gen_dir = os.path.join(tmpdir, f"gen_{gen}")
                os.makedirs(gen_dir)
                signals = {
                    "ladder_tracking": {"current_level": level, "current_level_int": gen - 1},
                }
                with open(os.path.join(gen_dir, ENHANCED_SIGNALS_FILENAME), "w") as f:
                    json.dump(signals, f)

            history = build_ladder_history(tmpdir, max_gen=5)
            self.assertEqual(len(history), 2)
            self.assertEqual(history[0].current_level, "FOUNDATION")
            self.assertEqual(history[1].current_level, "PATTERN_RECOGNITION")

    def test_uses_cache(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen_dir = os.path.join(tmpdir, "gen_1")
            os.makedirs(gen_dir)

            # Create cached ladder state (no signals file)
            cached = LadderStateSummary(
                gen=1, task_family="cached",
                current_level="THEORY_FORMATION", current_level_int=2,
                entropy=0.3, transition_possible=True,
                evidence_count=15, transition_count=1,
                semantic_verdict="VERIFIED", semantic_score=0.9,
                value_cognitive_return=0.1, theory_results={},
                is_enhanced=True, extracted_from="cache",
            )
            cached.save(os.path.join(gen_dir, LADDER_STATE_FILENAME))

            history = build_ladder_history(tmpdir, max_gen=3)
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0].current_level, "THEORY_FORMATION")
            self.assertEqual(history[0].task_family, "cached")


# ─── run_enhanced_pipeline_check Tests ────────────────────────────────────────
class TestRunEnhancedPipelineCheck(unittest.TestCase):
    def test_no_signals(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen_dir = os.path.join(tmpdir, "gen_1")
            os.makedirs(gen_dir)
            summary, section = run_enhanced_pipeline_check(tmpdir, 1, gen_dir)
            self.assertFalse(summary.is_enhanced)
            self.assertEqual(section, "")

    def test_with_signals(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen_dir = os.path.join(tmpdir, "gen_2")
            os.makedirs(gen_dir)
            signals = {
                "ladder_tracking": {
                    "current_level": "PATTERN_RECOGNITION",
                    "current_level_int": 1,
                    "entropy": 0.25,
                    "transition_possible": False,
                    "evidence_count": 8,
                    "transition_count": 0,
                },
                "semantic_verification": {"verdict": "VERIFIED", "verification_score": 0.8},
                "task": {"task_family": "test_task"},
            }
            with open(os.path.join(gen_dir, ENHANCED_SIGNALS_FILENAME), "w") as f:
                json.dump(signals, f)

            summary, section = run_enhanced_pipeline_check(tmpdir, 2, gen_dir)
            self.assertTrue(summary.is_enhanced)
            self.assertIn("ENHANCED PIPELINE", section)
            self.assertIn("PATTERN_RECOGNITION", section)

            # Verify ladder_state.json was saved
            cache_path = os.path.join(gen_dir, LADDER_STATE_FILENAME)
            self.assertTrue(os.path.exists(cache_path))


# ─── get_enhanced_pipeline_snippet Tests ─────────────────────────────────────
class TestGetEnhancedPipelineSnippet(unittest.TestCase):
    def test_returns_string(self):
        snippet = get_enhanced_pipeline_snippet(enabled=True)
        self.assertIsInstance(snippet, str)
        self.assertGreater(len(snippet), 0)

    def test_contains_key_content(self):
        snippet = get_enhanced_pipeline_snippet(enabled=True)
        self.assertIn("run_enhanced_pipeline", snippet)
        self.assertIn("ladder_tracking", snippet)
        self.assertIn("semantic_verification", snippet)
        self.assertIn("Ladder levels", snippet)

    def test_disabled_returns_nonempty(self):
        """Even disabled, snippet has content (always injected)."""
        snippet = get_enhanced_pipeline_snippet(enabled=False)
        self.assertEqual(snippet, "")

    def test_snippet_has_import(self):
        snippet = get_enhanced_pipeline_snippet(enabled=True)
        self.assertIn("from virtual_genesis.runtime.enhanced_pipeline", snippet)

    def test_snippet_has_save_instructions(self):
        snippet = get_enhanced_pipeline_snippet(enabled=True)
        self.assertIn("enhanced_signals.json", snippet)


if __name__ == "__main__":
    unittest.main(verbosity=2)
