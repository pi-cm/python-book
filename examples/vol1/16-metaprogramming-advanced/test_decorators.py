# [1권 Chapter 16: 메타프로그래밍과 고급 기법 · 1. 데코레이터 (Decorators) · manuscript/chapters/16-metaprogramming-advanced.md:69]
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
