"""CLI entry point for the (future) HTTP MCP server.

Currently a placeholder so `agentmemo-server` exists as a console script. Will
boot a Starlette app exposing MCP tools backed by `MemoRepository`.
"""

from __future__ import annotations


def main(argv: list[str] | None = None) -> int:
    raise NotImplementedError(
        "agentmemo-server is not implemented yet. The UI MVP ships first; the "
        "HTTP MCP server lands in a follow-up. See src/agentmemo/server/README.md."
    )


if __name__ == "__main__":
    raise SystemExit(main())
