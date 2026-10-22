"""1권 Chapter 7: 딕셔너리와 집합 — 7.2 딕셔너리 메서드

원고: manuscript/chapters/07-dictionaries-sets.md (112줄부터)
"""

# ---- 원고 112줄 ----
# 한국 전통 음식과 지역
korean_foods = {
    "김치찌개": "전국",
    "불고기": "서울/경기",
    "냉면": "평양/함흥",
    "갈비탕": "서울",
    "해물탕": "부산",
    "막국수": "강원도",
    "순두부찌개": "강원도"
}

# keys(): 모든 키 조회
food_names = list(korean_foods.keys())
print(f"음식 이름들: {food_names}")

# values(): 모든 값 조회  
regions = list(korean_foods.values())
print(f"지역들: {regions}")

# items(): 키-값 쌍 조회
print("음식별 지역:")
for food, region in korean_foods.items():
    print(f"  {food}: {region}")

# 특정 지역 음식 찾기
gangwon_foods = [food for food, region in korean_foods.items() 
                 if "강원도" in region]
print(f"강원도 음식: {gangwon_foods}")

# ---- 원고 152줄 ----
# 학생 성적 관리
grades = {
    "김철수": {"국어": 85, "영어": 92, "수학": 78},
    "이영희": {"국어": 95, "영어": 87, "수학": 91},
    "박민수": {"국어": 78, "영어": 82, "수학": 95}
}

# pop(): 항목 제거 후 반환
removed_student = grades.pop("박민수")
print(f"제거된 학생: {removed_student}")

# popitem(): 마지막 항목 제거 (Python 3.7+에서 순서 보장)
last_student = grades.popitem()
print(f"마지막 학생: {last_student}")

# 다시 추가
grades["박민수"] = {"국어": 88, "영어": 85, "수학": 92}
grades["최지영"] = {"국어": 90, "영어": 88, "수학": 89}

# setdefault(): 키가 없을 때만 추가
grades.setdefault("정수진", {"국어": 0, "영어": 0, "수학": 0})
print(f"새 학생 추가: {'정수진' in grades}")

# clear(): 모든 항목 제거
test_dict = grades.copy()
test_dict.clear()
print(f"clear 후 크기: {len(test_dict)}")

# del 문으로 특정 키 제거
del grades["정수진"]
print(f"정수진 제거 후: {list(grades.keys())}")

# ---- 원고 190줄 ----
def 인사():
    return "안녕하세요"

def 작별():
    return "안녕히 가세요"

명령들 = {"인사": 인사, "작별": 작별}
print(명령들["인사"]())                                  # 안녕하세요
print(명령들.get("춤", lambda: "모르는 명령입니다")())   # 모르는 명령입니다
