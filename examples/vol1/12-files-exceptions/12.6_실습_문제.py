"""1권 Chapter 12: 파일과 예외 처리 — 12.6 실습 문제

원고: manuscript/chapters/12-files-exceptions.md (1546줄부터)
"""

# ---- 원고 1546줄 ----
# 1번: 파일 읽기/쓰기 기본
def create_korean_diary():
    """한국어 일기 파일 생성"""
    pass

# 문제: 한국어 일기를 파일로 저장하고 읽어오는 함수를 만드세요
# 답:
def create_korean_diary():
    diary_content = """2024년 3월 15일 일기

오늘은 파이썬 파일 처리를 공부했다.
한글 인코딩도 배웠고, pathlib도 사용해봤다.
내일은 예외 처리를 더 자세히 공부해야겠다.

기분: 좋음
날씨: 맑음"""
    
    with open("my_diary.txt", "w", encoding="utf-8") as f:
        f.write(diary_content)
    
    with open("my_diary.txt", "r", encoding="utf-8") as f:
        content = f.read()
        print(content)
    
    import os
    os.remove("my_diary.txt")

create_korean_diary()

# 2번: pathlib 활용
from pathlib import Path

# 문제: 한국어 프로젝트 구조를 pathlib로 만드세요
# 답:
def create_project_structure():
    project = Path("한국어_프로젝트")
    
    # 디렉터리 구조 생성
    dirs = ["소스코드", "데이터", "문서", "테스트"]
    for dir_name in dirs:
        (project / dir_name).mkdir(parents=True, exist_ok=True)
    
    # 파일 생성
    (project / "README.md").write_text("# 한국어 프로젝트", encoding="utf-8")
    (project / "소스코드" / "main.py").write_text('print("안녕하세요!")', encoding="utf-8")
    
    print(f"프로젝트 구조 생성: {project}")
    
    # 정리
    import shutil
    shutil.rmtree(project)

create_project_structure()

# 3번: 예외 처리 기본
def safe_division(a, b):
    # 문제: 안전한 나눗셈 함수를 만드세요
    pass

# 답:
def safe_division(a, b):
    try:
        result = a / b
        return {"success": True, "result": result}
    except ZeroDivisionError:
        return {"success": False, "error": "0으로 나눌 수 없습니다"}
    except TypeError:
        return {"success": False, "error": "숫자만 입력 가능합니다"}

print(safe_division(10, 2))
print(safe_division(10, 0))
print(safe_division("10", 2))

# 4번: CSV 처리
import csv

# 문제: 한국 학생 성적을 CSV로 관리하는 함수를 만드세요
# 답:
def manage_student_grades():
    students = [
        {"이름": "김철수", "국어": 85, "영어": 90, "수학": 88},
        {"이름": "이영희", "국어": 92, "영어": 87, "수학": 95},
        {"이름": "박민수", "국어": 78, "영어": 82, "수학": 90}
    ]
    
    # CSV 저장
    with open("성적.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = ["이름", "국어", "영어", "수학"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(students)
    
    # CSV 읽기 및 평균 계산
    with open("성적.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scores = [int(row["국어"]), int(row["영어"]), int(row["수학"])]
            avg = sum(scores) / len(scores)
            print(f"{row['이름']}: 평균 {avg:.1f}점")
    
    import os
    os.remove("성적.csv")

manage_student_grades()

# 5번: JSON 처리
import json

# 문제: 한국 음식 정보를 JSON으로 저장하고 검색하는 함수를 만드세요
# 답:
def korean_food_database():
    foods = {
        "한식": [
            {"이름": "김치찌개", "재료": ["김치", "돼지고기", "두부"], "매운맛": 3},
            {"이름": "비빔밥", "재료": ["밥", "나물", "고추장"], "매운맛": 2},
            {"이름": "불고기", "재료": ["소고기", "양파", "배"], "매운맛": 1}
        ]
    }
    
    # JSON 저장
    with open("음식.json", "w", encoding="utf-8") as f:
        json.dump(foods, f, ensure_ascii=False, indent=2)
    
    # JSON 읽기 및 검색
    with open("음식.json", "r", encoding="utf-8") as f:
        loaded_foods = json.load(f)
    
    # 매운맛 2 이상인 음식 찾기
    spicy_foods = [food for food in loaded_foods["한식"] if food["매운맛"] >= 2]
    print("매운 음식:")
    for food in spicy_foods:
        print(f"- {food['이름']} (매운맛: {food['매운맛']})")
    
    import os
    os.remove("음식.json")

korean_food_database()
