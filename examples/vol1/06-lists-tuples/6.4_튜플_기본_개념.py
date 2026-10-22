"""1권 Chapter 6: 리스트와 튜플 — 6.4 튜플 기본 개념

원고: manuscript/chapters/06-lists-tuples.md (313줄부터)
"""

# ---- 원고 313줄 ----
# 기본 튜플 생성
coordinates = (37.5665, 126.9780)  # 서울 좌표
person = ("김철수", 25, "서울시 강남구")
colors = "빨강", "파랑", "노랑"  # 괄호 생략 가능

# 단일 요소 튜플 (쉼표 필수!)
single = (42,)
single2 = 42,

# 빈 튜플
empty = ()
empty2 = tuple()

print(f"좌표: {coordinates}")
print(f"개인정보: {person}")
print(f"색상들: {colors}")
print(f"단일 요소: {single}, {single2}")

# ---- 원고 346줄 ----
# 기본 언패킹
point = (10, 20)
x, y = point
print(f"x={x}, y={y}")

# 여러 값 언패킹
student = ("박영수", 20, "컴퓨터과학과", 3.8)
name, age, major, gpa = student
print(f"{name}({age}세) - {major}, GPA: {gpa}")

# 부분 언패킹 (Python 3.0+)
scores = (95, 87, 92, 78, 88)
first, second, *rest = scores
print(f"1등: {first}, 2등: {second}, 나머지: {rest}")

# 중간 값 무시
data = ("김철수", 25, "서울", "개발자", 5000)
name, age, *_, salary = data
print(f"{name}({age}세) 연봉: {salary}만원")

# ---- 원고 374줄 ----
def get_student_info():
    """학생 정보를 튜플로 반환"""
    return "이영희", 22, "경영학과", 3.9

def calculate_stats(scores):
    """점수 통계를 튜플로 반환"""
    return min(scores), max(scores), sum(scores) / len(scores)

# 함수에서 튜플 반환 받기
student_info = get_student_info()
name, age, major, gpa = get_student_info()  # 직접 언패킹
print(f"학생: {name}, 전공: {major}")

# 통계 계산
test_scores = [85, 92, 78, 96, 87]
min_score, max_score, avg_score = calculate_stats(test_scores)
print(f"최저: {min_score}, 최고: {max_score}, 평균: {avg_score:.1f}")
