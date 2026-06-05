# Theory-07 — Pipeline as Memory vs Pipeline as Decision Injection

**Source ideas:** [Idea-001] (LEAP paper) + [Idea-002] (Creative Attribution Rule)
**Related thefts:** T5.92 (LEAP), T5.84 (AlphaEvolve), T5.85 (Co-Scientist), T5.86 (Aletheia)
**Related findings:** Empirical Discovery #6 (Pipeline overhead) + run_57 (-10) + run_58 A3 (+5)
**Status:** Draft Theory v1.0
**Tag للاستخدام في الورقة:** `[Theory-07]`

---

## 1. الظاهرة المُلاحظة (Observation)

في GENESIS، عندنا تناقض حاد بين نتيجتين مرتبطتين:

| النتيجة | Pure baseline | GENESIS (full) | Δ |
|---|---|---|---|
| GPQA-20 على gpt-oss-120b | 75% | 65% | **-10** |
| A3 (no_pipeline) | 75% | 70% | **-5** (recovered +5) |

في المقابل، LEAP على نفس class of base model (Gemini-3.1-Pro):

| النتيجة | Direct LLM | LEAP (full pipeline) | Δ |
|---|---|---|---|
| Putnam 2025 | 0% | 100% | **+100** |
| Lean-IMO Basic | 20% | 83.3% | **+63.3** |

**السؤال المركزي:** ليه الـ pipeline في GENESIS تضر، بينما الـ pipeline في LEAP تضيف +100؟

كلاهما "pipeline" بمعنى ما، وكلاهما يستخدم general-purpose foundation model.

## 2. الفرضية المركزية

نقترح أن **الـ pipeline ليست شيئاً واحداً** — هي تقع على spectrum من نوعين فلسفياً مختلفين:

### النوع A — Pipeline as Memory (مفيدة)

الـ pipeline تعمل كـ **ذاكرة هيكلية للـ state**:
- تحفظ ما تم إثباته/حله/اكتشافه.
- توفر context عند الطلب دون فرض signals.
- الـ LLM يستدعي ما يريد منها، متى يريد.
- **علاقة LLM ↔ Pipeline:** الـ LLM يقود، الـ pipeline يخدم.

**مثال LEAP:** الـ DAG memoization
- DAG = memory of proven lemmas + open goals + dependencies.
- الـ LLM يطلب الـ state عند بداية كل attempt.
- لا signals من الـ DAG تُحقن في الـ answer generation.
- النتيجة: +100 نقطة.

### النوع B — Pipeline as Decision Injection (ضارة في الـ general case)

الـ pipeline تعمل كـ **مصدر signals تحقن في الـ prompt**:
- تحسب tier decisions, theory predictions, blackboard signals.
- تحقن هذه الـ signals في كل question prompt.
- الـ LLM يضطر لـ "weigh" هذه الـ signals مع reasoning الأصلي.
- **علاقة LLM ↔ Pipeline:** الـ pipeline تقود، الـ LLM يطيع/يقاوم.

**مثال GENESIS (current):** الـ cognitive pipeline في answer generation
- `tier_decision`, `theory_prediction`, `blackboard`, `verification` كلها تُحقن.
- الـ LLM يحصل على noise إضافي قبل ما يجاوب.
- النتيجة: -10 نقطة (و +5 لما شيلناها في A3).

## 3. الـ Axioms

### Axiom 1 — Capacity Asymmetry
General-purpose foundation models عندها **enormous prior knowledge** + reasoning capacity. أي signal خارجي تحقن في الـ prompt يجب أن يكون **decision-useful**، وإلا فهو noise يقلل signal-to-noise ratio للـ reasoning.

### Axiom 2 — Memory is Pull, Decision is Push
الـ memory access هو **pull-based** (الـ LLM يقرر متى يستدعي). الـ decision injection هو **push-based** (الـ pipeline يفرض على كل request).

Push-based يحتاج justification أعلى بكثير من pull-based.

### Axiom 3 — Verification ≠ Decision
الـ pipeline يمكن أن تكون **verifier** قوية (تحكم على generated outputs) بدون أن تكون **decision injector** (تشكّل الـ prompt الأصلي).

LEAP's Lean compiler = verifier.
LEAP's DAG = memory.
LEAP's LLM Reviewer = filtering verifier (وليس injector).

GENESIS's tier_decision = injector (current).

## 4. الـ Propositions المشتقة

### Prop 1 — Memory Architectures Generalize
أي pipeline component يمكن تحويلها من Decision Injector → Memory Provider بتغيير:
- **متى تُستدعى:** من "كل request" إلى "عند الحاجة".
- **كيف تُستخدم:** من "حُقن في الـ prompt" إلى "متاحة عند الـ pull".
- **مَن يقود:** من "الـ pipeline يفرض" إلى "الـ LLM يطلب".

### Prop 2 — Verification Beats Injection
عند نفس compute budget، **verification-based pipelines** (filter outputs) تتفوق على **injection-based pipelines** (shape inputs).

دليل: LEAP يستخدم verification heavy (Lean + LLM reviewer)، GENESIS يستخدم injection heavy (pipeline signals في prompts).

### Prop 3 — Decision Injection Scales Inversely with Base Model Strength
كلما زاد الـ base model في الـ capacity، زاد الضرر من decision injection.

- Weak model: pipeline signals قد تُساعد (يحتاج كل توجيه).
- Strong model: pipeline signals تتعارض مع الـ internal reasoning.

هذا يفسر **لماذا** GENESIS كانت أكثر فائدة في الإصدارات الأولى (لما كانت تستخدم نماذج أضعف) ولماذا تضر الآن مع gpt-oss-120b القوي.

## 5. التوقعات القابلة للاختبار (Predictions)

### P1: Verification-only ablation
لو نشيل **كل injection** ونـ نحتفظ بالـ pipeline فقط كـ **post-hoc verifier**:
- التوقع: accuracy يقترب أو يتجاوز pure baseline (75%).
- (هذا A5 + A6 modes في الـ ablation matrix.)

### P2: Memory-only ablation
لو نحول الـ pipeline لـ memory provider (الـ target_agent يستدعي معلومات عند الحاجة بدلاً من الحقن التلقائي):
- التوقع: accuracy يقترب من 75% أو يتجاوزه.
- (يتطلب refactor جوهري — phase 2 من LEAP integration plan.)

### P3: Base model strength interaction
لو نختبر نفس الـ GENESIS pipeline على base model أضعف (Phi-4، Llama 3.3 8B):
- التوقع: injection-induced damage يقل، وقد يصبح injection مفيد.
- هذا اختبار لـ Prop 3.

### P4: DAG memoization wins over flat
لو نطبق LEAP-style DAG memoization على GPQA:
- التوقع: accuracy على المسائل المركبة (Chemistry Organic) تتحسن بشكل غير متناسب.
- لأن الـ DAG يسمح بـ reuse من sub-task إلى sub-task.

### P5: Anticipatory storage beats lazy
Components تكتشف proactively (lemmas, concepts) تتفوق على components تكتشف reactively.
- LEAP anticipatory lemmas → +10-17 نقاط.
- GENESIS Concept Engine المُحدّث anticipatory → expected similar gain.

## 6. الـ Empirical Checks الموجودة

| Check | Result | يدعم Theory-07؟ |
|---|---|---|
| run_57 (full pipeline injection) | 65% | ✅ نعم — injection يضر |
| run_58 A3 (no_pipeline) | 70% | ✅ نعم — إزالة injection تساعد |
| LEAP DAG ablation | +10-17 نقاط | ✅ نعم — memory architecture يساعد |
| LEAP iterative on specialized (Goedel) | -3.4 | ✅ نعم — قوة الـ base model لها وزن |
| LEAP iterative on general (Gemini) | +16.6 | ✅ نعم — الـ general LLM يستفيد من scaffolding صحيح |

## 7. الـ Empirical Checks اللي تنقص (للمستقبل)

| Check | كيف نختبره | الأولوية |
|---|---|---|
| P1: verification-only | A5 ablation | high |
| P2: memory-only | New ablation mode "memory_only_pipeline" | high |
| P3: weaker base model | Run على Phi-4 + Llama 8B | medium |
| P4: DAG memoization | New "dag_mode" implementation | high |
| P5: anticipatory storage | Modify Concept Engine | medium |

**ملاحظة:** هذه الـ checks **مخططة فقط** — لا تُنفّذ في v2.0 mode (Theoretical Focus).

## 8. الـ Implications على المشروع

### للورقة (paper-level):
1. **Re-framing لـ RQ2:** ليس "هل architecture يضيف قيمة؟" بل "أي نوع من الـ architecture يضيف قيمة؟"
2. **Section 8.5 جديد:** يستخدم Theory-07 لتفسير الـ 110-point gap.
3. **Conclusion يصبح أقوى:** Two-claim instead of one — (1) scaffolding fixes worked; (2) architecture type matters more than we thought.

### للمشروع (engineering-level):
1. **Refactor مقترح:** فصل الـ pipeline إلى memory layer + verifier layer + (optional, removed by default) injection layer.
2. **Default mode الجديد:** memory + verifier فقط. Injection يصبح opt-in فقط.
3. **A3 result يصبح baseline جديد** بدلاً من standard GENESIS.

### للنظرية الأوسع (theoretical-level):
1. **Theory-07 يُعمم:** ينطبق على أي LLM orchestration system.
2. **يُربط بـ:** `GENESIS_Cognitive_Economy_Theory_AR.md` (cost of injection) + `GENESIS_Tiered_Intelligence_AR.md` (tier as memory pull, not push).

## 9. الروابط بالنظريات الأخرى

### نظريات داخلية
- **Cognitive Economy Theory:** Injection له cost ليس مبرراً دائماً.
- **Tiered Intelligence:** الـ tier decision يجب أن يكون pull-based (الـ task يسأل عن الـ tier) وليس push-based (الـ pipeline يفرض tier).
- **Concept Formation Theory:** Concepts كـ memory (✅ صحيح) vs Concepts كـ injection (❌ خطر).
- **Anomaly Leverage:** Anomalies كـ memory entries (yes) vs Anomalies كـ injected hints (caution).

### نظريات خارجية / سرقات
- **T5.92 (LEAP):** الـ canonical example على Pipeline as Memory.
- **T5.84 (AlphaEvolve):** Population كـ pull-based memory.
- **T5.85 (Co-Scientist):** Multi-agent debate كـ pull-based reasoning.
- **T5.86 (Aletheia):** Verifier-based (not injection-based).

## 10. الروابط بالأقسام في الورقة

- **Abstract:** Theory-07 يُذكر كأحد contributions جديدة في الـ revised abstract.
- **Section 7.5 (Analysis):** Theory-07 يدخل كقسم فرعي جديد.
- **Section 8.3 (Discussion):** Theory-07 يُستخدم لتفسير الـ -10 gap.
- **Section 8.5 (Contrast with LEAP):** Theory-07 هو الـ central explanatory framework.
- **Section 10 (Future Work):** Theory-07's predictions (P1–P5) تصبح roadmap.
- **Conclusion:** Theory-07 يُذكر كأحد main takeaways.

## 11. Citation

```
Theory-07 — Pipeline as Memory vs Pipeline as Decision Injection.
Internal theory developed in PAPER/theory/07_*.md.
Source ideas: [Idea-001] (LEAP), [Idea-002] (Attribution Rule).
Empirical anchor: GENESIS run_58 (A3 +5) vs LEAP Putnam (+100).
```

## 12. Status

- ✅ Drafted (Session 7).
- ⏳ Pending Fares review.
- ⏳ Pending integration into Section 7.5 + 8.5 + Conclusion.
- ⏳ ATTRIBUTION_MAP.md update upon integration.
