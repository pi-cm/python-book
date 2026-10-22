# 부록 A. uv 완전 가이드

이 책의 예제는 모두 `uv run python ...`으로 실행했습니다. 14장에서 uv로 패키지를 만드는 흐름을 한 번 따라가 봤다면, 이 부록은 그때 다 못 한 이야기를 모아 둔 사용 설명서예요. 새 프로젝트를 시작할 때, 남의 프로젝트를 받아 실행할 때, 그리고 "어, 이거 왜 안 되지?" 싶을 때 펼쳐 보세요.

이 부록의 명령과 출력은 **uv 0.9.16**(macOS)에서 직접 실행해 확인했습니다. uv는 업데이트가 잦아서 버전이 다르면 출력 문구가 조금 다를 수 있지만, 명령과 옵션의 뜻은 그대로입니다. 지금 쓰는 버전은 `uv --version`으로 확인할 수 있어요.

```bash
$ uv --version
uv 0.9.16 (a63e5b62e 2025-12-06)
```

---

## A.1 uv는 무엇을 대신해 주나요?

예전에는 파이썬 프로젝트 하나를 시작하려면 도구를 여러 개 써야 했습니다. 파이썬 자체는 공식 홈페이지나 pyenv로 설치하고, 가상환경은 `python -m venv`로 만들고, 활성화한 다음 `pip install`로 라이브러리를 넣고, 설치한 목록은 `pip freeze > requirements.txt`로 따로 적어 두고, 명령행 도구는 pipx로 설치하고, 배포할 때는 build와 twine을 썼죠.

uv는 이 일을 명령 하나로 모았습니다.

| 예전 방식 | uv |
|---|---|
| pyenv, 공식 설치 프로그램 | `uv python install` |
| `python -m venv .venv` + 활성화 | `uv venv`, 또는 `uv run`이 알아서 |
| `pip install 패키지` | `uv add 패키지` (프로젝트), `uv pip install` (호환 모드) |
| `pip freeze > requirements.txt` | `uv.lock` (자동), `uv export` |
| pipx | `uv tool install`, `uvx` |
| `python -m build`, twine | `uv build`, `uv publish` |

가장 큰 차이는 **목록(pyproject.toml)과 잠금 파일(uv.lock)과 실제 설치 상태(.venv)를 uv가 늘 맞춰 준다**는 점입니다. 14장의 비유로 말하면 공구 목록을 적는 사람, 공구를 사 오는 사람, 창고를 정리하는 사람이 한 명이 된 셈이에요.

## A.2 설치

운영체제마다 설치 방법이 조금 다릅니다. 아래는 uv 공식 문서의 설치 명령입니다. 하나만 고르면 돼요.

```bash
# macOS / Linux (공식 설치 스크립트)
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS (Homebrew)
brew install uv
```

```powershell
# Windows (PowerShell, 공식 설치 스크립트)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Windows (WinGet 또는 Scoop)
winget install --id=astral-sh.uv -e
scoop install main/uv
```

설치가 끝나면 **터미널을 새로 열고** `uv --version`을 실행해 보세요. "명령을 찾을 수 없다"고 나오면 대개 설치 경로가 아직 PATH에 반영되지 않은 것이라 터미널을 다시 열면 해결됩니다.

uv 자체를 최신 버전으로 올릴 때는 이렇게 합니다.

```bash
uv self update
```

다만 `uv self update`는 공식 설치 스크립트로 설치했을 때만 동작합니다. Homebrew로 설치했다면 `brew upgrade uv`처럼 설치한 도구의 업그레이드 방법을 쓰세요.

> **Q. 파이썬을 먼저 설치해야 하나요?**
> 아니요. uv는 파이썬 없이 혼자 동작하는 프로그램이에요. 필요한 파이썬 버전이 컴퓨터에 없으면 uv가 알아서 내려받습니다. 다음 절에서 직접 해 봅시다.

## A.3 파이썬 버전 관리: uv python

### 설치된 버전 보기

`uv python list`는 컴퓨터에 있는 파이썬과 내려받을 수 있는 파이썬을 함께 보여 줍니다. 설치된 것은 경로가, 아직 없는 것은 `<download available>`이 붙어요.

```bash
$ uv python list
cpython-3.15.0a2-macos-aarch64-none                 <download available>
cpython-3.15.0a2+freethreaded-macos-aarch64-none    <download available>
cpython-3.14.2-macos-aarch64-none                   <download available>
cpython-3.13.11-macos-aarch64-none                  /Users/.../uv/python/cpython-3.13.11-macos-aarch64-none/bin/python3.13
cpython-3.12.10-macos-aarch64-none                  /Users/.../uv/python/cpython-3.12.10-macos-aarch64-none/bin/python3.12
...
```

이름 끝의 `+freethreaded`는 부록 C에서 소개할 "GIL 없는 실험 빌드"이고, `a2` 같은 꼬리표는 아직 정식 출시 전인 알파 버전이라는 뜻입니다. 설치된 것만 보고 싶으면 `uv python list --only-installed`를 쓰세요.

### 설치하고 찾기

```bash
$ uv python install 3.14
Installed Python 3.14.2 in 1.45s
 + cpython-3.14.2-macos-aarch64-none (python3.14)

$ uv python find 3.12
/Users/.../uv/python/cpython-3.12.10-macos-aarch64-none/bin/python3.12
```

`3.14`처럼 버전을 짧게 쓰면 그 계열의 최신 패치 버전을 받아 옵니다. uv가 받은 파이썬은 `uv python dir`이 알려 주는 폴더에 모이고, 지울 때는 `uv python uninstall 3.14`를 씁니다.

사실 이 명령을 직접 쓸 일은 생각보다 적습니다. `uv run`이나 `uv sync`가 프로젝트에 필요한 버전이 없으면 알아서 내려받기 때문이에요.

### 프로젝트의 버전 고정: uv python pin

```bash
$ uv python pin 3.12
Pinned `.python-version` to `3.12`
```

`pin`은 현재 폴더의 `.python-version` 파일에 버전을 적어 둡니다. 이 폴더에서 실행하는 `uv run`, `uv sync`, `uv venv`는 이 파일을 보고 파이썬 버전을 고릅니다. 이 책의 저장소에도 이 파일이 있어서 `uv run python`이 늘 3.12로 실행돼요.

`.python-version`과 `pyproject.toml`의 `requires-python`은 하는 일이 다릅니다.

| 위치 | 뜻 | 예 |
|---|---|---|
| `.python-version` | 이 폴더에서 **실제로 쓸** 버전 | `3.12` |
| `requires-python` | 이 프로젝트가 **동작한다고 약속하는** 범위 | `>=3.12` |

`requires-python = ">=3.12"`인 프로젝트를 3.13에서 돌려도 되지만, 개발할 때는 `.python-version`으로 한 버전을 정해 두면 팀원 모두가 같은 버전으로 실행하게 됩니다.

## A.4 프로젝트 만들기: uv init

### 기본 프로젝트(애플리케이션)

옵션 없이 `uv init`을 하면 바로 실행해 볼 수 있는 작은 프로젝트가 생깁니다. `--python`으로 버전을 정할 수 있어요.

```bash
$ uv init --python 3.12 hello
Initialized project `hello` at `.../uvtest/hello`
$ cd hello
$ ls -A
.git  .gitignore  .python-version  main.py  pyproject.toml  README.md
```

`.git`과 `.gitignore`까지 만들어 주는 것이 보이죠? 이미 git 저장소 안에서 실행하면 새 저장소는 만들지 않습니다. 생성된 `pyproject.toml`은 이렇습니다.

```toml
[project]
name = "hello"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []
```

`dependencies`가 빈 목록이고, `[build-system]`이 없습니다. 이 프로젝트는 "실행만 하는 프로그램"이라 남에게 설치해 줄 포장(빌드) 정보가 필요 없기 때문이에요.

### 패키지 프로젝트: --package

남에게 배포할 패키지나 명령행 도구를 만들 때는 14장에서 한 것처럼 `--package`를 붙입니다.

```bash
$ uv init --package --python 3.12 mypkg
$ find mypkg -not -path '*/.git/*' -type f
mypkg/.gitignore
mypkg/.python-version
mypkg/pyproject.toml
mypkg/README.md
mypkg/src/mypkg/__init__.py
```

소스가 `src/mypkg/` 아래로 들어갔고, `pyproject.toml`에는 두 부분이 더 생깁니다.

```toml
[project.scripts]
mypkg = "mypkg:main"

[build-system]
requires = ["uv_build>=0.9.16,<0.10.0"]
build-backend = "uv_build"
```

`[project.scripts]`는 "`mypkg`라는 터미널 명령을 치면 `mypkg` 패키지의 `main()` 함수를 실행하라"는 뜻입니다. 그래서 바로 이렇게 실행할 수 있어요.

```bash
$ uv run mypkg
Hello from mypkg!
```

`[build-system]`은 패키지를 포장할 도구(빌드 백엔드)를 정합니다. uv 0.9는 기본으로 uv가 직접 만든 `uv_build`를 씁니다. 14장의 예제처럼 `hatchling`을 적어도 똑같이 동작해요. 다른 백엔드로 시작하고 싶으면 `uv init --package --build-backend hatch`처럼 고를 수 있습니다.

### 그 밖의 init 옵션

| 옵션 | 하는 일 |
|---|---|
| `--app` | 애플리케이션 프로젝트 (옵션을 안 주면 이것) |
| `--package` | 빌드 가능한 패키지(`src/` 구조, 빌드 백엔드 포함) |
| `--lib` | 라이브러리 프로젝트 (`--package`가 함께 켜짐) |
| `--script 파일.py` | 프로젝트 없이 스크립트 하나 (A.6절) |
| `--bare` | `pyproject.toml`만 만듦 |
| `--python 3.12` | 파이썬 버전 지정 |
| `--vcs none` | git 저장소를 만들지 않음 |
| `--name 이름` | 폴더 이름과 다른 프로젝트 이름 |

## A.5 의존성 관리: add, remove

### uv add

라이브러리를 프로젝트에 넣을 때는 `uv add`입니다. 이 명령 하나가 세 가지 일을 합니다. `pyproject.toml`에 적고, `uv.lock`에 정확한 버전을 기록하고, `.venv`에 설치합니다. 가상환경이 없으면 그것도 만들어요.

```bash
$ uv add requests
Using CPython 3.12.10
Creating virtual environment at: .venv
Resolved 6 packages in 38ms
Prepared 3 packages in 53ms
Installed 5 packages in 3ms
 + certifi==2026.10.19
 + charset-normalizer==3.5.2
 + idna==3.20
 + requests==2.34.2
 + urllib3==2.8.0
```

`requests` 하나를 넣었는데 다섯 개가 설치됐죠? `requests`가 쓰는 라이브러리(전이 의존성)까지 함께 들어온 것입니다. `pyproject.toml`에는 내가 직접 고른 `requests`만 적히고, 나머지는 `uv.lock`에 기록됩니다. 버전 번호는 실행하는 날에 따라 다르게 나와요.

버전 범위를 직접 정하고 싶으면 따옴표로 감싸서 씁니다. 셸이 `<`, `>`를 다른 뜻으로 해석하지 않게 하려는 거예요.

```bash
uv add "requests>=2.30,<3"
uv add "fastapi>=0.100.0"
```

### 개발용, 묶음, 선택 의존성

모든 라이브러리가 같은 자격으로 들어가는 것은 아닙니다. 실제로 네 가지 방법으로 하나씩 넣어 보면 `pyproject.toml`이 이렇게 바뀝니다.

```bash
uv add requests                  # 프로그램이 돌아가는 데 꼭 필요
uv add --dev pytest              # 개발할 때만 (테스트)
uv add --group lint ruff         # 개발용인데 이름 붙인 묶음
uv add --optional web fastapi    # 설치하는 사람이 골라서 받는 기능
```

```toml
[project]
dependencies = [
    "requests>=2.34.2",
]

[project.optional-dependencies]
web = [
    "fastapi>=0.156.4",
]

[dependency-groups]
dev = [
    "pytest>=9.1.1",
]
lint = [
    "ruff>=0.17.1",
]
```

`--group`과 `--optional`은 헷갈리기 쉬운데, **누가 쓰느냐**로 구분하면 됩니다.

| 구분 | 적히는 곳 | 누구를 위한 것 | 설치할 때 |
|---|---|---|---|
| (기본) | `[project] dependencies` | 프로그램을 쓰는 모든 사람 | 늘 설치 |
| `--dev` | `[dependency-groups] dev` | 이 프로젝트를 **개발하는 사람** | `uv sync`가 기본으로 설치 |
| `--group 이름` | `[dependency-groups] 이름` | 개발하는 사람 (용도별 묶음) | `--group 이름`을 줄 때만 |
| `--optional 이름` | `[project.optional-dependencies] 이름` | 패키지를 **설치해 쓰는 사람** | `--extra 이름`을 줄 때만 |

`--dev`는 사실 `--group dev`의 줄임말입니다. `dev` 묶음만 특별히 기본으로 설치되는 거예요. 그리고 `[dependency-groups]`는 패키지를 배포할 때 포함되지 않습니다. 반대로 `optional-dependencies`는 배포한 패키지에 들어가서, 남이 `pip install "mypkg[web]"`처럼 골라 설치할 수 있어요. 정리하면 이렇습니다. 테스트 도구나 코드 검사 도구는 `--dev`나 `--group`, 사용자가 고를 수 있는 추가 기능은 `--optional`입니다.

`uv tree`로 보면 어디서 왔는지가 표시됩니다.

```bash
$ uv tree --depth 1
Resolved 23 packages in 1ms
hello v0.1.0
├── requests v2.34.2
├── fastapi v0.156.4 (extra: web)
└── pytest v9.1.1 (group: dev)
```

`lint` 묶음이 안 보이는 것은 기본으로 포함되는 묶음이 아니기 때문입니다.

### uv remove

```bash
uv remove requests
uv remove --dev pytest
uv remove --optional web fastapi
```

뺄 때도 넣을 때와 같은 옵션을 줍니다. `pyproject.toml`, `uv.lock`, `.venv`에서 함께 사라져요.

## A.6 실행: uv run

### 프로젝트 안에서

`uv run` 뒤에 오는 명령은 프로젝트의 가상환경 안에서 실행됩니다. 실행하기 전에 uv가 잠금 파일과 가상환경을 확인하고, 다르면 먼저 맞춥니다. 그래서 가상환경을 "활성화"할 필요가 없어요.

```bash
$ uv run main.py
Hello from hello!

$ uv run python -c "import sys; print(sys.version.split()[0]); print(sys.prefix)"
3.12.10
.../uvtest/hello/.venv
```

`sys.prefix`가 프로젝트의 `.venv`를 가리키는 것이 보이죠? `uv run main.py`처럼 `.py` 파일을 바로 줘도 되고, `uv run pytest`, `uv run ruff check`처럼 설치된 명령을 줘도 됩니다.

### 잠깐만 빌려 쓰기: --with

프로젝트 목록에 넣고 싶지는 않은데 한 번만 써 보고 싶은 라이브러리가 있을 때는 `--with`를 씁니다. 14장에서 `pycodestyle`을 이렇게 썼죠.

```bash
$ uv run --with rich python -c "import rich; print('rich OK')"
Installed 4 packages in 7ms
rich OK

$ uv run python -c "import rich"
ModuleNotFoundError: No module named 'rich'
```

`--with`로 준 패키지는 그 실행에만 쓰이는 임시 환경에 들어갑니다. 바로 다음 실행에서는 `rich`가 없다고 나오죠. 프로젝트의 `pyproject.toml`도 `.venv`도 바뀌지 않습니다.

### 다른 파이썬 버전으로 한 번 돌리기: --python

```bash
$ uv run --python 3.13 python -c "import sys; print(sys.version_info[:2])"
(3, 13)
```

부록 C의 예제를 확인할 때 이 방법을 썼습니다. 다만 **프로젝트 폴더 안에서** 이렇게 하면 uv는 프로젝트의 `.venv` 자체를 3.13으로 다시 만듭니다. 그다음 그냥 `uv run`을 하면 `.python-version`의 3.12로 또 다시 만들어요.

```bash
$ uv run python -c "import sys; print(sys.version_info[:2])"
Using CPython 3.12.10
Removed virtual environment at: .venv
Creating virtual environment at: .venv
Installed 10 packages in 7ms
(3, 12)
```

동작은 맞지만 매번 환경을 지웠다 만드는 셈이니, 다른 버전으로 잠깐 시험만 할 때는 `--no-project`를 붙이거나 프로젝트 밖 폴더에서 실행하세요.

### 스크립트 하나에 의존성 적기: --script

파일 하나짜리 스크립트에 프로젝트까지 만들기는 번거롭죠. uv는 스크립트 파일 맨 위에 의존성을 적는 방법(PEP 723 인라인 메타데이터)을 지원합니다.

```bash
$ uv init --script fetch.py --python 3.12
Initialized script at `fetch.py`
$ uv add --script fetch.py httpx
Resolved 7 packages in 2ms
```

그러면 `fetch.py` 맨 위에 이런 주석 덩어리가 생깁니다.

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx>=0.28.1",
# ]
# ///
```

이제 `uv run fetch.py`만 하면 uv가 `httpx`가 든 임시 환경을 만들어 실행합니다. 파일 하나만 친구에게 보내도 똑같이 실행되니, 간단한 자동화 스크립트에 아주 편해요.

## A.7 잠금과 동기화: uv lock, uv sync

### uv.lock은 무엇인가요?

`pyproject.toml`에는 `requests>=2.34.2`처럼 **범위**가 적혀 있습니다. 오늘 설치하면 2.34.2가, 몇 달 뒤에 설치하면 2.40이 들어올 수도 있죠. `uv.lock`은 "지금 이 프로젝트가 실제로 쓰는 정확한 버전"을 전이 의존성까지 모두 적어 둔 파일입니다. 그래서 `uv.lock`을 git에 함께 커밋하면 다른 사람도 똑같은 버전을 받습니다.

`uv add`, `uv remove`, `uv run`, `uv sync`는 필요하면 잠금 파일을 알아서 갱신하므로 `uv lock`을 직접 칠 일은 많지 않아요. 직접 쓰는 경우는 주로 **업그레이드**할 때입니다.

```bash
uv lock --upgrade                     # 범위 안에서 모두 최신으로
uv lock --upgrade-package requests    # requests만 최신으로
uv lock --check                       # 잠금 파일이 최신인지 검사만
```

`--upgrade`도 `pyproject.toml`에 적힌 범위는 넘지 않습니다. `requests>=2.30,<3`이라면 3.0이 나와도 2.x 중 최신까지만 올라가요.

### uv sync는 "정확히 맞추기"

`uv sync`는 잠금 파일대로 `.venv`를 맞춥니다. 여기서 "맞춘다"는 말이 중요합니다. **목록에 없는 것은 지웁니다.** 앞에서 `--group lint`와 `--optional web`으로 넣었던 것들이 그냥 `uv sync`를 하면 어떻게 되는지 보세요.

```bash
$ uv sync
Resolved 23 packages in 1ms
Uninstalled 11 packages in 23ms
 - annotated-doc==0.0.5
 ...
 - fastapi==0.156.4
 ...
 - ruff==0.17.1
 ...
```

`fastapi`와 `ruff`가 지워졌죠. `uv sync`가 기본으로 설치하는 것은 `dependencies`와 `dev` 묶음뿐이라서 그렇습니다. 다른 묶음까지 원하면 옵션으로 알려 줍니다.

| 옵션 | 설치 범위 |
|---|---|
| (없음) | `dependencies` + `dev` 묶음 |
| `--extra web` | 위 + 선택 의존성 `web` |
| `--all-extras` | 위 + 모든 선택 의존성 |
| `--group lint` | 위 + `lint` 묶음 |
| `--all-groups` | 위 + 모든 묶음 |
| `--no-dev` | `dev` 묶음 빼고 (배포 서버용) |
| `--only-dev` | `dev` 묶음만 |
| `--inexact` | 목록에 없는 패키지를 지우지 않음 |

```bash
$ uv sync --extra web --group lint
...
 + ruff==0.17.1
 + starlette==1.9.0
 ...
```

### --locked와 --frozen

CI(자동 테스트 서버)나 배포 서버에서는 잠금 파일이 바뀌면 안 됩니다. 이때 두 옵션을 씁니다.

- `--locked`: 잠금 파일이 `pyproject.toml`과 맞지 않으면 **오류를 내고 멈춥니다**.
- `--frozen`: 잠금 파일을 검사하지도 고치지도 않고 **있는 그대로** 설치합니다.

`pyproject.toml`에 의존성을 손으로 추가하고 `uv lock`을 깜빡한 상태에서 실행해 보면 차이가 보입니다.

```bash
$ uv sync --locked
The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.
To update the lockfile, run `uv lock`.

$ uv sync --frozen
Audited 10 packages in 0.19ms
```

`--frozen`은 조용히 지나가 버리죠. 그래서 "잠금 파일 갱신을 잊었는지" 잡아내고 싶은 CI에서는 `--locked`가 안전합니다.

### requirements.txt가 필요할 때: uv export

uv를 쓰지 않는 서버나 도구가 `requirements.txt`를 요구하면 잠금 파일에서 뽑아 줄 수 있습니다.

```bash
$ uv export --format requirements.txt --no-hashes --no-dev
# This file was autogenerated by uv via the following command:
#    uv export --format requirements.txt --no-hashes --no-dev
certifi==2026.10.19
    # via requests
...
```

## A.8 명령행 도구: uvx, uv tool

`ruff`, `black`, `httpie`처럼 **라이브러리가 아니라 터미널 명령으로 쓰는 도구**는 프로젝트에 넣을 필요가 없을 때가 많습니다. 이럴 때 쓰는 것이 `uv tool`입니다.

### 한 번 실행: uvx

`uvx`는 `uv tool run`의 줄임말입니다. 도구를 임시 환경에 받아서 바로 실행해요.

```bash
$ uvx pycowsay hi

  --
< hi >
  --
   \   ^__^
    \  (oo)\_______
       (__)\       )\/\
           ||----w |
           ||     ||
```

특정 버전을 쓰고 싶거나, 패키지 이름과 명령 이름이 다를 때는 `--from`을 씁니다.

```bash
$ uvx --from 'ruff==0.6.0' ruff --version
ruff 0.6.0
```

### 계속 쓸 도구: uv tool install

자주 쓰는 도구는 설치해 두면 `uvx` 없이 이름만으로 실행할 수 있습니다. 도구마다 따로 격리된 환경에 들어가서 서로 부딪히지 않아요.

```bash
$ uv tool install pycowsay
Resolved 1 package in 0.59ms
Installed 1 package in 2ms
 + pycowsay==0.0.0.2
Installed 1 executable: pycowsay

$ uv tool list
pycowsay v0.0.0.2
- pycowsay

$ uv tool upgrade pycowsay
$ uv tool uninstall pycowsay
Uninstalled 1 executable: pycowsay
```

설치하고 나서 명령을 못 찾는다면 도구 폴더가 PATH에 없는 것입니다. uv가 설치할 때 경고로 알려 주니, 안내대로 `uv tool update-shell`을 실행하고 터미널을 다시 여세요.

> **Q. `uv add --dev ruff`와 `uv tool install ruff`, 무엇을 써야 하나요?**
> 프로젝트마다 ruff 버전을 맞춰야 하면(팀원 모두 같은 규칙으로 검사해야 하면) `uv add --dev`로 프로젝트에 넣으세요. 버전이 잠금 파일에 남습니다. 어느 프로젝트에서나 그냥 쓰는 개인 도구라면 `uv tool install`이 편합니다.

## A.9 가상환경 직접 다루기: uv venv

`uv run`이 가상환경을 알아서 관리하니 직접 만들 일은 드뭅니다. 그래도 "프로젝트 없이 가상환경만 하나" 필요할 때가 있죠.

```bash
$ uv venv --python 3.12 myenv
Using CPython 3.12.10
Creating virtual environment at: myenv
Activate with: source myenv/bin/activate
```

이름을 생략하면 `.venv`에 만듭니다. Windows에서는 활성화 명령이 `myenv\Scripts\activate`예요. 이미 있는 가상환경을 비우고 새로 만들려면 `--clear`를 붙입니다.

한 가지 알아 둘 점이 있습니다. **uv가 만든 가상환경에는 pip가 들어 있지 않습니다.**

```bash
$ uv run python -m pip --version
.../.venv/bin/python3: No module named pip
```

고장 난 게 아니라 uv가 pip 역할을 하니 일부러 넣지 않은 거예요. 패키지는 `uv add`나 다음 절의 `uv pip install`로 넣으세요.

## A.10 pip와 같은 방식으로: uv pip

`requirements.txt`로 관리하는 오래된 프로젝트나, pip 명령에 익숙한 팀과 일할 때는 `uv pip`을 씁니다. pip와 거의 같은 명령을 훨씬 빠르게 실행해 줘요.

| pip | uv pip |
|---|---|
| `pip install requests` | `uv pip install requests` |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `pip install -e .` | `uv pip install -e .` |
| `pip uninstall requests` | `uv pip uninstall requests` |
| `pip list` | `uv pip list` |
| `pip freeze` | `uv pip freeze` |
| `pip show requests` | `uv pip show requests` |
| `pip-compile requirements.in` | `uv pip compile requirements.in` |
| `pip-sync requirements.txt` | `uv pip sync requirements.txt` |

`uv pip`은 지금 폴더의 `.venv`(또는 활성화된 가상환경)에 설치합니다. 다른 환경을 가리키려면 `--python`으로 그 환경을 줍니다.

```bash
$ uv pip install --python myenv requests
 + requests==2.34.2
 + urllib3==2.8.0
$ uv pip freeze --python myenv
Using Python 3.12.10 environment at: myenv
certifi==2026.10.19
charset-normalizer==3.5.2
...
```

주의할 점은 `uv pip install`은 **`pyproject.toml`과 `uv.lock`을 건드리지 않는다**는 것입니다. 프로젝트(`uv init`으로 만든 폴더)에서 `uv pip install`로 넣은 패키지는 다음 `uv sync`나 `uv run` 때 목록에 없다는 이유로 지워질 수 있어요. 프로젝트에서는 `uv add`, 프로젝트가 아닌 곳에서는 `uv pip`. 이렇게 나눠 쓰세요.

## A.11 빌드와 배포: uv build, uv publish

### 버전 올리기: uv version

배포하기 전에는 버전 번호를 올려야 합니다. `pyproject.toml`을 손으로 고쳐도 되지만 `uv version`이 편합니다.

```bash
$ uv version
hello 0.1.0
$ uv version --bump minor
hello 0.1.0 => 0.2.0
```

`--bump`에는 `major`(1.0.0 → 2.0.0), `minor`(0.1.0 → 0.2.0), `patch`(0.1.0 → 0.1.1)를 줄 수 있습니다.

### uv build

`--package`로 만든 프로젝트에서 `uv build`를 실행하면 `dist/` 폴더에 두 파일이 생깁니다.

```bash
$ uv build
Building source distribution (uv build backend)...
Building wheel from source distribution (uv build backend)...
Successfully built dist/mypkg-0.1.0.tar.gz
Successfully built dist/mypkg-0.1.0-py3-none-any.whl
```

`.tar.gz`는 소스 배포본(sdist), `.whl`은 바로 설치할 수 있는 휠입니다. 결과물 폴더를 바꾸려면 `--out-dir`(`-o`), 소스 배포본이나 휠 하나만 만들려면 `--sdist`, `--wheel`을 씁니다. 만든 휠은 올리기 전에 `uv pip install dist/mypkg-0.1.0-py3-none-any.whl`로 설치해 보는 것이 좋아요.

### uv publish

`uv publish`는 `dist/`의 파일을 PyPI에 올립니다. 실제로 올리기 전에 `--dry-run`으로 무엇이 올라갈지 먼저 확인할 수 있어요.

```bash
$ uv publish --dry-run --publish-url https://test.pypi.org/legacy/ --token 토큰
Checking 2 files against https://test.pypi.org/legacy/
Checking mypkg-0.1.0-py3-none-any.whl (1.4KiB)
Checking mypkg-0.1.0.tar.gz (592.0B)
```

자주 쓰는 옵션은 이렇습니다(uv 0.9.16의 `uv publish --help`로 확인).

| 옵션 | 뜻 |
|---|---|
| `--token`, `-t` | PyPI API 토큰. 환경 변수 `UV_PUBLISH_TOKEN`으로도 줄 수 있음 |
| `--username`, `-u` / `--password`, `-p` | 아이디와 비밀번호(토큰을 쓸 때는 사용자 이름 `__token__`) |
| `--publish-url` | 올릴 주소. 내려받는 주소(`/simple/`)가 아니라 **업로드 주소**(`/legacy/`) |
| `--index 이름` | `pyproject.toml`에 이름 붙여 둔 저장소로 올리기 |
| `--trusted-publishing` | GitHub Actions 같은 CI에서 토큰 없이 인증 |
| `--check-url` | 이미 올라간 파일이면 건너뛰도록 확인할 주소 |
| `--dry-run` | 실제로 올리지 않고 확인만 |

토큰은 명령에 직접 쓰면 셸 기록에 남습니다. 환경 변수로 주거나, 14장의 GitHub Actions 예제처럼 CI의 비밀 저장소에서 꺼내 쓰세요.

연습용 TestPyPI를 자주 쓴다면 `pyproject.toml`에 이름을 붙여 두면 편합니다.

```toml
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true
```

```bash
uv publish --index testpypi
```

`explicit = true`는 "평소 패키지를 받을 때는 이 저장소를 쓰지 말라"는 뜻입니다. 이게 없으면 다른 패키지까지 TestPyPI에서 받으려고 할 수 있어요.

> 한 번 올린 버전 번호는 지워도 다시 쓸 수 없습니다. 실수로 올렸다면 `uv version --bump patch`로 번호를 올려서 다시 올려야 해요. 그래서 처음에는 꼭 TestPyPI에서 연습하세요.

## A.12 자주 하는 실수

**1. `uv pip install`로 넣었는데 다음 실행 때 사라져요.**
프로젝트에서는 `uv add`를 써야 목록에 남습니다. `uv run`과 `uv sync`는 목록에 없는 패키지를 지웁니다(A.7절).

**2. `uv add`를 했더니 "No `pyproject.toml` found"가 나와요.**

```text
error: No `pyproject.toml` found in current directory or any parent directory
```

프로젝트 폴더 밖에서 실행했거나 아직 프로젝트를 만들지 않은 것입니다. `cd`로 프로젝트 폴더에 들어가거나 `uv init`부터 하세요. 스크립트 하나라면 `uv add --script 파일.py 패키지`를 씁니다.

**3. `pip install`을 했더니 엉뚱한 파이썬에 설치돼요.**
uv의 `.venv`에는 pip가 없어서, 터미널의 `pip`는 컴퓨터에 원래 깔린 다른 파이썬의 pip일 가능성이 큽니다. 이 책에서 `pip install` 대신 `uv add`를 쓰는 이유이기도 해요.

**4. `python main.py`로 실행하니 `ModuleNotFoundError`가 나와요.**
`uv add`로 설치한 라이브러리는 프로젝트의 `.venv`에 있습니다. 활성화하지 않은 상태의 `python`은 그 환경을 모르죠. `uv run python main.py`로 실행하세요(부록 D의 ModuleNotFoundError 항목도 참고).

**5. 그냥 `uv sync`를 했더니 선택 의존성이 지워졌어요.**
`--extra 이름`이나 `--all-extras`를 함께 줘야 합니다. 묶음(group)도 `dev` 말고는 `--group 이름`이 필요해요.

**6. 프로젝트 폴더에서 `uv run --python 3.13`을 했더니 매번 가상환경을 다시 만들어요.**
`.python-version`과 다른 버전을 주면 프로젝트 환경 자체를 그 버전으로 바꿉니다. 잠깐 시험할 때는 `--no-project`를 붙이세요(A.6절).

**7. `uv.lock`을 `.gitignore`에 넣었어요.**
빼세요. 잠금 파일은 커밋해야 다른 사람도 같은 버전을 받습니다. 반대로 `.venv` 폴더는 커밋하지 않습니다(`uv init`이 만든 `.gitignore`에 이미 들어 있어요).

**8. `uv publish`에 `/simple/` 주소를 줬어요.**
`--publish-url`은 업로드 주소인 `https://test.pypi.org/legacy/`처럼 `/legacy/`로 끝나는 주소입니다. `/simple/`은 패키지를 내려받을 때 쓰는 주소예요.

## A.13 명령 한눈에 보기

| 하고 싶은 일 | 명령 |
|---|---|
| 새 프로젝트 | `uv init 이름`, `uv init --package 이름` |
| 파이썬 버전 설치·고정 | `uv python install 3.12`, `uv python pin 3.12` |
| 라이브러리 추가·제거 | `uv add 패키지`, `uv remove 패키지` |
| 개발용 추가 | `uv add --dev pytest` |
| 실행 | `uv run 파일.py`, `uv run pytest` |
| 임시로 빌려 실행 | `uv run --with 패키지 ...` |
| 받은 프로젝트 설치 | `uv sync` |
| 의존성 업그레이드 | `uv lock --upgrade` 후 `uv sync` |
| 의존성 구조 보기 | `uv tree` |
| 도구 한 번 실행 | `uvx 도구` |
| 도구 설치 | `uv tool install 도구` |
| requirements.txt 뽑기 | `uv export --format requirements.txt` |
| 버전 올리기 | `uv version --bump patch` |
| 빌드·배포 | `uv build`, `uv publish` |
| uv 업데이트 | `uv self update` |

명령마다 `--help`를 붙이면 그 버전에서 쓸 수 있는 모든 옵션이 나옵니다. 이 부록에 없는 옵션이 궁금하면 `uv add --help`처럼 직접 물어보세요.
