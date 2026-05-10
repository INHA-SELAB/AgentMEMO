"""Left pane: search bar + scrolling list of memos.

Row layout: state-color dot · (header / preview / meta). The 1 Hz auto-refresh
in MainWindow hits `refresh()`; we fingerprint the result and skip the rebuild
when nothing observable has changed, to avoid flicker and pointless work.
"""

from __future__ import annotations

from PySide6.QtCore import QSignalBlocker, QSize, Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from agentmemo.core.models import Memo
from agentmemo.core.repository import MemoRepository

_PREVIEW_LEN = 80


def _fingerprint(memos: list[Memo]) -> tuple:
    """Cheap signature of what the list visibly depends on."""
    return tuple((m.id, m.updated_at, m.header, m.type, m.state) for m in memos)


class _MemoItemWidget(QWidget):
    """Row widget — colored state dot + (header / optional preview / meta)."""

    def __init__(self, memo: Memo, parent: QWidget | None = None):
        super().__init__(parent)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(12, 10, 14, 10)
        outer.setSpacing(10)

        dot = QLabel("●")
        dot.setObjectName("stateDot")
        dot.setProperty("state", memo.state.value)
        dot.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        outer.addWidget(dot)

        text = QVBoxLayout()
        text.setContentsMargins(0, 0, 0, 0)
        text.setSpacing(3)

        header = QLabel(memo.header or "Untitled")
        header.setProperty("class", "memo-header")
        text.addWidget(header)

        preview_text = (memo.contents or "").strip().replace("\n", " ")
        if preview_text:
            if len(preview_text) > _PREVIEW_LEN:
                preview_text = preview_text[: _PREVIEW_LEN - 1] + "…"
            preview = QLabel(preview_text)
            preview.setProperty("class", "memo-preview")
            text.addWidget(preview)

        meta = QLabel(
            f"{memo.updated_at:%Y-%m-%d %H:%M}  ·  {memo.type.value}  ·  {memo.state.value}"
        )
        meta.setProperty("class", "memo-meta")
        text.addWidget(meta)

        outer.addLayout(text, 1)


class MemoListPane(QWidget):
    """Search + list. Emits `memoSelected(Memo | None)` on selection change."""

    memoSelected = Signal(object)  # Memo | None

    def __init__(self, repo: MemoRepository, parent: QWidget | None = None):
        super().__init__(parent)
        self._repo = repo
        self._memos: list[Memo] = []
        self._last_fp: tuple | None = None

        self._search = QLineEdit(self)
        self._search.setPlaceholderText("🔍  Search")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._on_search_changed)

        self._list = QListWidget(self)
        self._list.setObjectName("memoList")
        self._list.itemSelectionChanged.connect(self._emit_selection)

        search_row = QHBoxLayout()
        search_row.setContentsMargins(8, 8, 8, 4)
        search_row.addWidget(self._search)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(search_row)
        layout.addWidget(self._list, 1)

        self.setMinimumWidth(280)

    # ------------------------------------------------------------------ public

    def refresh(self) -> None:
        """Re-fetch from the repository. Skip the rebuild if nothing changed.

        Called both on user action (search input) and from the 1 Hz timer.
        """
        query = self._search.text().strip() or None
        fresh = self._repo.list(search=query)
        fp = _fingerprint(fresh)
        if fp == self._last_fp:
            return
        self._last_fp = fp

        # Preserve current selection by id across the rebuild.
        selected_id = self._selected_id()
        self._memos = fresh

        # Block selection signals so the clear+repopulate doesn't fire spurious
        # None-selection events that would clear the right pane.
        blocker = QSignalBlocker(self._list)
        self._list.clear()
        for memo in fresh:
            item = QListWidgetItem(self._list)
            widget = _MemoItemWidget(memo)
            item.setSizeHint(QSize(0, widget.sizeHint().height()))
            item.setData(Qt.ItemDataRole.UserRole, memo.id)
            self._list.addItem(item)
            self._list.setItemWidget(item, widget)

        target_row = self._row_for_id(selected_id) if selected_id is not None else -1
        if target_row >= 0:
            self._list.setCurrentRow(target_row)
        elif self._list.count():
            self._list.setCurrentRow(0)
        del blocker

        self._emit_selection()

    def current_memo(self) -> Memo | None:
        memo_id = self._selected_id()
        if memo_id is None:
            return None
        return next((m for m in self._memos if m.id == memo_id), None)

    # ------------------------------------------------------------------- slots

    def _on_search_changed(self, _text: str) -> None:
        # Force rebuild on search change (fingerprint-only check would skip it
        # because the underlying memos may not have changed).
        self._last_fp = None
        self.refresh()

    def _emit_selection(self) -> None:
        self.memoSelected.emit(self.current_memo())

    # ----------------------------------------------------------------- helpers

    def _selected_id(self) -> int | None:
        item = self._list.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def _row_for_id(self, memo_id: int) -> int:
        for i in range(self._list.count()):
            if self._list.item(i).data(Qt.ItemDataRole.UserRole) == memo_id:
                return i
        return -1
