# 🔴 TODO — أولويات حرجة

1. **[CRITICAL EXPERIMENT]** تشغيل GENESIS post-fix (run_54)
   - النموذج: `openai/gpt-oss-120b:free`
   - المهمة: GPQA Diamond 20-question
   - الإعداد: `max_gen=2`, `--use_evolutionary_discovery`
   - الهدف: معرفة هل GENESIS > 75% pure baseline
   - المانع: OpenRouter daily quota exhausted
   - الحل: انتظار UTC midnight أو استخدام GitHub Models gpt-5

2. **[PAPER]** إكمال PAPER.md بعد نتيجة run_54
   - كتابة Abstract
   - كتابة Conclusion
   - تحديث Results section بالنتيجة الفعلية

3. **[DATA]** تشغيل Full 198-question GPQA
   - مطلوب: quota كافية (198 سؤال × multiple models)
   - Margin of error: ±3.5% بدل ±10%
   - يقضي على sample bias الـ current

4. **[INFRA]** استلام وتفعيل Gemini × 11 keys
   - فارس قال هيحضرهم
   - 1,500 RPD/model → قفزة كبيرة في الـ daily capacity

5. **[INFRA]** استلام وتفعيل Groq × 11 keys  
   - فارس قال هيحضرهم
   - 315 tok/s → سرعة عالية للتجارب
