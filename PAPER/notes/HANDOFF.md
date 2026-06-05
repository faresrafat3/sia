# 📋 HANDOFF — آخر حالة للمشروع

**آخر تحديث:** 2026-06-05 (Session 2 — انقطع بسبب hang)  
**الـ Session التالي:** سيبدأ من هنا

---

## ✅ اللي خلص (اكتمل واترفع)

| المكون | الحالة | آخر commit |
|--------|--------|------------|
| Pure baseline gpt-oss-120b على GPQA 20q | **75.00% مُثبت** | `a609c90` |
| تشخيص run_53 (30% = bugs) | **مكتمل** | `33ada0a` |
| 5 scaffolding bugs identified + fixed | **مكتمل** | `91cd9ea` |
| genesis/llm_helpers.py (220 سطر، 35 test) | **مكتمل** | `3a16a87` |
| orchestrator.py prompts updated | **مكتمل** | `3a16a87` |
| 463 tests passing (35 new + 428 old) | **مكتمل** | `3a16a87` |
| tools/api_key_pool.py (11-key pool) | **مكتمل** | `91cd9ea` |
| tools/providers.py (9 مزودين) | **مكتمل** | `6240094` |
| tools/model_registry.py (13 نموذج) | **مكتمل** | `6c840c6` |
| tools/run_multi_model_benchmark.py | **مكتمل** | `6c840c6` |
| GENESIS_RESEARCH_REPORT (515 سطر) | **مكتمل** | `3cbe48b` |
| PAPER_PROTOCOL.md | **مكتمل** | Session الحالية |
| PAPER/ directory structure | **مكتمل** | Session الحالية |

---

## 🔴 اللي ناقص (مش مكتمل — الـ session انقطعت هنا)

### أولوية قصوى

1. **PAPER.md — الورقة الرئيسية** (لم تُكتب بعد)
   - Skeleton الورقة بـ 12 قسم
   - يجب أن يحتوي على كل النتائج الحالية
   - Figures مرقمة + captions مفصلة
   - Tables بكل البيانات

2. **PAPER/notes/SESSION_LOG.md** — سجل الجلسات

3. **PAPER/notes/TODO_HIGH.md** — الأولويات

### أولوية عالية

4. **PAPER/figures/** — Figures الورقة:
   - `fig01_pipeline_overview.md` (Mermaid)
   - `fig02_baseline_vs_genesis.md` (bar chart)
   - `fig03_reasoning_correlation.md` (scatter)
   - `fig04_domain_difficulty.md` (heatmap matrix)

5. **PAPER/tables/** — جداول الورقة:
   - `tab01_models_registry.md`
   - `tab02_runs_summary.md`
   - `tab03_bugs_root_causes.md`
   - `tab04_per_question_results.md`

6. **PAPER/data/aggregated_results.json** — تجميع كل النتائج الخام

### أولوية متوسطة

7. **PAPER/references/** — بطاقات المصادر المستلهمة
8. **PAPER/sections/** — أقسام الورقة منفصلة للتحرير

---

## 🎯 الـ Critical Experiment المطلوب

**السؤال:** هل GENESIS بعد الإصلاحات يحقق > 75% (pure baseline)؟

**المتغيرات:**
- النموذج: `openai/gpt-oss-120b:free`
- المهمة: GPQA Diamond (20 سؤال subset)
- الإعداد: `max_gen=2`, `--use_evolutionary_discovery`
- الفارق: scaffolding fixes من commit `3a16a87` فقط

**الـ 3 سيناريوهات:**

| النتيجة | المعنى | الـ action |
|--------|--------|-----------|
| **> 75.00%** | البنية تضيف قيمة ✨ | Paper claim: architecture has positive impact |
| **≈ 75.00%** | البنية neutral | Need ablation to understand |
| **< 75.00%** | لسه bugs | Diagnose, fix, retry |

**المانع الحالي:** OpenRouter free tier daily quota exhausted على gpt-oss-120b.  
**الحلول:**
- انتظار UTC midnight (الـ quota بيرجع)
- استخدام GitHub Models (gpt-5 — فيه key شغال)
- استخدام Gemini keys (لما فارس يبعتهم)

---

## 📊 الأرقام الحرجة (لازم تفضل في الذاكرة)

| Metric | Value | المصدر |
|--------|-------|--------|
| gpt-oss-120b official GPQA | 80.1% | NVIDIA model card |
| gpt-oss-120b pure baseline (n=20) | **75.00%** | Run final baseline |
| gpt-oss-120b GPQA Physics subscore | 81.8% | Per-domain analysis |
| gpt-oss-120b GPQA Chemistry subscore | 66.7% | Per-domain analysis |
| gpt-oss-120b GPQA Biology subscore | 66.7% | Per-domain analysis |
| GENESIS run_53 (pre-fix) | 30.30% | Buggy scaffolding |
| Gap (pure − GENESIS old) | −44.70 | 5 bugs |
| Invalid rate smoke v1 | 35% | 4-pattern extract_letter |
| Invalid rate smoke v2 | 5% | 16-pattern + extract_response_text |
| Reasoning tokens: correct | avg 3,001 (median 989) | Counter-intuitive |
| Reasoning tokens: incorrect | avg 5,104 (median 6,836) | More thinking ≠ better |
| Empty content rate | 35% | finish_reason=length |
| Recovery rate (extract_response_text) | 86% | 6/7 recovered |
| Tests passing | 463/463 | 35 new + 428 existing |

---

## 🔬 الـ Discoveries الرئيسية (للورقة)

1. **Reasoning Saturation:** النموذج اللي يفكر أكثر = أقل دقة (counter-intuitive)
2. **Domain Asymmetry:** Physics 90%+ easy، Chemistry 83% hard
3. **Empty Content Phenomenon:** 35% من الـ requests محتواها فاضي — محتاجين extract من reasoning text
4. **Case Sensitivity Bug:** `q.get('question')` ≠ `'Question'` في JSON → −45 نقطة
5. **GitHub Models GPT-5:** متاح مجاناً على PAT فارس

---

## 🤔 أسئلة مفتوحة لفارس

1. متى هتبعت Gemini × 11 keys؟
2. متى هتبعت Groq × 11 keys؟
3. هل عايزني أجرب GitHub Models gpt-5 على GPQA قبل GENESIS؟
4. إيه أول المواضيع التقيلة اللي عايز تفتحها (بعد baseline confirmed)?
5. هل ننتظر UTC midnight للـ quota ولا نستخدم بديل؟

---

## ✍️ ملاحظات للـ agent الجاي

- الـ workspace نظيف — محتاج clone من `github.com/faresrafat3/GENESIS`
- الـ .env بيتحط محلياً على جهاز فارس (مش في الـ repo)
- آخر commit: `3cbe48b`
- الـ session السابقة انتهت بكتابة PAPER_PROTOCOL.md + بداية PAPER/ structure
- مازال يجب كتابة PAPER.md (الورقة الرئيسية) + figures + tables
- **لا تكرر الأخطاء:** لا تلخص، لا تكرر شغل — كمل من هنا
- **كل Claim يحتاج evidence:** يا figure، يا table، يا citation من theft