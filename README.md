# AgentMEMO - AI 에이전트를 위한 메모 저장소

AgentMEMO는 AI 에이전트가 작업하면서 남기는 메모를 사람이 지켜볼 수 있게
해주는 macOS/iPadOS Notes 스타일의 메모 **뷰어**입니다.

에이전트(Claude, Codex, Gemini 등)는 HTTP MCP 서버를 통해 메모를 만들고
수정합니다. 사람은 GUI에서 렌더링된 마크다운 메모를 실시간에 가깝게
확인합니다.

GUI는 의도적으로 **읽기 전용**입니다. 새 메모 만들기, 삭제, 편집 버튼을
두지 않습니다. 이 프로젝트의 핵심 목적은 거대한 협업 플랫폼을 만드는 것이
아니라, MCP 서버가 어떤 모습으로 동작하는지와 에이전트가 공유 상태를 어떻게
다루는지를 교육용으로 보여주는 것입니다. GUI는 1초마다 자동 새로고침되어
에이전트 쪽 변경 사항이 바로 드러납니다.

> 상태: **alpha**. UI 뷰어는 연결되어 있으며, MCP 서버는 아직 구현 중입니다.
> 자세한 내용은 `src/agentmemo/server/`를 참고하세요.

---

## 메모 스키마

| 필드 | 타입 / 값 |
|------|-----------|
| 날짜 | `created_at`, `updated_at` (ISO-8601, UTC) |
| 타입 | `PLAN` · `RESEARCH` · `IMPLEMENT` · `REVIEW` (작업 성격에 대한 에이전트 힌트) |
| 상태 | `OPEN` -> `IN_PROGRESS` -> `CLOSED` (작업 생명주기) |
| 제목 | 한 줄짜리 짧은 제목 |
| 내용 | 마크다운 본문 |

---

## 빠른 시작

**Python 3.10+**가 필요합니다. 저장소를 받은 뒤 다음 명령을 실행하세요.

```bash
cd AgentMEMO

# macOS / Linux
./run.sh

# Windows
run.bat              # 또는 Explorer에서 run.bat 더블클릭
```

첫 실행 시 `.venv`를 만들고 필요한 패키지를 설치합니다(약 30초).
이후 실행부터는 바로 GUI를 시작합니다.

`run.sh`와 `run.bat`는 실행 전에 스크립트가 있는 프로젝트 루트로 이동합니다.
따라서 다른 위치에서 실행하거나 Windows Explorer에서 더블클릭해도 기본
데이터베이스는 프로젝트 안의 `./data/agentmemo.db`에 생성됩니다.
`AGENTMEMO_DB_PATH` 환경 변수로 데이터베이스 경로를 바꿀 수 있습니다.

---

## 개발용 수동 설치

가상환경을 직접 관리하고 싶다면 다음 순서로 설치하세요.

```bash
git clone https://github.com/your-org/AgentMEMO.git
cd AgentMEMO
python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"     # 테스트와 린터 포함
# pip install -e ".[server]"  # MCP 서버용 의존성 (계획)

agentmemo                   # GUI 실행
python -m agentmemo         # 동일한 실행 방식
```

수동 실행에서는 현재 터미널 위치를 기준으로 `./data/agentmemo.db`가 만들어집니다.
프로젝트 안에 데이터를 두고 싶다면 저장소 루트에서 실행하거나
`AGENTMEMO_DB_PATH`를 지정하세요.

---

## 구조

```text
src/agentmemo/
├── core/        # Qt/UI 의존성이 없는 순수 Python 도메인 계층
│   ├── models.py        # Memo, MemoType, MemoState
│   ├── repository.py    # SQLite CRUD + 검색
│   └── markdown.py      # markdown-it -> HTML
├── ui/          # PySide6 위젯
│   ├── main_window.py
│   ├── memo_list.py
│   ├── memo_view.py
│   └── assets/          # QSS 스타일시트 + viewer.html 템플릿
└── server/      # HTTP MCP 서버 스텁
```

`core` 계층은 `ui`나 `server`를 import하지 않습니다. 그래서 이후 MCP 서버도
GUI와 같은 `MemoRepository`를 재사용할 수 있습니다.

---

## 현재 구현 상태

- [x] UI MVP: 3-pane 레이아웃, 검색, 읽기 전용 마크다운 뷰어
- [x] 타입/상태 배지 표시
- [x] SQLite 저장소: CRUD, 검색, 타입/상태 필터
- [x] GUI 자동 새로고침: 1초 주기로 저장소 변경 확인
- [ ] 타입/상태 필터 UI
- [ ] HTTP MCP 서버 (`agentmemo-server`): 에이전트용 CRUD + 검색 도구 노출
- [ ] 메모별 첨부 파일 폴더

---

## 라이선스

MIT.
