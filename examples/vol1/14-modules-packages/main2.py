# [1권 Chapter 14: 모듈과 패키지 · 14.2 모듈 불러오기 (Import) · manuscript/chapters/14-modules-packages.md:173]
# main2.py
from cafe_utils import calculate_total, format_menu_item, CafeManager

# 모듈명 없이 직접 사용
orders = [
    {'price': 4500},  # 아메리카노
    {'price': 5000},  # 라떼
    {'price': 3500}   # 크로와상
]

total = calculate_total(orders)
print(f"총 주문금액: {total:,}원")  # 총 주문금액: 13,000원

# 클래스도 직접 사용
hongdae_cafe = CafeManager("수진네 카페", "홍대")
