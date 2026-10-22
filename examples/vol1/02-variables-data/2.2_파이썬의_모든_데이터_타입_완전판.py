"""1권 Chapter 2. 변수와 데이터 — 2.2 파이썬의 모든 데이터 타입 (완전판)

원고: manuscript/chapters/02-variables-data.md (179줄부터)
"""

# ---- 원고 179줄 ----
# 다양한 진법 표현
십진수 = 42
이진수 = 0b101010      # 0b 접두사
팔진수 = 0o52          # 0o 접두사  
십육진수 = 0x2A        # 0x 접두사

print(f"모두 같은 값: {십진수} == {이진수} == {팔진수} == {십육진수}")

# 언더스코어로 가독성 향상 (Python 3.6+)
큰_숫자 = 1_000_000
매우_큰_숫자 = 999_999_999_999

# 정수는 크기 제한이 없음
거대한_수 = 2 ** 1000
print(f"2의 1000제곱의 자릿수: {len(str(거대한_수))}자리")

# ---- 원고 203줄 ----
# 기본 실수
파이 = 3.14159
온도 = -15.5

# 과학적 표기법
광속 = 2.998e8        # 2.998 × 10^8
아보가드로_수 = 6.022e23
전자_질량 = 9.109e-31

# 특수 값들
양의_무한대 = float('inf')
음의_무한대 = float('-inf')
비수 = float('nan')   # Not a Number

print(f"∞ + 1 = {양의_무한대 + 1}")
print(f"NaN == NaN: {비수 == 비수}")  # False!

# 부동소수점 정밀도 문제
print(f"0.1 + 0.2 = {0.1 + 0.2}")  # 0.30000000000000004
print(f"0.1 + 0.2 == 0.3: {0.1 + 0.2 == 0.3}")  # False

# 해결책: decimal 모듈
from decimal import Decimal
정확한_계산 = Decimal('0.1') + Decimal('0.2')
print(f"정확한 계산: {정확한_계산}")  # 0.3

# ---- 원고 237줄 ----
# 복소수 생성 방법
복소수1 = 3 + 4j
복소수2 = complex(3, 4)
복소수3 = complex('3+4j')

print(f"실부: {복소수1.real}")  # 3.0
print(f"허부: {복소수1.imag}")  # 4.0
print(f"절댓값: {abs(복소수1)}")  # 5.0

# 복소수 연산
z1 = 1 + 2j
z2 = 2 - 1j
print(f"덧셈: {z1 + z2}")     # (3+1j)
print(f"곱셈: {z1 * z2}")     # (4+3j)
print(f"켤레: {z1.conjugate()}")  # (1-2j)

# ---- 원고 265줄 ----
# 다양한 문자열 생성 방법
단일_따옴표 = '안녕하세요'
이중_따옴표 = "반갑습니다"
삼중_따옴표 = """여러 줄
문자열
입니다"""

# Raw 문자열 (이스케이프 시퀀스 무시)
경로 = r"C:\Users\Documents\새 폴더"
정규식 = r"\d{3}-\d{4}-\d{4}"

# f-string (Python 3.6+) - 가장 권장되는 방식
이름 = "김파이썬"
나이 = 30
소개 = f"안녕하세요! 제 이름은 {이름}이고, 나이는 {나이}살입니다."

# f-string 고급 활용
숫자 = 3.14159
print(f"원주율: {숫자:.2f}")      # 소수점 2자리
print(f"원주율: {숫자:>10.3f}")   # 오른쪽 정렬, 10자리, 소수점 3자리

가격 = 1234567
print(f"가격: {가격:,}원")        # 천단위 구분자
print(f"가격: {가격:_}원")        # 언더스코어 구분자

# ---- 원고 322줄 ----
# 한글 인코딩 이해
한글_문자열 = "안녕하세요, 파이썬!"

# UTF-8 인코딩/디코딩
바이트_데이터 = 한글_문자열.encode('utf-8')
print(f"UTF-8 바이트: {바이트_데이터}")
복원된_문자열 = 바이트_데이터.decode('utf-8')
print(f"복원: {복원된_문자열}")

# 한글 길이 측정
문장 = "파이썬Programming"
print(f"전체 길이: {len(문장)}")         # 14
print(f"한글만: {''.join(c for c in 문장 if ord(c) >= 44032 and ord(c) <= 55203)}")

# 한글 자모 분리 (고급)
def 한글_자모_분리(글자):
    """한글 글자를 초성, 중성, 종성으로 분리"""
    if not (44032 <= ord(글자) <= 55203):
        return 글자, "", ""
    
    code = ord(글자) - 44032
    초성_index = code // (21 * 28)
    중성_index = (code % (21 * 28)) // 28
    종성_index = code % 28
    
    초성 = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"[초성_index]
    중성 = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"[중성_index]
    종성 = "" if 종성_index == 0 else "ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"[종성_index - 1]
    
    return 초성, 중성, 종성

# 한글 자모 분리 예제
for 글자 in "한글":
    초성, 중성, 종성 = 한글_자모_분리(글자)
    print(f"{글자} = {초성} + {중성} + {종성}")

# ---- 원고 366줄 ----
텍스트 = "  Python Programming 파이썬 프로그래밍  "

# 공백 제거
print(f"strip(): '{텍스트.strip()}'")
print(f"lstrip(): '{텍스트.lstrip()}'")
print(f"rstrip(): '{텍스트.rstrip()}'")

# 대소문자 변환
영문 = "Hello Python World"
print(f"upper(): {영문.upper()}")
print(f"lower(): {영문.lower()}")
print(f"title(): {영문.title()}")
print(f"capitalize(): {영문.capitalize()}")
print(f"swapcase(): {영문.swapcase()}")

# 문자열 검색과 치환
문장 = "파이썬은 쉽고 강력한 프로그래밍 언어입니다. 파이썬을 배워보세요!"
print(f"'파이썬' 위치: {문장.find('파이썬')}")
print(f"'파이썬' 개수: {문장.count('파이썬')}")
print(f"'Java'로 치환: {문장.replace('파이썬', 'Java')}")

# 문자열 분할과 결합
단어들 = "사과,바나나,오렌지,포도".split(',')
print(f"분할: {단어들}")
print(f"결합: {' | '.join(단어들)}")

# 문자열 포매팅 (여러 방법)
이름, 점수 = "김학생", 95

# % 포매팅 (구식)
old_style = "%s님의 점수는 %d점입니다." % (이름, 점수)

# .format() 메서드
new_style = "{}님의 점수는 {}점입니다.".format(이름, 점수)
named_style = "{name}님의 점수는 {score}점입니다.".format(name=이름, score=점수)

# f-string (최신, 권장)
f_string = f"{이름}님의 점수는 {점수}점입니다."

print(f"구식: {old_style}")
print(f"신식: {new_style}")
print(f"명명: {named_style}")
print(f"f-string: {f_string}")

# ---- 원고 422줄 ----
# bytes (불변)
한글_바이트 = "안녕".encode('utf-8')
print(f"bytes: {한글_바이트}")
print(f"길이: {len(한글_바이트)}")  # UTF-8에서 한글은 글자당 3바이트

# bytearray (가변)
가변_바이트 = bytearray("Hello", 'utf-8')
가변_바이트[0] = ord('h')  # 첫 글자를 'h'로 변경
print(f"변경된 bytearray: {가변_바이트.decode('utf-8')}")

# 바이트 연산
바이트1 = b"Hello"
바이트2 = b" World"
결합 = 바이트1 + 바이트2
print(f"바이트 결합: {결합}")

# 16진수 변환
데이터 = "파이썬".encode('utf-8')
hex_string = 데이터.hex()
print(f"16진수: {hex_string}")
복원 = bytes.fromhex(hex_string)
print(f"복원: {복원.decode('utf-8')}")

# ---- 원고 455줄 ----
# 불린 기본값
참 = True
거짓 = False

# 불린으로 평가되는 값들
print("=== 거짓으로 평가되는 값들 ===")
거짓_값들 = [False, 0, 0.0, 0j, '', [], {}, set(), None]
for 값 in 거짓_값들:
    print(f"{repr(값):>8} -> {bool(값)}")

print("\n=== 참으로 평가되는 값들 ===")
참_값들 = [True, 1, -1, 3.14, 1+2j, 'a', [1], {'a': 1}, {1}]
for 값 in 참_값들:
    print(f"{repr(값):>8} -> {bool(값)}")

# 불린 연산
print(f"True and False: {True and False}")
print(f"True or False: {True or False}")
print(f"not True: {not True}")

# 단축 평가 (Short-circuit evaluation)
def 참_함수():
    print("참 함수 실행됨")
    return True

def 거짓_함수():
    print("거짓 함수 실행됨")
    return False

print("=== and 연산 단축 평가 ===")
result1 = 거짓_함수() and 참_함수()  # 첫 번째만 실행됨

print("=== or 연산 단축 평가 ===")
result2 = 참_함수() or 거짓_함수()   # 첫 번째만 실행됨
