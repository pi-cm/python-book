"""1권 Chapter 12: 파일과 예외 처리 — 12.5 CSV와 JSON 파일 처리

원고: manuscript/chapters/12-files-exceptions.md (1198줄부터)
"""

# ---- 원고 1198줄 ----
import csv
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime, date
from decimal import Decimal

def korean_csv_processing():
    """한국어 CSV 파일 처리"""
    
    print("=== 한국어 CSV 파일 처리 ===")
    
    # 한국 학생 데이터 생성
    korean_students = [
        {"이름": "김철수", "나이": 20, "전공": "컴퓨터과학과", "평점": 3.8, "입학년도": 2022},
        {"이름": "이영희", "나이": 21, "전공": "경영학과", "평점": 3.9, "입학년도": 2021},
        {"이름": "박민수", "나이": 19, "전공": "기계공학과", "평점": 3.6, "입학년도": 2023},
        {"이름": "최지영", "나이": 22, "전공": "화학과", "평점": 4.0, "입학년도": 2020},
        {"이름": "정수진", "나이": 20, "전공": "수학과", "평점": 3.7, "입학년도": 2022}
    ]
    
    csv_file = Path("korean_students.csv")
    
    # CSV 파일 쓰기
    try:
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            if korean_students:
                fieldnames = korean_students[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # 헤더 쓰기
                writer.writeheader()
                
                # 데이터 쓰기
                writer.writerows(korean_students)
        
        print(f"[O] CSV 파일 생성 완료: {csv_file}")
        
    except Exception as e:
        print(f"[X] CSV 파일 생성 실패: {e}")
        return
    
    # CSV 파일 읽기
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            print(f"\nCSV 파일 내용:")
            print(f"컬럼: {reader.fieldnames}")
            
            loaded_students = []
            for row_num, row in enumerate(reader, 1):
                print(f"  {row_num}: {dict(row)}")
                loaded_students.append(row)
        
        print(f"총 {len(loaded_students)}명의 학생 데이터 로드")
        
    except Exception as e:
        print(f"[X] CSV 파일 읽기 실패: {e}")
    
    # 데이터 분석
    try:
        # 전공별 통계
        major_stats = {}
        for student in loaded_students:
            major = student["전공"]
            if major not in major_stats:
                major_stats[major] = {"count": 0, "total_gpa": 0}
            
            major_stats[major]["count"] += 1
            major_stats[major]["total_gpa"] += float(student["평점"])
        
        print(f"\n전공별 통계:")
        for major, stats in major_stats.items():
            avg_gpa = stats["total_gpa"] / stats["count"]
            print(f"  {major}: {stats['count']}명, 평균 평점: {avg_gpa:.2f}")
        
    except Exception as e:
        print(f"[X] 데이터 분석 실패: {e}")
    
    # 정리
    if csv_file.exists():
        csv_file.unlink()

def advanced_csv_processing():
    """고급 CSV 처리 기법"""
    
    print("\n=== 고급 CSV 처리 ===")
    
    # 복잡한 한국 회사 데이터
    company_data = [
        {
            "회사명": "삼성전자",
            "업종": "전자제품",
            "설립일": "1969-01-13",
            "직원수": 267800,
            "매출액": 2796890,  # 억원
            "주소": "경기도 수원시 영통구 삼성로 129",
            "상장여부": True,
            "특이사항": "글로벌, 반도체 1위"
        },
        {
            "회사명": "LG전자", 
            "업종": "전자제품",
            "설립일": "1958-02-01",
            "직원수": 75000,
            "매출액": 748632,
            "주소": "서울특별시 영등포구 여의대로 128",
            "상장여부": True,
            "특이사항": "가전제품, 인공지능"
        }
    ]
    
    # 복잡한 데이터를 CSV로 저장
    complex_csv = Path("korean_companies.csv")
    
    try:
        with open(complex_csv, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["회사명", "업종", "설립일", "직원수", "매출액", "주소", "상장여부", "특이사항"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
            
            writer.writeheader()
            writer.writerows(company_data)
        
        print(f"[O] 복잡한 CSV 파일 생성: {complex_csv}")
        
    except Exception as e:
        print(f"[X] CSV 생성 실패: {e}")
        return
    
    # CSV 파일을 다양한 방식으로 읽기
    try:
        print(f"\n다양한 CSV 읽기 방식:")
        
        # 1. DictReader 사용
        with open(complex_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            print("1. DictReader로 읽기:")
            for row in reader:
                # 데이터 타입 변환
                company_info = {
                    "회사명": row["회사명"],
                    "업종": row["업종"],
                    "설립일": datetime.strptime(row["설립일"], "%Y-%m-%d").date(),
                    "직원수": int(row["직원수"]),
                    "매출액": int(row["매출액"]),
                    "상장여부": row["상장여부"].lower() == "true"
                }
                print(f"  {company_info}")
        
        # 2. 일반 reader 사용
        with open(complex_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)  # 첫 번째 행은 헤더
            
            print(f"\n2. 일반 reader로 읽기:")
            print(f"헤더: {headers}")
            
            for row_num, row in enumerate(reader, 1):
                print(f"  행 {row_num}: {row}")
        
    except Exception as e:
        print(f"[X] CSV 읽기 실패: {e}")
    
    # 정리
    if complex_csv.exists():
        complex_csv.unlink()

def json_file_processing():
    """JSON 파일 처리"""
    
    print("\n=== JSON 파일 처리 ===")
    
    # 복잡한 한국 도시 데이터
    korean_cities_data = {
        "metadata": {
            "title": "한국 주요 도시 정보",
            "created": datetime.now().isoformat(),
            "version": "1.0",
            "source": "통계청"
        },
        "cities": [
            {
                "name": "서울특별시",
                "english_name": "Seoul",
                "population": 9720846,
                "area_km2": 605.21,
                "districts": ["강남구", "강동구", "강북구", "강서구", "관악구"],
                "coordinates": {"latitude": 37.5665, "longitude": 126.9780},
                "established": "1394-07-01",
                "is_capital": True,
                "famous_for": ["한강", "경복궁", "남산타워", "홍대", "강남"]
            },
            {
                "name": "부산광역시",
                "english_name": "Busan", 
                "population": 3448737,
                "area_km2": 770.06,
                "districts": ["해운대구", "부산진구", "동래구", "남구", "중구"],
                "coordinates": {"latitude": 35.1796, "longitude": 129.0756},
                "established": "1963-01-01",
                "is_capital": False,
                "famous_for": ["해운대해수욕장", "자갈치시장", "태종대", "광안대교"]
            }
        ],
        "statistics": {
            "total_cities": 2,
            "total_population": 13169583,
            "average_area": 687.635
        }
    }
    
    json_file = Path("korean_cities.json")
    
    # JSON 파일 쓰기
    try:
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(korean_cities_data, f, 
                     ensure_ascii=False,  # 한글 그대로 저장
                     indent=2,           # 예쁘게 포맷팅
                     separators=(',', ': '))  # 구분자 설정
        
        print(f"[O] JSON 파일 생성 완료: {json_file}")
        
    except Exception as e:
        print(f"[X] JSON 파일 생성 실패: {e}")
        return
    
    # JSON 파일 읽기
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        
        print(f"\nJSON 파일 내용:")
        print(f"제목: {loaded_data['metadata']['title']}")
        print(f"버전: {loaded_data['metadata']['version']}")
        print(f"도시 수: {loaded_data['statistics']['total_cities']}")
        
        # 도시별 정보 출력
        for city in loaded_data["cities"]:
            print(f"\n{city['name']} ({city['english_name']})")
            print(f"  인구: {city['population']:,}명")
            print(f"  면적: {city['area_km2']} km²")
            print(f"  인구밀도: {city['population']/city['area_km2']:,.1f}명/km²")
            print(f"  주요 관광지: {', '.join(city['famous_for'])}")
            print(f"  좌표: ({city['coordinates']['latitude']}, {city['coordinates']['longitude']})")
        
    except Exception as e:
        print(f"[X] JSON 파일 읽기 실패: {e}")
    
    # JSON 데이터 조작 및 저장
    try:
        # 새로운 도시 추가
        new_city = {
            "name": "대구광역시",
            "english_name": "Daegu",
            "population": 2438031,
            "area_km2": 883.56,
            "districts": ["중구", "동구", "서구", "남구", "북구"],
            "coordinates": {"latitude": 35.8714, "longitude": 128.6014},
            "established": "1949-08-15",
            "is_capital": False,
            "famous_for": ["83타워", "서문시장", "동화사", "수성못"]
        }
        
        loaded_data["cities"].append(new_city)
        loaded_data["statistics"]["total_cities"] = len(loaded_data["cities"])
        loaded_data["statistics"]["total_population"] += new_city["population"]
        
        # 수정된 데이터 저장
        updated_file = Path("korean_cities_updated.json")
        with open(updated_file, "w", encoding="utf-8") as f:
            json.dump(loaded_data, f, ensure_ascii=False, indent=2)
        
        print(f"[O] 업데이트된 JSON 파일 저장: {updated_file}")
        
        # JSON Lines 형식으로도 저장 (스트리밍에 유용)
        jsonl_file = Path("korean_cities.jsonl")
        with open(jsonl_file, "w", encoding="utf-8") as f:
            for city in loaded_data["cities"]:
                json.dump(city, f, ensure_ascii=False)
                f.write('\n')
        
        print(f"[O] JSON Lines 파일 저장: {jsonl_file}")
        
    except Exception as e:
        print(f"[X] JSON 데이터 조작 실패: {e}")
    
    # 정리
    for file in [json_file, Path("korean_cities_updated.json"), Path("korean_cities.jsonl")]:
        if file.exists():
            file.unlink()

# 실행
korean_csv_processing()
advanced_csv_processing()
json_file_processing()

# ---- 원고 1518줄 ----
import pickle
from pathlib import Path

scores = {"김철수": 85, "이영희": 92}
names = ["김철수", "이영희"]
round_no = 3

# 여러 변수를 딕셔너리 하나로 묶어서 한 번에 저장
with open("work.pkl", "wb") as f:
    pickle.dump({"scores": scores, "names": names, "round_no": round_no}, f)

with open("work.pkl", "rb") as f:
    saved = pickle.load(f)

print(saved["scores"], saved["names"], saved["round_no"])
# {'김철수': 85, '이영희': 92} ['김철수', '이영희'] 3
Path("work.pkl").unlink()
