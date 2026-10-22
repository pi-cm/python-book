# [1권 Chapter 14: 모듈과 패키지 · 14.6 상대 import vs 절대 import · manuscript/chapters/14-modules-packages.md:942]
# seoul_restaurants/services/recommendation_relative.py
"""
맛집 추천 엔진 (상대 import 사용 예제)
"""
from typing import List

# 같은 레벨의 다른 모듈
from .search import RestaurantSearch

# 상위 패키지의 모듈
from ..models.restaurant import Restaurant
from ..models.review import Review

# 상위 패키지의 다른 하위 패키지
from ..utils.rating import RatingAnalyzer

class RecommendationEngineRelative:
    """상대 import를 사용한 추천 엔진"""
    
    def __init__(self, restaurants: List[Restaurant]):
        self.restaurants = restaurants
        self.search_engine = RestaurantSearch(restaurants)  # 같은 패키지
        self.rating_analyzer = RatingAnalyzer()  # 다른 패키지
