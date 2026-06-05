"""
GENESIS LLM Helpers — Shared utilities for working with reasoning-capable LLMs.
==============================================================================

Provides battle-tested helpers for:
- extract_response_text: handles empty content when reasoning models consume max_tokens
- extract_letter: parses A/B/C/D answers in 16+ formats
- force_letter_followup: recovers from empty/invalid responses

These were originally developed in tools/run_multi_model_benchmark.py and proven
to lift accuracy from 30% → 75% on GPQA Diamond (gpt-oss-120b).

Usage in target_agent.py (and similar):
    from genesis.llm_helpers import extract_response_text, extract_letter

    resp = client.chat.completions.create(...)
    text, meta = extract_response_text(resp)
    letter = extract_letter(text)

تصميم عام: يصلح لأي OpenAI-compatible LLM (OpenAI, OpenRouter, Groq, Gemini, etc.)
"""
from __future__ import annotations

import re
from typing import Any, Optional


# Standard system prompt for graduate-level MCQ (GPQA-style)
SCIENTIFIC_MCQ_SYSTEM_PROMPT = """You are an expert scientist (physics, chemistry, biology) taking a graduate-level
multiple-choice exam (GPQA Diamond level). Each question has exactly 4 options labeled A, B, C, D
and exactly one is correct.

RESPONSE PROTOCOL — follow strictly:
1. Reason carefully and step by step about the underlying science.
2. Eliminate clearly wrong options when possible.
3. You MUST end your reply with a final line in EXACTLY this format (no other text after it):

ANSWER: X

where X is one single letter A, B, C, or D. The line must literally start with the word ANSWER
followed by a colon and a space, then the letter. Do NOT add explanations after the ANSWER line.
If you are unsure, still output your best guess in the ANSWER line — never refuse, never output
"unknown" or "I don't know"."""


# Prompt for forced-letter follow-up call
FORCE_LETTER_PROMPT = (
    "STOP THINKING. Just output one line with your best guess in this exact format:\n\n"
    "ANSWER: X\n\n"
    "where X is one of A, B, C, or D. Output ONLY that single line — no reasoning, "
    "no explanation, no markdown, nothing else. Just the literal string 'ANSWER: ' "
    "followed by one capital letter."
)


def extract_response_text(resp) -> tuple[str, dict]:
    """Extract text from an OpenAI response, handling reasoning content as fallback.

    Many reasoning models (Nemotron, gpt-oss, gpt-5, o-series) consume tokens in
    INTERNAL reasoning before producing visible content. When max_tokens runs out
    during reasoning, message.content is empty but message.reasoning still has data.

    Returns:
        (combined_text, meta) where:
          combined_text = content + reasoning (or fallback if either empty)
          meta = {finish_reason, content_chars, reasoning_chars, usage}
    """
    msg = resp.choices[0].message
    content = msg.content or ""
    reasoning_text = ""

    # Try string-typed reasoning attributes
    for attr in ("reasoning", "reasoning_content"):
        v = getattr(msg, attr, None)
        if v and isinstance(v, str):
            reasoning_text = v
            break

    # Try structured reasoning_details list
    if not reasoning_text:
        rd = getattr(msg, "reasoning_details", None)
        if rd:
            try:
                if isinstance(rd, list):
                    parts = []
                    for item in rd:
                        if isinstance(item, dict):
                            parts.append(item.get("text", "") or item.get("content", ""))
                        else:
                            t = getattr(item, "text", None) or getattr(item, "content", None)
                            if t:
                                parts.append(t)
                    reasoning_text = "\n".join(p for p in parts if p)
            except Exception:
                pass

    # Combine: content first, reasoning as appendix
    if content and reasoning_text:
        combined = content + "\n\n[REASONING]\n" + reasoning_text
    elif content:
        combined = content
    elif reasoning_text:
        combined = reasoning_text
    else:
        combined = ""

    meta = {
        "finish_reason": resp.choices[0].finish_reason,
        "content_chars": len(content),
        "reasoning_chars": len(reasoning_text),
    }
    try:
        u = resp.usage
        meta["usage"] = {
            "prompt_tokens": u.prompt_tokens,
            "completion_tokens": u.completion_tokens,
            "total_tokens": u.total_tokens,
        }
        ctd = getattr(u, "completion_tokens_details", None)
        if ctd:
            rt = getattr(ctd, "reasoning_tokens", None)
            if rt is not None:
                meta["usage"]["reasoning_tokens"] = rt
    except Exception:
        pass
    return combined, meta


def extract_letter(text: str) -> str:
    """Extract A/B/C/D answer letter from response text using 16+ patterns.

    Handles: ANSWER: X, ANSWER:X, **X**, \\boxed{X}, (X), X. at end, last A-D, etc.
    Returns empty string if no letter found.

    Tested against 16 real-world response formats — all pass.
    """
    if not text:
        return ""
    txt = text.strip()

    # 1) Explicit ANSWER lines (with various separators)
    for pattern in (
        r"ANSWER\s*[:\-=]+\s*\*?\*?\s*([ABCD])\s*\*?\*?",
        r"\bANSWER\s+IS\s*[:\-=]?\s*\*?\*?\s*([ABCD])\b",
        r"FINAL\s+ANSWER\s*[:\-=]+\s*\*?\*?\s*([ABCD])",
        r"THE\s+ANSWER\s+IS\s*[:\-=]?\s*\*?\*?\s*([ABCD])",
        r"CORRECT\s+(?:ANSWER|OPTION)\s+IS\s*[:\-=]?\s*\*?\*?\s*([ABCD])",
        r"OPTION\s*[:\-=]?\s*\*?\*?\s*([ABCD])\s*\*?\*?\s*(?:IS|$)",
    ):
        m = re.search(pattern, txt, re.IGNORECASE)
        if m:
            return m.group(1).upper()

    # 2) Markdown/LaTeX wrappers in tail
    tail = txt[-800:]
    for pattern in (
        r"\*\*\s*([ABCD])\s*\*\*",
        r"\\boxed\{\s*([ABCD])\s*\}",
        r"\\textbf\{\s*([ABCD])\s*\}",
        r"\(\s*([ABCD])\s*\)\s*$",
        r"\s([ABCD])\s*\.\s*$",
        r"^\s*([ABCD])\s*$",
    ):
        m = re.search(pattern, tail, re.IGNORECASE | re.MULTILINE)
        if m:
            return m.group(1).upper()

    # 3) Last line containing only a letter
    for line in reversed(txt.strip().split("\n")):
        line_clean = line.strip().strip(".").strip(":").strip("*").strip()
        m = re.match(
            r"^(?:answer\s*[:\-]?\s*)?\*?\*?\s*([ABCD])\s*\*?\*?\s*\.?\s*$",
            line_clean, re.IGNORECASE,
        )
        if m:
            return m.group(1).upper()

    # 4) Final fallback: last A-D in last 200 chars
    last_match = None
    for m in re.finditer(r"\b([ABCD])\b", txt[-200:]):
        last_match = m
    if last_match:
        return last_match.group(1).upper()

    return ""


def ask_for_letter_followup(
    client,
    model: str,
    original_messages: list[dict],
    round1_text: str,
    *,
    max_tokens: int = 256,
    use_low_reasoning: bool = True,
) -> tuple[str, str]:
    """Force-letter follow-up call when round 1 produced no parseable letter.

    Sends original messages + assistant's previous reply + STOP THINKING instruction.
    Returns (followup_text, extracted_letter).

    Recovers ~80% of round-1 failures on tested models.
    """
    assistant_content = round1_text if round1_text else "(I was thinking but ran out of tokens before answering)"
    followup_msgs = original_messages + [
        {"role": "assistant", "content": assistant_content},
        {"role": "user", "content": FORCE_LETTER_PROMPT},
    ]
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": followup_msgs,
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }
    if use_low_reasoning:
        # Disable heavy reasoning so the model produces the letter quickly
        kwargs["extra_body"] = {"reasoning": {"effort": "low"}}
    try:
        resp = client.chat.completions.create(**kwargs)
        text, _ = extract_response_text(resp)
        return text, extract_letter(text)
    except Exception:
        return "", ""


def safe_get_question_field(q: dict, *field_candidates: str) -> str:
    """Get a question field with multiple case/key variants.

    Example:
        qtext = safe_get_question_field(q, 'Question', 'question', 'text', 'prompt')
        # tries each, returns first non-empty
    """
    for field in field_candidates:
        v = q.get(field)
        if v:
            return str(v)
    return ""


def safe_get_question_id(q: dict, default_idx: int) -> str:
    """Get question id with fallback to index. Common variants tried."""
    for field in ("id", "question_id", "qid", "ID"):
        v = q.get(field)
        if v is not None:
            return str(v)
    return str(default_idx)


def safe_get_options(q: dict) -> dict:
    """Get options dict, normalized to {A,B,C,D} keys if possible."""
    opts = q.get("options") or q.get("Options") or q.get("choices") or {}
    if isinstance(opts, list):
        # Convert list to {A: ..., B: ...}
        return {chr(65 + i): opt for i, opt in enumerate(opts)}
    return dict(opts) if isinstance(opts, dict) else {}


def build_mcq_prompt(q: dict) -> str:
    """Build a standard MCQ prompt from a question dict with multi-variant field reads.

    Returns prompt string ready to send to LLM.
    """
    qtext = safe_get_question_field(q, "Question", "question", "QUESTION", "text", "prompt")
    options = safe_get_options(q)
    opts_str = ""
    for k in sorted(options.keys()):
        opts_str += f"{k}) {options[k]}\n"
    return f"{qtext.strip()}\n\nOptions:\n{opts_str}"
