"""1권 Chapter 7: 딕셔너리와 집합 — 7.4 집합(Set) 기본 개념

원고: manuscript/chapters/07-dictionaries-sets.md (280줄부터)
"""

# ---- 원고 280줄 ----
# 기본 집합 생성
fruits = {"사과", "바나나", "오렌지", "포도"}
numbers = {1, 2, 3, 4, 5}

# 리스트에서 집합 생성 (중복 제거)
duplicated_list = [1, 2, 2, 3, 3, 3, 4, 4, 5]
unique_numbers = set(duplicated_list)
print(f"중복 제거: {unique_numbers}")

# 문자열에서 집합 생성
text = "안녕하세요"
unique_chars = set(text)
print(f"고유 문자: {unique_chars}")

# 빈 집합 생성 (주의: {}는 딕셔너리!)
empty_set = set()
print(f"빈 집합: {empty_set}")

# frozenset (불변 집합)
immutable_set = frozenset([1, 2, 3, 4, 5])
print(f"불변 집합: {immutable_set}")

# ---- 원고 313줄 ----
# 한국 도시 집합
seoul_metro = {"서울", "인천", "수원", "성남", "고양", "안양"}
busan_metro = {"부산", "울산", "창원", "김해"}

# add(): 요소 추가
seoul_metro.add("의정부")
print(f"의정부 추가: {seoul_metro}")

# update(): 여러 요소 추가
seoul_metro.update(["파주", "이천"])
print(f"여러 도시 추가: {seoul_metro}")

# remove(): 요소 제거 (없으면 에러)
seoul_metro.remove("이천")
print(f"이천 제거: {seoul_metro}")

# discard(): 요소 제거 (없어도 에러 안 남)
seoul_metro.discard("존재하지않는도시")
print(f"안전 제거 시도 후: {len(seoul_metro)}")

# pop(): 임의 요소 제거 후 반환
removed_city = seoul_metro.pop()
print(f"제거된 도시: {removed_city}")

# clear(): 모든 요소 제거
test_set = seoul_metro.copy()
test_set.clear()
print(f"clear 후: {test_set}")
