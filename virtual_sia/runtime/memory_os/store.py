from __future__ import annotations

from typing import Dict

from ...core.objects.memory import MemoryUnit


class InMemoryMemoryStore:
    def __init__(self) -> None:
        self._items: Dict[str, MemoryUnit] = {}

    def store_memory(self, unit: MemoryUnit) -> MemoryUnit:
        self._items[unit.id] = unit
        return unit

    def get(self, memory_id: str) -> MemoryUnit | None:
        return self._items.get(memory_id)

    def all(self) -> list[MemoryUnit]:
        return list(self._items.values())
