# Virtual-SIA

نسخة أولية/تجريبية من طبقة ذكاء تشغيلية فوق LLM APIs.

## الوضع الحالي
المشروع الآن في مرحلة **Experimental Regime Consolidation**:
- TaskCase-based evaluation where available
- Memory OS minimal
- Concept formation minimal
- Economy-aware routing
- Contradiction / anomaly / theory plumbing minimal

## أهم أوامر التشغيل
### Primary thesis regime
```bash
python -m virtual_sia.eval.runners.run_local_eval_v3b_curriculum
```

### Diagnostic slice
```bash
python -m virtual_sia.eval.runners.run_local_eval_v4
```

### Selectivity ablation
```bash
python -m virtual_sia.eval.runners.run_selectivity_ablation
```

### Family-specific selectivity ablation
```bash
python -m virtual_sia.eval.runners.run_family_selectivity_ablation
```

## أين أقرأ أكثر؟
راجع في root workspace:
- `Virtual_SIA_Current_Regime_Memo_AR.md`
- `Virtual_SIA_Current_Evidence_Package_AR.md`
- `Virtual_SIA_Decision_Memo_AR.md`
- `Virtual_SIA_Current_Reference_Index_AR.md`

## ملاحظة
هذه ليست production system بعد. هي research/execution prototype تهدف إلى اختبار فرضيتين مركزيتين:
1. Concept Formation beats retrieval-only adaptation
2. Cognitive Economy beats stronger-model-only scaling
