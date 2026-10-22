"""1권 Chapter 16: 메타프로그래밍과 고급 기법 — 1. 데코레이터 (Decorators)

원고: manuscript/chapters/16-metaprogramming-advanced.md (41줄부터)
"""

# ---- 원고 41줄 ----
def 큰소리(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper


def 인사(이름):
    return f"hello, {이름}"

인사 = 큰소리(인사)   # @큰소리 와 똑같은 일
print(인사("kim"))
print(인사.__name__)

# ---- 원고 122줄 ----
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

# ---- 원고 206줄 ----
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

# ---- 원고 290줄 ----
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
