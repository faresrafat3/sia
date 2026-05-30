from __future__ import annotations

from typing import Dict, List

from ...core.objects.ledger import LedgerEntry


class InMemoryLedgerStore:
    def __init__(self) -> None:
        self._entries: Dict[str, LedgerEntry] = {}

    def record_cognitive_spend(self, entry: LedgerEntry) -> LedgerEntry:
        self._entries[entry.id] = entry
        return entry

    def all(self) -> List[LedgerEntry]:
        return list(self._entries.values())
