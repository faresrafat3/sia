# Table 17 — Feedback Value Matrix

**Source:** [Theory-08] (from [Idea-001] LEAP)
**Section:** 8.5.3
**Companion figure:** Figure 12

---

## The 2×2 Matrix

| Determinism ↓ \ Scope → | **Narrow** (targeted fix only) | **Broad** (full refactor allowed) |
|---|---|---|
| **High** (compiler / formal verifier) | ✅ **TOP-LEFT — BEST**: compound monotonic improvement. Each fix small, machine-verifiable, never regresses. | ⚠ **TOP-RIGHT — MIXED**: wastes search budget on unnecessary changes, but rarely regresses because verifier catches breakage. |
| **Low** (LLM-as-judge) | ✅ **BOTTOM-LEFT — GOOD**: bounded stochastic gain. Constraint on scope limits drift; gains accumulate with variance but no catastrophic regressions. | ❌ **BOTTOM-RIGHT — WORST**: stochastic drift compounded over generations. Each gen reshapes the agent with no guarantee of improvement; regressions are frequent and large. |

---

## Empirical Calibration

| Quadrant | Concrete System | Measured Gen-over-Gen Δ |
|---|---|---|
| **Top-Left** | LEAP (Lean compiler + LLM reviewer in rejection-only role) | +16.6 (Gemini iterative on Lean-IMO Basic) |
| **Top-Right** | (no clean exemplar in our data) | — |
| **Bottom-Left** | GENESIS A7a `narrow_feedback` (planned, infra wired in Session 5) | Not yet run — prediction: ≥ 0 |
| **Bottom-Right** | GENESIS standard (run_57) — LLM judge + full rewrite allowed | 0 (Gen 1 = Gen 2 = 65%) |
| **Bottom-Right** | GENESIS A3 + feedback (run_58) — same feedback rules | **−10** (Gen 1 = 70%, Gen 2 = 60%) |

---

## The Three Axioms (verbatim from Theory-08)

1. **Determinism Reduces Stochastic Drift.** Feedback deterministic (compiler, formal verifier) يعطي signal واضح ومتسق. يمكن للـ agent أن يثق فيه ويبني عليه. Feedback stochastic (LLM-as-judge) يعطي signal مع noise. كل iteration يضيف noise جديد.

2. **Broad Scope Amplifies Stochastic Noise.** لما الـ feedback scope واسع (refactor entire agent)، الـ stochastic noise يُضرب في عدد الـ changes. كل change فيه احتمال يضر، والـ broad refactor يفرض changes كثيرة.

3. **Narrow Scope Compounds Deterministic Wins.** لما الـ feedback scope ضيق (fix one failure)، الـ deterministic signal يتراكم بشكل monotonic. كل fix يحسن score أو يبقيه ثابتاً.

---

## Migration Path for GENESIS

Current position: **Bottom-Right** (worst quadrant).

Two independent migration steps, each measurable:

| Step | Migration | Implementation | Expected Result |
|---|---|---|---|
| **Step 1** | Bottom-Right → Bottom-Left | Restrict feedback agent to narrow scope (existing `narrow_feedback` mode, infra wired in Session 5) | Gen-over-Gen variance shrinks; Gen 2 ≥ Gen 1 |
| **Step 2** | Bottom-Left → Top-Left | Add deterministic post-feedback verifier with rollback on regression | Gen-over-Gen Δ becomes monotonically ≥ 0 |

After Step 2, GENESIS feedback dynamics should structurally match LEAP's.

---

## Decision Rule for the Paper

| Observed Δ Gen-over-Gen | Quadrant Diagnosis |
|---|---|
| Strictly ≥ 0 across many runs | Top-Left or Bottom-Left |
| Mean ≈ 0, low variance | Top-Right |
| Mean ≈ 0, high variance | Bottom-Right (current GENESIS) |
| Mean < 0, large negative tail | Bottom-Right with broken constraints |

GENESIS run_58 (Gen 2 = −10) is the **canonical Bottom-Right case** in our data.

---

## What This Table Is For (Honest Caveat)

This table is a **conceptual framework with one empirical anchor per known quadrant**. It is *not* a fully-populated 2×2 of controlled GENESIS experiments. The Bottom-Left cell in particular is a *prediction*, awaiting A7a execution. Top-Right has no clean GENESIS exemplar at all.

The framework is useful precisely because:
- It generates **falsifiable predictions** (move to Bottom-Left → Gen 2 ≥ Gen 1).
- It explains **why** GENESIS Gen 2 keeps disappointing (we are sitting in the worst quadrant).
- It gives a **concrete migration path** independent of any deeper architectural redesign.

Once A7a runs are available, this table will be updated with measured numbers in all four cells.

---

## Citation in the Paper

Referenced from Section 8.5.3 — *Theory-08: Feedback Value = f(Determinism, Scope)*.
