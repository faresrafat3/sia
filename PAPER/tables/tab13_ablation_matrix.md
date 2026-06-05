# Table 13: Ablation Matrix — Explaining the Remaining 10-Point Architecture Gap

## Objective

After `run_57`, the scientific question is no longer **"Is GENESIS broken?"**
That is answered.

The new question is:

> **Which exact architectural components account for the remaining gap between `pure baseline = 75.0%` and `GENESIS = 65.0%`?**

This table defines the next ablation sequence in a paper-friendly, claim-driven way.

---

## A. Core ablation ladder

| Ablation ID | Configuration | What is disabled / changed | Expected score range | Main hypothesis being tested | What a strong result would mean |
|---|---|---|---:|---|---|
| **A0** | Pure baseline | No GENESIS at all | **75.0** | Reference ceiling for this subset | The model alone is the comparison anchor |
| **A1** | GENESIS minimal | Meta-agent generated target agent, but **no feedback**, **no evo**, **no constitutional optimization pressure** beyond execution | 68–74 | Is the largest remaining loss caused simply by orchestration overhead around a single generated agent? | If A1 ≈ 75, then feedback/evo/constitutional are the real problem |
| **A2** | Current Gen 1 replay | Full current Gen 1 behavior (`run_57 gen_1`) | **65.0 observed** | Baseline for architecture-side analysis | Starting point for all deltas |
| **A3** | No cognitive pipeline leverage | Keep agent scaffold, but remove or neutralize `run_minimal_pipeline` influence on answer generation | 68–76 | Does the pipeline currently add noisy context rather than useful signal? | If A3 > A2 clearly, pipeline overhead is a major culprit |
| **A4** | No feedback loop | Run only Gen 1 on the subset, skip feedback agent entirely | 65–70 | Is feedback currently net-neutral or net-harmful? | If A4 ≥ Gen2, feedback is not helping yet |
| **A5** | No constitutional pressure | Skip constitutional evaluation or stop feeding its findings into the optimization loop | 65–72 | Are quality/safety constraints pulling optimization away from benchmark accuracy? | If A5 > Gen2, constitutional pressure is too dominant |
| **A6** | No evolutionary discovery | Full run but without `--use_evolutionary_discovery` | 63–70 | Is AlphaEvolve-style search helping, hurting, or just consuming cycles? | If A6 > current, evo is noise; if A6 < current, evo adds some value |
| **A7** | Feedback-only prompt simplification | Keep feedback agent, but constrain it to only fix measured wrong-answer patterns instead of broad refactors | 67–74 | Is feedback drift caused by over-broad code rewriting? | If A7 > current Gen2, feedback scope is the problem |
| **A8** | Domain-targeted chemistry mode (research ablation, not product router) | Same model, same architecture, but feedback/meta prompts emphasize chemistry-specific step verification only | 68–76 | Is the architecture gap concentrated enough that Chemistry-focused scaffolding fixes can erase it? | If A8 closes most of the gap, the problem is domain-localized, not global |

---

## B. Priority ordering

Not all ablations are equally useful. This is the recommended order:

| Priority | Ablation | Why it comes first |
|---|---|---|
| **1** | **A3 — No pipeline leverage** | The question-level delta analysis shows GENESIS preserves Physics but damages Chemistry. That pattern is consistent with added context/noise more than catastrophic generation failure. |
| **2** | **A4 — No feedback loop** | Gen 2 changed the error pattern but did not improve score. This strongly suggests feedback drift without net gain. |
| **3** | **A6 — No evolutionary discovery** | Evo may be computationally expensive yet irrelevant on a 20Q subset. We need to know if it adds anything before attributing value to it. |
| **4** | **A5 — No constitutional pressure** | Constitutional checks may be optimizing for code quality rather than question accuracy. |
| **5** | **A7 — Feedback-only simplification** | Once we know feedback is the issue, we test whether narrow feedback beats broad rewriting. |
| **6** | **A8 — Domain-targeted chemistry mode** | This is a more advanced research intervention once the root cause is clearer. |

---

## C. Question-level expectations

Using the already completed delta map, we can pre-register what to watch.

### Questions where GENESIS currently hurts
- **Q9, Q13, Q19** — Chemistry Organic (persistent architecture losses)
- **Q8** — Biology regression introduced by feedback in Gen 2

### Questions where GENESIS currently helps
- **Q7** — Physics gain in both generations
- **Q2** — Chemistry gain only after feedback (Gen 2)

### Persistent failures regardless of condition
- **Q11, Q16, Q18**

So a successful ablation should primarily do one of two things:

1. **recover one or more of Q9, Q13, Q19**, or
2. **preserve the gains on Q7 / Q2 without introducing new regressions**.

---

## D. Decision rules

This is the most important part for paper honesty.

| Outcome | Interpretation | Paper claim |
|---|---|---|
| Ablation raises score to **70–74%** | We found a major harmful component, but architecture still not above baseline | "Current architecture is over-specified; simplified variants are stronger." |
| Ablation reaches **75%** | We eliminated the architecture gap but still did not beat the model | "Architecture can be made neutral, but not yet value-adding." |
| Ablation exceeds **75%** | We found a truly value-adding configuration | "Specific orchestrated configuration improves over pure inference." |
| All ablations remain **<75%** | Current architecture family is still net-negative on this task | "GENESIS remains below the direct baseline under current design assumptions." |

---

## E. Paper-style interpretation strategy

This ablation matrix prevents us from making vague claims like:
- "feedback might be bad"
- "pipeline maybe adds overhead"
- "evolutionary discovery is probably not helping"

Instead, every component gets a falsifiable test.

The scientific standard becomes:

> **No component receives credit or blame without a controlled score delta on the same 20-question subset.**

That rule keeps the paper strong, honest, and defensible.
