"""1권 Chapter 7: 딕셔너리와 집합 — 7.1 딕셔너리 기본 개념

원고: manuscript/chapters/07-dictionaries-sets.md (29줄부터)
"""

# ---- 원고 29줄 ----
# 기본 딕셔너리 생성
student = {
    "이름": "김철수",
    "나이": 20,
    "전공": "컴퓨터과학과",
    "학점": 3.8
}

# 다양한 키 타입 사용
mixed_dict = {
    "문자열키": "값1",
    42: "숫자키",
    (1, 2): "튜플키",
    True: "불린키"
}

# 빈 딕셔너리 생성
empty_dict1 = {}
empty_dict2 = dict()

print(f"학생 정보: {student}")
print(f"혼합 딕셔너리: {mixed_dict}")

# ---- 원고 66줄 ----
# 한국 지역별 인구 데이터
population = {
    "서울": 9720846,
    "부산": 3448737,
    "대구": 2438031,
    "인천": 2963991,
    "광주": 1441970,
    "대전": 1475221,
    "울산": 1124459
}

# 값 접근
print(f"서울 인구: {population['서울']:,}명")
print(f"부산 인구: {population.get('부산'):,}명")

# 안전한 접근 (기본값 사용)
print(f"세종 인구: {population.get('세종', '정보 없음')}")

# 값 수정
population["서울"] = 9700000
print(f"수정된 서울 인구: {population['서울']:,}명")

# 새 항목 추가
population["세종"] = 373096
print(f"세종 추가 후: {len(population)}개 도시")

# 여러 값 동시 업데이트
population.update({"제주": 672948, "강원": 1540681})
print(f"업데이트 후: {len(population)}개 지역")
