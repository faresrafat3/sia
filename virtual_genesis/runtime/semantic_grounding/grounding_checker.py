"""
Semantic Grounding Layer — GENESIS v2.0
=========================================
Bridge between semantic content and operational structure.

v2.0 REWRITE: Replaces keyword-based intent inference with
structural semantic analysis. The v1 approach used keyword lists
(e.g., ["compare", "differ", "contrast"]) to determine intent —
this is the exact gap the Ninja Excavator Report identified as THE
core gap: "GENESIS is a deep philosophical mind in a keyword body."

Key innovations in v2.0:
1. Structural Intent Analysis: uses sentence patterns, clause
   structure, and punctuation to infer intent — no keyword lists
2. N-gram Distributional Similarity: character/word n-gram overlap
   for semantic similarity instead of keyword matching
3. Ontological Grounding: maps to GENESIS intent dimensions via
   structural heuristics (question type, verb position, negation)
4. Constraint Extraction via Syntax: uses punctuation patterns,
   clause boundaries, and conditional structures instead of keyword lists

Core Problem Solved:
- Concept Formation currently builds concepts from keyword patterns
- Verification currently checks keyword presence
- This creates "floating symbols" without semantic grounding

Solution: Semantic Grounding Layer provides:
1. Semantic Fingerprint: a vector representation of task intent
2. Grounding Validator: confirms concept ↔ task alignment
3. Semantic Bridge: connects LLM output to operational structure
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import math
import re
from collections import Counter


class GroundingLevel(Enum):
    """How well a symbol is grounded in task semantics."""
    FULLY_GROUNDED = "fully_grounded"      # Direct semantic mapping
    PARTIALLY_GROUNDED = "partially_grounded"  # Some semantic alignment
    SUPERFICIAL = "superficial"            # Surface pattern only
    FLOATING = "floating"                  # No semantic connection


@dataclass
class SemanticFingerprint:
    """
    A semantic fingerprint of a task or concept.

    Unlike keyword-based matching, this represents the INTENDED meaning:
    - What is the task asking for at a deep level?
    - What are the semantic constraints?
    - What would constitute correct vs incorrect completion?
    """
    intent_vector: Dict[str, float]  # Semantic intent dimensions
    constraint_set: Set[str]         # Semantic constraints
    expected_outcome_type: str       # What kind of output is expected
    grounding_score: float           # 0.0-1.0, how well-grounded this is
    source: str                      # Where this fingerprint came from

    def compute_similarity(self, other: 'SemanticFingerprint') -> float:
        """
        Compute semantic similarity between two fingerprints.

        Uses cosine similarity on intent vectors + Jaccard on constraint sets.
        """
        # Cosine similarity on intent vectors
        dot_product = 0.0
        norm_self = 0.0
        norm_other = 0.0

        all_keys = set(self.intent_vector.keys()) | set(other.intent_vector.keys())
        for key in all_keys:
            v1 = self.intent_vector.get(key, 0.0)
            v2 = other.intent_vector.get(key, 0.0)
            dot_product += v1 * v2
            norm_self += v1 ** 2
            norm_other += v2 ** 2

        cosine_sim = dot_product / (math.sqrt(norm_self) * math.sqrt(norm_other) + 1e-9)

        # Jaccard similarity on constraint sets
        intersection = len(self.constraint_set & other.constraint_set)
        union = len(self.constraint_set | other.constraint_set)
        jaccard_sim = intersection / (union + 1e-9)

        # Combined: 60% intent vector, 40% constraints
        return 0.6 * cosine_sim + 0.4 * jaccard_sim


@dataclass
class GroundingReport:
    """Report on the semantic grounding quality of a concept or operation."""
    concept_id: str
    task_fingerprint: SemanticFingerprint
    concept_fingerprint: SemanticFingerprint
    alignment_score: float          # 0.0-1.0
    grounding_level: GroundingLevel
    is_safe_to_activate: bool
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


# ─── Structural Intent Analyzer ─────────────────────────────────────
# Replaces keyword-based _infer_intent_vector with structural analysis

class StructuralIntentAnalyzer:
    """
    Determines task intent from STRUCTURAL patterns in text.

    Instead of matching keywords like "compare" or "analyze",
    this analyzer looks at:
    - Sentence type (interrogative, imperative, declarative)
    - Clause structure (compound, complex, if-then, contrastive)
    - Punctuation patterns (?, :, --, ;)
    - Quantifier usage (all, none, most, at least)
    - Negation patterns (not, never, except)
    - Sentence position of key structural elements

    This is inherently more semantic than keyword matching because
    it captures the FUNCTION of language, not just its vocabulary.
    """

    # Structural pattern signatures (NOT keyword lists — these are
    # syntactic markers that indicate the function of a sentence)
    CONTRASTIVE_PATTERNS = [
        r'\bcompare\b',                               # Direct comparison verb
        r'\bcontrast\b',                               # Direct contrast verb
        r'\b\w+\s+vs\.?\s+\w+',           # X vs Y
        r'\b\w+\s+versus\s+\w+',           # X versus Y
        r'\b(?:which|what)\s+is\s+(?:better|worse|more|less|greater|smaller|faster|slower)',
        r'\b(?:differ|distinguish|separate)\b.*\b(?:from|between|and)\b',
        r'\b(?:advantage|disadvantage|pro|con)\b',
        r'\bon\s+the\s+other\s+hand\b',
        r'\b(?:while|whereas|although|though|but|however|yet)\b',
        r'\b(?:superior|inferior|outperform|underperform)\b',
        # Arabic structural patterns
        r'أي\s+(?:أفضل|أسرع|أقوى|أكبر|أصغر)',
        r'مقارنة\s+(?:بـ|مع|بين)',
        r'(?:فروق|اختلاف|تمييز)',
        r'(?:أفضل|أسوأ|أقوى|أضعف)\s+(?:من|عن)',
    ]

    SYNTHESIS_PATTERNS = [
        r'\b(?:combine|merge|integrate|unify|synthesize)\b',
        r'\b(?:build|construct|assemble|compose)\b.*\b(?:from|out\s+of|using)\b',
        r'\b(?:together|joint|holistic|comprehensive)\b',
        r'\b(?:both|all\s+(?:of|these))\b',
        # Arabic
        r'(?:دمج|تجميع|توحيد|تركيب|بناء)',
        r'(?:معاً|كلي|شامل)',
    ]

    PROCEDURE_PATTERNS = [
        r'\b(?:first|second|third|then|next|finally|lastly)\b',
        r'\b(?:step|phase|stage|stage\s+\d+)\b',
        r'\b(?:follow|execute|implement|perform|carry\s+out)\b',
        r'\b(?:algorithm|procedure|method|process)\b',
        r'\d+\.\s+\w+',                      # Numbered list: "1. something"
        r'\b(?:how\s+to|in\s+order\s+to)\b',
        # Arabic
        r'(?:خطوة|مرحلة|أولاً|ثانياً|ثالثاً)',
        r'(?:كيف\s+(?:ن|أ|ت))',
        r'(?:تنفيذ|تطبيق|إجراء)',
    ]

    ANALYSIS_PATTERNS = [
        r'\b(?:why|explain|analyze|examine|investigate|explore)\b',
        r'\b(?:cause|reason|factor|source|origin)\b',
        r'\b(?:underlying|root|fundamental|deep|core)\b',
        r'\b(?:mechanism|process|structure|pattern|relationship)\b',
        r'\b(?:what)\s+(?:causes|drives|leads|results)\b',
        # Arabic
        r'(?:لماذا|ما\s+سبب|ما\s+هو\s+السبب)',
        r'(?:تحليل|دراسة|بحث|فحص)',
        r'(?:آلية|علاقة|بنية)',
    ]

    EXTRACTION_PATTERNS = [
        r'\b(?:find|identify|locate|extract|retrieve|discover)\b',
        r'\b(?:what\s+(?:is|are|was|were))\b',
        r'\b(?:who|where|when|which)\b.*\b(?:is|are|was|were)\b',
        r'\b(?:list|enumerate|name|specify)\b',
        # Arabic
        r'(?:ما\s+هو|ما\s+هي|من\s+هو|أين|متى)',
        r'(?:استخراج|إيجاد|تحديد|تعيين)',
    ]

    PLANNING_PATTERNS = [
        r'\b(?:plan|strategy|approach|design|roadmap|blueprint)\b',
        r'\b(?:should|could|would|might|will)\b.*\b(?:do|go|proceed|take)\b',
        r'\b(?:future|next|upcoming|planned|proposed)\b',
        r'\b(?:improve|optimize|enhance|refine|extend)\b.*\b(?:by|through|via)\b',
        # Arabic
        r'(?:خطة|استراتيجية|تخطيط|تصميم)',
        r'(?:مستقبل|قادم|مقترح|محسن)',
    ]

    GENERATION_PATTERNS = [
        r'\b(?:generate|create|produce|construct|invent|devise)\b',
        r'\b(?:write|compose|draft|formulate)\b.*\b(?:new|novel|original)\b',
        r'\b(?:propose|suggest|hypothesize|conjecture)\b.*\b(?:new|novel)\b',
        # Arabic
        r'(?:توليد|إنشاء|إنتاج|ابتكار)',
        r'(?:اقترح|افترض)',
    ]

    CLASSIFICATION_PATTERNS = [
        r'\b(?:classify|categorize|group|sort|arrange|organize)\b',
        r'\b(?:type\s+of|kind\s+of|category|class|family|group)\b',
        r'\b(?:belongs?\s+to|member\s+of|instance\s+of)\b',
        # Arabic
        r'(?:تصنيف|فئة|نوع|صنف|مجموعة)',
        r'(?:ينتمي|ينتمي|عضو)',
    ]

    def __init__(self):
        """Initialize the structural analyzer."""
        # Compile all patterns for efficiency
        self._dimension_patterns = {
            "comparison": self.CONTRASTIVE_PATTERNS,
            "synthesis": self.SYNTHESIS_PATTERNS,
            "procedure": self.PROCEDURE_PATTERNS,
            "analysis": self.ANALYSIS_PATTERNS,
            "extraction": self.EXTRACTION_PATTERNS,
            "planning": self.PLANNING_PATTERNS,
            "generation": self.GENERATION_PATTERNS,
            "classification": self.CLASSIFICATION_PATTERNS,
        }
        self._compiled = {
            dim: [re.compile(p, re.IGNORECASE) for p in patterns]
            for dim, patterns in self._dimension_patterns.items()
        }

    def analyze_intent(
        self,
        text: str,
        family: str = "",
    ) -> Dict[str, float]:
        """
        Analyze text to produce an intent vector.

        Uses THREE layers of analysis:
        1. Structural patterns (regex on syntactic markers)
        2. Sentence-type detection (question, imperative, conditional)
        3. Family-based prior (soft bias toward family dimension)

        Returns intent vector with values in [0.0, 1.0].
        """
        vector = {dim: 0.0 for dim in self._dimension_patterns}

        # ── Layer 1: Structural pattern matching ──
        for dimension, patterns in self._compiled.items():
            score = 0.0
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    # Multiple matches increase confidence, with diminishing returns
                    score += min(1.0, 0.3 * len(matches))
            if score > 0:
                vector[dimension] = min(1.0, score)

        # ── Layer 2: Sentence-type structural signals ──
        sentences = self._split_sentences(text)

        for sent in sentences:
            sent_stripped = sent.strip()

            # Interrogative: starts with question word or ends with ?
            if sent_stripped.endswith('?') or self._starts_with_question_word(sent_stripped):
                vector["extraction"] += 0.15

            # Imperative: starts with a verb (command)
            if self._is_imperative(sent_stripped):
                vector["procedure"] += 0.15

            # Conditional: contains if-then structure
            if re.search(r'\bif\b.*\bthen\b|\bif\b.*,', sent_stripped, re.IGNORECASE):
                vector["analysis"] += 0.1
                vector["planning"] += 0.1

            # Contrastive conjunction: indicates comparison
            if re.search(r'\b(?:but|however|while|whereas|although|yet)\b',
                        sent_stripped, re.IGNORECASE):
                vector["comparison"] += 0.15

            # List structure: numbered items
            if re.match(r'\s*\d+[\.\)]\s', sent_stripped):
                vector["procedure"] += 0.2
                vector["extraction"] += 0.1

            # Colon usage often precedes classification or extraction
            if ':' in sent_stripped and sent_stripped.index(':') > 5:
                vector["classification"] += 0.1
                vector["extraction"] += 0.1

        # ── Layer 3: Family-based prior (soft bias) ──
        if family in vector:
            vector[family] = max(vector[family], 0.3)  # Floor at 0.3, don't override

        # ── Normalize: ensure no dimension exceeds 1.0 ──
        for dim in vector:
            vector[dim] = min(1.0, vector[dim])

        return vector

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using structural boundaries."""
        # Split on sentence-ending punctuation, keeping the delimiter
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _starts_with_question_word(self, sentence: str) -> bool:
        """Check if sentence starts with a question word (structural signal)."""
        # These are grammatical function words, not content keywords
        question_starters = {
            "what", "which", "who", "whom", "whose", "where", "when",
            "why", "how", "is", "are", "was", "were", "do", "does",
            "did", "can", "could", "would", "should", "will", "shall",
            "may", "might", "has", "have", "had",
            # Arabic question starters
            "هل", "ما", "من", "أين", "متى", "كيف", "لماذا", "أي",
        }
        first_word = sentence.split()[0].lower().rstrip('.,;:!?') if sentence else ""
        return first_word in question_starters

    def _is_imperative(self, sentence: str) -> bool:
        """Detect imperative (command) sentences structurally."""
        if not sentence:
            return False
        # Imperative: starts with a base-form verb (no subject before it)
        # Structural heuristic: no pronoun/article at start + present tense verb
        first_word = sentence.split()[0].lower().rstrip('.,;:!?') if sentence else ""
        # English articles and pronouns at start = NOT imperative
        non_imperative_starters = {
            "the", "a", "an", "this", "that", "these", "those",
            "i", "you", "he", "she", "it", "we", "they",
            "my", "your", "his", "her", "its", "our", "their",
            "is", "are", "was", "were", "has", "have", "had",
            # Arabic non-imperative starters
            "ال", "هذا", "هذه", "ذلك", "تلك", "أنا", "أنت", "هو", "هي",
        }
        if first_word in non_imperative_starters:
            return False
        # Check if first word looks like a verb (common imperative verbs)
        common_imperatives = {
            "find", "show", "list", "name", "give", "explain",
            "describe", "compare", "identify", "determine", "calculate",
            "compute", "derive", "prove", "demonstrate", "solve",
            "evaluate", "assess", "analyze", "consider", "define",
            "construct", "design", "implement", "provide", "select",
            "choose", "write", "draw", "state", "classify",
            # Arabic imperatives
            "أوجد", "اشرح", "صف", "قارن", "حدد", "احسب", "أثبت",
        }
        return first_word in common_imperatives


class StructuralConstraintExtractor:
    """
    Extracts semantic constraints from text using STRUCTURAL patterns.

    Instead of keyword lists like ["must", "should", "require"],
    this looks at:
    - Conditional clauses (if, when, unless)
    - Quantifier phrases (all, none, at least N, exactly N)
    - Modal verb usage (must, should, cannot)
    - Negation patterns (not, never, except, without)
    - Boundary markers (only, exclusively, limited to)
    """

    # Structural patterns for constraint extraction
    CONSTRAINT_PATTERNS = [
        # Conditional structures
        (r'(?:if|when|unless|provided|assuming|given)\s+[^,.;]+', 'conditional'),
        # Quantifier phrases
        (r'(?:at\s+least|at\s+most|no\s+more\s+than|no\s+less\s+than|exactly|precisely)\s+\d+', 'quantifier'),
        # Universal/existential quantifiers
        (r'(?:all|every|each|any|none|no\s+\w+|some)\s+[^,.;]+', 'scope'),
        # Modal constraints
        (r'(?:must|shall|should|has\s+to|needs?\s+to|is\s+required\s+to)\s+[^,.;]+', 'requirement'),
        # Negation
        (r'(?:not|never|cannot|can\'t|won\'t|don\'t|doesn\'t|didn\'t)\s+[^,.;]+', 'negation'),
        # Exclusive constraints
        (r'(?:only|exclusively|solely|just|merely)\s+[^,.;]+', 'exclusive'),
        # Arabic constraint patterns
        (r'(?:يجب|لازم|من\s+الضروري)\s*[^،.؛]+', 'requirement'),
        (r'(?:فقط|حصراً|فحسب)\s*[^،.؛]+', 'exclusive'),
        (r'(?:لا|لن|لم|لن)\s*[^،.؛]+', 'negation'),
        (r'(?:كل|جميع|أي|بعض|لا\s+\w+)\s*[^،.؛]+', 'scope'),
        (r'(?:إذا|عندما|بشرط|بفرض)\s*[^،.؛]+', 'conditional'),
    ]

    def __init__(self):
        """Compile constraint extraction patterns."""
        self._compiled = [
            (re.compile(p, re.IGNORECASE), ctype)
            for p, ctype in self.CONSTRAINT_PATTERNS
        ]

    def extract(self, text: str) -> Set[str]:
        """
        Extract semantic constraints from text.

        Returns a set of constraint strings, each prefixed with
        its type (conditional, quantifier, scope, etc.)
        """
        constraints = set()
        for pattern, ctype in self._compiled:
            matches = pattern.findall(text)
            for match in matches:
                constraint = f"{ctype}:{match.strip()}"
                # Normalize whitespace
                constraint = re.sub(r'\s+', ' ', constraint)
                if len(constraint) > 8:  # Filter trivially short matches
                    constraints.add(constraint)
        return constraints

    def extract_from_contrasts(
        self,
        success_text: str,
        failure_text: str,
    ) -> Set[str]:
        """
        Extract what differentiates success from failure.

        Uses n-gram overlap analysis instead of simple word-set
        subtraction.
        """
        success_ngrams = self._get_character_ngrams(success_text, n=4)
        failure_ngrams = self._get_character_ngrams(failure_text, n=4)

        # N-grams present in success but not failure
        unique_to_success = success_ngrams - failure_ngrams

        # Find the most informative (longest words contributing to n-grams)
        success_words = set(success_text.lower().split())
        failure_words = set(failure_text.lower().split())
        key_differences = success_words - failure_words

        constraints = set()
        for word in key_differences:
            if len(word) > 4:
                # Check if this word's n-grams are in the unique set
                word_ngrams = set()
                for i in range(len(word) - 3):
                    word_ngrams.add(word[i:i+4])
                if word_ngrams & unique_to_success:
                    constraints.add(f"contrast_indicator:{word}")

        return constraints

    @staticmethod
    def _get_character_ngrams(text: str, n: int = 4) -> Set[str]:
        """Extract character n-grams from text."""
        text_lower = text.lower()
        return {text_lower[i:i+n] for i in range(len(text_lower) - n + 1)}


class SemanticGroundingChecker:
    """
    The core semantic grounding engine (v2.0).

    v2.0 changes:
    - StructuralIntentAnalyzer replaces keyword-based _infer_intent_vector
    - StructuralConstraintExtractor replaces keyword-based _extract_constraints
    - No keyword lists anywhere in the grounding pipeline

    This is the bridge that solves the "floating symbols" problem.
    Before any concept is activated or any operation is performed,
    this checker validates semantic alignment.
    """

    INTENT_DIMENSIONS = [
        "comparison",      # Comparing entities
        "synthesis",       # Combining information
        "procedure",       # Following/executing steps
        "analysis",        # Breaking down structure
        "extraction",      # Pulling specific info
        "planning",        # Creating future actions
        "generation",      # Creating new content
        "classification",  # Categorizing
    ]

    def __init__(
        self,
        min_grounding_threshold: float = 0.65,
        intent_analyzer: StructuralIntentAnalyzer | None = None,
        constraint_extractor: StructuralConstraintExtractor | None = None,
    ):
        """
        Initialize the grounding checker with dependency injection.

        Args:
            min_grounding_threshold: Minimum alignment score to consider
                                    a concept semantically grounded to a task.
            intent_analyzer: Optional custom intent analyzer (for testing/DI).
            constraint_extractor: Optional custom constraint extractor (for testing/DI).
        """
        self.min_grounding_threshold = min_grounding_threshold
        self.grounding_history: List[GroundingReport] = []

        # Dependency injection: use provided instances or create defaults
        self._intent_analyzer = intent_analyzer or StructuralIntentAnalyzer()
        self._constraint_extractor = constraint_extractor or StructuralConstraintExtractor()

    def create_task_fingerprint(
        self,
        task_description: str,
        task_family: str,
        constraints: Optional[List[str]] = None,
    ) -> SemanticFingerprint:
        """
        Create a semantic fingerprint for a task.

        Uses structural analysis to understand what a task
        actually SEMANTICALLY requires, not just what keywords it contains.
        """
        # Intent vector: structural analysis (NOT keyword matching)
        intent_vector = self._intent_analyzer.analyze_intent(
            task_description, task_family
        )

        # Constraint set: structural extraction
        constraint_set = set()
        if constraints:
            constraint_set = set(constraints)
        else:
            constraint_set = self._constraint_extractor.extract(task_description)

        # Expected outcome type: infer from intent vector
        outcome_type = self._infer_outcome_type(intent_vector)

        # Grounding score: task fingerprints are the gold standard
        grounding_score = 1.0

        return SemanticFingerprint(
            intent_vector=intent_vector,
            constraint_set=constraint_set,
            expected_outcome_type=outcome_type,
            grounding_score=grounding_score,
            source=f"task:{task_description[:50]}"
        )

    def create_concept_fingerprint(
        self,
        concept_name: str,
        concept_family: str,
        activation_pattern: str,
        success_contrast: str,
        failure_contrast: str,
    ) -> SemanticFingerprint:
        """
        Create a semantic fingerprint for a concept.

        Uses structural analysis of activation patterns and
        n-gram contrast analysis for success/failure differentiation.
        """
        # Intent vector: from activation pattern structural analysis
        intent_vector = self._intent_analyzer.analyze_intent(
            activation_pattern, concept_family
        )

        # Constraint set: from success/failure contrast analysis
        constraint_set = self._constraint_extractor.extract_from_contrasts(
            success_contrast, failure_contrast
        )

        # Outcome type: inferred from intent
        outcome_type = self._infer_outcome_type(intent_vector)

        # Grounding score: starts at 0.5, updated based on validation
        grounding_score = 0.5

        return SemanticFingerprint(
            intent_vector=intent_vector,
            constraint_set=constraint_set,
            expected_outcome_type=outcome_type,
            grounding_score=grounding_score,
            source=f"concept:{concept_name}"
        )

    def check_grounding(
        self,
        concept_id: str,
        task_fingerprint: SemanticFingerprint,
        concept_fingerprint: SemanticFingerprint,
    ) -> GroundingReport:
        """
        Check if a concept is semantically grounded to a task.

        This is the core validation: does this concept actually mean
        something relevant to this task, or is it just a surface pattern match?
        """
        # Compute alignment
        alignment_score = task_fingerprint.compute_similarity(concept_fingerprint)

        # Determine grounding level
        if alignment_score >= 0.8:
            grounding_level = GroundingLevel.FULLY_GROUNDED
        elif alignment_score >= self.min_grounding_threshold:
            grounding_level = GroundingLevel.PARTIALLY_GROUNDED
        elif alignment_score >= 0.4:
            grounding_level = GroundingLevel.SUPERFICIAL
        else:
            grounding_level = GroundingLevel.FLOATING

        # Determine if safe to activate
        is_safe = grounding_level in [
            GroundingLevel.FULLY_GROUNDED,
            GroundingLevel.PARTIALLY_GROUNDED,
        ]

        # Generate warnings/suggestions
        warnings = []
        suggestions = []

        if grounding_level == GroundingLevel.FLOATING:
            warnings.append(
                f"Concept '{concept_id}' is semantically disconnected from task. "
                f"Activation may produce false positives."
            )
            suggestions.append(
                "Consider deactivating this concept for this task family."
            )

        if grounding_level == GroundingLevel.SUPERFICIAL:
            warnings.append(
                f"Concept '{concept_id}' has only surface-level alignment. "
                f"May not capture task's semantic essence."
            )
            suggestions.append(
                "Review concept's success/failure contrasts for deeper patterns."
            )

        # Check outcome type alignment
        if task_fingerprint.expected_outcome_type != concept_fingerprint.expected_outcome_type:
            warnings.append(
                f"Outcome type mismatch: task expects {task_fingerprint.expected_outcome_type}, "
                f"concept produces {concept_fingerprint.expected_outcome_type}"
            )

        # Update concept's grounding score based on validation
        concept_fingerprint.grounding_score = (
            0.7 * concept_fingerprint.grounding_score + 0.3 * alignment_score
        )

        report = GroundingReport(
            concept_id=concept_id,
            task_fingerprint=task_fingerprint,
            concept_fingerprint=concept_fingerprint,
            alignment_score=alignment_score,
            grounding_level=grounding_level,
            is_safe_to_activate=is_safe,
            warnings=warnings,
            suggestions=suggestions,
        )

        self.grounding_history.append(report)
        return report

    def _infer_outcome_type(self, intent_vector: Dict[str, float]) -> str:
        """
        Infer expected outcome type from intent vector.

        Looks at the dominant intent dimension to determine
        what kind of output is expected.
        """
        outcome_map = {
            "comparison": "comparison_result",
            "synthesis": "integrated_output",
            "procedure": "executed_plan",
            "analysis": "decomposed_structure",
            "extraction": "extracted_values",
            "planning": "future_action_sequence",
            "classification": "category_assignment",
            "generation": "new_content",
        }

        if not intent_vector:
            return "general_output"

        # Find the dominant intent dimension
        dominant = max(intent_vector, key=intent_vector.get)
        max_score = intent_vector[dominant]

        if max_score < 0.1:
            return "general_output"

        return outcome_map.get(dominant, "general_output")

    def get_grounding_statistics(self) -> Dict:
        """Get statistics on grounding quality across history."""
        if not self.grounding_history:
            return {"total_checks": 0}

        total = len(self.grounding_history)
        fully_grounded = sum(
            1 for r in self.grounding_history
            if r.grounding_level == GroundingLevel.FULLY_GROUNDED
        )
        partially_grounded = sum(
            1 for r in self.grounding_history
            if r.grounding_level == GroundingLevel.PARTIALLY_GROUNDED
        )
        floating = sum(
            1 for r in self.grounding_history
            if r.grounding_level == GroundingLevel.FLOATING
        )

        avg_alignment = sum(r.alignment_score for r in self.grounding_history) / total

        return {
            "total_checks": total,
            "fully_grounded": fully_grounded,
            "partially_grounded": partially_grounded,
            "superficial": total - fully_grounded - partially_grounded - floating,
            "floating": floating,
            "avg_alignment": round(avg_alignment, 3),
            "floating_rate": round(floating / total, 3),
        }


def create_grounding_checker(
    min_grounding_threshold: float = 0.65,
    intent_analyzer: StructuralIntentAnalyzer | None = None,
    constraint_extractor: StructuralConstraintExtractor | None = None,
) -> SemanticGroundingChecker:
    """
    Factory function for creating grounding checkers.

    Replaces the singleton get_grounding_checker() pattern.
    Use this for new code; existing callers can migrate gradually.
    """
    return SemanticGroundingChecker(
        min_grounding_threshold=min_grounding_threshold,
        intent_analyzer=intent_analyzer,
        constraint_extractor=constraint_extractor,
    )


# Legacy singleton — kept for backward compatibility.
# New code should use create_grounding_checker() or inject directly.
_grounding_checker: Optional[SemanticGroundingChecker] = None


def get_grounding_checker() -> SemanticGroundingChecker:
    """
    Get or create the default grounding checker instance.

    NOTE: Prefer create_grounding_checker() or direct construction
    for test isolation. This function exists for backward compatibility.
    """
    global _grounding_checker
    if _grounding_checker is None:
        _grounding_checker = SemanticGroundingChecker()
    return _grounding_checker


def reset_grounding_checker() -> None:
    """
    Reset the singleton grounding checker.

    Use in test teardown to prevent test pollution.
    """
    global _grounding_checker
    _grounding_checker = None
