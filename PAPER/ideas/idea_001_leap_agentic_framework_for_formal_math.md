# 💡 Idea-001 — LEAP: Agentic Framework for Formal Mathematics

**التاريخ:** 2026-06-05 (Session 6)
**الحالة:** Received → بدء التوسع
**الأولوية الأولية:** عالية جداً (Critical for paper)
**الـ Slug:** `leap_agentic_framework_for_formal_math`

---

## 1. نص فارس (Verbatim)

> "شوف دي
>
> Link – arxiv. org/abs/2606.03303 Title: 'LEAP: Supercharging LLMs for Formal Mathematics with Agentic Frameworks'"

---

## 2. المصدر الكامل

| الحقل | القيمة |
|---|---|
| **العنوان** | LEAP: Supercharging LLMs for Formal Mathematics with Agentic Frameworks |
| **الـ arXiv ID** | 2606.03303 |
| **التاريخ** | v1: 2 Jun 2026, v2: 3 Jun 2026 |
| **المؤلفون** | Po-Nien Kung, Linfeng Song, Dawsen Hwang, Jinsung Yoon, Chun-Liang Li, Simone Severini, Mirek Olšák, Edward Lockhart, Quoc V Le, Burak Gokturk, Thang Luong, Tomas Pfister, Nanyun Peng |
| **الجهة** | Google Cloud AI Research + Google DeepMind |
| **الكود** | github.com/google-deepmind/superhuman/tree/main/leap |
| **الـ benchmark الجديد** | Lean-IMO-Bench (60 problems) — imobench.github.io |
| **الـ Subjects** | cs.AI |

---

## 3. ملخص الورقة (فهمي بعد القراءة الكاملة)

LEAP (LLM-in-Lean Environment Agentic Prover) يستخدم **general-purpose foundation models فقط** (Gemini-3.1-Pro) لإثبات مبرهنات رياضية رسمية في Lean، ويصل إلى نتائج state-of-the-art بدون ما يكون فيه أي specialized prover model.

### النتائج الرقمية المركزية

| Benchmark | Direct LLM (one-shot) | Hilbert | Aristotle (Gold IMO) | **LEAP** |
|---|---|---|---|---|
| **Putnam 2025** | 0% | 33.3% | 75% | **100%** (12/12) |
| **Lean-IMO Basic** | 20% | 36.6% | 76.7% | **83.3%** |
| **Lean-IMO Advanced** | 3.3% | 6.6% | 20% | **56.7%** |

### الـ Architecture (الجوهر)

1. **DAG-based Hierarchical Memoization (AND-OR DAG)**
   - OR nodes = goals (أهداف يمكن إثباتها بأي طريقة).
   - AND nodes = decompositions (نجاحها يعتمد على إثبات كل sub-goals).
   - Lemma reuse عبر branches → reduces redundancy.
   - **Anticipatory lemma planning:** lemmas مقترحة قد لا تكون مطلوبة الآن لكن ستفيد لاحقاً.

2. **Interleaved Informal–Formal Planning**
   - LLM يكتب informal proof (طبيعي) أولاً.
   - ثم يترجمه إلى Lean (رسمي).
   - الـ informal sketch يلعب دور "planning space" قبل الـ formalization.

3. **Verification-Guided Proof Search**
   - **مستوى 1:** Lean compiler يتحقق syntactically.
   - **مستوى 2:** LLM Reviewer يحكم: هل الـ decomposition مفيدة فعلاً؟ هل تبسّط المشكلة؟ هل تتجنب trivial restatement؟
   - بدون الـ LLM reviewer → الـ agent يدخل في cyclic non-simplifying loops (وثقوها في الـ ablation).

4. **Workflow**
   - يحاول direct proof أولاً (مع compiler feedback + LeanSearch retrieval).
   - لو فشل → decomposition: blueprint → sketch → verified subgoals → DAG update (يحافظ على acyclicity).

### الـ Ablations التي عملوها

| Ablation | النتيجة |
|---|---|
| One-shot vs iterative (Gemini-3.1-Pro) | 20.0% → 36.6% (iteration helps a lot) |
| One-shot vs iterative (Goedel-V2-32B specialized) | 10.0% → 6.6% (specialized model doesn't benefit from iteration!) |
| DAG vs Tree (no lemma sharing) | Basic: 73.3 → 83.3, Advanced: 40.0 → 56.7 |
| With vs without LLM reviewer (Putnam A5) | Without: fails after 8 rollouts. With: solves in 2 rollouts. |

---

## 4. ليه الورقة دي مهمة لمشروعنا (فهمي الأولي)

هذه واحدة من **أقوى الأوراق المرجعية الممكنة** لـ GENESIS لأنها تجيب — من زاوية تجريبية شديدة القوة — على بعض الأسئلة المركزية اللي إحنا واقفين عندها بالظبط:

### الـ Connections المباشرة

#### (A) السؤال الأساسي بتاع RQ2 — هل orchestration بتضيف قيمة؟
**LEAP يقول: نعم، بشكل دراماتيكي.**
- Direct Gemini-3.1-Pro على Putnam 2025: **0/12 = 0%**.
- Gemini-3.1-Pro نفسه داخل LEAP: **12/12 = 100%**.
- Δ = **+100 نقطة**.

هذا **مقابل** نتيجتنا الحالية:
- Direct gpt-oss-120b على GPQA-20: 75%.
- gpt-oss-120b داخل GENESIS: 65%.
- Δ = **−10 نقطة**.

**السؤال المركزي:** لماذا LEAP يضيف 100 نقطة لنفس النموذج، بينما GENESIS يضيع 10 نقاط؟

هذا فرق **110 نقاط في الـ architecture impact** على نفس class من المهام (reasoning-heavy)، باستخدام نفس النوع من الـ base model (general-purpose foundation).

#### (B) الـ "Scaffolding vs Architecture" distinction التي أقمناها
LEAP يدعمها بشكل مذهل:
- Specialized prover model (Goedel-V2-32B) لا يستفيد من iteration (10% → 6.6%).
- General-purpose model يستفيد بشكل كبير (20% → 36.6%).
- **الـ scaffolding هو اللي بيخلق القيمة، مش الـ specialized weights.**

هذا يتطابق مع finding بتاعنا: الـ 5 scaffolding bugs اللي اكتشفناها كانت بتدمر 44.7 نقطة.

#### (C) Pipeline overhead vs useful structure
LEAP يثبت أن **الـ structure نفسها يمكن أن تكون قيمة عالية** عندما تكون مصممة بدقة:
- DAG memoization → +10 نقاط على Basic، +16.7 على Advanced.
- LLM reviewer → الفرق بين الفشل والنجاح في الأسئلة الصعبة.

بينما نتيجة A3 بتاعتنا قالت: إزالة pipeline leverage → +5 نقاط.

**الفرق الجوهري:** عند LEAP الـ pipeline (DAG + memoization) **مصممة كـ memory structure** للـ proof state. عندنا الـ pipeline **يحقن signals** في الـ answer generation.

→ هذا يقترح فرضية نظرية جديدة (Theory-07؟): **الـ pipeline as memory ≠ pipeline as decision injection.**

#### (D) Reasoning saturation finding بتاعنا
LEAP يقدم perspective جديد: الـ Goedel specialized model يفشل في الـ iteration. اللي بيستفيد من الـ scaffolding هو الـ general model اللي عنده **complementary capabilities**: instruction following, long-context reasoning, informal planning, tool use, feedback-based revision.

هذا يربط بـ "reasoning saturation" بتاعتنا: ربما الـ specialized capabilities (deep one-shot reasoning) تتعارض مع agentic iteration. الـ ablation عندهم بـ Goedel يدعم هذا.

#### (E) Domain asymmetry بتاعنا
LEAP يلاحظ نفس الظاهرة:
- Algebra & Number Theory: 100% solve rate حتى في Advanced.
- Geometry: ~12-17% فقط.
- Combinatorics: متوسط.

→ هذا يدعم Theory-04 (Domain Asymmetry) بتاعتنا. الـ domain asymmetry ليس خاص بـ GPQA — هو ظاهرة عامة في reasoning-heavy benchmarks.

#### (F) Feedback drift vs structured feedback
LEAP يستخدم compiler feedback (deterministic, machine-verifiable).
نحن نستخدم LLM-based feedback (subjective, code review style).

**Hypothesis (Theory-08؟):** Feedback يضيف قيمة عندما:
- يكون **deterministic + verifiable** (مثل compiler).
- يكون **scoped on a single failure mode** (مثل "this Lean tactic failed").

Feedback يضيع قيمة عندما:
- يكون **stochastic** (LLM judgment).
- يكون **broad-scoped** (refactor entire agent).

→ هذا يفسر مباشرة لماذا feedback drift عندنا، ولماذا LEAP feedback يعمل.

#### (G) "Anticipatory lemma planning" → ربط بـ Concept Engine بتاعنا
LEAP يقترح lemmas مفيدة قد لا تكون مطلوبة الآن. هذا concept موازي لـ:
- `GENESIS_Concept_Formation_Engine_Spec_AR.md`
- `GENESIS_Concept_Engine_TaskCase_Refinement_Memo_AR.md`

→ فيه فرصة قوية لإعادة قراءة الـ Concept Engine بتاعنا في ضوء "anticipatory lemmas" بتاع LEAP.

---

## 5. أسئلة مفتوحة لفارس

أنا محتاج توجيهك في النقاط دي قبل ما نقرر إزاي ندخل LEAP في الورقة:

1. **هل نريد LEAP يكون reference أساسي للورقة؟** (واضح إنه نعم، بس عاوز تأكيدك على الـ centrality).

2. **أي زاوية أهم عندك؟** (يمكن نختار أكثر من واحدة):
   - (a) LEAP كـ "proof of concept" أن orchestration بيشتغل (دعم لـ RQ2 من خارج المشروع).
   - (b) LEAP كـ "contrast case" نقارن إزاي architecture-impact = +100 vs −10.
   - (c) LEAP كـ مصدر لـ structural ideas نسرقها (DAG memoization, LLM reviewer, anticipatory lemmas).
   - (d) LEAP كـ rephrasing للـ scaffolding-vs-architecture distinction.

3. **هل نعتبره سرقة شرعية جديدة (T5.92 أو ما يليه) في الـ master index؟** على غرار AlphaEvolve وCo-Scientist وAletheia.

4. **هل تريد نظرية جديدة كاملة عن "Pipeline as Memory vs Pipeline as Decision Injection"؟** هذا فرق structural عميق ظهر من قراءة LEAP.

5. **هل تريد إعادة تأمل في Concept Engine بتاعنا** في ضوء "anticipatory lemma planning" بتاع LEAP؟

---

## 6. اقتراحات التوسع (مرتبة بالأولوية)

### اقتراح 1 (الأقوى): سرقة شرعية كاملة + ربط ثلاثي

نعمل ملف سرقة شرعية بنفس نمط `GENESIS_DeepMind_AlphaEvolve_FunSearch_Theft_AR.md`:
- `GENESIS_DeepMind_LEAP_Agentic_Theft_AR.md`
- نوثق كل element من LEAP architecture: ما أخذناه + ما تركناه + كيف يدخل GENESIS.
- نسجله كـ T5.92 في `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md`.

### اقتراح 2: قسم جديد في الورقة "Contrast with LEAP"

في `PAPER.md` section 8 (Discussion)، نضيف 8.5:
**"Why GENESIS loses 10 points while LEAP gains 100 — a structural comparison"**

نطرح فيه:
- جدول مقارن بين الـ architectures.
- تحليل لكل element: ما يفعله LEAP بشكل مختلف.
- استنتاج: GENESIS تحتاج structural redesign، مش feedback tuning.

### اقتراح 3: نظريتان جديدتان

- **Theory-07:** Pipeline as Memory vs Pipeline as Decision Injection.
- **Theory-08:** Feedback Value = f(Determinism, Scope).

### اقتراح 4: ربط بـ Concept Engine

ملف جديد في `PAPER/theory/`:
- `09_anticipatory_concepts_vs_anticipatory_lemmas.md`
- نقارن Concept Engine بتاعنا بـ DAG memoization بتاع LEAP.
- نستخرج principles مشتركة.

### اقتراح 5: Philosophy

- **Phil-07:** ماذا يعني "general-purpose model is sufficient"؟ (سؤال LEAP المركزي).
- يربط بـ Phil-01 (architecture adds value).

### اقتراح 6: Future Work في الورقة

نضيف في Section 10 (Future Work) بند جديد:
- "Adopting LEAP-style DAG memoization for GENESIS task decomposition."
- نوضح أنه not blind adoption — مع تحليل لـ adaptation.

---

## 7. الـ Citations المرتبطة من السرقات الموجودة

LEAP يذكر هذه الأوراق وفيهم ربط مباشر بسرقاتنا:
- **AlphaProof** [T5.86 — AlphaEvolve/FunSearch family].
- **Hilbert, Aristotle, Seed Prover, Goedel V2** — كلها agentic Lean provers، يمكن إضافتها كـ references ثانوية.
- **Lean Blueprint tool** — إطار human formalization workflow → ربط ممكن بـ GENESIS workflow.

---

## 8. الـ Roadmap المقترح (في انتظار قرار فارس)

```
Step 1: فارس يرد على الأسئلة في §5.
Step 2: لو وافق على Suggestion 1 → أبني ملف السرقة الكامل.
Step 3: أحدّث Master Index بـ T5.92.
Step 4: لو وافق على Suggestion 2 → أكتب Section 8.5 في PAPER.md.
Step 5: لو وافق على Suggestion 3 → أكتب Theory-07 و Theory-08.
Step 6: لو وافق على Suggestion 4 → أكتب theory/09_*.md.
Step 7: لو وافق على Suggestion 5 → أكتب philosophy/07_*.md.
Step 8: تحريك Idea-001 من INBOX → IN_PROGRESS → INTEGRATED.
```

**لا أنفذ أي خطوة من 2-7 بدون موافقة فارس صراحة على كل واحدة.**

---

## 9. الحالة الحالية

- ✅ استلام الفكرة (Session 6).
- ✅ قراءة الورقة كاملة (5 chunks).
- ✅ إنشاء هذا الملف التفصيلي.
- ⏳ في انتظار توجيه فارس على §5 و §6.

---

## 10. ملاحظة مهمة من الـ agent

هذه أول فكرة رسمية في الـ Ideas Bank. الـ depth هنا هو الـ standard للأفكار اللي جاية. لا أختصر. لا أفترض. لا أنفذ بدون موافقة فارس على كل خطوة.

كما قال فارس صراحة في Session 6:
> "اللي في بالي ده ممكن يكون مجرد 3% منه. تفاصيل كثيرة لسه جاية."

أتعامل مع كل فكرة كأنها قد تكون **العمود الفقري** لقسم كامل في الورقة.
