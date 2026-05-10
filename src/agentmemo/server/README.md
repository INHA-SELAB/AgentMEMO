# `agentmemo.server` — HTTP MCP server (planned)

This subpackage is a **placeholder**. The UI MVP ships first; the server lands
in a follow-up.

## Planned shape

- Transport: **HTTP + SSE** (Streamable HTTP per MCP spec) — picked over stdio
  because the expected workload is multiple agents (Claude / Codex / Gemini)
  connected at once.
- Default bind: `127.0.0.1:8765` (loopback only — never bind to `0.0.0.0` by
  default).
- Backed by `agentmemo.core.MemoRepository` against the same SQLite file the GUI
  uses (WAL mode is already enabled in `MemoRepository.__init__`).

## Tools to expose

| MCP tool        | Maps to                                              |
|-----------------|------------------------------------------------------|
| `memo.create`   | `repo.create(Memo(...))`                             |
| `memo.get`      | `repo.get(id)`                                       |
| `memo.update`   | `repo.update(memo)`                                  |
| `memo.delete`   | `repo.delete(id)`                                    |
| `memo.list`     | `repo.list(type=, state=, search=, limit=)`          |
| `memo.append`   | (helper) appends markdown to `contents` + saves      |

## Entry point

`pyproject.toml` already wires `agentmemo-server = "agentmemo.server.cli:main"`. The
CLI is not implemented yet — calling it raises `NotImplementedError`.

## Why later, not now

Per the project plan, the UI MVP comes first so the human-visible side can be
reviewed before the agent-facing API surface is locked in.
