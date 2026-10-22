"""1권 Chapter 17: 표준 라이브러리 핵심 가이드 — 문자열과 텍스트 처리

원고: manuscript/chapters/17-standard-library-guide.md (31줄부터)
"""

# ---- 원고 31줄 ----
import string

# 한글과 영문이 섞인 텍스트 처리
korean_text = "안녕하세요! Hello123 파이썬!"

# 영문 문자만 추출
english_chars = [c for c in korean_text if c in string.ascii_letters]
print(''.join(english_chars))  # Hello

# 숫자만 추출  
digits = [c for c in korean_text if c in string.digits]
print(''.join(digits))  # 123

# 안전한 템플릿 처리
template = string.Template("$name님, $product 주문이 완료되었습니다.")
message = template.substitute(name="김철수", product="파이썬 책")
print(message)  # 김철수님, 파이썬 책 주문이 완료되었습니다.

# ---- 원고 63줄 ----
import re

# 한국어 패턴 정의
korean_pattern = re.compile(r'[가-힣]{2,}')  # 한글 2자 이상
phone_pattern = re.compile(r'010-\d{4}-\d{4}')
email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

text = """
김철수 대리 (010-1234-5678)
이영희 과장 (kim.cs@company.co.kr)  
박민수 부장의 연락처: 010-9876-5432
"""

# 한글 이름 추출
names = korean_pattern.findall(text)
print("이름들:", names)  # ['김철수', '대리', '이영희', '과장', '박민수', '부장의', '연락처']

# 전화번호 추출
phones = phone_pattern.findall(text)
print("전화번호들:", phones)  # ['010-1234-5678', '010-9876-5432']

# 이메일 추출  
emails = email_pattern.findall(text)
print("이메일들:", emails)  # ['kim.cs@company.co.kr']

# 한글 이름만 정확히 추출 (조사 제거)
name_pattern = re.compile(r'[가-힣]{2,}(?=\s+(?:대리|과장|부장|사원|주임|차장))')
proper_names = name_pattern.findall(text)
print("정확한 이름들:", proper_names)  # ['김철수', '이영희', '박민수']

# ---- 원고 103줄 ----
import textwrap
import unicodedata

# 한글 텍스트 줄바꿈
long_korean = "파이썬은 1991년 귀도 반 로섬에 의해 개발된 프로그래밍 언어입니다. 간결하고 읽기 쉬운 문법이 특징이며, 다양한 분야에서 활용되고 있습니다."

wrapped = textwrap.fill(long_korean, width=30)
print(wrapped)

# 한글 문자 정보 분석
korean_char = '한'
print(f"문자: {korean_char}")
print(f"유니코드 이름: {unicodedata.name(korean_char)}")
print(f"카테고리: {unicodedata.category(korean_char)}")

# 한글 자모 분해
from unicodedata import normalize, decomposition
decomposed = normalize('NFD', '한글')
print(f"분해된 형태: {[hex(ord(c)) for c in decomposed]}")
