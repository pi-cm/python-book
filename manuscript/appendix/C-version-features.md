# 부록 C. 버전별 새 기능 (3.8~3.14)

파이썬은 해마다 10월쯤 새 버전이 나옵니다. 인터넷에서 찾은 코드가 내 컴퓨터에서 `SyntaxError`를 낸다면, 코드가 틀린 게 아니라 내 파이썬이 그 문법보다 오래된 것일 수 있어요. 3장에서 바다코끼리 연산자를 "신입 캐릭터"라고 불렀죠? 이 부록은 버전마다 어떤 신입이 들어왔는지 정리한 명단입니다. 남의 코드를 읽다가 낯선 문법을 만났을 때, 또는 "이 기능은 몇 버전부터 쓸 수 있지?"가 궁금할 때 펼쳐 보세요.

모든 항목은 파이썬 공식 문서의 "What's New in Python 3.x"로 확인했습니다. 문법 예제는 부록 A에서 소개한 `uv run --python 3.x`로 **그 버전에서 실제로 실행**했고, 3.9 이후 항목은 바로 앞 버전에서 실행해 오류가 나는 것까지 확인했어요. 사용한 버전은 3.8.20, 3.9.6, 3.10.17, 3.11.12, 3.12.10, 3.13.11, 3.14.2입니다. 이 책의 기준은 3.12이므로 3.12까지의 기능은 본문 예제에서 모두 쓸 수 있습니다.

```bash
# 특정 버전으로 한 줄 실행해 보기 (프로젝트 밖에서)
uv run --no-project --python 3.10 python -c "print(int | str)"
```

---

## C.1 한눈에 보기

| 버전 | 나온 해 | 가장 눈에 띄는 변화 |
|---|---|---|
| 3.8 | 2019 | 바다코끼리 연산자 `:=`, 위치 전용 매개변수 `/`, f-string `=` |
| 3.9 | 2020 | 딕셔너리 합치기 \|, `removeprefix`, `list[int]`, `zoneinfo` |
| 3.10 | 2021 | `match`-`case`, 타입 `X` \| `Y`, 훨씬 친절한 `SyntaxError` |
| 3.11 | 2022 | 평균 1.25배 빨라짐, `ExceptionGroup`·`except*`, `tomllib`, 오류 위치 표시 |
| 3.12 | 2023 | f-string 제약 해제, `type` 문, 제네릭 새 문법, "import 잊었나요?" 안내 |
| 3.13 | 2024 | 새 대화형 셸(REPL), GIL 없는 실험 빌드, JIT 실험 |
| 3.14 | 2025 | t-string, 괄호 없는 `except A, B`, 미뤄 읽는 타입 힌트 |

## C.2 Python 3.8

3.8의 주인공은 3장에서 만난 바다코끼리 연산자입니다. 값을 변수에 담으면서 동시에 그 값을 식에서 쓸 수 있게 해 줘요.

| 기능 | 예 | 이 책에서 다룬 장 |
|---|---|---|
| 바다코끼리 연산자 `:=` (PEP 572) | `if (n := len(s)) > 3:` | 3장 3.3 |
| 위치 전용 매개변수 `/` (PEP 570) | `def f(a, /, b):` | 부록 B.10 |
| f-string 디버깅 `=` | `f"{x=}"` → `x=3` | 부록 B.4 |
| `typing.Literal`, `Final`, `TypedDict`, `Protocol` | `Literal["대기", "완료"]` | 2장 2.3 |
| `functools.cached_property` | 한 번 계산한 속성 값을 저장 | — |
| `math.prod`, `math.isqrt` | `math.prod([2, 3, 4])` → `24` | — |

```python
# Python 3.8 이상
data = [3, 8, 1, 9]
if (n := len(data)) > 3:
    print(f"원소가 {n}개라 너무 많아요")  # 원소가 4개라 너무 많아요

def divide(a, b, /):          # a, b는 위치로만 넘길 수 있음
    return a / b
print(divide(6, 3))           # 2.0

x, items = 3, ["a", "b"]
print(f"{x=}, {len(items)=}")  # x=3, len(items)=2

import math
print(math.prod([2, 3, 4]), math.isqrt(10))  # 24 3
```

`divide(a=6, b=3)`처럼 이름을 붙여 부르면 `TypeError`가 납니다. 매개변수 이름을 나중에 바꿔도 부르는 쪽 코드가 깨지지 않게 하려고 쓰는 장치예요. 내장 함수 중에도 `len(obj, /)`처럼 이렇게 정의된 것이 많습니다.

## C.3 Python 3.9

3.9는 "자주 쓰던 우회로를 정식 길로" 바꾼 버전입니다. 딕셔너리를 합치려고 `{**a, **b}`를 쓰거나, 접두사를 떼려고 슬라이싱을 계산하던 수고가 줄었어요.

| 기능 | 예 | 이 책에서 다룬 장 |
|---|---|---|
| 딕셔너리 합치기 \|, \|`=` (PEP 584) | `a` \| `b` | 부록 B.8 |
| `str.removeprefix`, `removesuffix` (PEP 616) | `"test.py".removesuffix(".py")` | 부록 B.3 |
| 내장 자료형으로 타입 힌트 (PEP 585) | `list[int]`, `dict[str, int]` | 2장 2.3 |
| `zoneinfo` 모듈 (PEP 615) | `ZoneInfo("Asia/Seoul")` | 17장 |
| `functools.cache` | 크기 제한 없는 메모 캐시 | 16장, 부록 B.10 |
| `math.lcm`, 여러 인자 `math.gcd` | `math.lcm(4, 6)` → `12` | — |
| 새 PEG 파서 | 이후 문법 추가의 바탕 | — |

```python
# Python 3.9 이상
defaults = {"theme": "light", "lang": "ko"}
user = {"theme": "dark"}
print(defaults | user)                # {'theme': 'dark', 'lang': 'ko'}

print("unhappy".removeprefix("un"))   # happy
print("report.csv".removesuffix(".csv"))  # report

def total(scores: dict[str, list[int]]) -> dict[str, int]:
    return {name: sum(s) for name, s in scores.items()}
print(total({"민수": [90, 80]}))       # {'민수': 170}

from zoneinfo import ZoneInfo
from datetime import datetime
seoul = datetime(2026, 10, 21, 9, 0, tzinfo=ZoneInfo("Asia/Seoul"))
print(seoul.astimezone(ZoneInfo("UTC")))  # 2026-10-21 00:00:00+00:00
```

`removeprefix`는 `lstrip`과 다릅니다. `"unhappy".lstrip("un")`은 앞에서부터 `u`나 `n`인 글자를 **모두** 지워서 `'happy'`가 되지만, `"nun".lstrip("un")`은 `''`가 돼요. `removeprefix`는 정확히 그 문자열 하나만 뗍니다. 3.8에서 `defaults | user`를 실행하면 `TypeError: unsupported operand type(s) for |: 'dict' and 'dict'`가 나옵니다.

## C.4 Python 3.10

3.10은 4장의 주인공 `match`-`case`가 들어온 버전입니다. 그리고 초보자에게 정말 고마운 변화가 하나 더 있는데, 바로 **오류 메시지가 친절해졌다**는 거예요.

| 기능 | 예 | 이 책에서 다룬 장 |
|---|---|---|
| 구조적 패턴 매칭 `match`-`case` (PEP 634) | `case [x, y]:` | 4장 4.2, 2장 2.4 |
| 타입 합치기 `X` \| `Y` (PEP 604) | `int` \| `None` | 2장 2.3 |
| 괄호로 묶는 여러 `with` | `with (open(a) as f, open(b) as g):` | — |
| `zip(..., strict=True)` (PEP 618) | 길이가 다르면 `ValueError` | 부록 B.6 |
| `itertools.pairwise` | `pairwise("abc")` → `ab`, `bc` | 부록 B.16 |
| `int.bit_count()` | `(255).bit_count()` → `8` | — |
| `@dataclass(slots=True, kw_only=True)` | | — |
| 더 정확한 `SyntaxError` 위치와 설명 | `'{' was never closed` | 부록 D |

```python
# Python 3.10 이상
def http_status(code: int | None) -> str:
    match code:
        case 200 | 201:
            return "성공"
        case 404:
            return "없음"
        case int(c) if 500 <= c < 600:
            return "서버 오류"
        case None:
            return "응답 없음"
        case _:
            return "기타"

print(http_status(201), http_status(503), http_status(None))  # 성공 서버 오류 응답 없음

import io
with (
    io.StringIO("첫째") as a,
    io.StringIO("둘째") as b,
):
    print(a.read(), b.read())     # 첫째 둘째

print(list(zip("ab", [1, 2], strict=True)))  # [('a', 1), ('b', 2)]
```

괄호로 묶는 `with`는 3.10에서 공식 문법이 됐습니다. 실제로는 3.9의 새 파서에서도 동작하지만 3.9 문서에는 없는 기능이라, 3.9를 지원해야 하는 코드라면 쓰지 않는 편이 안전해요.

오류 메시지가 얼마나 달라졌는지 직접 비교해 볼까요? 콜론을 빠뜨린 `if True` 다음 줄에 `print(1)`을 쓴 파일을 두 버전에서 실행한 결과입니다.

```text
# Python 3.9
SyntaxError: invalid syntax

# Python 3.10
SyntaxError: expected ':'
```

닫지 않은 중괄호도 3.9는 `unexpected EOF while parsing`(파일이 갑자기 끝났다)라고만 했지만, 3.10은 `'{' was never closed`라고 원인을 짚어 줍니다.

## C.5 Python 3.11

3.11의 가장 큰 뉴스는 **속도**입니다. 공식 문서에 따르면 3.10보다 10~60% 빨라졌고, 표준 벤치마크에서 평균 1.25배 빨라졌어요. 코드를 한 줄도 안 고쳤는데 버전만 올려서 빨라진 거죠. 오류 메시지는 이번에도 좋아져서, 한 줄 안에서 **정확히 어느 부분**이 문제인지 `^` 표시로 짚어 줍니다.

| 기능 | 예 | 이 책에서 다룬 장 |
|---|---|---|
| 속도 향상 (Faster CPython) | 평균 1.25배 | — |
| 오류 위치를 `~~~^^^`로 표시 (PEP 657) | 아래 예 | 부록 D |
| `ExceptionGroup`, `except*` (PEP 654) | 여러 예외를 한꺼번에 | — |
| 예외에 메모 붙이기 `add_note()` | `e.add_note("설명")` | — |
| `tomllib` (PEP 680) | TOML 읽기 (`pyproject.toml` 등) | — |
| `asyncio.TaskGroup` | 작업 묶어 실행 | 부록 B.17 |
| `typing.Self` (PEP 673) | 자기 클래스를 돌려주는 메서드 | — |
| `enum.StrEnum` | 문자열처럼 쓰는 열거형 | — |

```python
# Python 3.11 이상
import tomllib
config = tomllib.loads('''
name = "my-app"
[server]
port = 8000
''')
print(config["server"]["port"])   # 8000

def check(values):
    errors = []
    for v in values:
        try:
            int(v)
        except ValueError as e:
            e.add_note(f"입력값: {v!r}")
            errors.append(e)
    if errors:
        raise ExceptionGroup("검사 실패", errors)

try:
    check(["1", "x", "2.5"])
except* ValueError as group:
    for e in group.exceptions:
        print(e.__notes__[0])     # 입력값: 'x' / 입력값: '2.5'
```

`ExceptionGroup`은 여러 작업을 동시에 돌리다가 **여러 개가 한꺼번에 실패**했을 때 그 예외들을 한 묶음으로 던지는 방법입니다. `except*`는 그 묶음에서 원하는 종류만 골라 잡아요. `asyncio.TaskGroup` 안의 작업이 실패하면 바로 이 `ExceptionGroup`이 올라옵니다.

`tomllib`은 읽기만 합니다. TOML 파일을 쓰려면 외부 라이브러리가 필요해요. 파일에서 읽을 때는 `open(경로, "rb")`처럼 **바이너리 모드**로 열어서 `tomllib.load()`에 넘깁니다.

오류 위치 표시는 이렇게 달라졌습니다. `data = {"a": {"b": None}}`에서 `data["a"]["b"]["c"]`를 읽으면 3.10은 줄만 알려 주지만, 3.11은 그 줄의 어느 대괄호가 문제인지 밑줄을 그어 줘요.

```text
# Python 3.11
    print(data["a"]["b"]["c"])
          ~~~~~~~~~~~~~~^^^^^
TypeError: 'NoneType' object is not subscriptable
```

`~~~` 부분(`data["a"]["b"]`)이 `None`이었고, 거기에 `^^^`의 `["c"]`를 하려다 실패했다는 뜻입니다.

## C.6 Python 3.12

3.12는 이 책의 기준 버전입니다. f-string 안에서 쓸 수 없던 것들이 풀렸고, 타입에 별명을 붙이거나 제네릭 함수를 만드는 문법이 아주 짧아졌어요.

| 기능 | 예 | 이 책에서 다룬 장 |
|---|---|---|
| f-string 문법 정식화 (PEP 701) | `f"{d["k"]}"`, 식 안에 `\n` | 부록 B.4 |
| `type` 문 (PEP 695) | `type Point = tuple[float, float]` | 2장(소프트 키워드), 부록 B.18 |
| 제네릭 새 문법 (PEP 695) | `def first[T](xs: list[T]) -> T:` | — |
| `typing.override` (PEP 698) | 부모 메서드를 덮어쓴다고 표시 | — |
| `itertools.batched` | `batched("abcde", 2)` | 부록 B.16 |
| `pathlib.Path.walk()` | 폴더를 아래로 훑기 | — |
| 오류 메시지 개선 | `Did you forget to import 'sys'?` | 부록 D |
| `distutils` 제거 (PEP 632) | `setuptools`나 uv를 쓸 것 | 14장 |

```python
# Python 3.12 이상
songs = ["봄", "여름"]
info = {"title": "계절"}
print(f"{info["title"]}: {", ".join(songs)}")  # 계절: 봄, 여름
print(f"{"\n".join(songs)!r}")                 # '봄\n여름'

type Point = tuple[float, float]
type Pair[T] = tuple[T, T]
print(Point.__value__)            # tuple[float, float]

def first[T](items: list[T]) -> T:
    return items[0]

class Box[T]:
    def __init__(self, value: T):
        self.value = value

print(first([10, 20]), Box("상자").value)  # 10 상자

from itertools import batched
print(list(batched("abcde", 2)))  # [('a', 'b'), ('c', 'd'), ('e',)]
```

3.11까지는 f-string의 `{}` 안에 바깥과 같은 따옴표를 쓰거나 역슬래시를 쓸 수 없었습니다. 첫 줄의 `info["title"]`이 3.11에서는 바로 `SyntaxError`예요. 3.12부터는 `{}` 안을 보통 파이썬 식과 똑같이 읽습니다.

`def first[T]`의 `[T]`는 "아무 타입이나 들어올 수 있는데, 들어온 타입을 `T`라고 부르겠다"는 뜻입니다. 예전에는 `T = TypeVar("T")`를 따로 선언하고 `Generic[T]`를 상속해야 했어요(2장, 13장의 예제가 그 방식입니다). 두 방식 모두 3.12에서 동작합니다.

오류 메시지는 이렇게 바뀌었습니다.

```text
# 3.11: import 없이 sys.version
NameError: name 'sys' is not defined
# 3.12
NameError: name 'sys' is not defined. Did you forget to import 'sys'?

# 3.11: from collections import chainmap
ImportError: cannot import name 'chainmap' from 'collections' (...)
# 3.12
ImportError: cannot import name 'chainmap' from 'collections' (...). Did you mean: 'ChainMap'?
```

## C.7 Python 3.13

3.13은 문법보다 **실행 환경**이 크게 바뀐 버전입니다. 터미널에서 `python`만 쳤을 때 나오는 대화형 셸이 새로 만들어졌고, 앞으로의 큰 변화 두 가지(GIL 없는 파이썬, JIT)가 실험 단계로 들어왔어요.

| 기능 | 내용 | 이 책에서 다룬 장 |
|---|---|---|
| 새 대화형 셸(REPL) | 여러 줄 편집, 색깔, F1 도움말, F2 기록, F3 붙여넣기 모드, `exit`만 쳐도 종료 | — |
| GIL 없는 실험 빌드 (PEP 703) | 별도 실행 파일 `python3.13t`, 스레드가 진짜로 동시에 실행 | 15장(GIL 설명) |
| JIT 컴파일러 실험 (PEP 744) | 기본은 꺼져 있고, 성능 향상은 아직 작음 | — |
| 색깔 있는 트레이스백 | 오류 출력에 색 (`NO_COLOR`로 끄기) | — |
| 오류 메시지 개선 | 키워드 인자 오타 추천, 표준 모듈과 같은 파일 이름 경고 | 14장, 부록 D |
| `copy.replace()` | 일부 값만 바꾼 복사본 | — |
| `warnings.deprecated` (PEP 702) | "곧 없어질 함수" 표시 | — |
| `locals()` 동작 정의 (PEP 667) | 함수 안 `locals()`는 독립된 스냅숏 | — |
| 오래된 모듈 19개 제거 (PEP 594) | `cgi`, `telnetlib`, `imghdr`, `crypt` 등 | — |

```python
# Python 3.13 이상
import copy
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    theme: str
    size: int

base = Settings("light", 12)
print(copy.replace(base, size=14))   # Settings(theme='light', size=14)

import sys
print(sys._is_gil_enabled())         # True
```

`frozen=True`인 데이터 클래스는 값을 바꿀 수 없으니, 일부만 바꾸고 싶으면 새로 만들어야 하죠. `copy.replace()`가 그 일을 한 줄로 해 줍니다.

마지막 줄의 `True`는 보통 빌드라서 GIL이 켜져 있다는 뜻입니다. **GIL**(전역 인터프리터 잠금)은 한 번에 스레드 하나만 파이썬 코드를 실행하게 하는 자물쇠예요(15장). uv로 GIL 없는 빌드를 받아서 확인해 보면 `False`가 나옵니다.

```bash
$ uv run --no-project --python 3.13t python -c "import sys; print(sys._is_gil_enabled())"
False
```

키워드 인자 오타와 파일 이름 충돌 안내는 실제로 이렇게 나옵니다.

```text
# 3.12: "a b".split(max_split=1)
TypeError: 'max_split' is an invalid keyword argument for split()
# 3.13
TypeError: split() got an unexpected keyword argument 'max_split'. Did you mean 'maxsplit'?

# 3.13: random.py라는 파일 안에서 import random 후 random.randint(1, 6)
AttributeError: module 'random' has no attribute 'randint' (consider renaming
'.../random.py' since it has the same name as the standard library module named
'random' and prevents importing that standard library module)
```

같은 실수를 3.12에서 하면 `partially initialized module 'random' has no attribute 'randint' (most likely due to a circular import)`라고만 나옵니다. 14장에서 본 그 메시지예요. 3.13은 "파일 이름을 바꾸라"고 해결책까지 알려 줍니다.

## C.8 Python 3.14 (맛보기)

이 책을 쓰는 지금 3.14도 나와 있습니다. 이 머신에서 uv로 받은 3.14.2로 확인한 것만 짧게 소개할게요.

| 기능 | 예 |
|---|---|
| t-string, 템플릿 문자열 (PEP 750) | `t"안녕, {name}!"` → 문자열이 아니라 `Template` 객체 |
| 괄호 없는 여러 예외 (PEP 758) | `except ValueError, TypeError:` |
| 타입 힌트를 나중에 읽기 (PEP 649, 749) | 아직 정의 안 된 클래스 이름을 힌트에 바로 써도 됨 |
| `finally` 안의 `return` 경고 (PEP 765) | `SyntaxWarning: 'return' in a 'finally' block` |
| GIL 없는 빌드 공식 지원 (PEP 779) | 실험 단계에서 졸업 |
| `compression.zstd` (PEP 784) | Zstandard 압축 |
| `uuid.uuid7()` | 시간순으로 정렬되는 UUID |
| REPL 문법 색칠 | 입력하는 코드에 색 |

```python
# Python 3.14 이상
name = "민수"
t = t"안녕, {name}!"
print(type(t).__name__, t.strings, t.values)   # Template ('안녕, ', '!') ('민수',)

try:
    int("x")
except ValueError, TypeError:
    print("둘 중 하나를 잡음")                   # 둘 중 하나를 잡음

class Node:
    def link(self, other: Node) -> Node:       # 3.13까지는 NameError
        return other
print("정의 OK")                                # 정의 OK
```

t-string은 f-string과 모양이 같지만 바로 문자열로 합치지 않고, 고정된 글자 부분(`strings`)과 끼워 넣을 값(`values`)을 따로 들고 있습니다. 그래서 값을 넣기 전에 HTML 특수 문자를 바꾸거나 SQL에 안전하게 넣는 식으로 **끼워 넣는 방법을 직접 정할 수** 있어요. 19장의 보안 절에서 말한 "입력은 믿지 않는다"를 문법으로 돕는 기능입니다.

`class Node` 예제는 3.13에서 실행하면 `NameError: name 'Node' is not defined. Did you mean: 'None'?`이 납니다. 클래스를 정의하는 도중에는 아직 `Node`라는 이름이 없기 때문이에요. 3.14부터는 타입 힌트를 필요할 때까지 읽지 않고 미뤄 두어서 이 문제가 사라졌습니다.

## C.9 이 책의 코드를 다른 버전에서 돌릴 때

이 책은 3.12를 기준으로 썼습니다. 그보다 낮은 버전에서 본문 예제를 돌리면 다음 부분에서 막힐 수 있어요.

| 이런 코드가 있으면 | 최소 버전 | 낮은 버전에서 나는 오류 |
|---|---|---|
| `match`, `case` | 3.10 | `SyntaxError: invalid syntax` |
| `int` \| `None` 같은 타입 힌트 | 3.10 | `TypeError: unsupported operand type(s)` ... |
| `list[int]`, `dict[str, int]` 힌트 | 3.9 | `TypeError: 'type' object is not subscriptable` |
| `tomllib`, `asyncio.TaskGroup` | 3.11 | `ModuleNotFoundError`, `AttributeError` |
| f-string `{}` 안의 같은 따옴표 | 3.12 | `SyntaxError` |
| `type X = ...`, `def f[T]()` | 3.12 | `SyntaxError` |
| `itertools.batched` | 3.12 | `ImportError` |

해결책은 간단합니다. 버전을 올리면 돼요. uv를 쓰면 다른 프로젝트에 영향을 주지 않고 프로젝트마다 버전을 고를 수 있습니다.

```bash
uv python pin 3.12      # 이 프로젝트는 3.12로
uv run python main.py
```

반대로 내가 만든 패키지를 여러 버전에서 쓰게 하려면 `pyproject.toml`의 `requires-python`을 낮추고, 그 버전에 없는 문법을 쓰지 않아야 합니다. 14장의 GitHub Actions 예제가 3.10, 3.11, 3.12 세 버전에서 테스트를 돌리는 것도 그래서예요.
