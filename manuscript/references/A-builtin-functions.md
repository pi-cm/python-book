# 레퍼런스 A. 내장 함수

`len()`, `print()`처럼 아무것도 `import`하지 않고 바로 부를 수 있는 함수를 **내장 함수**라고 합니다. 이름은 기억나는데 인자 순서가 헷갈릴 때, 또는 "이런 일을 하는 함수가 이미 있지 않았나?" 싶을 때 이 표를 펼쳐 보세요. Python 3.12 기준으로 71개 전부를 용도별로 묶었고, 맨 뒤에 알파벳순 색인을 붙였습니다.

### 표 읽는 법

- **시그니처**는 공식 문서 표기를 따릅니다. 부르는 형태가 여럿이면 "또는"으로 나란히 적었습니다(`int(x=0)` 또는 `int(x, base=10)`).
- 괄호 안의 `/`는 "이 앞의 인자는 위치로만 넘긴다", `*`는 "이 뒤의 인자는 키워드로만 넘긴다"는 뜻이에요. 예를 들어 `sorted(iterable, /, *, key=None, reverse=False)`는 `sorted(data, reverse=True)`로는 부를 수 있지만 `sorted(data, None, True)`로는 부를 수 없습니다.
- **예와 결과**는 모두 Python 3.12에서 실행해 확인한 값입니다. 쉼표로 여러 예를 나열한 칸은 결과도 같은 순서로 쉼표로 나열했어요. `;`로 이어 쓴 칸은 앞 문장을 실행한 뒤 마지막 식의 값을 적었습니다.
- **장**은 본문에서 그 함수를 다루는 장 번호입니다. `—`는 본문에서 따로 다루지 않는 함수예요.
- 객체·속성 표의 `p`는 `class P: pass`로 만든 빈 클래스의 인스턴스 `p = P()`입니다.

## 숫자와 계산

| 이름(시그니처) | 하는 일 | 예와 결과 | 장 |
|---|---|---|---|
| `abs(x)` | 절댓값을 돌려줍니다. 복소수는 크기(거리)를 줍니다. | `abs(-7), abs(3+4j)` → `7, 5.0` | 03 |
| `divmod(a, b)` | 몫과 나머지를 튜플 `(a // b, a % b)`로 한 번에 돌려줍니다. | `divmod(17, 5), divmod(-17, 5)` → `(3, 2), (-4, 3)` | 03 |
| `pow(base, exp, mod=None)` | 거듭제곱. `mod`를 주면 `(base ** exp) % mod`를 빠르게 계산합니다. | `pow(2, 10), pow(2, 10, 1000)` → `1024, 24` | 03(`**`) |
| `round(number, ndigits=None)` | 반올림. 정확히 절반이면 짝수 쪽으로 보냅니다(은행가 반올림). | `round(2.5), round(3.5), round(3.14159, 2)` → `2, 4, 3.14` | 03 |
| `sum(iterable, /, start=0)` | 합계. `start`부터 더해 나갑니다. 문자열 이어 붙이기에는 `str.join()`을 씁니다. | `sum([1, 2, 3]), sum([[1], [2]], start=[])` → `6, [1, 2]` | 05 |
| `max(iterable, *, key=None, default)` 또는 `max(a, b, *args, key=None)` | 가장 큰 값. 빈 반복 가능 객체는 `default`가 없으면 `ValueError`. | `max(3, 9, 4), max(['apple', 'fig'], key=len), max([], default=0)` → `9, 'apple', 0` | 06 |
| `min(iterable, *, key=None, default)` 또는 `min(a, b, *args, key=None)` | 가장 작은 값. 사용법은 `max()`와 같습니다. | `min(3, 9, 4), min('python')` → `3, 'h'` | 06 |

## 형 변환과 자료형 만들기

| 이름(시그니처) | 하는 일 | 예와 결과 | 장 |
|---|---|---|---|
| `bool(x=False)` | 진릿값으로 바꿉니다. `0`, `''`, `[]`, `None` 등 빈 값은 `False`. | `bool(0), bool('0'), bool([])` → `False, True, False` | 02 |
| `int(x=0)` 또는 `int(x, base=10)` | 정수로 바꿉니다. 실수는 0 쪽으로 버리고, 문자열은 `base` 진법으로 읽습니다. | `int(3.9), int(-3.9), int('ff', 16), int('0b101', 0)` → `3, -3, 255, 5` | 02 |
| `float(x=0.0)` | 실수로 바꿉니다. `'inf'`, `'nan'` 같은 문자열도 읽습니다. | `float('3.5'), float(7), float('inf')` → `3.5, 7.0, inf` | 02 |
| `complex(real=0, imag=0)` 또는 `complex(string)` | 복소수를 만듭니다. 허수 단위는 `j`. | `complex(1, 2), complex('3-4j')` → `(1+2j), (3-4j)` | 02 |
| `str(object='')` 또는 `str(object, encoding, errors)` | 문자열로 바꿉니다. 바이트에 `encoding`을 주면 디코딩합니다. | `str(42), str(b'hi', 'utf-8')` → `'42', 'hi'` | 02 |
| `bytes(source=b'', encoding, errors)` | 변경 불가능한 바이트열. 정수 n이면 0으로 채운 n바이트. | `bytes(3), bytes('가', 'utf-8'), bytes([65, 66])` → `b'\x00\x00\x00', b'\xea\xb0\x80', b'AB'` | 12 |
| `bytearray(source=b'', encoding, errors)` | 변경 가능한 바이트열. 사용법은 `bytes()`와 같습니다. | `b = bytearray(b'abc'); b[0] = 65; b` → `bytearray(b'Abc')` | 02 |
| `memoryview(object)` | 바이트 객체를 복사하지 않고 들여다보는 창을 만듭니다. | `m = memoryview(b'abcd'); m[1:3].tobytes()` → `b'bc'` | — |
| `list(iterable=())` | 리스트를 만듭니다. | `list('abc'), list(range(3))` → `['a', 'b', 'c'], [0, 1, 2]` | 06 |
| `tuple(iterable=())` | 튜플을 만듭니다. | `tuple([1, 2]), tuple('ab')` → `(1, 2), ('a', 'b')` | 06 |
| `dict(**kwargs)` 또는 `dict(mapping_or_iterable, **kwargs)` | 딕셔너리를 만듭니다. 키-값 쌍 목록이나 키워드 인자를 받습니다. | `dict(a=1, b=2), dict([('x', 1)])` → `{'a': 1, 'b': 2}, {'x': 1}` | 07 |
| `set(iterable=())` | 집합을 만듭니다. 중복이 사라집니다. 빈 집합은 `{}`가 아니라 `set()`. | `set([3, 1, 3, 2]), set()` → `{1, 2, 3}, set()` | 07 |
| `frozenset(iterable=())` | 변경 불가능한 집합. 해시 가능해서 딕셔너리 키나 집합 원소가 됩니다. | `frozenset([1, 1, 2])` → `frozenset({1, 2})` | 07 |

## 문자, 진법, 표현

| 이름(시그니처) | 하는 일 | 예와 결과 | 장 |
|---|---|---|---|
| `bin(x)` | 정수를 `0b` 붙은 2진 문자열로. | `bin(10), bin(-3)` → `'0b1010', '-0b11'` | 02 |
| `oct(x)` | 정수를 `0o` 붙은 8진 문자열로. | `oct(8), oct(493)` → `'0o10', '0o755'` | 02 |
| `hex(x)` | 정수를 `0x` 붙은 16진 문자열로. | `hex(255), hex(-1)` → `'0xff', '-0x1'` | 02 |
| `chr(i)` | 유니코드 코드 포인트(정수)를 문자로. | `chr(65), chr(44032)` → `'A', '가'` | 02 |
| `ord(c)` | 문자 한 개를 코드 포인트(정수)로. `chr()`의 반대입니다. | `ord('A'), ord('가')` → `65, 44032` | 02 |
| `repr(object)` | 개발자용 문자열 표현. 대개 다시 코드로 쓸 수 있는 모양입니다. | `repr('hi'), repr([1, 'a'])` → `'hi', [1, 'a']` | 11 |
| `ascii(object)` | `repr()`과 같되 ASCII 밖의 문자를 `\x`, `\u` 이스케이프로 바꿉니다. | `ascii('가a')` → `'\uac00a'` | — |
| `format(value, format_spec='')` | 형식 지정자로 값을 문자열로. f-문자열의 `:` 뒤와 같은 문법입니다. | `format(3.14159, '.2f'), format(1234567, ','), format(5, '08b')` → `'3.14', '1,234,567', '00000101'` | — |

## 시퀀스와 반복

| 이름(시그니처) | 하는 일 | 예와 결과 | 장 |
|---|---|---|---|
| `len(s)` | 원소 개수(길이)를 돌려줍니다. | `len('파이썬'), len({'a': 1})` → `3, 1` | 06 |
| `range(stop)` 또는 `range(start, stop, step=1)` | 정수 범위. `stop`은 포함하지 않습니다. 메모리를 거의 쓰지 않습니다. | `list(range(2, 10, 3)), list(range(3, 0, -1))` → `[2, 5, 8], [3, 2, 1]` | 05 |
| `enumerate(iterable, start=0)` | `(번호, 원소)` 쌍을 차례로 내놓습니다. | `list(enumerate('ab', start=1))` → `[(1, 'a'), (2, 'b')]` | 05 |
| `zip(*iterables, strict=False)` | 여러 반복 가능 객체를 짝지어 튜플로. 가장 짧은 쪽에서 멈춥니다. `strict=True`(3.10+)면 길이가 다를 때 `ValueError`. | `list(zip('ab', [1, 2, 3]))` → `[('a', 1), ('b', 2)]` | 05 |
| `map(function, iterable, *iterables)` | 각 원소에 함수를 적용한 결과를 지연 반복자로 돌려줍니다. | `list(map(str.upper, ['a', 'b'])), list(map(pow, [2, 3], [3, 2]))` → `['A', 'B'], [8, 9]` | 10 |
| `filter(function, iterable)` | 함수가 참을 돌려준 원소만 남깁니다. `function`이 `None`이면 참인 원소만. | `list(filter(None, [0, 1, '', 'a']))` → `[1, 'a']` | 10 |
| `sorted(iterable, /, *, key=None, reverse=False)` | 정렬한 **새 리스트**를 돌려줍니다. 원본은 그대로입니다. 안정 정렬. | `sorted([3, 1, 2], reverse=True), sorted(['bb', 'a'], key=len)` → `[3, 2, 1], ['a', 'bb']` | 06 |
| `reversed(seq)` | 거꾸로 도는 반복자를 돌려줍니다. | `list(reversed([1, 2, 3])), ''.join(reversed('abc'))` → `[3, 2, 1], 'cba'` | 05 |
| `iter(object)` 또는 `iter(callable, sentinel)` | 반복자를 꺼냅니다. 두 번째 형태는 `sentinel`이 나올 때까지 함수를 부릅니다. | `it = iter([1, 2]); next(it)` → `1` | 15 |
| `next(iterator)` 또는 `next(iterator, default)` | 다음 원소를 꺼냅니다. 다 쓰면 `StopIteration`, `default`가 있으면 그 값. | `it = iter([1]); next(it), next(it, '끝')` → `1, '끝'` | 15 |
| `aiter(async_iterable)` | 비동기 반복자를 꺼냅니다(3.10+). `iter()`의 비동기판. | `it = aiter(agen())` → 비동기 반복자 | 15 |
| `anext(async_iterator)` 또는 `anext(async_iterator, default)` | 비동기 반복자의 다음 원소를 기다릴 객체로(3.10+). `await`와 함께 씁니다. | `await anext(it, '끝')` → `'끝'` | 15 |
| `all(iterable)` | 모든 원소가 참이면 `True`. 빈 것은 `True`. | `all([1, 2, 3]), all([1, 0]), all([])` → `True, False, True` | 10 |
| `any(iterable)` | 하나라도 참이면 `True`. 빈 것은 `False`. | `any([0, '', 5]), any([])` → `True, False` | 04 |
| `slice(stop)` 또는 `slice(start, stop, step=None)` | 슬라이스 객체. `s[1:3]`은 `s[slice(1, 3)]`과 같습니다. | `'python'[slice(1, 4)], 'python'[slice(None, None, -1)]` → `'yth', 'nohtyp'` | 06(슬라이싱) |

## 객체, 타입, 속성

| 이름(시그니처) | 하는 일 | 예와 결과 | 장 |
|---|---|---|---|
| `type(object)` 또는 `type(name, bases, dict)` | 객체의 타입을 돌려줍니다. 인자 셋이면 클래스를 새로 만듭니다. | `type(3), type('C', (), {'x': 1}).x` → `<class 'int'>, 1` | 02, 16 |
| `isinstance(object, classinfo)` | 객체가 그 클래스(또는 하위 클래스)의 인스턴스인지. 튜플이나 `int` \| `str`도 됩니다. | `isinstance(True, int), isinstance(3, (str, float))` → `True, False` | 04, 13 |
| `issubclass(class, classinfo)` | 클래스가 다른 클래스의 하위 클래스인지. 자기 자신도 `True`. | `issubclass(bool, int), issubclass(int, int)` → `True, True` | — |
| `callable(object)` | 호출할 수 있는 객체(함수, 클래스, `__call__` 있는 인스턴스)인지. | `callable(len), callable(3)` → `True, False` | 13 |
| `id(object)` | 객체의 고유 번호. 살아 있는 동안 바뀌지 않습니다. `is`는 이 값을 비교합니다. | `a = []; b = a; id(a) == id(b)` → `True` | 02 |
| `hash(object)` | 해시값(정수). 딕셔너리 키와 집합 원소가 되려면 필요합니다. 리스트는 `TypeError`. | `hash(1) == hash(1.0), hash((1, 2)) == hash((1, 2))` → `True, True` | 07 |
| `dir(object)` | 속성 이름 목록. 인자가 없으면 현재 이름 공간의 이름 목록. | `'append' in dir([]), dir(None)[:2]` → `True, ['__bool__', '__class__']` | 14 |
| `vars(object)` | 객체의 `__dict__`를 돌려줍니다. 인자가 없으면 `locals()`와 같습니다. | `p.x = 1; vars(p)` → `{'x': 1}` | — |
| `getattr(object, name)` 또는 `getattr(object, name, default)` | 이름(문자열)으로 속성을 읽습니다. 없으면 `AttributeError`, `default`가 있으면 그 값. | `getattr('abc', 'upper')(), getattr(3, 'nope', None)` → `'ABC', None` | 16 |
| `setattr(object, name, value)` | 이름(문자열)으로 속성을 씁니다. `obj.name = value`와 같습니다. | `setattr(p, 'x', 5); p.x` → `5` | 16 |
| `hasattr(object, name)` | 속성이 있는지. `getattr()`이 예외 없이 되는지로 판단합니다. | `hasattr([], 'append'), hasattr([], 'push')` → `True, False` | 13 |
| `delattr(object, name)` | 이름(문자열)으로 속성을 지웁니다. `del obj.name`과 같습니다. | `p.x = 1; delattr(p, 'x'); hasattr(p, 'x')` → `False` | 16 |
| `super()` 또는 `super(type, object_or_type=None)` | 부모(MRO에서 다음) 클래스의 메서드를 부르는 대리 객체. | 아래 예제 → `'B+A'` | 13 |
| `object()` | 모든 클래스의 뿌리. 속성을 붙일 수 없는 빈 객체를 만듭니다. | `isinstance(3, object), type(object())` → `True, <class 'object'>` | 11 |

`super()`는 클래스 안에서 써야 해서 따로 적었습니다.

```python
class A:
    def hi(self):
        return 'A'

class B(A):
    def hi(self):
        return 'B+' + super().hi()   # 부모 A의 hi()를 부른다

print(B().hi())   # B+A
```

## 클래스를 꾸미는 데코레이터

| 이름(시그니처) | 하는 일 | 예와 결과 | 장 |
|---|---|---|---|
| `@classmethod` | 첫 인자로 클래스(`cls`)를 받는 메서드로 바꿉니다. 대체 생성자에 씁니다. | 아래 예제 → `'C'` | 11 |
| `@staticmethod` | `self`도 `cls`도 받지 않는 메서드로 바꿉니다. | 아래 예제 → `5` | 11 |
| `property(fget=None, fset=None, fdel=None, doc=None)` | 메서드를 속성처럼 읽고 쓰게 합니다. 보통 `@property`로 씁니다. | 아래 예제 → `6` | 11 |

세 데코레이터를 한 클래스에 모아 보면 차이가 잘 보입니다.

```python
class Circle:
    PI = 3.14

    def __init__(self, r):
        self.r = r

    @classmethod
    def unit(cls):            # cls == Circle, 대체 생성자
        return cls(1)

    @staticmethod
    def is_valid(r):          # self도 cls도 없다, 그냥 함수
        return r > 0

    @property
    def area(self):           # 괄호 없이 c.area로 읽는다
        return self.PI * self.r ** 2

c = Circle.unit()
print(c.r, Circle.is_valid(-1), c.area)   # 1 False 3.14
```

## 입출력

| 이름(시그니처) | 하는 일 | 예와 결과 | 장 |
|---|---|---|---|
| `print(*objects, sep=' ', end='\n', file=None, flush=False)` | 값을 출력합니다. 사이에 `sep`, 끝에 `end`를 붙입니다. | `print(1, 2, 3, sep='-', end='!')` → 출력 `1-2-3!` | 01 |
| `input(prompt='')` | 한 줄을 읽어 **문자열**로 돌려줍니다(줄바꿈 제외). 숫자는 `int()`로 바꿔 씁니다. | `int(input('나이: '))` → 입력 25 → `25` | 01 |
| `open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)` | 파일을 열어 파일 객체를 돌려줍니다. `with`와 함께 쓰고, 텍스트 모드는 `encoding='utf-8'`을 명시합니다. | `with open('a.txt', 'w', encoding='utf-8') as f: f.write('hi')` → `a.txt`에 `hi` 기록 | 12 |

## 실행, 이름 공간, 도움말

| 이름(시그니처) | 하는 일 | 예와 결과 | 장 |
|---|---|---|---|
| `eval(expression, globals=None, locals=None)` | 문자열 **식**을 계산합니다. 외부 입력에 쓰면 위험합니다. | `eval('2 + 3 * 4'), eval('x * 2', {'x': 5})` → `14, 10` | 03 |
| `exec(object, globals=None, locals=None, /, *, closure=None)` | 문자열(또는 코드 객체) **문장**을 실행합니다. 늘 `None`을 돌려줍니다. | `ns = {}; exec('y = 10', ns); ns['y']` → `10` | — |
| `compile(source, filename, mode, flags=0, dont_inherit=False, optimize=-1)` | 소스를 코드 객체로 컴파일합니다. `mode`는 `'exec'`, `'eval'`, `'single'`. | `eval(compile('1 + 1', '<s>', 'eval'))` → `2` | — |
| `globals()` | 모듈 전역 이름 공간 딕셔너리. | `x = 1; 'x' in globals()` → `True` | 09 |
| `locals()` | 현재 지역 이름 공간 딕셔너리(함수 안에서는 복사본). | `f = lambda a: locals(); f(1)` → `{'a': 1}` | 09 |
| `__import__(name, globals=None, locals=None, fromlist=(), level=0)` | `import` 문이 내부에서 부르는 함수. 직접 쓸 일은 드물고 `importlib.import_module()`을 씁니다. | `__import__('math').sqrt(16)` → `4.0` | — |
| `breakpoint(*args, **kws)` | 그 자리에서 디버거(기본 `pdb`)를 띄웁니다. 환경 변수 `PYTHONBREAKPOINT=0`이면 무시합니다. | `breakpoint()` → `(Pdb)` 프롬프트 | — |
| `help(request)` | 대화형 도움말을 보여 줍니다. 독스트링을 읽어 옵니다. | `help(len)` → `len(obj, /)` 설명 출력 | 10, 14 |

## 목록에 넣지 않은 것

`dir(builtins)`에는 함수 말고도 이름이 더 있습니다. 아래는 일부러 뺀 것들이에요.

| 이름 | 빠진 이유 |
|---|---|
| `True` `False` `None` `Ellipsis` `NotImplemented` `__debug__` | 함수가 아니라 내장 상수입니다(레퍼런스 B의 키워드 표 참고). |
| `ValueError` 등 예외 클래스 69개 | 레퍼런스 C에 따로 정리했습니다. |
| `exit` `quit` `copyright` `credits` `license` | `site` 모듈이 대화형 셸을 위해 넣어 두는 객체입니다. 프로그램 안에서는 `sys.exit()`를 씁니다. |
| `__build_class__` `__loader__` `__name__` `__doc__` 등 | 인터프리터 내부용입니다. |

## 알파벳순 색인

71개 전체를 알파벳순으로 모았습니다. 분류 이름이 곧 위의 절 제목이에요.

| 이름 | 분류 | 이름 | 분류 |
|---|---|---|---|
| `abs()` | 숫자와 계산 | `isinstance()` | 객체, 타입, 속성 |
| `aiter()` | 시퀀스와 반복 | `issubclass()` | 객체, 타입, 속성 |
| `all()` | 시퀀스와 반복 | `iter()` | 시퀀스와 반복 |
| `anext()` | 시퀀스와 반복 | `len()` | 시퀀스와 반복 |
| `any()` | 시퀀스와 반복 | `list()` | 형 변환과 자료형 만들기 |
| `ascii()` | 문자, 진법, 표현 | `locals()` | 실행, 이름 공간, 도움말 |
| `bin()` | 문자, 진법, 표현 | `map()` | 시퀀스와 반복 |
| `bool()` | 형 변환과 자료형 만들기 | `max()` | 숫자와 계산 |
| `breakpoint()` | 실행, 이름 공간, 도움말 | `memoryview()` | 형 변환과 자료형 만들기 |
| `bytearray()` | 형 변환과 자료형 만들기 | `min()` | 숫자와 계산 |
| `bytes()` | 형 변환과 자료형 만들기 | `next()` | 시퀀스와 반복 |
| `callable()` | 객체, 타입, 속성 | `object()` | 객체, 타입, 속성 |
| `chr()` | 문자, 진법, 표현 | `oct()` | 문자, 진법, 표현 |
| `@classmethod` | 클래스를 꾸미는 데코레이터 | `open()` | 입출력 |
| `compile()` | 실행, 이름 공간, 도움말 | `ord()` | 문자, 진법, 표현 |
| `complex()` | 형 변환과 자료형 만들기 | `pow()` | 숫자와 계산 |
| `delattr()` | 객체, 타입, 속성 | `print()` | 입출력 |
| `dict()` | 형 변환과 자료형 만들기 | `property()` | 클래스를 꾸미는 데코레이터 |
| `dir()` | 객체, 타입, 속성 | `range()` | 시퀀스와 반복 |
| `divmod()` | 숫자와 계산 | `repr()` | 문자, 진법, 표현 |
| `enumerate()` | 시퀀스와 반복 | `reversed()` | 시퀀스와 반복 |
| `eval()` | 실행, 이름 공간, 도움말 | `round()` | 숫자와 계산 |
| `exec()` | 실행, 이름 공간, 도움말 | `set()` | 형 변환과 자료형 만들기 |
| `filter()` | 시퀀스와 반복 | `setattr()` | 객체, 타입, 속성 |
| `float()` | 형 변환과 자료형 만들기 | `slice()` | 시퀀스와 반복 |
| `format()` | 문자, 진법, 표현 | `sorted()` | 시퀀스와 반복 |
| `frozenset()` | 형 변환과 자료형 만들기 | `@staticmethod` | 클래스를 꾸미는 데코레이터 |
| `getattr()` | 객체, 타입, 속성 | `str()` | 형 변환과 자료형 만들기 |
| `globals()` | 실행, 이름 공간, 도움말 | `sum()` | 숫자와 계산 |
| `hasattr()` | 객체, 타입, 속성 | `super()` | 객체, 타입, 속성 |
| `hash()` | 객체, 타입, 속성 | `tuple()` | 형 변환과 자료형 만들기 |
| `help()` | 실행, 이름 공간, 도움말 | `type()` | 객체, 타입, 속성 |
| `hex()` | 문자, 진법, 표현 | `vars()` | 객체, 타입, 속성 |
| `id()` | 객체, 타입, 속성 | `zip()` | 시퀀스와 반복 |
| `input()` | 입출력 | `__import__()` | 실행, 이름 공간, 도움말 |
| `int()` | 형 변환과 자료형 만들기 |  |  |
