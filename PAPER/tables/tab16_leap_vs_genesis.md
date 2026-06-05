# Table 16 — LEAP vs GENESIS Architecture Impact Comparison

**Source:** [Idea-001] (LEAP paper)
**Section:** 8.5.1
**Companion figure:** Figure 11

---

## Main Comparison

| System | Benchmark | n | Direct LLM | + Agentic Framework | Δ (Architecture Impact) |
|---|---|---|---|---|---|
| **LEAP** [T5.92] | Putnam 2025 | 12 | 0% (0/12) | **100%** (12/12) | **+100.0** |
| **LEAP** [T5.92] | Lean-IMO Basic | 30 | 20.0% | **83.3%** | **+63.3** |
| **LEAP** [T5.92] | Lean-IMO Advanced | 30 | 3.3% | **56.7%** | **+53.4** |
| GENESIS (run_57) | GPQA-20 | 20 | 75.0% | 65.0% | −10.0 |
| GENESIS A3 Gen1 (run_58) | GPQA-20 | 20 | 75.0% | 70.0% | −5.0 |
| GENESIS A3 Gen2 (run_58) | GPQA-20 | 20 | 75.0% | 60.0% | −15.0 |

**Spread:** +100 (best LEAP) to −15 (worst GENESIS) = **115-point range** at fixed model class.

---

## Side-by-Side Architectural Properties

| Property | LEAP | GENESIS (standard) |
|---|---|---|
| **Base model** | Gemini-3.1-Pro (general-purpose, frontier) | gpt-oss-120b (general-purpose, frontier-grade) |
| **Domain** | Formal mathematics (Lean) | Scientific MCQ (GPQA Diamond) |
| **Pipeline type** [Theory-07] | **Memory** (DAG, pull-based) | **Decision Injection** (signals pushed into prompts) |
| **Verification** | Lean compiler (deterministic, machine-checkable) | Constitutional check + execution log analysis (mostly heuristic) |
| **Feedback signal source** [Theory-08] | Compiler errors + LLM reviewer (rejection-only) | LLM-as-judge (full rewrite scope) |
| **Feedback scope** [Theory-08] | Narrow (per-tactic, per-lemma) | Broad (entire target_agent.py rewritable) |
| **Anticipatory abstraction** [Theory-09] | Anticipatory lemma planning (active) | Concept Engine (reactive only, not anticipatory) |
| **Search structure** | AND-OR DAG with memoization | Linear gen-over-gen (no memoization across generations) |
| **State persistence** | Full DAG persists; lemmas reused across branches | Each generation independent (no cross-gen memory of lemmas) |
| **Compute per problem (LLM calls)** | 71–3,000 per problem | ~10–30 per problem (much lower) |

---

## Ablation-Level Sub-Comparisons

| Ablation | LEAP result | GENESIS analog | GENESIS result |
|---|---|---|---|
| **Iteration helps general models** | Gemini iterative: 20% → 36.6% (+16.6) | A3 single-gen (no iterative feedback) | 70% — but Gen 2 drops to 60% (drift) |
| **Iteration hurts specialized models** | Goedel iterative: 10% → 6.6% (−3.4) | (no specialized model tested in GENESIS) | N/A |
| **DAG vs Flat memory** | Basic: 73.3% → 83.3% (+10), Advanced: 40% → 56.7% (+16.7) | (no DAG implemented in GENESIS) | N/A — would require Theory-09 implementation |
| **LLM reviewer rejection** | Without: fails after 8 rollouts on Putnam A5. With: solves in 2 rollouts. | (no LLM reviewer in GENESIS) | N/A — would require Track A.2 implementation |

---

## What the Comparison Does NOT Establish

To preserve scientific honesty, we are explicit about what this table does *not* show:

- It does **not** compare formal math difficulty against scientific MCQ difficulty directly. The Δ column is normalized to each system's own direct-LLM baseline, so cross-benchmark difficulty cancels out.
- It does **not** claim Gemini-3.1-Pro is better than gpt-oss-120b. The architecture impact (Δ) is computed against each model's own baseline.
- It does **not** claim LEAP would dominate GENESIS if applied to GPQA. We do not have empirical evidence for that.

The valid claim is structural: **the architectural design choices in the right-hand "Properties" column predict the sign of Δ in the top half of the table.** Theories 07/08/09 articulate which design choices and why.

---

## Citation in the Paper

Referenced from Section 8.5.1 — *The Headline Contrast*.
