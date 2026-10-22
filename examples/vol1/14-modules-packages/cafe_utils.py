# [1권 Chapter 14: 모듈과 패키지 · 14.1 모듈의 기본 개념 · manuscript/chapters/14-modules-packages.md:47]
# cafe_utils.py
"""
서울 카페 관리를 위한 유틸리티 모듈
"""

# 상수 정의
DEFAULT_PRICE = 4500
MENU_CATEGORIES = ['커피', '차', '디저트', '베이커리']

# 함수 정의
def calculate_total(items):
    """주문 항목들의 총액을 계산합니다."""
    total = 0
    for item in items:
        total += item.get('price', DEFAULT_PRICE)
    return total

def format_menu_item(name, price, category='커피'):
    """메뉴 항목을 형식에 맞게 포맷팅합니다."""
    return {
        'name': name,
        'price': price,
        'category': category,
        'formatted': f"{name} - {price:,}원 ({category})"
    }

# 클래스 정의
class CafeManager:
    """카페 관리 클래스"""
    
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.menu = []
        self.orders = []
    
    def add_menu_item(self, name, price, category='커피'):
        item = format_menu_item(name, price, category)
        self.menu.append(item)
        return item
    
    def get_daily_sales(self):
        return sum(calculate_total(order['items']) for order in self.orders)

# 모듈 레벨 변수
cafe_locations = ['강남', '홍대', '명동', '건대', '신촌']

# 실행 시점 확인
if __name__ == '__main__':
    # 이 부분은 모듈이 직접 실행될 때만 실행됩니다
    print("카페 유틸리티 모듈 테스트")
    test_cafe = CafeManager("테스트 카페", "강남")
    test_cafe.add_menu_item("아메리카노", 4500)
    print(f"메뉴: {test_cafe.menu}")
