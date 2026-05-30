# Virtual SIA - Current Regime Status
# حالة النظام الحالي

> Document Type: Stabilization Package
> Status: Frozen Regime
> Date: 2026-05-31
> Phase: Option B - Stabilize and Package (from Decision Memo)

---

## 1. Frozen Defaults

The following configuration values are frozen as the current operating regime. Changes require new evaluation evidence.

### 1.1 Concept Engine Configuration

Source: `virtual_sia/runtime/concept_engine/config.py`

```python
DEFAULT_GLOBAL_MAX_ACTIVE_CONCEPTS = 1
DEFAULT_MIN_OVERLAP = 2
DEFAULT_MIN_ACTIVATION_SCORE = 7
```

### 1.2 Family-Specific Selectivity

```python
DEFAULT_FAMILY_SELECTIVITY = {
    'comparison': {'max_active': 1, 'min_score': 7},
    'synthesis': {'max_active': 1, 'min_score': 7},
    'procedure': {'max_active': 0, 'min_score': 99},
}

FAMILY_SELECTIVITY_STRATEGY = {
    'comparison': 'contract_heavy',
    'synthesis': 'semantic_balanced',
    'procedure': 'structural_only',
}
```

### 1.3 Rationale for Frozen Values

| Parameter | Value | Evidence |
|-----------|-------|----------|
| Global max_active | 1 | Selectivity ablation: top2 gives identical success (0.986) and activation_rate (0.653) as top1 |
| Min activation score | 7 | Score 6 and score 7 produce identical results on current concept set; 7 is more conservative for future growth |
| Comparison max_active | 1 | Family ablation: current_default already achieves maximum success |
| Synthesis max_active | 1 | synthesis_top2 override shows no improvement |
| Procedure max_active | 0 | procedure_top1 raises activation_rate (0.653 to 0.708) without improving success |
| Comparison strategy | contract_heavy | Contract alignment is the primary distinguishing signal for comparison tasks |
| Synthesis strategy | semantic_balanced | Broader token matching suits multi-source integration tasks |
| Procedure strategy | structural_only | Conservative - procedure concepts not yet proven beneficial |

---

## 2. Current Best Path

### 2.1 Optimal Operating Condition

**condition_c_combined** (concept-aware + economy-aware tier routing) is the current best operating path:

- Success rate: 0.986 (v3b_curriculum, 72 tasks)
- Average inference cost: 0.00068 per task
- Versus premium-always: +12.5pp success at 14.7x lower cost
- Versus baseline (retrieval-only): +19.4pp success at same cost order

### 2.2 Curriculum-Based Evaluation

The evaluation operates under a `TaskCase`-based curriculum model:

1. Tasks are organized by family (comparison, synthesis, procedure)
2. Each family has 4 difficulty levels in the curriculum
3. The warmup phase runs concept cycles on all curriculum tasks to build the concept registry
4. Post-warmup: 8 concepts + 4 theories available for activation
5. At inference time, concepts are selected per-family using the frozen selectivity configuration

### 2.3 Tier Routing Logic

The economy-aware tier router (condition_b / condition_c):
- Defaults to standard model (cost=0.001)
- Escalates to premium model (cost=0.010) when estimated difficulty exceeds threshold
- On v3b_curriculum: escalates 13 out of 72 tasks (18% escalation rate)
- Combined with concepts, escalation drops to 0 tasks (concepts handle the difficulty)

---

## 3. What Remains Open

### 3.1 Synthesis Top-2 Policy

**Status**: Tested, not clearly better.

- synthesis_top2 configuration allows 2 concepts for synthesis tasks
- Result: identical success (0.986) and identical activation rate (0.653)
- The second concept slot is never filled in practice (no competitive second candidate)
- **Decision**: Keep synthesis at max_active=1 until the concept set grows and a second candidate becomes viable

### 3.2 Procedure Concept Activation

**Status**: Currently disabled (max_active=0).

- procedure_top1 configuration increases activation_rate from 0.653 to 0.708
- No improvement in success rate
- Procedure tasks rely on structural workflow reuse rather than concept-guided reasoning
- **Decision**: Leave disabled until evidence shows concept activation improves procedure outcomes

### 3.3 Governance-to-Control Bridge

**Status**: Not yet implemented.

- The governance layer (theory runtime, anomaly detection) currently operates independently
- A bridge to control concept formation (e.g., governance can veto concept promotion) is architecturally planned
- **Decision**: Deferred to next cycle - requires design specification before implementation

### 3.4 V4 Classification Accuracy

**Status**: Known limitation.

- Top-1 match rate is 0.667 on v4's deliberately ambiguous tasks
- Top-2 match rate is 0.917, showing the ranker identifies the correct family within its top 2
- The 50% ambiguity rate means many tasks genuinely belong to multiple families
- **Decision**: Accept as a characteristic of the diagnostic slice. The top-2 performance is adequate for concept selection.

### 3.5 Cross-Family Concept Transfer

**Status**: Not yet explored.

- Currently each concept is scoped to exactly one family
- A concept like "Evidence Sufficiency Contrast" could potentially benefit both comparison and synthesis
- **Decision**: Deferred. Requires new eval slice that tests transfer scenarios.

---

## 4. Evidence Confidence Assessment

### 4.1 Thesis 1: Concept Formation Beats Retrieval-Only

| Dimension | Assessment |
|-----------|-----------|
| Signal strength | +19.4pp on primary slice (0.792 to 0.986) |
| Consistency | Positive across v2, v3, v3b, v3b_curriculum, v3c_curriculum |
| Cost parity | Yes - concept-aware runs at same cost as baseline (0.001/task) |
| Exceptions | v4 diagnostic shows no separation (expected - high ambiguity blocks activation) |
| Overall confidence | **Moderate-to-high** |

**Caveats**: The evaluation is simulated (deterministic contract checking rather than live LLM output). The concept set is small (8-11 concepts). The task families are limited to comparison/synthesis/procedure.

### 4.2 Thesis 2: Cognitive Economy Matches Premium

| Dimension | Assessment |
|-----------|-----------|
| Signal strength | Equal success at 4-6x lower cost across all slices |
| Consistency | Perfect across every evaluated slice |
| Combined effect | When paired with concepts: 14.7x cost reduction with +12.5pp improvement |
| Exceptions | None observed |
| Overall confidence | **High** |

**Caveats**: The cost model is simplified (two discrete tiers). Real-world API pricing may differ. The escalation heuristic has not been tested against streaming or latency-sensitive workloads.

---

## 5. Next Cycle Options

From the Decision Memo (Option B stabilization), the following cycles are available:

### 5.1 Concept Leverage Cycle

**Goal**: Increase the benefit derived from existing concepts.

- Explore cross-family concept transfer
- Test concept combinations (when max_active > 1 becomes relevant)
- Add concept confidence decay based on activation outcomes
- Estimated effort: Medium

### 5.2 Governance Control Cycle

**Goal**: Connect governance runtime to concept formation decisions.

- Implement governance veto on concept promotion
- Add anomaly-triggered concept re-evaluation
- Build the theory-to-concept feedback loop
- Estimated effort: High

### 5.3 Broader Domain Cycle

**Goal**: Validate findings beyond the current three families.

- Design v5 task set with new families (classification, extraction, generation)
- Test whether concept formation advantage transfers to unfamiliar domains
- Measure whether the economy advantage holds with larger task diversity
- Estimated effort: Medium-High

### 5.4 Live Model Validation Cycle

**Goal**: Move from simulated evaluation to live LLM-backed verification.

- Replace deterministic contract checking with actual LLM output evaluation
- Measure real latency and cost under API constraints
- Validate that simulated success rates correspond to real performance
- Estimated effort: High (requires API budget)

---

## 6. Regime Summary Table

| Category | Item | Value | Status |
|----------|------|-------|--------|
| Config | max_active_concepts | 1 | Frozen |
| Config | min_activation_score | 7 | Frozen |
| Config | min_overlap | 2 | Frozen |
| Config | comparison strategy | contract_heavy | Frozen |
| Config | synthesis strategy | semantic_balanced | Frozen |
| Config | procedure activation | disabled | Frozen |
| Eval | primary slice | v3b_curriculum (72 tasks) | Active |
| Eval | diagnostic slice | v4 (12 tasks) | Active |
| Eval | stress slice | v3c_curriculum (72 tasks) | Active |
| Result | best success | 0.986 (combined) | Verified |
| Result | best cost | 0.00068/task (combined) | Verified |
| Result | concept count post-warmup | 8 | Stable |
| Result | theory count post-warmup | 4 | Stable |
| Thesis | Thesis 1 confidence | Moderate-to-high | Documented |
| Thesis | Thesis 2 confidence | High | Documented |
| Open | synthesis top-2 | No benefit observed | Monitor |
| Open | procedure concepts | No benefit observed | Monitor |
| Open | governance bridge | Not implemented | Deferred |
| Open | cross-family transfer | Not explored | Deferred |

---

*End of Current Regime Status*
