"""1권 Chapter 5. 반복문과 루프 — 5.5 중첩 루프 최적화와 성능 향상

원고: manuscript/chapters/05-loops.md (891줄부터)
"""

# ---- 원고 891줄 ----
import time
from typing import List, Tuple

# 1. 비효율적 vs 효율적 중첩 루프
def 비효율적_중복_찾기(리스트1: List[int], 리스트2: List[int]) -> List[Tuple[int, int]]:
    """비효율적인 중복 찾기 O(n*m)"""
    중복들 = []
    for i, 값1 in enumerate(리스트1):
        for j, 값2 in enumerate(리스트2):
            if 값1 == 값2:
                중복들.append((i, j))
    return 중복들

def 효율적_중복_찾기(리스트1: List[int], 리스트2: List[int]) -> List[Tuple[int, int]]:
    """효율적인 중복 찾기 O(n+m)"""
    # 두 번째 리스트를 딕셔너리로 변환 (O(m))
    값_to_인덱스들 = {}
    for j, 값 in enumerate(리스트2):
        if 값 not in 값_to_인덱스들:
            값_to_인덱스들[값] = []
        값_to_인덱스들[값].append(j)
    
    # 첫 번째 리스트를 순회하며 찾기 (O(n))
    중복들 = []
    for i, 값 in enumerate(리스트1):
        if 값 in 값_to_인덱스들:
            for j in 값_to_인덱스들[값]:
                중복들.append((i, j))
    
    return 중복들

# 성능 비교
큰_리스트1 = list(range(0, 1000, 2))  # 짝수
큰_리스트2 = list(range(0, 1000, 3))  # 3의 배수

print("=== 중첩 루프 최적화 성능 비교 ===")

# 비효율적 방법
시작 = time.time()
결과1 = 비효율적_중복_찾기(큰_리스트1[:100], 큰_리스트2[:100])
시간1 = time.time() - 시작

# 효율적 방법  
시작 = time.time()
결과2 = 효율적_중복_찾기(큰_리스트1[:100], 큰_리스트2[:100])
시간2 = time.time() - 시작

print(f"비효율적 방법: {시간1:.4f}초, 결과 수: {len(결과1)}")
print(f"효율적 방법: {시간2:.4f}초, 결과 수: {len(결과2)}")
print(f"성능 개선: {시간1/시간2:.2f}배 빠름" if 시간2 > 0 else "측정 불가")

# 2. 조기 종료 최적화
def 매트릭스_특정값_찾기_기본(매트릭스: List[List[int]], 타겟: int) -> Tuple[int, int]:
    """기본적인 2차원 배열 검색"""
    for i in range(len(매트릭스)):
        for j in range(len(매트릭스[i])):
            if 매트릭스[i][j] == 타겟:
                return (i, j)
    return (-1, -1)

def 매트릭스_특정값_찾기_최적화(매트릭스: List[List[int]], 타겟: int) -> Tuple[int, int]:
    """최적화된 2차원 배열 검색 (조기 종료)"""
    for i, 행 in enumerate(매트릭스):
        for j, 값 in enumerate(행):
            if 값 == 타겟:
                return (i, j)
            # 정렬된 배열이라면 추가 최적화 가능
            # if 값 > 타겟:
            #     break
    return (-1, -1)

# 3. 루프 언롤링 (Loop Unrolling)
def 기본_합계_계산(숫자들: List[int]) -> int:
    """기본적인 합계 계산"""
    합계 = 0
    for 숫자 in 숫자들:
        합계 += 숫자
    return 합계

def 언롤링_합계_계산(숫자들: List[int]) -> int:
    """루프 언롤링을 적용한 합계 계산"""
    합계 = 0
    i = 0
    
    # 4개씩 묶어서 처리
    while i + 3 < len(숫자들):
        합계 += 숫자들[i] + 숫자들[i+1] + 숫자들[i+2] + 숫자들[i+3]
        i += 4
    
    # 나머지 처리
    while i < len(숫자들):
        합계 += 숫자들[i]
        i += 1
    
    return 합계

# 테스트
테스트_숫자들 = list(range(1, 10001))

시작 = time.time()
결과1 = 기본_합계_계산(테스트_숫자들)
시간1 = time.time() - 시작

시작 = time.time()
결과2 = 언롤링_합계_계산(테스트_숫자들)
시간2 = time.time() - 시작

print(f"\n=== 루프 언롤링 비교 ===")
print(f"기본 방법: {결과1}, 시간: {시간1:.6f}초")
print(f"언롤링 방법: {결과2}, 시간: {시간2:.6f}초")

# ---- 원고 1018줄 ----
# 1. 큰 데이터셋 처리 - 청크 단위 처리
def 청크_단위_처리(데이터, 청크_크기=1000):
    """큰 데이터를 청크 단위로 처리"""
    처리된_개수 = 0
    
    for i in range(0, len(데이터), 청크_크기):
        청크 = 데이터[i:i + 청크_크기]
        
        # 청크 처리 (예: 각 값에 2를 곱함)
        처리된_청크 = [값 * 2 for 값 in 청크]
        처리된_개수 += len(처리된_청크)
        
        print(f"청크 {i//청크_크기 + 1} 처리 완료: {len(처리된_청크)}개 항목")
        
        # 실제로는 여기서 결과를 파일에 저장하거나 다른 처리를 함
        # yield 처리된_청크  # 제너레이터로 만들 수도 있음
    
    return 처리된_개수

# 큰 데이터셋 시뮬레이션
큰_데이터 = list(range(5000))
처리_결과 = 청크_단위_처리(큰_데이터, 청크_크기=1000)
print(f"총 {처리_결과}개 항목 처리 완료")

# 2. 메모리 효율적인 파일 처리
def 메모리_효율적_파일_처리():
    """대용량 파일을 메모리 효율적으로 처리"""
    # 실제 파일 대신 시뮬레이션 데이터
    가짜_파일_라인들 = [f"라인 {i}: 중요한 데이터 {i*10}" for i in range(1000)]
    
    중요한_라인_수 = 0
    
    # 한 번에 하나씩 처리 (메모리 사용량 최소화)
    for 라인번호, 라인 in enumerate(가짜_파일_라인들, 1):
        if "중요한" in 라인:
            중요한_라인_수 += 1
            
            # 진행상황 표시 (100개마다)
            if 라인번호 % 100 == 0:
                print(f"진행상황: {라인번호}줄 처리, 중요한 라인 {중요한_라인_수}개 발견")
    
    return 중요한_라인_수

print(f"\n=== 메모리 효율적 파일 처리 ===")
중요한_라인들 = 메모리_효율적_파일_처리()
print(f"총 중요한 라인: {중요한_라인들}개")

# 3. 캐싱을 활용한 최적화
class 피보나치_캐시:
    def __init__(self):
        self.캐시 = {0: 0, 1: 1}
    
    def 계산(self, n):
        if n in self.캐시:
            return self.캐시[n]
        
        # 이전 값들을 순차적으로 계산 (재귀 대신 루프 사용)
        for i in range(len(self.캐시), n + 1):
            self.캐시[i] = self.캐시[i-1] + self.캐시[i-2]
        
        return self.캐시[n]

print(f"\n=== 캐싱 활용 최적화 ===")
피보나치 = 피보나치_캐시()

for i in [10, 20, 30, 25]:  # 25는 이미 캐시된 값 활용
    결과 = 피보나치.계산(i)
    print(f"피보나치({i}) = {결과}")

print(f"캐시 크기: {len(피보나치.캐시)}개 값 저장됨")
