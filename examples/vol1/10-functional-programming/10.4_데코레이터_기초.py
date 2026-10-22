"""1권 Chapter 10: 함수형 프로그래밍 — 10.4 데코레이터 기초

원고: manuscript/chapters/10-functional-programming.md (687줄부터)
"""

# ---- 원고 687줄 ----
import time
import functools
from datetime import datetime

def korean_time_logger(func):
    """한국 시간으로 함수 실행 시간 기록"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_datetime = datetime.now()
        
        print(f"함수 '{func.__name__}' 실행 시작: {start_datetime.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}")
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"함수 '{func.__name__}' 실행 완료: {execution_time:.4f}초 소요")
        return result
    
    return wrapper

def korean_input_validator(*validators):
    """한국어 입력 검증 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 인자 검증
            for i, (arg, validator) in enumerate(zip(args, validators)):
                if not validator(arg):
                    validator_name = validator.__name__ if hasattr(validator, '__name__') else str(validator)
                    raise ValueError(f"인자 {i+1}번 '{arg}'이(가) 조건 '{validator_name}'을(를) 만족하지 않습니다.")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 검증 함수들
def is_korean_name(name: str) -> bool:
    """한글 이름 검증"""
    import re
    return bool(re.match(r'^[가-힣]{2,5}$', name))

def is_positive_int(value: int) -> bool:
    """양의 정수 검증"""
    return isinstance(value, int) and value > 0

def is_valid_age(age: int) -> bool:
    """유효한 나이 검증"""
    return isinstance(age, int) and 0 <= age <= 150

# 데코레이터 적용 예제
@korean_time_logger
@korean_input_validator(is_korean_name, is_positive_int, is_valid_age)
def create_korean_student_id(name: str, student_number: int, age: int) -> str:
    """한국 학생 ID 생성"""
    time.sleep(0.1)  # 처리 시간 시뮬레이션
    
    # 이름의 첫 글자로 성씨 추출
    surname = name[0]
    
    # 학번을 4자리로 포맷팅
    formatted_number = f"{student_number:04d}"
    
    # 연령대 코드
    age_group = f"{age // 10}0"
    
    student_id = f"KOR{surname}{formatted_number}{age_group}"
    
    print(f"학생 ID 생성: {name}님 → {student_id}")
    return student_id

# 사용 예제
print("학생 ID 생성 테스트:")
try:
    id1 = create_korean_student_id("김철수", 1234, 20)
    id2 = create_korean_student_id("이영희", 5678, 22)
    print(f"생성된 ID들: {id1}, {id2}")
except ValueError as e:
    print(f"[X] 오류: {e}")

# 잘못된 입력 테스트
print(f"\n잘못된 입력 테스트:")
try:
    create_korean_student_id("John", 1234, 20)  # 영문 이름
except ValueError as e:
    print(f"[X] 오류: {e}")

# ---- 원고 793줄 ----
def korean_retry(max_attempts: int = 3, delay: float = 1.0, exceptions=(Exception,)):
    """한국어 재시도 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    print(f"시도 {attempt}/{max_attempts}: {func.__name__}")
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        print(f"[O] {attempt}번째 시도에서 성공!")
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    print(f"[X] {attempt}번째 시도 실패: {str(e)}")
                    
                    if attempt < max_attempts:
                        print(f"{delay}초 후 재시도...")
                        time.sleep(delay)
                    else:
                        print(f"모든 시도 실패. 포기합니다.")
            
            raise last_exception
        
        return wrapper
    return decorator

def korean_cache(maxsize: int = 128):
    """한국어 캐시 데코레이터"""
    def decorator(func):
        cache = {}
        cache_info = {"hits": 0, "misses": 0, "maxsize": maxsize}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 딕셔너리는 해시 불가능하므로 키워드 인자를 튜플로 변환
            key = (args, tuple(sorted(kwargs.items())))
            
            if key in cache:
                cache_info["hits"] += 1
                print(f"캐시 히트: {func.__name__}")
                return cache[key]
            
            # 캐시 크기 제한
            if len(cache) >= maxsize:
                # 가장 오래된 항목 제거 (FIFO)
                oldest_key = next(iter(cache))
                del cache[oldest_key]
                print(f"캐시 공간 확보: 항목 제거")
            
            cache_info["misses"] += 1
            print(f"캐시 미스: {func.__name__} 계산 중...")
            
            result = func(*args, **kwargs)
            cache[key] = result
            
            return result
        
        def cache_clear():
            cache.clear()
            cache_info["hits"] = cache_info["misses"] = 0
            print("캐시 초기화 완료")
        
        def cache_status():
            total = cache_info["hits"] + cache_info["misses"]
            hit_rate = cache_info["hits"] / total * 100 if total > 0 else 0
            return {
                "캐시_크기": len(cache),
                "최대_크기": cache_info["maxsize"],
                "히트_수": cache_info["hits"],
                "미스_수": cache_info["misses"],
                "히트율": f"{hit_rate:.1f}%"
            }
        
        wrapper.cache_clear = cache_clear
        wrapper.cache_status = cache_status
        
        return wrapper
    return decorator

# 데코레이터 적용 예제
import random

@korean_retry(max_attempts=3, delay=0.5, exceptions=(ValueError, ConnectionError))
def unstable_korean_api_call(city: str) -> dict:
    """불안정한 한국 도시 API 호출 시뮬레이션"""
    
    # 랜덤하게 실패
    if random.random() < 0.7:  # 70% 실패율
        raise ConnectionError(f"{city} 날씨 정보 조회 실패")
    
    # 성공 시 가짜 데이터 반환
    weather_conditions = ["맑음", "흐림", "비", "눈", "안개"]
    return {
        "도시": city,
        "날씨": random.choice(weather_conditions),
        "온도": random.randint(-10, 35),
        "습도": random.randint(30, 90)
    }

@korean_cache(maxsize=5)
def expensive_korean_calculation(base: int, exponent: int) -> int:
    """비용이 많이 드는 한국어 계산"""
    print(f"복잡한 계산 수행: {base}^{exponent}")
    time.sleep(1)  # 계산 시간 시뮬레이션
    result = base ** exponent
    print(f"[O] 계산 완료: {result:,}")
    return result

# 사용 예제
print("API 재시도 테스트:")
try:
    weather = unstable_korean_api_call("서울")
    print(f"날씨 정보: {weather}")
except Exception as e:
    print(f"최종 실패: {e}")

print(f"\n캐시 테스트:")
# 같은 계산을 여러 번 수행 (캐시 효과 확인)
for _ in range(2):
    expensive_korean_calculation(2, 10)

for _ in range(2):
    expensive_korean_calculation(3, 5)

print(f"캐시 상태: {expensive_korean_calculation.cache_status()}")
