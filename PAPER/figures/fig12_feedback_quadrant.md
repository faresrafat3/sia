# Figure 12 — Feedback Value Quadrant (Theory-08)

**Source:** [Theory-08] from [Idea-001] (LEAP)
**Section:** 8.5.3
**Tag:** Figure 12

---

## The 2×2 Quadrant

```
                            SCOPE
                NARROW (targeted fix only)     BROAD (full refactor allowed)
              ┌───────────────────────────────┬───────────────────────────────┐
              │                                │                                │
        HIGH  │   ✅  TOP-LEFT                │   ⚠  TOP-RIGHT                │
        (det. │   compound monotonic           │   wastes budget without harm   │
         compiler│   improvement                  │                                │
       / formal │                                │                                │
       verifier)│   ● LEAP                       │                                │
              │     (Lean compiler + LLM       │                                │
DETERMINISM  │      reviewer in rejection      │                                │
              │      role only)                 │                                │
              │                                │                                │
              ├───────────────────────────────┼───────────────────────────────┤
              │                                │                                │
        LOW   │   ✅  BOTTOM-LEFT             │   ❌  BOTTOM-RIGHT            │
        (LLM- │   bounded stochastic gain      │   stochastic drift compounded  │
         as-  │                                │   over generations             │
         judge)│                                │                                │
              │   ● GENESIS A7a (planned)      │   ● GENESIS standard (run_57)  │
              │     narrow_feedback mode        │   ● GENESIS A3 + feedback     │
              │     (infra wired, not run)      │     (run_58 Gen 2: 70 → 60)   │
              │                                │                                │
              └───────────────────────────────┴───────────────────────────────┘
```

## Position Justification

| Quadrant | Position Marker | Evidence |
|---|---|---|
| Top-Left | LEAP | Lean compiler is deterministic. LLM reviewer is constrained to *accept/reject*, not rewrite. Per-step scope is narrow (one lemma, one proof attempt). LEAP iterative result: 20% → 36.6%. |
| Bottom-Right | GENESIS standard (run_57) | LLM judges generated agent; can rewrite entire target_agent.py. No deterministic post-feedback verifier. Result: Gen 2 = Gen 1 (no gain). |
| Bottom-Right | GENESIS A3 + feedback (run_58) | Same broad/stochastic feedback applied to A3 base. Result: 70% → 60% (active regression). |
| Bottom-Left | A7a (planned) | `narrow_feedback` mode constrains scope but feedback is still LLM-based (stochastic). Predicted: ≥ Gen 1 score. |

## The Migration Path

**GENESIS's current position → desired position:**

```
            BOTTOM-RIGHT (current GENESIS)
                    │
                    │  (1) Narrow the scope
                    ▼
              BOTTOM-LEFT (A7a)
                    │
                    │  (2) Add deterministic post-verifier
                    ▼
              TOP-LEFT (LEAP-equivalent)
```

Each migration step is independently testable. The path is monotonic — no step should make things worse.

## The Underlying Axioms

1. **Determinism Reduces Stochastic Drift.** Compiler signals are consistent across iterations; LLM judgments inject fresh noise each generation.
2. **Broad Scope Amplifies Stochastic Noise.** Each allowed change has independent risk; broad refactors compound that risk multiplicatively.
3. **Narrow Scope Compounds Deterministic Wins.** Bounded fixes on deterministic signals are monotonic — they never make things worse.

## The Quantitative Prediction

For each quadrant, predicted Gen-over-Gen score change:

| Quadrant | Predicted ΔGen | Observed (where measured) |
|---|---|---|
| Top-Left | **Strictly ≥ 0** (monotonic) | LEAP iterative: +16.6 ✅ matches |
| Bottom-Left | **≥ 0 in expectation, ±small variance** | A7a: not yet run |
| Top-Right | **≥ 0 in expectation, but compute-wasteful** | Not directly tested |
| Bottom-Right | **Mean ≈ 0, large negative variance** | GENESIS run_57: 0 / run_58: −10 ✅ matches |

## Citation in the Paper

Referenced from Section 8.5.3 — *Theory-08: Feedback Value = f(Determinism, Scope)*.
