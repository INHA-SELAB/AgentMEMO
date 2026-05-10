"""Read-only memo viewer.

Shows a single memo's metadata (date, type, state, id) plus its markdown body
rendered in a QWebEngineView. There is no editor — agents write via MCP, the
GUI just observes. We re-render only when the displayed memo's fingerprint
changes so the QWebEngineView scroll position survives the 1 Hz auto-refresh.
"""

from __future__ import annotations

from importlib import resources

from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from agentmemo.core.markdown import pygments_css, render
from agentmemo.core.models import Memo


def _load_viewer_template() -> str:
    try:
        return (
            resources.files("agentmemo.ui.assets")
            .joinpath("viewer.html")
            .read_text(encoding="utf-8")
        )
    except (FileNotFoundError, ModuleNotFoundError):
        return "<html><body>{body}</body></html>"


_EMPTY_BODY = (
    '<div class="empty-state">'
    '<div class="empty-glyph">¶</div>'
    '<div class="empty-title">No content yet</div>'
    '<div class="empty-hint">Waiting for an agent to fill this in.</div>'
    "</div>"
)


class MemoViewPane(QWidget):
    """Read-only pane: header / type+state badges / markdown body."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._memo: Memo | None = None
        self._last_render_key: tuple | None = None
        self._template = _load_viewer_template()
        self._pygments_css = pygments_css()

        # ---- top bar: centered date + #id on the right -------------------
        self._date_lbl = QLabel("—")
        self._date_lbl.setObjectName("dateLabel")
        self._date_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._id_lbl = QLabel("")
        self._id_lbl.setObjectName("idLabel")

        top = QHBoxLayout()
        top.setContentsMargins(20, 10, 20, 6)
        top.addStretch(1)
        top.addWidget(self._date_lbl, 2)
        top.addStretch(1)
        top.addWidget(self._id_lbl)

        # ---- title -------------------------------------------------------
        self._title_lbl = QLabel("—")
        self._title_lbl.setObjectName("titleLabel")
        self._title_lbl.setWordWrap(True)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(28, 4, 28, 4)
        title_row.addWidget(self._title_lbl)

        # ---- badges row --------------------------------------------------
        self._type_badge = QLabel("")
        self._type_badge.setObjectName("typeBadge")
        self._state_badge = QLabel("")
        self._state_badge.setObjectName("stateBadge")

        badges = QHBoxLayout()
        badges.setContentsMargins(28, 4, 28, 12)
        badges.setSpacing(8)
        badges.addWidget(self._type_badge)
        badges.addWidget(self._state_badge)
        badges.addStretch(1)

        # ---- header/body separator (1px hairline) ------------------------
        separator = QWidget()
        separator.setObjectName("headerSep")
        separator.setFixedHeight(1)

        # ---- body --------------------------------------------------------
        self._viewer = QWebEngineView()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(top)
        layout.addLayout(title_row)
        layout.addLayout(badges)
        layout.addWidget(separator)
        layout.addWidget(self._viewer, 1)

        self.clear()

    # ------------------------------------------------------------------ public

    def show_memo(self, memo: Memo | None) -> None:
        if memo is None:
            self.clear()
            return

        # Rebuild only when the memo or its visible fields actually changed —
        # otherwise auto-refresh would reset scroll position every second.
        key = (memo.id, memo.updated_at, memo.header, memo.type, memo.state)
        if key == self._last_render_key:
            return
        self._last_render_key = key
        self._memo = memo

        self._date_lbl.setText(memo.updated_at.strftime("%B %d, %Y · %I:%M %p"))
        self._id_lbl.setText(f"#{memo.id}")
        self._title_lbl.setText(memo.header or "Untitled")
        self._set_badge(self._type_badge, "type", memo.type.value)
        self._set_badge(self._state_badge, "state", memo.state.value)
        self._render_viewer()

    def clear(self) -> None:
        self._memo = None
        self._last_render_key = None
        self._date_lbl.setText("—")
        self._id_lbl.setText("")
        self._title_lbl.setText("—")
        self._set_badge(self._type_badge, "type", "")
        self._set_badge(self._state_badge, "state", "")
        self._viewer.setHtml("")

    # ----------------------------------------------------------------- helpers

    @staticmethod
    def _set_badge(label: QLabel, prop: str, value: str) -> None:
        """Set badge text + dynamic property, then force QSS to re-evaluate."""
        label.setText(value.replace("_", " ") if value else "")
        label.setProperty(prop, value)
        label.setVisible(bool(value))
        st = label.style()
        st.unpolish(label)
        st.polish(label)

    def _render_viewer(self) -> None:
        if self._memo is None:
            self._viewer.setHtml("")
            return
        body = render(self._memo.contents) if self._memo.contents.strip() else _EMPTY_BODY
        html = self._template.replace("{pygments_css}", self._pygments_css).replace(
            "{body}", body
        )
        self._viewer.setHtml(html)
