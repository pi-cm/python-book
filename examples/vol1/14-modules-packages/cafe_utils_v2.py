# [1권 Chapter 14: 모듈과 패키지 · 14.3 모듈의 고급 기능 · manuscript/chapters/14-modules-packages.md:293]
# cafe_utils_v2.py
"""
개선된 카페 유틸리티 모듈
"""

# public API 명시적으로 정의
__all__ = [
    'calculate_total',
    'format_menu_item', 
    'CafeManager',
    'DEFAULT_PRICE'
]

DEFAULT_PRICE = 4500
_INTERNAL_CONFIG = {'debug': False}  # private 변수

def calculate_total(items):
    """공개 함수"""
    return sum(item.get('price', DEFAULT_PRICE) for item in items)

def _validate_price(price):
    """내부 함수 (private)"""
    return price > 0

def format_menu_item(name, price, category='커피'):
    """공개 함수"""
    if not _validate_price(price):
        raise ValueError("가격은 0보다 커야 합니다")
    
    return {
        'name': name,
        'price': price,
        'category': category,
        'formatted': f"{name} - {price:,}원 ({category})"
    }

class CafeManager:
    """공개 클래스"""
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.menu = []
