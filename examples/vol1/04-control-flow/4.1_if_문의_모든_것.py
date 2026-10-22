"""1권 Chapter 4. 조건문과 분기 — 4.1 if 문의 모든 것

원고: manuscript/chapters/04-control-flow.md (37줄부터)
"""

# ---- 원고 37줄 ----
# 기본 if 문
나이 = 20

if 나이 >= 18:
    print("성인입니다.")
    print("투표권이 있습니다.")

# if-else 문
점수 = 85

if 점수 >= 60:
    print("합격입니다!")
else:
    print("불합격입니다.")

# if-elif-else 문 (한국형 학점 시스템)
점수 = 92

if 점수 >= 95:
    학점 = "A+"
elif 점수 >= 90:
    학점 = "A"
elif 점수 >= 85:
    학점 = "B+"
elif 점수 >= 80:
    학점 = "B"
elif 점수 >= 75:
    학점 = "C+"
elif 점수 >= 70:
    학점 = "C"
elif 점수 >= 65:
    학점 = "D+"
elif 점수 >= 60:
    학점 = "D"
else:
    학점 = "F"

print(f"점수 {점수}점은 {학점} 학점입니다.")

# ---- 원고 97줄 ----
# 1. 숫자 범위 검사
def 연령대_분류(나이):
    if 0 <= 나이 < 13:
        return "아동"
    elif 13 <= 나이 < 20:
        return "청소년"
    elif 20 <= 나이 < 65:
        return "성인"
    elif 나이 >= 65:
        return "노인"
    else:
        return "유효하지 않은 나이"

# 연쇄 비교 활용
나이 = 25
if 20 <= 나이 <= 30:  # 파이썬의 강력한 연쇄 비교
    print("20대입니다")

# 2. 문자열 조건 검사
이름 = "김철수"

if 이름.startswith("김"):
    print("김씨 성을 가지고 있습니다")

if "철" in 이름:
    print("이름에 '철'자가 들어있습니다")

if len(이름) >= 3:
    print("이름이 3글자 이상입니다")

# 3. 컨테이너 조건 검사
과일_바구니 = ["사과", "바나나", "오렌지"]

if 과일_바구니:  # 비어있지 않으면 True
    print(f"과일이 {len(과일_바구니)}개 있습니다")

if "사과" in 과일_바구니:
    print("사과가 있습니다")

빈_리스트 = []
if not 빈_리스트:  # 비어있으면 True
    print("리스트가 비어있습니다")

# 4. None 체크 패턴
사용자_입력 = None

if 사용자_입력 is None:
    print("입력값이 없습니다")

# is vs == 차이
a = None
b = None
print(f"a is b: {a is b}")      # True (같은 None 객체)
print(f"a == b: {a == b}")      # True (값이 같음)

# 5. 타입 체크
def 안전한_나눗셈(a, b):
    if not isinstance(a, (int, float)):
        return "첫 번째 인수는 숫자여야 합니다"
    
    if not isinstance(b, (int, float)):
        return "두 번째 인수는 숫자여야 합니다"
    
    if b == 0:
        return "0으로 나눌 수 없습니다"
    
    return a / b

print(안전한_나눗셈(10, 2))    # 5.0
print(안전한_나눗셈(10, 0))    # 0으로 나눌 수 없습니다
print(안전한_나눗셈("10", 2))  # 첫 번째 인수는 숫자여야 합니다

# ---- 원고 177줄 ----
점수 = 0

if 점수:
    print("점수가 있습니다")
else:
    print("점수가 없습니다")       # 이쪽이 실행된다

if 점수 is not None:
    print("점수가 입력되었습니다")  # 이쪽도 실행된다

# ---- 원고 195줄 ----
# 단축 평가 (Short-circuit evaluation) 활용
def 안전한_접근():
    데이터 = None
    
    # 잘못된 방법 - AttributeError 발생 가능
    # if 데이터.length > 0:  # 오류!
    
    # 올바른 방법 - 단축 평가 활용
    if 데이터 and len(데이터) > 0:
        print("데이터가 있습니다")
    else:
        print("데이터가 없습니다")

# 실용적인 단축 평가 패턴
def 사용자_정보_출력(사용자):
    # 모든 조건을 안전하게 체크
    if (사용자 and 
        hasattr(사용자, 'name') and 
        사용자.name and 
        len(사용자.name.strip()) > 0):
        
        print(f"사용자: {사용자.name}")
    else:
        print("유효하지 않은 사용자 정보")

# 복잡한 논리 조건 정리
def 대출_심사(나이, 소득, 신용점수, 직업):
    # 가독성이 떨어지는 조건
    # if 나이 >= 20 and 소득 >= 3000 and 신용점수 >= 700 or 직업 == "공무원" and 나이 >= 25:
    
    # 가독성 좋은 조건
    기본_자격 = 나이 >= 20 and 소득 >= 3000 and 신용점수 >= 700
    특별_자격 = 직업 == "공무원" and 나이 >= 25
    
    if 기본_자격 or 특별_자격:
        return "대출 승인"
    else:
        return "대출 거부"

print(대출_심사(30, 4000, 750, "개발자"))  # 대출 승인
print(대출_심사(27, 2000, 600, "공무원"))  # 대출 승인
print(대출_심사(19, 2000, 600, "학생"))   # 대출 거부
