# Table 12: Question-by-Question Delta Analysis — Pure Baseline vs GENESIS (`run_57`)

This table answers the most useful immediate research question:

> **Which exact questions does GENESIS help, and which does it hurt, relative to the pure baseline?**

## Category A — Stable wins (all systems correct)

These are the questions where the model is strong enough that architecture does not change the outcome.

| Q# | Domain | Subdomain | Pure | Gen 1 | Gen 2 | Note |
|---|---|---|---|---|---|---|
| 1 | Physics | General | ✓ | ✓ | ✓ | Stable easy physics |
| 3 | Physics | Quantum Mechanics | ✓ | ✓ | ✓ | Stable easy |
| 4 | Physics | Electromagnetism | ✓ | ✓ | ✓ | Stable easy |
| 5 | Physics | Quantum Mechanics | ✓ | ✓ | ✓ | Stable easy |
| 6 | Physics | Quantum Mechanics | ✓ | ✓ | ✓ | Stable easy |
| 10 | Physics | Astrophysics | ✓ | ✓ | ✓ | Stable easy |
| 12 | Physics | Particle Physics | ✓ | ✓ | ✓ | Stable easy |
| 14 | Biology | Molecular Biology | ✓ | ✓ | ✓ | Stable medium |
| 15 | Physics | General | ✓ | ✓ | ✓ | Stable medium |
| 17 | Chemistry | General Chemistry | ✓ | ✓ | ✓ | Stable non-organic chemistry |
| 20 | Physics | Quantum Mechanics | ✓ | ✓ | ✓ | Stable easy |

**Count:** 11/20

---

## Category B — GENESIS helps relative to baseline

These are the rare questions where architecture improves over the direct model baseline.

| Q# | Domain | Pure | Gen 1 | Gen 2 | Interpretation |
|---|---|---|---|---|---|
| 7 | Physics | ✗ | ✓ | ✓ | Architecture consistently helps on this physics question |
| 2 | Chemistry | ✗ | ✗ | ✓ | Feedback repaired one chemistry miss, but only in Gen 2 |

**Count:**
- Gen 1 gains vs pure: **1 question** (Q7)
- Gen 2 gains vs pure: **2 questions** (Q7, Q2)

---

## Category C — GENESIS hurts relative to baseline

These are the questions where the architecture loses information or adds harmful overhead.

| Q# | Domain | Pure | Gen 1 | Gen 2 | Interpretation |
|---|---|---|---|---|---|
| 9 | Chemistry | ✓ | ✗ | ✗ | Persistent chemistry degradation |
| 13 | Chemistry | ✓ | ✗ | ✗ | Persistent chemistry degradation |
| 19 | Chemistry | ✓ | ✗ | ✗ | Persistent chemistry degradation |
| 8 | Biology | ✓ | ✓ | ✗ | Feedback introduced regression |

**Count:**
- Gen 1 losses vs pure: **3 questions** (Q9, Q13, Q19)
- Gen 2 losses vs pure: **4 questions** (Q8, Q9, Q13, Q19)

---

## Category D — Persistent failures (all systems wrong)

These are not architecture-specific losses; they are hard questions for the base model itself.

| Q# | Domain | Subdomain | Pure | Gen 1 | Gen 2 | Interpretation |
|---|---|---|---|---|---|---|
| 11 | Biology | Molecular Biology | ✗ | ✗ | ✗ | Persistent biology blind spot |
| 16 | Chemistry | Organic Chemistry | ✗ | ✗ | ✗ | Persistent hard chemistry |
| 18 | Physics | General | ✗ | ✗ | ✗ | Persistent hard physics outlier |

**Count:** 3/20

---

## Category E — Feedback swap (same total score, different mistakes)

This is the most important local effect of the feedback loop in `run_57`.

| Change from Gen 1 → Gen 2 | Effect |
|---|---|
| **Q2:** wrong → correct | Improvement |
| **Q8:** correct → wrong | Regression |
| Net score change | **0** |

**Interpretation:** the feedback agent is currently producing **error redistribution**, not net improvement.

---

## Structural Summary

| Pattern | Count |
|---|---:|
| Stable wins (all correct) | 11 |
| Persistent failures (all wrong) | 3 |
| Questions where GENESIS can help | 2 |
| Questions where GENESIS hurts | 4 |

This means the current architecture is operating in a narrow region:

- it preserves easy wins,
- cannot fix the hardest questions,
- occasionally improves a hard item,
- but introduces enough new mistakes to stay below baseline.

---

## Core scientific takeaway

The **−10 point architecture gap** is not spread uniformly across the benchmark.
It is concentrated in a small set of questions — **mostly Chemistry Organic** — where GENESIS converts baseline wins into architecture losses.

So the next ablation question is not:

> “Why is GENESIS generally worse?”

but rather:

> **“Why does GENESIS preserve Physics, occasionally help, but systematically damage several Chemistry wins?”**
