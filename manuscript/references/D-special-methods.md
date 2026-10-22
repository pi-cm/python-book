# 레퍼런스 D. 특수 메서드

`len(x)`, `x + y`, `for a in x`, `with x:`처럼 평범해 보이는 문법 뒤에는 늘 이름 앞뒤에 밑줄 두 개가 붙은 **특수 메서드**가 숨어 있습니다. 11장에서 `Won` 클래스에 `__add__`, `__repr__`을 붙여 봤다면, 이 표는 "이 문법은 어떤 메서드를 부르지?", "이 메서드는 무엇을 돌려줘야 하지?"가 궁금할 때 펼쳐 보는 자료예요. 범주마다 표 하나와 Python 3.12에서 실행해 확인한 짧은 예를 실었습니다. 예제의 주석은 실제 출력입니다.

목록은 공식 문서 "Data model"(3.12)에 시그니처가 실린 메서드를 빠짐없이 옮겼고, 3.12의 내장 타입에서 `hasattr()`로 이름이 실제로 있는지 확인했습니다. 내장 타입에 없는 메서드(`__matmul__` 같은)는 직접 클래스를 만들어 불리는 것을 확인했어요.

## 먼저 알아 둘 규칙

- 특수 메서드는 **클래스에 정의**해야 동작합니다. `len(x)`나 `x + y`는 객체 자신이 아니라 객체의 타입(클래스)에서 메서드를 찾기 때문에, 인스턴스에 나중에 붙인 `__len__`은 무시됩니다.
- 지원하지 않는 상대를 만나면 예외를 내지 말고 `NotImplemented`를 돌려주세요. 그래야 파이썬이 상대편의 반사 메서드를 시도하거나 알맞은 `TypeError`를 냅니다.
- 직접 `x.__len__()`처럼 부르지 말고 `len(x)` 같은 문법·내장 함수를 쓰세요. 특수 메서드는 파이썬이 부르라고 있는 것입니다.

```python
class Box:
    pass

b = Box()
b.__len__ = lambda: 5                         # 인스턴스에 붙이면
print(b.__len__())                            # 5 (직접 부르면 되지만)
try:
    len(b)                                    # len()은 타입(클래스)에서만 찾음
except TypeError as e:
    print("[X]", e)                           # [X] object of type 'Box' has no len()

Box.__len__ = lambda self: 5                  # 클래스에 붙여야 동작
print(len(b))                                 # 5
```

## 생성과 소멸

| 메서드 | 언제 불리나 | 돌려줘야 하는 것 | 관련 장 |
|---|---|---|---|
| `__new__(cls, ...)` | `C(...)`로 객체를 만들 때 가장 먼저. 정적 메서드라 첫 인자가 클래스 | 새 객체. `cls`의 인스턴스가 아니면 `__init__`이 불리지 않음 | 11, 16 |
| `__init__(self, ...)` | `__new__`가 돌려준 객체를 채울 때 | `None`(다른 값이면 `TypeError`) | 11 |
| `__del__(self)` | 객체가 정리되기 직전. 언제 불릴지 보장되지 않음 | 없음 | 11 |

`int`, `str`, `tuple`처럼 바꿀 수 없는 타입을 상속할 때는 값이 `__new__`에서 정해지므로 검사도 그곳에서 합니다.

```python
class Won(int):
    """음수가 될 수 없는 금액(int를 상속)"""

    def __new__(cls, amount: int) -> "Won":
        if amount < 0:
            raise ValueError("금액은 0 이상이어야 해요")
        return super().__new__(cls, amount)   # 바꿀 수 없는 int는 __new__에서 값을 정함

    def __init__(self, amount: int) -> None:
        self.currency = "KRW"                 # 이미 만들어진 객체에 속성만 채움

price = Won(5000)
print(price + 1000, price.currency, isinstance(price, int))   # 6000 KRW True
```

## 문자열 표현

| 메서드 | 언제 불리나 | 돌려줘야 하는 것 | 관련 장 |
|---|---|---|---|
| `__repr__(self)` | `repr()`, 대화형 창, 리스트 안의 객체 출력, f-문자열의 `!r` | `str`. 가능하면 `Won(35000)`처럼 다시 만들 수 있는 모양 | 11 |
| `__str__(self)` | `str()`, `print()`, f-문자열 기본값. 없으면 `__repr__`을 씀 | `str`. 사람이 읽기 좋은 모양 | 11 |
| `__format__(self, spec)` | `format(x, spec)`, `f"{x:spec}"`, `str.format()` | `str`. `spec`은 콜론 뒤의 글자 | 11 |
| `__bytes__(self)` | `bytes(x)` | `bytes` | |

```python
class Won:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __repr__(self) -> str:                # 개발자용: repr(), 대화형 창
        return f"Won({self.amount})"

    def __str__(self) -> str:                 # 사용자용: print(), str()
        return f"{self.amount:,}원"

    def __format__(self, spec: str) -> str:   # format(), f-문자열의 :spec
        if spec == "만":
            return f"{self.amount / 10000:g}만 원"
        return format(self.amount, spec)

w = Won(35000)
print(repr(w), str(w))       # Won(35000) 35,000원
print(f"{w:만} / {w:>8,}")   # 3.5만 원 /   35,000
```

## 비교

| 메서드 | 언제 불리나 | 돌려줘야 하는 것 | 관련 장 |
|---|---|---|---|
| `__eq__(self, other)` | `x == y` | 보통 `bool`, 모르면 `NotImplemented`. 없으면 `is`로 비교 | 11 |
| `__ne__(self, other)` | `x != y`. 없으면 `__eq__` 결과를 뒤집음 | 보통 `bool` | 11 |
| `__lt__(self, other)` | `x < y`, `sorted()`, `min()`, `max()` | 보통 `bool` | 11 |
| `__le__(self, other)` | `x <= y` | 보통 `bool` | 11 |
| `__gt__(self, other)` | `x > y` | 보통 `bool` | 11 |
| `__ge__(self, other)` | `x >= y` | 보통 `bool` | 11 |

`x < y`가 `NotImplemented`를 받으면 파이썬은 자리를 바꿔 `y > x`를 시도합니다(`<`와 `>`, `<=`와 `>=`, `==`와 `==`가 짝). 여섯 개를 다 쓰기 번거로우면 `functools.total_ordering`이 `__eq__`와 하나의 순서 비교만으로 나머지를 채워 줍니다.

```python
from functools import total_ordering

@total_ordering                               # __eq__와 __lt__만 있으면 나머지를 채워 줌
class Won:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Won):
            return NotImplemented             # 모르는 타입이면 상대에게 넘김
        return self.amount == other.amount

    def __lt__(self, other: "Won") -> bool:
        if not isinstance(other, Won):
            return NotImplemented
        return self.amount < other.amount

print(Won(1000) < Won(2000), Won(3000) >= Won(2000), Won(1000) == 1000)   # True True False
print(max(Won(1000), Won(5000), Won(3000)).amount)                        # 5000
```

## 해시와 진릿값

| 메서드 | 언제 불리나 | 돌려줘야 하는 것 | 관련 장 |
|---|---|---|---|
| `__hash__(self)` | `hash()`, 집합에 넣을 때, 딕셔너리 키로 쓸 때 | `int`. `==`로 같은 객체는 해시도 같아야 함 | 11 |
| `__bool__(self)` | `bool()`, `if`·`while` 조건, `and`·`or`·`not` | `bool`. 없으면 `__len__()`이 0인지로, 둘 다 없으면 항상 참 | 11 |

`__eq__`만 정의하고 `__hash__`를 정의하지 않으면 `__hash__`가 `None`이 되어 집합이나 딕셔너리 키로 쓸 수 없게 됩니다. 값이 바뀌는 객체라면 일부러 그렇게 두는 것이 맞아요.

```python
class Won:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Won) and self.amount == other.amount

    def __hash__(self) -> int:                # 같으면 해시도 같아야 함
        return hash(self.amount)

    def __bool__(self) -> bool:               # if 문, bool()
        return self.amount != 0

print(len({Won(1000), Won(1000), Won(2000)}))   # 2
print(bool(Won(0)), bool(Won(500)))             # False True

class NoHash:
    def __eq__(self, other: object) -> bool:
        return True

print(NoHash.__hash__)                          # None (__eq__만 정의하면 해시가 꺼짐)
```

## 속성 접근

| 메서드 | 언제 불리나 | 돌려줘야 하는 것 | 관련 장 |
|---|---|---|---|
| `__getattribute__(self, name)` | **모든** 속성 읽기 `x.name` | 속성 값, 없으면 `AttributeError` | 16 |
| `__getattr__(self, name)` | 평소대로 찾다가 `AttributeError`가 났을 때만 | 속성 값, 없으면 `AttributeError` | 16 |
| `__setattr__(self, name, value)` | **모든** 속성 대입 `x.name = v` | `None` | 16 |
| `__delattr__(self, name)` | `del x.name` | `None` | 16 |
| `__dir__(self)` | `dir(x)` | 이름들을 담은 반복 가능 객체(`dir()`이 정렬해 줌) | |

모듈 파일의 맨 바깥에 `def __getattr__(name)`과 `def __dir__()`을 정의하면 모듈의 속성 접근도 바꿀 수 있습니다(3.7부터). 오래된 이름에 경고를 띄울 때 씁니다.

```python
class Settings:
    def __init__(self) -> None:
        super().__setattr__("_data", {})      # __setattr__를 거치지 않고 저장

    def __getattr__(self, name: str) -> object:   # 평소대로 찾아서 없을 때만
        return self._data.get(name)

    def __setattr__(self, name: str, value: object) -> None:  # 모든 대입
        self._data[name] = value

    def __delattr__(self, name: str) -> None:
        self._data.pop(name, None)

    def __dir__(self) -> list[str]:
        return sorted(self._data)

s = Settings()
s.region = "서울"
print(s.region, s.timeout, dir(s))   # 서울 None ['region']
del s.region
print(s.region)                      # None
```

## 디스크립터

클래스 속성 자리에 놓인 객체가 아래 메서드를 가지면 **디스크립터**가 되어, 그 속성을 읽고 쓰는 일을 가로챕니다. `property`, `classmethod`, `staticmethod`가 모두 디스크립터예요.

| 메서드 | 언제 불리나 | 돌려줘야 하는 것 | 관련 장 |
|---|---|---|---|
| `__get__(self, instance, owner=None)` | `obj.attr` 또는 `Owner.attr`로 읽을 때. 클래스에서 읽으면 `instance`가 `None` | 속성 값 | 16 |
| `__set__(self, instance, value)` | `obj.attr = v` | `None` | 16 |
| `__delete__(self, instance)` | `del obj.attr` | `None` | 16 |
| `__set_name__(self, owner, name)` | 디스크립터가 놓인 클래스가 만들어지는 순간(3.6부터) | `None` | 16 |

`__set__`이나 `__delete__`가 있으면 인스턴스의 `__dict__`보다 먼저 쓰이고(데이터 디스크립터), `__get__`만 있으면 인스턴스의 `__dict__`에 같은 이름이 있을 때 밀립니다.

```python
class Positive:
    def __set_name__(self, owner: type, name: str) -> None:   # 클래스에 붙는 순간
        self.name = "_" + name

    def __get__(self, obj: object, objtype: type | None = None) -> object:
        if obj is None:
            return self                       # 클래스에서 읽으면 디스크립터 자신
        return getattr(obj, self.name)

    def __set__(self, obj: object, value: int) -> None:
        if value < 0:
            raise ValueError(f"{self.name[1:]}은(는) 0 이상이어야 해요")
        setattr(obj, self.name, value)

class Coffee:
    price = Positive()

    def __init__(self, price: int) -> None:
        self.price = price                    # Positive.__set__이 불림

c = Coffee(4500)
print(c.price, type(Coffee.__dict__["price"]).__name__)   # 4500 Positive
try:
    c.price = -1
except ValueError as e:
    print("[X]", e)                           # [X] price은(는) 0 이상이어야 해요
```

## 클래스 만들기

| 메서드 | 언제 불리나 | 돌려줘야 하는 것 | 관련 장 |
|---|---|---|---|
| `__init_subclass__(cls, **kwargs)` | 이 클래스를 상속한 자식 클래스가 정의될 때(3.6부터). 자동으로 클래스 메서드 | `None` | 16 |
| `__class_getitem__(cls, key)` | 클래스에 대괄호를 쓸 때 `C[key]`. 자동으로 클래스 메서드 | 보통 제네릭 별칭 객체(`list[int]` 같은) | |
| `__mro_entries__(self, bases)` | 클래스가 아닌 객체를 `class D(obj):`의 부모 자리에 썼을 때 | 실제 부모 클래스들의 튜플 | |
| `__prepare__(name, bases, **kwargs)` | 메타클래스에 정의. 클래스 본문을 실행하기 전 | 클래스 본문의 이름을 담을 매핑(보통 `dict`) | |
| `__instancecheck__(self, instance)` | 메타클래스에 정의. `isinstance(obj, C)` | `bool` | |
| `__subclasscheck__(self, subclass)` | 메타클래스에 정의. `issubclass(S, C)` | `bool` | |

`__instancecheck__`와 `__subclasscheck__`는 13장에서 본 추상 클래스의 메타클래스 `abc.ABCMeta`가 구현하고 있습니다. 상속하지 않은 클래스라도 `register()`로 등록하면 `isinstance()` 검사를 통과하는 것이 이 덕분이에요.

```python
class Plugin:
    registry: dict[str, type] = {}

    def __init_subclass__(cls, /, key: str, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Plugin.registry[key] = cls            # 자식 클래스가 정의될 때마다 등록

    def __class_getitem__(cls, item: type) -> str:   # Plugin[int] 문법
        return f"{cls.__name__}[{item.__name__}]"

class CsvExport(Plugin, key="csv"): pass
class JsonExport(Plugin, key="json"): pass

print(Plugin.registry)
# {'csv': <class '__main__.CsvExport'>, 'json': <class '__main__.JsonExport'>}
print(Plugin[int])     # Plugin[int]
```

## 호출

| 메서드 | 언제 불리나 | 돌려줘야 하는 것 | 관련 장 |
|---|---|---|---|
| `__call__(self, ...)` | 객체를 함수처럼 부를 때 `x(...)`. 있으면 `callable(x)`가 `True` | 무엇이든 | 11, 16 |

```python
class VatCalculator:
    def __init__(self, rate: float) -> None:
        self.rate = rate

    def __call__(self, price: int) -> int:    # 객체를 함수처럼 부르기
        return round(price * (1 + self.rate))

vat = VatCalculator(0.1)
print(vat(10000), callable(vat))   # 11000 True
```

## 컨테이너와 반복

| 메서드 | 언제 불리나 | 돌려줘야 하는 것 | 관련 장 |
|---|---|---|---|
| `__len__(self)` | `len(x)`, `__bool__`이 없을 때의 진릿값 | 0 이상의 `int` | 11 |
| `__length_hint__(self)` | `operator.length_hint(x)`. 미리 자리를 잡는 최적화용(3.4부터) | 0 이상의 `int`(추정치), 또는 `NotImplemented` | |
| `__getitem__(self, key)` | `x[key]`, 슬라이스 `x[1:3]`(key가 `slice` 객체), `__iter__`가 없을 때의 `for` | 값. 없는 위치면 `IndexError`, 없는 키면 `KeyError` | 11 |
| `__setitem__(self, key, value)` | `x[key] = v` | `None` | 11 |
| `__delitem__(self, key)` | `del x[key]` | `None` | 11 |
| `__missing__(self, key)` | `dict`를 상속한 클래스에서 없는 키를 `d[key]`로 읽을 때 | 대신 돌려줄 값(또는 예외) | |
| `__iter__(self)` | `iter(x)`, `for`, 리스트 내포, `list(x)`, 언패킹 | 반복자(`__next__`가 있는 객체) | 11, 15 |
| `__next__(self)` | `next(it)`, `for`의 매 단계 | 다음 값. 끝나면 `StopIteration` | 11, 15 |
| `__reversed__(self)` | `reversed(x)` | 역순 반복자. 없으면 `__len__`과 `__getitem__`으로 대신함 | |
| `__contains__(self, item)` | `item in x`, `not in` | `bool`. 없으면 `__iter__`, 그다음 `__getitem__`으로 하나씩 비교 | 11 |

```python
class Wallet:
    def __init__(self) -> None:
        self._bills: list[int] = []

    def __len__(self) -> int:                 # len()
        return len(self._bills)

    def __getitem__(self, i: int) -> int:     # w[i], 슬라이스, for의 마지막 수단
        return self._bills[i]

    def __setitem__(self, i: int, value: int) -> None:
        self._bills[i] = value

    def __delitem__(self, i: int) -> None:
        del self._bills[i]

    def __iter__(self):                       # for, list()
        return iter(self._bills)

    def __reversed__(self):                   # reversed()
        return reversed(self._bills)

    def __contains__(self, bill: int) -> bool:  # in
        return bill in self._bills

w = Wallet()
w._bills += [1000, 5000, 10000, 50000]
w[0] = 50000
del w[1]
print(len(w), w[0], w[-1], 10000 in w, list(reversed(w)))
# 3 50000 50000 True [50000, 10000, 50000]

class Prices(dict):
    def __missing__(self, key: str) -> int:   # dict 하위 클래스에서 없는 키
        return 0

print(Prices(아메리카노=4500)["라테"])   # 0
```

## 숫자: 이항 연산

연산자 하나에 메서드가 세 벌 있습니다. `x + y`는 먼저 `x.__add__(y)`를 부르고, 그 결과가 `NotImplemented`이면(또는 메서드가 없으면) 두 타입이 다를 때 `y.__radd__(x)`를 부릅니다. 이것이 **반사(reflected)** 메서드예요. `x += y`는 `x.__iadd__(y)`를 먼저 찾고, 없으면 `x = x + y`로 대신합니다. 이것이 **제자리(in-place)** 메서드로, 리스트처럼 바꿀 수 있는 객체는 자기 자신을 고친 뒤 `self`를 돌려줍니다.

| 연산 | 기본 | 반사(r) | 제자리(i) |
|---|---|---|---|
| `x + y` | `__add__` | `__radd__` | `__iadd__` |
| `x - y` | `__sub__` | `__rsub__` | `__isub__` |
| `x * y` | `__mul__` | `__rmul__` | `__imul__` |
| `x @ y` | `__matmul__` | `__rmatmul__` | `__imatmul__` |
| `x / y` | `__truediv__` | `__rtruediv__` | `__itruediv__` |
| `x // y` | `__floordiv__` | `__rfloordiv__` | `__ifloordiv__` |
| `x % y` | `__mod__` | `__rmod__` | `__imod__` |
| `divmod(x, y)` | `__divmod__` | `__rdivmod__` | (없음) |
| `x ** y`, `pow(x, y[, m])` | `__pow__` | `__rpow__` | `__ipow__` |
| `x << y` | `__lshift__` | `__rlshift__` | `__ilshift__` |
| `x >> y` | `__rshift__` | `__rrshift__` | `__irshift__` |
| `x & y` | `__and__` | `__rand__` | `__iand__` |
| `x ^ y` | `__xor__` | `__rxor__` | `__ixor__` |
| `x` \| `y` | `__or__` | `__ror__` | `__ior__` |

돌려줄 것은 연산 결과, 또는 상대 타입을 모르면 `NotImplemented`입니다. 제자리 메서드는 결과(보통 `self`)를 돌려줘야 하고, `None`을 돌려주면 변수가 `None`이 돼 버리니 주의하세요. 관련 장은 11장(연산자 오버로딩)과 3장(연산자 자체)입니다.

## 숫자: 단항 연산과 변환

| 메서드 | 언제 불리나 | 돌려줘야 하는 것 | 관련 장 |
|---|---|---|---|
| `__neg__(self)` | `-x` | 결과 값 | 11 |
| `__pos__(self)` | `+x` | 결과 값 | |
| `__abs__(self)` | `abs(x)` | 결과 값 | 11 |
| `__invert__(self)` | `~x` | 결과 값 | |
| `__int__(self)` | `int(x)` | `int` | 11 |
| `__float__(self)` | `float(x)` | `float` | 11 |
| `__complex__(self)` | `complex(x)` | `complex` | |
| `__index__(self)` | 손실 없이 정수가 필요할 때: 인덱스·슬라이스, `bin()`, `hex()`, `oct()`, `operator.index()` | `int`. `int()`·`float()`·`complex()`도 해당 메서드가 없으면 이것을 씀 | 11 |
| `__round__(self[, ndigits])` | `round(x)`, `round(x, n)` | `ndigits` 없이 부르면 보통 `int` | |
| `__trunc__(self)` | `math.trunc(x)` | 보통 `int`. `int()`가 이것으로 넘어가는 동작은 3.11부터 폐지 예고 | |
| `__floor__(self)` | `math.floor(x)` | 보통 `int` | |
| `__ceil__(self)` | `math.ceil(x)` | 보통 `int` | |

```python
class Won:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __add__(self, other: "Won") -> "Won":     # won + won
        if not isinstance(other, Won):
            return NotImplemented
        return Won(self.amount + other.amount)

    def __mul__(self, n: int) -> "Won":           # won * 3
        if not isinstance(n, int):
            return NotImplemented
        return Won(self.amount * n)

    __rmul__ = __mul__                            # 3 * won (왼쪽이 int라 반사 메서드)

    def __radd__(self, other: int) -> "Won":      # sum()은 0 + won부터 시작
        return self if other == 0 else NotImplemented

    def __iadd__(self, other: "Won") -> "Won":    # won += won (제자리)
        self.amount += other.amount
        return self

    def __neg__(self) -> "Won":
        return Won(-self.amount)

    def __index__(self) -> int:                   # hex(), 인덱스, int()의 대안
        return self.amount

    def __repr__(self) -> str:
        return f"Won({self.amount})"

a = Won(1000)
print(a + Won(500), 3 * a, a * 2, -a, sum([Won(100), Won(200)]))
# Won(1500) Won(3000) Won(2000) Won(-1000) Won(300)
a += Won(1)
print(a, hex(Won(255)), int(Won(7)), [10, 20, 30][Won(1)])
# Won(1001) 0xff 7 20
```

`int(Won(7))`이 `__int__` 없이도 7을 돌려주는 것은 `__index__`로 넘어갔기 때문입니다. `sum()`은 0에서 시작해 `0 + Won(100)`을 계산하므로 `__radd__`가 필요해요.

## 컨텍스트 매니저

| 메서드 | 언제 불리나 | 돌려줘야 하는 것 | 관련 장 |
|---|---|---|---|
| `__enter__(self)` | `with x as v:` 블록에 들어갈 때 | `as` 뒤의 이름에 담길 값(보통 `self`) | 11, 16 |
| `__exit__(self, exc_type, exc_value, traceback)` | 블록을 빠져나올 때 **항상**. 예외가 없으면 세 인자가 모두 `None` | 참이면 예외를 삼킴, `None`·`False`면 예외가 그대로 퍼짐 | 11, 16 |

```python
class Transaction:
    def __enter__(self) -> "Transaction":
        print("거래 시작")
        return self                           # as 뒤의 이름에 담김

    def __exit__(self, exc_type, exc, tb) -> bool:
        print("롤백" if exc_type else "커밋")
        return exc_type is ValueError         # True면 예외를 삼킴

with Transaction():
    print("이체 1만 원")
with Transaction():
    raise ValueError("잔액 부족")
print("계속 실행")
# 거래 시작 / 이체 1만 원 / 커밋 / 거래 시작 / 롤백 / 계속 실행 (한 줄씩 출력)
```

## 비동기

`async`·`await` 문법과 함께 3.5에서 들어온 메서드들입니다.

| 메서드 | 언제 불리나 | 돌려줘야 하는 것 | 관련 장 |
|---|---|---|---|
| `__await__(self)` | `await x` | 반복자(보통 제너레이터). `async def` 함수가 돌려주는 코루틴에는 이미 있음 | |
| `__aiter__(self)` | `async for v in x:`. `async def`가 아닌 **일반 메서드**로 정의 | 비동기 반복자(보통 `self`) | 15 |
| `__anext__(self)` | `async for`의 매 단계, `anext()` | 어웨이터블(보통 `async def`로 정의). 끝나면 `StopAsyncIteration` | 15 |
| `__aenter__(self)` | `async with x as v:` 들어갈 때 | 어웨이터블(보통 `async def`로 정의) | 15 |
| `__aexit__(self, exc_type, exc_value, traceback)` | `async with` 블록을 나올 때 | 어웨이터블. 기다린 결과의 의미는 `__exit__`과 같음 | 15 |

```python
import asyncio

class Countdown:
    def __init__(self, n: int) -> None:
        self.n = n

    def __aiter__(self) -> "Countdown":       # async for
        return self

    async def __anext__(self) -> int:
        if self.n == 0:
            raise StopAsyncIteration
        await asyncio.sleep(0)
        self.n -= 1
        return self.n + 1

class Session:
    async def __aenter__(self) -> "Session":  # async with
        print("접속")
        return self

    async def __aexit__(self, *exc: object) -> None:
        print("종료")

class Ready:
    def __await__(self):                      # await Ready()
        yield from asyncio.sleep(0).__await__()
        return "준비 완료"

async def main() -> None:
    async with Session():
        print([n async for n in Countdown(3)])
        print(await Ready())

asyncio.run(main())
# 접속 / [3, 2, 1] / 준비 완료 / 종료 (한 줄씩 출력)
```

## 버퍼 프로토콜

`bytes`, `bytearray`, `memoryview`처럼 메모리 덩어리를 복사 없이 넘겨주는 규약입니다. 예전에는 C로만 구현할 수 있었는데, 3.12부터 파이썬 클래스에서도 구현할 수 있게 됐어요(PEP 688). 이 메서드가 있는 클래스는 `collections.abc.Buffer`로 검사할 수 있습니다.

| 메서드 | 언제 불리나 | 돌려줘야 하는 것 | 관련 장 |
|---|---|---|---|
| `__buffer__(self, flags)` | `memoryview(x)`, `bytes(x)`처럼 버퍼를 요청할 때(3.12부터). `flags`는 `inspect.BufferFlags`로 해석 | `memoryview` | |
| `__release_buffer__(self, buffer)` | 받아 간 버퍼를 다 썼을 때(3.12부터). 정리할 게 없으면 생략 가능 | `None` | |

```python
from collections.abc import Buffer

class Payload:
    def __init__(self, text: str) -> None:
        self.data = bytearray(text.encode())

    def __buffer__(self, flags: int) -> memoryview:   # memoryview(), bytes()
        return memoryview(self.data)

p = Payload("가")
print(bytes(p), memoryview(p).nbytes, isinstance(p, Buffer))   # b'\xea\xb0\x80' 3 True
```

## 파이썬 3에서 쓰지 않는 이름

예전 자료에서 아래 이름을 보면 파이썬 2 시절 코드입니다. 파이썬 3에서 정의해도 오류는 나지 않지만 **아무도 부르지 않는** 평범한 메서드가 될 뿐이에요. 11장에서 말한 `__div__`, `__long__`, `__oct__`, `__hex__`도 여기 들어 있습니다. 3.12의 `object`, `int`, `float`, `str`, `list`, `type` 어디에도 이 이름들이 없는 것을 `hasattr()`로 확인했습니다.

| 파이썬 2 이름 | 하던 일 | 파이썬 3에서는 |
|---|---|---|
| `__div__`, `__rdiv__`, `__idiv__` | `/` 연산 | `__truediv__`(`/`)와 `__floordiv__`(`//`)로 나뉨, 반사·제자리도 같음 |
| `__cmp__`, `__rcmp__` | 크기 비교를 한 메서드로(음수·0·양수) | 비교 메서드 여섯 개, 또는 `functools.total_ordering`. 정렬 키는 `functools.cmp_to_key` |
| `__nonzero__` | `bool(x)` | `__bool__` |
| `__unicode__` | `unicode(x)` | `__str__`(파이썬 3의 `str`이 곧 유니코드) |
| `__str__`이 바이트를 돌려주던 것 | `str(x)` | 바이트 표현은 `__bytes__`로 분리 |
| `__long__` | `long(x)` | `__int__`(`int`와 `long`이 합쳐짐) |
| `__oct__`, `__hex__` | `oct(x)`, `hex(x)` | `__index__`가 정수를 돌려주면 `oct()`·`hex()`·`bin()`이 동작 |
| `__coerce__` | 혼합 타입 연산 전에 타입 맞추기 | 없앰. 모르는 타입이면 `NotImplemented`를 돌려줌 |
| `__getslice__`, `__setslice__`, `__delslice__` | `x[i:j]` | `__getitem__`·`__setitem__`·`__delitem__`이 `slice` 객체를 받음 |
| `next(self)` (밑줄 없음) | 반복자의 다음 값 | `__next__` |
| `__metaclass__ = M` (클래스 속성) | 메타클래스 지정 | `class C(metaclass=M):` |

```python
class OldWon:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __nonzero__(self) -> bool:            # 파이썬 2의 진릿값 메서드
        return self.amount != 0

    def __div__(self, n: int) -> "OldWon":    # 파이썬 2의 / 메서드
        return OldWon(self.amount // n)

zero = OldWon(0)
print(bool(zero))                             # True (__nonzero__는 무시되고 기본값)
try:
    zero / 2
except TypeError as e:
    print("[X]", e)   # [X] unsupported operand type(s) for /: 'OldWon' and 'int'
```
