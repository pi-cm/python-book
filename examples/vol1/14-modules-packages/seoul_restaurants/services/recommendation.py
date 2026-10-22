# [1권 Chapter 14: 모듈과 패키지 · 14.6 상대 import vs 절대 import · manuscript/chapters/14-modules-packages.md:855]
# seoul_restaurants/services/recommendation.py
"""
맛집 추천 엔진 (절대 import 사용)
"""
from seoul_restaurants.models.restaurant import Restaurant
from seoul_restaurants.models.review import Review
from seoul_restaurants.utils.rating import RatingAnalyzer
from typing import List, Dict

class RecommendationEngine:
    """맛집 추천 엔진"""
    
    def __init__(self, restaurants: List[Restaurant]):
        self.restaurants = restaurants
        self.rating_analyzer = RatingAnalyzer()
    
    def recommend_by_preference(self, 
                              preferred_cuisines: List[str],
                              preferred_districts: List[str] = None,
                              min_rating: float = 4.0) -> List[Restaurant]:
        """사용자 선호도 기반 추천"""
        candidates = []
        
        for restaurant in self.restaurants:
            # 음식 종류 필터
            if restaurant.cuisine_type not in preferred_cuisines:
                continue
            
            # 지역 필터 (선택사항)
            if preferred_districts and restaurant.district not in preferred_districts:
                continue
            
            # 최소 평점 필터
            if restaurant.rating < min_rating:
                continue
                
            candidates.append(restaurant)
        
        # 평점과 리뷰 수를 종합한 점수로 정렬
        return sorted(candidates, 
                     key=lambda r: (r.rating * 0.7 + min(r.review_count/100, 1) * 0.3),
                     reverse=True)[:10]
    
    def recommend_similar(self, target_restaurant: Restaurant) -> List[Restaurant]:
        """비슷한 맛집 추천"""
        similar = []
        
        for restaurant in self.restaurants:
            if restaurant.name == target_restaurant.name:
                continue
            
            similarity_score = 0
            
            # 같은 음식 종류 (+3점)
            if restaurant.cuisine_type == target_restaurant.cuisine_type:
                similarity_score += 3
            
            # 같은 지역 (+2점)  
            if restaurant.district == target_restaurant.district:
                similarity_score += 2
            
            # 비슷한 가격대 (+1점)
            if restaurant.price_range == target_restaurant.price_range:
                similarity_score += 1
            
            # 비슷한 평점 (차이가 적을수록 높은 점수)
            rating_diff = abs(restaurant.rating - target_restaurant.rating)
            if rating_diff <= 0.5:
                similarity_score += 2
            elif rating_diff <= 1.0:
                similarity_score += 1
            
            if similarity_score >= 3:  # 임계점
                similar.append((restaurant, similarity_score))
        
        # 유사도 점수 순으로 정렬
        similar.sort(key=lambda x: x[1], reverse=True)
        return [restaurant for restaurant, score in similar[:5]]
