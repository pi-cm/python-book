# [1권 Chapter 14: 모듈과 패키지 · 14.9 파이썬 내장 모듈 활용 · manuscript/chapters/14-modules-packages.md:1485]
# builtin_modules_demo.py
"""자주 사용하는 파이썬 내장 모듈들"""

import os
import sys
import json
import datetime
import random
import pathlib
import collections
from typing import Dict, List, Any

print("=== 파이썬 내장 모듈 활용 예제 ===")

# 1. os 모듈 - 운영체제 관련 기능
print("\n1. os 모듈:")
print(f"  현재 OS: {os.name}")
print(f"  환경변수 PATH 일부: {os.environ.get('PATH', '')[:50]}...")
print(f"  임시 디렉토리: {os.path.join(os.getcwd(), 'temp')}")

# 2. sys 모듈 - 파이썬 인터프리터 관련
print("\n2. sys 모듈:")
print(f"  파이썬 버전: {sys.version_info}")
print(f"  플랫폼: {sys.platform}")
print(f"  모듈 검색 경로 수: {len(sys.path)}")

# 3. datetime 모듈 - 날짜와 시간
print("\n3. datetime 모듈:")
now = datetime.datetime.now()
print(f"  현재 시간: {now.strftime('%Y년 %m월 %d일 %H시 %M분')}")
print(f"  한 주 후: {(now + datetime.timedelta(weeks=1)).strftime('%Y-%m-%d')}")

# 4. json 모듈 - JSON 처리
print("\n4. json 모듈:")
sample_data = {
    "맛집명": "김수한무 한정식",
    "평점": 4.5,
    "리뷰수": 128,
    "메뉴": ["불고기", "갈비찜", "된장찌개"]
}
json_str = json.dumps(sample_data, ensure_ascii=False, indent=2)
print(f"  JSON 변환:\n{json_str}")

# 5. random 모듈 - 난수 생성
print("\n5. random 모듈:")
korean_foods = ["김치찌개", "불고기", "비빔밥", "냉면", "삼겹살"]
print(f"  오늘의 추천 메뉴: {random.choice(korean_foods)}")
print(f"  평점 시뮬레이션: {random.uniform(3.5, 5.0):.1f}점")

# 6. collections 모듈 - 특수 컨테이너
print("\n6. collections 모듈:")
review_counts = collections.Counter(["긍정", "긍정", "부정", "긍정", "중립", "긍정"])
print(f"  리뷰 분석: {dict(review_counts)}")

# defaultdict 사용 예제
district_restaurants = collections.defaultdict(list)
district_restaurants["강남구"].append("김수한무 한정식")
district_restaurants["종로구"].append("홍길동 짜장면")
print(f"  지역별 맛집: {dict(district_restaurants)}")
