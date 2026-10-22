"""1권 Chapter 2. 변수와 데이터 — 2.1 변수와 할당의 깊은 이해

원고: manuscript/chapters/02-variables-data.md (31줄부터)
"""

# ---- 원고 31줄 ----
# 변수 할당의 내부 동작
이름 = "김철수"  # 문자열 객체 생성 후 '이름'이 참조
나이 = 25       # 정수 객체 생성 후 '나이'가 참조

# id() 함수로 객체의 고유 주소 확인
print(f"'이름' 변수가 참조하는 객체의 주소: {id(이름)}")
print(f"'나이' 변수가 참조하는 객체의 주소: {id(나이)}")

# ---- 원고 59줄 ----
# 기본 규칙
name = "홍길동"
age_in_years = 30
_private_var = "은밀한 값"
MAX_SIZE = 100

# 한글 변수명 (완전 지원)
사용자명 = "김영희"
나이 = 28
한국_도시들 = ["서울", "부산", "대구"]

# 유니코드 변수명
π = 3.14159
α = 0.05
β = 0.95

# 언더스코어 활용
__private = "매우 은밀"  # 이름 맹글링은 클래스 안에서만 일어남 (여기서는 평범한 변수)
__init__ = "특수 메서드"  # 파이썬이 특별히 쓰는 이름 모양 (여기서는 평범한 변수, 실제로는 피할 것)

# ---- 원고 87줄 ----
# 이런 변수명들은 사용할 수 없습니다 (예제로만 표시)
# 2name = "숫자로 시작"      # SyntaxError
# class = "예약어 사용"       # SyntaxError  
# my-name = "하이픈 사용"     # SyntaxError
# my name = "공백 사용"       # SyntaxError

# 올바른 대안들
name2 = "숫자로 끝남"        # 올바름
class_name = "예약어 피하기"   # 올바름
my_name = "언더스코어 사용"    # 올바름
my_name_with_space = "공백 대신 언더스코어"  # 올바름

# ---- 원고 105줄 ----
import keyword
print(keyword.kwlist)      # 예약어 35개
print(keyword.softkwlist)  # ['_', 'case', 'match', 'type'] (Python 3.12 기준)

# ---- 원고 141줄 ----
# 작은 정수는 파이썬이 미리 생성해둠 (-5 ~ 256)
a = 100
b = 100
print(f"a is b: {a is b}")  # True - 같은 객체를 참조

# 큰 정수는 미리 만들어 두지 않음
x = 1000
y = 1000
print(f"x is y: {x is y}")  # 파일 실행은 True, 대화형(>>>)은 False - 실행 방식에 따라 다름

# 문자열 인터닝 (String Interning)
str1 = "hello"
str2 = "hello"
print(f"str1 is str2: {str1 is str2}")  # True

# 하지만 실행 중에 만들어진 문자열은 따로 만들어짐
str3 = "".join(["hel", "lo"])
str4 = "".join(["hel", "lo"])
print(f"str3 is str4: {str3 is str4}")  # False - 값은 같지만 다른 객체
