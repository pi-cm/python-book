"""1권 Chapter 10: 함수형 프로그래밍 — 10.1 함수 정의 심화: 매개변수 더 깊이

원고: manuscript/chapters/10-functional-programming.md (42줄부터)
"""

# ---- 원고 42줄 ----
from typing import Optional

def greet_korean(name: str, age: Optional[int] = None) -> str:
    """한국식 인사 함수"""
    if age is not None:
        return f"안녕하세요, {name}님! {age}세이시군요."
    return f"안녕하세요, {name}님!"

def calculate_korean_age(birth_year: int, current_year: Optional[int] = None) -> int:
    """세는 나이 계산 (올해 - 출생연도 + 1)"""
    if current_year is None:
        from datetime import datetime
        current_year = datetime.now().year
    
    international_age = current_year - birth_year
    korean_age = international_age + 1  # 한국 나이는 태어나면서 1세
    return korean_age

# 사용 예제
print(greet_korean("김철수"))
print(greet_korean("이영희", 25))

korean_age = calculate_korean_age(1995)
print(f"1995년생의 한국 나이: {korean_age}세")

# ---- 원고 77줄 ----
def format_korean_address(*address_parts, separator=" ", postal_code=None):
    """한국 주소 포맷팅"""
    if not address_parts:
        return "주소가 입력되지 않았습니다."
    
    formatted_address = separator.join(address_parts)
    
    if postal_code:
        formatted_address = f"({postal_code}) {formatted_address}"
    
    return formatted_address

def create_student_profile(name: str, **kwargs) -> dict:
    """학생 프로필 생성 (키워드 인자 활용)"""
    profile = {
        "이름": name,
        "나이": kwargs.get("age", "미입력"),
        "전공": kwargs.get("major", "미정"),
        "학년": kwargs.get("grade", 1),
        "연락처": kwargs.get("phone", "미입력"),
        "이메일": kwargs.get("email", "미입력")
    }
    
    # 추가 정보가 있다면 포함
    extra_info = {k: v for k, v in kwargs.items() 
                  if k not in ["age", "major", "grade", "phone", "email"]}
    
    if extra_info:
        profile["추가정보"] = extra_info
    
    return profile

# 사용 예제
print("주소 포맷팅:")
print(format_korean_address("서울시", "강남구", "역삼동", "123-45"))
print(format_korean_address("부산시", "해운대구", "우동", postal_code="48094"))

print("\n학생 프로필:")
student = create_student_profile(
    "김철수",
    age=20,
    major="컴퓨터과학과",
    grade=2,
    phone="010-1234-5678",
    hobby="프로그래밍",
    mbti="ISTJ"
)

for key, value in student.items():
    print(f"{key}: {value}")

# ---- 원고 138줄 ----
def calculate_loan_payment(
    principal: int,        # 원금
    rate: float,          # 연이율
    years: int,           # 대출 기간
    *,                    # 이후 매개변수는 키워드 전용
    payment_type: str = "equal_payment",  # 상환 방식
    include_insurance: bool = False,       # 보험 포함 여부
    insurance_rate: float = 0.005         # 보험료율
) -> dict:
    """한국 주택담보대출 계산기"""
    
    monthly_rate = rate / 12
    total_months = years * 12
    
    if payment_type == "equal_payment":  # 원리금균등상환
        if monthly_rate == 0:
            monthly_payment = principal / total_months
        else:
            monthly_payment = principal * (
                monthly_rate * (1 + monthly_rate) ** total_months
            ) / ((1 + monthly_rate) ** total_months - 1)
    
    elif payment_type == "equal_principal":  # 원금균등상환
        monthly_principal = principal / total_months
        # 첫 달 이자 (최대 이자)
        first_month_interest = principal * monthly_rate
        monthly_payment = monthly_principal + first_month_interest
    
    else:
        raise ValueError("payment_type은 'equal_payment' 또는 'equal_principal'이어야 합니다.")
    
    # 보험료 계산
    insurance_payment = 0
    if include_insurance:
        insurance_payment = principal * insurance_rate / 12
        monthly_payment += insurance_payment
    
    total_payment = monthly_payment * total_months
    total_interest = total_payment - principal
    
    return {
        "원금": f"{principal:,}원",
        "월상환액": f"{monthly_payment:,.0f}원",
        "총상환액": f"{total_payment:,.0f}원", 
        "총이자": f"{total_interest:,.0f}원",
        "상환방식": "원리금균등" if payment_type == "equal_payment" else "원금균등",
        "보험료": f"{insurance_payment:,.0f}원" if include_insurance else "없음"
    }

# 사용 예제 (키워드 전용 매개변수 활용)
loan1 = calculate_loan_payment(
    300000000,  # 3억원
    0.035,      # 3.5%
    20,         # 20년
    payment_type="equal_payment",
    include_insurance=True
)

print("주택담보대출 계산 결과:")
for key, value in loan1.items():
    print(f"{key}: {value}")
