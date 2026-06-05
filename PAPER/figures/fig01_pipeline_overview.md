# Figure 1: GENESIS Orchestration Architecture

```mermaid
graph TB
    subgraph "GENESIS Orchestrator"
        MA[Meta-Agent<br/>Writes target_agent.py<br/>from task spec]
        TA[Target Agent<br/>Executes task using<br/>cognitive pipeline]
        FA[Feedback Agent<br/>Reads Gen N results<br/>→ improves for Gen N+1]
        ED[Evolutionary Discovery<br/>AlphaEvolve-style<br/>Population search]
        CE[Constitutional<br/>Evaluator]
        RM[Research<br/>Memory]
        SPIN[SPIN Semantic<br/>Gap Analysis]
    end

    subgraph "Virtual GENESIS Cognitive Pipeline"
        MEM[Memory OS<br/>InMemoryMemoryStore]
        CON[Concept Engine<br/>InMemoryConceptRegistry]
        THY[Theory Runtime<br/>InMemoryTheoryRegistry]
        TIER[Tier Decision<br/>tier_2 / tier_1 routing]
        ECON[Economy Control<br/>InMemoryLedgerStore]
    end

    subgraph "Task Environment"
        TASK[GPQA Diamond<br/>198 graduate-level<br/>science MCQs]
        EVAL[evaluate.py<br/>Per-domain scoring]
    end

    MA -->|"writes"| TA
    TA -->|"execution log<br/>+ results"| FA
    FA -->|"improved code"| TA
    TA --> MEM
    TA --> CON
    TA --> THY
    TA --> TIER
    TA --> ECON
    ED -.->|"variants"| TA
    CE -->|"quality check"| FA
    RM -->|"insights"| MA
    SPIN -->|"semantic gap"| FA
    TA -->|"answers"| EVAL
    TASK -->|"questions"| TA
    EVAL -->|"scores"| FA
```

**Caption:** Architecture of the GENESIS orchestration framework. The Meta-Agent generates a target_agent.py script from task specifications and reference examples. The Target Agent executes the task while interfacing with a cognitive pipeline (memory, concepts, theory, tier decision, economy control). The Feedback Agent reads execution logs and evaluation results, then produces an improved agent for the next generation. The optional Evolutionary Discovery module performs population search over agent variants (inspired by AlphaEvolve/FunSearch [T5.86]). Constitutional evaluation, research memory, and SPIN semantic gap analysis provide additional quality signals. The task environment shown is GPQA Diamond — a benchmark of 198 graduate-level multiple-choice science questions across Physics (86), Chemistry (93), and Biology (19).

## Key Design Decisions

1. **Pipeline as substrate, not replacement:** The cognitive pipeline provides guidance (tier decisions, theory predictions, memory) but the LLM makes the final answer decision. This avoids the pipeline becoming a bottleneck.

2. **Multi-generation refinement:** Generation 1 is written by the meta-agent from specifications. Each subsequent generation is an improvement by the feedback agent based on actual execution results.

3. **Evolutionary diversity:** Population search with lineage tracking and diversity weighting prevents convergence to a single strategy.

4. **Constitutional constraints:** A set of rules (code quality, safety, performance) that must pass for each generation. Violations are fed to the feedback agent for correction.
