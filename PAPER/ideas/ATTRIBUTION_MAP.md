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
| **Master Index** | ✅ مُحدّث | T5.91 + T5.92 + scope 5.1-5.92 + provenance + sources |
| **Theory-07** | ✅ مُنفّذ | `PAPER/theory/07_pipeline_as_memory_vs_decision_injection.md` |
| **Theory-08** | ✅ مُنفّذ | `PAPER/theory/08_feedback_value_determinism_scope.md` |
| **Theory-09** | ✅ مُنفّذ | `PAPER/theory/09_anticipatory_concepts_vs_lemmas.md` |
| **Phil-07** | ✅ مُنفّذ | `PAPER/philosophy/07_meaning_of_general_purpose_sufficiency.md` |
| **PAPER.md Section 8.5** (Contrast with LEAP) | ✅ مُنفّذ | 7 sub-sections (8.5.1–8.5.7), full integration of theories + philosophy + theft |
| **PAPER.md Abstract revision** | ✅ مُنفّذ | LEAP contrast + Theories 07/08/09 + Phil-07 reframing of RQ2 added |
| **PAPER.md §1.4 RQ2 reframing** | ✅ مُنفّذ | Added RQ2-revised based on Phil-07 Position D |
| **PAPER.md §10 Future Work** | ✅ مُنفّذ | Restructured into Tracks A–E; Track A is direct adoption of Theory-07/08/09 |
| **PAPER.md §11 Conclusion** | ✅ مُنفّذ | New paragraph integrating Theories + Phil-07; revised final claim |
| **PAPER.md Appendix B** | ✅ مُحدّث | T5.91 + T5.92 added |
| **PAPER.md Appendix C** (new) | ✅ مُنفّذ | Cross-reference to internal theories + philosophy |
| **PAPER.md Appendix D** (new) | ✅ مُنفّذ | Idea attribution table per [Idea-002] |
| **Figure 11** (110-point gap) | ✅ مُنفّذ | `PAPER/figures/fig11_110_point_gap.md` |
| **Figure 12** (Theory-08 quadrant) | ✅ مُنفّذ | `PAPER/figures/fig12_feedback_quadrant.md` |
| **Table 16** (LEAP vs GENESIS) | ✅ مُنفّذ | `PAPER/tables/tab16_leap_vs_genesis.md` + embedded in §8.5.1 |
| **Table 17** (Feedback Value Matrix) | ✅ مُنفّذ | `PAPER/tables/tab17_feedback_value_matrix.md` + embedded in §8.5.3 |

**حجم التأثير:** **CORE** — أعادت تشكيل RQ2 من "هل architecture يضيف قيمة؟" إلى "تحت أي conditions يضيف قيمة؟" *وتم تطبيق هذا الـ reframing في كل قسم رئيسي من الورقة*.

**مدخلات Session 7 + Session 8 (continuation):**

| Session | Outputs |
|---|---|
| Session 7 | 1 theft memo + 3 theories + 1 philosophy + Master Index update |
| Session 8 (this) | PAPER.md Section 8.5 (7 sub-sections), Abstract revision, RQ2 reframing, Future Work restructure, Conclusion revision, Appendix C + D added, Figure 11, Figure 12, Table 16, Table 17 |

**Status:** ✅ **INTEGRATED** — Idea-001 has fully entered the paper. Move from IN_PROGRESS to INTEGRATED.

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

## Agent-Initiated Synthesis (per [Idea-002] disclosure rule)

> **Disclosure principle (Idea-002):** Even Fares-authorized agent work is attributed transparently. When Fares says "القرار عندك" the agent is empowered to act, but the resulting work is labeled as **agent-initiated** (not Fares-authored) so the final paper can honor the actual division of intellectual labor.

### Session 9 agent-initiated work

| Item | Triggering context | Paper impact | Status |
|---|---|---|---|
| **Theory-10 (Reasoning Saturation)** | Fares delegation ("القرار عندك") + last untheorized Empirical Discovery (#1) | `PAPER/theory/10_*.md` (full theory, 14 sections); Section 7.3 expanded from placeholder to full theory; §1.5 Contributions item 7 added; §11 Conclusion mention; Appendix C row; Track A.5 added to Future Work | ✅ Integrated |
| **Literature anchor: Wu et al. 2025** | Search to support Theory-10 | Cited in §7.3.2, Theory-10 Axiom 1 & 4, Future Work | ✅ Cited (no theft memo yet) |
| **Literature anchor: UVA-Google DTR** | Search to support Theory-10 | Cited in §7.3.2 (r=-0.54 on same model family); Track A.5 DTR-style termination | ✅ Cited (no theft memo yet) |
| **Literature anchor: 4 more papers** | Search to support Theory-10 | Chen 2024b, Su 2025, OptimalThinkingBench, "When More Thinking Hurts" all cited in §7.3.2 | ✅ Cited |
| **Candidate Theft T5.93 (Wu et al.)** | Agent recommendation | Master Index entry pending Fares approval | ⏳ Proposed, awaiting decision |
| **Candidate Theft T5.94 (UVA-Google DTR)** | Agent recommendation | Master Index entry pending Fares approval | ⏳ Proposed, awaiting decision |

---

## ملخص

| ID | عنوان مختصر | مصدر | حجم التأثير | ملفات منفّذة |
|---|---|---|---|---|
| 001 | LEAP integration | Fares (Session 6) | CORE | 10+ (theft + 3 theories + 1 philosophy + index + Section 8.5 + 2 figures + 2 tables + future work + appendices) |
| 002 | Creative Attribution Rule | Fares (Session 7) | META-CORE | 5 (protocol §12.2 + map + proof + Appendix D + agent-initiated disclosure) |
| Theory-10 | Reasoning Saturation | Agent-initiated (Session 9, Fares-authorized) | MAJOR | 3 (full theory file + Section 7.3 expansion + Appendix C/D rows + 6 external citations) |

---

## ملاحظة للـ agent في الجلسات الجاية

عند إضافة أي محتوى جديد في الورقة:
1. **اسأل:** "هذا المحتوى جاء من أي Idea-NNN؟"
2. **سجِّل** الـ entry في الجدول أعلاه.
3. **أضف citation** `[Idea-NNN]` في موضع المحتوى نفسه.
4. **حدِّث** هذا الملف عند كل dependency جديد.

**القاعدة:** لا يدخل محتوى للورقة دون نسبه إلى مصدره (Idea, Theory, Phil, Theft, أو original execution by agent).
