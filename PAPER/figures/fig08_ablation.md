# Figure 8: Ablation Study Design — Isolating GENESIS Component Contributions

## Status: EXPERIMENTAL DESIGN — DATA PENDING

This figure describes the planned ablation study. Results will be filled after experiments complete.

## Hypothesized Component Contributions

```
Hypothesized accuracy impact of each GENESIS component (relative to pure baseline = 75.0%):

No orchestration (pure baseline)     ███████▌ 75.0%
                                     │
+ Meta-agent only (Gen 1 only)       ████████ ?  (+ pipeline scaffolding)
                                     │
+ Feedback agent (Gen 1→2)           ████████▌ ?  (+ refinement)
                                     │
+ Evolutionary discovery             █████████ ?  (+ population diversity)
                                     │
+ Constitutional evaluation          █████████ ?  (+ quality constraints)
                                     │
+ Research memory                    █████████▌ ? (+ cross-run learning)
                                     │
Full GENESIS (all components)        ██████████ ?  (TOTAL ARCHITECTURE IMPACT)
```

## Ablation Experiment Design

| Experiment | Components Active | Components Disabled | Hypothesis |
|-----------|-------------------|---------------------|------------|
| **A0** | None | All | Pure baseline = 75.0% |
| **A1** | Meta-agent only | Feedback, Evo, Constitutional, Memory | Pipeline scaffolding adds overhead without benefit? |
| **A2** | Meta + Feedback (1 generation) | Evo, Constitutional, Memory | Feedback refines code quality but not accuracy? |
| **A3** | Meta + Feedback (2 generations) | Evo, Constitutional, Memory | Multi-gen feedback improves or overfits? |
| **A4** | Meta + Feedback + Constitutional | Evo, Memory | Constitutional constraints filter bad agents? |
| **A5** | Full GENESIS (no Evo) | Evolutionary discovery | Evo is necessary for >baseline? |
| **A6** | Full GENESIS | None | Architecture ceiling? |

## Measurement Protocol

Each experiment runs on:
- **Model:** gpt-oss-120b:free (same as pure baseline)
- **Task:** GPQA Diamond, 20-question subset (same as all other runs)
- **Runs:** 2 repetitions per experiment (to measure variance)
- **Total experiments:** 7 × 2 = 14 runs
- **Estimated time:** ~14 × 40 min = ~9 hours (with parallel key pool)

## Expected Outcomes (Pre-Registered Hypotheses)

| Hypothesis | Prediction | If True | If False |
|-----------|-----------|---------|----------|
| H1: Scaffolding costs ~3-5 points | A1 ≈ 70-72% | Pipeline overhead is real but small | Pipeline is "free" computationally |
| H2: Feedback adds value | A3 > A1 | Self-improvement works | Feedback is cosmetic |
| H3: Evolution adds diversity value | A6 > A5 | Population search beats single trajectory | Random variants add noise |
| H4: Constitutional constrains quality | A4 > A2 | Rule-based filtering helps | Rules are too rigid |
| H5: Full architecture > baseline | A6 > 75.0% | **PROOF OF ARCHITECTURE VALUE** ✨ | Architecture is neutral/negative |

## Controlled Variables

- Same model (gpt-oss-120b:free)
- Same benchmark (GPQA Diamond Q1-Q20)
- Same max_tokens (16384), temperature (0.0), reasoning effort (high)
- Same 11-key OpenRouter pool
- Same `genesis/llm_helpers.py` for response parsing (post-fix)

## Statistical Power

- n=20 per run → ±10% margin of error (95% CI)
- To detect a +5-point architecture improvement, need ~10 runs per condition
- Our 2 reps per condition can detect ~+15-point effects
- For paper-level evidence, need 198-question full benchmark (±3.5% CI)