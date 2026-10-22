"""1권 Chapter 4. 조건문과 분기 — 4.2 match-case 구문 완전 마스터 (Python 3.10+)

원고: manuscript/chapters/04-control-flow.md (263줄부터)
"""

# ---- 원고 263줄 ----
# 기본 패턴 매칭
def 요일_처리(요일):
    match 요일:
        case "월요일":
            return "새로운 한 주의 시작!"
        case "화요일":
            return "월요일보다는 낫네요"
        case "수요일":
            return "주 중반입니다"
        case "목요일":
            return "거의 다 왔어요"
        case "금요일":
            return "TGIF! 불금입니다"
        case "토요일" | "일요일":  # OR 패턴
            return "주말입니다!"
        case _:  # 와일드카드 (모든 경우)
            return "유효하지 않은 요일입니다"

# 가드 조건이 있는 매칭
def 학생_성적_처리(점수):
    match 점수:
        case score if not isinstance(score, (int, float)) or not 0 <= score <= 100:
            return "잘못된 점수입니다"
        case score if score >= 95:
            return "A+ 우수상 수상!"
        case score if 90 <= score < 95:
            return "A 학점"
        case score if 80 <= score < 90:
            return "B 학점"  
        case score if 70 <= score < 80:
            return "C 학점"
        case score if 60 <= score < 70:
            return "D 학점"
        case _:
            return "F 학점 - 재수강 필요"

print(학생_성적_처리(97))     # A+ 우수상 수상!
print(학생_성적_처리(85))     # B 학점
print(학생_성적_처리(94.5))   # A 학점
print(학생_성적_처리("abc"))  # 잘못된 점수입니다

# ---- 원고 308줄 ----
for n in range(1, 16):
    match (n % 3, n % 5):
        case (0, 0):
            print("FizzBuzz")
        case (0, _):
            print("Fizz")
        case (_, 0):
            print("Buzz")
        case _:
            print(n)

# ---- 원고 331줄 ----
# 1. 리스트/튜플 패턴 매칭
def 리스트_분석(데이터):
    match 데이터:
        case []:
            return "빈 리스트"
        case [x]:
            return f"단일 원소: {x}"
        case [x, y]:
            return f"두 원소: {x}, {y}"
        case [x, y, z]:
            return f"세 원소: {x}, {y}, {z}"
        case [첫번째, *중간, 마지막]:
            return f"첫번째: {첫번째}, 중간: {중간}, 마지막: {마지막}"
        case _:
            return "기타 형태"

print(리스트_분석([]))           # 빈 리스트
print(리스트_분석([1]))          # 단일 원소: 1
print(리스트_분석([1, 2]))       # 두 원소: 1, 2
print(리스트_분석([1, 2, 3, 4, 5]))  # 첫번째: 1, 중간: [2, 3, 4], 마지막: 5

# 2. 딕셔너리 패턴 매칭
def 사용자_처리(사용자_정보):
    match 사용자_정보:
        case {"type": "admin", "name": name}:
            return f"관리자 {name}님 환영합니다"
        case {"type": "user", "name": name, "age": age} if age >= 18:
            return f"성인 사용자 {name}님 ({age}세)"
        case {"type": "user", "name": name, "age": age}:
            return f"미성년 사용자 {name}님 ({age}세)"
        case {"type": "guest"}:
            return "게스트 사용자입니다"
        case {"error": message}:
            return f"오류: {message}"
        case _:
            return "알 수 없는 사용자 정보"

# 테스트
users = [
    {"type": "admin", "name": "김관리자"},
    {"type": "user", "name": "이철수", "age": 25},
    {"type": "user", "name": "박미성", "age": 16},
    {"type": "guest"},
    {"error": "인증 실패"},
    {"invalid": "data"}
]

for user in users:
    print(사용자_처리(user))

# 3. 클래스 인스턴스 패턴 매칭
from dataclasses import dataclass
from typing import Union

@dataclass
class 점:
    x: int
    y: int

@dataclass  
class 원:
    중심: 점
    반지름: int

@dataclass
class 사각형:
    왼쪽위: 점
    너비: int
    높이: int

def 도형_분석(도형: Union[점, 원, 사각형]):
    match 도형:
        case 점(x=0, y=0):
            return "원점입니다"
        case 점(x=x, y=y) if x == y:
            return f"대각선 위의 점 ({x}, {y})"
        case 점(x=x, y=y):
            return f"점 ({x}, {y})"
        case 원(중심=점(x=0, y=0), 반지름=r):
            return f"원점 중심의 원 (반지름: {r})"
        case 원(중심=center, 반지름=r):
            return f"원 (중심: ({center.x}, {center.y}), 반지름: {r})"
        case 사각형(왼쪽위=점(x=x, y=y), 너비=w, 높이=h) if w == h:
            return f"정사각형 ({x}, {y})에서 시작, 크기: {w}"
        case 사각형(왼쪽위=점(x=x, y=y), 너비=w, 높이=h):
            return f"직사각형 ({x}, {y})에서 시작, 크기: {w}×{h}"
        case _:
            return "알 수 없는 도형"

# 도형 테스트
도형들 = [
    점(0, 0),
    점(3, 3), 
    점(1, 2),
    원(점(0, 0), 5),
    원(점(2, 3), 7),
    사각형(점(1, 1), 5, 5),
    사각형(점(0, 0), 3, 4)
]

for 도형 in 도형들:
    print(f"{도형} → {도형_분석(도형)}")

# ---- 원고 442줄 ----
# 한국 주민등록번호 분석기
def 주민번호_분석(주민번호: str):
    """주민등록번호를 분석하여 정보 추출"""
    if len(주민번호) != 14 or 주민번호[6] != '-':
        return "잘못된 주민등록번호 형식"
    
    앞자리 = 주민번호[:6]
    뒷자리 = 주민번호[7:]
    
    if not (앞자리.isdigit() and 뒷자리.isdigit()):
        return "주민등록번호는 숫자로만 구성되어야 합니다"
    
    # 생년월일 추출
    년도 = int(앞자리[:2])
    월 = int(앞자리[2:4])
    일 = int(앞자리[4:6])
    
    # 성별 코드
    성별코드 = int(뒷자리[0])
    
    match 성별코드:
        case 1 | 2:
            # 1900년대 출생
            전체년도 = 1900 + 년도
            성별 = "남성" if 성별코드 == 1 else "여성"
        case 3 | 4:
            # 2000년대 출생  
            전체년도 = 2000 + 년도
            성별 = "남성" if 성별코드 == 3 else "여성"
        case 5 | 6:
            # 1900년대 출생 외국인
            전체년도 = 1900 + 년도
            성별 = "남성 외국인" if 성별코드 == 5 else "여성 외국인"
        case 7 | 8:
            # 2000년대 출생 외국인
            전체년도 = 2000 + 년도
            성별 = "남성 외국인" if 성별코드 == 7 else "여성 외국인"
        case _:
            return "유효하지 않은 성별 코드"
    
    # 현재 나이 계산
    from datetime import date
    오늘 = date.today()
    나이 = 오늘.year - 전체년도
    
    # 생일이 지났는지 확인
    if (오늘.month, 오늘.day) < (월, 일):
        나이 -= 1
    
    return {
        "생년월일": f"{전체년도}년 {월}월 {일}일",
        "성별": 성별,
        "나이": 나이,
        "연령대": f"{(나이//10)*10}대"
    }

# 테스트
주민번호_예제들 = [
    "900101-1234567",  # 1990년 남성
    "051215-4345678",  # 2005년 여성
    "800303-5456789",  # 1980년 남성 외국인
    "123456-789012",   # 잘못된 형식
]

for 번호 in 주민번호_예제들:
    결과 = 주민번호_분석(번호)
    print(f"{번호} → {결과}")
