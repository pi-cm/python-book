# [1권 Chapter 14: 모듈과 패키지 · 14.5 패키지 사용하기 · manuscript/chapters/14-modules-packages.md:769]
# restaurant_app.py
from seoul_restaurants import Restaurant, RestaurantSearch, get_district_info

# 샘플 맛집 데이터 생성
restaurants = [
    Restaurant("김수한무 한정식", "강남구", "한식", "비쌈", 4.5, 128),
    Restaurant("홍길동 짜장면", "종로구", "중식", "저렴", 4.2, 89),
    Restaurant("이순신 초밥", "서초구", "일식", "보통", 4.7, 156),
    Restaurant("장보고 파스타", "마포구", "양식", "보통", 4.1, 94),
    Restaurant("을지문덕 족발", "강남구", "한식", "보통", 4.3, 201)
]

# 검색 엔진 초기화
search_engine = RestaurantSearch(restaurants)

print("=== 서울 맛집 검색 시스템 ===")

# 지역별 검색
print("\n1. 강남구 맛집:")
gangnam_restaurants = search_engine.search_by_district("강남구")
for restaurant in gangnam_restaurants:
    print(f"  • {restaurant.display_name} - {restaurant.rating}점")

# 음식 종류별 검색  
print("\n2. 한식 맛집:")
korean_restaurants = search_engine.search_by_cuisine("한식")
for restaurant in korean_restaurants:
    print(f"  • {restaurant.display_name} - {restaurant.price_range}")

# 평점 기준 검색
print("\n3. 평점 4.5 이상 맛집:")
high_rated = search_engine.search_by_rating(4.5)
for restaurant in high_rated:
    print(f"  • {restaurant.display_name} - {restaurant.rating}점 ({restaurant.review_count}개 리뷰)")

# 복합 조건 검색
print("\n4. 강남구의 4.0점 이상 맛집:")
filtered = search_engine.advanced_search(
    district="강남구",
    min_rating=4.0
)
for restaurant in filtered:
    print(f"  • {restaurant.display_name} - {restaurant.rating}점")

# 지역 정보 조회
print("\n5. 지역 정보:")
district_info = get_district_info("강남구")
print(f"  강남구: {district_info['region']} 권역")
print(f"  좌표: ({district_info['latitude']}, {district_info['longitude']})")
