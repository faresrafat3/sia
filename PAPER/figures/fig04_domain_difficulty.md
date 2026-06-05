# Figure 4: Domain × Difficulty Matrix

## Cross-Model Question Difficulty Classification (6 model runs across GPQA Q1-Q20)

Each question is classified by how many of 6 tested models (across multiple runs: gpt-oss-120b, nemotron-3-nano, lfm-2.5-thinking) answered it correctly:

| Classification | Models Correct | Count | % |
|---------------|----------------|-------|---|
| **Easy** | ≥4 of 6 models | 11 | 55% |
| **Medium** | 2-3 of 6 models | 3 | 15% |
| **Hard** | ≤1 of 6 models | 6 | 30% |

## Domain × Difficulty Matrix

```
                Easy (≥4/6)    Medium (2-3/6)    Hard (≤1/6)    TOTAL
─────────────────────────────────────────────────────────────────────
Physics           10 ★              0                1             11
Chemistry          1                0                5 █            6
Biology            0                3 ●              0              3
─────────────────────────────────────────────────────────────────────
TOTAL             11                3                6             20
```

```
Visual Heatmap (■ = more questions):

                 Easy       Medium      Hard
Physics    ■■■■■■■■■■                          ■
Chemistry      ■                          ■■■■■
Biology                    ■■■

★ = Physics is dramatically easier: 10/11 questions (91%) classified as Easy
█ = Chemistry Organic is dramatically harder: 5/6 questions (83%) classified as Hard
● = Biology is consistently medium difficulty across models
```

## Per-Domain Accuracy (gpt-oss-120b final baseline)

```
Physics:    9/11  (81.8%)  ████████████████████░░░░  81.8%
Chemistry:  4/6   (66.7%)  ████████████████░░░░░░░░  66.7%
Biology:    2/3   (66.7%)  ████████████████░░░░░░░░  66.7%
─────────────────────────────────────────────────────
Overall:   15/20  (75.0%)  ██████████████████░░░░░░  75.0%
```

## Individual Hard Questions (Chemistry Organic — where all models struggle)

| Q# | Topic | Models Correct | Notes |
|----|-------|---------------|-------|
| Q2 | Cinnamaldehyde + Grignard + sulfur ylide | 0/6 | Multi-step reaction: 4+ transformations |
| Q9 | Organic Chemistry | 1/6 | Requires specific reaction mechanism knowledge |
| Q13 | Organic Chemistry | 1/6 | Stereochemistry determination |
| Q16 | Organic Chemistry | 0/6 | **ALL models agreed on wrong answer D (truth: C)** |
| Q18 | General Physics | 1/6 | Quantum state energy level discrimination |
| Q19 | Organic Chemistry | 1/6 | Multi-step synthesis with protecting groups |

## Consensus Analysis (Q16 — Shared Erroneous Prior)

All 6 model runs answered Q16 as "D", while the correct answer is "C".
This suggests a **shared erroneous prior** across models about a specific organic chemistry transformation.
The phenomenon warrants further investigation: are models learning the same incorrect patterns
from shared training data, or is there a genuine ambiguity in the question?

## Implications

1. **Benchmark composition matters:** Our 20-question subset is 55% Physics but the full GPQA Diamond is 43% Physics and 47% Chemistry. Accuracy on the full set will likely be LOWER than our 75% due to more Chemistry questions.

2. **Domain-specific architecture tuning:** GENESIS could potentially route Chemistry questions through a different reasoning strategy (e.g., step-by-step reaction mechanism verification) than Physics questions (equation-based reasoning).

3. **Sample size warning:** With only 20 questions and such strong domain asymmetry, per-domain sub-scores have large margins of error (Physics ±12%, Chemistry ±20%, Biology ±28% at 95% CI).
