# سرقة شرعية: LEAP (LLM-in-Lean Environment Agentic Prover) من Google DeepMind + Google Cloud AI
## GENESIS DeepMind Science Thefts — Cycle 7 (Agentic Decomposition + DAG Memoization + LLM-Guided Search)

> **المصدر الرئيسي**:
> - LEAP paper: arXiv 2606.03303 (Jun 2026, v2)
> - الكود: github.com/google-deepmind/superhuman/tree/main/leap
> - الـ benchmark الجديد: Lean-IMO-Bench (imobench.github.io)
> - المؤلفون: Po-Nien Kung, Linfeng Song, Dawsen Hwang, Jinsung Yoon, Chun-Liang Li, Simone Severini, Mirek Olšák, Edward Lockhart, Quoc V Le, Burak Gokturk, Thang Luong, Tomas Pfister, Nanyun Peng
> - الجهة: Google Cloud AI Research + Google DeepMind

**تاريخ السرقة**: 2026-06-05
**الحالة المقترحة**: 🟢 (مبدأ + خطة دمج كاملة في الـ orchestrator والـ concept engine والـ improvement plane)
**الأولوية**: 🔴 حرجة جداً (تجيب على RQ2 الأساسي بتاع الورقة من زاوية خارجية: orchestration **يقدر** يضيف +100 نقطة على نفس النموذج، لو اتعمل صح)
**ربط الأفكار**: [Idea-001] (المصدر من فارس) + [Idea-002] (Attribution Rule)

---

## 1. الفكرة الأساسية (ما هي القوة الكامنة؟)

LEAP هو **agentic framework لإثبات المبرهنات الرياضية الرسمية في Lean** يستخدم **general-purpose LLMs فقط** (Gemini-3.1-Pro)، بدون أي specialized prover model، ويحقق state-of-the-art:

- **Putnam 2025**: من 0% (direct LLM) إلى **100% (12/12)** — تخطّى Aristotle (gold IMO medal system, 75%) و Hilbert (33.3%).
- **Lean-IMO-Bench Basic**: من 20% إلى **83.3%**.
- **Lean-IMO-Bench Advanced**: من 3.3% إلى **56.7%**.

**القوة الحقيقية (الدليل التجريبي الصارم):**

1. **Architecture impact = +100 نقطة** على نفس class of base model.
2. **Specialized models لا تستفيد من iteration** (Goedel-V2-32B: 10% → 6.6%).
3. **General models تستفيد بشكل دراماتيكي** (Gemini-3.1-Pro: 20% → 36.6% في iteration وحدها، 20% → 83.3% بكامل LEAP).
4. **DAG memoization** يضيف +10 نقاط على Basic، +17 على Advanced.
5. **LLM Reviewer** هو الفرق بين الفشل والنجاح على الأسئلة الصعبة (Putnam A5: بدون reviewer = فشل بعد 8 rollouts، مع reviewer = نجاح في 2).

**ده بالظبط اللي يجيب على السؤال المركزي بتاع GENESIS:**

> "هل architecture بتضيف قيمة فوق pure baseline؟"

LEAP يجيب: **نعم، بمقدار +100 نقطة، تحت شروط معمارية محددة**. هذه الشروط هي بالظبط اللي إحنا محتاجين نقتبسها.

---

## 2. السرقة الشرعية (ما أخذناه / ما تركناه / ما أصبح عندنا)

### ما أخذناه (الجوهر القابل للتشغيل):

1. **Workflow-Inspired Agentic Design (Blueprint → Sketch → Verify):**
   - Decomposition هرمي للأهداف (mathematician's workflow).
   - High-level informal blueprint قبل low-level formal code.
   - Iterative compiler feedback (في حالتنا: evaluator feedback).

2. **AND-OR DAG Memoization:**
   - **OR nodes** = goals (أي proof يصلح).
   - **AND nodes** = decompositions (نجاحها يتطلب كل sub-goals).
   - **Lemma reuse** عبر branches → reduces redundancy.
   - **Anticipatory lemma planning** = lemmas مقترحة قد لا تكون مطلوبة الآن لكن تفيد لاحقاً.

3. **Interleaved Informal-Formal Planning:**
   - LLM يكتب informal reasoning أولاً (planning space).
   - ثم يترجم لـ formal code.
   - الـ informal sketch يحمي من brittleness بتاع direct code generation.

4. **Verification-Guided Proof Search (مستويين):**
   - **مستوى 1 — Deterministic verifier** (Lean compiler): syntactic + type-correctness.
   - **مستوى 2 — LLM Reviewer**: هل الـ decomposition useful فعلاً؟ هل تبسّط المشكلة؟ هل تتجنب trivial restatement؟

5. **Search Filter بـ LLM Heuristic:**
   - الـ LLM reviewer يرفض weak decompositions مبكراً.
   - يقلل redundant search على branches غير مثمرة.

6. **State Reader / State Writer pattern:**
   - State Reader: يجمع الـ goal + dependencies + related lemmas قبل الـ attempt.
   - State Writer: يتحقق من الـ acyclicity قبل commit إلى الـ DAG.

7. **Hybrid potential (مذكور في discussion):**
   - General model للـ high-level structural reasoning.
   - Specialized model للـ focused formal step generation.
   - LEAP أثبت إن general-only يكفي، لكنه فتح الباب للهجين.

### ما تركناه عمداً (عشان يتوافق مع قفلنا الداخلي):

1. **التركيز على Lean فقط:**
   - LEAP مخصص لـ formal mathematics في Lean.
   - عندنا GPQA = informal scientific reasoning (Physics/Chem/Bio MCQ).
   - **التكييف:** الـ workflow يبقى لكن "Lean compiler" يتحول إلى "task-specific verifier" (وقد لا يكون deterministic).

2. **الـ Lean Blueprint tool dependency:**
   - LEAP يستخدم أدوات Lean المتخصصة.
   - عندنا لا proof obligations رسمية — عندنا questions.
   - **التكييف:** Blueprint = "informal reasoning plan" قبل answer.

3. **الـ DFS البسيط للـ DAG:**
   - LEAP يستخدم DFS فقط حالياً.
   - عندنا فرصة لـ smarter search (مثل beam search مع cognitive economy gating).

4. **الـ "general LLM is sufficient" claim بشكل مطلق:**
   - LEAP يثبت ده على formal math.
   - عندنا تحتاج تحقق منفصل على scientific reasoning.
   - **التكييف:** نأخذ المنهج، لكن نوسّع بـ hybrid حسب الـ task.

5. **انعدام الـ cognitive economy:**
   - LEAP يصرف 71 إلى 3,000 LLM call لكل problem (A5 = 3k!).
   - عندنا budget محدود.
   - **التكييف:** نضيف tier-aware search budget (يرتبط بـ `GENESIS_Cognitive_Economy_Theory_AR.md`).

6. **التركيز على pass@1 / iterative بدون population diversity:**
   - LEAP يحاول واحد في كل مرة مع backtracking.
   - AlphaEvolve [T5.86] يعمل population search.
   - **التكييف:** الدمج بين الاتنين = LEAP DAG + AlphaEvolve population على المستوى الأعلى.

### ما أصبح عندنا (التحويل العملي في GENESIS):

#### 7.1 — في الـ Orchestrator (genesis/orchestrator.py)

**التغيير الأكبر:** بدل ما الـ meta-agent يكتب target_agent.py واحد monolithic، يبني **AND-OR DAG of sub-tasks**:

```python
# pseudo-code للـ orchestrator الجديد
def orchestrate_with_dag(task):
    root_goal = OR_node(task)
    dag = AND_OR_DAG(root=root_goal)

    while dag.has_open_goals():
        goal = dag.next_open_goal()  # DFS or tier-aware

        # Direct attempt first
        informal = llm.reason_informally(goal, dag.context(goal))
        formal_attempt = llm.translate_to_executable(informal)
        if verifier.check(formal_attempt):
            dag.mark_proved(goal, formal_attempt)
            continue

        # Decomposition
        blueprint = llm.draft_blueprint(goal)
        if not llm_reviewer.is_useful_decomposition(blueprint, goal):
            dag.mark_dead_end(goal)
            continue

        sub_goals = llm.extract_sub_goals(blueprint)
        sketch = llm.write_sketch_with_sorries(blueprint, sub_goals)
        if verifier.check(sketch):
            and_node = AND_node(parent=goal, sketch=sketch)
            for sg in sub_goals:
                dag.add_OR(sg, parent=and_node)

    return dag.assemble_full_proof(root_goal)
```

#### 7.2 — في الـ Concept Engine (virtual_genesis/runtime/concept_engine/)

**ربط جوهري:** الـ "anticipatory lemma planning" بتاع LEAP **يطابق بشكل مذهل** فكرة الـ Concept Formation Engine بتاعنا:

- LEAP: lemmas تُقترح بشكل proactive لاحتمال إعادة استخدامها لاحقاً.
- GENESIS: concepts تتشكّل بشكل proactive عبر `propose_concepts_from_groups`.

**التحديث المقترح:**
- إضافة `anticipatory_proposer` mode في الـ Concept Engine.
- الـ Concept يصبح memoized lemma على مستوى التفكير العلمي.
- ربط مباشر بـ `GENESIS_Concept_Formation_Engine_Spec_AR.md` (re-read in light of LEAP).

#### 7.3 — في الـ Theory Runtime (virtual_genesis/runtime/theory_runtime/)

**التحديث المقترح:**
- الـ theory يلعب دور "LLM Reviewer" داخلي.
- قبل ما الـ orchestrator يـ commit decomposition جديدة، الـ theory_registry يحكم: هل ده يطابق الـ existing theories؟ هل ده يبسّط الـ task فعلاً؟
- ده يحول الـ theory layer من passive (predicts) لـ active (gates decisions).

#### 7.4 — في الـ Memory OS (virtual_genesis/runtime/memory_os/)

**الـ DAG memoization** = upgrade لـ MemoryStore:

- بدل flat memory entries، نخزن DAG of dependency relationships.
- "Anticipatory lemmas" = memory items not currently needed but stored for future reuse.
- Hierarchical retrieval: لما task جديد يجي، نشوف هل في memoized sub-task مشابه.

#### 7.5 — في الـ Verification (genesis/llm_helpers.py + extensions)

**Two-level verification:**

- **Level 1 (Deterministic):** existing `extract_letter()` + `extract_response_text()` + format checks.
- **Level 2 (LLM Reviewer):** **جديد** — قبل قبول أي generated answer/code، LLM reviewer يحكم:
  - هل الإجابة معقولة في سياق السؤال؟
  - هل الـ reasoning chain منطقية؟
  - هل في trivial restatement؟ (LEAP اكتشف ده ablation بتاعهم)

#### 7.6 — في الـ Improvement Plane (Replay Research Lab)

دمج LEAP + AlphaEvolve [T5.86]:
- LEAP DAG على مستوى single task → decomposition عميقة.
- AlphaEvolve population على المستوى الأعلى → diversity of strategies.
- النتيجة: "Evolutionary DAG Search Engine".

#### 7.7 — Hybrid Architecture للـ Future

LEAP يلمّح في §5.4 لـ hybrid: general model + specialized model.
عندنا فرصة لـ:
- general model = orchestrator + reviewer.
- specialized fine-tune لـ specific domains (Chemistry Organic مثلاً، أضعف domain عندنا).

---

## 3. الدمج العملي (نقاط التنفيذ المحددة)

### المرحلة 1 (فورية — paper-impact):

**3.1.1 — Theoretical Integration في الورقة (لا runs مطلوبة):**

- **Section 8.5 جديد:** "Why GENESIS loses 10 points while LEAP gains 100 — a structural comparison"
- **Table 16 جديد:** LEAP vs GENESIS architecture impact comparison.
- **Figure 11 جديد:** The 110-point gap visualization.

**3.1.2 — Theory papers جديدة في `PAPER/theory/`:**

- `07_pipeline_as_memory_vs_decision_injection.md`
- `08_feedback_value_determinism_scope.md`
- `09_anticipatory_concepts_vs_anticipatory_lemmas.md`

**3.1.3 — Philosophy paper جديد في `PAPER/philosophy/`:**

- `07_meaning_of_general_purpose_sufficiency.md`

### المرحلة 2 (متوسطة — يتطلب runs لاحقاً):

**3.2.1 — Orchestrator Refactor:**
- إضافة `dag_mode` flag في `genesis/orchestrator.py`.
- بدل monolithic target_agent → DAG of sub-task agents.
- ablation A9 جديد: GENESIS-DAG vs GENESIS-flat.

**3.2.2 — LLM Reviewer Integration:**
- إضافة `llm_reviewer` step بعد كل generation.
- قبل commit إلى الـ memory/answer، reviewer يحكم.
- ablation A10: with/without reviewer.

**3.2.3 — Anticipatory Concept Proposer:**
- في `virtual_genesis/runtime/concept_engine/proposer.py`:
- إضافة `anticipatory_mode` ينشئ concepts قد تفيد tasks مستقبلية.

### المرحلة 3 (طويلة — research direction):

**3.3.1 — Domain-Aware DAG:**
- DAG decomposition strategies مختلفة حسب الـ domain.
- Chemistry Organic decomposition ≠ Physics decomposition.
- ربط بـ `GENESIS_Domain_Asymmetry_Theory` (Theory-04).

**3.3.2 — Hybrid Architecture Pilot:**
- General model للـ orchestration.
- Specialized fine-tuned model للـ Chemistry Organic بالذات.
- اختبار: هل يقفل الـ −10 gap عندنا؟

---

## 4. الـ Connections مع السرقات السابقة (interlocking thefts)

LEAP يتشابك بقوة مع سرقاتنا الموجودة:

### مع T5.86 (AlphaEvolve / FunSearch):
- **Common ground:** LLM + Evaluator closed loop.
- **الفرق:** AlphaEvolve = population evolution. LEAP = single-thread DAG decomposition.
- **التكامل:** Population of DAGs > single DAG > population of monolithic agents.

### مع T5.85 (Aletheia):
- **Common ground:** Generate-Verify-Revise loop.
- **الفرق:** Aletheia = proof-driven feedback. LEAP = DAG-structured proof state.
- **التكامل:** Aletheia's verify-revise يصبح node-level داخل LEAP's DAG.

### مع T5.84 (Co-Scientist):
- **Common ground:** Multi-agent reasoning.
- **الفرق:** Co-Scientist = specialized agent roles. LEAP = single agent + DAG memory.
- **التكامل:** Co-Scientist roles can populate different DAG layers.

### مع GRASP (سرقة سابقة):
- **Common ground:** Hard acceptance gates.
- **التكامل:** LEAP's LLM Reviewer + Lean compiler = double gate (LLM + deterministic).

### مع ExpGraph (سرقة سابقة):
- **Common ground:** Graph-structured memory.
- **التكامل:** LEAP's AND-OR DAG = special case of ExpGraph's general-purpose graph.

### مع Reflexion (T5.5) و Self-Refine (T5.6) و STaR (T5.7):
- **Common ground:** Iterative refinement.
- **التكامل:** LEAP يعمم refinement من single-trajectory إلى DAG of trajectories.

---

## 5. الأرقام المرجعية (للورقة)

### LEAP performance baseline (للاقتباس في الورقة):

| Benchmark | Direct LLM | Hilbert | Aristotle (Gold IMO) | LEAP | Δ vs Direct |
|---|---|---|---|---|---|
| Putnam 2025 | 0% | 33.3% | 75% | **100%** | **+100** |
| Lean-IMO Basic | 20% | 36.6% | 76.7% | **83.3%** | **+63.3** |
| Lean-IMO Advanced | 3.3% | 6.6% | 20% | **56.7%** | **+53.4** |

### LEAP ablation results (للورقة):

| Component | Impact |
|---|---|
| Iteration (Gemini-3.1-Pro) | 20% → 36.6% (+16.6) |
| Iteration (Goedel-V2-32B specialized) | 10% → 6.6% (**-3.4**) |
| DAG vs Tree (Basic) | 73.3% → 83.3% (+10) |
| DAG vs Tree (Advanced) | 40.0% → 56.7% (+16.7) |
| With vs Without LLM Reviewer (Putnam A5) | Failure → Success in 2 rollouts |

### Cost figures (للـ Future Work section):

LEAP يستهلك بين 71 و 3,000 LLM call لكل problem.
هذا **يبرر** integration الـ Cognitive Economy theory بتاعنا لأي adoption.

---

## 6. الأسئلة البحثية الجديدة اللي LEAP فتحها لنا

1. **Q-LEAP-1:** هل GENESIS gap (-10) يقفل لو طبقنا DAG memoization بشكل صحيح؟
2. **Q-LEAP-2:** هل الـ LLM Reviewer يحل feedback drift اللي شفناه (Gen 2 من 70 → 60 في A3)؟
3. **Q-LEAP-3:** هل الـ "general LLM is sufficient" claim يتعمم على scientific reasoning غير formal math؟
4. **Q-LEAP-4:** هل الـ anticipatory lemma planning يحسن الـ Chemistry Organic gap (5/6 hard)؟
5. **Q-LEAP-5:** هل دمج LEAP DAG مع AlphaEvolve [T5.86] population يعطي superlinear gain؟

كل سؤال من دول هو **section كامل** ممكن في الورقة، أو نظرية كاملة، أو ablation منفصل.

---

## 7. ربط بالـ Strategic Plan

- ✅ يدعم **Task 6** (AlphaEvolve integration) بقاعدة معمارية أقوى.
- ✅ يدعم **Task 9** (real benchmarks) بمثال خارجي قوي على ما يمكن تحقيقه.
- 🆕 يفتح **Task 10 محتمل**: DAG-based decomposition pilot.
- 🆕 يفتح **Task 11 محتمل**: LLM Reviewer integration.

---

## 8. الحالة في الـ Master Index

**المقترح:** إضافة هذه السرقة كـ **T5.92** في `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md`.

**التصنيف:**
- **Family:** DeepMind Agentic Frameworks (alongside T5.84 Co-Scientist, T5.85 Aletheia, T5.86 AlphaEvolve).
- **Category:** Orchestration + DAG Memoization + LLM-Guided Search.
- **Status:** 🟢 خطة دمج كاملة جاهزة.
- **Priority:** 🔴 حرجة.

---

## 9. Acknowledgments

**المصدر الأصلي للفكرة:** فارس، [Idea-001].
**نص فارس الأصلي:** "Link – arxiv. org/abs/2606.03303 Title: 'LEAP: Supercharging LLMs for Formal Mathematics with Agentic Frameworks'"

**النسب الإبداعي:** هذه السرقة بحد ذاتها هي [Idea-001] في الـ Ideas Bank بتاعنا. القاعدة الإبداعية ([Idea-002]) تنطبق هنا: كل ما يُبنى على هذه السرقة في الورقة النهائية يُنسب إلى Idea-001.

---

## 10. الخطوة التالية الفورية

بعد إنشاء هذا الملف:

1. ✅ تحديث `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md` بإضافة T5.92.
2. ⏳ كتابة Theory-07, Theory-08, Theory-09 في `PAPER/theory/`.
3. ⏳ كتابة Phil-07 في `PAPER/philosophy/`.
4. ⏳ كتابة Section 8.5 + Table 16 + Figure 11 في `PAPER.md`.
5. ⏳ تحديث `ATTRIBUTION_MAP.md` بـ links فعلية بدل "مخطط".

**القرار:** الخطوات 1-4 يمكن البدء بها فوراً (theoretical only، لا runs). الخطوة 5 تتم بالتوازي مع كل إضافة.
