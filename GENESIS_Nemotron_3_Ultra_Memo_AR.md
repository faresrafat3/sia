# 🚀 Nemotron 3 Ultra — مذكرة استكشاف لـ GENESIS

**التاريخ:** 2026-06-04 (يوم الإطلاق!)
**المصدر الرسمي:** NVIDIA Developer Blog + OpenRouter
**الحالة:** متاح **اليوم** على OpenRouter

---

## 📋 البطاقة الفنية (الأرقام الرسمية)

| الخاصية | القيمة |
|---|---|
| **Model ID على OpenRouter** | `nvidia/nemotron-3-ultra-550b-a55b` |
| **حجم النموذج** | 550B إجمالي / **55B active** (MoE) |
| **البنية** | Hybrid Transformer-Mamba + MoE + Multi-Token Prediction |
| **Context Window** | **1,000,000 token (1M)** ✅ |
| **Max Output** | 16,384 tokens |
| **تاريخ الإصدار** | 4 يونيو 2026 |
| **Provider** | DeepInfra (واحد دلوقتي، NVIDIA NIM جاي) |
| **الـ Modalities** | Text in / Text out |
| **Reasoning support** | ✅ (مع `reasoning` parameter) |
| **Tool calling** | ✅ |

### السعر
| Tier | Input | Output | Cache Read |
|---|---|---|---|
| Paid (DeepInfra) | $0.50 / 1M tokens | $2.50 / 1M tokens | $0.15 / 1M tokens |
| **Free tier (NVIDIA NIM)** | $0 | $0 | — (rate limited + يُسجَّل) |

> **مهم:** الـ `:free` endpoint بيتسجل عشان NVIDIA تحسّن منتجاتها. **لا ترفع بيانات حساسة عليه.** ده ينطبق على كل اختبارات GPQA / SWE-bench عادي لأن البيانات public.

---

## 🏆 الـ Benchmarks الرسمية (من NVIDIA blog)

### Agent Orchestration (نقطة قوة Ultra الأساسية)

| Benchmark | Nemotron 3 Ultra (550B) | GLM 5.1 (744B) | Kimi K2.6 (1T) | Qwen3.5 (397B) |
|---|---|---|---|---|
| **Agent Productivity** (PinchBench) | **91%** 🥇 | 84% | 91% | 89% |
| **Long-horizon Planning** (EnterpriseOps-Gym) | 33% | **40%** 🥇 | 29% | 30% |
| **Coding** (Terminal-Bench 2.0) | 54% | 64% | **67%** 🥇 | 53% |
| **Instruction Following** (IFBench) | **82%** 🥇 | 77% | 74% | 78% |
| **Knowledge Work** (GDPVal-AA) | 1,448 | **1,594** 🥇 | 1,508 | 1,192 |
| **Professional Work** (ProfBench Search) | **56%** 🥇 | 46% | 56% | 53% |
| **Long Context @ 1M** (RULER) | **95%** 🥇 | N/A (256K max) | N/A (256K max) | 90% |

### SWE-Bench Verified عبر harnesses مختلفة
**65% — 70.4%** عبر Pi / OpenHands / Hermes / OpenCode / Mini SWE Agent

⚠️ **ملاحظة مهمة:** الـ NVIDIA blog **لم يذكر GPQA Diamond تحديداً لـ Ultra**. ده غريب لكنه يدل على إن النموذج مُحسَّن لـ **agentic tasks** مش لـ knowledge benchmarks الكلاسيكية.

### الكفاءة (مقارنة بـ gpt-oss-120b وغيره)
- **5x أعلى throughput** من نماذج المنافسة في فئته
- **30% أرخص** في cost-to-task-completion على SWE-bench
- مدرّب بـ NVFP4 (أسرع 4x من FP8 على Blackwell)

---

## 🎯 إيه اللي يخص GENESIS تحديداً؟

### نقاط القوة الحقيقية لمشروعك

1. **🔥 Agent Orchestration = 91% PinchBench**
   GENESIS بالظبط agent orchestration framework: meta-agent + target agent + feedback agent + evolutionary discovery. Ultra **مُصمَّم خصيصاً** لهذا النوع من workflows.

2. **🔥 Instruction Following = 82% IFBench (الأعلى)**
   مشكلتنا في run_53 كانت أن النموذج بـ instruction following ضعيف:
   - مكتبش `q.get('Question')` صح
   - رد بـ `max_tokens=50` بدل ما يفكر
   - الـ feedback agent مكتشفش الـ bugs

   نموذج بـ 82% IFBench هيخفض احتمالية هذه الأخطاء بشكل كبير.

3. **🔥 1M context + 95% RULER**
   - يقدر يحمل **كل سرقاتك الـ 102** + كل الـ MASTER INDEX + كل القرارات السابقة في prompt واحد
   - الـ meta-agent يقدر يشوف **كل النموذج كحالة كاملة** بدل ما يشتغل بقطع
   - مفيد لـ AlphaEvolve loop: كل المجتمع (population) في context واحد

4. **🔥 Multi-step reasoning + planning**
   ده بالظبط اللي محتاجينه لـ Task 6 (Evolutionary Discovery) وTask 9 (real benchmarks).

5. **🔥 70.4% SWE-Bench Verified**
   لو هنشتغل على SWE-bench (zoals مخطط في Task 9)، ده **أعلى من gpt-oss-120b (62.4%)** بفارق 8 نقاط.

### نقاط الحذر

1. **مفيش GPQA score رسمي محدد لـ Ultra**
   NVIDIA ركّز على agent benchmarks. لازم نقيس بأنفسنا.

2. **Coding على Terminal-Bench فقط 54%**
   ده أقل من Kimi K2.6 (67%). للمهام الـ coding-heavy، Kimi ممكن يكون أحسن.

3. **Long-horizon planning 33%**
   أقل من GLM 5.1 (40%). يعني لو الـ task محتاج خطة لـ 50+ خطوة، GLM ممكن يكون أنسب.

4. **Free tier يُسجَّل**
   مش مشكلة لـ benchmarks public، بس لازم نوعى.

---

## 🛠️ التغييرات المقترحة في GENESIS

### تعديل 1: إضافة Nemotron 3 Ultra كـ option في run_openrouter_benchmark.py

```python
# في run_openrouter_benchmark.py
RECOMMENDED_MODELS = {
    "gpt-oss-120b-free": "openai/gpt-oss-120b:free",          # baseline قديم
    "nemotron-3-ultra-free": "nvidia/nemotron-3-ultra-550b-a55b:free",  # 🆕 الجديد
    "nemotron-3-ultra-paid": "nvidia/nemotron-3-ultra-550b-a55b",       # paid
    "nemotron-3-super-free": "nvidia/nemotron-3-super-120b-a12b:free",  # متوسط
    "deepseek-v4-flash-free": "deepseek/deepseek-v4-flash:free",        # للمقارنة
}
```

### تعديل 2: استخدام reasoning parameter في prompts الـ QA

```python
response = client.chat.completions.create(
    model="nvidia/nemotron-3-ultra-550b-a55b:free",
    messages=[...],
    max_tokens=4096,        # مش 50!
    temperature=0.0,
    extra_body={
        "reasoning": {"effort": "high"}   # ✅ Ultra يدعمها
    }
)
```

### تعديل 3: تشغيل pure baseline على Ultra الأول

عشان نعرف السقف الحقيقي للنموذج لوحده على GPQA Diamond:

```bash
# الاختبار السريع — 20 سؤال
python tools/gpqa_pure_baseline.py \
    --model "nvidia/nemotron-3-ultra-550b-a55b:free" \
    --questions_path genesis/tasks/gpqa/data/private/diamond_questions.json \
    --output_path results/pure_baseline_nemotron3_ultra_first20.json \
    --reasoning high \
    --max_tokens 8192 \
    --limit 20

# اختبار كامل لو الأول كويس
python tools/gpqa_pure_baseline.py \
    --model "nvidia/nemotron-3-ultra-550b-a55b:free" \
    --questions_path genesis/tasks/gpqa/data/private/diamond_questions.json \
    --output_path results/pure_baseline_nemotron3_ultra_full.json \
    --reasoning high \
    --max_tokens 8192 \
    --limit 0
```

---

## 📊 مقارنة سريعة: gpt-oss-120b vs Nemotron 3 Ultra

| الميزة | gpt-oss-120b | Nemotron 3 Ultra | المفضل لـ GENESIS |
|---|---|---|---|
| الحجم | 120B / 5.1B active | 550B / **55B active** | Ultra (قدرة أعلى) |
| Context | 131K | **1M** ✅ | Ultra |
| GPQA Diamond | **80.1%** (high) | غير معلن (متوقع 75-80%) | gpt-oss واضح |
| SWE-Bench Verified | 62.4% | **65-70.4%** | Ultra ✅ |
| Agent Productivity | غير معلن | **91%** PinchBench | Ultra ✅ |
| Instruction Following | متوسط | **82%** IFBench | Ultra ✅ |
| سعر input | $free / $0.075 (paid) | $0.50 (paid) / free | gpt-oss أرخص |
| سعر output | $free / $0.30 (paid) | $2.50 (paid) / free | gpt-oss أرخص |
| Free tier speed | بطيء جداً | متوسط (58 tok/s) | Ultra |

**التوصية لمشروعك:**
- **meta-agent + feedback-agent + evolutionary discovery → Nemotron 3 Ultra** (الـ agent orchestration نقطة قوته)
- **target-agent على knowledge tasks (GPQA) → جرّب الاتنين**

---

## 🧪 خطة اختبار مقترحة (مرتبة بالأولوية)

### الخطوة 1 (دلوقتي): Pure baseline لكل نموذج على 20 سؤال GPQA
يحدد لنا السقف الحقيقي لكل واحد:

```bash
# gpt-oss-120b — اللي بتشغله الآن
python tools/gpqa_pure_baseline.py --model openai/gpt-oss-120b:free \
    --questions_path genesis/tasks/gpqa/data/private/diamond_questions.json \
    --output_path results/pure_oss120b_20.json --reasoning high --limit 20

# Nemotron 3 Ultra — الجديد
python tools/gpqa_pure_baseline.py --model nvidia/nemotron-3-ultra-550b-a55b:free \
    --questions_path genesis/tasks/gpqa/data/private/diamond_questions.json \
    --output_path results/pure_nemotron3_20.json --reasoning high --limit 20
```

**نتيجة متوقعة:**
- gpt-oss-120b → ~70-80% (إن كان الـ free مش quantized بشدة)
- Nemotron 3 Ultra → ~75-85% (بحكم 91% PinchBench + 82% IFBench)

### الخطوة 2: لو الاتنين فوق 60%، شغل GENESIS عليهما
بعد ما نصلح الـ bug في target_agent (الـ case mismatch + max_tokens + CoT)، شغّل run_54 على Ultra:

```bash
python run_openrouter_benchmark.py \
    --task gpqa \
    --max_gen 2 \
    --run_id 54 \
    --use_evolutionary_discovery \
    --meta_model "nvidia/nemotron-3-ultra-550b-a55b:free" \
    --task_model "nvidia/nemotron-3-ultra-550b-a55b:free"
```

### الخطوة 3: لو النتائج >baseline pure، عندك أول evidence حقيقي على لfactor lift من GENESIS

---

## 🎁 سرقة شرعية مقترحة (5.91)

**العنوان:** استثمار 1M context window في AlphaEvolve population coherence

**ما نأخذه:**
- Nemotron 3 Ultra context window 1M يسمح للـ evolutionary discovery engine بـ:
  - حمل **كل المجتمع (population) كاملاً** في prompt واحد للـ meta-agent
  - تمرير **كل lineage history** للـ mutation operator
  - حفظ **كل research_memory** (97 entries حالياً) داخل context كل قرار

**ما لا نأخذه:**
- لا نلتزم بـ NVIDIA hardware (open weights متاحة)
- لا نخصص الكود لـ Mamba architecture
- لا نعتمد على NVIDIA NIM endpoint الحصري

**ما يصبح عندنا:**
- evolutionary_discovery_engine بقدرة "memory-rich mutation" — كل اقتراح variant يأخذ في الاعتبار كل التاريخ
- meta-agent يرى المشروع كاملاً (102 سرقة + كل الـ specs) في كل run
- لا حاجة لـ summarization lossy للـ history

**التطبيق:**
1. إضافة flag `--full_context_mode` في `run_openrouter_benchmark.py` يفعّل تمرير كل research_memory + lineage للـ prompt
2. شرط: model يدعم >=256K context (Ultra ✅، gpt-oss-120b ❌ بـ 131K)

---

## 🔗 المراجع

- [NVIDIA Developer Blog (الإعلان الرسمي)](https://developer.nvidia.com/blog/nvidia-nemotron-3-ultra-powers-faster-more-efficient-reasoning-for-long-running-agents/)
- [NVIDIA Technical Report PDF](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf)
- [OpenRouter Model Page](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b)
- [Hugging Face Weights (BF16)](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16)
- [NVIDIA NeMo RL](https://github.com/nvidia-nemo/rl) + [Gym](https://github.com/NVIDIA-NeMo/gym)

---

## ⚠️ تنبيهات هامة (للحفاظ على عمومية المشروع)

1. **لا نخصص أي كود لـ Nemotron**. أي إضافة لازم تكون عبر `--meta_model` و `--task_model` arguments فقط.
2. **الـ prompts تظل عامة**. القاعدة "حاول case variants" + "use chain-of-thought" تنفع أي نموذج، مش Nemotron بس.
3. **نقيس قبل ما نلتزم**. لو Nemotron طلع أقل من gpt-oss على GPQA، نرجع له. لو طلع أكثر، نضيفه كـ default للـ agent orchestration. مش نلتزم أعمى.
4. **Free tier للـ R&D فقط**. لو هنطلع paper جدي، نستخدم الـ paid endpoint للأرقام النهائية الموثقة.
