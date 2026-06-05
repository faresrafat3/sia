# 📋 HANDOFF — آخر حالة للمشروع

**آخر تحديث:** 2026-06-05 (Session 6)
**آخر commit:** `(pending after this session)`

## ⚠️ تغيير جوهري في الـ Mode — اقرأه أولاً

في Session 6، فارس قرر صراحة:

> "هنعمل اسكيب لمواضيع التشغيل، احنا هنضبطها على الورقة وفلسفياً ونظرياً المشروع بالكامل بالأفكار اللي لسه هتجي."

**يعني:**
- ✅ نشتغل على الورقة، النظرية، الفلسفة، والأفكار الجديدة من فارس.
- ❌ لا نشغّل runs جديدة، لا نستهلك free tier، لا نقترح ablations عملية كأولوية.
- 🔄 الديناميكية تبادلية: فارس يعطي أفكار، agent ينفّذ ويوسّع ويقترح أيضاً.

**التفاصيل الكاملة:** اقرأ `PAPER_PROTOCOL.md` (v2.0).

---

## ✅ المكتمل (لا يتغير في v2.0)

### البنية التحتية
- ✅ PAPER.md v0.2 + 10 figures + aggregated data
- ✅ PAPER_PROTOCOL.md v2.0 (Theoretical Mode)
- ✅ genesis/llm_helpers.py (463 tests passing)
- ✅ 11 OpenRouter keys + 5 Gemini keys + GitHub PAT (متاحة، مؤجلة)
- ✅ `tasks/gpqa_subset_20` for fast paper-grade iteration
- ✅ `run_openrouter_benchmark.py` يدعم `--task_dir` + `--ablation_mode` (na, no_pipeline, narrow_feedback, no_pipeline+narrow_feedback)

### النتائج التجريبية (Empirical Anchors — ثابتة)
- ✅ Pure baseline: **75.00%** (n=20)
- ✅ GENESIS pre-fix (run_53): **30.30%** (n=198)
- ✅ GENESIS post-fix standard (run_57): **65.00%** (both gens)
- ✅ A3 no_pipeline (run_58): Gen1 = **70.00%**, Gen2 = **60.00%**
- ✅ 6 bugs documented and fixed
- ✅ Question-by-question delta analysis complete

### الإكتشافات التجريبية (موضوع للتنظير في v2.0)
1. Reasoning saturation: more tokens → less accuracy
2. Domain asymmetry: Physics easy, Chemistry Organic hard
3. Empty content phenomenon: 35% of reasoning responses return content=""
4. Architecture gap localization: loss concentrated on Chemistry
5. Feedback drift: Gen 2 changes pattern without improving total score
6. Pipeline overhead: removing it recovers half the gap

---

## 🆕 الجديد في Session 6 (v2.0 Infrastructure)

### بنية تحتية فكرية جديدة
- ✅ `PAPER_PROTOCOL.md` v2.0 — يعكس Theoretical Mode + Ideas/Theory/Philosophy pipelines
- ✅ `PAPER/ideas/` — bank الأفكار من فارس (INBOX, IN_PROGRESS, INTEGRATED)
- ✅ `PAPER/theory/` — النظريات اللي تشرح الـ observations (6 placeholders)
- ✅ `PAPER/philosophy/` — الأسئلة الفلسفية العميقة (6 placeholders)
- ✅ Citation tags جديدة: `[Idea-NNN]`, `[Theory-NN]`, `[Phil-NN]`

### لا يوجد runs جديدة في هذه السيشن — بالقصد

---

## 🎯 Next: الـ Ideas Pipeline في انتظار فارس

### الـ workflow الجديد

1. فارس يقول فكرة جديدة (نظرية، فلسفية، paper، تطوير).
2. أنا أستلمها فوراً في `PAPER/ideas/INBOX.md`.
3. أعمل ملف تفصيلي `idea_NNN_<slug>.md`.
4. أسأل توضيحياً إن لزم.
5. أقترح اتجاهات للتوسع.
6. فارس يوافق/يرفض/يعدّل.
7. ندخل التنفيذ (IN_PROGRESS).
8. ندخل الورقة (INTEGRATED).

### بدائل لو فارس مش جاهز بفكرة محددة

أقترح نبدأ بواحد من دول (كلهم theoretical/philosophical):

**(A) أكتب أول نظرية كاملة:** Theory-01 (Pipeline Overhead Theory)
- نشرح ليه إضافة pipeline أضرت بالـ score
- نربطها بـ Cognitive Economy theory الداخلية
- نربطها بـ Reasoning Saturation
- نشتق منها predictions جديدة

**(B) أكتب أول مقال فلسفي:** Phil-01 (ماذا يعني "architecture adds value"؟)
- نحدد معنى RQ2 بدقة
- نطرح positions ممكنة
- نختار موقف الورقة

**(C) أعمل deep dive في الـ thefts:**
- أقرأ الـ 102+ سرقة
- أبني خريطة "كل ظاهرة عندنا → أي theft تشرحها"
- أرجع بـ thefts فاضلين ما اشتغلناش عليهم بعد

**(D) أكتب deep related work section للورقة:**
- بـ 5-7 أقسام فرعية
- تربط GENESIS بـ context أوسع: SIA, Reflexion, AlphaEvolve, Co-Scientist, Aletheia, STaR, Self-Refine, إلخ

**(E) فكرة من عند فارس** — وأنا أنفّذ.

---

## 📊 الأرقام الحرجة المحفوظة (ثابتة)

- Pure baseline: **75.00%** (n=20)
- GENESIS pre-fix (run_53): **30.30%** (n=198)
- GENESIS post-fix (run_57 gen1/gen2): **65.00% / 65.00%**
- A3 no_pipeline (run_58 gen1/gen2): **70.00% / 60.00%**
- Recovery from buggy run: **+34.7 points**
- Half of residual gap explained by pipeline overhead (+5 from A3)
- Tests: 463/463

---

## ✍️ ملاحظة للـ session الجاي

اقرأ `PAPER_PROTOCOL.md` v2.0 أولاً.
ثم اقرأ هذا الملف.
ثم اسأل فارس: **"عندك فكرة جديدة نشتغل عليها، أم تختار من (A) إلى (D) أعلاه؟"**

**لا تقترح runs جديدة** إلا لو فارس صراحة طلب.
