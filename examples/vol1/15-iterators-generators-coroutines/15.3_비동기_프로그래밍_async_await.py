"""1권 Chapter 15. 반복자, 제너레이터, 코루틴 — 15.3 비동기 프로그래밍 (async/await)

원고: manuscript/chapters/15-iterators-generators-coroutines.md (583줄부터)
"""

# ---- 원고 583줄 ----
import time
import asyncio
from typing import List

# 동기 방식 - 한 번에 하나씩 처리
def 동기_뉴스_수집(url_목록: List[str]) -> List[str]:
    """여러 뉴스 사이트를 동기적으로 수집"""
    결과 = []
    시작_시간 = time.time()
    
    for i, url in enumerate(url_목록):
        print(f"  동기 처리: {i+1}번째 사이트 접속 중...")
        try:
            # 실제로는 HTTP 요청, 여기서는 시뮬레이션
            time.sleep(1)  # 네트워크 지연 시뮬레이션
            결과.append(f"뉴스 데이터_{i+1}")
        except Exception as e:
            결과.append(f"오류_{i+1}: {e}")
    
    소요_시간 = time.time() - 시작_시간
    print(f"  동기 처리 완료: {소요_시간:.2f}초")
    return 결과

# 비동기 방식 - 동시에 여러 개 처리
async def 비동기_뉴스_수집(url_목록: List[str]) -> List[str]:
    """여러 뉴스 사이트를 비동기적으로 수집"""
    
    async def 단일_사이트_수집(index: int) -> str:
        print(f"  비동기 처리: {index+1}번째 사이트 접속 시작...")
        await asyncio.sleep(1)  # 네트워크 지연 시뮬레이션
        print(f"  비동기 처리: {index+1}번째 사이트 완료!")
        return f"뉴스 데이터_{index+1}"
    
    시작_시간 = time.time()
    
    # 모든 사이트를 동시에 처리
    작업_목록 = [단일_사이트_수집(i) for i in range(len(url_목록))]
    결과 = await asyncio.gather(*작업_목록)
    
    소요_시간 = time.time() - 시작_시간
    print(f"  비동기 처리 완료: {소요_시간:.2f}초")
    return 결과

# 성능 비교
if __name__ == "__main__":
    가짜_url_목록 = ['site1.com', 'site2.com', 'site3.com', 'site4.com']
    
    print("성능 비교 테스트:")
    print("\n1. 동기 방식 (순차 처리):")
    동기_결과 = 동기_뉴스_수집(가짜_url_목록)
    
    print("\n2. 비동기 방식 (동시 처리):")
    비동기_결과 = asyncio.run(비동기_뉴스_수집(가짜_url_목록))
    
    print(f"\n결과 비교:")
    print(f"  동기 결과: {동기_결과}")
    print(f"  비동기 결과: {비동기_결과}")

# ---- 원고 673줄 ----
import asyncio
from typing import AsyncGenerator

# 기본 비동기 함수
async def 한국어_인사(이름: str, 지연_시간: float = 1.0) -> str:
    """비동기적으로 한국어 인사를 생성"""
    print(f"  {이름}님에게 인사 준비 중...")
    await asyncio.sleep(지연_시간)  # 비동기 대기
    return f"안녕하세요, {이름}님!"

# 여러 사람에게 동시에 인사
async def 다중_인사():
    """여러 사람에게 동시에 인사하기"""
    사람들 = ['김철수', '이영희', '박민수', '정지영']
    
    # 모든 인사를 동시에 시작
    인사_작업들 = [한국어_인사(사람, 지연_시간=1.0) for 사람 in 사람들]
    
    # 모든 작업이 완료될 때까지 대기
    인사_결과들 = await asyncio.gather(*인사_작업들)
    
    for 인사 in 인사_결과들:
        print(f"  완료: {인사}")

# 실행
print("비동기 인사 시스템:")
asyncio.run(다중_인사())

# ---- 원고 709줄 ----
import asyncio
import time


async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)


async def 순서대로():
    await say_after(1, 'hello')
    await say_after(2, 'world')


async def 태스크로():
    task1 = asyncio.create_task(say_after(1, 'hello'))
    task2 = asyncio.create_task(say_after(2, 'world'))
    await task1
    await task2


for main in (순서대로, 태스크로):
    시작 = time.perf_counter()
    asyncio.run(main())
    print(f"{main.__name__}: {time.perf_counter() - 시작:.2f}초")

# ---- 원고 759줄 ----
import asyncio
import time


async def 잘못된_대기():
    time.sleep(1)  # 이벤트 루프 전체를 멈춤


async def 올바른_대기():
    await asyncio.sleep(1)  # 기다리는 동안 다른 코루틴에 양보


async def main():
    for 작업 in (잘못된_대기, 올바른_대기):
        시작 = time.perf_counter()
        await asyncio.gather(*(작업() for _ in range(3)))
        print(f"{작업.__name__}: {time.perf_counter() - 시작:.2f}초")

asyncio.run(main())

# ---- 원고 793줄 ----
import asyncio

잔액 = 0


async def 입금(금액):
    global 잔액
    현재 = 잔액                # 1. 잔액을 읽고
    await asyncio.sleep(0)     # 2. 잠깐 다른 코루틴에 양보한 뒤
    잔액 = 현재 + 금액         # 3. 읽어 둔 값에 더해 저장


async def main():
    await asyncio.gather(*(입금(1) for _ in range(100)))
    print(f"100번 입금한 뒤 잔액: {잔액}")

asyncio.run(main())

# ---- 원고 823줄 ----
import asyncio
import random
from datetime import datetime
from typing import AsyncGenerator, Dict, Any

async def 실시간_주가_스트림(
    종목코드: str,
    업데이트_간격: float = 1.0
) -> AsyncGenerator[Dict[str, Any], None]:
    """한국 주식의 실시간 가격 스트림을 시뮬레이션"""
    
    # 한국 주요 종목 정보
    종목_정보 = {
        '005930': {'회사명': '삼성전자', '현재가': 75000},
        '000660': {'회사명': 'SK하이닉스', '현재가': 130000},
        '035420': {'회사명': 'NAVER', '현재가': 350000}
    }
    
    if 종목코드 not in 종목_정보:
        raise ValueError(f"지원하지 않는 종목코드: {종목코드}")
    
    회사_정보 = 종목_정보[종목코드]
    현재가 = 회사_정보['현재가']
    
    while True:
        # 가격 변동 시뮬레이션 (-2% ~ +2%)
        변동율 = random.uniform(-0.02, 0.02)
        현재가 = int(현재가 * (1 + 변동율))
        
        주가_정보 = {
            '시간': datetime.now().strftime('%H:%M:%S'),
            '종목코드': 종목코드,
            '회사명': 회사_정보['회사명'],
            '현재가': 현재가,
            '변동율': round(변동율 * 100, 2),
            '거래량': random.randint(1000, 10000)
        }
        
        yield 주가_정보
        await asyncio.sleep(업데이트_간격)

async def 주가_모니터링():
    """실시간 주가 모니터링 시스템"""
    print("실시간 주가 모니터링 시작:")
    
    # 삼성전자 실시간 주가 스트림
    삼성전자_스트림 = 실시간_주가_스트림('005930', 1.5)
    
    # 첫 10개 업데이트만 모니터링
    count = 0
    async for 주가_정보 in 삼성전자_스트림:
        print(f"  [{주가_정보['시간']}] {주가_정보['회사명']}: "
              f"{주가_정보['현재가']:,}원 ({주가_정보['변동율']:+.1f}%)")
        
        count += 1
        if count >= 10:
            break

# 실행
print("\n비동기 제너레이터 활용:")
asyncio.run(주가_모니터링())

# ---- 원고 893줄 ----
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class 비동기_데이터베이스:
    """비동기 데이터베이스 시뮬레이션"""
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.is_connected = False
    
    async def 연결(self):
        """데이터베이스 연결"""
        print(f"  {self.db_name} 데이터베이스 연결 중...")
        await asyncio.sleep(0.5)  # 연결 지연 시뮬레이션
        self.is_connected = True
        print(f"  {self.db_name} 데이터베이스 연결 완료!")
    
    async def 연결_해제(self):
        """데이터베이스 연결 해제"""
        print(f"  {self.db_name} 데이터베이스 연결 해제 중...")
        await asyncio.sleep(0.2)
        self.is_connected = False
        print(f"  {self.db_name} 데이터베이스 연결 해제 완료!")
    
    async def 쿼리_실행(self, query: str) -> str:
        """쿼리 실행"""
        if not self.is_connected:
            raise RuntimeError("데이터베이스가 연결되지 않았습니다")
        
        print(f"  쿼리 실행: {query}")
        await asyncio.sleep(0.3)  # 쿼리 실행 지연
        return f"쿼리 결과: {query}의 결과 데이터"
    
    # 비동기 컨텍스트 매니저로 사용하기 위한 메서드
    async def __aenter__(self):
        await self.연결()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"  오류 발생으로 롤백: {exc_val}")
        await self.연결_해제()

@asynccontextmanager
async def 데이터베이스_트랜잭션(db: 비동기_데이터베이스) -> AsyncGenerator[비동기_데이터베이스, None]:
    """데이터베이스 트랜잭션 컨텍스트 매니저"""
    print("  트랜잭션 시작")
    try:
        yield db
        print("  트랜잭션 커밋")
    except Exception as e:
        print(f"  트랜잭션 롤백: {e}")
        raise

async def 데이터베이스_작업_예제():
    """비동기 컨텍스트 매니저 사용 예제"""
    
    # async with를 사용한 리소스 관리
    async with 비동기_데이터베이스("한국_고객_DB") as db:
        
        # 중첩 컨텍스트 매니저로 트랜잭션 관리
        async with 데이터베이스_트랜잭션(db):
            결과1 = await db.쿼리_실행("SELECT * FROM 고객")
            print(f"    {결과1}")
            
            결과2 = await db.쿼리_실행("INSERT INTO 고객 VALUES ('김철수')")
            print(f"    {결과2}")

print("\n비동기 컨텍스트 매니저:")
asyncio.run(데이터베이스_작업_예제())

# ---- 원고 988줄 ----
import asyncio
import json
from typing import AsyncIterator, Dict, Any

class 한국_뉴스_수집기:
    """한국 뉴스를 비동기적으로 수집하는 반복자"""
    
    def __init__(self, 카테고리_목록: list, 각_카테고리_뉴스_수: int = 3):
        self.카테고리_목록 = 카테고리_목록
        self.각_카테고리_뉴스_수 = 각_카테고리_뉴스_수
        self.현재_카테고리_인덱스 = 0
        self.현재_뉴스_인덱스 = 0
    
    def __aiter__(self) -> AsyncIterator[Dict[str, Any]]:
        return self
    
    async def __anext__(self) -> Dict[str, Any]:
        if self.현재_카테고리_인덱스 >= len(self.카테고리_목록):
            raise StopAsyncIteration
        
        현재_카테고리 = self.카테고리_목록[self.현재_카테고리_인덱스]
        
        # 뉴스 수집 시뮬레이션 (비동기 처리)
        print(f"  {현재_카테고리} 뉴스 #{self.현재_뉴스_인덱스 + 1} 수집 중...")
        await asyncio.sleep(0.5)  # 네트워크 지연 시뮬레이션
        
        뉴스_데이터 = {
            '카테고리': 현재_카테고리,
            '제목': f'{현재_카테고리} 뉴스 #{self.현재_뉴스_인덱스 + 1}',
            '내용': f'{현재_카테고리}에 관한 중요한 뉴스입니다.',
            '수집_시간': asyncio.get_event_loop().time()
        }
        
        # 다음 뉴스로 이동
        self.현재_뉴스_인덱스 += 1
        
        # 현재 카테고리의 모든 뉴스를 수집했으면 다음 카테고리로
        if self.현재_뉴스_인덱스 >= self.각_카테고리_뉴스_수:
            self.현재_카테고리_인덱스 += 1
            self.현재_뉴스_인덱스 = 0
        
        return 뉴스_데이터

async def 뉴스_수집_예제():
    """비동기 반복자 사용 예제"""
    print("한국 뉴스 비동기 수집:")
    
    뉴스_카테고리 = ['정치', '경제', '사회', '스포츠']
    뉴스_수집기 = 한국_뉴스_수집기(뉴스_카테고리, 2)
    
    수집된_뉴스 = []
    async for 뉴스 in 뉴스_수집기:
        print(f"    수집 완료: [{뉴스['카테고리']}] {뉴스['제목']}")
        수집된_뉴스.append(뉴스)
    
    print(f"\n총 {len(수집된_뉴스)}개의 뉴스를 수집했습니다.")

print("\n비동기 반복자:")
asyncio.run(뉴스_수집_예제())
