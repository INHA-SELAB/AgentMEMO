from agentmemo.core.markdown import pygments_css, render


def test_render_basic_heading_and_paragraph() -> None:
    html = render("# Title\n\nbody text")
    assert "<h1>" in html and "Title" in html
    assert "<p>" in html and "body text" in html


def test_render_fenced_code_uses_pygments() -> None:
    html = render("```python\nprint('hi')\n```")
    # Pygments wraps tokens in span.<class>
    assert "language-python" in html
    assert "<span" in html


def test_render_table_and_tasklist() -> None:
    md = (
        "| a | b |\n"
        "|---|---|\n"
        "| 1 | 2 |\n\n"
        "- [x] done\n"
        "- [ ] todo\n"
    )
    html = render(md)
    assert "<table>" in html
    assert "checkbox" in html


def test_pygments_css_nonempty() -> None:
    css = pygments_css()
    assert ".hl" in css
    assert len(css) > 100
