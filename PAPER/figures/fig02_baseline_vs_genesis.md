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
   |
20 ┤                                                           ● 65.0%
   |                                                            (GENESIS post-fix
15 ┤                                                            run_57 gen1/gen2)
   |
   └────────────────────────────────────────────────────────────────────────────▶
      run_53    smoke_v1   smoke_v2   smoke_v2   pure         run_57
      (pre-fix)  (4pat)    (lfm)      (nano)     baseline     (post-fix)
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
                    │ After fixes        │  +34.7  (vs buggy run_53)
                    │ (commit 3a16a87)   │
                    └─────────┬─────────┘
                              │
                    GENESIS post-fix: 65.0%  ← recovered, but still below pure baseline
                              │
                    ┌─────────▼─────────┐
                    │ Residual arch gap  │  −10.0  (65.0 vs 75.0)
                    │                    │
                    └───────────────────┘
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
  80.1% ────────▶ 75.0% ────────────▶ 65.0%
  [NVIDIA]      [Our measurement]     [GENESIS run_57]
                     ↓                       ↓
              Gap: −5.1                Gap: −10.0
         (free-tier loss)        (current architecture overhead)
```

This framework isolates infrastructure losses (Official → Pure) from architecture impact (Pure → Orchestrated). Without it, one might incorrectly attribute the free-tier quantization gap (−5.1) to GENESIS, or worse, attribute the scaffolding gap (−44.7) to model limitations.

**The critical scientific conclusion now is precise:** GENESIS has eliminated the catastrophic scaffolding failure, but the current architecture still trails the pure baseline by 10 points on the same subset.
