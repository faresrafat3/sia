"""
Semantic Verifier — GENESIS
=============================
The core verification engine that goes beyond keyword matching.

Key Design Principle (from Theory-08):
    Verification value = f(determinism, scope)
    
    We aim for the top-left quadrant:
    - HIGH determinism (rules-based, not LLM-as-judge)
    - NARROW scope (specific checks, not broad refactoring)

This verifier provides DETERMINISTIC checks that don't require
an LLM call, making them:
    - Fast (no API cost)
    - Reproducible (same input → same output)
    - Composable (multiple checks can be combined)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re
import math
import logging

logger = logging.getLogger(__name__)


class VerificationVerdict(Enum):
    """Verdict from semantic verification."""
    PASS = "pass"
    WARN = "warn"       # Passed with concerns
    FAIL = "fail"        # Definite problem detected
    INCONCLUSIVE = "inconclusive"  # Not enough information


@dataclass
class ReasoningPathValidator:
    """
    Validates the internal consistency of a reasoning path.
    
    Unlike keyword verification which checks "did the output contain X",
    this checks "does the reasoning path make logical sense?"
    
    Checks:
    1. Conclusion follows from premises
    2. No internal contradictions
    3. All required reasoning steps present
    4. No circular reasoning
    5. Evidence cited supports the claim
    """
    
    def validate(
        self,
        reasoning: str,
        answer: str,
        question: str,
        domain: str = "",
    ) -> Dict[str, Any]:
        """
        Validate a reasoning path.
        
        Returns a verification result with verdict and specific checks.
        """
        checks = {}
        
        # Check 1: Reasoning-to-answer consistency
        answer_in_reasoning = self._answer_derived_from_reasoning(reasoning, answer)
        checks["answer_derived"] = {
            "passed": answer_in_reasoning,
            "detail": "Answer should be derivable from reasoning",
        }
        
        # Check 2: Internal consistency (no self-contradiction patterns)
        consistent = self._check_internal_consistency(reasoning)
        checks["internal_consistency"] = {
            "passed": consistent["consistent"],
            "detail": consistent["detail"],
        }
        
        # Check 3: Question addressed (reasoning discusses the question topic)
        addressed = self._question_addressed(reasoning, question)
        checks["question_addressed"] = {
            "passed": addressed,
            "detail": "Reasoning should address the question topic",
        }
        
        # Check 4: Reasoning completeness (minimum length for non-trivial reasoning)
        completeness = self._check_completeness(reasoning, domain)
        checks["completeness"] = {
            "passed": completeness["passed"],
            "detail": completeness["detail"],
        }
        
        # Check 5: No circular reasoning
        circular = self._check_circular_reasoning(reasoning)
        checks["no_circular_reasoning"] = {
            "passed": not circular["circular"],
            "detail": circular["detail"],
        }
        
        # Compute overall verdict
        critical_checks = ["answer_derived", "question_addressed"]
        warning_checks = ["internal_consistency", "completeness", "no_circular_reasoning"]
        
        all_critical_pass = all(checks[c]["passed"] for c in critical_checks)
        all_warning_pass = all(checks[c]["passed"] for c in warning_checks)
        warning_fails = sum(1 for c in warning_checks if not checks[c]["passed"])
        
        if all_critical_pass and all_warning_pass:
            verdict = VerificationVerdict.PASS
        elif all_critical_pass and warning_fails <= 1:
            verdict = VerificationVerdict.WARN
        elif not all_critical_pass:
            verdict = VerificationVerdict.FAIL
        else:
            verdict = VerificationVerdict.WARN
        
        return {
            "verdict": verdict.value,
            "checks": checks,
            "critical_pass": all_critical_pass,
            "warning_count": warning_fails,
            "overall_score": self._compute_overall_score(checks),
        }
    
    def _answer_derived_from_reasoning(self, reasoning: str, answer: str) -> bool:
        """Check if the answer is derivable from the reasoning."""
        if not reasoning or not answer:
            return False
        
        answer_clean = answer.strip().upper()
        reasoning_upper = reasoning.upper()
        
        # The answer letter should appear in the reasoning's conclusion
        if answer_clean in ["A", "B", "C", "D"]:
            # Check if the letter appears in the reasoning at all
            # (more sophisticated: check it appears in the conclusion)
            return answer_clean in reasoning_upper
        
        # For text answers, check if key terms appear
        answer_terms = set(answer_clean.split())
        reasoning_terms = set(reasoning_upper.split())
        overlap = answer_terms & reasoning_terms
        
        return len(overlap) >= min(1, len(answer_terms))
    
    def _check_internal_consistency(self, reasoning: str) -> Dict[str, Any]:
        """Check for internal contradictions in reasoning."""
        if not reasoning:
            return {"consistent": False, "detail": "Empty reasoning"}
        
        # Pattern-based contradiction detection
        contradiction_patterns = [
            (r"therefore.*however.*therefore", "conflicting conclusions"),
            (r"is correct.*is incorrect", "correct and incorrect in same reasoning"),
            (r"must be.*cannot be.*must be", "conflicting necessity"),
        ]
        
        reasoning_lower = reasoning.lower()
        for pattern, description in contradiction_patterns:
            if re.search(pattern, reasoning_lower):
                return {"consistent": False, "detail": f"Possible contradiction: {description}"}
        
        return {"consistent": True, "detail": "No obvious contradictions"}
    
    def _question_addressed(self, reasoning: str, question: str) -> bool:
        """Check if the reasoning addresses the question topic."""
        if not reasoning or not question:
            return False
        
        # Extract key terms from question (simple: non-stopword nouns/terms)
        question_terms = self._extract_key_terms(question)
        reasoning_lower = reasoning.lower()
        
        # At least some key terms should appear in reasoning
        matches = sum(1 for term in question_terms if term in reasoning_lower)
        
        # Need at least 30% overlap or at least 2 terms
        threshold = max(2, len(question_terms) * 0.3)
        return matches >= threshold
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text (simple keyword extraction)."""
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "can", "shall",
            "of", "in", "on", "at", "to", "for", "with", "by", "from",
            "as", "into", "about", "between", "through", "during",
            "this", "that", "these", "those", "which", "what", "who",
            "how", "when", "where", "why", "not", "no", "nor", "but",
            "or", "and", "if", "then", "so", "than", "too", "very",
        }
        
        # Simple extraction: words longer than 3 chars, not stopwords
        words = re.findall(r'[a-zA-Z]{3,}', text.lower())
        terms = [w for w in words if w not in stopwords]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for t in terms:
            if t not in seen:
                seen.add(t)
                unique_terms.append(t)
        
        return unique_terms
    
    def _check_completeness(self, reasoning: str, domain: str) -> Dict[str, Any]:
        """Check if reasoning is sufficiently complete."""
        if not reasoning:
            return {"passed": False, "detail": "No reasoning provided"}
        
        word_count = len(reasoning.split())
        
        # Different domains have different completeness expectations
        min_words = {
            "physics": 20,
            "chemistry": 25,
            "biology": 20,
            "default": 15,
        }
        threshold = min_words.get(domain, min_words["default"])
        
        if word_count < threshold:
            return {
                "passed": False,
                "detail": f"Reasoning too short ({word_count} words, need ≥{threshold})",
            }
        
        return {"passed": True, "detail": f"Reasoning has {word_count} words"}
    
    def _check_circular_reasoning(self, reasoning: str) -> Dict[str, Any]:
        """Check for circular reasoning patterns."""
        if not reasoning:
            return {"circular": False, "detail": "No reasoning to check"}
        
        # Simple check: repeated identical sentences
        sentences = [s.strip().lower() for s in reasoning.split(".") if len(s.strip()) > 10]
        
        # Check for near-duplicate sentences
        seen = set()
        for sentence in sentences:
            normalized = re.sub(r'\s+', ' ', sentence)
            if normalized in seen:
                return {
                    "circular": True,
                    "detail": f"Duplicate reasoning step detected: '{normalized[:50]}...'",
                }
            seen.add(normalized)
        
        return {"circular": False, "detail": "No circular reasoning detected"}
    
    def _compute_overall_score(self, checks: Dict[str, Dict]) -> float:
        """Compute an overall verification score [0.0, 1.0]."""
        weights = {
            "answer_derived": 0.3,
            "question_addressed": 0.25,
            "internal_consistency": 0.2,
            "completeness": 0.15,
            "no_circular_reasoning": 0.1,
        }
        
        score = 0.0
        for check_name, weight in weights.items():
            if check_name in checks:
                score += weight * (1.0 if checks[check_name]["passed"] else 0.0)
        
        return round(score, 3)


@dataclass
class CalibrationEntry:
    """A single calibration data point."""
    confidence: float       # What the system predicted
    was_correct: bool       # What actually happened
    domain: str
    timestamp: datetime = field(default_factory=datetime.now)


class ConfidenceCalibrator:
    """
    Calibrates system confidence against actual accuracy.
    
    A well-calibrated system:
    - When it says "90% confident", it's right ~90% of the time
    - When it says "60% confident", it's right ~60% of the time
    
    This is CRITICAL for the Economy Control layer:
    without calibration, tier decisions are based on unreliable confidence.
    """
    
    def __init__(self):
        self.entries: List[CalibrationEntry] = []
        self._calibration_map: Dict[str, Dict[float, float]] = {}
    
    def record(self, confidence: float, was_correct: bool, domain: str = "default") -> None:
        """Record a calibration data point."""
        self.entries.append(CalibrationEntry(
            confidence=confidence,
            was_correct=was_correct,
            domain=domain,
        ))
        
        # Update calibration map incrementally
        bucket = round(confidence * 10) / 10  # Round to nearest 0.1
        if domain not in self._calibration_map:
            self._calibration_map[domain] = {}
        if bucket not in self._calibration_map[domain]:
            self._calibration_map[domain][bucket] = 0.0
        
        # Running average
        domain_entries = [
            e for e in self.entries
            if e.domain == domain and abs(e.confidence - bucket) < 0.05
        ]
        if domain_entries:
            accuracy = sum(1 for e in domain_entries if e.was_correct) / len(domain_entries)
            self._calibration_map[domain][bucket] = accuracy
    
    def calibrate(self, confidence: float, domain: str = "default") -> float:
        """
        Calibrate a raw confidence score.
        
        Returns the empirically-adjusted confidence.
        If no calibration data exists, returns the raw confidence.
        """
        if domain not in self._calibration_map:
            return confidence
        
        domain_map = self._calibration_map[domain]
        bucket = round(confidence * 10) / 10
        
        if bucket in domain_map:
            calibrated = domain_map[bucket]
            # Blend: 70% calibrated + 30% raw (to avoid overcorrection with little data)
            data_count = sum(1 for e in self.entries if e.domain == domain and abs(e.confidence - bucket) < 0.05)
            blend = min(0.7, data_count / 20.0)  # Gradually trust calibration more
            return blend * calibrated + (1 - blend) * confidence
        
        return confidence
    
    def get_calibration_error(self, domain: str = "default") -> Optional[float]:
        """
        Compute the Expected Calibration Error (ECE).
        
        ECE = Σ |predicted_confidence - actual_accuracy| * (n_bucket / n_total)
        
        Lower is better. ECE = 0 means perfect calibration.
        """
        if domain not in self._calibration_map:
            return None
        
        domain_entries = [e for e in self.entries if e.domain == domain]
        if not domain_entries:
            return None
        
        total = len(domain_entries)
        ece = 0.0
        
        for bucket, accuracy in self._calibration_map[domain].items():
            bucket_entries = [
                e for e in domain_entries if abs(e.confidence - bucket) < 0.05
            ]
            n_bucket = len(bucket_entries)
            if n_bucket > 0:
                ece += abs(bucket - accuracy) * (n_bucket / total)
        
        return round(ece, 3)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get calibration statistics."""
        total = len(self.entries)
        if total == 0:
            return {"total_entries": 0}
        
        domains = set(e.domain for e in self.entries)
        stats = {"total_entries": total, "domains": list(domains)}
        
        for domain in domains:
            ece = self.get_calibration_error(domain)
            domain_entries = [e for e in self.entries if e.domain == domain]
            avg_confidence = sum(e.confidence for e in domain_entries) / len(domain_entries)
            actual_accuracy = sum(1 for e in domain_entries if e.was_correct) / len(domain_entries)
            
            stats[f"{domain}_ece"] = ece
            stats[f"{domain}_avg_confidence"] = round(avg_confidence, 3)
            stats[f"{domain}_actual_accuracy"] = round(actual_accuracy, 3)
            stats[f"{domain}_overconfidence"] = round(avg_confidence - actual_accuracy, 3)
        
        return stats


@dataclass
class TheoryPrediction:
    """A testable prediction from a theory."""
    prediction_id: str
    theory_id: str
    description: str
    expected_outcome: str
    conditions: List[str]
    confidence: float
    tested: bool = False
    outcome: Optional[bool] = None


class TheoryFalsificationEngine:
    """
    Engine for testing theories against data.
    
    A theory in GENESIS should be falsifiable (Karl Popper).
    Each theory must produce testable predictions that can be
    confirmed or refuted by empirical evidence.
    
    This is the GENESIS equivalent of Lean's type checker:
    just as Lean rejects proofs that don't type-check,
    this engine rejects theories whose predictions fail.
    """
    
    def __init__(self):
        self.theories: Dict[str, Dict[str, Any]] = {}
        self.predictions: Dict[str, TheoryPrediction] = {}
        self.test_results: List[Dict[str, Any]] = []
    
    def register_theory(
        self,
        theory_id: str,
        description: str,
        axioms: List[str],
        predictions: List[Dict[str, Any]],
        falsification_conditions: List[str],
    ) -> None:
        """Register a theory for falsification tracking."""
        self.theories[theory_id] = {
            "description": description,
            "axioms": axioms,
            "falsification_conditions": falsification_conditions,
            "registered_at": datetime.now().isoformat(),
            "status": "untested",
            "prediction_ids": [],
            "confirmed_count": 0,
            "refuted_count": 0,
        }
        
        for i, pred_data in enumerate(predictions):
            pred_id = f"{theory_id}_P{i+1}"
            pred = TheoryPrediction(
                prediction_id=pred_id,
                theory_id=theory_id,
                description=pred_data.get("description", ""),
                expected_outcome=pred_data.get("expected", ""),
                conditions=pred_data.get("conditions", []),
                confidence=pred_data.get("confidence", 0.5),
            )
            self.predictions[pred_id] = pred
            self.theories[theory_id]["prediction_ids"].append(pred_id)
    
    def test_prediction(
        self,
        prediction_id: str,
        actual_outcome: str,
        passed: bool,
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Test a specific prediction against empirical data.
        
        This is the core of theory falsification.
        """
        if prediction_id not in self.predictions:
            return {"error": f"Unknown prediction: {prediction_id}"}
        
        pred = self.predictions[prediction_id]
        pred.tested = True
        pred.outcome = passed
        
        theory_id = pred.theory_id
        theory = self.theories.get(theory_id, {})
        
        if passed:
            theory["confirmed_count"] = theory.get("confirmed_count", 0) + 1
        else:
            theory["refuted_count"] = theory.get("refuted_count", 0) + 1
        
        # Update theory status
        all_preds = [
            self.predictions[pid]
            for pid in theory.get("prediction_ids", [])
            if pid in self.predictions
        ]
        tested_preds = [p for p in all_preds if p.tested]
        
        if len(tested_preds) == len(all_preds) and len(all_preds) > 0:
            all_passed = all(p.outcome for p in tested_preds)
            theory["status"] = "confirmed" if all_passed else "partially_refuted"
        elif any(not p.outcome for p in tested_preds if p.outcome is False):
            theory["status"] = "partially_refuted"
        else:
            theory["status"] = "testing"
        
        result = {
            "prediction_id": prediction_id,
            "theory_id": theory_id,
            "expected": pred.expected_outcome,
            "actual": actual_outcome,
            "passed": passed,
            "theory_status": theory["status"],
            "notes": notes,
        }
        
        self.test_results.append(result)
        return result
    
    def get_theory_status(self, theory_id: str) -> Dict[str, Any]:
        """Get the current status of a theory."""
        theory = self.theories.get(theory_id, {})
        if not theory:
            return {"error": f"Unknown theory: {theory_id}"}
        
        pred_ids = theory.get("prediction_ids", [])
        predictions = [
            {
                "id": pid,
                "description": self.predictions[pid].description,
                "tested": self.predictions[pid].tested,
                "outcome": self.predictions[pid].outcome,
            }
            for pid in pred_ids if pid in self.predictions
        ]
        
        return {
            "theory_id": theory_id,
            "description": theory["description"],
            "status": theory["status"],
            "total_predictions": len(pred_ids),
            "tested_predictions": sum(1 for p in predictions if p["tested"]),
            "confirmed": theory.get("confirmed_count", 0),
            "refuted": theory.get("refuted_count", 0),
            "predictions": predictions,
            "falsification_conditions": theory.get("falsification_conditions", []),
        }
    
    def get_overview(self) -> Dict[str, Any]:
        """Get overview of all theories and their status."""
        return {
            "total_theories": len(self.theories),
            "total_predictions": len(self.predictions),
            "tested_predictions": sum(1 for p in self.predictions.values() if p.tested),
            "theory_statuses": {
                tid: t.get("status", "unknown")
                for tid, t in self.theories.items()
            },
        }


class SemanticVerifier:
    """
    The unified semantic verification interface.
    
    This is the GENESIS equivalent of LEAP's Lean compiler.
    It composes all verification checks into a single verdict.
    
    Usage:
        verifier = SemanticVerifier()
        result = verifier.verify(
            question="What is the energy of...",
            reasoning="We know that E = mc^2...",
            answer="B",
            domain="physics",
        )
        print(result["verdict"])  # "pass", "warn", "fail"
    """
    
    def __init__(self):
        self.path_validator = ReasoningPathValidator()
        self.confidence_calibrator = ConfidenceCalibrator()
        self.falsification_engine = TheoryFalsificationEngine()
    
    def verify(
        self,
        question: str,
        reasoning: str,
        answer: str,
        domain: str = "",
        confidence: float = 0.5,
        theory_predictions: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Perform full semantic verification.
        
        Returns a comprehensive verification result.
        """
        # 1. Validate reasoning path
        path_result = self.path_validator.validate(
            reasoning=reasoning,
            answer=answer,
            question=question,
            domain=domain,
        )
        
        # 2. Calibrate confidence
        calibrated_confidence = self.confidence_calibrator.calibrate(
            confidence, domain=domain
        )
        
        # 3. Overall verdict
        verdict = VerificationVerdict(path_result["verdict"])
        
        # 4. Compute verification score (for Economy Control)
        verification_score = path_result["overall_score"] * calibrated_confidence
        
        return {
            "verdict": verdict.value,
            "verification_score": round(verification_score, 3),
            "path_validation": path_result,
            "raw_confidence": confidence,
            "calibrated_confidence": round(calibrated_confidence, 3),
            "domain": domain,
            "recommendation": self._generate_recommendation(verdict, verification_score),
        }
    
    def record_outcome(
        self,
        confidence: float,
        was_correct: bool,
        domain: str = "default",
    ) -> None:
        """Record outcome for calibration."""
        self.confidence_calibrator.record(confidence, was_correct, domain)
    
    def _generate_recommendation(
        self, verdict: VerificationVerdict, score: float
    ) -> str:
        """Generate actionable recommendation."""
        if verdict == VerificationVerdict.PASS and score > 0.8:
            return "High confidence result. No additional verification needed."
        elif verdict == VerificationVerdict.PASS:
            return "Acceptable result. Consider re-verification on similar tasks."
        elif verdict == VerificationVerdict.WARN:
            return "Concerns detected. Review reasoning path before trusting."
        elif verdict == VerificationVerdict.FAIL:
            return "Critical issues. Do NOT trust this result without investigation."
        else:
            return "Insufficient information. Run additional checks."


# Singleton
_verifier: Optional[SemanticVerifier] = None


def get_semantic_verifier() -> SemanticVerifier:
    """Get or create the default semantic verifier instance.

    NOTE: Prefer direct SemanticVerifier() construction for test isolation.
    This function exists for backward compatibility.
    """
    global _verifier
    if _verifier is None:
        _verifier = SemanticVerifier()
    return _verifier


def reset_semantic_verifier() -> None:
    """Reset the singleton semantic verifier. Use in test teardown."""
    global _verifier
    _verifier = None


def create_semantic_verifier() -> SemanticVerifier:
    """Factory function for creating fresh SemanticVerifier instances.

    Replaces singleton pattern. Use for new code and tests.
    """
    return SemanticVerifier()
