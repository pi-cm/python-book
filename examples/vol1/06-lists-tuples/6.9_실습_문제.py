"""1권 Chapter 6: 리스트와 튜플 — 6.9 실습 문제

원고: manuscript/chapters/06-lists-tuples.md (851줄부터)
"""

# ---- 원고 851줄 ----
# 1번: 한국 도시 리스트 조작
cities = ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]
# 문제: 인구 순으로 도시를 정렬하고, 상위 3개 도시만 남기세요
# 답:
population_order = ["서울", "부산", "인천", "대구", "대전"]
top3_cities = [city for city in population_order if city in cities][:3]
print(f"상위 3개 도시: {top3_cities}")

# 2번: 학생 점수 튜플 처리
student_scores = ("김철수", 85, 92, 78, 88, 90)
# 문제: 이름과 점수들을 분리하고 평균을 계산하세요
# 답:
name, *scores = student_scores
average = sum(scores) / len(scores)
print(f"{name}의 평균: {average:.1f}점")

# 3번: 중복 제거와 정렬
korean_foods = ["김치", "불고기", "김치", "비빔밥", "불고기", "떡볶이", "김치"]
# 문제: 중복을 제거하고 가나다순으로 정렬하세요
# 답:
unique_foods = list(set(korean_foods))
unique_foods.sort()
print(f"정렬된 음식: {unique_foods}")

# 4번: 리스트 컴프리헨션 활용
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# 문제: 짝수의 제곱만 구하세요
# 답:
even_squares = [n**2 for n in numbers if n % 2 == 0]
print(f"짝수의 제곱: {even_squares}")

# 5번: 튜플 언패킹
coordinates = [(37.5665, 126.9780), (35.1796, 129.0756), (35.8714, 128.6014)]
# 문제: 각 좌표의 위도와 경도를 따로 리스트로 만드세요
# 답:
latitudes = [lat for lat, lng in coordinates]
longitudes = [lng for lat, lng in coordinates]
print(f"위도: {latitudes}")
print(f"경도: {longitudes}")

# ---- 원고 895줄 ----
# 6번: 중첩 리스트 처리
class_scores = [
    ["김철수", [85, 92, 78]],
    ["이영희", [95, 87, 91]],
    ["박민수", [78, 95, 85]]
]
# 문제: 각 학생의 이름과 평균 점수로 구성된 리스트를 만드세요
# 답:
student_averages = [(name, sum(scores)/len(scores)) for name, scores in class_scores]
print(f"학생별 평균: {student_averages}")

# 7번: namedtuple 활용
from collections import namedtuple
Book = namedtuple('Book', ['title', 'author', 'year', 'pages'])

books = [
    Book("파이썬 프로그래밍", "김철수", 2023, 350),
    Book("웹 개발 기초", "이영희", 2022, 280),
    Book("데이터 과학", "박민수", 2023, 420)
]
# 문제: 2023년에 출간된 책의 제목을 리스트로 만드세요
# 답:
books_2023 = [book.title for book in books if book.year == 2023]
print(f"2023년 출간 도서: {books_2023}")

# 8번: 리스트 슬라이싱 고급
korean_alphabet = list("가나다라마바사아자차카타파하")
# 문제: 홀수 번째 문자들만 뽑아서 역순으로 정렬하세요
# 답:
odd_chars = korean_alphabet[::2][::-1]
print(f"홀수번째 문자 역순: {odd_chars}")

# 9번: 복잡한 정렬
students_data = [
    ("김철수", 2, 3.7),
    ("이영희", 1, 3.9),
    ("박민수", 2, 3.5),
    ("최지영", 1, 4.0),
    ("정수진", 3, 3.8)
]
# 문제: 학년 우선, 같으면 GPA 높은 순으로 정렬하세요
# 답:
sorted_students = sorted(students_data, key=lambda x: (x[1], -x[2]))
print(f"정렬된 학생: {sorted_students}")

# 10번: 리스트 병합과 중복 처리
list1 = ["사과", "바나나", "오렌지"]
list2 = ["바나나", "포도", "딸기"]
list3 = ["오렌지", "키위", "망고"]
# 문제: 모든 리스트를 합치고 중복을 제거하되, 원래 순서를 보존하세요
# 답:
merged = []
for lst in [list1, list2, list3]:
    for item in lst:
        if item not in merged:
            merged.append(item)
print(f"순서 보존 병합: {merged}")

# ---- 원고 957줄 ----
# 11번: 행렬 연산
matrix1 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
matrix2 = [[9, 8, 7], [6, 5, 4], [3, 2, 1]]
# 문제: 두 행렬의 원소별 곱셈 결과를 구하세요
# 답:
result_matrix = [[matrix1[i][j] * matrix2[i][j] for j in range(len(matrix1[0]))] 
                 for i in range(len(matrix1))]
print(f"원소별 곱셈 결과: {result_matrix}")

# 12번: 데이터 그룹화
sales_data = [
    ("김철수", "서울", 1500000),
    ("이영희", "부산", 1200000),
    ("박민수", "서울", 1800000),
    ("최지영", "대구", 900000),
    ("정수진", "서울", 1400000),
]
# 문제: 지역별로 매출을 그룹화하고 총합을 계산하세요
# 답:
region_sales = {}
for name, region, sales in sales_data:
    if region not in region_sales:
        region_sales[region] = []
    region_sales[region].append(sales)

region_totals = {region: sum(sales) for region, sales in region_sales.items()}
print(f"지역별 총 매출: {region_totals}")

# 13번: 문자열 리스트 고급 처리
sentences = [
    "파이썬은 강력한 프로그래밍 언어입니다",
    "리스트와 튜플은 중요한 자료구조입니다", 
    "함수형 프로그래밍도 지원합니다"
]
# 문제: 각 문장에서 5글자 이상인 단어만 추출하세요
# 답:
long_words = []
for sentence in sentences:
    words = sentence.split()
    long_words.extend([word for word in words if len(word) >= 5])
print(f"5글자 이상 단어: {long_words}")

# 14번: 리스트 평탄화 (Flattening)
nested_list = [[1, 2, [3, 4]], [5, [6, 7, [8, 9]]], [10]]
# 문제: 중첩된 리스트를 완전히 평탄화하세요
# 답:
def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

flattened = flatten(nested_list)
print(f"평탄화된 리스트: {flattened}")

# 15번: 복합 데이터 구조 분석
company_data = [
    {
        "부서": "개발팀",
        "직원": [
            ("김철수", "시니어", 5500),
            ("이영희", "주니어", 3500),
            ("박민수", "시니어", 6000)
        ]
    },
    {
        "부서": "마케팅팀", 
        "직원": [
            ("최지영", "매니저", 7500),
            ("정수진", "주니어", 3000)
        ]
    }
]
# 문제: 부서별 평균 연봉을 계산하고, 가장 높은 부서를 찾으세요
# 답:
dept_averages = {}
for dept_info in company_data:
    dept_name = dept_info["부서"]
    salaries = [salary for _, _, salary in dept_info["직원"]]
    dept_averages[dept_name] = sum(salaries) / len(salaries)

highest_avg_dept = max(dept_averages.items(), key=lambda x: x[1])
print(f"부서별 평균 연봉: {dept_averages}")
print(f"평균 연봉이 가장 높은 부서: {highest_avg_dept[0]} ({highest_avg_dept[1]:.0f}만원)")
