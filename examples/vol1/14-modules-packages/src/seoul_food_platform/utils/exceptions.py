# [1권 Chapter 14: 모듈과 패키지 · 14.10 실전 프로젝트 구조 · manuscript/chapters/14-modules-packages.md:2303]
# src/seoul_food_platform/utils/exceptions.py
"""서울 음식 플랫폼의 예외 모음"""


class SeoulFoodPlatformError(Exception):
    """이 프로젝트의 모든 예외의 기반 클래스"""


class RestaurantNotFoundError(SeoulFoodPlatformError):
    """찾는 레스토랑이 없거나 삭제되었을 때"""


class InvalidRatingError(SeoulFoodPlatformError):
    """평점이 허용 범위(1~5)를 벗어났을 때"""
