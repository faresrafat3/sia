# 📜 PAPER PROTOCOL — دليل العمل على الورقة عبر الجلسات

**⚠️ اقرأ هذا الملف أولاً قبل أي تعديل على الورقة. هذا هو العقد بيني (الـ agent) وبين فارس (المالك).**

**التاريخ:** 2026-06-05
**النسخة:** 2.0 — Theoretical/Philosophical Focus Mode
**الوضع:** Living document — يُحدّث بعد كل session كبيرة

---

## 0. تحديث جوهري (Session 6, v2.0) — Mode Pivot

**فارس قرر صراحة في Session 6:**

> "هنعمل اسكيب لمواضيع التشغيل، احنا هنضبطها على الورقة وفلسفياً ونظرياً المشروع بالكامل بالأفكار اللي لسه هتجي وكل حاجة."

> "اللي في بالي ده ممكن يكون مجرد 3% منه. تفاصيل كثيرة لسه جاية وكلها علمية مترابطة. شغل ونظريات وحاجات هنفكر نضيفها إزاي ونربطها."

> "أنا هقولك الأفكار أو الأوراق أو المواضيع، والاتنين متبادل. أيوة، اقترح وضيف واعمل."

### معنى ذلك

#### ✅ Mode حالي (DO)
- العمل على **الورقة كمنتج فكري**: framing, narrative, depth, connections.
- بناء **نظرية** خلف كل observation تجريبية موجودة.
- بناء **فلسفة** للمشروع تجيب على "ليه؟" قبل "إزاي؟".
- ربط كل قطعة بـ **الأدبيات** (السرقات الشرعية الـ 102+).
- توسيع **الأفكار الجديدة** اللي بييجي بها فارس واحدة واحدة.
- اقتراح اتجاهات نظرية/فلسفية مكملة، بشكل تبادلي.
- الحفاظ على النتائج التجريبية الموجودة (75% pure, 65% GENESIS, 70% A3) كـ **empirical anchor** ثابت.

#### ❌ Mode حالي (DON'T)
- **لا تشغّل runs جديدة** على free tier.
- **لا تقترح A4/A5/A6/A7 runs** كأولوية.
- **لا تستهلك quotas** على benchmarks جديدة.
- **لا تركّز على scores رقمية جديدة** كهدف.
- **لا تختصر** على حساب العمق الفكري.
- **لا تفترض إن اللي عند فارس في باله هو كل اللي هييجي** — هو نفسه قال "3% بس".

#### 🔄 ديناميكية العمل
- **فارس يقود**: يعطي أفكار، أوراق، مواضيع، أسئلة.
- **Agent ينفّذ ويوسّع**: يكتب، يربط، يعمّق، يبني figures/tables/sections فكرية.
- **Agent يقترح أيضاً**: اتجاهات نظرية/فلسفية، روابط بأدبيات، طبقات جديدة.
- **التبادل مستمر**: لا واحد يحتكر القيادة.

---

## 1. الهدف من الورقة

**"نهدف لأقوى ورقة في المجال"** — فارس (Session 2)
**"هنعمل اسكيب لمواضيع التشغيل، نضبطها على الورقة وفلسفياً ونظرياً"** — فارس (Session 6)

### نبني paper بحثية واحدة كبيرة عن

#### السؤال البحثي الأساسي

**هل تضيف بنية orchestration (GENESIS) قيمة قابلة للقياس فوق الـ baseline لـ LLMs على المهام الـ reasoning-heavy، ولماذا، وتحت أي شروط نظرية؟**

#### الأهداف الفرعية (محدّثة v2.0)

1. توثيق علمي صارم للحالة التجريبية الحالية (baselines, bugs, fixes, A3 result) — **هذا الجزء مُغلق ومستقر**.
2. **بناء نظرية كاملة** خلف كل ظاهرة لاحظناها (reasoning saturation, domain asymmetry, pipeline overhead, feedback drift).
3. **بناء فلسفة** للمشروع: ماذا يعني "architecture adds value"؟ ماذا يعني "scaffolding error" مقابل "model error"؟ ماذا يعني "thinking model" أصلاً؟
4. **ربط شامل بالأدبيات**: استعمال السرقات الـ 102+ كنسيج تحتي.
5. **استقبال أفكار فارس** الجديدة وتوسيعها واحدة واحدة، مع ربطها بالموجود.
6. **(مؤجل لمرحلة لاحقة):** أي runs أو benchmarks جديدة.

---

## 2. هيكل الـ Repository للورقة (محدّث v2.0)

```
PAPER.md                       ← الورقة الرئيسية (master document)
PAPER_PROTOCOL.md              ← هذا الملف (دليل العمل)
PAPER/
├── sections/                  ← أقسام الورقة منفصلة للتحرير المريح
│   ├── 00_abstract.md
│   ├── 01_introduction.md
│   ├── 02_related_work.md
│   ├── 03_methodology.md
│   ├── 04_infrastructure.md
│   ├── 05_experiments.md
│   ├── 06_results.md
│   ├── 07_analysis.md
│   ├── 08_discussion.md
│   ├── 09_limitations.md
│   ├── 10_future_work.md
│   └── 11_conclusion.md
│
├── theory/                    ← 🆕 v2.0 — النظريات اللي تشرح "ليه؟"
│   ├── README.md              ← فهرس النظريات + روابط بالـ findings
│   ├── 01_*.md                ← نظرية لكل ظاهرة (نبدأ بـ pipeline overhead)
│   └── ...                    ← يُضاف بالتدريج
│
├── philosophy/                ← 🆕 v2.0 — الأسئلة الفلسفية العميقة
│   ├── README.md              ← فهرس الأسئلة الفلسفية
│   ├── 01_*.md                ← مقال فلسفي لكل سؤال
│   └── ...                    ← يُضاف بالتدريج
│
├── ideas/                     ← 🆕 v2.0 — bank الأفكار الجديدة من فارس
│   ├── README.md              ← فهرس + status لكل فكرة
│   ├── INBOX.md               ← الأفكار اللي لسه ما اشتغلناش عليها
│   ├── IN_PROGRESS.md         ← الأفكار اللي بنوسعها حالياً
│   ├── INTEGRATED.md          ← الأفكار اللي دخلت الورقة فعلاً
│   └── &lt;idea_NNN_slug&gt;.md     ← ملف لكل فكرة تفصيلية
│
├── figures/                   ← كل الرسوم البيانية
│   ├── README.md
│   ├── fig01_pipeline_overview.md
│   └── ...
│
├── tables/                    ← الجداول
│   ├── README.md
│   ├── tab01_models_registry.md
│   └── ...
│
├── references/                ← المصادر اللي نستلهم منها (الـ thefts)
│   ├── README.md
│   └── ...
│
├── data/                      ← البيانات الخام للورقة (لا تتوسع في v2.0)
│   ├── aggregated_results.json
│   └── ...
│
└── notes/                     ← ملاحظات الـ session للـ continuity
    ├── SESSION_LOG.md
    ├── TODO_HIGH.md
    ├── TODO_MEDIUM.md
    ├── OPEN_QUESTIONS.md
    └── HANDOFF.md
```

---

## 3. قواعد الكتابة (Writing Style)

### اللغة

- **اللغة الأساسية:** العربية الفصحى/المصرية المختلطة (زي لما فارس بيكلمني).
- **الـ technical terms:** بالإنجليزية مع ترجمة عربية أحياناً للوضوح.
- **الـ code/equations:** بالإنجليزية فقط.
- **الـ Mermaid diagrams:** labels بالإنجليزية (للـ rendering).
- **في الـ paper sections الإنجليزية النهائية:** إنجليزية أكاديمية صارمة (لما نوصل لمرحلة الـ submission).

### النبرة (Tone)

- **علمي صارم** — كل ادعاء له دليل (بيانات + المصدر).
- **شفاف** — نذكر الـ limitations صراحة.
- **مفصل** — لا نختصر على حساب الفهم.
- **متواضع لكن واثق** — "نظهر أن..." بدل "أثبتنا قطعياً...".
- **فلسفي عميق** (v2.0) — لا نخاف نسأل أسئلة "ساذجة" زي "إيه يعني value؟".
- **نظري طموح** (v2.0) — لا نكتفي بـ observation، نطلع نظرية تفسره.

### الـ Citations

- **لـ الـ thefts:** نشير بـ `[T#]` حيث # رقم السرقة في `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md`.
  مثال: "نتبنى منهجية evolutionary search من AlphaEvolve [T5.86]".
- **لـ الـ external papers:** بـ نمط `[Author Year]`.
  مثال: "GPQA Diamond benchmark [Rein 2024]".
- **لـ النتائج الداخلية:** نشير بـ figure/table/section number.
  مثال: "كما يظهر في Figure 3 / Table 2 / Section 8.3".
- **لـ النظريات الداخلية (v2.0):** نشير بـ `[Theory-NN]` حيث NN رقم في `PAPER/theory/`.
  مثال: "تحت Theory-03 (Pipeline Overhead)، نتوقع...".
- **لـ الأفكار من فارس (v2.0):** نشير بـ `[Idea-NNN]` حيث NNN رقم في `PAPER/ideas/`.

### الـ Numbers

- **دقة:** نسبة مئوية بـ 2 خانات عشرية (75.00%) أو 1 (75.0%) حسب السياق.
- **مع margin of error:** كلما أمكن (75.0% ± 10% on n=20).
- **مقارنات:** نوضح الفرق (Δ) صراحة (+10.0 نقطة).

---

## 4. الـ Workflow عبر الجلسات (Session Handoff)

### في بداية كل session جديد، أنا (الـ agent) لازم

1. **اقرأ** `PAPER_PROTOCOL.md` (هذا الملف) كاملاً.
2. **اقرأ** `PAPER/notes/HANDOFF.md` — آخر حالة من الـ session السابقة.
3. **اقرأ** `PAPER/notes/SESSION_LOG.md` — تاريخ كل session.
4. **اقرأ** `PAPER.md` — الورقة الحالية.
5. **اقرأ** `PAPER/notes/TODO_HIGH.md` — الأولويات.
6. **اقرأ** `PAPER/ideas/INBOX.md` و `IN_PROGRESS.md` — أفكار فارس الجديدة (v2.0).
7. **اسأل فارس:** "أكمل من X (آخر session) أم خطوة جديدة Y؟" أو **"عندك فكرة جديدة تحب نبدأ بها؟"** (v2.0).

### في نهاية كل session، أنا لازم

1. **حدّث** `PAPER.md` بالتغييرات الجديدة.
2. **أضف entry في** `PAPER/notes/SESSION_LOG.md`:
   - التاريخ + ID الـ session.
   - إيش اتعمل (مفصل).
   - إيش الـ figures/tables/theories/philosophy/ideas الجديدة.
   - أي ادعاءات علمية أو نظرية جديدة + دليلها.
   - الـ commits المرفوعة.
3. **حدّث** `PAPER/notes/HANDOFF.md`:
   - الحالة الحالية (Current State).
   - الـ open threads (شغل مش مكتمل).
   - الـ next concrete step.
   - أي قرار محتاج فارس يأكده.
4. **حدّث** `PAPER/notes/TODO_HIGH.md` و `TODO_MEDIUM.md`.
5. **أضف أي سؤال مفتوح في** `PAPER/notes/OPEN_QUESTIONS.md`.
6. **حدّث** `PAPER/ideas/` لو دخلت أو خرجت أي فكرة (v2.0).
7. **اعمل commit واحد كبير** بـ message شامل (مش commits صغيرة مبعثرة).

### القاعدة الذهبية

**"اللي مش مكتوب في الورقة أو notes، لم يحدث."**
أي اكتشاف، أي قرار، أي نتيجة، أي فكرة من فارس — لازم تتسجل. لا تعتمد على ذاكرة الـ session.

---

## 5. الـ Figures و Tables — معايير الجودة

### الـ Figures

- **كل figure له رقم + caption مفصل** (لا "Figure 1" بدون شرح).
- **الـ caption يشرح ماذا نرى + ماذا نستنتج**.
- **استخدم Mermaid لـ flowcharts/architectures** (يرندر في GitHub).
- **استخدم ASCII art لـ charts بسيطة** (يعرض في أي محرر).
- **استخدم SVG inline للرسوم المعقدة** (يرندر في GitHub).
- **كل figure مرتبط بـ section** يشير إليه.
- **v2.0:** نضيف **conceptual figures** للنظريات والفلسفة (مش بس data plots).

### الـ Tables

- **كل column له اسم واضح + unit** (لو رقم).
- **الـ rows لها logical ordering** (بالأداء، بالـ chronology، بالـ category).
- **الـ highlights بـ bold** (الأفضل/الأسوأ/الـ relevant).
- **الـ caption يشرح ما يوضحه الجدول**.
- **v2.0:** نضيف **conceptual tables** (theory-prediction matrices, idea-theory mappings, إلخ).

---

## 6. الاستلهام من الـ Thefts

**القاعدة:** لا نخترع pattern لو في pattern موثق في paper سرقناها منها.

### كيف نستلهم

1. **قبل ما نختار format للـ figure/section:**
   - شوف الـ paper الأصلية (FunSearch، AlphaEvolve، Aletheia، إلخ).
   - افهم إزاي عرضوا نتائجهم.
   - استلهم (مش نسخ) الـ structure.

2. **للـ tables:**
   - **AlphaEvolve [T5.86]:** يقدم النتائج بـ ablation tables.
   - **GPQA paper [Rein 2024]:** يقدم per-domain breakdowns.
   - **FunSearch [Nature 2023]:** يقدم evolutionary trajectory plots.

3. **للـ figures:**
   - **Reflexion [T5.5]:** memory architecture diagrams.
   - **STaR [T5.7]:** training loop visualization.
   - **Self-Refine [T5.6]:** generate→critique→refine loops.

4. **للـ writing structure:**
   - **DeepMind papers:** open with strong "what we found".
   - **OpenAI papers:** strong methodology sections.
   - **Academic papers:** clear limitations sections.

5. **للنظريات (v2.0):**
   - استلهم بنية الـ theory papers (axioms → propositions → predictions → empirical checks).
   - استلهم من السرقات النظرية الداخلية (Cognitive Economy, Anomaly Leverage, Concept Formation, Identity Governance، إلخ).

### بروتوكول الاستلهام

لما نستلهم من theft معين:

1. سجل في `PAPER/references/<NNN>_<name>.md` ليه استلهمنا منه.
2. اذكر بـ صريح في الورقة: "Following the approach of [Author Year]..." أو "Inspired by AlphaEvolve [T5.86] which uses...".
3. وضح **الفرق** عنهم (ليه أخذنا حاجة وتركنا حاجة).

---

## 7. الـ Versioning

- **PAPER.md:** semantic versioning (v0.1 → v0.2 → v1.0).
- **major version:** لما نضيف section جديد أو تغيير كبير في النتائج أو النظرية.
- **minor version:** لما نضيف figure/table/data/idea/theory جديد.

### السجل في `PAPER/notes/SESSION_LOG.md`

```
## v0.3 — 2026-06-05 (Session 2)
- Added Figure 5: Per-domain accuracy bar chart
- Added Table 3: Bugs taxonomy with fixes
- Updated Section 7: Reasoning correlation analysis
- Commits: abc1234, def5678
```

---

## 8. النواهي (Don'ts) — محدّثة v2.0

- ❌ **لا تنشئ تقارير منفصلة** (`*_REPORT_*.md`) — كل شيء يدخل في الورقة.
  - **استثناء:** تقارير سابقة موجودة بالفعل تبقى للأرشيف.
- ❌ **لا تكتب claims بدون دليل** — كل ادعاء يحتاج figure/table/citation/theory link.
- ❌ **لا تنسى تحدّث** `HANDOFF.md` في نهاية كل session.
- ❌ **لا تختصر على حساب الوضوح** — فارس قال "بالغ في التفاصيل".
- ❌ **لا تستخدم نماذج مدفوعة بدون إذن** — اسأل فارس أولاً.
- ❌ **لا تنشر مفاتيح في الـ commits** — اعمل scan دائماً قبل push.
- ❌ **(v2.0) لا تقترح runs جديدة كأولوية** — احنا في theoretical/philosophical mode.
- ❌ **(v2.0) لا تفترض إن فكرة فارس "صغيرة" — هو نفسه قال إن اللي في باله الآن ممكن يكون 3% بس من اللي جاي.**
- ❌ **(v2.0) لا تعمل فكرة فارس كـ side note** — كل فكرة لازم ياخد ملفها الخاص في `PAPER/ideas/` ويُربط بالنظرية والفلسفة والورقة.

---

## 9. القرارات المعمارية المُتفق عليها مع فارس

| السؤال | القرار | السبب |
|---|---|---|
| نبني router للـ instant/thinking؟ | **لا — مؤجل** | مرحلة لاحقة بعد baseline قوي. |
| نضيف complexity جديدة عملية؟ | **لا — Theoretical mode** (v2.0) | نركز على فهم اللي عندنا. |
| نستخدم نماذج مدفوعة؟ | **لا في المرحلة الحالية** | فيزا فارس الافتراضية لا تُشحن. |
| GitHub Models (PAT)؟ | **متاح** | gpt-5, gpt-4.1, gpt-4o, DeepSeek-R1, Phi-4 شغّالين. |
| متى نشغّل GENESIS post-fix؟ | **مؤجل** (v2.0) | احنا في theoretical mode. |
| نضيف Gemini × 11 keys؟ | **مؤجل** (v2.0) | احنا في theoretical mode. |
| نضيف Groq × 11 keys؟ | **مؤجل** (v2.0) | احنا في theoretical mode. |
| NVIDIA NIM؟ | **مش متاح في مصر** | skip. |
| **(v2.0) إيش نعمل بدل التشغيل؟** | **Theory + Philosophy + Ideas + Paper depth** | قرار فارس Session 6. |

---

## 10. الـ Reference Quick Cards

### المفاتيح المتاحة (للسياق فقط، الكيز نفسها في .env المحلي)

- ✅ 11 OpenRouter keys (free tier — بعض النماذج exhausted)
- ✅ 1 GitHub PAT (gpt-5, gpt-4.1, gpt-4o, DeepSeek-R1, Phi-4 شغّالين)
- ⏳ Gemini × 11 (فارس يحضّرهم — مؤجل في v2.0)
- ⏳ Groq × 11 (فارس يحضّرهم — مؤجل في v2.0)
- ❌ NVIDIA NIM (مش متاح في مصر)

### الـ Benchmark الأساسي

- **GPQA Diamond** — 198 questions, A/B/C/D MCQ, 3 domains (Physics 86, Chemistry 93, Biology 19).
- نستخدم subset 20 questions للسرعة، الـ 198 الكامل للقياس النهائي.

### الـ Empirical Anchors (مستقرة، لا تتغير في v2.0 إلا بـ run جديد)

- Pure baseline: **75.00%** (n=20).
- GENESIS pre-fix (run_53): **30.30%**.
- GENESIS post-fix standard (run_57): **65.00%** (both gens).
- GENESIS A3 no_pipeline (run_58): **70.00%** (gen1), **60.00%** (gen2).
- Recovery from buggy run: **+34.7 points**.
- Residual architecture gap vs baseline: **−10.0 points** (standard) / **−5.0 points** (A3 gen1).
- Bugs found: 6.
- Tests: 463/463.

### الـ Empirical Discoveries (موضوع للتنظير في v2.0)

1. **Reasoning saturation:** more reasoning tokens → lower accuracy.
2. **Domain asymmetry:** Physics easy, Chemistry Organic hard.
3. **Empty content phenomenon:** 35% of reasoning responses return content="".
4. **Architecture gap localization:** loss concentrated on Chemistry questions, not uniform.
5. **Feedback drift:** Gen 2 changes pattern without improving total score.
6. **Pipeline overhead:** removing it recovers half the gap.

**كل واحدة من دول تحتاج نظرية تفسرها** (v2.0).

---

## 11. الـ Session Continuity — كيف تستلم الجلسة الجاية

```
1. اقرأ هذا الملف (PAPER_PROTOCOL.md) — انتبه إن النسخة v2.0 = Theoretical Mode
2. اقرأ PAPER/notes/HANDOFF.md
3. اقرأ PAPER.md
4. اقرأ PAPER/ideas/INBOX.md و IN_PROGRESS.md (v2.0)
5. اسأل فارس: "عندك فكرة جديدة؟ أم نكمل من X؟"
6. اشتغل (theory/philosophy/ideas/paper depth — مش runs)
7. حدّث PAPER.md + HANDOFF.md + SESSION_LOG.md + ideas/
8. اعمل commit واحد كبير شامل
9. لا تنسى scan أمني قبل push
```

---

## 12. الـ Ideas Pipeline (v2.0 — جديد)

لما فارس يقول فكرة جديدة:

1. **استلامها فوراً** في `PAPER/ideas/INBOX.md` بتاريخ + ID رقمي تتابعي (Idea-001, Idea-002...).
2. **عمل ملف تفصيلي** `PAPER/ideas/idea_NNN_<slug>.md` فيه:
   - **النص الأصلي من فارس** (verbatim، احتراماً للقصد).
   - **فهمي للفكرة** (rephrasing من غير ما يضيع المعنى).
   - **الأسئلة المفتوحة** (لو فيه ambiguity).
   - **الروابط المحتملة بالموجود**: لأي theory, philosophy, section, theft, finding.
   - **التوسع المقترح**: ازاي ممكن نطورها لـ نظرية/قسم/figure/table.
3. **نقاش تبادلي** مع فارس:
   - أنا أقترح اتجاهات.
   - فارس يوافق/يرفض/يعدّل.
4. **تحريك للـ IN_PROGRESS.md** عند البدء في التنفيذ.
5. **تحريك للـ INTEGRATED.md** عند دخولها الورقة فعلاً.
6. **في الورقة:** أي ادعاء مبني على فكرة فارس يُشار إليه بـ `[Idea-NNN]`.

---

## 13. الـ Theory Pipeline (v2.0 — جديد)

لما نلاحظ ظاهرة تجريبية أو نستلم فكرة:

1. **اسأل:** هل لها نظرية موجودة في الـ docs الداخلية أو السرقات؟
2. **لو أيوة:** اربطها صراحة.
3. **لو لأ:** اعمل ملف نظرية جديد `PAPER/theory/NN_<name>.md` فيه:
   - **الظاهرة المُلاحظة** (observation).
   - **الفرضية المقترحة** (hypothesis).
   - **الـ axioms أو المبادئ الأولية**.
   - **الـ propositions المشتقة**.
   - **التوقعات (predictions) القابلة للاختبار**.
   - **الـ empirical checks الموجودة** (لو فيه).
   - **الـ empirical checks اللي تنقص** (للمستقبل، مش الآن).
   - **الروابط بالنظريات الأخرى** الداخلية والخارجية.
4. **في الورقة:** كل observation تُشار إلى نظريتها بـ `[Theory-NN]`.

---

## 14. الـ Philosophy Pipeline (v2.0 — جديد)

لما نلاحظ سؤال أعمق من "إيه؟" — سؤال "ليه؟" أو "إيه معنى؟":

1. **اعمل ملف فلسفي جديد** `PAPER/philosophy/NN_<question>.md` فيه:
   - **السؤال الفلسفي** بصياغة حادة.
   - **ليه السؤال ده مهم للمشروع**.
   - **الـ positions الممكنة** (مع الـ pros و cons).
   - **موقف الورقة المؤقت** (مع justification).
   - **الـ implications** على الـ findings والـ design.
   - **الـ open sub-questions**.
2. **في الورقة:** كل claim له بُعد فلسفي يُشار إلى الملف الفلسفي بـ `[Phil-NN]`.

---

**نهاية البروتوكول v2.0. لو فيه أي حاجة ناقصة، أضفها هنا قبل ما تبدأ شغل.**
