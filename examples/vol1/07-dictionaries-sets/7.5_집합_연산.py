"""1권 Chapter 7: 딕셔너리와 집합 — 7.5 집합 연산

원고: manuscript/chapters/07-dictionaries-sets.md (361줄부터)
"""

# ---- 원고 361줄 ----
# 프로그래밍 언어 선호도 조사
backend_developers = {"Python", "Java", "JavaScript", "Go", "C++"}
frontend_developers = {"JavaScript", "TypeScript", "Python", "HTML", "CSS"}
data_scientists = {"Python", "R", "SQL", "Scala", "Java"}

# 합집합 (union): |, union()
all_languages = backend_developers | frontend_developers | data_scientists
print(f"모든 언어: {all_languages}")

# 교집합 (intersection): &, intersection()
backend_frontend = backend_developers & frontend_developers
print(f"백엔드-프론트엔드 공통: {backend_frontend}")

# 차집합 (difference): -, difference()
only_backend = backend_developers - frontend_developers
print(f"백엔드 전용: {only_backend}")

# 대칭차집합 (symmetric_difference): ^, symmetric_difference()
backend_or_frontend = backend_developers ^ frontend_developers
print(f"백엔드 또는 프론트엔드 전용: {backend_or_frontend}")

# 부분집합 검사
python_users = {"Python"}
print(f"Python 사용자가 데이터 과학자 부분집합인가? {python_users.issubset(data_scientists)}")
print(f"데이터 과학자가 Python 사용자 상위집합인가? {data_scientists.issuperset(python_users)}")

# ---- 원고 395줄 ----
# 한국 대학교 전공 분석
engineering_majors = {
    "컴퓨터공학과", "전자공학과", "기계공학과", 
    "화학공학과", "건축공학과", "산업공학과"
}

science_majors = {
    "수학과", "물리학과", "화학과", "생물학과",
    "컴퓨터과학과", "통계학과", "지구과학과"
}

business_majors = {
    "경영학과", "경제학과", "회계학과", 
    "마케팅학과", "국제통상학과", "경영정보학과"
}

# 전체 전공
all_majors = engineering_majors | science_majors | business_majors
print(f"총 전공 수: {len(all_majors)}")

# STEM 전공 (Science, Technology, Engineering, Mathematics)
stem_majors = engineering_majors | science_majors
print(f"STEM 전공: {len(stem_majors)}개")

# 컴퓨터 관련 전공 찾기
computer_keywords = {"컴퓨터", "정보"}
computer_majors = {
    major for major in all_majors 
    if any(keyword in major for keyword in computer_keywords)
}
print(f"컴퓨터 관련 전공: {computer_majors}")

# 학과별 특성 분석
def analyze_major_characteristics(majors, category_name):
    char_frequency = {}
    for major in majors:
        for char in major:
            char_frequency[char] = char_frequency.get(char, 0) + 1
    
    common_chars = sorted(char_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"{category_name} 전공 특성 문자: {common_chars}")

analyze_major_characteristics(engineering_majors, "공학계열")
analyze_major_characteristics(science_majors, "자연과학계열")
