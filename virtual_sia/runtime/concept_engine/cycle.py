from __future__ import annotations

from ...runtime.memory_os.store import InMemoryMemoryStore
from .proposer import promote_candidate, propose_concepts_from_groups
from .registry import InMemoryConceptRegistry
from .scope import draft_scope
from .selector import build_contrastive_groups


def run_concept_cycle(memory_store: InMemoryMemoryStore, registry: InMemoryConceptRegistry) -> dict:
    groups = build_contrastive_groups(memory_store.all())
    candidates = propose_concepts_from_groups(groups)
    promoted = []

    for candidate in candidates:
        candidate = draft_scope(candidate)
        registered_candidate = registry.add_candidate(candidate)
        if registered_candidate.recommendation == "validate_as_concept":
            concept = promote_candidate(registry, registered_candidate.id)
            if concept:
                promoted.append(concept)

    return {
        "group_count": len(groups),
        "candidate_count": len(candidates),
        "promoted_count": len({c.id for c in promoted}),
        "concept_ids": list({c.id for c in promoted}),
    }
