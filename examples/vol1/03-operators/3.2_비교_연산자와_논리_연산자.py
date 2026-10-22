"""1권 Chapter 3. 연산과 표현식 — 3.2 비교 연산자와 논리 연산자

원고: manuscript/chapters/03-operators.md (169줄부터)
"""

# ---- 원고 169줄 ----
# 기본 비교 연산자
a, b, c = 10, 20, 10

print(f"{a} == {b}: {a == b}")  # False - 같음
print(f"{a} != {b}: {a != b}")  # True - 다름
print(f"{a} < {b}: {a < b}")    # True - 작음
print(f"{a} > {b}: {a > b}")    # False - 큼
print(f"{a} <= {c}: {a <= c}")  # True - 작거나 같음
print(f"{a} >= {c}: {a >= c}")  # True - 크거나 같음

# 연쇄 비교 (Chained Comparison)
x = 15
print(f"10 < {x} < 20: {10 < x < 20}")     # True
print(f"10 < {x} < 15: {10 < x < 15}")     # False
print(f"10 <= {x} <= 20: {10 <= x <= 20}") # True

# 문자열 비교 (사전식 순서)
print(f"'apple' < 'banana': {'apple' < 'banana'}")  # True
print(f"'Apple' < 'apple': {'Apple' < 'apple'}")    # True (ASCII 값)
print(f"'가나다' < '나다라': {'가나다' < '나다라'}")      # True (유니코드)

# 리스트 비교 (원소별 비교)
list1 = [1, 2, 3]
list2 = [1, 2, 4]
list3 = [1, 2, 3, 4]

print(f"{list1} < {list2}: {list1 < list2}")   # True (첫 번째 다른 원소)
print(f"{list1} < {list3}: {list1 < list3}")   # True (길이가 다르면 짧은 것이 작음)

# ---- 원고 216줄 ----
# 기본 논리 연산자
print(f"True and True: {True and True}")    # True
print(f"True and False: {True and False}")  # False
print(f"True or False: {True or False}")    # True
print(f"not True: {not True}")              # False

# 단축 평가 (Short-circuit Evaluation)
def 참_함수():
    print("참 함수 실행됨")
    return True

def 거짓_함수():
    print("거짓 함수 실행됨")
    return False

print("=== and 연산 단축 평가 ===")
result = 거짓_함수() and 참_함수()  # 거짓이므로 두 번째 함수는 실행되지 않음
print(f"결과: {result}")

print("\n=== or 연산 단축 평가 ===")
result = 참_함수() or 거짓_함수()   # 참이므로 두 번째 함수는 실행되지 않음
print(f"결과: {result}")

# 논리 연산자의 반환값 (불린이 아닐 수 있음)
print(f"5 and 10: {5 and 10}")        # 10 (마지막 평가된 값)
print(f"0 and 10: {0 and 10}")        # 0 (첫 번째 거짓값)
print(f"5 or 10: {5 or 10}")          # 5 (첫 번째 참값)
print(f"0 or 10: {0 or 10}")          # 10 (첫 번째 참값)
print(f"'' or 'hello': {'' or 'hello'}")  # 'hello'

# ---- 원고 254줄 ----
a = [1, 2]
b = [1, 2]   # 내용은 같지만 따로 만든 리스트
c = a        # a가 가리키는 리스트에 이름을 하나 더 붙임

print(a == b)  # True  - 값이 같다
print(a is b)  # False - 서로 다른 물건이다
print(c is a)  # True  - 완전히 같은 물건이다

# ---- 원고 268줄 ----
# 안전한 비교를 위한 함수들
def 안전한_문자열_비교(str1: str, str2: str) -> bool:
    """대소문자를 무시한 문자열 비교"""
    if str1 is None or str2 is None:
        return str1 is str2
    return str1.lower() == str2.lower()

def 근사치_비교(a: float, b: float, 허용오차: float = 1e-9) -> bool:
    """부동소수점 근사치 비교"""
    return abs(a - b) <= 허용오차

def 리스트_내용_비교(list1: list, list2: list) -> bool:
    """순서를 무시한 리스트 내용 비교"""
    return sorted(list1) == sorted(list2)

# 사용 예제
print(f"대소문자 무시 비교: {안전한_문자열_비교('Hello', 'HELLO')}")
print(f"부동소수점 근사 비교: {근사치_비교(0.1 + 0.2, 0.3)}")
print(f"리스트 내용 비교: {리스트_내용_비교([1, 2, 3], [3, 1, 2])}")

# None 값 처리 패턴
이름 = None
기본이름 = "익명"

# Falsy 값 처리
표시이름 = 이름 or 기본이름
print(f"표시 이름: {표시이름}")

# 명시적 None 체크
if 이름 is not None:
    표시이름 = 이름
else:
    표시이름 = 기본이름

# 더 간단한 방법
표시이름 = 이름 if 이름 is not None else 기본이름
