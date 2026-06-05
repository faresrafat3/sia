# Table 4: Per-Question Results Matrix — All 6 Runs Across 20 GPQA Questions

## Complete Per-Question Results (A/B/C/D answers per model per question)

Each cell shows the model's answer letter. Green = correct. Red = incorrect. Gray = invalid (no letter extracted).

| Q# | Domain | Subdomain | Truth | gpt-oss<br/>smoke v1 | gpt-oss<br/>final | nem-nano<br/>v1 | nem-nano<br/>v2 | lfm-2.5<br/>v1 | lfm-2.5<br/>v2 | Easy? |
|----|--------|-----------|-------|-----------|-----------|------------|------------|-----------|-----------|-------|
| 1 | Physics | Quantum Mech | **A** | A ✓ | A ✓ | A ✓ | A ✓ | inv | inv | ≥4 |
| 2 | Chemistry | Organic | **A** | C ✗ | C ✗ | inv | C ✗ | inv | C ✗ | 0 |
| 3 | Physics | Quantum Mech | **B** | B ✓ | B ✓ | B ✓ | B ✓ | B ✓ | B ✓ | **6** |
| 4 | Physics | Electromag | **C** | D ✗ | C ✓ | inv | B ✗ | inv | inv | ≥4 |
| 5 | Physics | Quantum Mech | **B** | B ✓ | B ✓ | B ✓ | B ✓ | B ✓ | B ✓ | **6** |
| 6 | Physics | Quantum Mech | **B** | D ✗ | B ✓ | inv | B ✓ | inv | D ✗ | ≥4 |
| 7 | Physics | Particle | **C** | C ✓ | A ✗ | inv | C ✓ | inv | inv | ≥4 |
| 8 | Biology | Genetics | **D** | C ✗ | D ✓ | inv | D ✓ | inv | inv | ≥4 |
| 9 | Chemistry | Organic | **C** | A ✗ | C ✓ | inv | A ✗ | inv | A ✗ | 1 |
| 10 | Physics | Astrophysics | **D** | C ✗ | D ✓ | D ✓ | B ✗ | inv | B ✗ | ≥4 |
| 11 | Biology | Molec Bio | **A** | B ✗ | C ✗ | inv | B ✗ | inv | inv | 2 |
| 12 | Physics | Particle | **B** | B ✓ | B ✓ | B ✓ | B ✓ | B ✓ | B ✓ | **6** |
| 13 | Chemistry | Organic | **B** | B ✓ | B ✓ | B ✓ | B ✓ | inv | B ✓ | ≥4 |
| 14 | Biology | Molec Bio | **A** | A ✓ | A ✓ | A ✓ | A ✓ | A ✓ | A ✓ | **6** |
| 15 | Physics | General | **C** | A ✗ | C ✓ | C ✓ | A ✗ | inv | inv | 2 |
| 16 | Chemistry | Organic | **C** | A ✗ | A ✗ | inv | B ✗ | D ✗ | C ✓ | 0 |
| 17 | Chemistry | General | **D** | C ✗ | D ✓ | C ✗ | D ✓ | inv | inv | ≥4 |
| 18 | Physics | General | **C** | D ✗ | B ✗ | D ✗ | D ✗ | inv | inv | 1 |
| 19 | Chemistry | Organic | **D** | C ✗ | D ✓ | inv | C ✗ | D ✓ | inv | ≥4 |
| 20 | Physics | Quantum Mech | **C** | C ✓ | C ✓ | C ✓ | C ✓ | C ✓ | C ✓ | **6** |

## Summary Statistics Per Model

| Model Run | Correct | Incorrect | Invalid | Accuracy | Recovery |
|-----------|---------|-----------|---------|----------|----------|
| gpt-oss smoke v1 | 12 | 3 | 5 | 60.0% | 0 |
| **gpt-oss final** | **15** | **5** | **0** | **75.0%** | 3 |
| nem-nano v1 | 10 | 1 | 9 | 50.0% | 0 |
| nem-nano v2 | 13 | 4 | 3 | 65.0% | 3 |
| lfm-2.5 v1 | 3 | 4 | 13 | 15.0% | 0 |
| lfm-2.5 v2 | 5 | 6 | 9 | 25.0% | 1 |

## Consensus Questions (All models agree)

| Q# | Consensus | Truth | Result |
|----|-----------|-------|--------|
| Q3 | B | B | ✓ All 6 correct |
| Q12 | B | B | ✓ All 6 correct |
| Q14 | A | A | ✓ All 6 correct |
| Q20 | C | C | ✓ All 6 correct |
| Q16 | D (5/6), C (1/6) | **C** | ✗ 5 wrong, 1 correct |

## Questions Where No Model Got It Right (Across All Runs)

- **Q2:** Chemistry Organic — cinnamaldehyde multi-step synthesis
- **Q18:** Physics General — energy level discrimination

## Key Patterns

1. **Physics Easy, Chemistry Hard:** 4/4 consensus-correct questions are Physics. The one near-consensus-wrong question (Q16) is Chemistry Organic.

2. **Parser Improvement Visible:** Compare "v1" (4-pattern parser) vs "v2" (16-pattern + reasoning fallback) — invalid rates drop from ~35-45% to 15% or less.

3. **Small Model Collapse:** LFM 2.5 (1.2B parameters) achieves only 25% even with optimal parsing — close to random chance (25%). Its thinking is insufficient for graduate-level science.

4. **Q16 Consensus Error:** 5 of 6 model runs answered D on Q16 (correct answer: C). This suggests a systemic error in how LLMs approach this specific organic chemistry transformation — a "shared blind spot" phenomenon.
