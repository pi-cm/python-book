"""1권 Chapter 17: 표준 라이브러리 핵심 가이드 — 데이터 직렬화

원고: manuscript/chapters/17-standard-library-guide.md (348줄부터)
"""

# ---- 원고 348줄 ----
import json
from datetime import date

# 한국 고객 데이터
customer_data = {
    "고객_정보": {
        "이름": "김철수",
        "나이": 35,
        "주소": "서울특별시 강남구 역삼동",
        "이메일": "kim.cs@example.com",
        "가입일": str(date.today()),
        "구매_이력": [
            {"상품": "파이썬 책", "가격": 25000, "날짜": "2024-01-15"},
            {"상품": "프로그래밍 강의", "가격": 150000, "날짜": "2024-02-10"}
        ]
    }
}

# 한글이 깨지지 않도록 저장
json_string = json.dumps(customer_data, ensure_ascii=False, indent=2)
print("JSON 문자열:")
print(json_string)

# 파일로 저장
with open("고객_데이터.json", "w", encoding="utf-8") as f:
    json.dump(customer_data, f, ensure_ascii=False, indent=2)

# 파일에서 읽기
with open("고객_데이터.json", "r", encoding="utf-8") as f:
    loaded_data = json.load(f)
    customer_name = loaded_data["고객_정보"]["이름"]
    print(f"고객명: {customer_name}")

# ---- 원고 387줄 ----
import pickle

scores = {"김철수": [85, 78, 92], "이영희": [92, 88, 84]}

with open("scores.pkl", "wb") as f:   # 바이너리 쓰기 모드
    pickle.dump(scores, f)

with open("scores.pkl", "rb") as f:
    loaded = pickle.load(f)

print(loaded)
print(loaded == scores, type(loaded["김철수"]))

# ---- 원고 418줄 ----
import csv

# 한국 직원 데이터
employees = [
    {"이름": "김철수", "부서": "개발팀", "연봉": 5000, "입사일": "2020-03-01"},
    {"이름": "이영희", "부서": "기획팀", "연봉": 4500, "입사일": "2021-06-15"},
    {"이름": "박민수", "부서": "영업팀", "연봉": 4800, "입사일": "2019-11-20"},
]

# CSV 파일 쓰기
with open("직원_명단.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["이름", "부서", "연봉", "입사일"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(employees)

# CSV 파일 읽기
with open("직원_명단.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    print("직원 목록:")
    for row in reader:
        print(f"- {row['이름']} ({row['부서']}) - {int(row['연봉']):,}만원")

# 고급 CSV 처리
import io

csv_data = """이름,나이,도시
김철수,25,서울
이영희,30,부산
박민수,28,대구"""

# StringIO를 사용한 메모리 CSV 처리
csv_stream = io.StringIO(csv_data)
reader = csv.DictReader(csv_stream)

for row in reader:
    print(f"{row['이름']}님은 {row['나이']}세, {row['도시']} 거주")
