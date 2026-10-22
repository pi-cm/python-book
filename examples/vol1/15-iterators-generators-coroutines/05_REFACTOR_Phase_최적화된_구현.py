"""1권 Chapter 15. 반복자, 제너레이터, 코루틴 — REFACTOR Phase: 최적화된 구현

원고: manuscript/chapters/15-iterators-generators-coroutines.md (1385줄부터)
"""

# ---- 원고 1385줄 ----
import asyncio
from typing import AsyncIterator, TypeVar, Callable, Any
import mmap
import os

T = TypeVar('T')

class 메모리_맵_파일_리더:
    """메모리 맵을 사용한 효율적인 대용량 파일 처리"""
    
    def __init__(self, 파일_경로: str):
        self.파일_경로 = 파일_경로
        self.파일_객체 = None
        self.메모리_맵 = None
    
    def __enter__(self):
        self.파일_객체 = open(self.파일_경로, 'rb')
        self.메모리_맵 = mmap.mmap(self.파일_객체.fileno(), 0, access=mmap.ACCESS_READ)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.메모리_맵:
            self.메모리_맵.close()
        if self.파일_객체:
            self.파일_객체.close()
    
    def 라인_제너레이터(self):
        """메모리 효율적인 라인별 읽기"""
        현재_위치 = 0
        
        while 현재_위치 < len(self.메모리_맵):
            라인_끝 = self.메모리_맵.find(b'\n', 현재_위치)
            if 라인_끝 == -1:
                라인_끝 = len(self.메모리_맵)
            
            라인_데이터 = self.메모리_맵[현재_위치:라인_끝]
            현재_위치 = 라인_끝 + 1
            
            try:
                yield 라인_데이터.decode('utf-8').strip()
            except UnicodeDecodeError:
                continue  # 인코딩 오류 라인 건너뛰기

async def 비동기_스트림_처리(
    데이터_스트림: AsyncIterator[T],
    처리_함수: Callable[[T], Any],
    배치_크기: int = 1000,
    동시_처리_수: int = 10
) -> AsyncIterator[Any]:
    """고성능 비동기 스트림 처리 시스템"""
    
    배치 = []
    
    async for 데이터 in 데이터_스트림:
        배치.append(데이터)
        
        if len(배치) >= 배치_크기:
            # 배치를 동시 처리
            처리_작업들 = [
                asyncio.create_task(asyncio.to_thread(처리_함수, 항목))
                for 항목 in 배치[:동시_처리_수]
            ]
            
            완료된_작업들 = await asyncio.gather(*처리_작업들, return_exceptions=True)
            
            for 결과 in 완료된_작업들:
                if not isinstance(결과, Exception):
                    yield 결과
            
            배치 = 배치[동시_처리_수:]
    
    # 남은 배치 처리
    if 배치:
        남은_작업들 = [
            asyncio.create_task(asyncio.to_thread(처리_함수, 항목))
            for 항목 in 배치
        ]
        
        완료된_남은_작업들 = await asyncio.gather(*남은_작업들, return_exceptions=True)
        
        for 결과 in 완료된_남은_작업들:
            if not isinstance(결과, Exception):
                yield 결과

# 사용 예제
async def 고성능_데이터_처리_데모():
    """고성능 데이터 처리 시스템 데모"""
    
    def 한국어_텍스트_처리(텍스트: str) -> dict:
        """한국어 텍스트 분석 (시뮬레이션)"""
        import time
        time.sleep(0.01)  # 처리 시간 시뮬레이션
        
        return {
            '원본': 텍스트,
            '길이': len(텍스트),
            '단어수': len(텍스트.split()),
            '한글포함': any('가' <= char <= '힣' for char in 텍스트)
        }
    
    # 가상의 텍스트 스트림
    async def 텍스트_스트림():
        텍스트_샘플 = [
            "안녕하세요 파이썬!",
            "대한민국의 아름다운 한글",
            "제너레이터와 코루틴 학습",
            "비동기 프로그래밍 마스터하기",
            "실시간 데이터 처리 시스템"
        ] * 100  # 500개 텍스트
        
        for 텍스트 in 텍스트_샘플:
            yield 텍스트
            await asyncio.sleep(0.001)  # 스트림 시뮬레이션
    
    print("고성능 비동기 스트림 처리 시작:")
    시작_시간 = asyncio.get_event_loop().time()
    
    처리_결과_수 = 0
    async for 처리_결과 in 비동기_스트림_처리(
        텍스트_스트림(),
        한국어_텍스트_처리,
        배치_크기=50,
        동시_처리_수=10
    ):
        처리_결과_수 += 1
        if 처리_결과_수 <= 5:  # 처음 5개만 출력
            print(f"  처리 결과: {처리_결과}")
    
    소요_시간 = asyncio.get_event_loop().time() - 시작_시간
    print(f"\n총 {처리_결과_수}개 항목을 {소요_시간:.2f}초에 처리 완료")
    print(f"처리 속도: {처리_결과_수/소요_시간:.1f} 항목/초")

# 실행
print("\n고성능 최적화 버전:")
asyncio.run(고성능_데이터_처리_데모())
