# ❓ OPEN QUESTIONS — أسئلة مفتوحة نناقشها مع فارس

1. متى هتبعت Gemini × 11 keys؟
   - الأولوية: عالية (1,500 RPD يغيروا المعادلة)

2. متى هتبعت Groq × 11 keys؟
   - الأولوية: متوسطة (سرعة عالية)

3. هل نجرب GitHub Models gpt-5 على GPQA قبل GENESIS؟
   - الـ PAT شغال ومتاح
   - gpt-5 أعلى من gpt-oss، يمكن يوصل 85%+ pure baseline

4. إيه أول المواضيع التقيلة اللي عايز تفتحها؟
   - بعد ما الـ baseline يتأكد (run_54)
   - اقتراحاتي: SWE-bench integration, paper writing strategy, instant vs thinking

5. هل ننتظر UTC midnight للـ quota ولا نستخدم بديل؟
   - OpenRouter daily quota بيرجع منتصف الليل
   - GitHub Models gpt-5 متاح دلوقتي

6. إيه رأيك في شكل الورقة الحالي؟
   - الـ skeleton كامل بـ 11 قسم
   - Figures مرقمة + captions
   - كل النتائج موجودة
   - الـ Abstract و Conclusion محتاجين نتيجة run_54

7. هل فيه نموذج تاني عايز تفضله للتجارب؟
   - Gemma 4 31B عنده 84.3% official (الأعلى)
   - Nemotron 3 Ultra عنده agent orchestration تخصص
   - Qwen3 Coder للـ SWE-bench

8. ملفات المفاتيح — تبعتهم ازاي؟
   - كل مزود له env var pattern مختلف
   - Gemini: `GEMINI_API_KEY_<NAME>`
   - Groq: `GROQ_API_KEY_<NAME>`
   - اقتراح: ابعتهم بنفس تنسيق OpenRouter (كل واحد في سطر)
