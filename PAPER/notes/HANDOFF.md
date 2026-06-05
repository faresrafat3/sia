# 📋 HANDOFF — آخر حالة للمشروع

**آخر تحديث:** 2026-06-05 (Session 4)  
**آخر commit:** `8bbdb93`

---

## ✅ المكتمل

- ✅ PAPER.md v0.1 + 8 figures + aggregated data
- ✅ PAPER_PROTOCOL.md + handoff system
- ✅ genesis/llm_helpers.py (463 tests passing)
- ✅ 11 OpenRouter keys + 5 Gemini keys working
- ✅ **Bug #6 discovered & fixed:** extract_response_text tuple unpacking
- ✅ `tasks/gpqa_subset_20` created for fast paper-grade iteration
- ✅ `run_openrouter_benchmark.py` now supports `--task_dir`
- ✅ First post-fix architecture comparison completed: `run_57`
- ✅ First targeted ablation completed: `run_58` (`A3 = no_pipeline`)

## 🔴 الحالة البحثية الحالية — أول Architecture Comparison مكتمل

**Run 55 على 198 سؤال تم إيقافه** لأنه يضيع وقت/Quota على free tier.
بعدها تم إنشاء المسار السريع `tasks/gpqa_subset_20`، وتم تشغيل أول مقارنة كاملة بعد الإصلاحات:

### `run_57` — GENESIS post-fix on 20-question subset
- **Generation 1:** 65.00% (13/20)
- **Generation 2:** 65.00% (13/20)
- **Pure baseline على نفس الـ subset:** 75.00% (15/20)
- **Architecture gap الحالي:** **−10.0 points**
- **Invalid answers:** 0 في الجيلين
- **الاستنتاج:** GENESIS recovered from catastrophic scaffolding failure, but still underperforms the direct baseline.

### `run_58` — A3 Ablation: no_pipeline
- **Generation 1:** 70.00% (14/20)
- **Generation 2:** 60.00% (12/20)
- **Delta vs run_57 Gen1:** **+5.0 points**
- **Gap vs pure baseline (Gen1):** **−5.0 points**
- **الاستنتاج:** removing pipeline leverage helps materially; feedback drift remains harmful.

## 📊 الأرقام الحرجة
- Pure baseline: **75.00%** (n=20)
- GENESIS pre-fix (run_53): **30.30%**
- GENESIS post-fix (run_57 gen1): **65.00%**
- GENESIS post-fix (run_57 gen2): **65.00%**
- Recovery from buggy run: **+34.7 points**
- Residual architecture gap vs baseline: **−10.0 points**
- Bugs found: 6 (5 original + tuple unpacking)
- Tests: 463/463

## 🎯 Next: Actual next step
1. **A4 / A7 feedback-focused ablation**
   - لأن `run_57` showed no net gain from feedback
   - و`run_58` showed feedback can actively worsen score (70 → 60)
2. Try stronger base model on same subset (Gemini / GPT-5 / Gemma)
3. Only after competitiveness, scale to full 198 questions
