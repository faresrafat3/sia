# 🔴 TODO — أولويات حرجة

1. **[ABLATION]** تفسير فجوة `−10.0 points` بين `pure_final=75%` و `run_57=65%`
  - ✅ تم إنجاز question-by-question delta analysis
  - التالي: isolate likely causes عملياً
  - افصل بين pipeline overhead و feedback drift و constitutional pressure

2. **[PAPER]** تحديث PAPER.md بالكامل بنتيجة `run_57`
   - تحديث Abstract
   - تحديث Discussion
   - تحديث Conclusion
   - تحديث Figure 2 والجداول

3. **[DATA]** لا ننتقل لـ Full 198-question GPQA إلا بعد ما GENESIS يبقى competitive على 20Q subset
   - المطلوب أولاً: تقليل gap من −10 إلى 0 أو أفضل
   - بعدها فقط نطلع للـ 198

4. **[INFRA]** استلام وتفعيل Gemini × 11 keys
   - فارس قال هيحضرهم
   - 1,500 RPD/model → قفزة كبيرة في الـ daily capacity

5. **[INFRA]** استلام وتفعيل Groq × 11 keys  
   - فارس قال هيحضرهم
   - 315 tok/s → سرعة عالية للتجارب
