# 📜 PAPER PROTOCOL — دليل العمل على الورقة عبر الجلسات

**⚠️ اقرأ هذا الملف أولاً قبل أي تعديل على الورقة. هذا هو العقد بيني (الـ agent) وبين فارس (المالك).**

**التاريخ:** 2026-06-05  
**النسخة:** 1.0  
**الوضع:** Living document — يُحدّث بعد كل session كبيرة

---

## 1. الهدف من الورقة

**"نهدف لأقوى ورقة في المجال"** — فارس

نبني paper بحثية واحدة كبيرة (مش تقارير مفرقة) عن:

### السؤال البحثي الأساسي

**هل تضيف بنية orchestration (GENESIS) قيمة قابلة للقياس فوق الـ baseline لـ LLMs على المهام الـ reasoning-heavy، وكيف تتفاعل البنية مع نوعي النماذج (instant vs thinking)?**

### الأهداف الفرعية

1. توثيق علمي صارم للحالة الحالية (baselines, bugs, fixes)
2. Ablation studies تفصيلية لكل component
3. تحليل عبر النماذج (cross-model architecture impact)
4. **(مؤجل لمرحلة لاحقة):** Instant vs Thinking comparison
5. ربط النتائج بـ literature (الـ 102 سرقة الموثقة)

---

## 2. هيكل الـ Repository للورقة

```
PAPER.md                        ← الورقة الرئيسية (master document)
PAPER_PROTOCOL.md               ← هذا الملف (دليل العمل)
PAPER/
├── sections/                   ← أقسام الورقة منفصلة للتحرير المريح
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
├── figures/                    ← كل الرسوم البيانية
│   ├── README.md              ← فهرس بكل figure + الوصف
│   ├── fig01_pipeline_overview.md      (Mermaid diagram)
│   ├── fig02_baseline_vs_genesis.md    (ASCII chart)
│   ├── fig03_reasoning_correlation.md  (scatter plot ASCII)
│   ├── fig04_domain_difficulty.md      (matrix heatmap)
│   └── ... (نضيف بالتدريج)
│
├── tables/                     ← الجداول
│   ├── README.md              ← فهرس
│   ├── tab01_models_registry.md       (13 models with benchmarks)
│   ├── tab02_runs_summary.md          (6 runs بكل التفاصيل)
│   ├── tab03_bugs_root_causes.md      (5 bugs + fixes)
│   ├── tab04_per_question_results.md  (20 سؤال × 6 runs)
│   └── ... (نضيف بالتدريج)
│
├── references/                 ← المصادر اللي نستلهم منها
│   ├── README.md              ← فهرس بكل reference + ليه مهم
│   ├── 001_alphaevolve_funsearch.md   (DeepMind, Nature 2023)
│   ├── 002_aletheia.md                (DeepMind)
│   ├── 003_coscientist.md             (DeepMind)
│   ├── 004_sia_self_improving_agents.md
│   ├── 005_reflexion.md
│   ├── 006_star_self_taught_reasoner.md
│   ├── 007_self_refine.md
│   ├── 008_gpqa_benchmark.md
│   └── ... (نضيف من المصادر الـ 102)
│
├── data/                       ← البيانات الخام للورقة
│   ├── aggregated_results.json        (كل النتائج مجمعة)
│   ├── reasoning_token_analysis.csv
│   ├── per_question_consensus.json
│   └── ... (نضيف من results/ بالتدريج)
│
└── notes/                      ← ملاحظات الـ session للـ continuity
    ├── SESSION_LOG.md         ← سجل كل session: ماذا أُضيف؟
    ├── TODO_HIGH.md           ← أولويات حرجة
    ├── TODO_MEDIUM.md         ← أولويات متوسطة
    ├── OPEN_QUESTIONS.md      ← أسئلة مفتوحة نناقشها مع فارس
    └── HANDOFF.md             ← الملف الأهم للـ session الجاية
```

---

## 3. قواعد الكتابة (Writing Style)

### اللغة

- **اللغة الأساسية:** العربية الفصحى/المصرية المختلطة (زي لما فارس بيكلمني)
- **الـ technical terms:** بالإنجليزية مع ترجمة عربية أحياناً للوضوح
- **الـ code/equations:** بالإنجليزية فقط
- **الـ Mermaid diagrams:** labels بالإنجليزية (للـ rendering)

### النبرة (Tone)

- **علمي صارم** — كل ادعاء له دليل (بيانات + المصدر)
- **شفاف** — نذكر الـ limitations صراحة
- **مفصل** — لا نختصر على حساب الفهم
- **متواضع لكن واثق** — "نظهر أن..." بدل "أثبتنا قطعياً..."

### الـ Citations

- **لـ الـ thefts:** نشير بـ `[T#]` حيث # رقم السرقة في `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md`  
  مثال: "نتبنى منهجية evolutionary search من AlphaEvolve [T5.86]"
- **لـ الـ external papers:** بـ نمط `[Author Year]`  
  مثال: "GPQA Diamond benchmark [Rein 2024]"
- **لـ النتائج الداخلية:** نشير بـ figure/table number  
  مثال: "كما يظهر في Figure 3 / Table 2"

### الـ Numbers

- **دقة:** نسبة مئوية بـ 2 خانات عشرية (75.00%) أو 1 (75.0%) حسب السياق
- **مع margin of error:** كلما أمكن (75.0% ± 10% on n=20)
- **مقارنات:** نوضح الفرق (Δ) صراحة (+10.0 نقطة)

---

## 4. الـ Workflow عبر الجلسات (Session Handoff)

### في بداية كل session جديد، أنا (الـ agent) لازم:

1. **اقرأ** `PAPER_PROTOCOL.md` (هذا الملف) كاملاً
2. **اقرأ** `PAPER/notes/HANDOFF.md` — آخر حالة من الـ session السابقة
3. **اقرأ** `PAPER/notes/SESSION_LOG.md` — تاريخ كل session
4. **اقرأ** `PAPER.md` — الورقة الحالية
5. **اقرأ** `PAPER/notes/TODO_HIGH.md` — الأولويات
6. **اسأل فارس:** "أكمل من X (آخر session) أم خطوة جديدة Y?"

### في نهاية كل session، أنا لازم:

1. **حدّث** `PAPER.md` بالتغييرات الجديدة
2. **أضف entry في** `PAPER/notes/SESSION_LOG.md`:
   - التاريخ + ID الـ session
   - إيش اتعمل (مفصل)
   - إيش الـ figures/tables الجديدة
   - أي ادعاءات علمية جديدة + دليلها
   - الـ commits المرفوعة
3. **حدّث** `PAPER/notes/HANDOFF.md`:
   - الحالة الحالية (Current State)
   - الـ open threads (شغل مش مكتمل)
   - الـ next concrete step
   - أي قرار محتاج فارس يأكده
4. **حدّث** `PAPER/notes/TODO_HIGH.md` و `TODO_MEDIUM.md`
5. **أضف أي سؤال مفتوح في** `PAPER/notes/OPEN_QUESTIONS.md`
6. **اعمل commit واحد كبير** بـ message شامل

### القاعدة الذهبية

**"اللي مش مكتوب في الورقة أو notes، لم يحدث."**  
أي اكتشاف، أي قرار، أي نتيجة — لازم تتسجل. لا تعتمد على ذاكرة الـ session.

---

## 5. الـ Figures و Tables — معايير الجودة

### الـ Figures

- **كل figure له رقم + caption مفصل** (لا "Figure 1" بدون شرح)
- **الـ caption يشرح ماذا نرى + ماذا نستنتج**
- **استخدم Mermaid لـ flowcharts/architectures** (يرندر في GitHub)
- **استخدم ASCII art لـ charts بسيطة** (يعرض في أي محرر)
- **استخدم SVG inline للرسوم المعقدة** (يرندر في GitHub)
- **كل figure مرتبط بـ section** يشير إليه

### مثال على caption قوي:

```
Figure 3: Reasoning Token Consumption vs Answer Correctness on GPQA Diamond (n=20).

The x-axis shows reasoning_tokens consumed per question (from API usage data).
The y-axis shows whether the model answered correctly (1) or not (0).
Each point is one question; size proportional to number of models that answered.

Key observation: Counter-intuitively, questions that consumed MORE reasoning
tokens were LESS likely to be answered correctly (median 6,836 tokens for
incorrect vs 989 for correct). This challenges the naive "more thinking =
better" assumption and is discussed in Section 7.3.
```

### الـ Tables

- **كل column له اسم واضح + unit (لو رقم)**
- **الـ rows لها logical ordering** (بالأداء، بالـ chronology، بالـ category)
- **الـ highlights بـ bold** (الأفضل/الأسوأ/الـ relevant)
- **الـ caption يشرح ما يوضحه الجدول**

---

## 6. الاستلهام من الـ Thefts

**القاعدة:** لا نخترع pattern لو في pattern موثق في paper سرقناها منها.

### كيف نستلهم:

1. **قبل ما نختار format للـ figure/section:**
   - شوف الـ paper الأصلية (FunSearch، AlphaEvolve، Aletheia، إلخ)
   - افهم إزاي عرضوا نتائجهم
   - استلهم (مش نسخ) الـ structure

2. **للـ tables:**
   - **AlphaEvolve [T5.86]:** يقدم النتائج بـ ablation tables
   - **GPQA paper [Rein 2024]:** يقدم per-domain breakdowns
   - **FunSearch [Nature 2023]:** يقدم evolutionary trajectory plots

3. **للـ figures:**
   - **Reflexion [T5.5]:** memory architecture diagrams
   - **STaR [T5.7]:** training loop visualization
   - **Self-Refine [T5.6]:** generate→critique→refine loops

4. **للـ writing structure:**
   - **DeepMind papers:** open with strong "what we found"
   - **OpenAI papers:** strong methodology sections
   - **Academic papers:** clear limitations sections

### بروتوكول الاستلهام

لما نستلهم من theft معين:
1. سجل في `PAPER/references/<NNN>_<name>.md` ليه استلهمنا منه
2. اذكر بـ صريح في الورقة: "Following the approach of [Author Year]..." أو "Inspired by AlphaEvolve [T5.86] which uses..."
3. وضح **الفرق** عنهم (ليه أخذنا حاجة وتركنا حاجة)

---

## 7. الـ Versioning

- **PAPER.md:** semantic versioning (v0.1 → v0.2 → v1.0)
- **major version:** لما نضيف section جديد أو تغيير كبير في النتائج
- **minor version:** لما نضيف figure/table/data جديد

السجل في `PAPER/notes/SESSION_LOG.md`:
```
## v0.3 — 2026-06-05 (Session 2)
- Added Figure 5: Per-domain accuracy bar chart
- Added Table 3: Bugs taxonomy with fixes
- Updated Section 7: Reasoning correlation analysis
- Commits: abc1234, def5678
```

---

## 8. النواهي (Don'ts)

- ❌ **لا تنشئ تقارير منفصلة** (`*_REPORT_*.md`) — كل شيء يدخل في الورقة
  - **استثناء:** تقارير سابقة موجودة بالفعل تبقى للأرشيف
- ❌ **لا تكتب claims بدون دليل** — كل ادعاء يحتاج figure/table/citation
- ❌ **لا تنسى تحدّث** `HANDOFF.md` في نهاية كل session
- ❌ **لا تختصر على حساب الوضوح** — فارس قال "بالغ في التفاصيل"
- ❌ **لا تستخدم نماذج مدفوعة بدون إذن** — اسأل فارس أولاً
- ❌ **لا تنشر مفاتيح في الـ commits** — اعمل scan دائماً قبل push

---

## 9. القرارات المعمارية المُتفق عليها مع فارس

| السؤال | القرار | السبب |
|--------|--------|-------|
| نبني router للـ instant/thinking? | **لا — مؤجل** | مرحلة لاحقة بعد baseline قوي |
| نضيف complexity جديدة؟ | **لا — الأول baseline** | نتأكد إن الأساس متين |
| نستخدم نماذج مدفوعة؟ | **لا في المرحلة الحالية** | فيزا فارس الافتراضية لا تُشحن |
| GitHub Models (PAT)? | **متاح** | gpt-5, gpt-4.1, gpt-4o, DeepSeek-R1, Phi-4 |
| متى نختبر GENESIS post-fix? | **لما daily quota يرجع** | أو لما فارس يبعت Gemini/Groq keys |
| نضيف Gemini × 11 keys? | **أيوة، فارس هيحضرهم** | أولوية على Groq |
| نضيف Groq × 11 keys? | **أيوة، فارس هيحضرهم** | ثاني أولوية |
| NVIDIA NIM? | **مش متاح في مصر** | skip |

---

## 10. الـ Reference Quick Cards

### المفاتيح المتاحة (للسياق فقط، الكيز نفسها في .env المحلي):

- ✅ 11 OpenRouter keys (free tier — بعض النماذج exhausted)
- ✅ 1 GitHub PAT (gpt-5, gpt-4.1, gpt-4o, DeepSeek-R1, Phi-4 شغّالين)
- ⏳ Gemini × 11 (فارس يحضّرهم)
- ⏳ Groq × 11 (فارس يحضّرهم)
- ❌ NVIDIA NIM (مش متاح في مصر)

### الـ Benchmark الأساسي:

- **GPQA Diamond** — 198 questions, A/B/C/D MCQ, 3 domains (Physics 86, Chemistry 93, Biology 19)
- نستخدم subset 20 questions للسرعة، الـ 198 الكامل للقياس النهائي

### الـ Pure Baseline المُثبت:

- gpt-oss-120b:free على GPQA 20q = **75.00%** (vs 80.1% official → gap -5.1)

### الـ Critical Unknown:

- GENESIS post-fix accuracy على نفس الـ setup = **؟؟؟**

---

## 11. الـ Session Continuity — كيف تستلم الجلسة الجاية

```
1. اقرأ هذا الملف (PAPER_PROTOCOL.md)
2. اقرأ PAPER/notes/HANDOFF.md
3. اقرأ PAPER.md
4. اسأل فارس: "أكمل من X أم Y?"
5. اشتغل
6. حدّث PAPER.md + HANDOFF.md + SESSION_LOG.md
7. اعمل commit واحد كبير شامل
8. لا تنسى scan أمني قبل push
```

**نهاية البروتوكول. لو فيه أي حاجة ناقصة، أضفها هنا قبل ما تبدأ شغل.**