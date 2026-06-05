# Figure 11 — The 110-Point Architecture Impact Gap (LEAP vs GENESIS)

**Source:** [Idea-001] (LEAP paper, arXiv 2606.03303)
**Theories:** [Theory-07], [Theory-08], [Theory-09]
**Section:** 8.5.1
**Tag:** Figure 11

---

## The Headline Visualization

```
Architecture Impact (Δ vs direct LLM baseline, same model class)

           +120 ┐
                │
           +100 ┤  ●  LEAP (Putnam 2025)
                │
            +80 ┤
                │
            +60 ┤  ●  LEAP (Lean-IMO Basic, +63.3)
                │
            +40 ┤
                │  ●  LEAP (Lean-IMO Advanced, +53.4)
            +20 ┤
                │
              0 ┼─────────────────────────────────────  ← direct LLM baseline (no architecture)
                │
            −20 ┤  ●  GENESIS A3 Gen1 (run_58, −5)
                │  ●  GENESIS standard (run_57, −10)
                │  ●  GENESIS A3 Gen2 (run_58, −15)
            −40 ┤
                │
           ── LEAP region (memory-based pipeline + deterministic narrow feedback) ──
           ── GENESIS region (injection-based pipeline + stochastic broad feedback) ──
```

## The Numerical Spread

| System | Configuration | Δ (Architecture Impact) |
|---|---|---|
| LEAP | Putnam 2025 | **+100.0** |
| LEAP | Lean-IMO Basic | +63.3 |
| LEAP | Lean-IMO Advanced | +53.4 |
| —— | Zero line (direct LLM) | 0 |
| GENESIS | A3 Gen 1 (no_pipeline) | −5.0 |
| GENESIS | Standard (run_57) | −10.0 |
| GENESIS | A3 Gen 2 (no_pipeline + feedback) | −15.0 |

**Total spread: 115 points** (from LEAP's +100 down to GENESIS A3 Gen2's −15).
**Reported gap: 110 points** (between LEAP +100 and GENESIS standard −10).

## What This Picture Says

The diagram is intentionally stark. Both systems:

- Use **general-purpose foundation models** as the reasoning backbone.
- Wrap that model in an **agentic framework**.
- Are evaluated on **graduate-level reasoning benchmarks**.

Yet the architecture impact differs by more than the entire scoring range of most benchmarks. Something **structural** is responsible.

## The Three-Line Bracket Below the Plot

The bracketed regions below the zero line identify the structural property each system is in:

- **LEAP region:** memory-based pipeline (DAG memoization) + deterministic narrow feedback (Lean compiler + LLM reviewer with rejection-only role).
- **GENESIS region:** injection-based pipeline (tier/theory/blackboard pushed into prompts) + stochastic broad feedback (LLM-as-judge with full refactor scope).

These regions correspond to the top-left vs bottom-right quadrants of Theory-08's Feedback Value Matrix (Figure 12) and to Type A vs Type B of Theory-07's Pipeline taxonomy.

## What This Picture Does NOT Say

This figure is a **structural comparison**, not a model-quality comparison. It does **not** claim:
- That LEAP is universally better than GENESIS.
- That formal math is harder than scientific MCQ (or vice versa).
- That Gemini-3.1-Pro is better than gpt-oss-120b (we have no direct comparison).

The claim is narrower and stronger:

> **At fixed model class and similar benchmark difficulty regime, structural design of the orchestration pipeline determines the sign and magnitude of architecture impact.**

## Citation in the Paper

Referenced from Section 8.5.1 — *The Headline Contrast*.
