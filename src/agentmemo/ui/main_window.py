"""Top-level window: 3-pane layout (search/list | viewer) + 1 Hz refresh.

The GUI is a passive observer of the SQLite store. Agents (via the MCP
server) write; this window just polls the repository every second and
displays whatever it finds.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMainWindow, QSplitter, QStatusBar, QWidget

from agentmemo.core.models import Memo
from agentmemo.core.repository import MemoRepository
from agentmemo.ui.memo_list import MemoListPane
from agentmemo.ui.memo_view import MemoViewPane

_REFRESH_INTERVAL_MS = 1000


class MainWindow(QMainWindow):
    def __init__(self, repo: MemoRepository, parent: QWidget | None = None):
        super().__init__(parent)
        self._repo = repo
        self.setWindowTitle("AgentMEMO")
        self.resize(1100, 680)

        self._list = MemoListPane(repo, self)
        self._view = MemoViewPane(self)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.addWidget(self._list)
        splitter.addWidget(self._view)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([320, 780])
        self.setCentralWidget(splitter)

        self.setStatusBar(QStatusBar(self))

        # Wiring
        self._list.memoSelected.connect(self._view.show_memo)
        self._list.memoSelected.connect(self._update_status)

        # Initial load + 1 Hz auto-refresh so MCP-driven changes appear.
        self._list.refresh()
        self._timer = QTimer(self)
        self._timer.setInterval(_REFRESH_INTERVAL_MS)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self) -> None:
        self._list.refresh()

    def _update_status(self, memo: Memo | None) -> None:
        if memo is None:
            self.statusBar().showMessage("No memo selected — waiting for an agent.")
            return
        self.statusBar().showMessage(
            f"#{memo.id}  ·  {memo.type.value}  ·  {memo.state.value}  ·  "
            f"updated {memo.updated_at:%Y-%m-%d %H:%M:%S}"
        )
