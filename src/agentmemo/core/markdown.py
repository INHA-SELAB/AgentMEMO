"""Markdown → HTML rendering for the memo viewer.

Lives in core (no Qt deps) so the same renderer can be reused by the MCP
server for previews/exports.
"""

from __future__ import annotations

from functools import lru_cache

from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound


def _highlight(code: str, lang: str, _attrs: str) -> str:
    try:
        lexer = get_lexer_by_name(lang) if lang else guess_lexer(code)
    except ClassNotFound:
        return ""  # let markdown-it fall back to its default <pre><code>
    formatter = HtmlFormatter(nowrap=True)
    return f'<pre class="hl"><code class="language-{lang}">{highlight(code, lexer, formatter)}</code></pre>'


@lru_cache(maxsize=1)
def _md() -> MarkdownIt:
    md = (
        MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": True, "highlight": _highlight})
        .enable(["table", "strikethrough"])
        .use(tasklists_plugin, enabled=True)
    )
    return md


@lru_cache(maxsize=1)
def pygments_css() -> str:
    """Return a Pygments stylesheet (light theme) for the viewer."""
    return HtmlFormatter().get_style_defs(".hl")


def render(markdown_text: str) -> str:
    """Render a markdown string to HTML body fragment."""
    return _md().render(markdown_text or "")
