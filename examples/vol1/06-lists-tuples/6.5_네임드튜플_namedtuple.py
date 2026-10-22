"""1권 Chapter 6: 리스트와 튜플 — 6.5 네임드튜플 (namedtuple)

원고: manuscript/chapters/06-lists-tuples.md (404줄부터)
"""

# ---- 원고 404줄 ----
from collections import namedtuple

# 학생 정보 namedtuple 정의
Student = namedtuple('Student', ['name', 'age', 'major', 'gpa'])

# 인스턴스 생성
student1 = Student("김철수", 21, "컴퓨터과학과", 3.7)
student2 = Student(name="이영희", age=20, major="경영학과", gpa=3.9)

print(f"학생1: {student1.name}, 전공: {student1.major}")
print(f"학생2: {student2}")

# 튜플처럼 인덱싱도 가능
print(f"첫 번째 필드: {student1[0]}")

# 딕셔너리 변환
student_dict = student1._asdict()
print(f"딕셔너리 형태: {student_dict}")

# ---- 원고 431줄 ----
from collections import namedtuple

# 좌표 시스템
Point = namedtuple('Point', ['x', 'y'])
Rectangle = namedtuple('Rectangle', ['top_left', 'bottom_right'])

# 서울시 주요 지역 좌표
seoul_districts = [
    Point(37.5665, 126.9780),  # 중구 (명동)
    Point(37.5172, 127.0473),  # 강남구 (강남역)
    Point(37.5512, 126.9882),  # 마포구 (홍대)
]

for i, point in enumerate(seoul_districts, 1):
    print(f"지역 {i}: 위도 {point.x}, 경도 {point.y}")

# 제품 정보 관리
Product = namedtuple('Product', ['name', 'price', 'category', 'stock'])

products = [
    Product("삼성 갤럭시", 900000, "전자제품", 50),
    Product("나이키 운동화", 120000, "의류", 30),
    Product("스타벅스 텀블러", 25000, "생활용품", 100),
]

# 카테고리별 분류
electronics = [p for p in products if p.category == "전자제품"]
print(f"전자제품: {electronics}")

# 가격순 정렬
sorted_products = sorted(products, key=lambda p: p.price)
print(f"가격순: {[p.name for p in sorted_products]}")
