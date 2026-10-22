# [1권 Chapter 14: 모듈과 패키지 · 14.4 패키지 기초 · manuscript/chapters/14-modules-packages.md:400]
# seoul_restaurants/models/__init__.py
"""
맛집 데이터 모델 패키지
"""
from .restaurant import Restaurant
from .review import Review

__all__ = ['Restaurant', 'Review']
