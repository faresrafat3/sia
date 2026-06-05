# 🧠 Theory — النظريات اللي تشرح "ليه؟"

هذا المجلد فيه **النظريات الداخلية** للمشروع. كل نظرية تربط:
- ظاهرة تجريبية مُلاحَظة
- بـ مبادئ أولية (axioms)
- بـ توقعات قابلة للاختبار (predictions)
- بـ نظريات أخرى داخلية وخارجية

## الفلسفة

> نحن لا نكتفي بـ observation. كل ظاهرة تحتاج نظرية تفسرها.
> — PAPER_PROTOCOL.md v2.0

---

## الـ Format لكل ملف نظرية

`NN_<theory_name>.md` يحتوي:

1. **العنوان + الـ tag** (Theory-NN).
2. **الظاهرة المُلاحظة** (observation).
3. **الفرضية المركزية** (central hypothesis).
4. **الـ axioms / المبادئ الأولية**.
5. **الـ propositions المشتقة**.
6. **التوقعات (predictions) القابلة للاختبار**.
7. **الـ empirical checks الموجودة** (لو فيه).
8. **الـ empirical checks اللي تنقص** (للمستقبل).
9. **الروابط بالنظريات الأخرى** (داخلية + خارجية).
10. **الروابط بالأقسام في الورقة**.

---

## النظريات المُخططة (نموذج أوّلي)

| # | النظرية | تشرح ماذا؟ | الحالة |
|---|---|---|---|
| 01 | Pipeline Overhead Theory | لماذا إضافة pipeline تؤذي بدل ما تساعد؟ | placeholder |
| 02 | Feedback Drift Theory | لماذا feedback agent يغير النمط بدون تحسن صافي؟ | placeholder |
| 03 | Reasoning Saturation Theory | لماذا more reasoning tokens → less accuracy؟ | placeholder |
| 04 | Domain Asymmetry Theory | لماذا Physics سهل و Chemistry Organic صعب على نفس النموذج؟ | placeholder |
| 05 | Empty Content Phenomenon Theory | لماذا 35% من responses ترجع content=""؟ | placeholder |
| 06 | Scaffolding-vs-Architecture Theory | كيف نفصل خطأ هندسي عن قيد معماري؟ | placeholder |

**الترتيب أعلاه ليس نهائياً.** يُعدَّل حسب أفكار فارس والاكتشافات الجديدة.

---

## الـ Citation في الورقة

```
[Theory-NN]
```

مثال: "نلاحظ pipeline overhead consistent with Theory-01."

---

## الروابط بالأدبيات

كل نظرية ترتبط:
- بـ السرقات الـ 102+ في `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md`.
- بـ النظريات الداخلية الموجودة في الـ docs (Cognitive Economy, Anomaly Leverage, Concept Formation, Identity Governance, Productive Forgetting, إلخ).
- بـ external papers معروفة.
