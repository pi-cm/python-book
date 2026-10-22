"""1권 Chapter 17: 표준 라이브러리 핵심 가이드 — 컬렉션과 반복

원고: manuscript/chapters/17-standard-library-guide.md (676줄부터)
"""

# ---- 원고 676줄 ----
from collections import Counter, defaultdict, deque, namedtuple, OrderedDict

# 한글 텍스트 단어 빈도 분석
korean_text = """
파이썬은 강력한 프로그래밍 언어입니다. 
파이썬을 배우면 웹 개발, 데이터 분석, 인공지능 등 
다양한 분야에서 파이썬을 활용할 수 있습니다.
파이썬의 문법은 간단하고 직관적입니다.
"""

words = korean_text.replace('\n', ' ').replace(',', '').split()
word_count = Counter(words)

print("단어 빈도수:")
for word, count in word_count.most_common(5):
    print(f"'{word}': {count}번")

# 학생 성적 관리
Student = namedtuple('Student', ['이름', '국어', '영어', '수학'])

students = [
    Student('김철수', 85, 78, 92),
    Student('이영희', 92, 88, 84),
    Student('박민수', 78, 85, 90),
    Student('정수진', 88, 92, 87)
]

# 과목별 점수 그룹화
subject_scores = defaultdict(list)
for student in students:
    subject_scores['국어'].append(student.국어)
    subject_scores['영어'].append(student.영어)
    subject_scores['수학'].append(student.수학)

print("\n과목별 평균 점수:")
for subject, scores in subject_scores.items():
    avg = sum(scores) / len(scores)
    print(f"{subject}: {avg:.1f}점")

# 최근 접속 기록 관리 (deque 사용)
recent_logins = deque(maxlen=5)  # 최대 5개만 보관

login_records = [
    "김철수 - 09:15",
    "이영희 - 09:32", 
    "박민수 - 10:05",
    "정수진 - 10:18",
    "최지영 - 10:45",
    "한민수 - 11:02"  # 이 시점에서 김철수 기록 삭제됨
]

for record in login_records:
    recent_logins.append(record)

print("\n최근 접속 기록 (최대 5개):")
for login in recent_logins:
    print(f"- {login}")

# ---- 원고 749줄 ----
import itertools

# 한국 회사 부서와 직급 조합
departments = ['개발팀', '기획팀', '영업팀']
positions = ['사원', '대리', '과장']

# 모든 조합 생성
all_combinations = list(itertools.product(departments, positions))
print("부서-직급 조합:")
for dept, pos in all_combinations[:6]:  # 처음 6개만
    print(f"- {dept} {pos}")

# 한국 음식 메뉴 추천 (순환)
korean_foods = ['김치찌개', '된장찌개', '불고기', '비빔밥', '냉면']
food_cycle = itertools.cycle(korean_foods)

print("\n일주일 점심 메뉴:")
for day, food in zip(['월', '화', '수', '목', '금'], food_cycle):
    print(f"{day}요일: {food}")

# 피보나치 수열 생성기 (itertools 활용)
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# 처음 10개 피보나치 수
fib_numbers = list(itertools.islice(fibonacci(), 10))
print(f"\n피보나치 수열: {fib_numbers}")

# 한국어 단어 조합 생성
syllables = ['안', '녕', '하', '세', '요']
combinations = list(itertools.combinations(syllables, 2))
print(f"\n음절 2개 조합: {combinations[:5]}")
