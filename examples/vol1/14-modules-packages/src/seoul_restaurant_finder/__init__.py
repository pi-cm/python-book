# [1권 Chapter 14: 모듈과 패키지 · 14.8 uv를 활용한 현대적 패키지 관리 · manuscript/chapters/14-modules-packages.md:1303]
# src/seoul_restaurant_finder/__init__.py
"""서울 맛집 검색 시스템"""
__version__ = "0.1.0"

from .models import Restaurant, Review
from .search import RestaurantSearch

__all__ = ["Restaurant", "Review", "RestaurantSearch"]
