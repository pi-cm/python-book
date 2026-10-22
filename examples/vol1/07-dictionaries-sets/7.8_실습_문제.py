"""1권 Chapter 7: 딕셔너리와 집합 — 7.8 실습 문제

원고: manuscript/chapters/07-dictionaries-sets.md (849줄부터)
"""

# ---- 원고 849줄 ----
# 1번: 한국 도시별 인구 딕셔너리 조작
cities_population = {
    "서울": 9720846, "부산": 3448737, "대구": 2438031,
    "인천": 2963991, "광주": 1441970, "대전": 1475221
}
# 문제: 인구가 300만 이상인 도시만 필터링하세요
# 답:
major_cities = {city: pop for city, pop in cities_population.items() if pop >= 3000000}
print(f"대도시: {major_cities}")

# 2번: 학생 성적 딕셔너리 처리
student_scores = {
    "김철수": [85, 92, 78, 88],
    "이영희": [95, 87, 91, 89],
    "박민수": [78, 95, 85, 92]
}
# 문제: 각 학생의 평균 점수를 계산하세요
# 답:
averages = {name: sum(scores)/len(scores) for name, scores in student_scores.items()}
print(f"평균 점수: {averages}")

# 3번: 집합 연산 활용
group_a = {"김철수", "이영희", "박민수", "최지영"}
group_b = {"이영희", "박민수", "정수진", "한미영"}
# 문제: 두 그룹 모두에 속한 사람과 한 그룹에만 속한 사람을 찾으세요
# 답:
both_groups = group_a & group_b
only_one_group = group_a ^ group_b
print(f"두 그룹 모두: {both_groups}")
print(f"한 그룹만: {only_one_group}")

# 4번: 문자 빈도 계산
text = "안녕하세요 파이썬 프로그래밍을 배워봅시다"
# 문제: 각 문자의 빈도를 딕셔너리로 만드세요 (공백 제외)
# 답:
char_freq = {}
for char in text.replace(' ', ''):
    char_freq[char] = char_freq.get(char, 0) + 1
print(f"문자 빈도: {char_freq}")

# 5번: 딕셔너리 병합
dict1 = {"a": 1, "b": 2, "c": 3}
dict2 = {"b": 4, "c": 5, "d": 6}
# 문제: 두 딕셔너리를 병합하되 dict2의 값을 우선하세요
# 답:
merged = {**dict1, **dict2}
print(f"병합 결과: {merged}")

# ---- 원고 901줄 ----
# 6번: 중첩 딕셔너리 처리
company = {
    "개발팀": {
        "김철수": {"직급": "시니어", "연봉": 6000},
        "이영희": {"직급": "주니어", "연봉": 4000}
    },
    "마케팅팀": {
        "박민수": {"직급": "매니저", "연봉": 7000},
        "최지영": {"직급": "사원", "연봉": 3500}
    }
}
# 문제: 부서별 평균 연봉을 계산하세요
# 답:
dept_averages = {}
for dept, employees in company.items():
    salaries = [emp["연봉"] for emp in employees.values()]
    dept_averages[dept] = sum(salaries) / len(salaries)
print(f"부서별 평균 연봉: {dept_averages}")

# 7번: defaultdict 활용
from collections import defaultdict

transactions = [
    ("김철수", "식료품", 15000),
    ("김철수", "교통", 5000),
    ("이영희", "식료품", 20000),
    ("이영희", "문화", 12000),
    ("김철수", "식료품", 8000)
]
# 문제: 사람별 카테고리별 지출 총액을 계산하세요
# 답:
expenses = defaultdict(lambda: defaultdict(int))
for name, category, amount in transactions:
    expenses[name][category] += amount

for name, categories in expenses.items():
    print(f"{name}: {dict(categories)}")

# 8번: Counter 활용
from collections import Counter

korean_text = "가나다라마바사아자차카타파하 가나다 가나 가"
# 문제: 가장 자주 나타나는 문자 3개를 찾으세요
# 답:
char_counter = Counter(korean_text.replace(' ', ''))
most_common = char_counter.most_common(3)
print(f"가장 빈번한 문자 3개: {most_common}")

# 9번: 집합으로 중복 제거와 교집합
sales_2022 = {"사과", "바나나", "오렌지", "포도", "딸기"}
sales_2023 = {"바나나", "오렌지", "키위", "망고", "딸기"}
# 문제: 두 해 연속 판매된 상품, 2023년에 판매가 끝난 상품, 2023년 신상품을 찾으세요
# 답:
continuous_products = sales_2022 & sales_2023
discontinued_2023 = sales_2022 - sales_2023
new_2023 = sales_2023 - sales_2022
print(f"연속 판매: {continuous_products}")
print(f"2023 판매 종료: {discontinued_2023}")
print(f"2023 신상품: {new_2023}")

# 10번: 딕셔너리 컴프리헨션 고급
students = ["김철수", "이영희", "박민수", "최지영", "정수진"]
scores = [85, 92, 78, 88, 95]
# 문제: 점수가 80점 이상인 학생들의 등급(A/B)을 딕셔너리로 만드세요
# 답:
student_grades = {
    student: "A" if score >= 90 else "B"
    for student, score in zip(students, scores)
    if score >= 80
}
print(f"80점 이상 학생 등급: {student_grades}")

# ---- 원고 977줄 ----
from collections import defaultdict

# 11번: 복잡한 데이터 구조 변환
raw_data = [
    {"name": "김철수", "dept": "개발", "skills": ["Python", "Java"]},
    {"name": "이영희", "dept": "개발", "skills": ["JavaScript", "Python"]},
    {"name": "박민수", "dept": "마케팅", "skills": ["Excel", "PowerPoint"]},
    {"name": "최지영", "dept": "개발", "skills": ["Java", "C++"]}
]
# 문제: 부서별로 보유 기술과 해당 기술을 가진 사람 수를 계산하세요
# 답:
dept_skills = defaultdict(lambda: defaultdict(int))
for person in raw_data:
    dept = person["dept"]
    for skill in person["skills"]:
        dept_skills[dept][skill] += 1

for dept, skills in dept_skills.items():
    print(f"{dept}: {dict(skills)}")

# 12번: 그래프 표현과 탐색
# 한국 주요 도시 간 연결 관계
city_connections = {
    "서울": {"인천", "수원", "춘천"},
    "인천": {"서울", "수원"},
    "수원": {"서울", "인천", "대전"},
    "대전": {"수원", "대구", "광주"},
    "대구": {"대전", "부산"},
    "부산": {"대구"},
    "광주": {"대전"},
    "춘천": {"서울"}
}
# 문제: 서울에서 시작해서 2단계 이내로 갈 수 있는 모든 도시를 찾으세요
# 답:
start_city = "서울"
reachable_1 = city_connections[start_city]
reachable_2 = set()

for city in reachable_1:
    reachable_2.update(city_connections[city])

all_reachable = reachable_1 | reachable_2
all_reachable.discard(start_city)  # 시작 도시 제외
print(f"서울에서 2단계 이내 도시: {all_reachable}")

# 13번: 역인덱스 구축
documents = {
    "doc1": "파이썬은 강력한 프로그래밍 언어입니다",
    "doc2": "자바는 객체지향 프로그래밍 언어입니다", 
    "doc3": "파이썬과 자바는 인기 있는 언어입니다"
}
# 문제: 단어별로 어떤 문서에 등장하는지 역인덱스를 만드세요
# 답:
inverse_index = defaultdict(set)
for doc_id, content in documents.items():
    words = content.split()
    for word in words:
        inverse_index[word].add(doc_id)

# 특정 단어 검색
search_word = "프로그래밍"
found_docs = inverse_index.get(search_word, set())
print(f"'{search_word}' 포함 문서: {found_docs}")

# 14번: 캐시 구현
class LRUCache:
    """LRU(Least Recently Used) 캐시 구현"""
    
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.access_order = []
    
    def get(self, key):
        if key in self.cache:
            # 접근 순서 업데이트
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            # 기존 키 업데이트
            self.cache[key] = value
            self.access_order.remove(key)
            self.access_order.append(key)
        else:
            # 새 키 추가
            if len(self.cache) >= self.capacity:
                # 가장 오래된 항목 제거
                oldest = self.access_order.pop(0)
                del self.cache[oldest]
            
            self.cache[key] = value
            self.access_order.append(key)

# LRU 캐시 테스트
cache = LRUCache(3)
cache.put("한국어", "Korean")
cache.put("영어", "English") 
cache.put("중국어", "Chinese")
print(f"캐시 상태: {cache.cache}")

cache.put("일본어", "Japanese")  # 한국어가 제거됨
print(f"일본어 추가 후: {cache.cache}")

# 15번: 복잡한 집계 연산
sales_data = [
    {"region": "서울", "product": "노트북", "sales": 150, "month": "2023-01"},
    {"region": "서울", "product": "마우스", "sales": 300, "month": "2023-01"},
    {"region": "부산", "product": "노트북", "sales": 100, "month": "2023-01"},
    {"region": "서울", "product": "노트북", "sales": 200, "month": "2023-02"},
    {"region": "부산", "product": "마우스", "sales": 250, "month": "2023-02"},
]
# 문제: 지역별, 제품별, 월별 매출을 다차원으로 집계하세요
# 답:
multi_dim_sales = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

for record in sales_data:
    region = record["region"]
    product = record["product"]  
    month = record["month"]
    sales = record["sales"]
    
    multi_dim_sales[region][product][month] += sales

# 결과 출력
for region, products in multi_dim_sales.items():
    print(f"\n{region} 지역:")
    for product, months in products.items():
        print(f"  {product}: {dict(months)}")
        
# 총합 계산
region_totals = {}
for region, products in multi_dim_sales.items():
    total = sum(
        sales 
        for product_data in products.values()
        for sales in product_data.values()
    )
    region_totals[region] = total

print(f"\n지역별 총 매출: {region_totals}")
