# Chapter 16: 메타프로그래밍과 고급 기법

> **학습 목표**  
> - 데코레이터로 함수에 기능을 덧입히기
> - 메타클래스와 __init_subclass__로 클래스 만들기에 끼어들기
> - 디스크립터로 속성 접근을 제어하기
> - 컨텍스트 매니저로 자원을 안전하게 열고 닫기

---

파이썬의 메타프로그래밍은 프로그램이 다른 프로그램을 조작하거나 자기 자신을 수정할 수 있는 강력한 기능입니다. 이 장에서는 데코레이터, 메타클래스, 디스크립터 등 파이썬의 고급 기법들을 체계적으로 학습하겠습니다.

## 들어가며: 코드를 다루는 코드

지금까지 우리는 숫자, 문자열, 리스트 같은 **데이터**를 다루는 코드를 짰습니다. 이 장에서는 한 단계 올라가서 함수와 클래스 같은 **코드 그 자체**를 재료로 다루는 코드를 짭니다. 이것을 **메타프로그래밍(metaprogramming)** 이라고 해요. 요리에 비유하면, 지금까지는 레시피대로 요리를 했다면 이제는 "모든 레시피에 '손 씻기' 단계를 자동으로 넣어 주는 레시피"를 만드는 셈입니다.

이게 가능한 이유는 파이썬에서는 **모든 것이 객체**이기 때문입니다. 함수도 예외가 아니에요. 확인해 볼까요? `print(print)`를 실행하면 `<built-in function print>`가 나옵니다. "입력을 출력하라"는 함수에게 자기 자신을 출력하라고 시켰더니, 함수 그 자체를 가리키는 정보가 나온 거죠. 그러니 `출력 = print`처럼 함수를 다른 이름에 담아 `출력("안녕")`으로 똑같이 쓸 수도 있고, 함수를 리스트에 넣거나, 다른 함수에 인자로 넘기거나, 함수에서 함수를 돌려줄 수도 있습니다. 숫자나 문자열과 똑같은 대접을 받는다고 해서 이런 함수를 **일급 객체(first-class object)** 라고 불러요. 10장에서 고차 함수와 클로저를 다룰 수 있었던 것도 이 덕분입니다.

이 장에서 볼 기법들은 모두 이 성질 위에 서 있습니다.

- **데코레이터**: 함수를 받아서 기능을 덧붙인 새 함수를 돌려줍니다.
- **메타클래스**: 클래스가 만들어지는 과정 자체에 끼어듭니다.
- **디스크립터**: `객체.속성`으로 값을 읽고 쓰는 순간에 끼어듭니다.
- **컨텍스트 매니저**: `with` 블록에 들어가고 나오는 순간에 끼어듭니다.

강력한 만큼 남용하면 "도대체 이 값이 어디서 바뀌는 거지?" 하고 코드를 읽는 사람을 괴롭힙니다. 그래서 각 절에서 **언제 쓰고 언제 참아야 하는지**도 함께 살펴보겠습니다.

이 장의 예제는 대부분 pytest 테스트 클래스 모양입니다. 각 기능이 어떻게 동작해야 하는지를 `assert`로 적어 두었으니, 코드를 읽을 때 `assert` 줄을 "이렇게 동작한다"는 설명으로 읽으면 됩니다. 직접 확인하려면 1.1절 예제의 `import` 세 줄(`time`, `pytest`, `wraps`)을 맨 위에 둔 한 파일에 예제들을 모으고 `uv run --with pytest pytest 파일이름.py`로 실행하세요.

## 1. 데코레이터 (Decorators)

데코레이터는 함수나 클래스의 동작을 수정하거나 확장하는 우아한 방법입니다.

케이크를 떠올려 보세요. 맛있는 시트(원래 함수)는 그대로 두고, 그 위에 크림과 장식(추가 기능)을 얹는 것이 데코레이션이죠. 10.4절에서 데코레이터의 기본 모양을 봤으니, 여기서는 **그 안에서 실제로 무슨 일이 일어나는지**를 더 깊이 들여다봅니다.

> **Q. 데코레이터를 왜 쓰나요? 그냥 함수를 수정하면 안 되나요?**
> 함수 하나라면 고치면 됩니다. 하지만 "실행 시간을 재고 싶은 함수"가 30개라면요? 30개 함수에 시간 재는 코드를 일일이 넣었다가, 나중에 기록 형식이 바뀌면 또 30군데를 고쳐야 합니다. 데코레이터로 만들어 두면 기능은 한 곳에만 있고, 각 함수 위에는 `@measure_time` 한 줄만 붙이면 됩니다. 원래 함수의 코드는 한 글자도 건드리지 않고요. 디버깅할 때 어떤 함수가 어떤 순서로 불렸는지 찍어 보거나, 웹 서버에서 요청마다 걸린 시간을 재는 것이 대표적인 쓰임입니다.

`@` 기호는 사실 문법 설탕(syntactic sugar), 즉 같은 일을 짧게 쓰게 해 주는 표기일 뿐입니다. 아래처럼 `@` 없이 써 보면 정체가 드러나요.

```python
def 큰소리(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper


def 인사(이름):
    return f"hello, {이름}"

인사 = 큰소리(인사)   # @큰소리 와 똑같은 일
print(인사("kim"))
print(인사.__name__)
```

```
HELLO, KIM
wrapper
```

`@큰소리`를 함수 위에 붙이는 것은 함수를 정의한 직후에 `인사 = 큰소리(인사)`를 실행하는 것과 완전히 같습니다. 데코레이터는 **함수를 받아서 함수를 돌려주는 함수**이고, 원래 이름표 `인사`가 이제 새 함수 `wrapper`에 붙은 거죠. `wrapper`가 원래 함수 `func`를 기억하고 있는 것은 10.5절에서 본 **클로저** 덕분입니다. 바깥 함수 `큰소리`의 실행은 이미 끝났는데도, 안쪽 함수 `wrapper`는 바깥의 `func`를 계속 붙들고 있어요.

그런데 두 번째 줄을 보세요. 함수 이름을 물었더니 `인사`가 아니라 `wrapper`라고 답합니다. 이름표가 바뀌었으니 당연한 결과지만, 에러 메시지나 로그, 문서화 도구가 엉뚱한 이름을 보여 주게 되죠. 이 문제를 해결하는 것이 아래 예제에 나오는 `functools.wraps`입니다.

### 1.1 함수 데코레이터

먼저 기본적인 함수 데코레이터부터 살펴보겠습니다. `wrapper` 위에 `@wraps(func)`를 붙이면 원래 함수의 이름(`__name__`)과 docstring 같은 정보를 `wrapper`에 그대로 복사해 줍니다. 데코레이터를 만들 때는 습관처럼 붙이세요.

```python
# test_decorators.py
import time
import pytest
from functools import wraps

class TestFunctionDecorators:
    def test_simple_decorator(self):
        """간단한 데코레이터 테스트"""
        def debug(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                print(f"호출: {func.__name__}")
                result = func(*args, **kwargs)
                print(f"완료: {func.__name__}")
                return result
            return wrapper
        
        @debug
        def 인사하기(이름):
            return f"안녕하세요, {이름}님!"
        
        result = 인사하기("김철수")
        assert result == "안녕하세요, 김철수님!"
        assert 인사하기.__name__ == "인사하기"  # functools.wraps 덕분
    
    def test_timing_decorator(self):
        """실행 시간 측정 데코레이터"""
        def measure_time(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                end = time.time()
                wrapper.execution_time = end - start
                return result
            return wrapper
        
        @measure_time
        def 복잡한_계산():
            return sum(range(10000))
        
        result = 복잡한_계산()
        assert result == 49995000
        assert hasattr(복잡한_계산, 'execution_time')
```

첫 번째 테스트의 `debug`는 함수가 불릴 때 "호출"과 "완료"를 찍어서 실행 순서를 추적하게 해 주고, 마지막 `assert`가 `@wraps` 덕분에 이름이 `인사하기`로 유지된다는 것을 확인합니다. 두 번째 `measure_time`에는 재미있는 줄이 하나 있어요. `wrapper.execution_time = end - start`입니다. 함수도 객체라서 이렇게 **함수에 속성을 붙일 수** 있습니다. 실행할 때마다 마지막 실행 시간이 함수 자신에게 기록되는 거죠. 데코레이터에 `*args, **kwargs`를 쓰는 이유도 짚고 가세요. 어떤 모양의 인자를 받는 함수에 붙더라도 받은 그대로 원래 함수에 넘겨주기 위해서입니다.

### 1.2 클래스 데코레이터

클래스 전체에 기능을 추가하는 클래스 데코레이터입니다. 원리는 함수 데코레이터와 똑같아요. `@singleton`을 클래스 위에 붙이면 `데이터베이스연결 = singleton(데이터베이스연결)`이 실행됩니다. 함수 대신 **클래스를 받아서** 무언가를 돌려줄 뿐이에요. 그리고 데코레이터는 클래스가 정의되는 순간 **딱 한 번** 실행됩니다. 객체를 만들 때마다 실행되는 것이 아니라는 점을 기억해 두세요.

```python
class TestClassDecorators:
    def test_singleton_decorator(self):
        """싱글톤 패턴을 구현하는 클래스 데코레이터"""
        def singleton(cls):
            instance = None
            original_init = cls.__init__

            def __new__(klass, *args, **kwargs):
                nonlocal instance
                if instance is None:  # 처음 한 번만 만들고 초기화
                    instance = object.__new__(klass)
                    original_init(instance, *args, **kwargs)
                return instance

            def __init__(self, *args, **kwargs):
                pass  # 초기화는 __new__에서 한 번만 했으므로 다시 하지 않음

            cls.__new__ = __new__
            cls.__init__ = __init__
            return cls  # 클래스를 그대로 돌려줌
        
        @singleton
        class 데이터베이스연결:
            def __init__(self, 호스트):
                self.호스트 = 호스트
                self.연결됨 = True
        
        db1 = 데이터베이스연결("localhost")
        db2 = 데이터베이스연결("localhost")
        
        assert db1 is db2  # 같은 인스턴스
        assert db1.호스트 == "localhost"
        assert isinstance(db1, 데이터베이스연결)  # 여전히 진짜 클래스
    
    def test_auto_property_decorator(self):
        """자동으로 프로퍼티를 생성하는 데코레이터"""
        def auto_property(cls):
            for attr_name in dir(cls):
                if attr_name.startswith('_') and not attr_name.startswith('__'):
                    property_name = attr_name[1:]  # _ 제거
                    
                    def make_property(attr):
                        def getter(self):
                            return getattr(self, attr)
                        def setter(self, value):
                            setattr(self, attr, value)
                        return property(getter, setter)
                    
                    setattr(cls, property_name, make_property(attr_name))
            return cls
        
        @auto_property
        class 사람:
            # 데코레이터가 정의 시점에 볼 수 있도록 클래스 속성으로 미리 선언
            _이름 = ""
            _나이 = 0

            def __init__(self, 이름, 나이):
                self._이름 = 이름
                self._나이 = 나이
        
        person = 사람("김철수", 30)
        assert person.이름 == "김철수"
        person.나이 = 31
        assert person._나이 == 31
```

**싱글톤(singleton)** 은 프로그램 전체에서 객체를 딱 하나만 만들게 하는 설계 방식입니다. 데이터베이스 연결처럼 여러 개 만들면 낭비인 것에 쓰죠. `singleton`은 받은 클래스의 `__new__`(객체를 만드는 메서드)와 `__init__`(초기화 메서드)을 바꿔 끼웁니다. 처음 부르면 객체를 만들고 원래 `__init__`으로 초기화해서 `instance`에 기억해 두고, 두 번째부터는 기억해 둔 것을 그대로 돌려줘요. 그래서 `db1 is db2`가 참입니다. 새 `__init__`이 아무것도 하지 않는 이유는, 파이썬이 `__new__`가 돌려준 객체에 `__init__`을 매번 다시 부르기 때문이에요. 그대로 두면 두 번째 호출 때 이미 만든 객체가 다시 초기화됩니다. 여기에도 클로저가 쓰였습니다. 바꿔 끼운 `__new__`가 바깥의 `instance`와 `original_init`을 기억하고 있죠.

이 데코레이터는 클래스를 고쳐서 **그 클래스를 그대로** 돌려줍니다. 만약 객체를 만들어 주는 함수를 대신 돌려줬다면 `데이터베이스연결`이라는 이름이 함수를 가리키게 되어, `isinstance(db1, 데이터베이스연결)`이 "두 번째 인자가 클래스가 아니다"라는 `TypeError`를 냈을 거예요. 마지막 `assert`가 클래스가 살아 있다는 것을 확인합니다.

`auto_property`도 받은 클래스에 `setattr`로 프로퍼티를 덧붙인 뒤 그 클래스를 그대로 돌려줍니다. 클래스 데코레이터는 이렇게 "받은 것을 고쳐서 돌려주기"로 쓰는 경우가 많아요. 여기서 기억할 점은 데코레이터가 살펴볼 수 있는 것이 **정의 시점에 클래스에 들어 있는 이름들**(`dir(cls)`)뿐이라는 것입니다. `__init__` 안에서 `self._이름 = ...`으로 만드는 인스턴스 속성은 객체가 만들어질 때에야 생기니까요. 그래서 `사람` 클래스 본문에 `_이름 = ""`, `_나이 = 0`을 미리 적어 두었습니다. 이 두 줄을 지우면 데코레이터가 밑줄 이름을 하나도 찾지 못해 `person.이름`에서 `AttributeError`가 납니다. `make_property(attr_name)`처럼 함수를 한 번 더 감싼 것도 이유가 있어요. 반복문 안에서 `getter`를 바로 만들면 모든 프로퍼티가 반복문의 마지막 `attr_name`을 보게 되는데, 함수 인자로 넘기면 그 순간의 값이 각자 따로 묶입니다.

### 1.3 매개변수가 있는 데코레이터

설정 가능한 데코레이터를 만들어보겠습니다. "최대 3번까지 재시도"처럼 데코레이터에 설정값을 넘기고 싶을 때는 함수가 **세 겹**이 됩니다.

- 바깥: `retry(max_attempts=3, delay=0.1)` → 설정값을 받아서 데코레이터를 돌려줌
- 가운데: `decorator(func)` → 함수를 받아서 wrapper를 돌려줌
- 안쪽: `wrapper(*args, **kwargs)` → 실제로 원래 함수를 실행

`@retry(max_attempts=3, delay=0.01)`에 괄호가 있다는 것에 주목하세요. 파이썬은 먼저 `retry(max_attempts=3, delay=0.01)`을 **실행해서** 그 결과로 나온 `decorator`를 데코레이터로 씁니다. 즉 `불안정한_함수 = retry(max_attempts=3, delay=0.01)(불안정한_함수)`예요. 안쪽 함수들은 클로저로 바깥의 `max_attempts`, `delay`, `func`를 모두 기억합니다.

```python
class TestParameterizedDecorators:
    def test_retry_decorator(self):
        """재시도 데코레이터 (매개변수 포함)"""
        def retry(max_attempts=3, delay=0.1):
            def decorator(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    for attempt in range(max_attempts):
                        try:
                            return func(*args, **kwargs)
                        except Exception as e:
                            if attempt == max_attempts - 1:
                                raise e
                            time.sleep(delay)
                return wrapper
            return decorator
        
        attempt_count = 0
        
        @retry(max_attempts=3, delay=0.01)
        def 불안정한_함수():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("실패!")
            return "성공!"
        
        result = 불안정한_함수()
        assert result == "성공!"
        assert attempt_count == 3
    
    def test_cache_decorator(self):
        """캐시 데코레이터 (TTL 지원)"""
        def cache_with_ttl(ttl_seconds=60):
            def decorator(func):
                cache = {}
                
                @wraps(func)
                def wrapper(*args, **kwargs):
                    key = str(args) + str(sorted(kwargs.items()))
                    now = time.time()
                    
                    if key in cache:
                        value, timestamp = cache[key]
                        if now - timestamp < ttl_seconds:
                            return value
                    
                    result = func(*args, **kwargs)
                    cache[key] = (result, now)
                    return result
                
                wrapper.clear_cache = lambda: cache.clear()
                return wrapper
            return decorator
        
        call_count = 0
        
        @cache_with_ttl(ttl_seconds=1)
        def 피보나치(n):
            nonlocal call_count
            call_count += 1
            if n <= 1:
                return n
            return 피보나치(n-1) + 피보나치(n-2)
        
        # 첫 번째 호출
        result1 = 피보나치(5)
        count1 = call_count
        
        # 캐시된 호출
        result2 = 피보나치(5)
        count2 = call_count
        
        assert result1 == result2 == 5
        assert count2 == count1  # 캐시 사용으로 호출 수 동일
```

`retry` 테스트에서 `불안정한_함수`는 처음 두 번은 실패하고 세 번째에 성공합니다. 데코레이터가 실패를 삼키고 다시 부른 덕분에 바깥에서는 `"성공!"`만 보여요. 마지막 시도까지 실패하면 그때는 예외를 그대로 다시 일으킵니다. 실패를 조용히 묻어 버리지 않는 거죠.

`cache_with_ttl`은 같은 인자로 다시 부르면 계산하지 않고 저장해 둔 결과를 돌려주되, 저장한 지 `ttl_seconds`초가 지나면 다시 계산합니다(TTL은 Time To Live, 유효 기간이라는 뜻이에요). 그래서 두 번째 `피보나치(5)` 호출에서는 `call_count`가 늘지 않습니다. `wrapper.clear_cache`처럼 데코레이터가 만든 함수에 도우미 기능을 붙여 두는 것도 함수가 객체라서 가능한 일이고요. 참고로 유효 기간 없는 캐시는 표준 라이브러리에 `functools.lru_cache`와 `functools.cache`로 이미 있으니, 직접 만들기 전에 먼저 찾아보세요.

데코레이터는 여러 개를 겹쳐 붙일 수도 있습니다. 이때 순서가 중요해요. **함수에 가까운 것(아래)부터** 감쌉니다.

```python
def 별(func):
    def wrapper():
        return "*" + func() + "*"
    return wrapper


def 괄호(func):
    def wrapper():
        return "(" + func() + ")"
    return wrapper


@별
@괄호
def 이름():
    return "파이썬"

print(이름())
```

결과는 `*(파이썬)*`입니다. `이름 = 별(괄호(이름))`이 실행된 것이라, 괄호가 먼저 감싸고 그 바깥을 별이 감쌌어요. 선물 상자를 포장지로 싸고 리본을 묶으면, 풀 때는 리본부터 풀어야 하는 것과 같습니다.

> **Q. 클래스 안에서 본 `@classmethod`, `@staticmethod`, `@property`도 데코레이터인가요?**
> 네, 모두 파이썬에 내장된 데코레이터입니다. 아무 데코레이터도 붙지 않은 메서드는 인스턴스 메서드라서 첫 번째 인자로 `self`(객체 자신)를 받죠. `@classmethod`를 붙이면 첫 인자로 `cls`(클래스 자신)를 받는 메서드로, `@staticmethod`를 붙이면 아무것도 자동으로 받지 않는 메서드로 바뀝니다. 11.2절에서 쓰는 법을 봤는데, 이 장의 3절에서 `@property`가 속으로는 어떻게 동작하는지 직접 만들어 보면서 확인합니다.

## 2. 메타클래스 (Metaclasses)

메타클래스는 클래스를 만드는 클래스입니다. "클래스의 클래스"라고 생각할 수 있습니다.

붕어빵으로 생각해 봅시다. 붕어빵(객체)은 붕어빵 틀(클래스)로 찍어 냅니다. 그럼 붕어빵 틀은 어디서 나왔을까요? 틀을 만드는 공장이 있겠죠. 그 **틀 공장**이 메타클래스입니다. 파이썬에서는 모든 것이 객체라고 했으니, 클래스도 객체이고, 클래스라는 객체를 찍어 낸 틀도 있어야 합니다. `type()`으로 확인해 볼 수 있어요.

- `type(3)`은 `<class 'int'>`: 3이라는 객체는 `int` 틀로 만들었습니다.
- `type(int)`는 `<class 'type'>`: `int`라는 클래스는 `type` 틀로 만들었습니다.
- `type(type)`도 `<class 'type'>`: `type`은 자기 자신으로 만들어진, 맨 꼭대기의 틀입니다.

우리가 `class 사람:`이라고 쓴 클래스도 `type(사람)`을 해 보면 `<class 'type'>`이 나옵니다. 따로 지정하지 않으면 모든 클래스는 `type`이라는 기본 메타클래스가 만들어요. 그러니 `type`을 상속한 나만의 메타클래스를 만들면, 클래스가 만들어지는 과정에 끼어들 수 있습니다.

### 2.1 클래스 생성 과정 이해

`class` 문은 사실 `type`을 부르는 편한 표기입니다. 파이썬은 `class 사람:` 아래의 본문을 실행해서 그 안에 정의된 이름들을 사전에 모은 뒤, `type('사람', (부모 클래스들), {이름: 값 사전})`을 불러 클래스를 만들어요. 그래서 아래 첫 번째 테스트처럼 `class` 문 없이 `type()`을 직접 불러도 똑같은 클래스가 생깁니다.

두 번째 테스트의 `SingletonMeta`는 `__call__`을 고쳤습니다. `로거()`처럼 **클래스를 함수처럼 부르는** 순간 실행되는 것이 메타클래스의 `__call__`이거든요. 원래는 이 안에서 객체를 새로 만들고 `__init__`을 불러 주는데, 여기서는 이미 만든 객체가 있으면 그것을 돌려주도록 바꿨습니다. 메타클래스는 클래스를 고치지 않고 "부르는 방법"만 바꾸므로, `로거`는 여전히 진짜 클래스라서 `isinstance`도 정상적으로 쓸 수 있어요. 1.2절의 데코레이터처럼 `__new__`와 `__init__`을 바꿔 끼우는 수고도 필요 없죠.

```python
class TestMetaclassBasics:
    def test_type_as_metaclass(self):
        """type을 이용한 동적 클래스 생성"""
        # 일반적인 클래스 정의와 동일한 효과
        def init_method(self, 이름):
            self.이름 = 이름
        
        def 인사_method(self):
            return f"안녕하세요, {self.이름}님!"
        
        # type(name, bases, dict)로 클래스 생성
        사람 = type('사람', (), {
            '__init__': init_method,
            '인사': 인사_method
        })
        
        person = 사람("김철수")
        assert person.이름 == "김철수"
        assert person.인사() == "안녕하세요, 김철수님!"
    
    def test_custom_metaclass(self):
        """커스텀 메타클래스 정의"""
        class SingletonMeta(type):
            _instances = {}
            
            def __call__(cls, *args, **kwargs):
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
                return cls._instances[cls]
        
        class 로거(metaclass=SingletonMeta):
            def __init__(self):
                self.로그들 = []
            
            def 로그(self, 메시지):
                self.로그들.append(메시지)
        
        logger1 = 로거()
        logger2 = 로거()
        
        assert logger1 is logger2
        
        logger1.로그("테스트 메시지")
        assert "테스트 메시지" in logger2.로그들
```

`logger1`에 남긴 메시지가 `logger2`의 `로그들`에도 있다는 것이 마지막 `assert`의 확인 내용입니다. 둘이 같은 객체이니 당연하죠. `_instances`를 메타클래스의 클래스 속성으로 둔 덕분에, 이 메타클래스를 쓰는 클래스가 여러 개여도 클래스마다 하나씩 따로 기억합니다.

### 2.2 메타클래스 활용 예제

메타클래스의 `__new__(mcs, name, bases, namespace)`는 클래스가 만들어지기 **직전**에 불립니다. `name`은 클래스 이름, `bases`는 부모 클래스 튜플, `namespace`는 클래스 본문에서 정의한 이름과 값을 담은 사전이에요. 이 사전을 들여다보고 고친 다음 `super().__new__()`에 넘기면, 고친 내용대로 클래스가 만들어집니다. 클래스를 만드는 사람이 따로 아무것도 하지 않아도 규칙을 강제하거나 기능을 덧붙일 수 있는 거죠.

`test_orm_like_metaclass`가 그 예입니다. `ModelMeta`는 클래스 본문에서 값이 타입(`str` 같은)인 이름들을 골라 `_fields`에 모으고, `save` 메서드를 자동으로 끼워 넣습니다. `사용자` 클래스에는 `save`를 쓴 적이 없는데도 `user.save()`가 동작하는 이유예요. `if name == 'Model':`로 기반 클래스 `Model` 자신은 건너뛰는 것도 눈여겨보세요. `Model`을 상속한 클래스들은 메타클래스도 함께 물려받기 때문에, `class 사용자(Model):`만 써도 `ModelMeta`가 동작합니다. 6절의 ORM이 이 아이디어를 더 발전시킵니다.

첫 번째 테스트의 `ValidatedMeta`는 반대 순서로 일합니다. `super().__new__()`로 클래스를 **먼저 만든 다음**, 완성된 클래스에서 `inspect.get_annotations(cls)`로 `이름: str`, `나이: int` 같은 타입 표시를 읽어 와 검사 규칙으로 삼아요. 그리고 원래 `__init__`을 검사하는 `__init__`으로 바꿔 끼웁니다. 새 `__init__`은 `inspect.signature(...).bind(...)`로 `학생("김철수", 20)`의 위치 인자들을 `이름`, `나이`라는 매개변수 이름에 짝지은 뒤, 각 값이 어노테이션의 타입과 맞는지 확인합니다. 그래서 `학생("김철수", "스무살")`은 객체가 만들어지기도 전에 `TypeError`로 막혀요. 클래스를 정의하는 쪽은 타입만 적었을 뿐인데 검사가 저절로 붙은 거죠.

```python
class TestMetaclassApplications:
    def test_validation_metaclass(self):
        """필드 유효성 검사 메타클래스"""
        import inspect

        class ValidatedMeta(type):
            def __new__(mcs, name, bases, namespace):
                cls = super().__new__(mcs, name, bases, namespace)

                # 유효성 검사 규칙 수집: 클래스 본문의 '이름: 타입' 어노테이션
                validators = inspect.get_annotations(cls)

                def validate_init(original_init):
                    signature = inspect.signature(original_init)

                    @wraps(original_init)
                    def new_init(self, *args, **kwargs):
                        # 위치 인자와 키워드 인자를 매개변수 이름에 짝지음
                        bound = signature.bind(self, *args, **kwargs)
                        for field, value in bound.arguments.items():
                            validator = validators.get(field)
                            if validator and not isinstance(value, validator):
                                raise TypeError(
                                    f"{field}는 {validator.__name__} 타입이어야 합니다"
                                )
                        return original_init(self, *args, **kwargs)
                    return new_init

                if '__init__' in namespace:
                    cls.__init__ = validate_init(namespace['__init__'])

                return cls
        
        class 학생(metaclass=ValidatedMeta):
            이름: str
            나이: int
            
            def __init__(self, 이름, 나이):
                self.이름 = 이름
                self.나이 = 나이
        
        # 정상 생성
        student = 학생("김철수", 20)
        assert student.이름 == "김철수"
        
        # 타입 오류
        with pytest.raises(TypeError):
            학생("김철수", "스무살")  # 나이가 문자열
    
    def test_orm_like_metaclass(self):
        """ORM과 유사한 메타클래스"""
        class ModelMeta(type):
            def __new__(mcs, name, bases, namespace):
                if name == 'Model':
                    return super().__new__(mcs, name, bases, namespace)
                
                # 필드 정보 수집
                fields = {}
                for key, value in namespace.items():
                    if isinstance(value, type):  # 타입 어노테이션
                        fields[key] = value
                
                namespace['_fields'] = fields
                
                # save 메서드 자동 추가
                def save(self):
                    data = {}
                    for field in fields:
                        if hasattr(self, field):
                            data[field] = getattr(self, field)
                    return data
                
                namespace['save'] = save
                
                return super().__new__(mcs, name, bases, namespace)
        
        class Model(metaclass=ModelMeta):
            pass
        
        class 사용자(Model):
            이름 = str
            이메일 = str
            
            def __init__(self, 이름, 이메일):
                self.이름 = 이름
                self.이메일 = 이메일
        
        user = 사용자("김철수", "kim@example.com")
        saved_data = user.save()
        
        assert saved_data == {"이름": "김철수", "이메일": "kim@example.com"}
        assert "이름" in 사용자._fields
```

메타클래스는 이 장에서 가장 강력하지만 가장 조심해서 써야 하는 도구입니다. 한 클래스에 메타클래스가 붙으면 그 클래스를 상속한 모든 클래스에 영향이 가고, 서로 다른 메타클래스를 쓰는 두 클래스를 함께 상속하면 충돌이 나기도 해요. 그래서 "상속받는 클래스마다 무언가를 해 주고 싶다" 정도라면 파이썬 3.6에서 생긴 `__init_subclass__`로 충분한 경우가 많습니다. 부모 클래스에 이 메서드를 정의해 두면 자식 클래스가 정의될 때마다 불립니다.

```python
class Base:
    registry = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Base.registry.append(cls.__name__)   # 자식 클래스가 생길 때마다 등록


class A(Base):
    pass


class B(Base):
    pass

print(Base.registry)   # ['A', 'B']
```

메타클래스 없이 평범한 클래스 메서드 하나로 "자식 클래스 자동 등록"을 해냈죠. 데코레이터나 `__init_subclass__`로 안 되는 일이 있을 때, 그때 메타클래스를 꺼내세요.

## 3. 디스크립터 (Descriptors)

디스크립터는 속성 접근을 제어하는 강력한 도구입니다.

`weather.온도 = 25.5`라고 쓰면 그냥 값이 저장될 것 같죠? 그런데 클래스에 `온도`라는 이름으로 **디스크립터 객체**가 놓여 있으면 이야기가 달라집니다. 파이썬은 값을 바로 저장하지 않고 그 디스크립터의 `__set__`을 불러서 "이 값 저장해 줘"라고 부탁해요. 읽을 때는 `__get__`, `del`로 지울 때는 `__delete__`를 부릅니다. 아파트 경비실과 비슷합니다. 택배(값)를 집(객체) 앞에 바로 두지 않고 경비실(디스크립터)을 거치게 하면, 경비실에서 내용물을 확인하거나 기록을 남길 수 있죠.

세 메서드 중 하나라도 있는 클래스가 디스크립터입니다. 각 매개변수의 뜻은 이렇습니다.

- `__get__(self, obj, objtype)`: `self`는 디스크립터 자신, `obj`는 속성을 읽으려는 객체(`weather`), `objtype`은 그 객체의 클래스(`날씨`)입니다. `날씨.온도`처럼 클래스에서 직접 읽으면 `obj`가 `None`으로 들어오는데, 이때는 보통 디스크립터 자신을 돌려줍니다.
- `__set__(self, obj, value)`: `value`는 저장하려는 값입니다. 여기서 타입이나 범위를 검사할 수 있어요.
- `__delete__(self, obj)`: `del weather.온도`를 했을 때 불립니다.

디스크립터는 혼자서는 의미가 없고, 반드시 **다른 클래스의 클래스 속성**으로 놓여야 동작합니다.

```python
class TestDescriptors:
    def test_basic_descriptor(self):
        """기본 디스크립터 구현"""
        class Temperature:
            def __set_name__(self, owner, name):
                self.name = name  # 이 디스크립터가 붙은 속성 이름 ('온도')
            
            def __get__(self, obj, objtype=None):
                if obj is None:
                    return self
                return obj.__dict__[self.name]  # 값은 인스턴스마다 따로 보관
            
            def __set__(self, obj, value):
                if not isinstance(value, (int, float)):
                    raise TypeError("온도는 숫자여야 합니다")
                if value < -273.15:
                    raise ValueError("절대영도보다 낮을 수 없습니다")
                obj.__dict__[self.name] = value
            
            def __delete__(self, obj):
                raise AttributeError("온도는 삭제할 수 없습니다")
        
        class 날씨:
            온도 = Temperature()
            
            def __init__(self, 온도):
                self.온도 = 온도
        
        weather = 날씨(25.5)
        assert weather.온도 == 25.5
        
        # 객체마다 온도를 따로 가짐
        다른_날씨 = 날씨(30)
        assert weather.온도 == 25.5 and 다른_날씨.온도 == 30
        
        with pytest.raises(ValueError):
            weather.온도 = -300  # 절대영도보다 낮음
        
        with pytest.raises(AttributeError):
            del weather.온도
    
    def test_property_implementation(self):
        """프로퍼티 구현 원리 이해"""
        class MyProperty:
            def __init__(self, fget=None, fset=None, fdel=None):
                self.fget = fget
                self.fset = fset
                self.fdel = fdel
            
            def __get__(self, obj, objtype=None):
                if obj is None:
                    return self
                if self.fget is None:
                    raise AttributeError("읽을 수 없는 속성")
                return self.fget(obj)
            
            def __set__(self, obj, value):
                if self.fset is None:
                    raise AttributeError("설정할 수 없는 속성")
                self.fset(obj, value)
            
            def __delete__(self, obj):
                if self.fdel is None:
                    raise AttributeError("삭제할 수 없는 속성")
                self.fdel(obj)
        
        class 원:
            def __init__(self, 반지름):
                self._반지름 = 반지름
            
            def _get_면적(self):
                return 3.14159 * self._반지름 ** 2
            
            면적 = MyProperty(fget=_get_면적)
        
        circle = 원(5)
        assert abs(circle.면적 - 78.53975) < 0.001
        
        with pytest.raises(AttributeError):
            circle.면적 = 100  # 설정 불가
```

첫 번째 테스트에서 `날씨.__init__`의 `self.온도 = 온도`는 평범한 대입처럼 보이지만, 실제로는 `Temperature.__set__`이 불려서 숫자인지, 절대영도(-273.15도)보다 낮지 않은지 검사합니다. 그래서 `-300`을 넣으면 `ValueError`가 나고, `del`은 `__delete__`가 막아서 `AttributeError`가 납니다.

값을 어디에 저장하는지도 눈여겨보세요. 디스크립터는 클래스 속성이라서 `날씨`로 만든 모든 객체가 **하나의 디스크립터를 함께 씁니다.** 그러니 만약 값을 `self._celsius`처럼 **디스크립터 자신**에 저장하면, `weather = 날씨(25.5)` 다음에 `다른_날씨 = 날씨(30)`을 만드는 순간 `weather.온도`까지 `30`으로 바뀌어 버려요. 경비실 한 곳에서 모든 집의 택배를 받는데, 물건 놓을 칸이 하나뿐인 셈이죠.

그래서 `Temperature`는 값을 **각 객체의** `__dict__`에 따로 저장합니다. 이때 열쇠로 쓸 이름을 알려 주는 것이 파이썬 3.6에서 생긴 `__set_name__`이에요. 디스크립터가 클래스에 놓이는 순간 파이썬이 "너는 `온도`라는 이름으로 붙었어"라고 알려 주면, 디스크립터는 그 이름을 기억해 두었다가 `obj.__dict__['온도']`에 값을 넣고 꺼냅니다. 객체의 `__dict__`에 같은 이름이 있어도 `__set__`을 가진 디스크립터가 먼저 불리기 때문에 검사를 건너뛸 수 없어요. 테스트 중간의 `다른_날씨` 두 줄이 두 객체의 온도가 섞이지 않는다는 것을 확인합니다. 6절의 ORM에 나오는 `Field`도 같은 방식으로 값을 객체마다 따로 보관합니다.

두 번째 테스트의 `MyProperty`는 우리가 11.2절에서 쓴 `@property`를 직접 만들어 본 것입니다. 읽기 함수(`fget`)만 주고 쓰기 함수(`fset`)를 안 주면 `circle.면적 = 100`에서 `AttributeError`가 나죠. 진짜 `property`도 바로 이런 디스크립터예요. 사실 디스크립터는 파이썬 곳곳에 숨어 있습니다. 클래스에 정의한 **함수**도 `__get__`을 가진 디스크립터라서, `객체.메서드`로 꺼낼 때 그 객체가 `self`로 묶인 메서드가 만들어집니다. 우리가 한 번도 `self`를 직접 넘기지 않았는데도 메서드가 `self`를 받을 수 있었던 비밀이 여기 있어요.

## 4. 컨텍스트 매니저 (Context Managers)

컨텍스트 매니저는 `with` 문과 함께 사용되어 리소스 관리를 자동화합니다.

도서관에서 책을 빌리면 반드시 반납해야 하죠. 파일, 네트워크 연결, 데이터베이스 연결, 잠금(lock)도 마찬가지입니다. 열었으면 닫아야 하고, 빌렸으면 돌려줘야 해요. 문제는 중간에 예외가 나서 닫는 코드까지 가지 못하는 경우입니다. `with`문은 블록을 어떻게 빠져나가든(정상 종료든, `return`이든, 예외든) **나올 때 정리하는 코드를 반드시 실행**해 줍니다. `try`/`finally`를 매번 쓰는 수고를 덜어 주는 장치죠. `with` 문은 파이썬 2.5에서 PEP 343으로 언어에 들어왔고, 12장에서 `with open(...)`으로 파일을 다룰 때 이미 써 왔습니다.

`with` 뒤에 올 수 있는 객체가 컨텍스트 매니저이고, 두 메서드로 동작이 정해집니다.

- `__enter__(self)`: 블록에 들어갈 때 실행됩니다. 여기서 돌려준 값이 `as` 뒤의 이름에 담겨요.
- `__exit__(self, exc_type, exc_value, traceback)`: 블록을 나올 때 실행됩니다. 블록이 정상적으로 끝났으면 세 인자가 모두 `None`이고, 예외가 났으면 예외의 종류, 예외 객체, 추적 정보가 들어옵니다.

`__exit__`의 반환값에는 중요한 규칙이 있습니다. `False`(또는 아무것도 돌려주지 않아서 `None`)를 돌려주면 예외가 블록 바깥으로 그대로 전달되고, `True`를 돌려주면 **예외를 삼켜서** 없던 일로 만듭니다.

```python
class 조용히:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"정리 중 (예외: {exc_type.__name__ if exc_type else None})")
        return True   # True를 돌려주면 예외를 삼킴


with 조용히():
    1 / 0
print("프로그램은 계속됩니다")
```

```
정리 중 (예외: ZeroDivisionError)
프로그램은 계속됩니다
```

0으로 나눴는데도 프로그램이 멈추지 않았죠. 편리해 보이지만 예외를 삼키면 문제가 생겼다는 사실 자체가 묻혀 버립니다. 표준 라이브러리의 `contextlib.suppress(ZeroDivisionError)`처럼 **어떤 예외를 삼킬지 분명히 정해 둔 경우**가 아니라면 `False`를 돌려주세요. 아래 예제의 `파일관리자`도 `return False`로 예외를 바깥에 그대로 알립니다.

```python
class TestContextManagers:
    def test_basic_context_manager(self):
        """기본 컨텍스트 매니저 구현"""
        class 파일관리자:
            def __init__(self, 파일명, 모드):
                self.파일명 = 파일명
                self.모드 = 모드
                self.파일 = None
            
            def __enter__(self):
                print(f"파일 열기: {self.파일명}")
                self.파일 = open(self.파일명, self.모드)
                return self.파일
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                print(f"파일 닫기: {self.파일명}")
                if self.파일:
                    self.파일.close()
                # 예외를 다시 발생시키려면 False 반환 (기본값)
                return False
        
        import tempfile
        import os
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp_name = tmp.name
            tmp.write("테스트 내용")
        
        try:
            with 파일관리자(tmp_name, 'r') as f:
                content = f.read()
                assert content == "테스트 내용"
        finally:
            os.unlink(tmp_name)
    
    def test_contextlib_usage(self):
        """contextlib을 이용한 컨텍스트 매니저"""
        from contextlib import contextmanager
        
        @contextmanager
        def 데이터베이스_트랜잭션():
            print("트랜잭션 시작")
            transaction = {"committed": False, "data": []}
            try:
                yield transaction
                print("트랜잭션 커밋")
                transaction["committed"] = True
            except Exception:
                print("트랜잭션 롤백")
                transaction["committed"] = False
                transaction["data"].clear()
                raise
        
        # 성공 케이스
        with 데이터베이스_트랜잭션() as trans:
            trans["data"].append("새 데이터")
        
        assert trans["committed"] == True
        assert "새 데이터" in trans["data"]
        
        # 예외 발생 케이스
        try:
            with 데이터베이스_트랜잭션() as trans:
                trans["data"].append("문제 데이터")
                raise ValueError("오류 발생!")
        except ValueError:
            pass
        
        assert trans["committed"] == False
        assert len(trans["data"]) == 0
```

첫 번째 테스트의 `파일관리자`는 `open()`이 원래 하는 일을 직접 흉내 낸 것입니다. `__enter__`에서 파일을 열어 돌려주니 `as f`로 받은 것은 파일 객체이고, `__exit__`에서 닫습니다. 비슷한 일을 하는 도구가 표준 라이브러리에도 있어요. `contextlib.closing(객체)`는 `close()` 메서드가 있는 아무 객체나 `with` 블록이 끝날 때 닫아 줍니다.

두 번째 테스트의 `@contextmanager`는 클래스를 만들지 않고 **제너레이터 함수 하나**로 컨텍스트 매니저를 만드는 방법입니다. `yield` 앞이 `__enter__`, `yield`한 값이 `as`로 받는 값, `yield` 뒤가 `__exit__`에 해당해요. 블록 안에서 예외가 나면 그 예외가 `yield` 자리에서 다시 일어나기 때문에, `try`/`except`로 감싸서 성공하면 커밋, 실패하면 롤백하는 흐름을 자연스럽게 쓸 수 있습니다. 15장에서 본 "멈췄다 이어 가는" 제너레이터가 여기서도 쓰인 거죠. `except` 끝의 `raise`는 롤백을 한 다음 예외를 바깥에 다시 알리는 역할을 합니다. 그래서 테스트가 바깥에서 `except ValueError`로 받을 수 있어요.

## 5. 고급 기법들

### 5.1 동적 속성 접근

디스크립터는 특정 이름 하나의 출입을 관리했죠. 이번에는 **모든 속성 출입**에 끼어드는 방법입니다. 파이썬은 `객체.이름`을 처리할 때 정해진 특수 메서드를 부르는데, 우리가 이것을 고쳐 쓰면 속성이 실제로 어디에 저장될지 마음대로 정할 수 있어요.

- `__getattr__(self, name)`: 평소대로 찾아봤는데 **없을 때만** 불립니다. 마지막 안전망이에요. (이름이 비슷한 `__getattribute__`는 있든 없든 **모든** 읽기에서 불려서 훨씬 다루기 까다롭습니다.)
- `__setattr__(self, name, value)`: `객체.이름 = 값`을 할 때마다 **항상** 불립니다.
- `__delattr__(self, name)`: `del 객체.이름`을 할 때 불립니다.

아래 `설정관리자`는 이 세 메서드로 설정값들을 실제 속성이 아니라 `_설정들`이라는 사전 하나에 모아 둡니다. 쓰는 쪽에서는 `config.포트`처럼 평범한 속성으로 보이죠.

```python
class TestDynamicAttributes:
    def test_getattr_setattr(self):
        """동적 속성 접근 구현"""
        class 설정관리자:
            def __init__(self):
                self._설정들 = {}
            
            def __getattr__(self, name):
                if name.startswith('_'):
                    raise AttributeError(f"'{name}' 속성이 없습니다")
                return self._설정들.get(name, None)
            
            def __setattr__(self, name, value):
                if name.startswith('_'):
                    super().__setattr__(name, value)
                else:
                    if not hasattr(self, '_설정들'):
                        super().__setattr__('_설정들', {})
                    self._설정들[name] = value
            
            def __delattr__(self, name):
                if name in self._설정들:
                    del self._설정들[name]
                else:
                    raise AttributeError(f"'{name}' 속성이 없습니다")
        
        config = 설정관리자()
        config.데이터베이스_호스트 = "localhost"
        config.포트 = 5432
        
        assert config.데이터베이스_호스트 == "localhost"
        assert config.포트 == 5432
        assert config.존재하지않는설정 is None
        
        del config.포트
        assert config.포트 is None
    
    def test_slots_optimization(self):
        """__slots__를 이용한 최적화"""
        class 일반클래스:
            def __init__(self, x, y):
                self.x = x
                self.y = y
        
        class 최적화클래스:
            __slots__ = ['x', 'y']
            
            def __init__(self, x, y):
                self.x = x
                self.y = y
        
        normal = 일반클래스(1, 2)
        optimized = 최적화클래스(1, 2)
        
        # 일반 클래스는 __dict__ 있음
        assert hasattr(normal, '__dict__')
        normal.z = 3  # 동적 속성 추가 가능
        
        # 슬롯 클래스는 __dict__ 없음
        assert not hasattr(optimized, '__dict__')
        
        with pytest.raises(AttributeError):
            optimized.z = 3  # 동적 속성 추가 불가
```

`설정관리자`에서 눈여겨볼 곳은 밑줄로 시작하는 이름을 따로 처리하는 부분입니다. `__setattr__`은 **모든** 대입에서 불리니, `__init__`의 `self._설정들 = {}`도 여기로 들어와요. 이때 다시 `self._설정들[...]`에 넣으려고 하면 아직 없는 `_설정들`을 찾느라 꼬여 버립니다. 그래서 밑줄 이름은 `super().__setattr__()`로 원래 방식대로 저장하고, 나머지만 사전에 넣습니다. `__getattr__`에서 밑줄 이름에 `AttributeError`를 내는 것도 같은 이유로, 없는 내부 속성을 찾다가 끝없이 자기 자신을 부르는 일을 막아 줘요. 결과적으로 없는 설정을 읽으면 에러 대신 `None`이 나오는 너그러운 설정 객체가 됩니다.

두 번째 테스트는 반대로 **속성을 제한**하는 방법입니다. 보통 객체는 속성을 `__dict__`라는 사전에 담아서 아무 때나 새 속성을 추가할 수 있어요. 클래스에 `__slots__ = ['x', 'y']`를 적으면 파이썬은 사전 대신 딱 `x`, `y` 두 칸짜리 고정된 자리만 만들어 줍니다. 그래서 `optimized.z = 3`처럼 목록에 없는 속성을 추가하려 하면 `AttributeError`가 나요. 사전이 없으니 메모리도 아낄 수 있습니다. 파이썬 3.12에서 `tracemalloc`으로 두 클래스의 객체를 10만 개씩 만들어 재 보니, 담는 리스트까지 포함해 일반 클래스는 약 11.4MB, `__slots__` 클래스는 약 8.4MB를 썼습니다. 객체를 수십만 개 만드는 프로그램이 아니라면 굳이 쓸 필요는 없어요.

### 5.2 연산자 오버로딩

3장 들어가며에서 연산자도 사람이 정한 약속이라서 필요하면 직접 새 규칙을 만들 수 있다고 했죠? 그 방법이 연산자 오버로딩입니다. `v1 + v2`를 만나면 파이썬은 `v1.__add__(v2)`를 부르고, `v1 * 2`는 `v1.__mul__(2)`, `abs(v1)`은 `v1.__abs__()`를 부릅니다. 그러니 이 특수 메서드들을 정의하면 내가 만든 클래스에도 `+`, `*`, `abs()`의 의미를 정해 줄 수 있어요. 11.4절에서 본 특수 메서드를 수학의 벡터에 적용해 보겠습니다.

```python
class TestOperatorOverloading:
    def test_arithmetic_operators(self):
        """산술 연산자 오버로딩"""
        class 벡터:
            def __init__(self, x, y):
                self.x = x
                self.y = y
            
            def __add__(self, other):
                return 벡터(self.x + other.x, self.y + other.y)
            
            def __sub__(self, other):
                return 벡터(self.x - other.x, self.y - other.y)
            
            def __mul__(self, scalar):
                return 벡터(self.x * scalar, self.y * scalar)
            
            def __rmul__(self, scalar):
                return self.__mul__(scalar)
            
            def __abs__(self):
                return (self.x ** 2 + self.y ** 2) ** 0.5
            
            def __eq__(self, other):
                return self.x == other.x and self.y == other.y
            
            def __repr__(self):
                return f"벡터({self.x}, {self.y})"
        
        v1 = 벡터(3, 4)
        v2 = 벡터(1, 2)
        
        # 벡터 덧셈
        v3 = v1 + v2
        assert v3.x == 4 and v3.y == 6
        
        # 벡터 뺄셈
        v4 = v1 - v2
        assert v4.x == 2 and v4.y == 2
        
        # 스칼라 곱셈
        v5 = v1 * 2
        v6 = 3 * v1
        assert v5.x == 6 and v5.y == 8
        assert v6.x == 9 and v6.y == 12
        
        # 크기 계산
        assert abs(벡터(3, 4)) == 5.0
```

흥미로운 것은 `3 * v1`입니다. 파이썬은 먼저 왼쪽에 있는 `3`에게 `(3).__mul__(v1)`로 물어봅니다. 정수는 벡터와 곱하는 법을 모르니 "모르겠어요"라는 뜻의 특별한 값 `NotImplemented`를 돌려주죠. 그러면 파이썬은 포기하지 않고 오른쪽의 `v1`에게 `v1.__rmul__(3)`으로 다시 물어봅니다. 이름의 `r`은 오른쪽(right)이라는 뜻이에요. `__rmul__`이 없었다면 `v1 * 2`는 되는데 `3 * v1`은 `TypeError`가 났을 겁니다. `abs(벡터(3, 4))`가 `5.0`인 것은 피타고라스 정리(3×3 + 4×4 = 5×5) 그대로고요.

연산자 오버로딩은 그 연산이 **누가 봐도 자연스러울 때**만 쓰세요. 벡터의 `+`처럼 수학에서 뜻이 정해진 경우는 좋지만, 주문 객체에 `+`를 정의해서 "결제"를 하게 만들면 코드를 읽는 사람이 당황합니다.

## 6. 실전 프로젝트: 고급 ORM 시스템

모든 메타프로그래밍 기법을 활용한 간단한 ORM을 구현해보겠습니다.

**ORM(Object-Relational Mapping)** 은 데이터베이스의 표(테이블)를 파이썬 클래스로, 표의 한 줄을 객체로 다루게 해 주는 도구입니다. SQL을 직접 쓰지 않고 `user.save()`처럼 객체를 다루듯 데이터베이스를 쓸 수 있어요. 18장에서 만날 SQLAlchemy 같은 실제 ORM도 속을 들여다보면 이 장에서 배운 도구들로 만들어져 있습니다. 이 예제에서 각 기법이 맡은 역할은 이렇습니다.

- **디스크립터** `Field`: 각 필드의 타입과 NULL 허용 여부를 검사하고, 값을 객체의 `_data` 사전에 객체마다 따로 보관합니다. `__set_name__`으로 자기 이름도 스스로 알아내요.
- **메타클래스** `ModelMeta`: 클래스가 만들어질 때 `Field`인 속성들을 모아 `_fields`에 기록하고, 클래스 이름을 테이블 이름으로 정하고, `save()` 메서드를 끼워 넣습니다.
- **컨텍스트 매니저** `database_transaction`: 성공하면 커밋, 실패하면 롤백, 어느 쪽이든 마지막에 연결을 닫습니다.
- **데코레이터** `timing_decorator`: 함수 실행 시간을 재는 도구로 함께 정의해 두었습니다.

`사용자` 클래스를 보면 필드 세 줄만 적었을 뿐인데, 나머지는 메타클래스와 디스크립터가 다 해 줍니다. 이것이 메타프로그래밍이 프레임워크에서 사랑받는 이유예요.

이 파일은 필요한 것을 모두 스스로 불러오므로, `uv run --with pytest pytest advanced_orm.py`로 테스트를 돌리거나 `uv run --with pytest python advanced_orm.py`로 바로 실행할 수 있습니다.

```python
# advanced_orm.py
from typing import Any, Dict, List, Optional
import sqlite3
import time
from contextlib import contextmanager
from functools import wraps

import pytest

class Field:
    """필드 디스크립터"""
    def __init__(self, field_type, null=True, default=None):
        self.field_type = field_type
        self.null = null
        self.default = default
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj._data.get(self.name, self.default)
    
    def __set__(self, obj, value):
        if value is None and not self.null:
            raise ValueError(f"{self.name}은 NULL이 될 수 없습니다")
        if value is not None and not isinstance(value, self.field_type):
            raise TypeError(f"{self.name}은 {self.field_type.__name__} 타입이어야 합니다")
        obj._data[self.name] = value

class ModelMeta(type):
    """모델 메타클래스"""
    def __new__(mcs, name, bases, namespace):
        if name == 'Model':
            return super().__new__(mcs, name, bases, namespace)
        
        # 필드 수집
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                fields[key] = value
        
        namespace['_fields'] = fields
        namespace['_table_name'] = name.lower()
        
        # 쿼리 메서드 자동 추가
        def save(self):
            columns = ', '.join(self._fields.keys())
            placeholders = ', '.join(['?' for _ in self._fields])
            values = [getattr(self, field) for field in self._fields]
            
            query = f"INSERT INTO {self._table_name} ({columns}) VALUES ({placeholders})"
            return query, values
        
        namespace['save'] = save
        
        return super().__new__(mcs, name, bases, namespace)

class Model(metaclass=ModelMeta):
    """베이스 모델 클래스"""
    def __init__(self, **kwargs):
        self._data = {}
        for field_name in self._fields:
            if field_name in kwargs:
                setattr(self, field_name, kwargs[field_name])

@contextmanager
def database_transaction():
    """데이터베이스 트랜잭션 컨텍스트 매니저"""
    conn = sqlite3.connect(':memory:')
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def timing_decorator(func):
    """실행 시간 측정 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 실행 시간: {end - start:.4f}초")
        return result
    return wrapper

# 사용 예제
class 사용자(Model):
    이름 = Field(str, null=False)
    이메일 = Field(str, null=False)
    나이 = Field(int, default=0)

class TestAdvancedORM:
    def test_orm_system(self):
        """고급 ORM 시스템 테스트"""
        # 모델 생성
        user = 사용자(이름="김철수", 이메일="kim@example.com", 나이=30)
        
        # 필드 접근
        assert user.이름 == "김철수"
        assert user.이메일 == "kim@example.com"
        assert user.나이 == 30
        
        # 타입 검증
        with pytest.raises(TypeError):
            user.나이 = "서른"
        
        # NULL 검증
        with pytest.raises(ValueError):
            user.이름 = None
        
        # 쿼리 생성
        query, values = user.save()
        expected_query = "INSERT INTO 사용자 (이름, 이메일, 나이) VALUES (?, ?, ?)"
        assert query == expected_query
        assert values == ["김철수", "kim@example.com", 30]
        
        # 트랜잭션 테스트
        with database_transaction() as conn:
            conn.execute('''
                CREATE TABLE 사용자 (
                    이름 TEXT NOT NULL,
                    이메일 TEXT NOT NULL,
                    나이 INTEGER DEFAULT 0
                )
            ''')
            
            conn.execute(query, values)
            
            cursor = conn.execute("SELECT * FROM 사용자")
            row = cursor.fetchone()
            assert row == ("김철수", "kim@example.com", 30)

if __name__ == "__main__":
    # 실제 사용 예제
    user = 사용자(이름="박영희", 이메일="park@example.com")
    print(f"사용자: {user.이름}, 이메일: {user.이메일}")
    
    query, values = user.save()
    print(f"쿼리: {query}")
    print(f"값들: {values}")
```

위처럼 직접 실행하면 아래처럼 나옵니다.

```
사용자: 박영희, 이메일: park@example.com
쿼리: INSERT INTO 사용자 (이름, 이메일, 나이) VALUES (?, ?, ?)
값들: ['박영희', 'park@example.com', 0]
```

`나이`를 넘기지 않았는데 값 목록에 `0`이 들어 있죠? `Field(int, default=0)`의 기본값을 디스크립터의 `__get__`이 돌려준 것입니다. 그리고 쿼리에 값을 직접 끼워 넣지 않고 `?` 자리표시자로 따로 넘기는 것도 눈여겨보세요. 사용자가 입력한 값이 SQL 명령으로 해석되는 공격(SQL 인젝션)을 막는 기본기로, 18장에서 데이터베이스를 다룰 때 자세히 봅니다. 테스트 쪽의 `database_transaction`은 메모리 안에 임시 데이터베이스(`:memory:`)를 만들어 이 쿼리를 실제로 실행하고, 저장된 줄이 `("김철수", "kim@example.com", 30)`인지 확인합니다.

## 정리

이 장에서는 파이썬의 고급 메타프로그래밍 기법들을 학습했습니다:

1. **데코레이터**: 함수와 클래스의 기능을 확장하는 우아한 방법
2. **메타클래스**: 클래스 생성 과정을 제어하는 강력한 도구
3. **디스크립터**: 속성 접근을 세밀하게 제어하는 메커니즘
4. **컨텍스트 매니저**: 리소스 관리를 자동화하는 안전한 방법
5. **고급 기법들**: 동적 속성 접근, 연산자 오버로딩, 슬롯 최적화

이러한 기법들은 프레임워크나 라이브러리 개발 시 매우 유용하며, 코드의 재사용성과 유지보수성을 크게 향상시킵니다. 하지만 과도한 사용은 코드의 복잡성을 증가시킬 수 있으므로, 적절한 상황에서 신중하게 사용해야 합니다.