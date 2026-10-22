# [1권 Chapter 14: 모듈과 패키지 · 14.10 실전 프로젝트 구조 · manuscript/chapters/14-modules-packages.md:2052]
# src/seoul_food_platform/models/restaurant.py
"""레스토랑 모델"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from decimal import Decimal

from .base import BaseModel, TimestampMixin, SoftDeleteMixin

class CuisineType(Enum):
    """음식 종류"""
    KOREAN = "한식"
    CHINESE = "중식"  
    JAPANESE = "일식"
    WESTERN = "양식"
    ASIAN = "아시안"
    FUSION = "퓨전"
    CAFE = "카페"
    BAKERY = "베이커리"
    FAST_FOOD = "패스트푸드"
    
class PriceRange(Enum):
    """가격대"""
    BUDGET = "저렴"      # ~15,000원
    MODERATE = "보통"    # 15,000~30,000원
    EXPENSIVE = "비쌈"   # 30,000원~
    FINE_DINING = "고급" # 50,000원~

class RestaurantStatus(Enum):
    """운영 상태"""
    OPEN = "영업중"
    CLOSED = "휴업"
    PERMANENTLY_CLOSED = "폐업"
    TEMPORARILY_CLOSED = "임시휴업"

@dataclass
class Location:
    """위치 정보"""
    address: str
    district: str  # 구
    neighborhood: str  # 동
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    postal_code: Optional[str] = None
    
    @property
    def full_address(self) -> str:
        """전체 주소"""
        return f"서울시 {self.district} {self.address}"

@dataclass
class ContactInfo:
    """연락처 정보"""
    phone: Optional[str] = None
    website: Optional[str] = None
    social_media: Dict[str, str] = field(default_factory=dict)

@dataclass
class BusinessHours:
    """영업시간"""
    monday: Optional[str] = None
    tuesday: Optional[str] = None
    wednesday: Optional[str] = None
    thursday: Optional[str] = None
    friday: Optional[str] = None
    saturday: Optional[str] = None
    sunday: Optional[str] = None
    holiday: Optional[str] = None
    
    def get_today_hours(self) -> Optional[str]:
        """오늘의 영업시간 반환"""
        from datetime import datetime
        weekday = datetime.now().weekday()  # 0=월요일
        
        hours_map = [
            self.monday, self.tuesday, self.wednesday, self.thursday,
            self.friday, self.saturday, self.sunday
        ]
        
        return hours_map[weekday] if weekday < 7 else None

@dataclass(kw_only=True)  # 부모의 기본값 필드 뒤에 필수 필드를 두기 위해 키워드 전용으로
class Restaurant(BaseModel, TimestampMixin, SoftDeleteMixin):
    """레스토랑 정보 모델"""
    name: str
    cuisine_type: CuisineType
    price_range: PriceRange
    location: Location
    
    # 평점 정보
    average_rating: Decimal = Decimal('0.0')
    review_count: int = 0
    rating_distribution: Dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0})
    
    # 기본 정보
    description: Optional[str] = None
    specialty_dishes: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)  # ["주차가능", "와이파이", "단체석"]
    
    # 연락처 및 영업정보
    contact: ContactInfo = field(default_factory=ContactInfo)
    business_hours: BusinessHours = field(default_factory=BusinessHours)
    status: RestaurantStatus = RestaurantStatus.OPEN
    
    # 메타데이터
    photos: List[str] = field(default_factory=list)  # 사진 URL들
    tags: List[str] = field(default_factory=list)
    verified: bool = False  # 사업자 인증 여부
    
    def __post_init__(self):
        super().__post_init__()
        
        # Enum 값 처리
        if isinstance(self.cuisine_type, str):
            self.cuisine_type = CuisineType(self.cuisine_type)
        if isinstance(self.price_range, str):
            self.price_range = PriceRange(self.price_range)
        if isinstance(self.status, str):
            self.status = RestaurantStatus(self.status)
        
        # Decimal 처리
        if isinstance(self.average_rating, (int, float)):
            self.average_rating = Decimal(str(self.average_rating))
    
    @property
    def display_name(self) -> str:
        """화면 표시용 이름"""
        return f"{self.name} ({self.location.district})"
    
    @property
    def is_highly_rated(self) -> bool:
        """고평점 맛집 여부 (4.0 이상)"""
        return self.average_rating >= Decimal('4.0')
    
    @property
    def is_popular(self) -> bool:
        """인기 맛집 여부 (리뷰 100개 이상)"""
        return self.review_count >= 100
    
    def add_review(self, rating: int, update_distribution: bool = True) -> None:
        """리뷰 추가 및 평점 업데이트"""
        if not 1 <= rating <= 5:
            raise ValueError("평점은 1-5 사이여야 합니다")
        
        # 새 평균 계산
        total_score = self.average_rating * self.review_count + Decimal(str(rating))
        self.review_count += 1
        self.average_rating = (total_score / self.review_count).quantize(Decimal('0.1'))
        
        # 평점 분포 업데이트
        if update_distribution:
            self.rating_distribution[rating] += 1
        
        self.update_timestamp()
    
    def get_rating_percentage(self, rating: int) -> float:
        """특정 평점의 비율 반환"""
        if self.review_count == 0:
            return 0.0
        return (self.rating_distribution.get(rating, 0) / self.review_count) * 100
    
    def matches_criteria(self, **criteria) -> bool:
        """검색 조건 매칭 확인"""
        for key, value in criteria.items():
            match key:
                case 'cuisine_type':
                    if self.cuisine_type != CuisineType(value):
                        return False
                case 'district':
                    if self.location.district != value:
                        return False
                case 'min_rating':
                    if self.average_rating < Decimal(str(value)):
                        return False
                case 'price_range':
                    if self.price_range != PriceRange(value):
                        return False
                case 'features':
                    if not all(feature in self.features for feature in value):
                        return False
                case _:
                    continue
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환 (오버라이드)"""
        result = super().to_dict()
        
        # Enum 처리
        result['cuisine_type'] = self.cuisine_type.value
        result['price_range'] = self.price_range.value  
        result['status'] = self.status.value
        
        # Decimal 처리
        result['average_rating'] = float(self.average_rating)
        
        # 중첩 객체 처리
        result['location'] = {
            'address': self.location.address,
            'district': self.location.district,
            'neighborhood': self.location.neighborhood,
            'latitude': self.location.latitude,
            'longitude': self.location.longitude,
            'postal_code': self.location.postal_code,
            'full_address': self.location.full_address
        }
        
        return result

# 팩토리 함수들
def create_sample_restaurant(name: str, district: str) -> Restaurant:
    """샘플 레스토랑 생성"""
    location = Location(
        address=f"{district} 샘플로 123",
        district=district,
        neighborhood="샘플동"
    )
    
    return Restaurant(
        name=name,
        cuisine_type=CuisineType.KOREAN,
        price_range=PriceRange.MODERATE,
        location=location,
        description=f"{name}의 맛있는 한식 레스토랑",
        specialty_dishes=["불고기", "된장찌개"],
        features=["주차가능", "와이파이"]
    )

def create_restaurant_from_dict(data: Dict[str, Any]) -> Restaurant:
    """딕셔너리로부터 레스토랑 객체 생성"""
    location_data = data.pop('location', {})
    contact_data = data.pop('contact', {})
    hours_data = data.pop('business_hours', {})
    
    location = Location(**location_data)
    contact = ContactInfo(**contact_data)  
    hours = BusinessHours(**hours_data)
    
    return Restaurant(
        location=location,
        contact=contact, 
        business_hours=hours,
        **data
    )
