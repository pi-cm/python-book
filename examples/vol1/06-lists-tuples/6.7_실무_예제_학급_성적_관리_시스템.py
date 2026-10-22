"""1권 Chapter 6: 리스트와 튜플 — 6.7 실무 예제: 학급 성적 관리 시스템

원고: manuscript/chapters/06-lists-tuples.md (556줄부터)
"""

# ---- 원고 556줄 ----
from collections import namedtuple
from statistics import mean, median

# 학생 정보 구조 정의
Student = namedtuple('Student', ['name', 'student_id', 'grade'])
Subject = namedtuple('Subject', ['name', 'credits'])

# 학생들과 과목 정의
students = [
    Student("김철수", "2023001", 2),
    Student("이영희", "2023002", 2),
    Student("박민수", "2023003", 2),
    Student("최지영", "2023004", 2),
    Student("정수진", "2023005", 2),
]

subjects = [
    Subject("국어", 3),
    Subject("영어", 3),
    Subject("수학", 4),
    Subject("과학", 3),
    Subject("사회", 2),
]

# 성적 데이터 (학생별 과목별 점수)
scores = {
    "김철수": {"국어": 85, "영어": 78, "수학": 92, "과학": 88, "사회": 90},
    "이영희": {"국어": 92, "영어": 95, "수학": 87, "과학": 91, "사회": 89},
    "박민수": {"국어": 78, "영어": 82, "수학": 95, "과학": 85, "사회": 83},
    "최지영": {"국어": 88, "영어": 87, "수학": 89, "과학": 93, "사회": 91},
    "정수진": {"국어": 94, "영어": 89, "수학": 86, "과학": 87, "사회": 92},
}

# ---- 원고 595줄 ----
def calculate_student_average(student_name, scores_dict):
    """개별 학생의 평균 계산"""
    student_scores = list(scores_dict[student_name].values())
    return mean(student_scores)

def calculate_subject_statistics(subject_name, scores_dict):
    """과목별 통계 계산"""
    subject_scores = [scores[subject_name] for scores in scores_dict.values()]
    return {
        "평균": mean(subject_scores),
        "중앙값": median(subject_scores),
        "최고점": max(subject_scores),
        "최저점": min(subject_scores),
        "표준편차": round((sum((x - mean(subject_scores))**2 for x in subject_scores) / len(subject_scores))**0.5, 2)
    }

def get_top_students(scores_dict, n=3):
    """상위 n명 학생 반환"""
    averages = [(name, calculate_student_average(name, scores_dict)) 
                for name in scores_dict.keys()]
    averages.sort(key=lambda x: x[1], reverse=True)
    return averages[:n]

def get_subject_rankings(subject_name, scores_dict):
    """특정 과목 순위 계산"""
    subject_scores = [(name, scores[subject_name]) 
                     for name, scores in scores_dict.items()]
    subject_scores.sort(key=lambda x: x[1], reverse=True)
    return subject_scores

# ---- 원고 631줄 ----
def generate_class_report(students, subjects, scores):
    """학급 종합 보고서 생성"""
    print("=" * 50)
    print("학급 성적 종합 보고서")
    print("=" * 50)
    
    # 학생별 평균 성적
    print("\n학생별 평균 성적:")
    print("-" * 30)
    for student in students:
        avg = calculate_student_average(student.name, scores)
        grade_letter = get_grade_letter(avg)
        print(f"{student.name:6} ({student.student_id}): {avg:5.1f}점 ({grade_letter})")
    
    # 과목별 통계
    print("\n과목별 통계:")
    print("-" * 50)
    for subject in subjects:
        stats = calculate_subject_statistics(subject.name, scores)
        print(f"\n{subject.name} (학점: {subject.credits})")
        print(f"  평균: {stats['평균']:5.1f}점")
        print(f"  중앙값: {stats['중앙값']:5.1f}점")
        print(f"  최고점: {stats['최고점']}점")
        print(f"  최저점: {stats['최저점']}점")
        print(f"  표준편차: {stats['표준편차']}")
    
    # 상위 3명 학생
    print("\n상위 3명 학생:")
    print("-" * 25)
    top_students = get_top_students(scores, 3)
    for rank, (name, avg) in enumerate(top_students, 1):
        print(f"{rank}등: {name} ({avg:.1f}점)")
    
    # 각 과목별 1등
    print("\n과목별 1등:")
    print("-" * 25)
    for subject in subjects:
        rankings = get_subject_rankings(subject.name, scores)
        winner_name, winner_score = rankings[0]
        print(f"{subject.name}: {winner_name} ({winner_score}점)")

def get_grade_letter(score):
    """숫자 점수를 등급으로 변환"""
    if score >= 95:
        return "A+"
    elif score >= 90:
        return "A"
    elif score >= 85:
        return "B+"
    elif score >= 80:
        return "B"
    elif score >= 75:
        return "C+"
    elif score >= 70:
        return "C"
    else:
        return "F"

# 보고서 생성 실행
generate_class_report(students, subjects, scores)

# ---- 원고 700줄 ----
def add_new_student(students_list, scores_dict, name, student_id, grade):
    """새 학생 추가"""
    new_student = Student(name, student_id, grade)
    students_list.append(new_student)
    scores_dict[name] = {}
    print(f"[O] {name} 학생이 추가되었습니다.")

def update_score(scores_dict, student_name, subject_name, new_score):
    """점수 수정"""
    if student_name in scores_dict:
        old_score = scores_dict[student_name].get(subject_name, "없음")
        scores_dict[student_name][subject_name] = new_score
        print(f"[O] {student_name}의 {subject_name} 점수가 {old_score} → {new_score}로 변경되었습니다.")
    else:
        print(f"[X] {student_name} 학생을 찾을 수 없습니다.")

def batch_input_scores(scores_dict, student_name, subject_scores):
    """한 학생의 모든 점수 일괄 입력"""
    if student_name not in scores_dict:
        scores_dict[student_name] = {}
    
    for subject, score in subject_scores.items():
        scores_dict[student_name][subject] = score
    
    print(f"[O] {student_name}의 성적이 일괄 입력되었습니다.")

# 사용 예제
print("\n" + "="*50)
print("성적 관리 기능 테스트")
print("="*50)

# 새 학생 추가
add_new_student(students, scores, "한미영", "2023006", 2)

# 점수 수정
update_score(scores, "김철수", "수학", 94)

# 일괄 점수 입력
new_scores = {"국어": 87, "영어": 91, "수학": 89, "과학": 85, "사회": 88}
batch_input_scores(scores, "한미영", new_scores)

# 수정된 보고서 확인
print(f"\n현재 학생 수: {len(students)}명")
print(f"한미영 평균: {calculate_student_average('한미영', scores):.1f}점")
