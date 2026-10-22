# 부록 B. 한눈에 보는 파이썬

책 한 권 분량의 문법을 몇십 쪽으로 눌러 담은 요약 노트입니다. 시험 전날 친구가 건네주는 정리 노트처럼, "그거 어떻게 쓰더라?" 싶을 때 빠르게 찾아보라고 만들었어요. 순서는 본문의 장 순서를 따랐고, 각 절 제목 옆에 자세한 설명이 있는 장을 적어 두었습니다.

코드 옆의 `# ...` 주석은 그 줄을 실행했을 때 실제로 찍히는 값입니다. 모든 코드는 Python 3.12(`uv run python`)에서 실행해 확인했어요.

---

## B.1 자료형 (2장)

| 자료형 | 예 | 바꿀 수 있나 | 만들기·변환 |
|---|---|---|---|
| `int` | `42`, `-7`, `1_000_000`, `0b1010`, `0xff` | 아니요 | `int("42")`, `int("ff", 16)` |
| `float` | `3.14`, `1e-3`, `float("inf")` | 아니요 | `float("3.5")` |
| `complex` | `3+4j` | 아니요 | `complex(3, 4)` |
| `bool` | `True`, `False` | 아니요 | `bool(0)` → `False` |
| `str` | `"안녕"`, `'hi'`, `"""여러 줄"""` | 아니요 | `str(42)` |
| `bytes` | `b"abc"` | 아니요 | `"한".encode("utf-8")` |
| `list` | `[1, 2, 3]` | 예 | `list("abc")` |
| `tuple` | `(1, 2)`, `(1,)` | 아니요 | `tuple([1, 2])` |
| `dict` | `{"a": 1}` | 예 | `dict(a=1)` |
| `set` | `{1, 2}` | 예 | `set()` (빈 집합) |
| `frozenset` | `frozenset({1, 2})` | 아니요 | `frozenset([1, 2])` |
| `NoneType` | `None` | 아니요 | 값이 없음을 나타냄 |

`{}`는 빈 집합이 아니라 빈 딕셔너리입니다. 빈 집합은 `set()`으로 만들어요. 그리고 원소가 하나인 튜플은 `(1,)`처럼 쉼표가 꼭 있어야 합니다. `(1)`은 그냥 괄호 친 숫자 1이에요.

**거짓으로 취급되는 값**은 이것뿐입니다. 나머지는 모두 참이에요.

```python
falsy = [False, None, 0, 0.0, 0j, "", [], (), {}, set(), range(0)]
print(all(not bool(v) for v in falsy))  # True
print(bool("0"), bool([0]), bool(" "))  # True True True
```

문자열 `"0"`, 0이 하나 든 리스트 `[0]`, 공백 한 칸 `" "`은 비어 있지 않으니 참입니다.

**타입 확인과 변환**

```python
x = 3.7
print(type(x).__name__)            # float
print(isinstance(x, (int, float))) # True
print(int(x), round(x), round(2.5))  # 3 4 2
print(int("0b101", 0), int("12", 8))  # 5 10
print(float("1e3"), str(1/3)[:6])  # 1000.0 0.3333
```

`int(3.7)`은 반올림이 아니라 소수점을 버려서 `3`입니다. `round(2.5)`가 `3`이 아니라 `2`인 것은 파이썬이 "가장 가까운 짝수"로 반올림하기 때문이에요(은행가 반올림).

**변수 할당 요령**

```python
a, b = 1, 2
a, b = b, a                 # 값 맞바꾸기
first, *rest = [1, 2, 3, 4]
print(a, b, first, rest)    # 2 1 1 [2, 3, 4]
x = y = 0                   # 같은 객체에 이름 두 개
print(x is y)               # True
```

## B.2 연산자 (3장)

| 종류 | 연산자 | 예 → 결과 |
|---|---|---|
| 산술 | `+ - * /` | `7 / 2` → `3.5` |
| 몫·나머지 | `//`, `%` | `-7 // 2` → `-4`, `-7 % 2` → `1` |
| 거듭제곱 | `**` | `2 ** 10` → `1024` |
| 비교 | `== != < <= > >=` | `1 < 2 < 3` → `True` |
| 논리 | `and or not` | `0 or "기본"` → `'기본'` |
| 동일성 | `is`, `is not` | `x is None` |
| 소속 | `in`, `not in` | `"a" in "cat"` → `True` |
| 비트 | `&`, \|, `^`, `~`, `<<`, `>>` | `5 & 3` → `1`, `1 << 4` → `16` |
| 할당 | `= += -= *= /= //= %= **=` | `n += 1` |
| 바다코끼리 | `:=` | `if (n := len(s)) > 3:` |
| 조건 표현식 | `A if 조건 else B` | `"짝" if n % 2 == 0 else "홀"` |

```python
print(divmod(17, 5))               # (3, 2)
print(0.1 + 0.2 == 0.3)            # False
import math
print(math.isclose(0.1 + 0.2, 0.3))  # True
print(None or [] or "마지막")       # 마지막
print(3 and 0 and 5)               # 0
```

`and`, `or`는 `True`/`False`가 아니라 **결정을 내린 피연산자 자체**를 돌려줍니다. `or`는 처음 만나는 참 값을, `and`는 처음 만나는 거짓 값을(없으면 마지막 값을) 돌려줘요.

**우선순위** (위가 먼저)

| 순위 | 연산자 |
|---|---|
| 1 | `()` 괄호, 함수 호출, 인덱싱 `x[i]`, 속성 `x.a` |
| 2 | `**` (오른쪽부터 계산: `2 ** 3 ** 2` → `512`) |
| 3 | 단항 `+x`, `-x`, `~x` (`-2 ** 2` → `-4`) |
| 4 | `* / // % @` |
| 5 | `+ -` |
| 6 | `<< >>` |
| 7 | `&`, 그다음 `^`, 그다음 \| |
| 8 | 비교 `in`, `not in`, `is`, `is not`, `<`, `==` 등 |
| 9 | `not` → `and` → `or` |
| 10 | `if-else` 조건 표현식 |
| 11 | `lambda` |
| 12 | `:=` |

헷갈리면 괄호를 치세요. 괄호는 계산을 바꾸지 않을 때도 읽는 사람을 돕습니다.

## B.3 문자열 (2장, 6장)

**인덱싱과 슬라이싱** `s[시작:끝:간격]`, 끝은 포함하지 않습니다.

```python
s = "Python"
print(s[0], s[-1], s[1:4], s[:2], s[2:])  # P n yth Py thon
print(s[::-1], s[::2])                      # nohtyP Pto
```

**자주 쓰는 메서드** (문자열은 바뀌지 않으므로 모두 **새 문자열**을 돌려줍니다)

| 메서드 | 예 | 결과 |
|---|---|---|
| `upper()`, `lower()` | `"Hi".upper()` | `'HI'` |
| `capitalize()`, `title()` | `"hello world".title()` | `'Hello World'` |
| `strip()`, `lstrip()`, `rstrip()` | `"  hi \n".strip()` | `'hi'` |
| `split(sep)` | `"a,b,c".split(",")` | `['a', 'b', 'c']` |
| `split()` (인자 없음) | `" a  b ".split()` | `['a', 'b']` |
| `join(iterable)` | `"-".join(["a", "b"])` | `'a-b'` |
| `replace(old, new)` | `"aaa".replace("a", "b", 2)` | `'bba'` |
| `find(sub)`, `index(sub)` | `"hello".find("z")` | `-1` (`index`는 `ValueError`) |
| `count(sub)` | `"banana".count("a")` | `3` |
| `startswith`, `endswith` | `"test.py".endswith((".py", ".txt"))` | `True` |
| `removeprefix`, `removesuffix` | `"test.py".removesuffix(".py")` | `'test'` |
| `isdigit()`, `isalpha()`, `isalnum()` | `"123".isdigit()` | `True` |
| `isspace()`, `isupper()`, `islower()` | `" ".isspace()` | `True` |
| `center`, `ljust`, `rjust`, `zfill` | `"7".zfill(3)` | `'007'` |
| `partition(sep)` | `"k=v=w".partition("=")` | `('k', '=', 'v=w')` |
| `splitlines()` | `"a\nb".splitlines()` | `['a', 'b']` |
| `encode()` / `bytes.decode()` | `"한".encode()` | `b'\xed\x95\x9c'` |

```python
print("  hi \n".strip(), "hello".find("z"), "banana".count("a"))  # hi -1 3
print("test.py".endswith((".py", ".txt")), "7".zfill(3))         # True 007
print("k=v=w".partition("="))                                    # ('k', '=', 'v=w')
print("한".encode())                                             # b'\xed\x95\x9c'
print(len("한글"), len("한글".encode("utf-8")))                   # 2 6
```

`len()`은 글자 수를 셉니다. UTF-8로 바꾸면 한글 한 글자가 3바이트라서 `6`이 나와요.

**이스케이프와 raw 문자열**

| 쓰기 | 뜻 |
|---|---|
| `\n`, `\t` | 줄바꿈, 탭 |
| `\\`, `\'`, `\"` | 역슬래시, 따옴표 |
| `r"C:\new"` | 역슬래시를 그대로 둠(정규식, 윈도우 경로) |

## B.4 f-string 서식 (2장)

`f"{값:서식}"` 꼴입니다. 서식은 `[채움][정렬][부호][폭][,][.정밀도][형식]` 순서로 씁니다.

| 서식 | 예 | 결과 |
|---|---|---|
| 소수점 자리 | `f"{3.14159:.2f}"` | `'3.14'` |
| 천 단위 쉼표 | `f"{1234567:,}"` | `'1,234,567'` |
| 쉼표 + 소수 | `f"{1234.5:,.1f}"` | `'1,234.5'` |
| 퍼센트 | `f"{0.256:.1%}"` | `'25.6%'` |
| 폭·오른쪽 정렬 | `f"{42:>6}"` | `'    42'` |
| 왼쪽·가운데 정렬 | `f"{'hi':<6}"`, `f"{'hi':^6}"` | `'hi    '`, `'  hi  '` |
| 채움 문자 | `f"{'hi':*^8}"` | `'***hi***'` |
| 0 채우기 | `f"{7:03d}"` | `'007'` |
| 부호 표시 | `f"{5:+d}"` | `'+5'` |
| 2·8·16진수 | `f"{255:b}"`, `f"{255:o}"`, `f"{255:x}"` | `'11111111'`, `'377'`, `'ff'` |
| 접두사 포함 | `f"{255:#x}"` | `'0xff'` |
| 지수 표기 | `f"{12345.678:.2e}"` | `'1.23e+04'` |
| 디버깅 `=` | `f"{x=}"` | `'x=10'` |
| repr로 | `f"{'hi'!r}"` | `"'hi'"` |
| 날짜 | `f"{d:%Y-%m-%d}"` | `'2026-10-21'` |
| 중괄호 그대로 | `f"{{x}}"` | `'{x}'` |

```python
from datetime import date
x, name, d = 10, "파이썬", date(2026, 10, 21)
print(f"{x=}, {x * 2 = }")          # x=10, x * 2 = 20
print(f"[{name:^8}]")               # [  파이썬   ]
print(f"{1234567:,}원 {0.256:.1%}")  # 1,234,567원 25.6%
print(f"{d:%Y년 %m월 %d일}")         # 2026년 10월 21일
w = 8
print(f"[{3.14159:>{w}.2f}]")       # [    3.14]
```

`[  파이썬   ]`의 앞뒤 공백 수가 다른 것은 폭 8에서 글자 3개를 뺀 5칸을 반으로 나눌 수 없어서입니다. 그리고 한글은 터미널에서 두 칸을 차지하지만 f-string은 한 글자로 세기 때문에, 한글이 섞인 표는 줄이 어긋날 수 있어요. 마지막 줄처럼 폭 자리에도 `{w}`처럼 변수를 넣을 수 있습니다.

## B.5 조건문 (4장)

```python
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"
print(grade)                               # B
print("합격" if score >= 60 else "불합격")  # 합격
print(80 <= score < 90)                    # True
```

**match-case** (3.10 이상)

```python
def describe(cmd):
    match cmd:
        case "quit" | "exit":
            return "종료"
        case ["go", direction]:
            return f"{direction}로 이동"
        case {"action": "say", "text": str(text)}:
            return f"말하기: {text}"
        case int(n) if n < 0:
            return "음수"
        case _:
            return "알 수 없음"

print(describe("exit"))                            # 종료
print(describe(["go", "북쪽"]))                    # 북쪽로 이동
print(describe({"action": "say", "text": "안녕"}))  # 말하기: 안녕
print(describe(-3), describe(3.5))                 # 음수 알 수 없음
```

| 패턴 | 뜻 |
|---|---|
| `case 42:`, `case "quit":` | 값과 같으면 |
| `case "a"` \| `"b":` | 둘 중 하나면 |
| `case [x, y]:` | 길이 2인 시퀀스, 원소를 `x`, `y`에 담음 |
| `case [first, *rest]:` | 첫 원소와 나머지 |
| `case {"key": v}:` | 그 키가 있는 딕셔너리(다른 키가 더 있어도 됨) |
| `case Point(x=0, y=yy):` | 클래스와 속성으로 비교 |
| `case int(n) if n < 0:` | 타입 확인 + 가드 조건 |
| `case _:` | 나머지 전부 |

## B.6 반복문 (5장)

```python
print(list(range(3)), list(range(2, 8, 2)))  # [0, 1, 2] [2, 4, 6]
print(list(range(10, 0, -3)))                 # [10, 7, 4, 1]

fruits = ["사과", "배"]
for i, f in enumerate(fruits, start=1):
    print(i, f)                      # 1 사과 / 2 배
for name, price in zip(["사과", "배"], [1000, 2000]):
    print(name, price)               # 사과 1000 / 배 2000
```

| 도구 | 하는 일 |
|---|---|
| `range(끝)`, `range(시작, 끝, 간격)` | 정수 순서 (끝은 미포함) |
| `enumerate(it, start=0)` | `(번호, 값)` 쌍 |
| `zip(a, b)` | 짝지어 묶기, 짧은 쪽에서 멈춤(`strict=True`면 길이가 다를 때 오류) |
| `reversed(seq)` | 거꾸로 |
| `sorted(it, key=, reverse=)` | 정렬한 새 리스트 |
| `dict.items()` | `(키, 값)` 쌍 |
| `break` / `continue` | 반복 끝내기 / 이번 회만 건너뛰기 |
| `for ... else`, `while ... else` | `break` 없이 끝까지 돌았을 때만 `else` 실행 |

```python
for n in [3, 5, 7]:
    if n % 2 == 0:
        print("짝수 발견")
        break
else:
    print("짝수 없음")     # 짝수 없음

count = 0
while True:
    count += 1
    if count == 3:
        break
print(count)               # 3
```

## B.7 리스트와 튜플 (6장)

| 연산 | 예 (`a = [3, 1, 2]`) | 결과·설명 |
|---|---|---|
| 끝에 추가 | `a.append(4)` | `[3, 1, 2, 4]` |
| 여러 개 추가 | `a.extend([5, 6])` | 리스트를 펼쳐서 붙임 |
| 위치에 끼우기 | `a.insert(0, 9)` | 맨 앞에 9 |
| 값으로 지우기 | `a.remove(1)` | 처음 나오는 1 하나 |
| 꺼내기 | `a.pop()`, `a.pop(0)` | 끝 / 0번 원소를 빼서 돌려줌 |
| 위치로 지우기 | `del a[0]`, `del a[1:3]` | |
| 찾기 | `a.index(2)`, `a.count(2)` | 없으면 `index`는 `ValueError` |
| 제자리 정렬 | `a.sort()`, `a.sort(reverse=True)` | 반환값은 `None` |
| 새 정렬 리스트 | `sorted(a)` | 원본 그대로 |
| 제자리 뒤집기 | `a.reverse()` | 반환값은 `None` |
| 얕은 복사 | `a.copy()`, `a[:]`, `list(a)` | |
| 비우기 | `a.clear()` | |
| 합치기·반복 | `a + b`, `a * 3` | 새 리스트 |
| 길이·합·최대·최소 | `len(a)`, `sum(a)`, `max(a)`, `min(a)` | |

```python
a = [3, 1, 2]
print(a.sort(), a)                       # None [1, 2, 3]
words = ["banana", "Apple", "cherry"]
print(sorted(words))                     # ['Apple', 'banana', 'cherry']
print(sorted(words, key=str.lower))      # ['Apple', 'banana', 'cherry']
print(sorted(words, key=len, reverse=True))  # ['banana', 'cherry', 'Apple']
people = [("민수", 30), ("지아", 25)]
print(sorted(people, key=lambda p: p[1]))    # [('지아', 25), ('민수', 30)]
```

**튜플**은 바꿀 수 없는 리스트입니다. 메서드는 `count()`와 `index()` 두 개뿐이고, 딕셔너리 키로 쓸 수 있어요.

```python
point = (3, 4)
x, y = point                  # 풀기(언패킹)
print(x, y, point.count(3))   # 3 4 1
print({(0, 0): "원점"}[(0, 0)])  # 원점
```

## B.8 딕셔너리와 집합 (7장)

**딕셔너리** (`d = {"a": 1, "b": 2}`)

| 연산 | 예 | 설명 |
|---|---|---|
| 읽기 | `d["a"]` | 없는 키면 `KeyError` |
| 안전하게 읽기 | `d.get("z", 0)` | 없으면 기본값(생략하면 `None`) |
| 쓰기 | `d["c"] = 3` | 있으면 덮어씀 |
| 없을 때만 넣기 | `d.setdefault("c", [])` | 있으면 그 값을 돌려줌 |
| 여러 개 넣기 | `d.update({"x": 9})`, `d` \|`=` `{"x": 9}` | |
| 합치기 | `d1` \| `d2` | 새 딕셔너리, 겹치면 오른쪽 우선 (3.9 이상) |
| 지우기 | `del d["a"]`, `d.pop("a", None)` | `pop`은 값을 돌려줌 |
| 마지막 쌍 꺼내기 | `d.popitem()` | 넣은 순서의 마지막 |
| 키·값·쌍 | `d.keys()`, `d.values()`, `d.items()` | |
| 키 확인 | `"a" in d` | 키만 검사 |
| 키 목록으로 만들기 | `dict.fromkeys(["a", "b"], 0)` | `{'a': 0, 'b': 0}` |

```python
d = {"a": 1, "b": 2}
print(d.get("z"), d.get("z", 0))          # None 0
print(d | {"b": 20, "c": 3})              # {'a': 1, 'b': 20, 'c': 3}
for k, v in d.items():
    print(k, v)                           # a 1 / b 2
print(dict(zip(["x", "y"], [1, 2])))      # {'x': 1, 'y': 2}
print(max(d, key=d.get))                  # b
```

파이썬 3.7부터 딕셔너리는 **넣은 순서**를 기억합니다. 마지막 줄처럼 `max(d, key=d.get)`은 값이 가장 큰 키를 찾는 관용구예요.

**집합**은 중복이 없고 순서가 없습니다.

| 연산 | 연산자 | 메서드 |
|---|---|---|
| 합집합 | `a` \| `b` | `a.union(b)` |
| 교집합 | `a & b` | `a.intersection(b)` |
| 차집합 | `a - b` | `a.difference(b)` |
| 대칭차 | `a ^ b` | `a.symmetric_difference(b)` |
| 부분집합 | `a <= b` | `a.issubset(b)` |
| 서로소 | | `a.isdisjoint(b)` |
| 추가·삭제 | | `add(x)`, `remove(x)`(없으면 오류), `discard(x)`(없어도 조용) |

```python
a, b = {1, 2, 3}, {2, 3, 4}
print(a | b, a & b, a - b, a ^ b)   # {1, 2, 3, 4} {2, 3} {1} {1, 4}
print(list(dict.fromkeys([3, 1, 3, 2, 1])))  # [3, 1, 2]
```

마지막 줄은 **순서를 지키면서** 중복을 없애는 요령입니다. `set()`을 쓰면 순서가 보장되지 않아요.

## B.9 고급 자료 구조 (8장)

```python
from collections import Counter, defaultdict, deque, namedtuple
from dataclasses import dataclass, field
from enum import Enum

print(Counter("hello").most_common(2))   # [('l', 2), ('h', 1)]

groups = defaultdict(list)
for word in ["apple", "avocado", "banana"]:
    groups[word[0]].append(word)
print(dict(groups))                      # {'a': ['apple', 'avocado'], 'b': ['banana']}

q = deque([1, 2, 3], maxlen=3)
q.append(4)                              # 꽉 차서 반대쪽 1이 밀려남
print(q)                                 # deque([2, 3, 4], maxlen=3)
print(q.popleft(), q)                    # 2 deque([3, 4], maxlen=3)

Point = namedtuple("Point", "x y")
print(Point(1, 2).x)                     # 1

@dataclass
class Item:
    name: str
    price: int = 0
    tags: list[str] = field(default_factory=list)

print(Item("펜", 1000))                   # Item(name='펜', price=1000, tags=[])

class Color(Enum):
    RED = 1
    GREEN = 2
print(Color.RED, Color(2).name)          # Color.RED GREEN
```

| 도구 | 언제 쓰나 |
|---|---|
| `Counter` | 개수 세기, 가장 많은 것 찾기 |
| `defaultdict(list)` | 키가 없을 때 빈 값을 자동으로 만들며 모으기 |
| `deque` | 양쪽 끝에서 빠르게 넣고 빼기, 최근 N개만 보관 |
| `namedtuple` | 이름으로 꺼내는 가벼운 튜플 |
| `@dataclass` | 데이터 담는 클래스를 짧게 |
| `Enum` | 정해진 선택지(상태, 색 등)에 이름 붙이기 |

## B.10 함수 (9장, 10장)

```python
def greet(name, greeting="안녕하세요", *args, sep=" ", **kwargs):
    """인사말을 만든다."""
    return sep.join([greeting, name, *args]) + str(kwargs or "")

print(greet("민수"))                      # 안녕하세요 민수
print(greet("민수", "반가워요", "님"))       # 반가워요 민수 님
print(greet("민수", sep="-", mood="good"))  # 안녕하세요-민수{'mood': 'good'}
```

| 매개변수 모양 | 뜻 |
|---|---|
| `def f(a, b)` | 위치나 키워드로 받음 |
| `def f(a, b=1)` | 기본값 (기본값 있는 것은 뒤에) |
| `def f(*args)` | 남는 위치 인자를 튜플로 |
| `def f(**kwargs)` | 남는 키워드 인자를 딕셔너리로 |
| `def f(a, *, b)` | `*` 뒤의 `b`는 키워드로만 |
| `def f(a, /, b)` | `/` 앞의 `a`는 위치로만 (3.8 이상) |
| `f(*lst)`, `f(**dct)` | 부를 때 리스트·딕셔너리를 펼쳐 넘김 |

```python
def area(w, h, /, *, unit="cm"):
    return f"{w * h}{unit}²"

print(area(3, 4))             # 12cm²
print(area(3, 4, unit="m"))   # 12m²
size = (5, 6)
print(area(*size))            # 30cm²
```

**스코프** — 이름은 L(함수 안) → E(감싼 함수) → G(모듈) → B(내장) 순서로 찾습니다.

```python
count = 0
def inc():
    global count             # 모듈의 count를 바꾸겠다
    count += 1

def make_counter():
    n = 0
    def step():
        nonlocal n           # 감싼 함수의 n을 바꾸겠다
        n += 1
        return n
    return step

inc()
c = make_counter()
c()
print(count, c())            # 1 2
```

**람다와 고차 함수** (10장)

```python
nums = [1, 2, 3, 4, 5]
print(list(map(lambda n: n * n, nums)))         # [1, 4, 9, 16, 25]
print(list(filter(lambda n: n % 2, nums)))      # [1, 3, 5]
from functools import reduce, partial
print(reduce(lambda a, b: a * b, nums))         # 120
double = partial(pow, exp=2)
print(double(9))                                # 81
print(any(n > 4 for n in nums), all(n > 0 for n in nums))  # True True
```

**데코레이터** (10장, 16장)

```python
import functools

def shout(func):
    @functools.wraps(func)          # 원래 함수의 이름·docstring 유지
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper

@shout
def hello(name):
    return f"hello, {name}"

print(hello("kim"), hello.__name__)  # HELLO, KIM hello

@functools.cache
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(80))                       # 23416728348467685
```

## B.11 컴프리헨션 (5장, 6장, 7장)

| 종류 | 모양 | 결과 |
|---|---|---|
| 리스트 | `[식 for x in it if 조건]` | `list` |
| 딕셔너리 | `{키: 값 for x in it}` | `dict` |
| 집합 | `{식 for x in it}` | `set` |
| 제너레이터 | `(식 for x in it)` | 하나씩 만드는 제너레이터 |

```python
print([x * x for x in range(6) if x % 2 == 0])   # [0, 4, 16]
print(["짝" if x % 2 == 0 else "홀" for x in range(3)])  # ['짝', '홀', '짝']
print({w: len(w) for w in ["hi", "hello"]})       # {'hi': 2, 'hello': 5}
print({len(w) for w in ["a", "b", "cc"]})         # {1, 2}
print(sum(x * x for x in range(4)))               # 14
print([(i, j) for i in range(2) for j in "ab"])   # [(0, 'a'), (0, 'b'), (1, 'a'), (1, 'b')]
matrix = [[1, 2], [3, 4]]
print([n for row in matrix for n in row])         # [1, 2, 3, 4]
```

`if`가 **뒤에** 오면 걸러내기, **앞에** `A if 조건 else B`로 오면 값 바꾸기입니다. 이중 `for`는 바깥 반복을 먼저 씁니다. 일반 `for`문을 위에서 아래로 쓰는 순서 그대로 한 줄에 옮긴다고 생각하면 돼요.

## B.12 클래스 (11장, 13장)

```python
class Account:
    bank = "파이썬은행"                     # 클래스 속성 (모든 객체가 공유)

    def __init__(self, owner, balance=0):
        self.owner = owner                 # 인스턴스 속성
        self._balance = balance            # 밑줄 하나: "내부용" 약속

    @property
    def balance(self):                     # 읽기 전용 속성처럼
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("입금액은 양수여야 합니다")
        self._balance += amount
        return self

    @classmethod
    def empty(cls, owner):                 # 다른 생성 방법
        return cls(owner)

    @staticmethod
    def fee(amount):                       # self도 cls도 필요 없는 도우미
        return amount // 100

    def __repr__(self):
        return f"{type(self).__name__}({self.owner!r}, {self._balance})"

acc = Account.empty("민수").deposit(5000).deposit(300)
print(acc, acc.balance, Account.fee(5000))  # Account('민수', 5300) 5300 50
```

**상속** (13장) — 바로 위의 `Account`를 이어받습니다.

```python
class Savings(Account):
    def __init__(self, owner, balance=0, rate=0.03):
        super().__init__(owner, balance)   # 부모의 초기화 먼저
        self.rate = rate

    def deposit(self, amount):             # 오버라이딩
        return super().deposit(amount + 100)

s = Savings("지아").deposit(1000)
print(s, isinstance(s, Account))           # Savings('지아', 1100) True
print([c.__name__ for c in Savings.__mro__])  # ['Savings', 'Account', 'object']
```

**자주 쓰는 특수 메서드** (11장)

| 메서드 | 불리는 때 |
|---|---|
| `__init__(self, ...)` | 객체를 만들 때 |
| `__repr__`, `__str__` | `repr(x)`, `print(x)`·`str(x)` |
| `__eq__`, `__lt__` 등 | `==`, `<` 등 비교 |
| `__hash__` | `hash(x)`, 딕셔너리 키·집합 원소로 쓸 때 |
| `__len__`, `__bool__` | `len(x)`, `if x:` |
| `__getitem__`, `__setitem__` | `x[k]`, `x[k] = v` |
| `__contains__` | `k in x` |
| `__iter__`, `__next__` | `for` 반복 |
| `__add__`, `__mul__` 등 | `+`, `*` 등 |
| `__call__` | `x()` |
| `__enter__`, `__exit__` | `with x:` |

**추상 클래스** (13장)

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self): ...

class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self):
        return self.side ** 2

print(Square(3).area())   # 9
```

`Shape()`처럼 추상 클래스를 바로 만들려고 하면 `TypeError`가 납니다. 자식 클래스가 `area()`를 꼭 만들도록 강제하는 장치예요.

## B.13 예외 처리 (12장)

```python
def to_int(text):
    try:
        n = int(text)
    except ValueError as e:
        print("변환 실패:", e)
        return None
    else:                         # 예외가 없을 때만
        return n
    finally:                      # 무슨 일이 있어도 마지막에
        print("검사 끝")

print(to_int("42"))
print(to_int("4.2"))
```

```text
검사 끝
42
변환 실패: invalid literal for int() with base 10: '4.2'
검사 끝
None
```

`return`이 있어도 `finally`는 먼저 실행됩니다. 그래서 `검사 끝`이 `42`보다 먼저 찍혀요.

| 문법 | 뜻 |
|---|---|
| `except (A, B) as e:` | 둘 중 하나 |
| `except Exception as e:` | 거의 모든 예외(되도록 구체적인 예외를 먼저) |
| `raise ValueError("메시지")` | 예외 일으키기 |
| `raise` | 잡은 예외를 그대로 다시 던지기 |
| `raise 새예외 from e` | 원인을 연결해서 바꿔 던지기 |
| `class MyError(Exception): pass` | 사용자 정의 예외 |

```python
class InsufficientFunds(Exception):
    def __init__(self, need):
        super().__init__(f"{need}원이 부족합니다")
        self.need = need

try:
    raise InsufficientFunds(500)
except InsufficientFunds as e:
    print(e, e.need)    # 500원이 부족합니다 500
```

## B.14 파일 (12장)

```python
from pathlib import Path

p = Path("memo.txt")
p.write_text("첫 줄\n둘째 줄\n", encoding="utf-8")

with open(p, encoding="utf-8") as f:     # 블록이 끝나면 자동으로 닫힘
    for line in f:
        print(line.rstrip())             # 첫 줄 / 둘째 줄

with open(p, "a", encoding="utf-8") as f:
    f.write("셋째 줄\n")

print(p.read_text(encoding="utf-8").splitlines())  # ['첫 줄', '둘째 줄', '셋째 줄']
print(p.exists(), p.suffix, p.stem)      # True .txt memo
p.unlink()                               # 파일 지우기
```

| 모드 | 뜻 |
|---|---|
| `"r"` | 읽기 (기본값, 파일이 없으면 오류) |
| `"w"` | 쓰기 (있으면 **내용을 지우고** 새로) |
| `"a"` | 끝에 덧붙이기 |
| `"x"` | 새로 만들기 (이미 있으면 오류) |
| `"b"` 추가 | 바이너리 (`"rb"`, `"wb"`) |
| `"+"` 추가 | 읽기와 쓰기 함께 |

| pathlib | 뜻 |
|---|---|
| `Path("a") / "b.txt"` | 경로 잇기 |
| `p.name`, `p.stem`, `p.suffix`, `p.parent` | 이름, 확장자 뺀 이름, 확장자, 상위 폴더 |
| `p.exists()`, `p.is_file()`, `p.is_dir()` | 존재 확인 |
| `p.mkdir(parents=True, exist_ok=True)` | 폴더 만들기 |
| `p.glob("*.py")`, `p.rglob("*.py")` | 찾기 (하위 폴더까지는 `rglob`) |
| `Path.cwd()`, `Path.home()` | 현재 작업 폴더, 홈 폴더 |

텍스트 파일을 열 때는 `encoding="utf-8"`을 꼭 적는 습관을 들이세요. 생략하면 운영체제마다 기본값이 달라서, 윈도우에서 한글이 깨지는 원인이 됩니다(부록 D 참고).

**JSON과 CSV**

```python
import csv, io, json

data = {"이름": "민수", "점수": [90, 85]}
text = json.dumps(data, ensure_ascii=False)
print(text)                        # {"이름": "민수", "점수": [90, 85]}
print(json.loads(text)["점수"][0])  # 90

buf = io.StringIO()
writer = csv.writer(buf)
writer.writerow(["이름", "점수"])
writer.writerow(["민수", 90])
print(buf.getvalue().splitlines())  # ['이름,점수', '민수,90']
```

## B.15 모듈과 패키지 (14장)

```python
import math                       # 모듈 통째로
import datetime as dt             # 별명
from pathlib import Path          # 필요한 것만
from collections import Counter, deque

print(math.sqrt(16), dt.date(2026, 1, 1).year)  # 4.0 2026
```

```python
# my_module.py
def main():
    print("직접 실행했을 때만")

if __name__ == "__main__":        # import될 때는 실행되지 않음
    main()
```

| 구조 | 뜻 |
|---|---|
| `pkg/__init__.py` | 이 폴더가 패키지임을 알리고, 패키지를 import할 때 실행됨 |
| `from . import mod` | 같은 패키지 안의 모듈 (상대 import) |
| `from .. import mod` | 한 단계 위 패키지 |
| `sys.path` | 모듈을 찾는 폴더 목록 |

외부 라이브러리 설치는 `uv add 패키지`, 실행은 `uv run`입니다. 자세한 것은 부록 A를 보세요.

## B.16 반복자와 제너레이터 (15장)

```python
it = iter([10, 20])
print(next(it), next(it), next(it, "끝"))   # 10 20 끝

def countdown(n):
    while n > 0:
        yield n                 # 값을 하나 내주고 여기서 멈춤
        n -= 1

print(list(countdown(3)))       # [3, 2, 1]

def read_upper(lines):
    for line in lines:
        yield line.upper()

def chain_all(*iterables):
    for it in iterables:
        yield from it           # 다른 반복 가능 객체를 그대로 넘김

print(list(chain_all("ab", [1, 2])))     # ['a', 'b', 1, 2]
print(list(read_upper(["a", "b"])))      # ['A', 'B']
gen = (x * x for x in range(3))
print(sum(gen), sum(gen))                # 5 0
```

마지막 줄을 보세요. 제너레이터는 **한 번 다 쓰면 끝**입니다. 두 번째 `sum(gen)`은 남은 값이 없어서 `0`이에요.

**itertools 자주 쓰는 것**

```python
import itertools as itt

print(list(itt.islice(itt.count(10, 5), 3)))       # [10, 15, 20]
print(list(itt.chain([1, 2], [3])))                # [1, 2, 3]
print(list(itt.accumulate([1, 2, 3, 4])))          # [1, 3, 6, 10]
print(list(itt.pairwise("abcd")))                  # [('a', 'b'), ('b', 'c'), ('c', 'd')]
print(list(itt.batched(range(7), 3)))              # [(0, 1, 2), (3, 4, 5), (6,)]
print(list(itt.combinations("abc", 2)))            # [('a', 'b'), ('a', 'c'), ('b', 'c')]
print(len(list(itt.permutations("abc"))))          # 6
print([(k, len(list(g))) for k, g in itt.groupby("aabccc")])  # [('a', 2), ('b', 1), ('c', 3)]
```

`pairwise`는 3.10, `batched`는 3.12에 들어왔습니다(부록 C).

## B.17 async 기본 (15장)

```python
import asyncio

async def fetch(name, delay):
    await asyncio.sleep(delay)        # 기다리는 동안 다른 작업에 양보
    return f"{name} 완료"

async def main():
    results = await asyncio.gather(fetch("A", 0.2), fetch("B", 0.1))
    print(results)                    # ['A 완료', 'B 완료']

    async with asyncio.TaskGroup() as tg:     # 3.11 이상
        t1 = tg.create_task(fetch("C", 0.1))
        t2 = tg.create_task(fetch("D", 0.1))
    print(t1.result(), t2.result())   # C 완료 D 완료

asyncio.run(main())
```

| 문법 | 뜻 |
|---|---|
| `async def` | 코루틴 함수 정의. 부르면 바로 실행되지 않고 코루틴 객체가 나옴 |
| `await 코루틴` | 끝날 때까지 기다림 (`async def` 안에서만) |
| `asyncio.run(main())` | 프로그램의 시작점에서 한 번 |
| `asyncio.gather(a, b)` | 여러 개를 동시에 돌리고 결과를 **넣은 순서대로** 받음 |
| `asyncio.TaskGroup()` | 묶어서 돌리고, 하나가 실패하면 나머지를 취소 |
| `asyncio.sleep(초)` | 비동기 대기 (`time.sleep`은 전체를 멈추게 함) |
| `async for`, `async with` | 비동기 반복, 비동기 컨텍스트 매니저 |

`B`가 먼저 끝나도 `gather`의 결과는 `['A 완료', 'B 완료']` 순서입니다. 넣은 순서를 지켜 주거든요.

## B.18 타입 힌트 (2장)

```python
from typing import Optional

def find(names: list[str], target: str) -> int | None:
    return names.index(target) if target in names else None

scores: dict[str, int] = {"민수": 90}
pair: tuple[int, str] = (1, "a")
maybe: Optional[int] = None       # int | None 과 같음
print(find(["a", "b"], "b"), find([], "x"))   # 1 None
```

| 쓰기 | 뜻 | 쓸 수 있는 버전 |
|---|---|---|
| `list[int]`, `dict[str, int]` | 원소 타입이 있는 리스트·딕셔너리 | 3.9 이상 |
| `int` \| `None` | 둘 중 하나 | 3.10 이상 |
| `Optional[int]` | `int` \| `None`과 같음 | 예전부터 |
| `tuple[int, ...]` | 길이 상관없는 정수 튜플 | 3.9 이상 |
| `Callable[[int], str]` | 함수 타입 (`collections.abc`에서) | |
| `type Pair = tuple[int, int]` | 타입에 별명 붙이기 | 3.12 이상 |

타입 힌트는 **실행에 영향을 주지 않는** 설명표입니다. 틀린 타입을 넘겨도 파이썬은 그대로 실행하고, 검사는 mypy 같은 도구나 편집기가 해 줘요.

## B.19 자주 쓰는 내장 함수 모음

| 분류 | 함수 |
|---|---|
| 입출력 | `print(*값, sep=" ", end="\n")`, `input(안내)`, `open()` |
| 형 변환 | `int`, `float`, `str`, `bool`, `list`, `tuple`, `dict`, `set` |
| 수 | `abs`, `round(x, 자리)`, `pow`, `divmod`, `min`, `max`, `sum` |
| 반복 도우미 | `range`, `enumerate`, `zip`, `reversed`, `sorted`, `map`, `filter` |
| 판정 | `all`, `any`, `isinstance`, `callable`, `hasattr` |
| 객체 정보 | `type`, `id`, `len`, `dir`, `help`, `repr`, `hash` |
| 문자 | `chr(65)` → `'A'`, `ord("A")` → `65`, `bin`, `oct`, `hex` |

전체 목록과 자세한 설명은 레퍼런스 A(내장 함수)를 보세요.
