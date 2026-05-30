from __future__ import annotations

DEFAULT_GLOBAL_MAX_ACTIVE_CONCEPTS = 1
DEFAULT_MIN_OVERLAP = 2
DEFAULT_MIN_ACTIVATION_SCORE = 7

# Optional family-specific overrides.
# Keys: task_family -> {'max_active': int, 'min_score': int}
DEFAULT_FAMILY_SELECTIVITY = {
    'comparison': {'max_active': 1, 'min_score': 7},
    'synthesis': {'max_active': 1, 'min_score': 7},
    'procedure': {'max_active': 0, 'min_score': 99},
}
