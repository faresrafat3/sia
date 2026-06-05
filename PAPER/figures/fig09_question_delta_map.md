# Figure 9: Question Delta Map — Where GENESIS Helps vs Hurts

Legend:
- `✓` correct
- `✗` incorrect
- columns compare **Pure baseline**, **GENESIS Gen 1**, **GENESIS Gen 2**

```
Q#   Domain      Pure   G1   G2   Delta pattern
────────────────────────────────────────────────────────────────────
Q1   Physics      ✓     ✓    ✓    stable win
Q2   Chemistry    ✗     ✗    ✓    feedback gain
Q3   Physics      ✓     ✓    ✓    stable win
Q4   Physics      ✓     ✓    ✓    stable win
Q5   Physics      ✓     ✓    ✓    stable win
Q6   Physics      ✓     ✓    ✓    stable win
Q7   Physics      ✗     ✓    ✓    architecture gain
Q8   Biology      ✓     ✓    ✗    feedback regression
Q9   Chemistry    ✓     ✗    ✗    architecture loss
Q10  Physics      ✓     ✓    ✓    stable win
Q11  Biology      ✗     ✗    ✗    persistent failure
Q12  Physics      ✓     ✓    ✓    stable win
Q13  Chemistry    ✓     ✗    ✗    architecture loss
Q14  Biology      ✓     ✓    ✓    stable win
Q15  Physics      ✓     ✓    ✓    stable win
Q16  Chemistry    ✗     ✗    ✗    persistent failure
Q17  Chemistry    ✓     ✓    ✓    stable win
Q18  Physics      ✗     ✗    ✗    persistent failure
Q19  Chemistry    ✓     ✗    ✗    architecture loss
Q20  Physics      ✓     ✓    ✓    stable win
```

## Visual grouping

### Stable wins (11)
`Q1 Q3 Q4 Q5 Q6 Q10 Q12 Q14 Q15 Q17 Q20`

### Architecture gains (GENESIS beats pure)
`Q7` (both gens), `Q2` (Gen 2 only)

### Architecture losses (pure beats GENESIS)
`Q9 Q13 Q19` (both gens), `Q8` (Gen 2 only)

### Persistent failures (nobody gets them)
`Q11 Q16 Q18`

## Domain signal

```
Physics    : mostly preserved, sometimes improved (Q7)
Chemistry  : the main source of net loss (Q9, Q13, Q19)
Biology    : unstable under feedback (Q8 regression, Q11 persistent fail)
```

## Interpretation

The GENESIS architecture is **not globally worse** across all questions.
It is:

- **neutral** on most easy questions,
- **occasionally helpful** on a small number of hard items,
- **systematically harmful** on a small cluster of chemistry questions,
- **unable to rescue** the hardest persistent failures.

This pattern strongly suggests that the architecture gap is **localized**, not universal — exactly the kind of result that motivates targeted ablation rather than broad redesign.
