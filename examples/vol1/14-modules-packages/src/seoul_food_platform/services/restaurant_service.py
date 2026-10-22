# [1권 Chapter 14: 모듈과 패키지 · 14.10 실전 프로젝트 구조 · manuscript/chapters/14-modules-packages.md:2322]
# src/seoul_food_platform/services/restaurant_service.py
"""레스토랑 서비스"""
from typing import List, Optional, Dict, Any
from decimal import Decimal
from uuid import UUID

from ..models.restaurant import Restaurant, CuisineType, PriceRange
from ..utils.exceptions import RestaurantNotFoundError, InvalidRatingError

class RestaurantService:
    """레스토랑 비즈니스 로직"""
    
    def __init__(self):
        self.restaurants: Dict[UUID, Restaurant] = {}
    
    def create_restaurant(self, **restaurant_data) -> Restaurant:
        """새 레스토랑 등록"""
        restaurant = Restaurant(**restaurant_data)
        self.restaurants[restaurant.id] = restaurant
        return restaurant
    
    def get_restaurant(self, restaurant_id: UUID) -> Restaurant:
        """레스토랑 조회"""
        restaurant = self.restaurants.get(restaurant_id)
        if not restaurant or restaurant.is_deleted:
            raise RestaurantNotFoundError(f"레스토랑을 찾을 수 없습니다: {restaurant_id}")
        return restaurant
    
    def update_restaurant(self, restaurant_id: UUID, **updates) -> Restaurant:
        """레스토랑 정보 수정"""
        restaurant = self.get_restaurant(restaurant_id)
        
        for key, value in updates.items():
            if hasattr(restaurant, key):
                setattr(restaurant, key, value)
        
        restaurant.update_timestamp()
        return restaurant
    
    def delete_restaurant(self, restaurant_id: UUID) -> None:
        """레스토랑 삭제 (소프트 삭제)"""
        restaurant = self.get_restaurant(restaurant_id)
        restaurant.delete()
    
    def add_review(self, restaurant_id: UUID, rating: int) -> Restaurant:
        """리뷰 추가"""
        if not 1 <= rating <= 5:
            raise InvalidRatingError("평점은 1-5 사이여야 합니다")
        
        restaurant = self.get_restaurant(restaurant_id)
        restaurant.add_review(rating)
        return restaurant
    
    def search_restaurants(self, **criteria) -> List[Restaurant]:
        """레스토랑 검색"""
        results = []
        
        for restaurant in self.restaurants.values():
            if restaurant.is_deleted:
                continue
                
            if restaurant.matches_criteria(**criteria):
                results.append(restaurant)
        
        # 평점 순으로 정렬
        return sorted(results, key=lambda r: r.average_rating, reverse=True)
    
    def get_restaurants_by_district(self, district: str) -> List[Restaurant]:
        """지역별 레스토랑 조회"""
        return self.search_restaurants(district=district)
    
    def get_highly_rated_restaurants(self, min_rating: float = 4.0) -> List[Restaurant]:
        """고평점 레스토랑 조회"""
        return self.search_restaurants(min_rating=min_rating)
    
    def get_popular_restaurants(self, min_reviews: int = 100) -> List[Restaurant]:
        """인기 레스토랑 조회 (리뷰 수 기준)"""
        results = []
        for restaurant in self.restaurants.values():
            if restaurant.is_deleted:
                continue
            if restaurant.review_count >= min_reviews:
                results.append(restaurant)
        
        return sorted(results, key=lambda r: r.review_count, reverse=True)
    
    def get_restaurant_statistics(self) -> Dict[str, Any]:
        """레스토랑 통계 정보"""
        active_restaurants = [r for r in self.restaurants.values() if not r.is_deleted]
        
        if not active_restaurants:
            return {
                'total_count': 0,
                'average_rating': 0.0,
                'cuisine_distribution': {},
                'district_distribution': {},
                'price_range_distribution': {}
            }
        
        # 음식 종류별 분포
        cuisine_dist = {}
        for restaurant in active_restaurants:
            cuisine = restaurant.cuisine_type.value
            cuisine_dist[cuisine] = cuisine_dist.get(cuisine, 0) + 1
        
        # 지역별 분포
        district_dist = {}
        for restaurant in active_restaurants:
            district = restaurant.location.district
            district_dist[district] = district_dist.get(district, 0) + 1
        
        # 가격대별 분포
        price_dist = {}
        for restaurant in active_restaurants:
            price = restaurant.price_range.value
            price_dist[price] = price_dist.get(price, 0) + 1
        
        # 평균 평점 계산
        total_rating = sum(r.average_rating for r in active_restaurants)
        avg_rating = float(total_rating / len(active_restaurants))
        
        return {
            'total_count': len(active_restaurants),
            'average_rating': round(avg_rating, 2),
            'cuisine_distribution': cuisine_dist,
            'district_distribution': district_dist,
            'price_range_distribution': price_dist
        }
