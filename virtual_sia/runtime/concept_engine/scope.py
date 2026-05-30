from __future__ import annotations

from ...core.objects.concept import ConceptCandidate


def draft_scope(candidate: ConceptCandidate) -> ConceptCandidate:
    if not candidate.candidate_scope.ambiguity_zone:
        candidate.candidate_scope.ambiguity_zone = ["near-domain tasks with mixed structure may require manual review"]
    return candidate
