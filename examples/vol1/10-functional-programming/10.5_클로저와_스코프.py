"""1권 Chapter 10: 함수형 프로그래밍 — 10.5 클로저와 스코프

원고: manuscript/chapters/10-functional-programming.md (937줄부터)
"""

# ---- 원고 937줄 ----
def korean_greeting_factory(greeting_type: str):
    """한국어 인사말 생성기"""
    
    greetings = {
        "formal": "안녕하십니까",
        "casual": "안녕하세요", 
        "friendly": "안녕",
        "morning": "좋은 아침입니다",
        "evening": "안녕히 주무세요"
    }
    
    base_greeting = greetings.get(greeting_type, "안녕하세요")
    
    def greet(name: str, title: str = "") -> str:
        # 클로저: 외부 함수의 변수에 접근
        if title:
            full_name = f"{name} {title}"
        else:
            full_name = name
            
        return f"{base_greeting}, {full_name}님!"
    
    # 클로저 정보를 추가하는 내부 함수
    def get_greeting_info():
        return {
            "인사_유형": greeting_type,
            "기본_인사말": base_greeting
        }
    
    # 함수에 속성 추가
    greet.get_info = get_greeting_info
    
    return greet

def korean_counter_factory(initial_value: int = 0, step: int = 1):
    """한국어 카운터 생성기"""
    
    count = initial_value
    
    def increment():
        nonlocal count
        count += step
        return count
    
    def decrement():
        nonlocal count
        count -= step
        return count
    
    def reset():
        nonlocal count
        count = initial_value
        return count
    
    def get_count():
        return count
    
    def get_korean_number():
        """숫자를 한국어로 변환"""
        korean_numbers = [
            "영", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구", "십"
        ]
        if 0 <= count <= 10:
            return korean_numbers[count]
        else:
            return str(count)
    
    # 여러 함수를 가진 객체 반환
    return {
        "증가": increment,
        "감소": decrement,
        "초기화": reset,
        "현재값": get_count,
        "한국어숫자": get_korean_number
    }

# 클로저 사용 예제
print("인사말 생성기:")
formal_greet = korean_greeting_factory("formal")
casual_greet = korean_greeting_factory("casual")
morning_greet = korean_greeting_factory("morning")

print(formal_greet("김철수", "부장"))
print(casual_greet("이영희"))
print(morning_greet("박민수", "교수"))

print(f"격식 인사 정보: {formal_greet.get_info()}")

print(f"\n카운터 생성기:")
counter1 = korean_counter_factory(0, 2)  # 0부터 시작, 2씩 증가
counter2 = korean_counter_factory(10, 1)  # 10부터 시작, 1씩 증가

print(f"카운터1 증가: {counter1['증가']()}, {counter1['증가']()}, {counter1['증가']()}")
print(f"카운터1 한국어: {counter1['한국어숫자']()}")

print(f"카운터2 감소: {counter2['감소']()}, {counter2['감소']()}")
print(f"카운터2 현재값: {counter2['현재값']()}")

# ---- 원고 1048줄 ----
def korean_validator_factory():
    """한국어 검증기 팩토리"""
    
    # 공통 검증 규칙들
    import re
    
    patterns = {
        "휴대폰": re.compile(r'^010-\d{4}-\d{4}$'),
        "이메일": re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
        "주민등록번호": re.compile(r'^\d{6}-\d{7}$'),
        "사업자등록번호": re.compile(r'^\d{3}-\d{2}-\d{5}$'),
        "한글이름": re.compile(r'^[가-힣]{2,5}$')
    }
    
    def create_validator(validation_type: str, custom_message: str = None):
        """특정 유형의 검증기 생성"""
        
        if validation_type not in patterns:
            raise ValueError(f"지원하지 않는 검증 유형: {validation_type}")
        
        pattern = patterns[validation_type]
        default_messages = {
            "휴대폰": "올바른 휴대폰 번호 형식이 아닙니다 (010-0000-0000)",
            "이메일": "올바른 이메일 형식이 아닙니다",
            "주민등록번호": "올바른 주민등록번호 형식이 아닙니다 (000000-0000000)",
            "사업자등록번호": "올바른 사업자등록번호 형식이 아닙니다 (000-00-00000)",
            "한글이름": "올바른 한글 이름이 아닙니다 (2-5글자)"
        }
        
        error_message = custom_message or default_messages[validation_type]
        
        def validate(value: str) -> tuple[bool, str]:
            """검증 수행"""
            if not isinstance(value, str):
                return False, "문자열이 아닙니다"
            
            if pattern.match(value):
                return True, "검증 성공"
            else:
                return False, error_message
        
        # 검증기 정보 추가
        validate.validation_type = validation_type
        validate.pattern = pattern.pattern
        
        return validate
    
    return create_validator

def korean_data_processor_factory(processing_rules: dict):
    """한국어 데이터 처리기 팩토리"""
    
    def create_processor(data_type: str):
        """특정 유형의 데이터 처리기 생성"""
        
        if data_type not in processing_rules:
            raise ValueError(f"지원하지 않는 데이터 유형: {data_type}")
        
        rules = processing_rules[data_type]
        
        def process(data_list: list) -> dict:
            """데이터 처리 수행"""
            results = {
                "원본_데이터": data_list.copy(),
                "처리_결과": [],
                "통계": {},
                "오류": []
            }
            
            for item in data_list:
                try:
                    processed_item = item
                    
                    # 규칙별로 처리
                    for rule_name, rule_func in rules.items():
                        processed_item = rule_func(processed_item)
                    
                    results["처리_결과"].append(processed_item)
                    
                except Exception as e:
                    results["오류"].append({
                        "원본": item,
                        "오류내용": str(e)
                    })
            
            # 통계 계산
            results["통계"] = {
                "총_건수": len(data_list),
                "성공_건수": len(results["처리_결과"]),
                "실패_건수": len(results["오류"]),
                "성공률": f"{len(results['처리_결과'])/len(data_list)*100:.1f}%" if data_list else "0%"
            }
            
            return results
        
        process.data_type = data_type
        process.rules = list(rules.keys())
        
        return process
    
    return create_processor

# 클로저 팩토리 사용 예제
print("검증기 팩토리 사용:")
validator_factory = korean_validator_factory()

phone_validator = validator_factory("휴대폰")
email_validator = validator_factory("이메일")
name_validator = validator_factory("한글이름", "이름은 한글 2-5글자여야 합니다")

test_data = [
    ("휴대폰", "010-1234-5678", phone_validator),
    ("휴대폰", "010-12345-6789", phone_validator),
    ("이메일", "test@example.com", email_validator),
    ("이메일", "잘못된이메일", email_validator),
    ("이름", "김철수", name_validator),
    ("이름", "김", name_validator)
]

for data_type, test_value, validator in test_data:
    is_valid, message = validator(test_value)
    status = "[O]" if is_valid else "[X]"
    print(f"{status} {data_type} '{test_value}': {message}")

# 데이터 처리기 팩토리 사용
print(f"\n데이터 처리기 팩토리 사용:")

# 처리 규칙 정의
text_processing_rules = {
    "한국어_텍스트": {
        "공백_정리": lambda x: ' '.join(x.split()),
        "소문자_변환": lambda x: x.lower(),
        "특수문자_제거": lambda x: ''.join(c for c in x if c.isalnum() or c.isspace() or ord(c) >= 0xAC00)
    }
}

processor_factory = korean_data_processor_factory(text_processing_rules)
text_processor = processor_factory("한국어_텍스트")

sample_texts = [
    "안녕하세요!!!   파이썬을 배워봅시다~~~",
    "DATA  분석이   정말 재미있어요!@#$",
    "프로그래밍은     창의적인 활동입니다.",
    None  # 오류 발생할 데이터
]

try:
    results = text_processor(sample_texts[:-1])  # None 제외
    
    print(f"처리 통계: {results['통계']}")
    print(f"처리 결과:")
    for original, processed in zip(results["원본_데이터"], results["처리_결과"]):
        print(f"  '{original}' → '{processed}'")
        
except Exception as e:
    print(f"처리 오류: {e}")
