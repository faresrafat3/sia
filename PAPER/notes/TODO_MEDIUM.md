# 🟡 TODO — أولويات متوسطة

1. **[ABLATION]** Ablation study لـ GENESIS components
   - بدون evolutionary discovery
   - بدون feedback agent (Gen 1 فقط)
   - بدون pipeline (target agent مباشر)
   - بدون constitutional check
   - الهدف: معرفة أي component يساهم بكم

2. **[CROSS-MODEL]** Pure baseline لـ Gemma 4 31B
   - الأعلى official GPQA: 84.3%
   - لو أكدنا الـ score على free tier، هذا أفضل baseline

3. **[CROSS-MODEL]** Pure baseline لـ Nemotron 3 Ultra
   - Agent orchestration optimized
   - GPQA score غير منشور — نقيسه بأنفسنا

4. **[REASONING]** Controlled reasoning token experiment
   - Vary max_tokens: 1K, 2K, 4K, 8K, 16K, 32K
   - Measure accuracy at each level
   - هدف: تأكيد أو دحض reasoning saturation hypothesis

5. **[FIGURES]** إنتاج Figures الورقة النهائية
   - Pipeline architecture diagram (Mermaid)
   - Baseline vs GENESIS bar chart
   - Reasoning correlation scatter plot
   - Domain difficulty heatmap
   - Per-question performance matrix

6. **[REFERENCES]** تعبئة PAPER/references/ من الـ 102 سرقة
   - اختيار أهم 15-20 reference للورقة
   - كتابة summary لكل واحد: ماذا أخذنا + ماذا تركنا
