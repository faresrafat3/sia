# Theory-08 — Feedback Value = f(Determinism, Scope)

**Source ideas:** [Idea-001] (LEAP) + [Idea-002] (Attribution Rule)
**Related thefts:** T5.92 (LEAP), T5.85 (Aletheia), T5.6 (Self-Refine), T5.5 (Reflexion)
**Related findings:** run_57 Gen 2 = 65% (no gain), run_58 Gen 2 = 60% (regression), LEAP iterative = +16.6%
**Status:** Draft Theory v1.0
**Tag:** `[Theory-08]`

---

## 1. الظاهرة المُلاحظة

في GENESIS:
- **run_57:** Gen 1 = 65%, Gen 2 = 65%. Feedback لم يزد score بأي مقدار.
- **run_58 (A3):** Gen 1 = 70%, Gen 2 = 60%. Feedback **خفض الـ score بـ 10 نقاط**.

في LEAP:
- Iterative (Gemini-3.1-Pro): 20% → 36.6%. Feedback **زاد score بـ 16.6 نقطة**.
- Iterative (Goedel specialized): 10% → 6.6%. Feedback **خفض score بـ 3.4 نقاط**.

**السؤال:** ما الذي يحدد متى feedback يضيف قيمة ومتى يضر؟

## 2. الفرضية المركزية

نقترح أن **قيمة الـ feedback تعتمد على بعدين قابلين للقياس:**

$$
\text{Value}(\text{feedback}) = f(\text{Determinism}, \text{Scope})
$$

حيث:
- **Determinism** = هل الـ feedback machine-verifiable (1) أم subjective LLM judgment (0)؟
- **Scope** = ما حجم التغيير المسموح به؟ من narrow (1 line fix) إلى broad (full refactor).

### الجدول المركزي

| Determinism | Scope | متوقع | مثال |
|---|---|---|---|
| **High (det.)** | **Narrow** | ✅ +ve | LEAP: Lean compiler + fix specific tactic |
| **High (det.)** | **Broad** | ⚠ mixed | Compiler-driven full rewrite (waste budget) |
| **Low (LLM)** | **Narrow** | ✅ +ve | LLM review + targeted answer fix |
| **Low (LLM)** | **Broad** | ❌ -ve | GENESIS current (LLM reviews + full code refactor) |

GENESIS الحالي يقع في الـ **bottom-right (Low det. + Broad scope) = أسوأ مربع**.
LEAP يقع في الـ **top-left (High det. + Narrow scope) = أفضل مربع**.

## 3. الـ Axioms

### Axiom 1 — Determinism Reduces Stochastic Drift
Feedback deterministic (compiler, formal verifier) يعطي signal واضح ومتسق. يمكن للـ agent أن يثق فيه ويبني عليه.

Feedback stochastic (LLM-as-judge) يعطي signal مع noise. كل iteration يضيف noise جديد.

### Axiom 2 — Broad Scope Amplifies Stochastic Noise
لما الـ feedback scope واسع (refactor entire agent)، الـ stochastic noise يُضرب في عدد الـ changes. كل change فيه احتمال يضر، والـ broad refactor يفرض changes كثيرة.

### Axiom 3 — Narrow Scope Compounds Deterministic Wins
لما الـ feedback scope ضيق (fix one failure)، الـ deterministic signal يتراكم بشكل monotonic. كل fix يحسن score أو يبقيه ثابتاً.

## 4. الـ Propositions المشتقة

### Prop 1 — Quadrant Stability
أي system يتحرك من Bottom-Right إلى Top-Left يحسّن feedback value.

GENESIS الحالي → adoption of LEAP-style verifier + narrow scope → expected improvement.

### Prop 2 — Determinism Tax for Stochastic Feedback
عند استخدام stochastic feedback (LLM-as-judge)، لازم نضيف:
- **Verification step** (deterministic) بعد كل feedback application.
- **Rollback mechanism** لو الـ verification فشلت.

بدون هذا الـ "tax"، الـ stochastic feedback يدخل drift.

### Prop 3 — Scope Should Match Confidence
الـ scope المسموح به للـ feedback يجب أن يكون مقيد بـ:
- مستوى الـ determinism في الـ signal.
- حجم الـ failure المرصود.

Failure معين قد يستحق narrow fix فقط، حتى لو الـ feedback agent يريد refactor.

### Prop 4 — Generation 2+ Drift Hypothesis
Feedback drift يظهر بشكل أوضح في Gen 2+ لأن:
- Gen 1 = output direct من meta-agent (single source).
- Gen 2 = output من feedback agent (which modifies Gen 1) → نقطة جديدة للـ noise injection.
- بدون constraints صارمة، كل Gen يضيف stochastic noise.

هذا يفسر ليه run_58 Gen 1 = 70% لكن Gen 2 = 60%: الـ broad feedback في Gen 2 أدخل noise.

## 5. التوقعات القابلة للاختبار

### P1: Narrow feedback improves Gen 2
لو نقيد الـ feedback agent بـ "fix only specific wrong answers, no refactor":
- التوقع: Gen 2 score ≥ Gen 1 score (مهما كان).
- (هذا A7 ablation — designed but not yet executed.)

### P2: Deterministic verifier prevents regression
لو نضيف post-feedback verification step ينقذف الـ change لو فشل:
- التوقع: zero regressions Gen-over-Gen.

### P3: Compound determinism beats stochastic
Stack of small deterministic fixes > single stochastic broad refactor:
- 5 narrow deterministic fixes (1 point each) = +5
- 1 broad stochastic refactor = mean 0, variance high

### P4: Quadrant migration improves measurable
لو نحرك GENESIS من Bottom-Right إلى Top-Left عبر steps:
1. أولاً narrow scope (Top-Right): expected +3 to +5 points.
2. ثم add deterministic check (Top-Left): expected +5 to +10 points.
3. النتيجة الكلية: يقفل الـ -10 gap الحالي.

## 6. الـ Empirical Checks الموجودة

| Check | Quadrant | النتيجة | يدعم Theory-08؟ |
|---|---|---|---|
| GENESIS standard (run_57) | Bottom-Right | Gen 2 = Gen 1 (no gain) | ✅ نعم |
| GENESIS A3 (run_58) | Bottom-Right | Gen 2 < Gen 1 (-10) | ✅ نعم |
| LEAP iterative (Gemini) | Top-Left | +16.6 | ✅ نعم |
| LEAP iterative (Goedel) | Top-Left but model-incapable | -3.4 | ⚠ partial — يكشف interaction مع Theory-07 (specialized model + iteration) |

## 7. الـ Empirical Checks اللي تنقص

| Check | كيف | الأولوية |
|---|---|---|
| A7 narrow feedback | New ablation `narrow_feedback` | high |
| Post-feedback verifier | New `feedback_verifier` step | medium |
| Quadrant comparison study | 4-cell experiment | high (لو ابتدينا runs مرة تانية) |

## 8. الـ Implications

### للورقة
1. **Section 8.5** يحتوي Theory-08 جنباً إلى جنب مع Theory-07.
2. **Figure 12 جديد:** 2x2 quadrant chart يوضح position كل system.
3. **Table 17 جديد:** Feedback value matrix بأرقام محددة.

### للمشروع
1. **Default feedback mode الجديد:** narrow + verified.
2. **Broad refactor mode:** opt-in فقط، يتطلب confidence معينة.
3. **Gen 2+ يصبح conservative** by default.

### للنظرية الأوسع
1. Theory-08 يُعمم على أي iterative agent system.
2. يُربط بـ:
   - `GENESIS_Cognitive_Economy_Theory_AR.md` (broad refactor = expensive without guaranteed value).
   - `GENESIS_Productive_Forgetting_Theory_AR.md` (متى نسمح بـ unlearning يحدث في feedback).

## 9. الروابط

### نظريات داخلية
- **Theory-07 (Pipeline as Memory):** Theory-08 يُكمل Theory-07. الـ memory-based pipeline (Theory-07) + narrow deterministic feedback (Theory-08) = strongest configuration.
- **Cognitive Economy:** Broad refactor = high cost, uncertain reward.
- **Productive Forgetting:** Feedback drift = unintentional forgetting of correct answers.

### سرقات
- **T5.92 (LEAP):** Canonical example على narrow deterministic feedback.
- **T5.85 (Aletheia):** Generate-Verify-Revise = narrow scope, deterministic verifier.
- **T5.5 (Reflexion):** Memory-based reflection = pull-based, narrow.
- **T5.6 (Self-Refine):** Generate-critique-refine = depends on scope of critique.

### قسم Concept Engine
الـ Concept Engine بتاعنا يطبق Prop 3 implicitly: concept changes scoped to specific evidence patterns. ربط مباشر بـ Theory-09 (next file).

## 10. الروابط بأقسام الورقة

- **Section 6.4** (run_57 results): يُذكر Theory-08 لتفسير feedback drift.
- **Section 6.6** (run_58 A3): يُذكر Theory-08 لتفسير Gen 2 regression.
- **Section 7.x** (Analysis): Theory-08 كقسم فرعي.
- **Section 8.5** (Contrast with LEAP): Theory-08 + Theory-07 معاً.
- **Section 10** (Future Work): A7 (narrow feedback) و A8 (verified feedback).

## 11. Citation

```
Theory-08 — Feedback Value = f(Determinism, Scope).
Internal theory developed in PAPER/theory/08_*.md.
Source ideas: [Idea-001] (LEAP), [Idea-002] (Attribution Rule).
Empirical anchor: GENESIS run_58 Gen 2 regression vs LEAP iterative gain.
```

## 12. Status

- ✅ Drafted (Session 7).
- ⏳ Pending Fares review.
- ⏳ Pending Figure 12 (quadrant chart) و Table 17.
- ⏳ ATTRIBUTION_MAP.md update.
