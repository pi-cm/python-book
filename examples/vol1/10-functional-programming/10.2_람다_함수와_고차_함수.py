"""1권 Chapter 10: 함수형 프로그래밍 — 10.2 람다 함수와 고차 함수

원고: manuscript/chapters/10-functional-programming.md (210줄부터)
"""

# ---- 원고 210줄 ----
def get_score(x):
    return x["점수"]

# ---- 원고 219줄 ----
# 한국어 정렬을 위한 람다 함수들
korean_students = [
    {"이름": "김철수", "점수": 85, "학과": "컴퓨터"},
    {"이름": "이영희", "점수": 92, "학과": "경영"}, 
    {"이름": "박민수", "점수": 78, "학과": "컴퓨터"},
    {"이름": "최지영", "점수": 88, "학과": "경영"},
    {"이름": "정수진", "점수": 95, "학과": "수학"}
]

# 점수순 정렬
by_score = sorted(korean_students, key=lambda x: x["점수"], reverse=True)
print("점수순 정렬:")
for student in by_score[:3]:
    print(f"{student['이름']}: {student['점수']}점")

# 이름순 정렬 (한글 가나다순)
by_name = sorted(korean_students, key=lambda x: x["이름"])
print(f"\n이름순 정렬: {[s['이름'] for s in by_name]}")

# 학과별 그룹핑 후 점수순 정렬
from itertools import groupby

grouped = groupby(
    sorted(korean_students, key=lambda x: x["학과"]), 
    key=lambda x: x["학과"]
)

print("\n학과별 최고점:")
for department, students in grouped:
    student_list = list(students)
    top_student = max(student_list, key=lambda x: x["점수"])
    print(f"{department}과: {top_student['이름']} ({top_student['점수']}점)")

# ---- 원고 263줄 ----
def add2(a, b): return a + b
def sub2(a, b): return a - b
def mul2(a, b): return a * b
def div2(a, b): return a / b

funcs = [add2, sub2, mul2, div2]   # 함수를 리스트에 담을 수 있어요
for func in funcs:
    print(func.__name__, ":", func(8, 2))

say = print                         # 함수에 다른 이름표를 붙일 수도 있고요
say("print를 say라는 이름으로 불렀어요")

# ---- 원고 283줄 ----
def korean_currency_formatter(amount: int, unit: str = "원") -> str:
    """한국 화폐 단위 포맷터"""
    
    # 큰 단위 변환기들
    def to_man(amount):
        if amount < 10000:
            return str(amount)
        man, rest = divmod(amount, 10000)
        return f"{man}만{rest}" if rest > 0 else f"{man}만"  # 25만0원이 아니라 25만원
    
    def to_eok(amount):
        eok = amount // 100000000
        remaining = amount % 100000000
        
        if eok > 0:
            if remaining > 0:
                man_part = to_man(remaining)
                return f"{eok}억{man_part}"
            return f"{eok}억"
        return to_man(amount)
    
    # 조 단위까지 처리
    def to_jo(amount):
        jo = amount // 1000000000000
        remaining = amount % 1000000000000
        
        if jo > 0:
            if remaining > 0:
                eok_part = to_eok(remaining)
                return f"{jo}조{eok_part}"
            return f"{jo}조"
        return to_eok(amount)
    
    formatted = to_jo(amount)
    return f"{formatted}{unit}"

def create_price_converter(exchange_rate: float, currency_name: str):
    """가격 변환기 생성 함수 (고차 함수)"""
    def converter(krw_amount: int) -> str:
        converted = krw_amount / exchange_rate
        return f"{converted:,.2f} {currency_name}"
    
    return converter

def create_tax_calculator(tax_rate: float, tax_name: str):
    """세금 계산기 생성 함수"""
    def calculator(amount: int, include_tax: bool = True) -> dict:
        if include_tax:
            # 세금 포함 가격에서 세전 가격 계산
            pre_tax = amount / (1 + tax_rate)
            tax_amount = amount - pre_tax
        else:
            # 세전 가격에서 세금 계산
            pre_tax = amount
            tax_amount = amount * tax_rate
            amount = pre_tax + tax_amount
        
        return {
            "세전가격": f"{pre_tax:,.0f}원",
            "세금": f"{tax_amount:,.0f}원",
            "총가격": f"{amount:,.0f}원",
            "세금종류": tax_name,
            "세율": f"{tax_rate*100:.1f}%"
        }
    
    return calculator

# 사용 예제
print("화폐 단위 포맷팅:")
amounts = [15000, 250000, 3500000, 120000000, 1500000000000]
for amount in amounts:
    print(f"{amount:,}원 → {korean_currency_formatter(amount)}")

# 환율 변환기
usd_converter = create_price_converter(1300, "USD")
eur_converter = create_price_converter(1400, "EUR") 
jpy_converter = create_price_converter(9.5, "JPY")

print(f"\n환율 변환:")
krw_price = 130000
print(f"{krw_price:,}원 = {usd_converter(krw_price)}")
print(f"{krw_price:,}원 = {eur_converter(krw_price)}")
print(f"{krw_price:,}원 = {jpy_converter(krw_price)}")

# 세금 계산기
vat_calc = create_tax_calculator(0.10, "부가가치세")
income_tax_calc = create_tax_calculator(0.24, "소득세")

print(f"\n세금 계산:")
price = 100000
vat_result = vat_calc(price, include_tax=False)
print("부가세 계산:")
for key, value in vat_result.items():
    print(f"  {key}: {value}")
