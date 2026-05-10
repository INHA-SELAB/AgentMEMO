from pathlib import Path

import pytest

from agentmemo.core.models import Memo, MemoState, MemoType
from agentmemo.core.repository import MemoRepository


@pytest.fixture
def repo(tmp_path: Path) -> MemoRepository:
    return MemoRepository(tmp_path / "test.db")


def test_create_and_get(repo: MemoRepository) -> None:
    memo = repo.create(Memo(header="hello", contents="# hi"))
    assert memo.id is not None
    fetched = repo.get(memo.id)
    assert fetched is not None
    assert fetched.header == "hello"
    assert fetched.contents == "# hi"
    assert fetched.type is MemoType.PLAN
    assert fetched.state is MemoState.OPEN


def test_update_changes_updated_at(repo: MemoRepository) -> None:
    memo = repo.create(Memo(header="orig"))
    original_ts = memo.updated_at
    memo.header = "changed"
    memo.state = MemoState.IN_PROGRESS
    repo.update(memo)
    fetched = repo.get(memo.id)
    assert fetched.header == "changed"
    assert fetched.state is MemoState.IN_PROGRESS
    assert fetched.updated_at >= original_ts


def test_delete(repo: MemoRepository) -> None:
    memo = repo.create(Memo(header="bye"))
    assert repo.delete(memo.id) is True
    assert repo.get(memo.id) is None
    assert repo.delete(memo.id) is False


def test_list_filter_and_search(repo: MemoRepository) -> None:
    repo.create(Memo(header="alpha plan",     type=MemoType.PLAN))
    repo.create(Memo(header="beta research",  type=MemoType.RESEARCH))
    repo.create(Memo(header="gamma plan",     type=MemoType.PLAN, state=MemoState.CLOSED))

    plans = repo.list(type=MemoType.PLAN)
    assert {m.header for m in plans} == {"alpha plan", "gamma plan"}

    open_plans = repo.list(type=MemoType.PLAN, state=MemoState.OPEN)
    assert [m.header for m in open_plans] == ["alpha plan"]

    matches = repo.list(search="research")
    assert [m.header for m in matches] == ["beta research"]


def test_list_orders_by_updated_desc(repo: MemoRepository) -> None:
    a = repo.create(Memo(header="a"))
    b = repo.create(Memo(header="b"))
    # touch a so it becomes most recent
    a.contents = "edited"
    repo.update(a)
    listed = repo.list()
    assert listed[0].id == a.id
    assert listed[1].id == b.id


def test_count(repo: MemoRepository) -> None:
    assert repo.count() == 0
    repo.create(Memo(header="x"))
    repo.create(Memo(header="y"))
    assert repo.count() == 2
