# [1권 Chapter 14: 모듈과 패키지 · 14.4 패키지 기초 · manuscript/chapters/14-modules-packages.md:509]
# seoul_restaurants/services/search.py
"""
맛집 검색 서비스
"""
from typing import List, Optional, Dict, Any
from .models import Restaurant

class RestaurantSearch:
    """맛집 검색 엔진"""
    
    def __init__(self, restaurants: List[Restaurant]):
        self.restaurants = restaurants
        self._build_indices()
    
    def _build_indices(self):
        """검색 성능을 위한 인덱스 구축"""
        self.district_index = {}
        self.cuisine_index = {}
        
        for restaurant in self.restaurants:
            # 지역별 인덱스
            district = restaurant.district
            if district not in self.district_index:
                self.district_index[district] = []
            self.district_index[district].append(restaurant)
            
            # 음식 종류별 인덱스
            cuisine = restaurant.cuisine_type
            if cuisine not in self.cuisine_index:
                self.cuisine_index[cuisine] = []
            self.cuisine_index[cuisine].append(restaurant)
    
    def search_by_district(self, district: str) -> List[Restaurant]:
        """지역별 맛집 검색"""
        return self.district_index.get(district, [])
    
    def search_by_cuisine(self, cuisine_type: str) -> List[Restaurant]:
        """음식 종류별 검색"""
        return self.cuisine_index.get(cuisine_type, [])
    
    def search_by_rating(self, min_rating: float) -> List[Restaurant]:
        """평점 이상 맛집 검색"""
        return [r for r in self.restaurants if r.rating >= min_rating]
    
    def advanced_search(self, **criteria) -> List[Restaurant]:
        """고급 검색"""
        results = self.restaurants.copy()
        
        if 'district' in criteria:
            results = [r for r in results if r.district == criteria['district']]
        
        if 'cuisine_type' in criteria:
            results = [r for r in results if r.cuisine_type == criteria['cuisine_type']]
        
        if 'min_rating' in criteria:
            results = [r for r in results if r.rating >= criteria['min_rating']]
        
        if 'price_range' in criteria:
            results = [r for r in results if r.price_range == criteria['price_range']]
        
        # 평점 순으로 정렬
        return sorted(results, key=lambda x: x.rating, reverse=True)
