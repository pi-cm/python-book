# [1권 Chapter 14: 모듈과 패키지 · 14.4 패키지 기초 · manuscript/chapters/14-modules-packages.md:455]
# seoul_restaurants/models/review.py
"""
리뷰 모델
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Review:
    """맛집 리뷰 클래스"""
    restaurant_id: str
    author_name: str
    rating: float
    content: str
    visit_date: datetime
    created_at: datetime = None
    helpful_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        
        if not (1 <= self.rating <= 5):
            raise ValueError("평점은 1-5 사이여야 합니다")
    
    @property
    def is_recent(self) -> bool:
        """최근 리뷰인지 확인 (30일 이내)"""
        days_ago = (datetime.now() - self.created_at).days
        return days_ago <= 30
    
    def get_summary(self) -> str:
        """리뷰 요약"""
        short_content = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.author_name} ({self.rating}점): {short_content}"
