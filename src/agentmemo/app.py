"""GUI entry point. Wires the repository to the main window and runs the
QApplication event loop.
"""

from __future__ import annotations

import sys
from importlib import resources

from PySide6.QtWidgets import QApplication

from agentmemo.core.repository import MemoRepository
from agentmemo.ui.main_window import MainWindow


def _load_stylesheet() -> str:
    try:
        return resources.files("agentmemo.ui.assets").joinpath("style.qss").read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError):
        return ""


def main(argv: list[str] | None = None) -> int:
    app = QApplication(argv if argv is not None else sys.argv)
    app.setApplicationName("AgentMEMO")
    app.setOrganizationName("AgentMEMO")
    qss = _load_stylesheet()
    if qss:
        app.setStyleSheet(qss)

    repo = MemoRepository()
    window = MainWindow(repo)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
