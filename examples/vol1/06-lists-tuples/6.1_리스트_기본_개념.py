"""1권 Chapter 6: 리스트와 튜플 — 6.1 리스트 기본 개념

원고: manuscript/chapters/06-lists-tuples.md (34줄부터)
"""

# ---- 원고 34줄 ----
# 기본 리스트 생성
fruits = ["사과", "바나나", "오렌지", "포도"]
numbers = [1, 2, 3, 4, 5]
mixed = ["김철수", 25, True, 3.14]

# 빈 리스트 생성
empty_list1 = []
empty_list2 = list()

print(f"과일: {fruits}")
print(f"숫자: {numbers}")
print(f"혼합: {mixed}")

# ---- 원고 61줄 ----
cities = ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]

# 인덱싱
print(f"첫 번째 도시: {cities[0]}")
print(f"마지막 도시: {cities[-1]}")
print(f"뒤에서 두 번째: {cities[-2]}")

# 슬라이싱
print(f"처음 3개 도시: {cities[:3]}")
print(f"마지막 3개 도시: {cities[-3:]}")
print(f"3번째부터 5번째까지: {cities[2:5]}")
print(f"홀수 번째 도시들: {cities[::2]}")
print(f"역순으로: {cities[::-1]}")

# 슬라이스로 부분 수정
cities[2:4] = ["창원", "안산"]
print(f"수정 후: {cities}")
