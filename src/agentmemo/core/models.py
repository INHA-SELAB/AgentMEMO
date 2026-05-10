"""Domain models for AgentMEMO memos.

Pure-Python; safe to import from both UI and server layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class MemoType(str, Enum):
    PLAN = "PLAN"
    RESEARCH = "RESEARCH"
    IMPLEMENT = "IMPLEMENT"
    REVIEW = "REVIEW"


class MemoState(str, Enum):
    """Lifecycle: agent creates → OPEN, starts → IN_PROGRESS, finishes → CLOSED."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass
class Memo:
    """A single memo. `id` is None until persisted by the repository."""

    header: str
    contents: str = ""
    type: MemoType = MemoType.PLAN
    state: MemoState = MemoState.OPEN
    id: int | None = None
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    def touch(self) -> None:
        self.updated_at = _now()
