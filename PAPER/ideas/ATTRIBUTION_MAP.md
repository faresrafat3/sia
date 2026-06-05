# 🗺️ Attribution Map — تتبع تأثير أفكار فارس على الورقة

> **بموجب [Idea-002]:** كل فكرة من فارس تُسجَّل + تُربط بكل ما تأثر بها في الورقة.

## الغرض

هذا الملف يجيب على السؤال:
> "أي جزء من الورقة جاء من أي فكرة من فارس؟"

ويُستخدم في:
- Acknowledgments الورقة النهائية.
- Author Contributions section.
- التتبع الأمين لمصدر كل insight.

---

## الـ Format

```
## Idea-NNN — <عنوان>
**التأثير على الورقة:**
- Section X.Y: <كيف تأثر>
- Figure N: <كيف تأثر>
- Table M: <كيف تأثر>
- Theory-NN: <كيف تأثر>
- Phil-NN: <كيف تأثر>
- Theft T#: <كيف تأثر>

**حجم التأثير:** core / major / supporting / minor
```

---

## Idea-001 — LEAP (arXiv 2606.03303)

**نص فارس الأصلي:** "Link – arxiv. org/abs/2606.03303 Title: 'LEAP: Supercharging LLMs for Formal Mathematics with Agentic Frameworks'"

**التأثير على الورقة:**

| العنصر | الحالة | الوصف |
|---|---|---|
| **Theft T5.92** | ✅ مُنفّذ | `GENESIS_DeepMind_LEAP_Agentic_Theft_AR.md` — سرقة شرعية كاملة (10 sections) |
| **Master Index** | ✅ مُحدّث | T5.92 + scope 5.1-5.92 + provenance + sources |
| **Theory-07** | ✅ مُنفّذ | `PAPER/theory/07_pipeline_as_memory_vs_decision_injection.md` |
| **Theory-08** | ✅ مُنفّذ | `PAPER/theory/08_feedback_value_determinism_scope.md` |
| **Theory-09** | ✅ مُنفّذ | `PAPER/theory/09_anticipatory_concepts_vs_lemmas.md` |
| **Phil-07** | ✅ مُنفّذ | `PAPER/philosophy/07_meaning_of_general_purpose_sufficiency.md` |
| **Section 8.5** (Contrast with LEAP) | ⏳ مخطط | placeholder موجود في idea file |
| **Table 16** (LEAP vs GENESIS) | ⏳ مخطط | في theft memo (§5) |
| **Figure 11** (110-point gap) | ⏳ مخطط | spec في theft memo (§5) |
| **Figure 12** (Theory-08 quadrant) | ⏳ مخطط | spec في Theory-08 |
| **Table 17** (Feedback value matrix) | ⏳ مخطط | spec في Theory-08 |
| **Future Work** | ⏳ مخطط | يتبع Section 8.5 |

**حجم التأثير:** **CORE** — أعادت تشكيل RQ2 من "هل architecture يضيف قيمة؟" إلى "تحت أي conditions يضيف قيمة؟"

**مدخلات Session 7:**
- 1 theft memo (10 sections)
- 3 theories (07, 08, 09)
- 1 philosophy article (Phil-07)
- 1 Master Index update
- 1 IN_PROGRESS update

---

## Idea-002 — Creative Attribution Rule (قاعدة نَسب الإبداع)

**نص فارس الأصلي:** "تمام خلي بالك اضافه السرقه الشرعيه القويه دي كفكره مني فلو عندك حاجات زي كده ابداعيه باي شكل اعملها تمام ونعم اشتغل"

**التأثير على الورقة:**

| العنصر | الحالة | الوصف |
|---|---|---|
| **PAPER_PROTOCOL.md §12.2** | ✅ مُطبَّق | قاعدة فارس الإبداعية رسمياً في البروتوكول |
| **ATTRIBUTION_MAP.md** | ✅ مُنشأ | هذا الملف نفسه |
| **idea_002_creative_attribution_rule.md** | ✅ مُنشأ | proof-of-concept للقاعدة نفسها |
| **كل سرقة وnظرية وفلسفة تُكتب لاحقاً** | ✅ ملزم | بـ tag [Idea-NNN] و source attribution |
| **Acknowledgments (مستقبلي)** | ⏳ مخطط | كل idea ستُذكر بالاسم |
| **Author Contributions (مستقبلي)** | ⏳ مخطط | تمييز vision (Fares) vs execution (agent) |

**حجم التأثير:** **META-CORE** — تحكم كل الأفكار الجاية، وتشكّل الـ research ethics للمشروع.

---

## ملخص

| ID | عنوان مختصر | حجم التأثير | ملفات منفّذة | ملفات مخططة |
|---|---|---|---|---|
| 001 | LEAP integration | CORE | 5 (theft + 3 theories + 1 philosophy + index update) | 5 (Section 8.5 + 2 figures + 2 tables + future work) |
| 002 | Creative Attribution Rule | META-CORE | 3 (protocol + map + proof) | 2 (acknowledgments + contributions) |

---

## ملاحظة للـ agent في الجلسات الجاية

عند إضافة أي محتوى جديد في الورقة:
1. **اسأل:** "هذا المحتوى جاء من أي Idea-NNN؟"
2. **سجِّل** الـ entry في الجدول أعلاه.
3. **أضف citation** `[Idea-NNN]` في موضع المحتوى نفسه.
4. **حدِّث** هذا الملف عند كل dependency جديد.

**القاعدة:** لا يدخل محتوى للورقة دون نسبه إلى مصدره (Idea, Theory, Phil, Theft, أو original execution by agent).
