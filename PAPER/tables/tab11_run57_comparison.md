# Table 11: First Post-Fix GENESIS Comparison (`run_57`)

| Metric | Pure baseline | GENESIS Gen 1 | GENESIS Gen 2 |
|---|---:|---:|---:|
| Accuracy % | **75.0** | 65.0 | 65.0 |
| Correct / 20 | **15** | 13 | 13 |
| Invalid | 0 | 0 | 0 |
| Physics % | 81.8 | **90.9** | **90.9** |
| Chemistry % | **66.7** | 16.7 | 33.3 |
| Biology % | **66.7** | **66.7** | 33.3 |
| Gap vs pure | — | -10.0 | -10.0 |

## Wrong question IDs

- **Pure baseline wrong:** Q2, Q7, Q11, Q16, Q18
- **GENESIS Gen 1 wrong:** Q2, Q9, Q11, Q13, Q16, Q18, Q19
- **GENESIS Gen 2 wrong:** Q8, Q9, Q11, Q13, Q16, Q18, Q19

## Interpretation

1. **GENESIS post-fix is clean but weaker than baseline.**
   - The architecture no longer crashes or produces invalid answers.
   - But it still loses **2 questions** relative to the pure baseline.

2. **Feedback changed the pattern, not the score.**
   - Gen 2 fixed **Q2**.
   - But Gen 2 regressed on **Q8**.
   - Net score stayed flat at **65.0%**.

3. **Physics remains strong, Chemistry remains the pain point.**
   - GENESIS actually beats the pure baseline on Physics (90.9 vs 81.8).
   - But the damage on Chemistry is severe enough to erase that gain.

## Immediate research question

Why does the architecture improve Physics while hurting Chemistry so much?

This is now the most useful ablation question for the next session.
