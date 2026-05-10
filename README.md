# AgentMEMO — A memo store for AI agents

A macOS/iPadOS Notes–style memo **viewer** for watching AI agents work.
Agents (Claude, Codex, Gemini, …) create and update memos through an HTTP
MCP server; humans watch the rendered markdown in the GUI as it happens.

The GUI is **read-only** by design — no New, Delete, or Edit affordances.
The whole point is to teach what an MCP server looks like in practice and how
agents drive shared state through it. The GUI auto-refreshes at 1 Hz so
agent-side changes appear immediately.

> Status: **alpha**. UI viewer is wired; the MCP server is in progress —
> see `src/agentmemo/server/`.

---

## Memo schema

| Field    | Type / values                                            |
|----------|----------------------------------------------------------|
| Date     | `created_at`, `updated_at` (ISO-8601, UTC)               |
| Type     | `PLAN` · `RESEARCH` · `IMPLEMENT` · `REVIEW` (agent hint about where the work belongs) |
| State    | `OPEN` → `IN_PROGRESS` → `CLOSED` (lifecycle)            |
| Header   | Short title (one line)                                   |
| Contents | Markdown body                                            |

---

## Quick start

Requires **Python 3.10+**. After cloning:

```bash
# macOS / Linux
./run.sh

# Windows
run.bat              # (or double-click run.bat in Explorer)
```

The first run creates a `.venv` and installs everything (~30 seconds).
Every run after that just launches the GUI.

The database is created on first launch at `./data/agentmemo.db` (override
with the `AGENTMEMO_DB_PATH` environment variable).

---

## Install manually (for development)

If you'd rather drive the venv yourself:

```bash
git clone https://github.com/your-org/AgentMEMO.git
cd AgentMEMO
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"     # adds tests + linter
# pip install -e ".[server]"  # for the MCP server (planned)

agentmemo                   # launches the GUI
python -m agentmemo         # equivalent
```

---

## Architecture

```
src/agentmemo/
├── core/        # pure-Python domain (no Qt/UI deps) — reusable from server
│   ├── models.py        # Memo, MemoType, MemoState
│   ├── repository.py    # SQLite CRUD + search
│   └── markdown.py      # markdown-it → HTML
├── ui/          # PySide6 widgets
│   ├── main_window.py
│   ├── memo_list.py
│   ├── memo_view.py
│   └── assets/          # QSS stylesheet + viewer.html template
└── server/      # (stub) HTTP MCP server — multi-agent access
```

The **core** layer never imports from `ui` or `server`. This is what lets the
upcoming MCP server reuse the same `MemoRepository` the GUI uses.

---

## Roadmap

- [x] UI MVP: 3-pane layout, search, create/delete, markdown viewer
- [ ] Type/State badges + filters
- [ ] HTTP MCP server (`agentmemo-server`) — exposes CRUD + search to agents
- [ ] Live refresh: GUI auto-updates when an agent writes via MCP
- [ ] Per-memo attachment folder

---

## License

MIT.
