"""1권 Chapter 5. 반복문과 루프 — 5.1 for 문 완전정복

원고: manuscript/chapters/05-loops.md (35줄부터)
"""

# ---- 원고 35줄 ----
# 1. 기본 반복
과일들 = ["사과", "바나나", "오렌지", "포도", "딸기"]

print("=== 기본 for 루프 ===")
for 과일 in 과일들:
    print(f"맛있는 {과일}!")

# 2. 인덱스와 함께 반복 - enumerate()
print("\n=== enumerate() 활용 ===")
for 순서, 과일 in enumerate(과일들):
    print(f"{순서 + 1}번째: {과일}")

# 시작 인덱스 지정
for 순서, 과일 in enumerate(과일들, start=1):
    print(f"{순서}. {과일}")

# 3. 여러 시퀀스 동시 반복 - zip()
이름들 = ["김철수", "이영희", "박민수"]
나이들 = [25, 30, 35]
직업들 = ["개발자", "디자이너", "기획자"]

print("\n=== zip() 활용 ===")
for 이름, 나이, 직업 in zip(이름들, 나이들, 직업들):
    print(f"{이름}({나이}세) - {직업}")

# 길이가 다른 시퀀스들의 zip
from itertools import zip_longest

긴_리스트 = [1, 2, 3, 4, 5]
짧은_리스트 = ['a', 'b', 'c']

print("\n=== 길이가 다른 시퀀스 처리 ===")
for 숫자, 문자 in zip_longest(긴_리스트, 짧은_리스트, fillvalue='?'):
    print(f"{숫자} - {문자}")

# ---- 원고 76줄 ----
A = [1, 2, 3, 4]
B = ["a", "b", "c"]

for i, (a, b) in enumerate(zip(A, B)):
    print(i, a, b)

# ---- 원고 96줄 ----
# range() 함수의 모든 형태
print("=== range() 기본 사용법 ===")

# range(stop)
for i in range(5):
    print(f"0부터 4까지: {i}")

# range(start, stop)
print("\n5부터 9까지:")
for i in range(5, 10):
    print(i, end=" ")

# range(start, stop, step)
print("\n\n짝수만:")
for i in range(0, 11, 2):
    print(i, end=" ")

print("\n\n거꾸로 카운트다운:")
for i in range(10, 0, -1):
    print(i, end=" ")

print("\n\n한국어 구구단 (2단):")
단 = 2
for i in range(1, 10):
    print(f"{단} × {i} = {단 * i}")

# range를 리스트로 변환 (메모리 사용 주의)
작은_범위 = list(range(1, 6))
print(f"\n작은 범위 리스트: {작은_범위}")

# 대용량 range는 리스트 변환 금지!
# 큰_범위 = list(range(1000000))  # 메모리 낭비!

# range 객체의 특성
범위 = range(1, 11)
print(f"범위 길이: {len(범위)}")
print(f"5가 범위에 있나? {5 in 범위}")
print(f"범위의 첫 번째: {범위[0]}")
print(f"범위의 마지막: {범위[-1]}")

# ---- 원고 149줄 ----
# 1. 딕셔너리 반복의 모든 방법
한국_도시_인구 = {
    "서울": 9720846,
    "부산": 3348871,
    "인천": 2947217,
    "대구": 2427954,
    "광주": 1456468,
    "대전": 1458365
}

print("=== 딕셔너리 반복 패턴 ===")

# 키만 반복
print("도시 목록:")
for 도시 in 한국_도시_인구:  # .keys()와 동일
    print(f"- {도시}")

# 값만 반복
print("\n인구 목록:")
for 인구 in 한국_도시_인구.values():
    print(f"인구: {인구:,}명")

# 키-값 쌍 반복
print("\n도시별 인구:")
for 도시, 인구 in 한국_도시_인구.items():
    print(f"{도시}: {인구:,}명")

# 2. 문자열 반복
한국어_문장 = "안녕하세요, 파이썬!"

print(f"\n=== 문자열 '{한국어_문장}' 문자별 반복 ===")
for i, 문자 in enumerate(한국어_문장):
    if 문자.isalpha():  # 한글/영문자만
        print(f"위치 {i}: '{문자}'")

# 3. 역순 반복 - reversed()
print("\n=== 역순 반복 ===")
숫자들 = [1, 2, 3, 4, 5]
for 숫자 in reversed(숫자들):
    print(숫자, end=" ")

print("\n\n문자열 역순:")
for 문자 in reversed("PYTHON"):
    print(문자, end="")

# 4. 정렬된 반복 - sorted()
무작위_숫자들 = [3, 1, 4, 1, 5, 9, 2, 6]
print(f"\n\n=== 정렬된 반복 ===")
print(f"원본: {무작위_숫자들}")

print("오름차순:")
for 숫자 in sorted(무작위_숫자들):
    print(숫자, end=" ")

print("\n내림차순:")
for 숫자 in sorted(무작위_숫자들, reverse=True):
    print(숫자, end=" ")

# 5. 중복 제거 반복
중복_과일들 = ["사과", "바나나", "사과", "오렌지", "바나나", "포도"]
print(f"\n\n=== 중복 제거 반복 ===")
print(f"원본: {중복_과일들}")

print("중복 제거 (순서 유지):")
이미_본_과일 = set()
for 과일 in 중복_과일들:
    if 과일 not in 이미_본_과일:
        print(과일, end=" ")
        이미_본_과일.add(과일)

print("\n중복 제거 (set 활용):")
for 과일 in sorted(set(중복_과일들)):
    print(과일, end=" ")
