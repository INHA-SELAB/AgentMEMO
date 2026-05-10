"""SQLite-backed repository for memos.

Single source of truth shared by UI and (future) MCP server. WAL mode is
enabled so multiple readers/writers (GUI + server processes) can coexist
without blocking.
"""

from __future__ import annotations

import os
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

from agentmemo.core.models import Memo, MemoState, MemoType

SCHEMA = """
CREATE TABLE IF NOT EXISTS memos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    type        TEXT NOT NULL,
    state       TEXT NOT NULL,
    header      TEXT NOT NULL,
    contents    TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_memos_state      ON memos(state);
CREATE INDEX IF NOT EXISTS idx_memos_type       ON memos(type);
CREATE INDEX IF NOT EXISTS idx_memos_updated_at ON memos(updated_at DESC);
"""


def default_db_path() -> Path:
    """Resolve the default DB path (env override > ./data/agentmemo.db)."""
    env = os.environ.get("AGENTMEMO_DB_PATH")
    if env:
        return Path(env).expanduser().resolve()
    return Path.cwd() / "data" / "agentmemo.db"


class MemoRepository:
    """Thread-safe SQLite repository.

    Uses one connection per thread (sqlite3 default safety). WAL mode lets the
    UI and the MCP server run in separate processes against the same file.
    """

    def __init__(self, db_path: Path | str | None = None):
        self._db_path = Path(db_path) if db_path else default_db_path()
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")

    @property
    def db_path(self) -> Path:
        return self._db_path

    # ------------------------------------------------------------------ utils

    def _connect(self) -> sqlite3.Connection:
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self._db_path, isolation_level=None)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON")
            self._local.conn = conn
        return conn

    @staticmethod
    def _row_to_memo(row: sqlite3.Row) -> Memo:
        return Memo(
            id=row["id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            type=MemoType(row["type"]),
            state=MemoState(row["state"]),
            header=row["header"],
            contents=row["contents"],
        )

    # ------------------------------------------------------------------- CRUD

    def create(self, memo: Memo) -> Memo:
        cur = self._connect().execute(
            """
            INSERT INTO memos (created_at, updated_at, type, state, header, contents)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                memo.created_at.isoformat(),
                memo.updated_at.isoformat(),
                memo.type.value,
                memo.state.value,
                memo.header,
                memo.contents,
            ),
        )
        memo.id = cur.lastrowid
        return memo

    def get(self, memo_id: int) -> Memo | None:
        row = self._connect().execute(
            "SELECT * FROM memos WHERE id = ?", (memo_id,)
        ).fetchone()
        return self._row_to_memo(row) if row else None

    def update(self, memo: Memo) -> Memo:
        if memo.id is None:
            raise ValueError("Cannot update a memo without an id")
        memo.touch()
        self._connect().execute(
            """
            UPDATE memos
               SET updated_at = ?, type = ?, state = ?, header = ?, contents = ?
             WHERE id = ?
            """,
            (
                memo.updated_at.isoformat(),
                memo.type.value,
                memo.state.value,
                memo.header,
                memo.contents,
                memo.id,
            ),
        )
        return memo

    def delete(self, memo_id: int) -> bool:
        cur = self._connect().execute("DELETE FROM memos WHERE id = ?", (memo_id,))
        return cur.rowcount > 0

    # ----------------------------------------------------------------- queries

    def list(
        self,
        *,
        type: MemoType | None = None,
        state: MemoState | None = None,
        search: str | None = None,
        limit: int = 500,
    ) -> list[Memo]:
        clauses: list[str] = []
        params: list[object] = []
        if type is not None:
            clauses.append("type = ?")
            params.append(type.value)
        if state is not None:
            clauses.append("state = ?")
            params.append(state.value)
        if search:
            clauses.append("(header LIKE ? OR contents LIKE ?)")
            like = f"%{search}%"
            params.extend([like, like])
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"SELECT * FROM memos {where} ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        rows = self._connect().execute(sql, params).fetchall()
        return [self._row_to_memo(r) for r in rows]

    def count(self) -> int:
        return self._connect().execute("SELECT COUNT(*) FROM memos").fetchone()[0]

    # ----------------------------------------------------------------- helpers

    def close(self) -> None:
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            conn.close()
            self._local.conn = None
