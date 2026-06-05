# 🤔 Philosophy — الأسئلة الفلسفية العميقة

هذا المجلد يحتوي على **المقالات الفلسفية** اللي تعالج الأسئلة العميقة قبل التجريبية:
- ماذا يعني "architecture adds value"؟
- ماذا يعني "scaffolding error" مقابل "model error"؟
- ماذا يعني "thinking model" أصلاً؟
- ماذا يعني "fair comparison" بين مدفوع/مجاني، quantized/full?
- ما الفرق بين "evaluation" و"measurement"؟

## الفلسفة

> لا نخاف نسأل أسئلة "ساذجة". الأسئلة الساذجة عادة بتكشف افتراضات خفية.
> — PAPER_PROTOCOL.md v2.0

---

## الـ Format لكل ملف فلسفي

`NN_<question_slug>.md` يحتوي:

1. **السؤال** بصياغة حادة.
2. **ليه السؤال مهم للمشروع**.
3. **الـ positions الممكنة** مع pros/cons.
4. **موقف الورقة المؤقت** (مع justification).
5. **الـ implications** على الـ findings والـ design.
6. **الـ open sub-questions**.

---

## الأسئلة المُخططة (نموذج أوّلي)

| # | السؤال | لماذا يهم؟ | الحالة |
|---|---|---|---|
| 01 | ماذا يعني "architecture adds value"؟ | يحدد معنى RQ2 كله | placeholder |
| 02 | كيف نفرّق "model error" عن "scaffolding error"؟ | يحدد attribution boundary | placeholder |
| 03 | هل "reasoning" نفس "internal tokens"؟ | يحدد دلالة reasoning saturation | placeholder |
| 04 | ما المعيار العادل للمقارنة بين free vs paid؟ | يحدد credibility الـ baselines | placeholder |
| 05 | ما الفرق بين "orchestration" و "scaffolding"؟ | يحدد nomenclature المشروع | placeholder |
| 06 | هل "Gen 2" نفس "Gen 1 + delta" أم نظام مختلف؟ | يحدد معنى feedback loop | placeholder |

**الترتيب أعلاه ليس نهائياً.** يُعدَّل حسب أفكار فارس.

---

## الـ Citation في الورقة

```
[Phil-NN]
```

مثال: "Under our working definition [Phil-01], architecture adds value iff Δ(orchestrated − pure) > 0 across a representative task distribution."

---

## ملاحظة منهجية

الـ philosophy هنا **ليست meta-commentary**. هي **شرط منطقي مسبق** لأي claim تجريبي. لو ما حددناش "ماذا يعني X"، الـ measurement لـ X بلا معنى.
