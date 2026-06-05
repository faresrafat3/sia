# Figure 2: Baseline vs GENESIS — Evolution of Measured Performance

## Accuracy Timeline Across All Runs

```
Accuracy (%)
  |
80 ┤                                                                  ● 75.0%
   |                                                                   (pure
75 ┤                                                                   baseline
   |                                                                   final)
70 ┤
   |
65 ┤                                              ● 65.0%
   |                                               (nemotron-nano
60 ┤                    ● 60.0%                     smoke v2)
   |                     (gpt-oss
55 ┤                     smoke v1)
   |
50 ┤
   |
45 ┤
   |
40 ┤
   |
35 ┤     ● 30.3%
   |      (GENESIS run_53 —    ● 25.0%
30 ┤      buggy scaffolding)    (lfm-2.5 smoke v2)
   |
25 ┤
   |                                             ┌─────────────────────┐
20 ┤                                             │ GENESIS post-fix     │
   |                                             │ (run_54) — PENDING   │
15 ┤                                             │ Expected: ???        │
   |                                             └─────────────────────┘
   └─────────────────────────────────────────────────────────────────────▶
      run_53    smoke_v1   smoke_v2   smoke_v2   pure        run_54
      (pre-fix)  (4pat)    (lfm)      (nano)     baseline    (PENDING)
```

## The -44.70 Gap Decomposition

```
                    gpt-oss-120b Official: 80.1%
                              │
                    ┌─────────▼─────────┐
                    │ Free-tier gap:    │  −5.1  (quantization, sample)
                    │                    │
                    └─────────┬─────────┘
                              │
                    Pure Baseline: 75.0%   ← سقف النموذج لوحده
                              │
                    ┌─────────▼─────────┐
                    │ Scaffolding bugs: │  −44.7  (5 bugs, fixed in 3a16a87)
                    │                    │
                    └─────────┬─────────┘
                              │
                    GENESIS run_53: 30.3%  ← أداء كارثي (bugs)
                              │
                    ┌─────────▼─────────┐
                    │ After fixes        │  +???   (Critical Experiment)
                    │ (commit 3a16a87)   │
                    └─────────┬─────────┘
                              │
                    GENESIS post-fix: ???%  ← السؤال المفتوح
```

## The Five Bugs That Caused the Gap

| Bug | Points Lost | Mechanism | Detection Method |
|-----|------------|-----------|------------------|
| #1: Case mismatch | ~25-30 | Empty question → random guess | χ² test + prompt inspection |
| #2: max_tokens=50 | ~10-15 | No room for reasoning | finish_reason="length" |
| #3: "Output ONLY letter" | ~5-10 | Suppressed chain-of-thought | Response quality analysis |
| #4: No reasoning fallback | ~3-5 | Lost empty-content responses | content="" frequency |
| #5: Default to "A" | ~0 (masked) | Hidden invalid responses | Invalid rate tracking |
| **TOTAL** | **~44.7** | | |

## Three-Number Framework for Architecture Claims

```
   Official Score ────────▶ Pure Baseline ────────▶ Orchestrated Score
   (vendor card)           (model alone)            (model + architecture)
        ↓                       ↓                          ↓
    Reference               True Ceiling             Architecture Impact
        ↓                       ↓                          ↓
  80.1% ────────▶ 75.0% ────────────▶ ???%
  [NVIDIA]      [Our measurement]     [Critical Experiment]
                     ↓                       ↓
              Gap: −5.1                Gap: ???
         (free-tier loss)        (architecture value)
```

This framework isolates infrastructure losses (Official → Pure) from architecture impact (Pure → Orchestrated). Without it, one might incorrectly attribute the free-tier quantization gap (−5.1) to GENESIS, or worse, attribute the scaffolding gap (−44.7) to model limitations.

**The only gap that matters for our research question is the rightmost one (Pure → Orchestrated).**
