# Figure 7: Error Attribution — Where the -44.70 Gap Came From

## The Waterfall: Official → Pure → Orchestrated

```
GPQA Diamond Accuracy (%)
  |
80 ┤ ████████████████████████████████████  80.1%  Official (NVIDIA model card, BF16, n=198)
   |
78 ┤
   |
76 ┤     ██████████████████████████████      75.0%  Pure Baseline (free-tier, n=20)
   |     │                                    ↓
74 ┤     │ −5.1: Free-tier quantization
   |     │       + sample size (n=20 vs 198)
72 ┤     │       + subset bias (55% Physics)
   |
70 ┤
   |
68 ┤
   |
66 ┤
   |
64 ┤     ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
   |     │ −44.7: FIVE SCAFFOLDING BUGS
62 ┤     │        │
   |     │   ┌────▼──────────────────────┐
60 ┤     │   │ Bug 1: Case mismatch      │  ~25-30 pts
   |     │   │ Bug 2: max_tokens=50      │  ~10-15 pts
58 ┤     │   │ Bug 3: Anti-CoT prompt    │  ~5-10 pts
   |     │   │ Bug 4: No reasoning fb    │  ~3-5 pts
56 ┤     │   │ Bug 5: Default to 'A'     │  masks failures
   |     │   └───────────────────────────┘
54 ┤     │
   |     │
52 ┤     │
   |
50 ┤
   |
48 ┤
   |
46 ┤
   |
44 ┤
   |
42 ┤
   |
40 ┤
   |
38 ┤
   |
36 ┤
   |
34 ┤
   |
32 ┤ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  30.3%  GENESIS run_53 (buggy)
   |
30 ┤

     █ = Model capability (80.1% → 75.0%)
     ▒ = Infrastructure losses (−44.7 from bugs)
     ░ = Measured buggy performance (30.3%)
```

## Error Type Taxonomy

| Error Category | Definition | Attribution | Example | Detection |
|---------------|-----------|-------------|---------|-----------|
| **Model Error** | Model lacks knowledge to answer | Model capability limit | Q2: model doesn't know Grignard reactions deeply enough | Per-question correctness analysis |
| **Scaffolding Error** | Infrastructure prevents model from answering correctly | Engineering bug | Q1 in run_53: empty question string sent to model | χ² test, prompt inspection, per-letter accuracy |
| **Parsing Error** | Valid answer produced but not extracted | Parser limitation | "ANSWER:A" not caught by 4-pattern parser | Invalid rate, regex coverage analysis |
| **Rate-Limit Error** | API returns error instead of answer | Infrastructure limit | 429 "free-models-per-day" | Pool statistics |
| **Sampling Error** | Subset composition biases results | Methodology limitation | 55% Physics in n=20 vs 43% in n=198 | Per-domain breakdown |

## How We Detected Each Bug

### Bug 1: JSON Case Mismatch (CRITICAL)
**Symptom:** χ² = 10.36 on prediction distribution (close to uniform random).  
**Detection:** Compared prediction distribution to χ² expected value for random guessing. Checked per-letter accuracy: most common correct letter (A, 57 questions) had lowest model accuracy (21%).  
**Root cause:** `q.get('question')` returns `None` when the JSON key is `'Question'`. The `or ''` creates empty prompt.  
**Fix:** `safe_get_question_field(q, 'Question', 'question', 'QUESTION', 'text', 'prompt')`

### Bug 2: Insufficient Token Budget (CRITICAL)
**Symptom:** 35% of responses had `finish_reason="length"` with `content=""`.  
**Detection:** Monitored API usage statistics; correlated `reasoning_tokens` with `content_chars`.  
**Root cause:** `max_tokens=50` (vs 16,384 needed for reasoning models).  
**Fix:** `max_tokens=16384` with guidance in meta-agent prompt.

### Bug 3: Anti-CoT Prompt (HIGH)
**Symptom:** Answers were present but shallow (no reasoning trace).  
**Detection:** Compared response quality (presence of step-by-step reasoning) between system prompts.  
**Root cause:** "Output ONLY the letter" suppresses chain-of-thought.  
**Fix:** System prompt allowing reasoning: "1. Reason step by step. 2. Eliminate wrong options. 3. End with ANSWER: X"

### Bug 4: Missing Reasoning Fallback (HIGH)
**Symptom:** 7/20 responses completely lost (no content, no parsing).  
**Detection:** Tracked `content=""` frequency; found 35% rate.  
**Root cause:** No fallback when `message.content` is empty but `message.reasoning_details` contains answer.  
**Fix:** `extract_response_text()` merges content + reasoning before parsing.

### Bug 5: Silent Invalid Default (MEDIUM)
**Symptom:** Invalid rate was 0% in run_53 — suspiciously perfect.  
**Detection:** Compared run_53 (0 invalid, 30.3% acc) to smoke_v1 (35% invalid, 60% acc).  
**Root cause:** Invalid answers defaulted to "A", masking the problem.  
**Fix:** Force-letter follow-up, mark truly unrecoverable as invalid.
