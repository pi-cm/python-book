# [1권 Chapter 14: 모듈과 패키지 · 14.6 상대 import vs 절대 import · manuscript/chapters/14-modules-packages.md:980]
# import_comparison.py
"""
절대 import vs 상대 import 비교
"""

# 1. 절대 import (권장)
from seoul_restaurants.models.restaurant import Restaurant
from seoul_restaurants.services.search import RestaurantSearch

# 장점:
# - 명확하고 이해하기 쉬움
# - IDE에서 자동완성 지원 좋음
# - 에러 메시지에 전체 경로가 드러나 원인을 찾기 쉬움
# - 어디서든 사용 가능

# 2. 상대 import (패키지 내부에서만)
# from .models.restaurant import Restaurant  # 같은 레벨
# from ..models.restaurant import Restaurant  # 상위 레벨

# 장점:
# - 패키지명이 바뀌어도 코드 수정 불필요
# - 타이핑이 적음

# 단점:
# - 복잡한 구조에서 헷갈리기 쉬움
# - 스크립트를 직접 실행할 때 문제 발생 가능
