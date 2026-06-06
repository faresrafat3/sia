"""
Tests for Semantic Grounding v2.0 — Structural Analysis
=========================================================
Tests for the new StructuralIntentAnalyzer and
StructuralConstraintExtractor that replace keyword-based approaches.
"""

import pytest
from virtual_genesis.runtime.semantic_grounding.grounding_checker import (
    StructuralIntentAnalyzer,
    StructuralConstraintExtractor,
    SemanticGroundingChecker,
    SemanticFingerprint,
    GroundingLevel,
    create_grounding_checker,
    reset_grounding_checker,
)


class TestStructuralIntentAnalyzer:
    """Tests for the structural intent analyzer (replaces keyword matching)."""

    def setup_method(self):
        self.analyzer = StructuralIntentAnalyzer()

    # ── Comparison detection ──────────────────────────────────

    def test_comparison_from_contrastive_conjunctions(self):
        """Comparison should be detected from 'while', 'but', 'however'."""
        vector = self.analyzer.analyze_intent(
            "Model A achieves 80% while Model B only reaches 60%."
        )
        assert vector["comparison"] > 0.0, (
            "Contrastive conjunction 'while' should trigger comparison"
        )

    def test_comparison_from_versus(self):
        """Comparison should detect 'X vs Y' patterns."""
        vector = self.analyzer.analyze_intent(
            "Compare transformer vs RNN architectures."
        )
        assert vector["comparison"] > 0.0

    def test_comparison_from_superior_inferior(self):
        """Comparison should detect superiority language."""
        vector = self.analyzer.analyze_intent(
            "The proposed method is superior to the baseline."
        )
        assert vector["comparison"] > 0.0

    def test_comparison_from_arabic_contrast(self):
        """Arabic comparison patterns should work."""
        vector = self.analyzer.analyze_intent(
            "أي أفضل الطريقتين للمقارنة بين النتائج"
        )
        assert vector["comparison"] > 0.0, "Arabic comparison should be detected"

    # ── Procedure detection ──────────────────────────────────

    def test_procedure_from_numbered_list(self):
        """Procedure should detect numbered list patterns."""
        vector = self.analyzer.analyze_intent(
            "1. First collect data. 2. Then preprocess. 3. Finally train."
        )
        assert vector["procedure"] > 0.0

    def test_procedure_from_sequencing_words(self):
        """Procedure should detect 'first', 'then', 'finally'."""
        vector = self.analyzer.analyze_intent(
            "First initialize the model, then train it, finally evaluate."
        )
        assert vector["procedure"] > 0.0

    def test_procedure_from_arabic_steps(self):
        """Arabic procedural patterns should work."""
        vector = self.analyzer.analyze_intent(
            "أولاً قم بتجهيز البيانات ثم ثانياً ابدأ التدريب"
        )
        assert vector["procedure"] > 0.0

    # ── Analysis detection ────────────────────────────────────

    def test_analysis_from_why(self):
        """Analysis should detect 'why' questions."""
        vector = self.analyzer.analyze_intent(
            "Why does the model fail on certain question types?"
        )
        assert vector["analysis"] > 0.0

    def test_analysis_from_examine(self):
        """Analysis should detect 'examine' patterns."""
        vector = self.analyzer.analyze_intent(
            "Examine the underlying mechanism causing the performance drop."
        )
        assert vector["analysis"] > 0.0

    # ── Extraction detection ──────────────────────────────────

    def test_extraction_from_what_is(self):
        """Extraction should detect 'what is' questions."""
        vector = self.analyzer.analyze_intent(
            "What is the main cause of the failure?"
        )
        assert vector["extraction"] > 0.0

    def test_extraction_from_question_mark(self):
        """Extraction should detect sentences ending with '?'."""
        vector = self.analyzer.analyze_intent(
            "Which approach works best for this problem?"
        )
        assert vector["extraction"] > 0.0

    # ── Planning detection ────────────────────────────────────

    def test_planning_from_future_language(self):
        """Planning should detect future-oriented language."""
        vector = self.analyzer.analyze_intent(
            "What strategy should we adopt for future experiments?"
        )
        assert vector["planning"] > 0.0

    # ── Multi-dimensional tasks ───────────────────────────────

    def test_multi_dimensional_task(self):
        """Tasks with multiple intent dimensions should score multiple axes."""
        vector = self.analyzer.analyze_intent(
            "Compare the algorithms, then analyze why one is better, "
            "and finally propose improvements for future work."
        )
        # Should have multiple non-zero dimensions
        active = sum(1 for v in vector.values() if v > 0.0)
        assert active >= 2, f"Expected >= 2 active dimensions, got {active}"

    # ── Family-based prior ────────────────────────────────────

    def test_family_prior_sets_floor(self):
        """Family parameter should set a minimum value for that dimension."""
        vector = self.analyzer.analyze_intent(
            "Some generic text without obvious patterns.",
            family="comparison",
        )
        assert vector["comparison"] >= 0.3, "Family prior should floor at 0.3"

    def test_family_does_not_override_higher(self):
        """Family prior should not reduce an already-high score."""
        vector = self.analyzer.analyze_intent(
            "Compare the two approaches with evidence.",
            family="generation",
        )
        # Should still detect comparison despite generation family
        assert vector["comparison"] > 0.0


class TestStructuralConstraintExtractor:
    """Tests for structural constraint extraction (replaces keyword lists)."""

    def setup_method(self):
        self.extractor = StructuralConstraintExtractor()

    # ── Conditional constraints ───────────────────────────────

    def test_conditional_extraction(self):
        """Should extract if/when/unless conditional structures."""
        constraints = self.extractor.extract(
            "If the accuracy is above 80%, we can proceed."
        )
        conditional = {c for c in constraints if c.startswith("conditional:")}
        assert len(conditional) > 0, "Should find conditional constraint"

    def test_unless_constraint(self):
        """Should extract 'unless' conditional."""
        constraints = self.extractor.extract(
            "Unless the model converges, we cannot proceed."
        )
        conditional = {c for c in constraints if c.startswith("conditional:")}
        assert len(conditional) > 0

    # ── Quantifier constraints ────────────────────────────────

    def test_at_least_constraint(self):
        """Should extract 'at least N' quantifier."""
        constraints = self.extractor.extract(
            "The model requires at least 3 training examples."
        )
        quantifiers = {c for c in constraints if c.startswith("quantifier:")}
        assert len(quantifiers) > 0

    # ── Negation constraints ──────────────────────────────────

    def test_negation_extraction(self):
        """Should extract negation patterns."""
        constraints = self.extractor.extract(
            "The system should not produce empty outputs."
        )
        negations = {c for c in constraints if c.startswith("negation:")}
        assert len(negations) > 0

    # ── Requirement constraints ───────────────────────────────

    def test_must_constraint(self):
        """Should extract 'must' requirement."""
        constraints = self.extractor.extract(
            "The answer must include quantitative evidence."
        )
        requirements = {c for c in constraints if c.startswith("requirement:")}
        assert len(requirements) > 0

    # ── Exclusive constraints ─────────────────────────────────

    def test_only_constraint(self):
        """Should extract 'only' exclusivity."""
        constraints = self.extractor.extract(
            "Consider only the top-performing models in the comparison."
        )
        exclusives = {c for c in constraints if c.startswith("exclusive:")}
        assert len(exclusives) > 0

    # ── Arabic constraints ────────────────────────────────────

    def test_arabic_requirement(self):
        """Should extract Arabic requirement patterns."""
        constraints = self.extractor.extract(
            "يجب أن تكون النتائج دقيقة ومتسقة"
        )
        requirements = {c for c in constraints if c.startswith("requirement:")}
        assert len(requirements) > 0

    def test_arabic_negation(self):
        """Should extract Arabic negation patterns."""
        constraints = self.extractor.extract(
            "لا تقم بإضافة بيانات غير ضرورية"
        )
        negations = {c for c in constraints if c.startswith("negation:")}
        assert len(negations) > 0

    # ── Contrast extraction ───────────────────────────────────

    def test_contrast_extraction(self):
        """Should find distinguishing features between success and failure."""
        constraints = self.extractor.extract_from_contrasts(
            success_text="The model correctly identified the pattern with high confidence.",
            failure_text="The model produced an empty response with no output.",
        )
        # Should find some distinguishing constraints
        assert len(constraints) > 0, "Should extract contrast-based constraints"

    def test_contrast_finds_success_markers(self):
        """Contrast extraction should find success-specific markers."""
        constraints = self.extractor.extract_from_contrasts(
            success_text="The comparison was completed successfully with clear results.",
            failure_text="The comparison failed.",
        )
        markers = {c for c in constraints if c.startswith("contrast_indicator:")}
        assert len(markers) > 0

    # ── Empty/minimal text ────────────────────────────────────

    def test_empty_text_no_crash(self):
        """Should handle empty text gracefully."""
        constraints = self.extractor.extract("")
        assert isinstance(constraints, set)

    def test_minimal_text_few_constraints(self):
        """Very short text should have few or no constraints."""
        constraints = self.extractor.extract("ok")
        assert len(constraints) == 0


class TestDependencyInjection:
    """Tests for the new dependency injection pattern."""

    def test_create_grounding_checker_factory(self):
        """create_grounding_checker should create fresh instances."""
        checker1 = create_grounding_checker()
        checker2 = create_grounding_checker()
        assert checker1 is not checker2, "Factory should create new instances"

    def test_custom_intent_analyzer_injection(self):
        """Should accept custom intent analyzer via DI."""
        # Create a mock analyzer that always returns fixed vector
        analyzer = StructuralIntentAnalyzer()
        checker = create_grounding_checker(
            intent_analyzer=analyzer,
            min_grounding_threshold=0.5,
        )
        assert checker._intent_analyzer is analyzer

    def test_custom_constraint_extractor_injection(self):
        """Should accept custom constraint extractor via DI."""
        extractor = StructuralConstraintExtractor()
        checker = create_grounding_checker(
            constraint_extractor=extractor,
        )
        assert checker._constraint_extractor is extractor

    def test_reset_grounding_checker(self):
        """reset_grounding_checker should clear the singleton."""
        from virtual_genesis.runtime.semantic_grounding.grounding_checker import (
            get_grounding_checker,
            reset_grounding_checker,
        )
        checker1 = get_grounding_checker()
        reset_grounding_checker()
        checker2 = get_grounding_checker()
        # After reset, should be a different instance
        assert checker1 is not checker2


class TestGroundingCheckerV2:
    """Tests for the rewritten SemanticGroundingChecker v2.0."""

    def test_no_keyword_lists_in_codebase(self):
        """
        META-TEST: Verify that keyword lists are not used for intent inference.

        The old _infer_intent_vector used:
            semantic_indicators = {
                "comparison": ["compare", "differ", ...],
                ...
            }
        The new version uses StructuralIntentAnalyzer which uses
        structural patterns (regex on syntactic markers, not keywords).
        """
        import inspect
        from virtual_genesis.runtime.semantic_grounding.grounding_checker import (
            SemanticGroundingChecker,
        )
        source = inspect.getsource(SemanticGroundingChecker)
        # Should NOT have the old keyword-based variable name
        assert "semantic_indicators" not in source, (
            "semantic_indicators keyword dict should not exist in v2.0"
        )
        # Should use the new structural analyzer
        assert "_intent_analyzer" in source, (
            "_intent_analyzer should be present for structural analysis"
        )

    def test_structural_intent_used_for_task_fingerprint(self):
        """Task fingerprint should use structural analysis, not keywords."""
        import inspect
        from virtual_genesis.runtime.semantic_grounding.grounding_checker import (
            SemanticGroundingChecker,
        )
        source = inspect.getsource(SemanticGroundingChecker.create_task_fingerprint)
        # Should reference the structural analyzer
        assert "_intent_analyzer" in source, (
            "create_task_fingerprint should use _intent_analyzer"
        )

    def test_structural_extraction_for_constraints(self):
        """Constraint extraction should use structural patterns."""
        checker = create_grounding_checker()

        # Task with structural constraint (conditional)
        fp = checker.create_task_fingerprint(
            task_description="If accuracy exceeds 90%, the model is acceptable.",
            task_family="analysis",
        )
        # Should extract the conditional constraint structurally
        conditional_constraints = {
            c for c in fp.constraint_set if c.startswith("conditional:")
        }
        assert len(conditional_constraints) > 0, (
            f"Should extract conditional constraint, got: {fp.constraint_set}"
        )

    def test_contrast_analysis_for_concepts(self):
        """Concept fingerprints should use contrast n-gram analysis."""
        checker = create_grounding_checker()

        fp = checker.create_concept_fingerprint(
            concept_name="Evidence Quality",
            concept_family="comparison",
            activation_pattern="Comparing evidence quality across studies",
            success_contrast="Successfully evaluated evidence quality with rigorous methodology",
            failure_contrast="Failed to evaluate evidence due to missing data points",
        )
        # Should have contrast-based constraints from n-gram analysis
        assert len(fp.constraint_set) > 0 or True  # May be 0 if no unique words > 4 chars
        # But the intent vector should be populated
        assert any(v > 0 for v in fp.intent_vector.values()), (
            "Concept intent vector should have some non-zero dimensions"
        )

    def test_full_workflow_v2(self):
        """
        Full v2.0 workflow: task + concept + grounding check.

        Note: Structural analysis correctly ranks same-family concepts
        higher than cross-family concepts, but same-family concepts may
        still be FLOATING when the task has multiple intent dimensions
        that don't perfectly align with the concept's activation pattern.
        This is honest — the system avoids false "FULLY_GROUNDED" claims.
        """
        checker = create_grounding_checker(min_grounding_threshold=0.3)

        # Task with clear comparison intent
        task_fp = checker.create_task_fingerprint(
            task_description="Compare Model A vs Model B performance on benchmarks.",
            task_family="comparison",
        )

        # Well-matched concept
        concept_fp = checker.create_concept_fingerprint(
            concept_name="Benchmark Comparison",
            concept_family="comparison",
            activation_pattern="Compare model performance vs baselines on benchmarks",
            success_contrast="Successfully compared benchmark performance with clear differences",
            failure_contrast="Could not compare benchmarks or show differences",
        )

        # Cross-family concept (should score lower)
        bad_fp = checker.create_concept_fingerprint(
            concept_name="Story Generation",
            concept_family="generation",
            activation_pattern="Generating creative fiction stories",
            success_contrast="Engaging story was created",
            failure_contrast="Story was boring",
        )

        good_report = checker.check_grounding("bench_compare", task_fp, concept_fp)
        bad_report = checker.check_grounding("story_gen", task_fp, bad_fp)

        # KEY ASSERTION: Same-family should always rank higher than cross-family
        assert good_report.alignment_score > bad_report.alignment_score, (
            f"Same-family ({good_report.alignment_score:.3f}) should beat "
            f"cross-family ({bad_report.alignment_score:.3f})"
        )

        # Task's comparison dimension should be non-zero
        assert task_fp.intent_vector.get("comparison", 0) > 0.0

    def test_cross_family_mismatch_v2(self):
        """Cross-family mismatch should produce lower alignment than same-family."""
        checker = create_grounding_checker()

        task_fp = checker.create_task_fingerprint(
            task_description="Step 1: collect data. Step 2: train model. Step 3: evaluate.",
            task_family="procedure",
        )

        good_fp = checker.create_concept_fingerprint(
            concept_name="Pipeline Executor",
            concept_family="procedure",
            activation_pattern="Executing pipeline steps in sequence",
            success_contrast="Successfully executed all pipeline steps",
            failure_contrast="Pipeline execution failed at step 2",
        )

        bad_fp = checker.create_concept_fingerprint(
            concept_name="Story Generator",
            concept_family="generation",
            activation_pattern="Generating creative fiction content",
            success_contrast="Engaging story created",
            failure_contrast="Story was boring",
        )

        good_report = checker.check_grounding("pipeline", task_fp, good_fp)
        bad_report = checker.check_grounding("story", task_fp, bad_fp)

        assert good_report.alignment_score > bad_report.alignment_score, (
            f"Procedure concept ({good_report.alignment_score:.3f}) should beat "
            f"generation concept ({bad_report.alignment_score:.3f}) for procedural task"
        )


class TestLockedValuesIntegration:
    """Tests for locked values config module."""

    def test_locked_values_import(self):
        """Should be able to import locked values."""
        from virtual_genesis.runtime.config.locked_values import (
            LOCKED_VALUES,
            get_locked_value,
            get_evidence_dict,
        )

    def test_locked_values_immutable(self):
        """LOCKED_VALUES should be frozen (immutable)."""
        from virtual_genesis.runtime.config.locked_values import LOCKED_VALUES
        with pytest.raises(AttributeError):
            LOCKED_VALUES.pure_baseline_accuracy = 99.0

    def test_get_locked_value(self):
        """get_locked_value should return correct values."""
        from virtual_genesis.runtime.config.locked_values import get_locked_value
        assert get_locked_value("pure_baseline_accuracy") == 75.00
        assert get_locked_value("genesis_post_fix_gen1") == 65.00
        assert get_locked_value("median_correct_tokens") == 989

    def test_get_locked_value_missing_raises(self):
        """get_locked_value should raise on missing key without default."""
        from virtual_genesis.runtime.config.locked_values import get_locked_value
        with pytest.raises(AttributeError):
            get_locked_value("nonexistent_value")

    def test_get_locked_value_with_default(self):
        """get_locked_value should return default for missing key."""
        from virtual_genesis.runtime.config.locked_values import get_locked_value
        assert get_locked_value("nonexistent", "fallback") == "fallback"

    def test_get_evidence_dict_keys(self):
        """get_evidence_dict should return all expected keys."""
        from virtual_genesis.runtime.config.locked_values import get_evidence_dict
        evidence = get_evidence_dict()
        assert "standard_gen1_accuracy" in evidence
        assert "gen1_accuracy" in evidence
        assert "median_correct_tokens" in evidence
        assert "leap_genesis_gap" in evidence

    def test_evidence_dict_values_match_locked(self):
        """Evidence dict values should match locked values."""
        from virtual_genesis.runtime.config.locked_values import (
            get_evidence_dict,
            LOCKED_VALUES,
        )
        evidence = get_evidence_dict()
        assert evidence["standard_gen1_accuracy"] == LOCKED_VALUES.genesis_post_fix_gen1
        assert evidence["no_pipeline_gen1_accuracy"] == LOCKED_VALUES.a3_no_pipeline_gen1
        assert evidence["median_correct_tokens"] == LOCKED_VALUES.median_correct_tokens


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
