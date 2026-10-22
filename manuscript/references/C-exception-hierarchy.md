# 레퍼런스 C. 예외 계층

`except` 뒤에 무엇을 적어야 할지, 이 예외가 저 예외에 포함되는지 헷갈릴 때 펼쳐 보세요. `except LookupError`는 `IndexError`와 `KeyError`를 함께 잡고, `except Exception`은 `KeyboardInterrupt`를 잡지 못합니다. 이런 관계가 모두 아래 트리에 있습니다. 예외 처리의 기본 문법은 12장에서 다뤘습니다.

## 내장 예외 트리

Python 3.12의 내장 예외 67개를 `BaseException`부터 `__subclasses__()`로 순회해 만든 트리입니다. 같은 부모 아래는 이름순이에요.

```text
BaseException
├── BaseExceptionGroup
│   └── ExceptionGroup  [+Exception]
├── Exception
│   ├── ArithmeticError
│   │   ├── FloatingPointError
│   │   ├── OverflowError
│   │   └── ZeroDivisionError
│   ├── AssertionError
│   ├── AttributeError
│   ├── BufferError
│   ├── EOFError
│   ├── ImportError
│   │   └── ModuleNotFoundError
│   ├── LookupError
│   │   ├── IndexError
│   │   └── KeyError
│   ├── MemoryError
│   ├── NameError
│   │   └── UnboundLocalError
│   ├── OSError
│   │   ├── BlockingIOError
│   │   ├── ChildProcessError
│   │   ├── ConnectionError
│   │   │   ├── BrokenPipeError
│   │   │   ├── ConnectionAbortedError
│   │   │   ├── ConnectionRefusedError
│   │   │   └── ConnectionResetError
│   │   ├── FileExistsError
│   │   ├── FileNotFoundError
│   │   ├── InterruptedError
│   │   ├── IsADirectoryError
│   │   ├── NotADirectoryError
│   │   ├── PermissionError
│   │   ├── ProcessLookupError
│   │   └── TimeoutError
│   ├── ReferenceError
│   ├── RuntimeError
│   │   ├── NotImplementedError
│   │   └── RecursionError
│   ├── StopAsyncIteration
│   ├── StopIteration
│   ├── SyntaxError
│   │   └── IndentationError
│   │       └── TabError
│   ├── SystemError
│   ├── TypeError
│   ├── ValueError
│   │   └── UnicodeError
│   │       ├── UnicodeDecodeError
│   │       ├── UnicodeEncodeError
│   │       └── UnicodeTranslateError
│   └── Warning
│       ├── BytesWarning
│       ├── DeprecationWarning
│       ├── EncodingWarning
│       ├── FutureWarning
│       ├── ImportWarning
│       ├── PendingDeprecationWarning
│       ├── ResourceWarning
│       ├── RuntimeWarning
│       ├── SyntaxWarning
│       ├── UnicodeWarning
│       └── UserWarning
├── GeneratorExit
├── KeyboardInterrupt
└── SystemExit
```

### 트리 읽는 법

- **`except 부모`는 자식까지 모두 잡습니다.** `except OSError`는 `FileNotFoundError`, `PermissionError`, `ConnectionError` 계열을 다 잡아요.
- **`Exception` 밖의 넷**(`BaseExceptionGroup`, `GeneratorExit`, `KeyboardInterrupt`, `SystemExit`)은 `except Exception`에 걸리지 않습니다. Ctrl+C와 `sys.exit()`가 엉뚱하게 삼켜지지 않게 하려는 설계예요. 그래서 "모든 오류를 잡고 싶다"면 `except BaseException`이 아니라 `except Exception`을 씁니다.
- `[+Exception]`은 다중 상속 표시입니다. `ExceptionGroup`은 `BaseExceptionGroup`과 `Exception`을 함께 상속해서 `except Exception`에도 걸립니다.
- `IOError`와 `EnvironmentError`는 `OSError`의 옛 이름입니다. `IOError is OSError`가 `True`라서 트리에 따로 나오지 않아요. 그래서 이름은 69개지만 클래스는 67개입니다.
- 표준 라이브러리 예외도 이 트리에 붙습니다. 예를 들어 `json.JSONDecodeError`는 `ValueError`의 하위라서 `except ValueError`로 잡힙니다.

직접 트리를 찍어 보고 싶다면 이렇게 하면 됩니다. `ExceptionGroup`은 부모가 둘이라 두 번 나옵니다.

```python
def show(cls, depth=0):
    print('    ' * depth + cls.__name__)
    for sub in sorted(cls.__subclasses__(), key=lambda c: c.__name__):
        if sub.__module__ == 'builtins':
            show(sub, depth + 1)

show(BaseException)
```

## 자주 만나는 예외

재현 코드는 모두 Python 3.12에서 실행해 그 예외가 정확히 나는지 확인했습니다. `PermissionError`와 `IsADirectoryError`는 맥·리눅스 기준이고, 윈도에서는 다른 `OSError`가 날 수 있어요. `UnboundLocalError`는 바깥에 `x = 0`이 있는 상태에서 `f()`를, `RecursionError`는 `f()`를, `RuntimeError`는 `d = {1: 1}`인 상태에서 실행한 결과입니다.

| 예외 | 언제 나나 | 최소 재현 코드 | 해결 방향 |
|---|---|---|---|
| `SyntaxError` | 문법이 틀려 코드를 읽을 수조차 없을 때. 실행 전에 납니다. | `eval('1 +')` | 오류 메시지의 `^` 위치와 그 앞 줄의 괄호·따옴표·콜론을 확인합니다. |
| `IndentationError` | 들여쓰기가 맞지 않을 때(`SyntaxError`의 하위). | `exec('if True:\nprint(1)')` | 블록 안은 같은 칸(보통 공백 4칸)으로 맞춥니다. |
| `NameError` | 정의하지 않은(또는 오타 난) 이름을 쓸 때. | `print(undefined_name)` | 철자, 정의 순서, `import` 누락을 확인합니다. |
| `UnboundLocalError` | 함수 안에서 대입하는 변수를 대입 전에 읽을 때(`NameError`의 하위). | `def f(): print(x); x = 1` | 바깥 변수를 바꾸려면 `global`/`nonlocal`을 선언하거나 인자로 넘깁니다. |
| `TypeError` | 연산·함수에 맞지 않는 타입을 넘기거나 인자 개수가 틀릴 때. | `'1' + 1` | `int()`, `str()`로 타입을 맞추고 함수 시그니처를 확인합니다. |
| `ValueError` | 타입은 맞지만 값이 허용 범위 밖일 때. | `int('abc')` | 입력을 검증하고 `try`/`except ValueError`로 감쌉니다. |
| `ZeroDivisionError` | 0으로 나눌 때(`/`, `//`, `%`). | `1 / 0` | 나누기 전에 0인지 검사합니다. |
| `IndexError` | 시퀀스의 범위를 벗어난 인덱스. | `[1, 2][5]` | `len()`으로 범위를 확인하거나 `for x in seq`로 순회합니다. |
| `KeyError` | 딕셔너리에 없는 키를 `d[key]`로 읽을 때. | `{'a': 1}['b']` | `d.get(key, 기본값)`이나 `key in d`를 씁니다. |
| `AttributeError` | 객체에 없는 속성·메서드를 쓸 때. `None`에서 자주 납니다. | `None.append(1)` | `None`이 들어온 경로를 찾고, `dir()`로 속성 이름을 확인합니다. |
| `ModuleNotFoundError` | 모듈을 찾지 못할 때(`ImportError`의 하위). | `import nopackage` | `uv add 패키지`로 설치했는지, 가상 환경이 맞는지 확인합니다. |
| `ImportError` | 모듈은 있는데 그 안에서 이름을 가져오지 못할 때. | `from math import nothing` | 가져올 이름의 철자, 순환 import 여부를 확인합니다. |
| `FileNotFoundError` | 없는 파일을 읽으려 할 때. | `open('없는파일.txt')` | `Path.exists()`로 확인하고, 상대 경로의 기준(현재 폴더)을 점검합니다. |
| `FileExistsError` | 이미 있는 파일·폴더를 새로 만들려 할 때. | `import os; os.mkdir('.')` | 폴더는 `Path.mkdir(exist_ok=True)`, 파일은 `'x'` 대신 `'w'` 모드를 씁니다. |
| `IsADirectoryError` | 폴더를 파일처럼 열 때(맥·리눅스). | `open('.')` | 경로가 파일을 가리키는지 `Path.is_file()`로 확인합니다. |
| `PermissionError` | 권한이 없는 파일에 쓰거나 읽을 때(맥·리눅스, 일반 사용자). | `open('/etc/passwd', 'a')` | 쓸 수 있는 위치(홈·프로젝트 폴더)로 경로를 바꿉니다. |
| `UnicodeDecodeError` | 바이트를 잘못된 인코딩으로 읽을 때. | `b'\xff'.decode('utf-8')` | `open(..., encoding='utf-8')`처럼 실제 인코딩을 명시합니다(윈도 파일은 `cp949`일 수 있음). |
| `UnicodeEncodeError` | 문자를 표현할 수 없는 인코딩으로 바꿀 때. | `'가'.encode('ascii')` | `utf-8`을 쓰거나 `errors='replace'`를 줍니다. |
| `StopIteration` | 다 쓴 반복자에서 `next()`를 부를 때. | `next(iter([]))` | `for`로 순회하거나 `next(it, 기본값)`을 씁니다. |
| `RecursionError` | 재귀가 너무 깊을 때(기본 한도 약 1000). | `def f(): return f()` | 종료 조건을 확인하고, 깊은 재귀는 반복문으로 바꿉니다. |
| `RuntimeError` | 다른 분류에 들지 않는 실행 중 오류. 예: 순회 중 딕셔너리 크기 변경. | `for k in d: d[k + 1] = 0` | `list(d)`처럼 복사본을 순회합니다. |
| `AssertionError` | `assert` 조건이 거짓일 때. | `assert 1 == 2, '다름'` | 가정이 깨진 지점을 찾습니다. 입력 검증에는 `assert` 대신 `raise ValueError`를 씁니다. |
| `OverflowError` | 실수 계산 결과가 표현 범위를 넘을 때(정수는 넘치지 않음). | `2.0 ** 10000` | 정수로 계산하거나 `decimal`, 로그 스케일을 씁니다. |
| `NotImplementedError` | 아직 구현하지 않은(하위 클래스가 채워야 할) 메서드를 부를 때. | `raise NotImplementedError` | 하위 클래스에서 그 메서드를 재정의합니다(13장의 추상 클래스 참고). |
| `KeyboardInterrupt` | 실행 중 Ctrl+C를 누를 때. `Exception`의 하위가 아닙니다. | `import os, signal; os.kill(os.getpid(), signal.SIGINT)` | 정리 작업은 `finally`에 둡니다. `except Exception`으로는 잡히지 않습니다. |

## 나머지 예외 한 줄 설명

위 표와 아래 경고 표에 없는 예외입니다. 부모 열은 트리의 바로 위 클래스예요.

| 예외 | 부모 | 뜻 |
|---|---|---|
| `BaseException` | `object` | 모든 예외의 뿌리. 직접 상속하지 말고 `Exception`을 상속합니다. |
| `Exception` | `BaseException` | 프로그램을 끝내지 않는 일반 예외의 뿌리. 사용자 정의 예외는 여기서 상속합니다(12장). |
| `SystemExit` | `BaseException` | `sys.exit()`가 일으킵니다. 잡지 않으면 인터프리터가 조용히 끝납니다. |
| `GeneratorExit` | `BaseException` | 제너레이터·코루틴의 `close()`가 멈춰 있는 자리에 던집니다(15장). |
| `BaseExceptionGroup` | `BaseException` | 여러 예외를 묶은 그룹의 뿌리(3.11+). `KeyboardInterrupt` 같은 것도 담을 수 있습니다. |
| `ExceptionGroup` | `BaseExceptionGroup` | `Exception`만 담는 예외 그룹(3.11+). 아래 절 참고. |
| `ArithmeticError` | `Exception` | 산술 오류의 부모. `ZeroDivisionError`, `OverflowError`, `FloatingPointError`를 한꺼번에 잡을 때 씁니다. |
| `FloatingPointError` | `ArithmeticError` | 부동소수점 연산 실패용으로 남아 있지만, 지금 파이썬은 기본 설정에서 일으키지 않습니다. |
| `LookupError` | `Exception` | `IndexError`와 `KeyError`의 부모. 둘을 한꺼번에 잡을 때 씁니다. |
| `BufferError` | `Exception` | 버퍼(메모리 뷰 등) 관련 연산을 할 수 없을 때. |
| `EOFError` | `Exception` | `input()`이 입력 끝(EOF)을 만났을 때. 파이프로 빈 입력을 넘기면 납니다. |
| `MemoryError` | `Exception` | 메모리가 바닥났을 때. |
| `ReferenceError` | `Exception` | `weakref.proxy`가 가리키던 객체가 이미 사라졌을 때. |
| `StopAsyncIteration` | `Exception` | 비동기 반복자의 `__anext__`가 끝을 알릴 때(15장). |
| `SystemError` | `Exception` | 인터프리터 내부 오류. 보통 버그 신고 대상입니다. |
| `TabError` | `IndentationError` | 들여쓰기에 탭과 공백을 일관성 없이 섞었을 때(`IndentationError`의 하위). |
| `UnicodeError` | `ValueError` | 유니코드 인코딩·디코딩 오류의 부모(`ValueError`의 하위). |
| `UnicodeTranslateError` | `UnicodeError` | `str.translate()` 계열 변환 중 오류. |
| `OSError` | `Exception` | 운영 체제 호출 실패의 부모. `errno`, `strerror`, `filename` 속성이 있습니다. `IOError`, `EnvironmentError`는 같은 클래스의 옛 이름입니다. |
| `BlockingIOError` | `OSError` | 논블로킹 입출력이 지금 진행될 수 없을 때. |
| `ChildProcessError` | `OSError` | 자식 프로세스 관련 호출이 실패했을 때. |
| `ConnectionError` | `OSError` | 연결 관련 오류의 부모. |
| `BrokenPipeError` | `ConnectionError` | 상대가 닫은 파이프·소켓에 쓸 때. |
| `ConnectionAbortedError` | `ConnectionError` | 상대가 연결을 중단했을 때. |
| `ConnectionRefusedError` | `ConnectionError` | 상대가 연결을 거부했을 때(서버가 꺼져 있는 포트 등). |
| `ConnectionResetError` | `ConnectionError` | 상대가 연결을 초기화했을 때. |
| `InterruptedError` | `OSError` | 시스템 호출이 시그널로 끊겼을 때(파이썬이 대부분 자동으로 재시도). |
| `NotADirectoryError` | `OSError` | 폴더가 필요한 자리에 파일 경로를 줬을 때. |
| `ProcessLookupError` | `OSError` | 없는 프로세스를 가리켰을 때. |
| `TimeoutError` | `OSError` | 시스템 수준 시간 초과. 3.11부터 `asyncio.TimeoutError`도 이 클래스입니다. |

## 경고 계층

경고는 프로그램을 멈추지 않고 메시지만 남기는 예외입니다. `warnings.warn('메시지', DeprecationWarning)`처럼 일으키고, `warnings.filterwarnings()`나 `python -W error`로 숨기거나 예외로 바꿀 수 있어요. "기본 설정에서" 열은 아무 옵션 없이 실행했을 때 화면에 보이는지입니다(`warnings.filters` 기본값으로 확인).

```text
Warning
├── BytesWarning
├── DeprecationWarning
├── EncodingWarning
├── FutureWarning
├── ImportWarning
├── PendingDeprecationWarning
├── ResourceWarning
├── RuntimeWarning
├── SyntaxWarning
├── UnicodeWarning
└── UserWarning
```

| 경고 | 언제 나나 | 기본 설정에서 |
|---|---|---|
| `Warning` | 모든 경고의 부모(`Exception`의 하위). | — |
| `UserWarning` | `warnings.warn()`에서 범주를 생략하면 쓰는 기본 경고. | 표시 |
| `DeprecationWarning` | 곧 없어질 기능을 쓸 때(개발자 대상). | `__main__`에서 난 것만 표시 |
| `PendingDeprecationWarning` | 앞으로 폐기될 예정인 기능. | 숨김 |
| `FutureWarning` | 앞으로 동작이 바뀔 기능(최종 사용자 대상). pandas에서 자주 봅니다. | 표시 |
| `SyntaxWarning` | 문법은 맞지만 의심스러운 코드. 예: 잘못된 이스케이프 `'\d'`(3.12). | 표시 |
| `RuntimeWarning` | 실행 중 의심스러운 동작. 예: `await` 없이 버려진 코루틴. | 표시 |
| `ImportWarning` | 모듈 import 과정의 경고. | 숨김 |
| `UnicodeWarning` | 유니코드 관련 경고. | 표시 |
| `BytesWarning` | `bytes`와 `str`을 비교하는 등. `python -b`로 실행할 때만 납니다. | 표시 |
| `ResourceWarning` | 파일·소켓 같은 자원을 닫지 않았을 때. | 숨김 |
| `EncodingWarning` | `open()`에 `encoding`을 생략했을 때(3.10+). `python -X warn_default_encoding`일 때만 납니다. | 표시 |

## 예외 그룹과 `except*` (3.11+)

여러 작업을 한꺼번에 돌리면 실패도 여러 개가 동시에 생깁니다. 3.11부터는 이를 `ExceptionGroup` 하나로 묶어 던지고, `except*`로 종류별로 나눠 받을 수 있어요. `asyncio.TaskGroup`이 바로 이 방식으로 실패를 알립니다.

```python
def load_all():
    errors = []
    for raw in ['1', 'x', None]:
        try:
            int(raw)
        except (ValueError, TypeError) as e:
            errors.append(e)
    if errors:
        raise ExceptionGroup('변환 실패', errors)

try:
    load_all()
except* ValueError as group:
    print('값 오류', len(group.exceptions), '개')    # 값 오류 1 개
except* TypeError as group:
    print('타입 오류', len(group.exceptions), '개')  # 타입 오류 1 개
```

- `except`와 달리 `except*`는 **맞는 절이 여러 개면 모두 실행**합니다. 위 예에서는 두 절이 다 실행됐어요.
- `group`은 그 종류만 걸러 낸 새 예외 그룹이고, 개별 예외는 `group.exceptions`에 들어 있습니다.
- 어느 `except*`에도 맞지 않은 예외는 남은 것끼리 다시 그룹으로 묶여 바깥으로 전파됩니다.
- 한 `try`에 `except`와 `except*`를 섞어 쓸 수는 없습니다.
- `ExceptionGroup`에는 `Exception`의 하위만 담을 수 있고(`KeyboardInterrupt`를 넣으면 `TypeError`), 그 밖의 예외까지 담으려면 `BaseExceptionGroup`을 씁니다.
