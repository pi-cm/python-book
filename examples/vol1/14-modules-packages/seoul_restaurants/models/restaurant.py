# [1권 Chapter 14: 모듈과 패키지 · 14.4 패키지 기초 · manuscript/chapters/14-modules-packages.md:413]
# seoul_restaurants/models/restaurant.py
"""
맛집 모델
"""
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Restaurant:
    """서울 맛집 정보를 담는 클래스"""
    name: str
    district: str  # 강남구, 종로구 등
    cuisine_type: str  # 한식, 중식, 일식 등
    price_range: str  # 저렴, 보통, 비쌈
    rating: float = 0.0
    review_count: int = 0
    address: Optional[str] = None
    phone: Optional[str] = None
    
    def __post_init__(self):
        """초기화 후 검증"""
        if not (0 <= self.rating <= 5):
            raise ValueError("평점은 0-5 사이여야 합니다")
        
        if self.review_count < 0:
            raise ValueError("리뷰 수는 0 이상이어야 합니다")
    
    @property
    def display_name(self) -> str:
        """표시용 이름"""
        return f"{self.name} ({self.district})"
    
    def update_rating(self, new_rating: float, review_count_delta: int = 1):
        """새 리뷰 반영하여 평점 업데이트"""
        total_score = self.rating * self.review_count + new_rating
        self.review_count += review_count_delta
        self.rating = round(total_score / self.review_count, 1)
