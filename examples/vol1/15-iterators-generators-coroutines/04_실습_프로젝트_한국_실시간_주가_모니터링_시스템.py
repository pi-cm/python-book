"""1권 Chapter 15. 반복자, 제너레이터, 코루틴 — 실습 프로젝트: 한국 실시간 주가 모니터링 시스템

원고: manuscript/chapters/15-iterators-generators-coroutines.md (1064줄부터)
"""

# ---- 원고 1064줄 ----
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, AsyncGenerator, Optional, Any
from pathlib import Path

class 한국_주식_시뮬레이터:
    """한국 주식 시장 시뮬레이터"""
    
    def __init__(self):
        self.종목_정보 = {
            '005930': {'회사명': '삼성전자', '현재가': 75000, '전일종가': 74500},
            '000660': {'회사명': 'SK하이닉스', '현재가': 130000, '전일종가': 128900},
            '035420': {'회사명': 'NAVER', '현재가': 350000, '전일종가': 355000},
            '051910': {'회사명': 'LG화학', '현재가': 800000, '전일종가': 795000},
            '006400': {'회사명': '삼성SDI', '현재가': 650000, '전일종가': 645000}
        }
        
        self.시장_개장 = True
    
    def 시장_상태_확인(self) -> bool:
        """주식 시장 개장 시간 확인 (9:00~15:30)"""
        현재_시간 = datetime.now()
        시간 = 현재_시간.hour
        분 = 현재_시간.minute
        
        # 주말이면 폐장
        if 현재_시간.weekday() >= 5:
            return False
        
        # 평일 9:00~15:30만 개장
        if 시간 < 9 or (시간 == 15 and 분 > 30) or 시간 > 15:
            return False
        
        return True
    
    def 주가_변동_생성(self, 종목코드: str) -> Dict[str, Any]:
        """실시간 주가 변동 데이터 생성"""
        if 종목코드 not in self.종목_정보:
            raise ValueError(f"존재하지 않는 종목코드: {종목코드}")
        
        종목 = self.종목_정보[종목코드]
        
        # 시장 상황에 따른 변동성 조정
        기본_변동성 = 0.005  # 0.5%
        if not self.시장_개장:
            기본_변동성 = 0.001  # 장외 시간엔 변동성 감소
        
        # 가격 변동 생성
        변동율 = random.uniform(-기본_변동성, 기본_변동성)
        새_가격 = int(종목['현재가'] * (1 + 변동율))
        
        # 가격 업데이트
        종목['현재가'] = 새_가격
        
        # 등락률 계산
        등락률 = ((새_가격 - 종목['전일종가']) / 종목['전일종가']) * 100
        등락액 = 새_가격 - 종목['전일종가']
        
        return {
            '시간': datetime.now().isoformat(),
            '종목코드': 종목코드,
            '회사명': 종목['회사명'],
            '현재가': 새_가격,
            '전일종가': 종목['전일종가'],
            '등락액': 등락액,
            '등락률': round(등락률, 2),
            '거래량': random.randint(1000, 50000),
            '시장_개장': self.시장_개장
        }

class 주가_데이터_수집기:
    """비동기 주가 데이터 수집기"""
    
    def __init__(self, 시뮬레이터: 한국_주식_시뮬레이터):
        self.시뮬레이터 = 시뮬레이터
        self.구독_종목 = set()
        self.실행_중 = False
    
    def 종목_구독(self, 종목코드: str):
        """종목을 구독 목록에 추가"""
        self.구독_종목.add(종목코드)
        print(f"  {종목코드} 구독 추가됨")
    
    def 종목_구독_해제(self, 종목코드: str):
        """종목을 구독 목록에서 제거"""
        self.구독_종목.discard(종목코드)
        print(f"  {종목코드} 구독 해제됨")
    
    async def 실시간_데이터_스트림(
        self, 
        업데이트_간격: float = 2.0
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """실시간 주가 데이터 스트림"""
        
        self.실행_중 = True
        print(f"실시간 주가 스트림 시작 (구독 종목: {len(self.구독_종목)}개)")
        
        while self.실행_중 and self.구독_종목:
            for 종목코드 in self.구독_종목.copy():  # 구독 목록이 변경될 수 있으므로 복사
                try:
                    주가_데이터 = self.시뮬레이터.주가_변동_생성(종목코드)
                    yield 주가_데이터
                except Exception as e:
                    print(f"  {종목코드} 데이터 수집 오류: {e}")
            
            await asyncio.sleep(업데이트_간격)
    
    def 중지(self):
        """스트림 중지"""
        self.실행_중 = False
        print("  주가 스트림 중지됨")

class 주가_알림_시스템:
    """주가 알림 시스템"""
    
    def __init__(self):
        self.알림_규칙 = []  # (종목코드, 조건, 임계값) 형태
    
    def 알림_규칙_추가(self, 종목코드: str, 조건: str, 임계값: float):
        """알림 규칙 추가"""
        규칙 = {
            '종목코드': 종목코드,
            '조건': 조건,  # 'price_up', 'price_down', 'volume_high'
            '임계값': 임계값,
            '생성시간': datetime.now()
        }
        self.알림_규칙.append(규칙)
        print(f"  알림 규칙 추가: {종목코드} {조건} {임계값}")
    
    def 알림_확인(self, 주가_데이터: Dict[str, Any]) -> Optional[str]:
        """주가 데이터가 알림 조건에 해당하는지 확인"""
        종목코드 = 주가_데이터['종목코드']
        
        for 규칙 in self.알림_규칙:
            if 규칙['종목코드'] != 종목코드:
                continue
            
            조건 = 규칙['조건']
            임계값 = 규칙['임계값']
            
            if 조건 == 'price_up' and 주가_데이터['등락률'] >= 임계값:
                return f"{주가_데이터['회사명']} 급등! {주가_데이터['등락률']:+.1f}%"
            
            elif 조건 == 'price_down' and 주가_데이터['등락률'] <= -임계값:
                return f"{주가_데이터['회사명']} 급락! {주가_데이터['등락률']:+.1f}%"
            
            elif 조건 == 'volume_high' and 주가_데이터['거래량'] >= 임계값:
                return f"{주가_데이터['회사명']} 거래량 급증! {주가_데이터['거래량']:,}"
        
        return None

class 주가_데이터_저장소:
    """주가 데이터 저장소"""
    
    def __init__(self, 저장_경로: str = "stock_data"):
        self.저장_경로 = Path(저장_경로)
        self.저장_경로.mkdir(exist_ok=True)
        self.일일_데이터 = {}  # 종목별 일일 데이터
    
    async def 데이터_저장(self, 주가_데이터: Dict[str, Any]):
        """주가 데이터를 파일로 저장"""
        종목코드 = 주가_데이터['종목코드']
        날짜 = datetime.now().strftime('%Y-%m-%d')
        
        # 종목별 일일 데이터 파일
        파일명 = f"{종목코드}_{날짜}.json"
        파일_경로 = self.저장_경로 / 파일명
        
        # 기존 데이터 로드
        if 종목코드 not in self.일일_데이터:
            if 파일_경로.exists():
                with open(파일_경로, 'r', encoding='utf-8') as f:
                    self.일일_데이터[종목코드] = json.load(f)
            else:
                self.일일_데이터[종목코드] = []
        
        # 새 데이터 추가
        self.일일_데이터[종목코드].append(주가_데이터)
        
        # 파일로 저장 (일반 동기 I/O라서 쓰는 동안 이벤트 루프가 잠깐 멈춤)
        with open(파일_경로, 'w', encoding='utf-8') as f:
            json.dump(self.일일_데이터[종목코드], f, ensure_ascii=False, indent=2)

class 실시간_주가_모니터:
    """실시간 주가 모니터링 시스템 메인 클래스"""
    
    def __init__(self):
        self.시뮬레이터 = 한국_주식_시뮬레이터()
        self.수집기 = 주가_데이터_수집기(self.시뮬레이터)
        self.알림_시스템 = 주가_알림_시스템()
        self.저장소 = 주가_데이터_저장소()
        
        self.실행_중 = False
        self.처리된_데이터_수 = 0
    
    def 설정(self):
        """시스템 초기 설정"""
        print("=== 한국 실시간 주가 모니터링 시스템 ===")
        
        # 주요 종목 구독
        주요_종목 = ['005930', '000660', '035420']  # 삼성전자, SK하이닉스, NAVER
        for 종목 in 주요_종목:
            self.수집기.종목_구독(종목)
        
        # 알림 규칙 설정
        self.알림_시스템.알림_규칙_추가('005930', 'price_up', 3.0)    # 삼성전자 3% 이상 상승
        self.알림_시스템.알림_규칙_추가('000660', 'price_down', 3.0)   # SK하이닉스 3% 이상 하락
        self.알림_시스템.알림_규칙_추가('035420', 'volume_high', 30000) # NAVER 거래량 3만주 이상
    
    async def 시작(self, 실행_시간: int = 30):
        """모니터링 시스템 시작"""
        self.설정()
        self.실행_중 = True
        
        print(f"\n모니터링 시작 (실행 시간: {실행_시간}초)")
        print("-" * 80)
        
        시작_시간 = asyncio.get_event_loop().time()
        
        # 실시간 데이터 스트림 처리
        async for 주가_데이터 in self.수집기.실시간_데이터_스트림(업데이트_간격=1.0):
            # 경과 시간 확인
            현재_시간 = asyncio.get_event_loop().time()
            if 현재_시간 - 시작_시간 > 실행_시간:
                break
            
            # 주가 정보 출력
            self._주가_정보_출력(주가_데이터)
            
            # 알림 확인
            알림_메시지 = self.알림_시스템.알림_확인(주가_데이터)
            if 알림_메시지:
                print(f"    [!]  {알림_메시지}")
            
            # 데이터 저장
            await self.저장소.데이터_저장(주가_데이터)
            
            self.처리된_데이터_수 += 1
        
        print(f"\n모니터링 완료 (총 {self.처리된_데이터_수}건 처리)")
        self.수집기.중지()
    
    def _주가_정보_출력(self, 주가_데이터: Dict[str, Any]):
        """주가 정보를 보기 좋게 출력"""
        시간 = datetime.fromisoformat(주가_데이터['시간']).strftime('%H:%M:%S')
        회사명 = 주가_데이터['회사명']
        현재가 = 주가_데이터['현재가']
        등락률 = 주가_데이터['등락률']
        거래량 = 주가_데이터['거래량']
        
        # 등락률에 따라 상승 [+], 하락 [-], 보합 [=] 표시를 붙임
        등락률_표시 = f"{등락률:+.1f}%"
        if 등락률 > 0:
            등락률_표시 = f"[+] {등락률_표시}"
        elif 등락률 < 0:
            등락률_표시 = f"[-] {등락률_표시}"
        else:
            등락률_표시 = f"[=] {등락률_표시}"
        
        print(f"[{시간}] {회사명:>8} | {현재가:>7,}원 | {등락률_표시:>8} | 거래량: {거래량:>6,}")

# 실행 예제
async def 주가_모니터링_데모():
    """주가 모니터링 시스템 데모"""
    모니터 = 실시간_주가_모니터()
    
    try:
        await 모니터.시작(실행_시간=20)  # 20초간 실행
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단됨")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    print("실습 프로젝트: 한국 실시간 주가 모니터링 시스템\n")
    asyncio.run(주가_모니터링_데모())
