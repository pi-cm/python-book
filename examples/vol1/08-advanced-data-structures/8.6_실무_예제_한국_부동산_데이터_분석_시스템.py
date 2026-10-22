"""1권 Chapter 8: 고급 데이터 구조 — 8.6 실무 예제: 한국 부동산 데이터 분석 시스템

원고: manuscript/chapters/08-advanced-data-structures.md (1487줄부터)
"""

# ---- 원고 1487줄 ----
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Set
from enum import Enum
from datetime import date, datetime
from collections import defaultdict, Counter
import statistics

class PropertyType(Enum):
    """부동산 유형"""
    APARTMENT = "아파트"
    VILLA = "빌라"
    ONEROOM = "원룸"
    OFFICETEL = "오피스텔"
    HOUSE = "단독주택"
    COMMERCIAL = "상가"

class TransactionType(Enum):
    """거래 유형"""
    SALE = "매매"
    RENT = "전세"
    MONTHLY_RENT = "월세"

@dataclass
class PropertyInfo:
    """부동산 기본 정보"""
    property_id: str
    address: str
    property_type: PropertyType
    area_sqm: float  # 평방미터
    floor: Optional[int] = None
    total_floors: Optional[int] = None
    built_year: Optional[int] = None
    
    @property
    def area_pyeong(self) -> float:
        """평 단위 면적"""
        return self.area_sqm / 3.3058
    
    @property
    def age(self) -> Optional[int]:
        """건물 연식"""
        if self.built_year:
            return datetime.now().year - self.built_year
        return None

@dataclass
class Transaction:
    """거래 내역"""
    transaction_id: str
    property_info: PropertyInfo
    transaction_type: TransactionType
    price: int  # 만원 단위
    deposit: Optional[int] = None  # 보증금 (월세의 경우)
    monthly_rent: Optional[int] = None  # 월세
    transaction_date: date = field(default_factory=date.today)
    
    @property
    def price_per_pyeong(self) -> float:
        """평당 가격"""
        return self.price / self.property_info.area_pyeong
    
    def format_price(self) -> str:
        """가격 포맷팅"""
        if self.transaction_type == TransactionType.MONTHLY_RENT:
            return f"보증금 {self.deposit:,}만원, 월세 {self.monthly_rent:,}만원"
        else:
            return f"{self.price:,}만원"

class RealEstateAnalyzer:
    """부동산 데이터 분석기"""
    
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.region_stats = defaultdict(list)
        self.property_type_stats = defaultdict(list)
        
    def add_transaction(self, transaction: Transaction):
        """거래 데이터 추가"""
        self.transactions.append(transaction)
        
        # 지역별 통계 업데이트
        region = self._extract_region(transaction.property_info.address)
        self.region_stats[region].append(transaction)
        
        # 부동산 유형별 통계 업데이트  
        self.property_type_stats[transaction.property_info.property_type].append(transaction)
    
    def _extract_region(self, address: str) -> str:
        """주소에서 지역 추출"""
        # 간단한 지역 추출 로직
        parts = address.split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}"  # 예: "서울시 강남구"
        return parts[0] if parts else "알 수 없음"
    
    def analyze_by_region(self) -> Dict[str, Dict[str, Any]]:
        """지역별 분석"""
        results = {}
        
        for region, transactions in self.region_stats.items():
            if not transactions:
                continue
                
            prices = [t.price for t in transactions if t.transaction_type != TransactionType.MONTHLY_RENT]
            
            if prices:
                results[region] = {
                    "거래수": len(transactions),
                    "평균가격": statistics.mean(prices),
                    "중간가격": statistics.median(prices),
                    "최고가격": max(prices),
                    "최저가격": min(prices),
                    "가격표준편차": statistics.stdev(prices) if len(prices) > 1 else 0,
                    "주요부동산유형": Counter(t.property_info.property_type for t in transactions).most_common(1)[0]
                }
        
        return results
    
    def analyze_by_property_type(self) -> Dict[PropertyType, Dict[str, Any]]:
        """부동산 유형별 분석"""
        results = {}
        
        for prop_type, transactions in self.property_type_stats.items():
            if not transactions:
                continue
                
            prices = [t.price for t in transactions if t.transaction_type != TransactionType.MONTHLY_RENT]
            areas = [t.property_info.area_pyeong for t in transactions]
            
            if prices and areas:
                # 가격과 면적을 같은 거래에서 짝지어야 하므로 월세를 뺀 거래에서 직접 계산
                price_per_pyeong = [t.price_per_pyeong for t in transactions
                                    if t.transaction_type != TransactionType.MONTHLY_RENT]
                
                results[prop_type] = {
                    "거래수": len(transactions),
                    "평균가격": statistics.mean(prices),
                    "평균면적": statistics.mean(areas),
                    "평당평균가격": statistics.mean(price_per_pyeong),
                    "거래유형분포": Counter(t.transaction_type for t in transactions),
                    "주요지역": Counter(self._extract_region(t.property_info.address) for t in transactions).most_common(3)
                }
        
        return results
    
    def find_best_value_properties(self, max_price: int, min_area: float) -> List[Transaction]:
        """가성비 좋은 매물 찾기"""
        candidates = []
        
        for transaction in self.transactions:
            if (transaction.transaction_type == TransactionType.SALE and
                transaction.price <= max_price and
                transaction.property_info.area_pyeong >= min_area):
                candidates.append(transaction)
        
        # 평당 가격 기준으로 정렬
        candidates.sort(key=lambda t: t.price_per_pyeong)
        
        return candidates[:10]  # 상위 10개 반환
    
    def generate_report(self) -> str:
        """종합 분석 보고서 생성"""
        report = ["부동산 시장 분석 보고서", "=" * 40]
        
        # 기본 통계
        total_transactions = len(self.transactions)
        report.append(f"\n기본 통계:")
        report.append(f"  총 거래 수: {total_transactions:,}건")
        report.append(f"  분석 지역 수: {len(self.region_stats)}개 지역")
        report.append(f"  부동산 유형 수: {len(self.property_type_stats)}개 유형")
        
        # 지역별 분석
        region_analysis = self.analyze_by_region()
        report.append(f"\n지역별 분석 (상위 5개 지역):")
        
        sorted_regions = sorted(region_analysis.items(), 
                               key=lambda x: x[1]["평균가격"], reverse=True)[:5]
        
        for region, stats in sorted_regions:
            report.append(f"  {region}:")
            report.append(f"    평균 가격: {stats['평균가격']:,.0f}만원")
            report.append(f"    거래 수: {stats['거래수']}건")
            report.append(f"    주요 유형: {stats['주요부동산유형'][0].value}")
        
        # 부동산 유형별 분석
        type_analysis = self.analyze_by_property_type()
        report.append(f"\n부동산 유형별 분석:")
        
        for prop_type, stats in type_analysis.items():
            report.append(f"  {prop_type.value}:")
            report.append(f"    평균 가격: {stats['평균가격']:,.0f}만원")
            report.append(f"    평당 가격: {stats['평당평균가격']:,.0f}만원/평")
            report.append(f"    평균 면적: {stats['평균면적']:.1f}평")
        
        return "\n".join(report)

# ---- 원고 1691줄 ----
def create_sample_data() -> List[Transaction]:
    """샘플 부동산 거래 데이터 생성"""
    import random
    from datetime import timedelta
    
    # 서울 주요 지역
    seoul_regions = [
        "서울시 강남구", "서울시 서초구", "서울시 송파구", "서울시 강동구",
        "서울시 마포구", "서울시 용산구", "서울시 성동구", "서울시 광진구",
        "서울시 강북구", "서울시 노원구"
    ]
    
    # 경기도 주요 지역
    gyeonggi_regions = [
        "경기도 성남시", "경기도 고양시", "경기도 수원시", "경기도 안양시",
        "경기도 부천시", "경기도 의정부시"
    ]
    
    all_regions = seoul_regions + gyeonggi_regions
    
    transactions = []
    base_date = date(2023, 1, 1)
    
    for i in range(200):  # 200개 샘플 거래 생성
        region = random.choice(all_regions)
        property_type = random.choice(list(PropertyType))
        transaction_type = random.choice(list(TransactionType))
        
        # 지역과 부동산 유형에 따른 가격 조정
        base_price = 50000  # 기본 5억
        if "강남구" in region or "서초구" in region:
            base_price *= 2
        elif "서울시" in region:
            base_price *= 1.5
        
        if property_type == PropertyType.APARTMENT:
            base_price *= 1.2
        elif property_type == PropertyType.ONEROOM:
            base_price *= 0.3
        elif property_type == PropertyType.VILLA:
            base_price *= 0.7
        
        # 면적 생성
        area_sqm = random.uniform(20, 150)
        if property_type == PropertyType.ONEROOM:
            area_sqm = random.uniform(15, 30)
        elif property_type == PropertyType.APARTMENT:
            area_sqm = random.uniform(60, 120)
        
        # 거래 생성
        property_info = PropertyInfo(
            property_id=f"PROP_{i+1:04d}",
            address=f"{region} {random.choice(['역삼동', '논현동', '도곡동', '청담동'])}",
            property_type=property_type,
            area_sqm=area_sqm,
            floor=random.randint(1, 20) if random.random() > 0.2 else None,
            total_floors=random.randint(5, 25) if random.random() > 0.3 else None,
            built_year=random.randint(1990, 2023) if random.random() > 0.1 else None
        )
        
        # 가격 계산
        price_variation = random.uniform(0.7, 1.3)
        final_price = int(base_price * price_variation)
        
        transaction_date = base_date + timedelta(days=random.randint(0, 365))
        
        if transaction_type == TransactionType.MONTHLY_RENT:
            deposit = int(final_price * random.uniform(0.1, 0.3))
            monthly_rent = int(final_price * random.uniform(0.01, 0.03))
            transaction = Transaction(
                transaction_id=f"TXN_{i+1:04d}",
                property_info=property_info,
                transaction_type=transaction_type,
                price=0,  # 월세는 price가 0
                deposit=deposit,
                monthly_rent=monthly_rent,
                transaction_date=transaction_date
            )
        else:
            transaction = Transaction(
                transaction_id=f"TXN_{i+1:04d}",
                property_info=property_info,
                transaction_type=transaction_type,
                price=final_price,
                transaction_date=transaction_date
            )
        
        transactions.append(transaction)
    
    return transactions

def demonstrate_real_estate_analysis():
    """부동산 분석 시연"""
    print("한국 부동산 데이터 분석 시스템")
    print("=" * 50)
    
    # 샘플 데이터 생성
    print("샘플 데이터 생성 중...")
    transactions = create_sample_data()
    
    # 분석기 생성 및 데이터 추가
    analyzer = RealEstateAnalyzer()
    for transaction in transactions:
        analyzer.add_transaction(transaction)
    
    # 종합 보고서 출력
    report = analyzer.generate_report()
    print(report)
    
    # 가성비 좋은 매물 찾기
    print(f"\n가성비 매물 (5억 이하, 25평 이상):")
    print("-" * 40)
    
    value_properties = analyzer.find_best_value_properties(
        max_price=50000,  # 5억
        min_area=25       # 25평
    )
    
    for i, transaction in enumerate(value_properties[:5], 1):
        prop = transaction.property_info
        print(f"{i}. {prop.property_type.value} | {prop.address}")
        print(f"   {prop.area_pyeong:.1f}평 | {transaction.format_price()}")
        print(f"   평당 {transaction.price_per_pyeong:,.0f}만원")
        if prop.age:
            print(f"   건물 연식: {prop.age}년")
        print()

# 분석 실행
demonstrate_real_estate_analysis()
