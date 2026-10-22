"""1권 Chapter 3. 연산과 표현식 — 3.3 Walrus 연산자 (:=) 완전 마스터

원고: manuscript/chapters/03-operators.md (320줄부터)
"""

# ---- 원고 320줄 ----
x = 1
if x == 1:
    print("x는 1입니다")

# ---- 원고 328줄 ----
if (x := 1) == 1:
    print("x는 1입니다")

# ---- 원고 335줄 ----
# Python 3.8+에서 도입된 할당 표현식
# 기존 방식 vs Walrus 연산자

# 기존 방식
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
squares = []
for num in numbers:
    square = num ** 2
    if square > 20:
        squares.append(square)

print(f"기존 방식: {squares}")

# Walrus 연산자 사용
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
squares = [square for num in numbers if (square := num ** 2) > 20]
print(f"Walrus 사용: {squares}")

# ---- 원고 396줄 ----
# 복잡한 계산을 한 번만 수행
def 복잡한_계산(x):
    """무거운 계산을 시뮬레이션"""
    import time
    time.sleep(0.001)  # 계산 시간 시뮬레이션
    return x ** 2 + x ** 3

numbers = range(1, 11)

# 기존 방식 (비효율적)
# results = [복잡한_계산(x) for x in numbers if 복잡한_계산(x) > 100]  # 두 번 계산됨

# Walrus 연산자 사용 (효율적)
results = [result for x in numbers if (result := 복잡한_계산(x)) > 100]
print(f"효율적인 결과: {results}")

# 정규 표현식에서의 활용
import re

텍스트들 = [
    "전화번호: 010-1234-5678",
    "일반 텍스트입니다",
    "또 다른 번호: 010-9876-5432",
    "이것도 일반 텍스트"
]

전화번호_패턴 = re.compile(r'010-\d{4}-\d{4}')

# 기존 방식
전화번호들_기존 = []
for 텍스트 in 텍스트들:
    match = 전화번호_패턴.search(텍스트)
    if match:
        전화번호들_기존.append(match.group())

# Walrus 연산자 사용
전화번호들_walrus = [
    match.group() 
    for 텍스트 in 텍스트들 
    if (match := 전화번호_패턴.search(텍스트))
]

print(f"기존 방식: {전화번호들_기존}")
print(f"Walrus: {전화번호들_walrus}")

# ---- 원고 445줄 ----
# 딕셔너리 처리에서의 활용
사용자_데이터 = {
    "이름": "김철수",
    "나이": 30,
    "직업": "개발자",
    "취미": ["독서", "영화감상"]
}

# 기존 방식
if "취미" in 사용자_데이터:
    취미들 = 사용자_데이터["취미"]
    if len(취미들) > 1:
        print(f"다양한 취미: {', '.join(취미들)}")

# Walrus 연산자 사용
if (취미들 := 사용자_데이터.get("취미")) and len(취미들) > 1:
    print(f"다양한 취미: {', '.join(취미들)}")

# 함수 결과 재사용
def 데이터_검증(데이터):
    """데이터 검증 후 정제된 데이터 반환"""
    if not 데이터:
        return None
    return 데이터.strip().lower()

원본_데이터 = "  PYTHON PROGRAMMING  "

# 기존 방식
정제된_데이터 = 데이터_검증(원본_데이터)
if 정제된_데이터:
    print(f"정제된 데이터: {정제된_데이터}")

# Walrus 연산자 사용
if (정제된_데이터 := 데이터_검증(원본_데이터)):
    print(f"정제된 데이터: {정제된_데이터}")

# ---- 원고 491줄 ----
if x := 5 > 3:        # 5 > 3이 먼저 계산되어 x에는 True가 들어간다
    print(x)          # True

if (x := 5) > 3:      # 괄호로 감싸야 x에 5가 들어간다
    print(x)          # 5

# ---- 원고 501줄 ----
data = list(range(150))  # 예제용 데이터

# 1. 가독성을 해치지 않도록 주의
# 좋은 예
if (length := len(data)) > 100:
    print(f"긴 데이터: {length}개 항목")

# 나쁜 예 (너무 복잡)
# if (result := complex_calc(x)) and (other := another_calc(y)) > result:

# 2. 스코프 주의사항
def 스코프_예제():
    # Walrus 연산자로 할당된 변수는 해당 스코프에서 사용 가능
    if (x := 10) > 5:
        print(f"x는 조건문 밖에서도 사용 가능: {x}")
    
    print(f"함수 끝에서도 x 사용 가능: {x}")  # 10

스코프_예제()

# 3. 리스트 컴프리헨션에서의 스코프
# 이건 작동하지 않음
# [y := f(x), y**2 for x in iterable]  # NameError

# 올바른 사용
[y**2 for x in range(5) if (y := x**2) > 10]
