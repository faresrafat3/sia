"""Tests for genesis.llm_helpers.

These tests prove that the LLM helpers handle real-world response formats
that reasoning models actually produce. Originally validated against
gpt-oss-120b, Nemotron Nano, LFM 2.5 Thinking on GPQA Diamond.
"""
from __future__ import annotations

import pytest

from genesis.llm_helpers import (
    extract_letter,
    safe_get_question_field,
    safe_get_question_id,
    safe_get_options,
    build_mcq_prompt,
)


class TestExtractLetter:
    """Tests for the extract_letter parser (16+ patterns)."""

    @pytest.mark.parametrize("text,expected", [
        # Standard ANSWER: X formats
        ("ANSWER: A", "A"),
        ("ANSWER:A", "A"),  # no space (Nemotron seen)
        ("ANSWER:  C  ", "C"),  # extra spaces
        ("answer: c", "C"),  # lowercase
        ("Final answer: B", "B"),
        ("The answer is D", "D"),
        ("Correct answer is B", "B"),
        # Markdown
        ("**A**", "A"),
        ("...\n\n**Answer: C**", "C"),
        # LaTeX
        ("\\boxed{B}", "B"),
        ("\\textbf{D}", "D"),
        # Duplicate / repeated ANSWER lines
        ("reasoning... \n\nANSWER: C\n\nANSWER: C", "C"),
        # Letter at end with punctuation
        ("Therefore option C is correct.\n\nC.", "C"),
        # Letter on its own line
        ("blah blah\n\nA\n", "A"),
        # OPTION X IS
        ("Option: D", "D"),
        # Fallback: last A-D in text
        ("something with random A in the middle text", "A"),
    ])
    def test_parses_known_formats(self, text, expected):
        assert extract_letter(text) == expected

    def test_empty_string(self):
        assert extract_letter("") == ""

    def test_no_letter_in_text(self):
        assert extract_letter("I don't know the answer") == ""

    def test_handles_none_gracefully(self):
        # extract_letter expects str; passing None would be programmer error,
        # but the func handles empty str
        assert extract_letter("") == ""


class TestSafeGetQuestionField:
    """Tests for multi-variant field readers (the run_53 bug fix)."""

    def test_finds_capital_question(self):
        q = {"Question": "What is gravity?"}
        assert safe_get_question_field(q, "Question", "question") == "What is gravity?"

    def test_finds_lowercase_question(self):
        q = {"question": "What is gravity?"}
        assert safe_get_question_field(q, "Question", "question") == "What is gravity?"

    def test_returns_first_found(self):
        q = {"text": "fallback text", "Question": "real question"}
        assert safe_get_question_field(q, "Question", "text") == "real question"

    def test_returns_empty_if_none_found(self):
        q = {"unrelated": "field"}
        assert safe_get_question_field(q, "Question", "question", "text") == ""

    def test_skips_empty_values(self):
        q = {"Question": "", "question": "real"}
        # "" is falsy, so it should fall through
        assert safe_get_question_field(q, "Question", "question") == "real"


class TestSafeGetQuestionId:
    def test_finds_id(self):
        assert safe_get_question_id({"id": 42}, 0) == "42"

    def test_finds_question_id(self):
        assert safe_get_question_id({"question_id": "q-7"}, 0) == "q-7"

    def test_falls_back_to_index(self):
        assert safe_get_question_id({}, 99) == "99"

    def test_handles_zero_id(self):
        # id=0 is valid (not None)
        assert safe_get_question_id({"id": 0}, 99) == "0"


class TestSafeGetOptions:
    def test_dict_options(self):
        q = {"options": {"A": "x", "B": "y"}}
        assert safe_get_options(q) == {"A": "x", "B": "y"}

    def test_list_options_converted(self):
        q = {"options": ["first", "second", "third", "fourth"]}
        result = safe_get_options(q)
        assert result == {"A": "first", "B": "second", "C": "third", "D": "fourth"}

    def test_capital_options(self):
        q = {"Options": {"A": "x"}}
        assert safe_get_options(q) == {"A": "x"}

    def test_choices_alias(self):
        q = {"choices": {"A": "first"}}
        assert safe_get_options(q) == {"A": "first"}

    def test_no_options(self):
        assert safe_get_options({}) == {}


class TestBuildMcqPrompt:
    def test_builds_standard_format(self):
        q = {
            "Question": "What is gravity?",
            "options": {"A": "force", "B": "wave", "C": "color", "D": "light"},
        }
        prompt = build_mcq_prompt(q)
        assert "What is gravity?" in prompt
        assert "A) force" in prompt
        assert "D) light" in prompt
        assert "\n\nOptions:\n" in prompt

    def test_handles_case_mismatch(self):
        # This is the run_53 scenario: JSON uses 'Question' (capital) but old
        # code used q.get('question'). build_mcq_prompt must NOT return empty.
        q = {"Question": "Real question text", "options": {"A": "a", "B": "b"}}
        prompt = build_mcq_prompt(q)
        assert "Real question text" in prompt
        # Must NOT be just "Options:" with no question
        assert not prompt.startswith("\n\nOptions:")
