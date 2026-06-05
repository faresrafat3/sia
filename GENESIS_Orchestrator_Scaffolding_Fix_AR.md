# 🔧 إصلاح GENESIS Orchestrator Scaffolding — الـ Fix الكبير

**التاريخ:** 2026-06-05
**Commit:** (بعد الـ push)
**الغرض:** نقل الـ lessons من smoke_test_v2 (75% pure baseline) إلى GENESIS orchestrator
**Expected impact:** نظري لو GENESIS اشتغل صح، الجاية runs لازم تطلع 75%+ بدل 30% بتاع run_53

---

## 🎯 المشكلة اللي بنحلها

في run_53:
- **GENESIS مع gpt-oss-120b على GPQA = 30%**
- **gpt-oss-120b وحده على GPQA = 75%** (smoke v2)
- **الفجوة -45 نقطة** = scaffolding bugs، مش ضعف في النموذج

### الـ Root Causes اللي حددناها:
1. ❌ **Case mismatch**: `q.get('question')` بـ small q بينما JSON بيستخدم `'Question'` بـ capital Q
2. ❌ **max_tokens=50**: reasoning models تحتاج 16K+
3. ❌ **"output ONLY the letter"**: يمنع chain-of-thought ويرجع response فاضي
4. ❌ **مفيش extract من reasoning**: لما `content=''`، الـ reasoning موجود في `message.reasoning` بس مش بيتقرأ
5. ❌ **مفيش follow-up**: لو رد invalid، مفيش retry ذكي

---

## ✅ الإصلاحات المُطبقة في الـ commit ده

### 1. ملف جديد: `genesis/llm_helpers.py` (220 سطر)

**Battle-tested utilities** مأخوذة من tools/run_multi_model_benchmark.py:

```python
from genesis.llm_helpers import (
    extract_response_text,    # Handles content='' fallback to reasoning
    extract_letter,           # 16+ patterns for A/B/C/D parsing
    ask_for_letter_followup,  # Smart retry for invalid responses
    safe_get_question_field,  # Multi-case JSON key reader
    safe_get_question_id,
    safe_get_options,
    build_mcq_prompt,
    SCIENTIFIC_MCQ_SYSTEM_PROMPT,  # Standard CoT-friendly prompt
    FORCE_LETTER_PROMPT,      # For follow-up calls
)
```

**Key features:**
- `extract_response_text(resp)`: يدمج content + reasoning_details + reasoning fallback
- `extract_letter(text)`: 16 regex patterns (ANSWER:, FINAL ANSWER, **X**, \\boxed{X}, إلخ)
- `ask_for_letter_followup()`: إعادة سؤال للنموذج "STOP THINKING. Just output ANSWER: X"
- `safe_get_question_field(q, 'Question', 'question', ...)`: يحل bug run_53

### 2. تعديل: `genesis/orchestrator.py` (META_AGENT_PROMPT + FEEDBACK_AGENT_PROMPT)

#### META_AGENT_PROMPT — Q&A guidance أعيد كتابته بالكامل:

**القاعدة الذهبية الجديدة:**
> "Most reasoning models consume 1000-7000 tokens in INTERNAL reasoning. If max_tokens is too low or you ban CoT, the model returns content='' with finish_reason='length'."

**الـ guidance الجديد بيشمل:**

1. **🔑 Read fields with multiple case variants** (مع warning صريح عن bug run_53):
   ```python
   qtext = (q.get('Question') or q.get('question') or q.get('QUESTION')
            or q.get('text') or q.get('prompt') or '')
   ```

2. **🔑 Allow chain-of-thought reasoning** — system prompt يطلب reasoning ثم ينتهي بـ `ANSWER: X`

3. **🔑 max_tokens=16384** (مش 50!)

4. **🔑 Handle empty content** — extract من reasoning بـ fallback

5. **🔑 Extract letter بـ 16 patterns** — markdown, latex, plain

6. **🔑 Force-letter follow-up** للـ invalid responses

#### FEEDBACK_AGENT_PROMPT — diagnostic guidance أوضح:

دلوقتي بيشخص common failure modes واضحة:
- **Accuracy ~25%** → empty responses → الـ 4 root causes
- **Invalid > 10%** → استخدم force-letter follow-up
- **Letters uniform-random** → smoke test على الـ prompt الأول

### 3. ملف جديد: `tests/test_llm_helpers.py` (35 tests)

**كل الـ patterns مختبرة:**
- 16 extract_letter formats
- 5 safe_get_question_field scenarios (including run_53 bug case)
- 4 safe_get_question_id scenarios
- 5 safe_get_options scenarios  
- 5 build_mcq_prompt scenarios

**النتيجة:** **35/35 passed** ✓ + كل الـ 428 الـ existing tests لسه passing → total **463/463**

---

## 📊 المقارنة (متوقعة)

| الـ Setup | الـ GPQA Accuracy المتوقع | الـ Invalid Rate |
|---|---|---|
| run_53 (الـ buggy) | 30% | "0" (fake) |
| pure baseline (gpt-oss-120b وحده) | **75%** | 0% |
| **GENESIS بعد الـ fix (متوقع)** | **≥75%** | **<5%** |

لو GENESIS طلع **>75%** على نفس النموذج، يبقى **أول دليل علمي على القيمة المضافة للبنية** ✨

---

## 🛠️ كيفية التطبيق على الـ runs الجاية

### الطريقة 1: تلقائي (محبذ)
لما تشغل `run_openrouter_benchmark.py --task gpqa`:
- الـ meta-agent هيشوف الـ guidance الجديد في الـ prompt
- هيكتب `target_agent.py` بـ `from genesis.llm_helpers import ...`
- لو الـ import فشل (لأي سبب)، الـ inline patterns موجودة في الـ prompt كـ fallback

### الطريقة 2: يدوي
لو عايز تكتب `target_agent.py` بنفسك:
```python
from genesis.llm_helpers import (
    extract_response_text, extract_letter, build_mcq_prompt,
    SCIENTIFIC_MCQ_SYSTEM_PROMPT,
)

# للسؤال:
prompt = build_mcq_prompt(q)  # يحل bug 'Question' vs 'question'

resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": SCIENTIFIC_MCQ_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ],
    max_tokens=16384,  # مش 50!
    temperature=0.0,
)

text, meta = extract_response_text(resp)  # handles empty content
letter = extract_letter(text)             # 16 patterns
```

---

## 🎯 الـ Next Steps المقترحة

### Priority 1: Run GENESIS مع الـ fixes
لما الـ daily quotas ترجع، شغّل:
```bash
python run_openrouter_benchmark.py \
    --task gpqa --max_gen 2 --run_id 54 \
    --meta_model openai/gpt-oss-120b:free \
    --task_model openai/gpt-oss-120b:free
```

**التوقعات:**
- ✅ **لو GENESIS بيضيف قيمة**: > 75% (مثلاً 80%) ← الـ proof!
- 🟡 **لو GENESIS = baseline**: ≈75% (البنية مش بتأثر بس مش بتضر)
- ❌ **لو GENESIS < baseline**: < 75% (لسه فيه bugs لازم نشخصها)

### Priority 2: Multi-Provider Pool
بناءً على الجلسة السابقة، نوسع `api_key_pool.py` ليدير 9 مزودين بدل OpenRouter بس.

### Priority 3: المواضيع التقيلة (لما الـ baseline يتأكد)
حسب اللي رفعته:
- SWE-bench integration
- Paper writing strategy
- توسعة evolutionary discovery
- thinking vs instant modes router

---

## ✅ ملخص اللي عملته في الـ commit ده

| الملف | الحجم | الـ Change |
|---|---|---|
| `genesis/llm_helpers.py` | +220 سطر جديد | Battle-tested LLM utilities |
| `genesis/orchestrator.py` | +133/-9 سطور | Q&A guidance rewritten with fixes |
| `tests/test_llm_helpers.py` | +180 سطر جديد | 35 tests، كلهم passing |
| `GENESIS_Orchestrator_Scaffolding_Fix_AR.md` | جديد | تقرير شامل |

**Tests: 463/463 passed (35 new + 428 existing)**

---

## 🔥 الـ Key Insight

> **مش الـ AI ضعيف. الـ scaffolding هو اللي بيوصّل (أو يخرب) الـ signal للنموذج.**

run_53 (30%) ضد pure baseline (75%) أثبتها رياضياً. الـ commit ده ينقل كل اللي تعلمناه من بناء الـ baseline infrastructure إلى GENESIS نفسه.

دلوقتي عندنا:
- ✅ `genesis.llm_helpers` كـ shared library  
- ✅ Tests شاملة (35 جديدة + 428 قديمة = 463)
- ✅ Prompts محدثة بـ explicit guidance + warnings
- ✅ Fallback pattern (لو import فشل، الـ inline موجود)
- ⏭ ينتظر run جديد للتأكيد التجريبي
