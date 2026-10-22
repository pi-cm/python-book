"""1권 Chapter 10: 함수형 프로그래밍 — 10.7 실습 문제

원고: manuscript/chapters/10-functional-programming.md (1508줄부터)
"""

# ---- 원고 1508줄 ----
# 1번: 기본 함수 정의
def korean_grade_calculator(scores: list, weights: list = None) -> dict:
    """한국 학점 계산기"""
    pass

# 문제: 점수 리스트와 가중치를 받아서 가중평균과 학점을 계산하세요
# 답:
def korean_grade_calculator(scores: list, weights: list = None) -> dict:
    if not scores:
        return {"오류": "점수가 없습니다"}
    
    if weights is None:
        weights = [1] * len(scores)
    
    if len(scores) != len(weights):
        return {"오류": "점수와 가중치 개수가 다릅니다"}
    
    weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
    total_weight = sum(weights)
    average = weighted_sum / total_weight
    
    if average >= 95: grade = "A+"
    elif average >= 90: grade = "A"
    elif average >= 85: grade = "B+"
    elif average >= 80: grade = "B"
    elif average >= 75: grade = "C+"
    elif average >= 70: grade = "C"
    else: grade = "F"
    
    return {"평균": round(average, 2), "학점": grade}

result = korean_grade_calculator([85, 92, 78], [3, 4, 3])
print(f"성적 계산 결과: {result}")

# 2번: 람다 함수 활용
korean_cities = ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]
# 문제: 도시명 길이로 정렬하고, 같으면 가나다순으로 정렬하세요
# 답:
sorted_cities = sorted(korean_cities, key=lambda x: (len(x), x))
print(f"정렬된 도시: {sorted_cities}")

# 3번: map() 활용
temperatures_celsius = [25, 30, 15, 35, 20]
# 문제: 섭씨온도를 화씨온도로 변환하고 한글 설명을 추가하세요
# 답:
to_fahrenheit = lambda c: f"{c}°C = {c * 9/5 + 32:.1f}°F"
fahrenheit_temps = list(map(to_fahrenheit, temperatures_celsius))
for temp in fahrenheit_temps:
    print(temp)

# 4번: filter() 활용
korean_words = ["사과", "apple", "바나나", "banana", "컴퓨터", "computer"]
# 문제: 한글이 포함된 단어만 필터링하세요
# 답:
import re
korean_only = list(filter(lambda word: bool(re.search(r'[가-힣]', word)), korean_words))
print(f"한글 포함 단어: {korean_only}")

# 5번: 기본 데코레이터
def korean_log(func):
    """함수 호출을 한글로 로그"""
    def wrapper(*args, **kwargs):
        print(f"함수 '{func.__name__}' 실행 시작")
        result = func(*args, **kwargs)
        print(f"[O] 함수 '{func.__name__}' 실행 완료")
        return result
    return wrapper

@korean_log
def add_numbers(a, b):
    return a + b

result = add_numbers(3, 5)
print(f"결과: {result}")

# ---- 원고 1589줄 ----
# 6번: 고차 함수 구현
def create_korean_formatter(format_type: str):
    """한국어 포맷터 생성기"""
    pass

# 문제: 다양한 한국 포맷터를 생성하는 함수를 만드세요
# 답:
def create_korean_formatter(format_type: str):
    formatters = {
        "currency": lambda amount: f"{amount:,}원",
        "phone": lambda number: f"{number[:3]}-{number[3:7]}-{number[7:]}",
        "date": lambda date_str: f"{date_str[:4]}년 {date_str[4:6]}월 {date_str[6:8]}일"
    }
    
    if format_type not in formatters:
        raise ValueError(f"지원하지 않는 포맷: {format_type}")
    
    return formatters[format_type]

currency_fmt = create_korean_formatter("currency")
phone_fmt = create_korean_formatter("phone")
date_fmt = create_korean_formatter("date")

print(f"통화: {currency_fmt(1500000)}")
print(f"전화번호: {phone_fmt('01012345678')}")
print(f"날짜: {date_fmt('20231225')}")

# 7번: reduce() 고급 활용
from functools import reduce

sales_data = [
    {"지역": "서울", "매출": 1500000},
    {"지역": "부산", "매출": 1200000}, 
    {"지역": "서울", "매출": 800000},
    {"지역": "대구", "매출": 600000},
    {"지역": "부산", "매출": 900000}
]

# 문제: reduce를 사용해서 지역별 매출 합계를 계산하세요
# 답:
def aggregate_sales(acc, sale):
    region = sale["지역"]
    amount = sale["매출"]
    if region in acc:
        acc[region] += amount
    else:
        acc[region] = amount
    return acc

regional_sales = reduce(aggregate_sales, sales_data, {})
print(f"지역별 매출: {regional_sales}")

# 8번: 매개변수를 받는 데코레이터
def korean_retry_decorator(max_attempts=3):
    """재시도 데코레이터"""
    pass

# 문제: 지정된 횟수만큼 재시도하는 데코레이터를 만드세요
# 답:
def korean_retry_decorator(max_attempts=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    print(f"시도 {attempt}/{max_attempts}")
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        print(f"최종 실패: {e}")
                        raise
                    print(f"실패, 재시도: {e}")
        return wrapper
    return decorator

@korean_retry_decorator(max_attempts=3)
def unstable_function():
    import random
    if random.random() < 0.7:
        raise Exception("일시적 오류")
    return "성공!"

try:
    result = unstable_function()
    print(f"결과: {result}")
except Exception as e:
    print(f"최종 실패: {e}")

# 9번: 클로저 활용
def korean_accumulator_factory(initial_value=0):
    """누적기 팩토리"""
    pass

# 문제: 값을 누적하고 통계를 제공하는 클로저를 만드세요
# 답:
def korean_accumulator_factory(initial_value=0):
    values = [initial_value]
    
    def add(value):
        values.append(value)
        return sum(values)
    
    def get_stats():
        if not values:
            return {"개수": 0, "합계": 0, "평균": 0}
        
        return {
            "개수": len(values),
            "합계": sum(values),
            "평균": sum(values) / len(values),
            "최대값": max(values),
            "최소값": min(values)
        }
    
    add.get_stats = get_stats
    add.values = values
    
    return add

acc = korean_accumulator_factory(10)
print(f"누적: {acc(5)}, {acc(15)}, {acc(20)}")
print(f"통계: {acc.get_stats()}")

# 10번: 함수 조합
def compose(*functions):
    """함수 조합기"""
    pass

# 문제: 여러 함수를 조합하는 compose 함수를 만드세요
# 답:
def compose(*functions):
    return lambda x: reduce(lambda acc, f: f(acc), functions, x)

# 한국어 텍스트 처리 함수들
def remove_spaces(text):
    return text.replace(" ", "")

def add_prefix(text):
    return f"한국어: {text}"

def add_suffix(text):
    return f"{text} (처리완료)"

# 함수 조합
text_processor = compose(remove_spaces, add_prefix, add_suffix)
result = text_processor("안녕 하세요 파이썬")
print(f"조합 결과: {result}")

# ---- 원고 1742줄 ----
# 11번: 복잡한 파이프라인
class KoreanTextPipeline:
    def __init__(self):
        self.steps = []
    
    def add_step(self, name, func):
        self.steps.append((name, func))
        return self
    
    def process(self, text):
        # 문제: 각 단계를 거쳐 텍스트를 처리하는 파이프라인을 구현하세요
        pass

# 답:
class KoreanTextPipeline:
    def __init__(self):
        self.steps = []
    
    def add_step(self, name, func):
        self.steps.append((name, func))
        return self
    
    def process(self, text):
        result = {
            "original": text,
            "final": text,
            "steps": []
        }
        
        current_text = text
        for step_name, step_func in self.steps:
            try:
                new_text = step_func(current_text)
                result["steps"].append({
                    "name": step_name,
                    "input": current_text,
                    "output": new_text
                })
                current_text = new_text
            except Exception as e:
                result["steps"].append({
                    "name": step_name,
                    "error": str(e)
                })
                break
        
        result["final"] = current_text
        return result

pipeline = KoreanTextPipeline()
pipeline.add_step("대문자변환", str.upper)
pipeline.add_step("접두어추가", lambda x: f"처리: {x}")
pipeline.add_step("길이계산", lambda x: f"{x} (길이: {len(x)})")

result = pipeline.process("안녕하세요")
print(f"파이프라인 결과: {result}")

# 12번: 동적 함수 생성
def create_korean_validator_function(rules):
    """검증 규칙으로 함수 생성"""
    pass

# 문제: 규칙 딕셔너리를 받아서 검증 함수를 동적으로 생성하세요
# 답:
def create_korean_validator_function(rules):
    def validator(data):
        errors = []
        
        for field, field_rules in rules.items():
            if field not in data:
                errors.append(f"{field}: 필수 필드입니다")
                continue
            
            value = data[field]
            
            for rule_name, rule_func in field_rules.items():
                try:
                    if not rule_func(value):
                        errors.append(f"{field}: {rule_name} 규칙 위반")
                except Exception as e:
                    errors.append(f"{field}: {rule_name} 검증 오류 - {e}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    return validator

# 검증 규칙 정의
validation_rules = {
    "이름": {
        "비어있지않음": lambda x: len(x.strip()) > 0,
        "한글만": lambda x: all('가' <= c <= '힣' for c in x.strip()),
        "길이제한": lambda x: 2 <= len(x.strip()) <= 5
    },
    "나이": {
        "양수": lambda x: isinstance(x, int) and x > 0,
        "범위": lambda x: 0 <= x <= 150
    }
}

validator = create_korean_validator_function(validation_rules)

test_data = {"이름": "김철수", "나이": 25}
result = validator(test_data)
print(f"검증 결과: {result}")

# 13번: 메모이제이션 데코레이터
def korean_memoize(maxsize=128):
    """메모이제이션 데코레이터"""
    pass

# 문제: 결과를 캐시하는 메모이제이션 데코레이터를 만드세요
# 답:
def korean_memoize(maxsize=128):
    def decorator(func):
        cache = {}
        stats = {"hits": 0, "misses": 0}
        
        def wrapper(*args, **kwargs):
            # 키 생성 (해시 가능한 형태로)
            key = (args, tuple(sorted(kwargs.items())))
            
            if key in cache:
                stats["hits"] += 1
                print(f"캐시 히트: {func.__name__}")
                return cache[key]
            
            # 캐시 크기 제한
            if len(cache) >= maxsize:
                # 가장 오래된 항목 제거
                oldest_key = next(iter(cache))
                del cache[oldest_key]
            
            stats["misses"] += 1
            result = func(*args, **kwargs)
            cache[key] = result
            
            return result
        
        wrapper.cache_info = lambda: stats
        wrapper.cache_clear = lambda: cache.clear()
        
        return wrapper
    return decorator

@korean_memoize(maxsize=10)
def fibonacci_korean(n):
    print(f"피보나치 {n} 계산 중...")
    if n <= 1:
        return n
    return fibonacci_korean(n-1) + fibonacci_korean(n-2)

result = fibonacci_korean(10)
print(f"피보나치(10): {result}")
print(f"캐시 정보: {fibonacci_korean.cache_info()}")

# 14번: 함수 체이닝
class KoreanDataProcessor:
    def __init__(self, data):
        self.data = data
    
    def filter_korean(self):
        # 문제: 메서드 체이닝이 가능한 데이터 처리기를 만드세요
        pass

# 답:
class KoreanDataProcessor:
    def __init__(self, data):
        self.data = data
    
    def filter_korean(self):
        import re
        self.data = [item for item in self.data if re.search(r'[가-힣]', str(item))]
        return self
    
    def filter_length(self, min_len=2, max_len=10):
        self.data = [item for item in self.data if min_len <= len(str(item)) <= max_len]
        return self
    
    def sort_by_length(self):
        self.data = sorted(self.data, key=lambda x: len(str(x)))
        return self
    
    def take(self, n):
        self.data = self.data[:n]
        return self
    
    def get_result(self):
        return self.data

words = ["안녕", "hello", "세상", "world", "프로그래밍", "programming", "파이썬"]
result = (KoreanDataProcessor(words)
          .filter_korean()
          .filter_length(min_len=2, max_len=5)
          .sort_by_length()
          .take(3)
          .get_result())

print(f"체이닝 결과: {result}")

# 15번: 고급 함수형 유틸리티
def korean_functional_utils():
    """한국어 함수형 유틸리티 모음"""
    
    def curry(func):
        """커링 함수"""
        pass
    
    def partial_korean(func, *partial_args, **partial_kwargs):
        """한국어 부분 적용"""
        pass

# 문제: 커링과 부분적용을 구현하세요
# 답:
def korean_functional_utils():
    
    def curry(func, arity=None):
        if arity is None:
            arity = func.__code__.co_argcount
        
        def curried(*args, **kwargs):
            if len(args) + len(kwargs) >= arity:
                return func(*args, **kwargs)
            else:
                def partial(*more_args, **more_kwargs):
                    return curried(*(args + more_args), **{**kwargs, **more_kwargs})
                return partial
        
        return curried
    
    def partial_korean(func, *partial_args, **partial_kwargs):
        def wrapper(*args, **kwargs):
            all_args = partial_args + args
            all_kwargs = {**partial_kwargs, **kwargs}
            return func(*all_args, **all_kwargs)
        
        return wrapper
    
    return curry, partial_korean

curry, partial_korean = korean_functional_utils()

# 한국어 인사 함수
def korean_greeting(greeting, name, title=""):
    return f"{greeting}, {name}{title}님!"

# 커링 적용
curried_greeting = curry(korean_greeting)
formal_greeting = curried_greeting("안녕하십니까")
casual_greeting = curried_greeting("안녕하세요")

print(f"정중한 인사: {formal_greeting('김철수', ' 부장')}")
print(f"일반 인사: {casual_greeting('이영희')}")

# 부분 적용
morning_greet = partial_korean(korean_greeting, "좋은 아침입니다")
print(f"아침 인사: {morning_greet('박민수', ' 교수')}")
