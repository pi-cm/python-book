"""1권 Chapter 15. 반복자, 제너레이터, 코루틴 — 15.1 반복자 프로토콜

원고: manuscript/chapters/15-iterators-generators-coroutines.md (37줄부터)
"""

# ---- 원고 37줄 ----
# 기본적인 for 문
한국_도시 = ['서울', '부산', '인천', '대구', '대전']

# 이것이 실제로는 어떻게 동작하는지 보기
도시_반복자 = iter(한국_도시)
print(f"반복자 객체: {도시_반복자}")
print(f"첫 번째 도시: {next(도시_반복자)}")
print(f"두 번째 도시: {next(도시_반복자)}")

# ---- 원고 61줄 ----
from collections.abc import Iterable, Iterator

한국_도시 = ['서울', '부산', '인천', '대구', '대전']
도시_반복자 = iter(한국_도시)

print(f"리스트는 반복 가능? {isinstance(한국_도시, Iterable)}")        # True
print(f"리스트는 반복자? {isinstance(한국_도시, Iterator)}")           # False
print(f"반복자는 반복 가능? {isinstance(도시_반복자, Iterable)}")       # True
print(f"반복자는 반복자? {isinstance(도시_반복자, Iterator)}")         # True

# ---- 원고 83줄 ----
class 한국어_카운터:
    """한국어로 카운트하는 반복자"""
    
    def __init__(self, 시작: int = 1, 끝: int = 10):
        self.시작 = 시작
        self.끝 = 끝
        self.현재 = 시작 - 1
        
        # 한국어 숫자 표현
        self.한국어_숫자 = {
            1: '하나', 2: '둘', 3: '셋', 4: '넷', 5: '다섯',
            6: '여섯', 7: '일곱', 8: '여덟', 9: '아홉', 10: '열'
        }
    
    def __iter__(self):
        """반복자 객체 자신을 반환"""
        return self
    
    def __next__(self):
        """다음 값 반환"""
        self.현재 += 1
        if self.현재 > self.끝:
            raise StopIteration
        
        한국어_표현 = self.한국어_숫자.get(self.현재, str(self.현재))
        return f"{한국어_표현}({self.현재})"

# 사용 예제
print("한국어 카운터 테스트:")
for 숫자 in 한국어_카운터(1, 5):
    print(f"  {숫자}")

# ---- 원고 133줄 ----
from typing import Dict, Tuple, Optional
import json

class 지역_날씨_반복자:
    """한국 지역별 날씨 데이터 반복자"""
    
    def __init__(self, 날씨_데이터: Dict[str, Dict]):
        self.날씨_데이터 = 날씨_데이터
        self.지역_목록 = list(날씨_데이터.keys())
        self.현재_인덱스 = 0
    
    def __iter__(self):
        return self
    
    def __next__(self) -> Tuple[str, str, int]:
        if self.현재_인덱스 >= len(self.지역_목록):
            raise StopIteration
        
        지역 = self.지역_목록[self.현재_인덱스]
        날씨_정보 = self.날씨_데이터[지역]
        
        self.현재_인덱스 += 1
        
        return (
            지역,
            날씨_정보['날씨'],
            날씨_정보['온도']
        )
    
    def 온도순_정렬(self):
        """온도 순으로 지역 목록 정렬"""
        self.지역_목록.sort(
            key=lambda 지역: self.날씨_데이터[지역]['온도'],
            reverse=True
        )
        self.현재_인덱스 = 0
        return self

# 샘플 데이터
한국_날씨_데이터 = {
    '서울': {'날씨': '맑음', '온도': 25},
    '부산': {'날씨': '흐림', '온도': 28},
    '인천': {'날씨': '비', '온도': 22},
    '대구': {'날씨': '맑음', '온도': 30},
    '광주': {'날씨': '흐림', '온도': 26}
}

print("지역별 날씨 정보:")
날씨_반복자 = 지역_날씨_반복자(한국_날씨_데이터)
for 지역, 날씨, 온도 in 날씨_반복자:
    print(f"  {지역}: {날씨}, {온도}°C")

print("\n온도 높은 순으로 정렬:")
날씨_반복자_정렬 = 지역_날씨_반복자(한국_날씨_데이터).온도순_정렬()
for 지역, 날씨, 온도 in 날씨_반복자_정렬:
    print(f"  {지역}: {날씨}, {온도}°C")

# ---- 원고 198줄 ----
import random
import time

# 형태 1: 반복 가능한 객체로부터 반복자 생성
한국_도시 = ['서울', '부산', '인천', '대구', '대전']
도시_반복자 = iter(한국_도시)

# 형태 2: 함수와 센티널 값으로 반복자 생성
def 랜덤_온도():
    """-10도에서 40도 사이의 랜덤 온도 생성"""
    return random.randint(-10, 40)

print("센티널 값을 활용한 반복자:")
온도_반복자 = iter(랜덤_온도, 0)  # 0이 나올 때까지 계속 호출

for i, 온도 in enumerate(온도_반복자):
    if i >= 5:  # 최대 5개만 출력
        break
    print(f"  현재 온도: {온도}°C")

# 파일 읽기에 활용
def 한국어_라인_읽기():
    """파일에서 한 줄씩 읽기 (빈 줄이 나오면 종료)"""
    sample_data = ['첫 번째 줄', '두 번째 줄', '세 번째 줄', '', '마지막 줄']
    index = 0
    
    def get_line():
        nonlocal index
        if index >= len(sample_data):
            return ''
        line = sample_data[index]
        index += 1
        return line
    
    return iter(get_line, '')  # 빈 문자열까지 읽기

print("\n파일 라인 읽기:")
for 라인 in 한국어_라인_읽기():
    print(f"  읽은 라인: '{라인}'")
