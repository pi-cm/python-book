# [1권 Chapter 14: 모듈과 패키지 · 14.4 패키지 기초 · manuscript/chapters/14-modules-packages.md:714]
# seoul_restaurants/__init__.py
"""
서울 맛집 관리 시스템

Usage:
    from seoul_restaurants import Restaurant, RestaurantSearch
    
    # 맛집 생성
    restaurant = Restaurant(
        name="김수한무 한정식",
        district="강남구",
        cuisine_type="한식",
        price_range="비쌈",
        rating=4.5
    )
    
    # 검색 엔진 사용
    search = RestaurantSearch([restaurant])
    results = search.search_by_district("강남구")
"""

# 패키지 정보 (PEP 8: docstring 바로 다음, import보다 위)
__version__ = "1.0.0"
__author__ = "Seoul Restaurant Team"

# 주요 클래스들을 패키지 레벨에서 import
from .models import Restaurant, Review
from .services import RestaurantSearch, RecommendationEngine
from .utils import DistanceCalculator, get_district_info

# 공개 API 정의
__all__ = [
    # Models
    'Restaurant',
    'Review',
    # Services  
    'RestaurantSearch',
    'RecommendationEngine',
    # Utils
    'DistanceCalculator',
    'get_district_info'
]

# 패키지 레벨 설정
DEFAULT_PRICE_RANGES = ['저렴', '보통', '비쌈']
SUPPORTED_CUISINES = ['한식', '중식', '일식', '양식', '아시안', '분식', '카페']
