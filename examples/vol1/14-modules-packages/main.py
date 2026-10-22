# [1권 Chapter 14: 모듈과 패키지 · 14.2 모듈 불러오기 (Import) · manuscript/chapters/14-modules-packages.md:150]
# main.py
import cafe_utils

# 모듈의 함수 사용
menu_item = cafe_utils.format_menu_item("라떼", 5000)
print(menu_item['formatted'])  # 라떼 - 5,000원 (커피)

# 모듈의 클래스 사용
my_cafe = cafe_utils.CafeManager("민수네 카페", "강남")
my_cafe.add_menu_item("아메리카노", 4500)
my_cafe.add_menu_item("크로와상", 3500, "베이커리")

print(f"카페명: {my_cafe.name}")
print(f"메뉴 개수: {len(my_cafe.menu)}")
