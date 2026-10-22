# [1권 Chapter 14: 모듈과 패키지 · 14.8 uv를 활용한 현대적 패키지 관리 · manuscript/chapters/14-modules-packages.md:1314]
# src/seoul_restaurant_finder/cli.py
"""명령행 인터페이스"""
import click
from .search import RestaurantSearch
from .models import Restaurant

@click.command()
@click.option('--district', help='검색할 지역구')
@click.option('--cuisine', help='음식 종류')
@click.option('--min-rating', type=float, default=0.0, help='최소 평점')
def main(district, cuisine, min_rating):
    """서울 맛집 검색 CLI"""
    # 샘플 데이터
    restaurants = [
        Restaurant("김수한무 한정식", "강남구", "한식", "비쌈", 4.5, 128),
        Restaurant("홍길동 짜장면", "종로구", "중식", "저렴", 4.2, 89),
        Restaurant("이순신 초밥", "서초구", "일식", "보통", 4.7, 156),
    ]
    
    search = RestaurantSearch(restaurants)
    
    # 검색 조건 적용
    criteria = {}
    if district:
        criteria['district'] = district
    if cuisine:
        criteria['cuisine_type'] = cuisine
    if min_rating > 0:
        criteria['min_rating'] = min_rating
    
    results = search.advanced_search(**criteria)
    
    click.echo(f"검색 결과: {len(results)}개 맛집")
    for restaurant in results:
        click.echo(f"• {restaurant.display_name} - {restaurant.rating}점")

if __name__ == '__main__':
    main()
