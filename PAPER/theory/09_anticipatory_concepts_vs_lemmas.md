# Theory-09 — Anticipatory Concepts vs Anticipatory Lemmas

**Source ideas:** [Idea-001] (LEAP) + [Idea-002] (Attribution Rule)
**Related thefts:** T5.92 (LEAP anticipatory lemmas)
**Related internal:** `GENESIS_Concept_Formation_Engine_Spec_AR.md`, `GENESIS_Concept_Formation_Theory_AR.md`, Concept Engine implementation
**Status:** Draft Theory v1.0
**Tag:** `[Theory-09]`

---

## 1. الظاهرة المُلاحظة

### في LEAP
LEAP يستخدم "anticipatory lemma planning":
> "During blueprint generation, LEAP may propose auxiliary lemma statements that are not immediately required by the current sketch but could support later proof steps. Such prospective lemmas remain available in the graph memory without being necessary for resolving the current AND node."

النتيجة: lemmas مُكتشفة proactively تُعاد استخدامها لاحقاً → +10 على Basic, +17 على Advanced.

### في GENESIS
الـ Concept Formation Engine بتاعنا يعمل شيء **مذهلاً مشابهاً**:
- `propose_concepts_from_groups` يقترح concepts بناءً على patterns ملاحظة.
- بعض هذه الـ concepts قد لا تكون مطلوبة للـ task الحالي.
- لكنها تُحفظ في `concept_registry` لإعادة استخدامها لاحقاً.

**الـ insight:** الـ Concept Engine بتاعنا هو بالفعل implementation لـ "anticipatory abstraction" — لكن في domain أوسع (scientific reasoning) عوضاً عن formal proofs.

## 2. الفرضية المركزية

نقترح أن **anticipatory abstraction** هي مبدأ معماري عام، يتجلى في صور مختلفة حسب الـ domain:

| Domain | الاسم في LEAP / GENESIS | الوحدة المُخزَّنة |
|---|---|---|
| Formal math | Anticipatory Lemmas | Lean lemma statements + proofs |
| Scientific MCQ | Anticipatory Concepts | Generalizable patterns/relations |
| Software engineering | (مرشح) Anticipatory Helpers | Reusable code functions/abstractions |
| Combinatorial discovery | (مرشح) Anticipatory Constructs | Heuristics/patterns |

**التعميم:** كل agent reasoning system يستفيد من تخزين abstractions ليست مطلوبة الآن لكن متوقع استخدامها لاحقاً، **شرط** أن يكون التخزين منظم بطريقة retrievable.

## 3. الـ Axioms

### Axiom 1 — Reuse Beats Rediscovery
الـ cost الحاسوبي لـ retrieving lemma/concept موجود << الـ cost لـ rediscovering it.

### Axiom 2 — Abstraction Generalizes
كل abstraction proactively-stored تزيد probability الـ generalization على tasks مستقبلية، لو تم تخزينها بـ key مناسب (signature).

### Axiom 3 — Storage Cost Sublinear vs Compute Cost
ذاكرة الـ abstractions تنمو linearly، بينما compute saving من reuse ينمو بشكل أعلى لو الـ abstractions tail-fat (بعضها يُستخدم كثيراً).

## 4. الـ Propositions

### Prop 1 — Concept Engine Should Be Anticipatory by Default
المرحلة الحالية من Concept Engine = reactive (concepts تتشكل response لـ groups موجودة).
المرحلة المقترحة = proactive (concepts تُقترح لـ patterns متوقعة قبل ظهورها).

### Prop 2 — DAG-Indexed Concepts
الـ concepts الحالية تُخزَّن flat. الـ DAG-indexed concepts (LEAP-style) تسمح بـ:
- Dependency tracking (concept A يبني على concept B).
- Lemma-like reuse عبر sub-tasks.
- Anticipatory chains (concept proposed for far-future use).

### Prop 3 — Anticipatory Storage Has Marginal Cost But Compounding Benefit
الـ cost إضافة concept إلى registry = O(1).
الـ benefit في reuse عبر سلسلة tasks = O(n) إلى O(n log n) حسب الـ retrieval scheme.

### Prop 4 — LEAP's +10/+17 Gain Generalizes to Scientific Domains
لو نطبق DAG memoization مع anticipatory concept storage على GPQA:
- Hard Chemistry Organic questions (5/6 hard) قد تستفيد بشكل غير متناسب.
- لأنها تشترك في sub-mechanisms (Grignard, PCC, oxidation, إلخ) — كل واحد منها = anticipatory concept.

## 5. التوقعات القابلة للاختبار

### P1: Anticipatory mode lifts Chemistry Organic
لو نضيف `anticipatory_mode` للـ Concept Engine + نخزن chemistry sub-mechanisms كـ concepts:
- التوقع: Chemistry Organic accuracy ينتقل من 16.7% (current GENESIS) إلى 50%+ (matching A3 result).

### P2: Cross-task transfer
لو نشغل GPQA-20 ثم GPQA-40 مع memory محفوظة من الـ first run:
- التوقع: الـ second run يستفيد من anticipatory concepts proposed في الأولى.
- (memory transfer = explicit measurement of anticipatory value.)

### P3: Anticipatory cost is sublinear
الـ Compute cost لـ anticipatory proposal step << الـ saved cost عبر reuse:
- التوقع: net positive حتى لو 50% من الـ anticipatory concepts لا تُستخدم أبداً.

## 6. الـ Empirical Checks الموجودة

| Check | النتيجة | يدعم Theory-09؟ |
|---|---|---|
| LEAP DAG ablation (Advanced: +17 نقاط) | DAG with anticipatory lemmas > flat | ✅ نعم |
| GENESIS Concept Engine evolution memos | Concept reuse مذكور بشكل intuitive | ✅ partial — توثيق موجود لكن لم يُختبر anticipatory mode |

## 7. الـ Empirical Checks اللي تنقص

| Check | كيف | الأولوية |
|---|---|---|
| P1: Chemistry lift | Implement anticipatory_mode في Concept Engine + run على GPQA-20 | high |
| P2: Cross-task transfer | Run sequence (GPQA-20 → GPQA-40 with shared memory) | medium |
| P3: Cost analysis | Profile compute في anticipatory proposal step | low |

## 8. الـ Design Sketch — Anticipatory Concept Proposer

```python
# Current (reactive) — virtual_genesis/runtime/concept_engine/proposer.py
def propose_concepts_from_groups(groups, registry):
    """React to observed groups; propose concepts that explain them."""
    for group in groups:
        if not registry.has_concept_for(group):
            candidate = build_candidate_concept(group)
            if evidence_score(candidate) > threshold:
                registry.add(candidate)
```

```python
# Proposed (anticipatory) — Theory-09 implementation
def propose_anticipatory_concepts(current_task, registry, depth=2):
    """
    Look at current task. Predict adjacent/related sub-tasks.
    Propose concepts for those predicted sub-tasks BEFORE they arise.
    """
    related_tasks = registry.predict_related(current_task, depth=depth)
    for predicted_task in related_tasks:
        if not registry.has_concept_for(predicted_task):
            candidate = build_anticipatory_concept(predicted_task)
            # Lower threshold than reactive (since cost is sunk)
            if anticipation_score(candidate) > lower_threshold:
                registry.add_anticipatory(candidate)
```

**Key difference:** lower threshold for inclusion, since the cost of unused anticipation is small but the cost of missed anticipation is large.

## 9. الروابط بالنظريات الأخرى

### نظريات داخلية
- **Theory-07 (Pipeline as Memory):** anticipatory concepts = memory entries, not injectors.
- **Theory-08 (Feedback Value):** anticipatory storage = narrow scope, deterministic addition.
- **Concept Formation Theory:** الـ extension الطبيعي للنظرية الموجودة.
- **Cognitive Economy:** anticipatory cost is justified by reuse savings.
- **Productive Forgetting:** balance — anticipatory storage + selective forgetting = optimal memory.

### سرقات
- **T5.92 (LEAP):** المصدر الأصلي لـ anticipatory lemma pattern.
- **T5.5 (Reflexion):** reflection-based memory ≈ partial anticipation.
- **T5.7 (STaR):** bootstrapped reasoning ≈ anticipatory rationales.

## 10. الروابط بأقسام الورقة

- **Section 4 (Methodology):** Concept Engine + anticipatory mode = new subsection.
- **Section 6.x:** يُذكر Theory-09 لتفسير أي Chemistry Organic improvements.
- **Section 8.x:** Theory-09 يدخل في discussion للـ scientific generalization.
- **Section 10 (Future Work):** P1 + P2 + P3 = ablation roadmap.

## 11. Citation

```
Theory-09 — Anticipatory Concepts vs Anticipatory Lemmas.
Internal theory developed in PAPER/theory/09_*.md.
Source ideas: [Idea-001] (LEAP anticipatory lemmas) → applied to Concept Engine.
Empirical anchor: LEAP DAG ablation +17 points + GENESIS Concept Engine existing structure.
```

## 12. Status

- ✅ Drafted (Session 7).
- ⏳ Pending Fares review.
- ⏳ Pending implementation of `anticipatory_mode` (Phase 2).
- ⏳ Pending re-read of `GENESIS_Concept_Formation_Engine_Spec_AR.md` in light of Theory-09.
- ⏳ ATTRIBUTION_MAP.md update.
