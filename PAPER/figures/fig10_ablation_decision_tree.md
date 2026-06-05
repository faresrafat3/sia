# Figure 10: Ablation Decision Tree — How We Explain the Remaining 10-Point Gap

```mermaid
flowchart TD
    A[Observed result: Pure baseline = 75% / GENESIS run_57 = 65%] --> B{What is the dominant source of the remaining gap?}

    B --> C[Pipeline overhead / noisy context]
    B --> D[Feedback drift]
    B --> E[Constitutional optimization pressure]
    B --> F[Evolutionary discovery adds noise]
    B --> G[Domain-localized chemistry weakness]

    C --> C1[A3: remove or neutralize pipeline leverage]
    D --> D1[A4: remove feedback loop]
    D --> D2[A7: narrow feedback scope]
    E --> E1[A5: remove constitutional pressure]
    F --> F1[A6: remove evo]
    G --> G1[A8: chemistry-focused research ablation]

    C1 --> H{Score improves?}
    D1 --> I{Score improves?}
    D2 --> J{Score improves?}
    E1 --> K{Score improves?}
    F1 --> L{Score improves?}
    G1 --> M{Score improves?}

    H -->|Yes| H2[Pipeline currently dilutes signal]
    H -->|No| H3[Pipeline is not the primary culprit]

    I -->|Yes| I2[Feedback loop is net harmful]
    I -->|No| I3[Feedback is not the main cause]

    J -->|Yes| J2[Feedback scope is too broad]
    J -->|No| J3[Feedback problem is deeper than scope]

    K -->|Yes| K2[Constitutional pressure trades accuracy for code quality]
    K -->|No| K3[Constitutional rules are not the main issue]

    L -->|Yes| L2[Evolutionary discovery adds noise on small benchmarks]
    L -->|No| L3[Evolutionary discovery is neutral or helpful]

    M -->|Yes| M2[Architecture gap is domain-localized, mainly Chemistry]
    M -->|No| M3[Gap is not mainly chemistry-specific]

    H2 --> Z[Best revised GENESIS configuration]
    I2 --> Z
    J2 --> Z
    K2 --> Z
    L2 --> Z
    M2 --> Z
```

## Reading the figure

This tree encodes the next research phase:

- We already answered the question **"Was the old 30.3% result just broken scaffolding?"** → **Yes**.
- The new question is **"Where does the remaining −10.0 architecture gap come from?"**
- Each branch corresponds to a controlled ablation from `Table 13`.

## Key principle

We do **not** redesign the whole system at once.
We isolate one suspected source of loss at a time, then update the best known architecture only after a controlled score improvement.

That keeps the project scientific instead of drifting into uncontrolled product-style iteration.
