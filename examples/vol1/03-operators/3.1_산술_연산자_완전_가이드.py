"""1권 Chapter 3. 연산과 표현식 — 3.1 산술 연산자 완전 가이드

원고: manuscript/chapters/03-operators.md (36줄부터)
"""

# ---- 원고 36줄 ----
# 기본 연산들
a, b = 17, 5

print(f"덧셈: {a} + {b} = {a + b}")        # 22
print(f"뺄셈: {a} - {b} = {a - b}")        # 12
print(f"곱셈: {a} * {b} = {a * b}")        # 85
print(f"나눗셈: {a} / {b} = {a / b}")      # 3.4
print(f"몫: {a} // {b} = {a // b}")        # 3
print(f"나머지: {a} % {b} = {a % b}")      # 2
print(f"거듭제곱: {a} ** {b} = {a ** b}")  # 1419857

# 음수와의 연산
print(f"음수 나눗셈: {-17} // {5} = {-17 // 5}")    # -4 (음의 무한대 방향)
print(f"음수 나머지: {-17} % {5} = {-17 % 5}")      # 3
print(f"양수 음수: {17} // {-5} = {17 // -5}")      # -4
print(f"양수 음수: {17} % {-5} = {17 % -5}")        # -3

# ---- 원고 69줄 ----
# divmod() 함수 - 몫과 나머지를 동시에
몫, 나머지 = divmod(17, 5)
print(f"divmod(17, 5) = ({몫}, {나머지})")

# 부동소수점 나눗셈의 주의사항
print(f"0.1 + 0.1 + 0.1 = {0.1 + 0.1 + 0.1}")  # 0.30000000000000004
print(f"0.3 == 0.1 + 0.1 + 0.1: {0.3 == 0.1 + 0.1 + 0.1}")  # False

# 해결책 1: round() 함수
import math
result = 0.1 + 0.1 + 0.1
print(f"round(0.3, 1) == 0.3: {round(result, 1) == 0.3}")  # True

# 해결책 2: math.isclose() 함수
print(f"math.isclose(0.3, 0.1+0.1+0.1): {math.isclose(0.3, 0.1+0.1+0.1)}")

# 해결책 3: decimal 모듈
from decimal import Decimal, getcontext

# 정밀도 설정
getcontext().prec = 28

d1 = Decimal('0.1')
d2 = Decimal('0.1') 
d3 = Decimal('0.1')
result_decimal = d1 + d2 + d3
print(f"Decimal: {result_decimal} == 0.3: {result_decimal == Decimal('0.3')}")

# 큰 수의 거듭제곱
huge_number = 2 ** 1000
print(f"2^1000의 자릿수: {len(str(huge_number))}")
print(f"2^1000의 마지막 10자리: {str(huge_number)[-10:]}")

# ---- 원고 108줄 ----
def 한국어_사칙연산(첫번째_수: float, 연산자: str, 두번째_수: float) -> float:
    """한국어 연산자를 사용한 계산기"""
    연산_매핑 = {
        "더하기": "+",
        "플러스": "+",
        "빼기": "-",
        "마이너스": "-",
        "곱하기": "*",
        "곱셈": "*",
        "나누기": "/",
        "나눗셈": "/",
        "몫": "//",
        "나머지": "%",
        "제곱": "**"
    }
    
    if 연산자 not in 연산_매핑:
        raise ValueError(f"지원하지 않는 연산자: {연산자}")
    
    연산_기호 = 연산_매핑[연산자]
    
    # eval() 대신 안전한 계산
    match 연산_기호:
        case "+":
            return 첫번째_수 + 두번째_수
        case "-":
            return 첫번째_수 - 두번째_수
        case "*":
            return 첫번째_수 * 두번째_수
        case "/":
            if 두번째_수 == 0:
                raise ZeroDivisionError("0으로 나눌 수 없습니다")
            return 첫번째_수 / 두번째_수
        case "//":
            if 두번째_수 == 0:
                raise ZeroDivisionError("0으로 나눌 수 없습니다")
            return 첫번째_수 // 두번째_수
        case "%":
            if 두번째_수 == 0:
                raise ZeroDivisionError("0으로 나눌 수 없습니다")
            return 첫번째_수 % 두번째_수
        case "**":
            return 첫번째_수 ** 두번째_수

# 한국어 계산기 사용 예제
print(f"10 더하기 5 = {한국어_사칙연산(10, '더하기', 5)}")
print(f"20 나누기 4 = {한국어_사칙연산(20, '나누기', 4)}")
print(f"3 제곱 4 = {한국어_사칙연산(3, '제곱', 4)}")
