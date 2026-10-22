# [1권 Chapter 14: 모듈과 패키지 · 14.5 패키지 사용하기 · manuscript/chapters/14-modules-packages.md:827]
# advanced_usage.py
from seoul_restaurants.models.restaurant import Restaurant
from seoul_restaurants.services.search import RestaurantSearch
from seoul_restaurants.utils.location import DistanceCalculator

# 거리 계산 예제
distance = DistanceCalculator.distance_between_districts("강남구", "종로구")
print(f"강남구와 종로구 사이의 거리: {distance:.1f}km")

# 맛집 평점 업데이트
restaurant = Restaurant("새로운 맛집", "홍대", "한식", "보통", 4.0, 50)
print(f"업데이트 전: {restaurant.rating}점 ({restaurant.review_count}개 리뷰)")

restaurant.update_rating(5.0)  # 새 리뷰 추가
print(f"업데이트 후: {restaurant.rating}점 ({restaurant.review_count}개 리뷰)")
