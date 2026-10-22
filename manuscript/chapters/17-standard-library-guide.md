# Chapter 17: 표준 라이브러리 핵심 가이드

> **학습 목표**  
> - 문자열, 날짜와 시간, 파일 경로를 표준 라이브러리로 다루기
> - JSON, CSV, pickle로 데이터를 저장하고 불러오기
> - 통계, 컬렉션, 로깅 모듈을 실무 예제로 써 보기
> - 동시성 도구와 성능 측정 도구 고르기

---

## 들어가며: 건전지가 들어 있는 장난감

어릴 때 장난감 상자를 열었는데 건전지가 없어서 바로 못 갖고 놀았던 기억, 있나요? 그래서 어떤 장난감 상자에는 "건전지 포함(batteries included)"이라고 크게 적혀 있죠. 사자마자 바로 쓸 수 있다는 뜻입니다.

파이썬이 바로 이런 언어입니다. 파이썬을 설치하면 날짜 계산, 파일과 폴더 다루기, JSON과 CSV 읽고 쓰기, 인터넷 주소 만들기, 통계, 로그 남기기, 여러 일 동시에 하기까지, 수백 개의 모듈이 **처음부터 함께 들어 있어요**. 이것을 **표준 라이브러리(standard library)** 라고 부릅니다. 14장에서 `random`과 `json`을 불러 쓴 것도 바로 이 표준 라이브러리였죠. 설치 명령 없이 `import` 한 줄이면 됩니다.

표준 라이브러리는 너무 커서 모두 외울 수도, 외울 필요도 없습니다. 중요한 것은 "이런 일은 표준 라이브러리에 이미 있겠지?" 하고 **먼저 찾아보는 습관**이에요. 전체 목록은 파이썬 공식 문서의 라이브러리 레퍼런스(https://docs.python.org/ko/3/library/)에 한국어로도 정리되어 있습니다. 이 장에서는 그중 실무에서 자주 쓰는 모듈을, 한글 텍스트·한국 시간·원화 계산처럼 우리 환경에서 마주치는 예제로 둘러봅니다.

미리 알아 둘 점이 하나 있습니다. 이 장의 예제 중 몇 개는 표준 라이브러리가 아닌 외부 패키지를 함께 씁니다. `psutil`, `aiohttp`, `aiofiles`, `memory_profiler`, `holidays`가 그래요. 해당 절에서 따로 짚어 드리니, 그 예제를 실행하려면 `uv add 패키지이름`으로 먼저 설치하세요. 설치하지 않고 실행하면 `ModuleNotFoundError`가 납니다.

## 문자열과 텍스트 처리

한글은 영어보다 다루기 까다로울 것 같지만, 파이썬 3의 문자열은 처음부터 **유니코드**라서 한글도 영어와 똑같이 한 글자씩 다룰 수 있습니다. `len("안녕")`은 2이고, `"안녕"[0]`은 `'안'`이에요. 이 절에서는 글자를 골라내고(`string`), 패턴으로 찾고(`re`), 보기 좋게 줄 바꾸고(`textwrap`), 글자 하나를 속까지 들여다보는(`unicodedata`) 모듈을 차례로 봅니다.

### string 모듈 활용

`string` 모듈에는 자주 쓰는 글자 묶음이 상수로 들어 있습니다. `string.ascii_letters`는 영문 대소문자 52개, `string.digits`는 숫자 `'0123456789'`예요. 글자 하나하나가 이 묶음에 들어 있는지(`in`) 검사하면 원하는 종류만 골라낼 수 있습니다.

`string.Template`은 `$이름` 자리에 값을 채워 넣는 간단한 틀입니다. f-문자열이 더 편한데 왜 쓸까요? f-문자열은 **코드 안에서** 만들어야 하지만, `Template`의 틀은 파일이나 데이터베이스에서 읽어 온 **문자열**이어도 됩니다. 그래서 운영자가 안내 문구를 고칠 수 있게 할 때 쓰기 좋아요. 틀 안에서는 값 채우기만 할 수 있고 코드를 실행할 수 없어서 안전하기도 하고요.

```python
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
```

결과는 주석대로 `Hello`, `123`, 그리고 이름과 상품이 채워진 안내문입니다. 한글 '안녕하세요'는 `ascii_letters`에 없으니 걸러졌어요. `substitute()`는 채울 값을 하나라도 빠뜨리면 `KeyError`를 내고, `safe_substitute()`는 빠진 자리를 `$product`처럼 그대로 남겨 둡니다.

### 정규표현식으로 한글 처리

전화번호, 이메일, 이름처럼 **모양이 정해진 글자열**을 찾을 때는 **정규표현식(regular expression)** 을 씁니다. 찾고 싶은 글자의 생김새를 기호로 적은 "몽타주"라고 생각하면 돼요.

- `[가-힣]`: '가'부터 '힣'까지, 즉 완성된 한글 한 글자. `{2,}`는 "2번 이상 반복"이라 두 글자 이상의 한글 덩어리를 찾습니다.
- `\d{4}`: 숫자 4개. 그래서 `010-\d{4}-\d{4}`는 010으로 시작하는 휴대전화 번호 모양입니다.
- `(?=...)`: **앞을 살펴보기(lookahead)**. "바로 뒤에 이것이 와야 한다"는 조건만 확인하고, 그 부분은 결과에 넣지 않습니다.

`re.compile()`로 패턴을 미리 만들어 두면 같은 패턴을 여러 번 쓸 때 편하고, `findall()`은 찾은 것을 모두 리스트로 돌려줍니다. 패턴 앞의 `r`은 원시 문자열(raw string)로, `\d`의 역슬래시를 파이썬이 먼저 해석하지 않고 그대로 정규표현식에 넘기라는 표시예요.

```python
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
```

첫 번째 결과를 보면 정규표현식의 한계가 보입니다. "한글 두 글자 이상"이라는 모양만 보니 '대리', '과장', '부장의', '연락처'까지 이름으로 잡혔어요. 정규표현식은 **모양**만 알지 **뜻**은 모릅니다. 그래서 마지막 패턴은 "이름 뒤에는 공백과 직급이 온다"는 모양 규칙을 하나 더 붙여서 이름만 골라냈습니다. 원하는 것만 잡힐 때까지 조건을 좁혀 가는 것, 이것이 정규표현식을 쓰는 요령입니다.

### textwrap과 unicodedata

`textwrap.fill(글, width=30)`은 긴 글을 한 줄에 30글자를 넘지 않게 **낱말 단위로** 끊어 줍니다. 낱말 중간에서 자르지 않으려고 공백에서 끊기 때문에, 줄마다 길이가 조금씩 달라요. 이때 한글 한 글자도 1글자로 세므로, 화면에서는 영문보다 줄이 길어 보일 수 있습니다.

`unicodedata`는 글자의 **신분증**을 보여 줍니다. 유니코드에는 세상의 모든 글자마다 고유 번호와 이름이 붙어 있어요. 그리고 한글 한 글자는 사실 초성·중성·종성으로 **분해할 수 있습니다**. `normalize('NFD', ...)`가 그 분해를 해 줘요.

```python
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
```

'한'의 유니코드 이름은 `HANGUL SYLLABLE HAN`, 분류는 `Lo`(Letter, other: 대소문자 구분이 없는 글자)입니다. '한글' 두 글자를 분해하면 여섯 개의 코드가 나와요. `0x1112`(ㅎ), `0x1161`(ㅏ), `0x11ab`(ㄴ)이 '한', `0x1100`(ㄱ), `0x1173`(ㅡ), `0x11af`(ㄹ)이 '글'입니다.

이게 실무에서 왜 중요할까요? macOS에서 만든 한글 파일 이름을 윈도우로 옮기면 "ㅎㅏㄴㄱㅡㄹ"처럼 자모가 풀려 보이는 일이 있습니다. 운영체제에 따라 파일 이름을 분해형(NFD)이나 조합형(NFC)으로 저장하기 때문이에요. 겉보기엔 같은 '한글'인데 `==`로 비교하면 `False`가 나오기도 합니다. 그럴 때 `normalize('NFC', 글자열)`로 양쪽을 같은 형태로 맞춘 다음 비교하면 됩니다.

## 날짜와 시간

"지금 몇 시야?"라는 질문은 간단해 보이지만, 프로그램에게는 "어디 기준으로?"라는 질문이 따라붙습니다. 서울이 오후 3시일 때 런던은 오전 6시죠. 서버가 해외에 있으면 서버의 시계는 한국 시간이 아닐 수도 있습니다. 여기에 주말, 공휴일, 영업일까지 얽히면 날짜 계산은 생각보다 훨씬 까다로워집니다.

### datetime과 한국 시간

`datetime`은 날짜와 시간을 다루는 기본 모듈이고, `zoneinfo`(파이썬 3.9부터)는 세계 각 지역의 시간대 정보를 제공합니다. `ZoneInfo("Asia/Seoul")`처럼 "대륙/도시" 이름으로 시간대를 고르죠.

시간에는 두 종류가 있다는 것을 기억하세요. 시간대 정보가 붙은 **aware** 시각과, 붙지 않은 **naive** 시각입니다. `datetime.now(seoul_tz)`처럼 시간대를 넘기면 aware 시각이 되어 `+09:00` 같은 꼬리표가 붙고, 이런 시각은 `astimezone()`으로 다른 시간대로 정확하게 바꿀 수 있어요. 여러 나라 사용자를 상대하는 서비스는 보통 **UTC(세계 표준시)로 저장하고, 보여 줄 때만 현지 시간으로 바꿉니다**.

```python
import datetime
from zoneinfo import ZoneInfo

# 한국 시간 다루기
seoul_tz = ZoneInfo("Asia/Seoul")
now_seoul = datetime.datetime.now(seoul_tz)
print(f"현재 서울 시간: {now_seoul.strftime('%Y년 %m월 %d일 %H시 %M분')}")

# UTC와 한국시간 변환
utc_time = datetime.datetime.now(datetime.timezone.utc)
seoul_time = utc_time.astimezone(seoul_tz)
print(f"UTC: {utc_time}")
print(f"서울: {seoul_time}")

# 한국 날짜 형식
korean_format = now_seoul.strftime('%Y년 %m월 %d일 (%a)')
print(f"한국식 날짜: {korean_format}")

# 업무일 계산 (주말 제외)
def add_business_days(start_date, days):
    current = start_date
    while days > 0:
        current += datetime.timedelta(days=1)
        if current.weekday() < 5:  # 월-금 (0-4)
            days -= 1
    return current

start = datetime.date.today()
business_day = add_business_days(start, 5)
print(f"5영업일 후: {business_day}")
```

출력에서 UTC 시각과 서울 시각은 숫자는 9시간 차이가 나지만 **같은 순간**입니다. 꼬리표 `+00:00`과 `+09:00`이 그 차이를 설명해 주죠.

그런데 "한국식 날짜"가 `2024년 03월 15일 (Fri)`처럼 요일만 영어로 나옵니다. `strftime`의 `%a`(요일 약어)와 `%A`(요일 이름)는 운영체제의 언어 설정(로케일)을 따르는데, 따로 설정하지 않으면 영어가 기본이기 때문이에요. 로케일 설정은 컴퓨터마다 다르게 동작해서 믿기 어려우니, 요일을 한국어로 확실하게 쓰고 싶다면 바로 다음 예제처럼 `['월', '화', ...]` 리스트를 만들어 `weekday()` 번호로 꺼내는 편이 안전합니다.

`add_business_days()`는 하루씩 넘기면서 `weekday()`가 5보다 작은 날, 즉 월요일(0)부터 금요일(4)까지만 세어 영업일을 계산합니다. 토요일과 일요일은 건너뛰지만 **공휴일은 모릅니다**. 추석 연휴가 끼어 있어도 영업일로 세어 버려요. 그래서 다음 예제에서 공휴일을 다룹니다.

### calendar 모듈 활용

`calendar` 모듈은 달력을 글자로 찍어 주고, 요일을 계산해 줍니다. `calendar.month(2024, 3)`은 2024년 3월 달력을 문자열로 돌려주고, `setfirstweekday(calendar.SUNDAY)`로 우리 달력처럼 일요일부터 시작하게 바꿀 수 있어요. `calendar.weekday(2024, 3, 1)`은 그날의 요일 번호(월요일이 0)를 알려 줍니다.

예제 뒷부분은 2024년 한국 공휴일을 `(월, 일)` 튜플을 키로 하는 딕셔너리에 담고, `is_korean_holiday()`로 어떤 날이 공휴일인지 검사합니다. 튜플은 바꿀 수 없는 값이라 딕셔너리의 키로 쓸 수 있다는 것(7장)을 활용한 거예요.

```python
import calendar

# 한국어 달력 생성
calendar.setfirstweekday(calendar.SUNDAY)  # 일요일부터 시작

# 2024년 3월 달력
march_2024 = calendar.month(2024, 3)
print("2024년 3월:")
print(march_2024)

# 특정 날짜가 무슨 요일인지
day_of_week = calendar.weekday(2024, 3, 1)
korean_days = ['월', '화', '수', '목', '금', '토', '일']
print(f"2024년 3월 1일은 {korean_days[day_of_week]}요일")

# 한국 공휴일 데이터
korean_holidays_2024 = {
    (1, 1): "신정",
    (2, 9): "설날 연휴",
    (2, 10): "설날",
    (2, 11): "설날 연휴",
    (2, 12): "설날 대체공휴일",
    (3, 1): "삼일절",
    (4, 10): "국회의원 선거일",
    (5, 5): "어린이날",
    (5, 6): "어린이날 대체공휴일",
    (5, 15): "부처님 오신날",
    (6, 6): "현충일",
    (8, 15): "광복절",
    (9, 16): "추석 연휴",
    (9, 17): "추석",
    (9, 18): "추석 연휴",
    (10, 1): "국군의 날(임시공휴일)",
    (10, 3): "개천절",
    (10, 9): "한글날",
    (12, 25): "크리스마스"
}

def is_korean_holiday(date):
    return (date.month, date.day) in korean_holidays_2024
```

달력은 일요일부터 시작하는 3월 달력으로 찍히고(요일 머리글은 `Su Mo Tu`처럼 영어입니다), 2024년 3월 1일은 금요일로 나옵니다.

공휴일 표를 자세히 보면 해마다 같은 날이 아닌 것이 많습니다. 2월 12일은 설날(2월 10일)이 일요일과 겹쳐서 생긴 **대체공휴일**이고, 5월 6일도 어린이날이 일요일이라 생긴 대체공휴일이에요. 4월 10일은 그해 국회의원 선거일, 10월 1일은 그해에만 정해진 국군의 날 임시공휴일입니다. 설날, 부처님 오신날, 추석은 **음력** 날짜라서 양력으로는 해마다 바뀌고요. 2024년 추석은 9월 17일이었지만, 2025년 추석은 10월 6일입니다.

그래서 공휴일을 코드에 직접 적어 두면 매년 손으로 고쳐야 하고, 날짜 하나만 밀려 적어도 알아채기 어렵습니다. 표준 라이브러리에는 한국 공휴일 정보가 없으니, 실무에서는 공휴일 정보를 관리해 주는 외부 패키지를 쓰거나 공공기관이 제공하는 공휴일 데이터를 받아 씁니다. 외부 패키지 `holidays`(`uv add holidays`로 설치)로 확인해 볼게요.

```python
from datetime import date

import holidays

kr_holidays = holidays.KR(years=2024, language="ko")
for day, name in sorted(kr_holidays.items()):
    if day.month == 9:
        print(day, name)

print(date(2024, 9, 19) in kr_holidays)  # 추석 연휴가 끝난 다음 날
print(date(2024, 10, 1) in kr_holidays)  # 국군의 날 임시공휴일
```

```text
2024-09-16 추석 전날
2024-09-17 추석
2024-09-18 추석 다음날
False
True
```

9월의 공휴일 세 날이 앞의 표와 정확히 같고, 표에 없는 9월 19일은 `False`, 표에 넣은 10월 1일 임시공휴일은 `True`로 나옵니다. `holidays.KR(years=2024)`는 딕셔너리처럼 동작해서, 날짜를 키로 공휴일 이름을 꺼낼 수 있고 `in`으로 공휴일인지 바로 확인할 수 있습니다. 앞 절의 `add_business_days()`에서 `current.weekday() < 5` 조건에 `and current not in kr_holidays`를 더하면 공휴일까지 건너뛰는 영업일 계산이 되죠. 다만 이런 패키지도 결국 사람이 정리한 데이터라서, 갑자기 정해지는 임시공휴일은 패키지를 업데이트해야 반영됩니다. 날짜가 돈이나 마감과 연결된 프로그램이라면 공휴일 목록을 한 번 더 확인하세요.

## 파일 시스템과 경로

파일 경로는 운영체제마다 생김새가 다릅니다. 윈도우는 `C:\데이터\고객.txt`처럼 역슬래시를, macOS와 리눅스는 `/home/데이터/고객.txt`처럼 슬래시를 쓰죠. 경로를 문자열로 이어 붙이면 이 차이 때문에 한쪽에서만 동작하는 코드가 되기 쉽습니다.

### pathlib로 한국어 경로 처리

`pathlib`의 `Path`는 경로를 문자열이 아닌 **객체**로 다룹니다. 12장에서 기본 사용법을 봤으니 여기서는 핵심만 짚을게요. `/` 연산자로 경로 조각을 이으면 운영체제에 맞는 구분자를 알아서 넣어 주고, `.parent`(부모 폴더), `.name`(파일 이름), `.suffix`(확장자)로 경로의 각 부분을 꺼낼 수 있습니다. `mkdir(parents=True, exist_ok=True)`는 중간 폴더까지 한꺼번에 만들고, 이미 있으면 조용히 넘어가요. `write_text()`와 `read_text()`는 파일 열기·쓰기·닫기를 한 줄로 해 줍니다. 한글을 다루니 `encoding='utf-8'`을 꼭 적어 주세요.

```python
from pathlib import Path
import os

# 한국어 파일명과 경로
korean_files = Path("데이터") / "한국어" / "고객_정보.txt"
print(f"전체 경로: {korean_files}")
print(f"부모 디렉토리: {korean_files.parent}")
print(f"파일명: {korean_files.name}")
print(f"확장자: {korean_files.suffix}")

# 경로 생성 및 파일 작업
data_dir = Path("한국_프로젝트/데이터")
data_dir.mkdir(parents=True, exist_ok=True)

# 한글 파일 생성 및 처리
korean_file = data_dir / "고객_목록.txt"
customers = ["김철수", "이영희", "박민수", "정수진"]

korean_file.write_text("\n".join(customers), encoding='utf-8')
print(f"파일 크기: {korean_file.stat().st_size} 바이트")

# 파일 읽기
content = korean_file.read_text(encoding='utf-8')
print(f"파일 내용:\n{content}")

# glob 패턴으로 파일 찾기  
for txt_file in data_dir.glob("*.txt"):
    print(f"찾은 파일: {txt_file.name}")
```

결과에서 파일 크기를 보세요. 이름 네 개, 열두 글자에 줄바꿈 세 개를 썼는데 39바이트입니다. UTF-8에서 한글 한 글자는 **3바이트**라서 12 × 3 = 36, 여기에 줄바꿈 3바이트가 더해진 거예요. 글자 수와 바이트 수가 다르다는 것은 파일 크기 제한이나 데이터베이스 열 길이를 정할 때 꼭 기억해야 합니다. `glob("*.txt")`는 폴더 안에서 이름이 `.txt`로 끝나는 파일을 모두 찾아 줍니다.

### os와 shutil 활용

`pathlib`가 경로를 다룬다면, `os`는 운영체제와 대화하고 `shutil`(shell utilities)은 파일을 복사하고 옮기는 일을 합니다. `os.environ`은 **환경변수**를 담은 딕셔너리예요. 환경변수는 프로그램 바깥에서 넣어 주는 설정값으로, 비밀번호나 서버 주소처럼 코드에 적으면 안 되는 값을 전달할 때 씁니다. `os.environ.get('이름', '기본값')`처럼 `get()`으로 꺼내면 값이 없어도 오류가 나지 않아요.

`shutil.copy2()`는 파일을 복사하면서 수정 시각 같은 정보까지 함께 옮기고, `copytree()`는 폴더를 통째로 복사합니다. `dirs_exist_ok=True`를 주면 대상 폴더가 이미 있어도 그 안에 덮어씁니다.

```python
import os
import shutil
from pathlib import Path

# 환경변수 설정
os.environ['한국어_설정'] = '서울_KR'
korean_setting = os.environ.get('한국어_설정', '기본값')
print(f"한국어 설정: {korean_setting}")

# 디렉토리 작업
work_dir = "한국_작업공간"
if not os.path.exists(work_dir):
    os.makedirs(work_dir)

# 파일 복사 및 이동
source = "한국_프로젝트/데이터/고객_목록.txt"
backup = "한국_프로젝트/데이터/백업_고객_목록.txt"

if Path(source).exists():
    shutil.copy2(source, backup)
    print(f"{source} → {backup} 복사 완료")

# 디렉토리 전체 복사
if os.path.exists("한국_프로젝트"):
    shutil.copytree("한국_프로젝트", "한국_프로젝트_백업", dirs_exist_ok=True)
```

앞 예제를 먼저 실행해 `한국_프로젝트/데이터/고객_목록.txt`가 있다면, 같은 폴더에 `백업_고객_목록.txt`로 복사되었다는 메시지가 나옵니다. `Path(source).exists()`로 원본이 있는지 먼저 확인하니, 앞 예제를 건너뛰었다면 복사를 조용히 건너뛰어요. 마지막으로 `copytree`가 `한국_프로젝트` 폴더 전체를 `한국_프로젝트_백업`으로 복사합니다.

`os.environ`에 넣은 값은 **지금 실행 중인 이 프로그램과, 이 프로그램이 실행하는 자식 프로그램에만** 보입니다. 프로그램이 끝나면 사라지고, 터미널이나 다른 프로그램의 환경변수는 바뀌지 않아요.

## 데이터 직렬화

파이썬의 딕셔너리나 리스트는 프로그램이 실행되는 동안 메모리 속에만 있습니다. 프로그램을 끄면 사라지고, 다른 프로그램에 그대로 건넬 수도 없죠. 그래서 메모리 속 데이터를 파일에 쓰거나 네트워크로 보낼 수 있는 **글자나 바이트의 줄**로 바꾸는데, 이것을 **직렬화(serialization)** 라고 합니다. 이사할 때 가구를 분해해서 상자에 차곡차곡 담는 것과 같아요. 새 집에서 다시 조립하는 것은 **역직렬화**입니다.

어떤 상자에 담을지는 받는 쪽에 따라 고릅니다. 다른 프로그램이나 웹과 주고받으려면 **JSON**, 엑셀 같은 표 프로그램과 주고받으려면 **CSV**, 파이썬끼리만 쓴다면 **pickle**이 편합니다. JSON과 CSV는 12장에서 처음 다뤘으니, 여기서는 한글을 다룰 때 주의할 점을 중심으로 봅니다.

### JSON으로 한글 데이터 처리

`json.dumps()`는 파이썬 객체를 JSON **문자열**로, `json.dump()`는 JSON으로 바꿔 **파일**에 바로 씁니다(끝에 s가 붙은 쪽이 string). 읽을 때도 `loads()`는 문자열에서, `load()`는 파일에서 읽어요.

한글에서 중요한 옵션은 `ensure_ascii=False`입니다. 기본값인 `True`로 두면 JSON은 영문·숫자 이외의 글자를 모두 `김` 같은 **유니코드 이스케이프**로 바꿔서 저장합니다. 틀린 것은 아니라 다시 읽으면 한글로 돌아오지만, 파일을 열어 봤을 때 사람이 읽을 수가 없어요. `False`로 두면 한글이 그대로 저장됩니다. `indent=2`는 보기 좋게 두 칸씩 들여쓰기를 해 줍니다.

```python
import json
from datetime import date

# 한국 고객 데이터
customer_data = {
    "고객_정보": {
        "이름": "김철수",
        "나이": 35,
        "주소": "서울특별시 강남구 역삼동",
        "이메일": "kim.cs@example.com",
        "가입일": str(date.today()),
        "구매_이력": [
            {"상품": "파이썬 책", "가격": 25000, "날짜": "2024-01-15"},
            {"상품": "프로그래밍 강의", "가격": 150000, "날짜": "2024-02-10"}
        ]
    }
}

# 한글이 깨지지 않도록 저장
json_string = json.dumps(customer_data, ensure_ascii=False, indent=2)
print("JSON 문자열:")
print(json_string)

# 파일로 저장
with open("고객_데이터.json", "w", encoding="utf-8") as f:
    json.dump(customer_data, f, ensure_ascii=False, indent=2)

# 파일에서 읽기
with open("고객_데이터.json", "r", encoding="utf-8") as f:
    loaded_data = json.load(f)
    customer_name = loaded_data["고객_정보"]["이름"]
    print(f"고객명: {customer_name}")
```

가입일을 `str(date.today())`로 바꿔 넣은 이유가 있습니다. JSON은 문자열, 숫자, 참/거짓, null, 배열, 객체만 알아요. `date` 객체를 그대로 넣으면 `TypeError: Object of type date is not JSON serializable`이 납니다. 날짜는 `'2024-01-15'` 같은 문자열로 바꿔서 담고, 읽은 뒤 필요하면 `date.fromisoformat()`으로 다시 날짜로 되돌리세요.

JSON에 담을 수 없는 파이썬 객체를 통째로 저장하고 싶을 때는 **pickle**을 씁니다. 작업하던 변수를 그대로 파일에 넣어 뒀다가 다음에 그대로 꺼내 쓰는 방법이에요.

```python
import pickle

scores = {"김철수": [85, 78, 92], "이영희": [92, 88, 84]}

with open("scores.pkl", "wb") as f:   # 바이너리 쓰기 모드
    pickle.dump(scores, f)

with open("scores.pkl", "rb") as f:
    loaded = pickle.load(f)

print(loaded)
print(loaded == scores, type(loaded["김철수"]))
```

```text
{'김철수': [85, 78, 92], '이영희': [92, 88, 84]}
True <class 'list'>
```

pickle은 글자가 아니라 바이트로 저장하므로 파일을 `"wb"`, `"rb"`처럼 **바이너리 모드**로 엽니다. 꺼낸 값은 원래와 같고, 리스트는 리스트 그대로 돌아왔어요. 날짜든, 직접 만든 클래스의 객체든 대부분 이렇게 저장할 수 있습니다.

> **Q. 그럼 JSON 대신 늘 pickle을 쓰면 되지 않나요?**
> 두 가지 이유로 안 됩니다. 첫째, pickle 파일은 파이썬만 읽을 수 있어서 웹 브라우저나 다른 언어의 프로그램과 주고받을 수 없어요. 둘째, 더 중요한 이유로 **pickle 파일을 여는 것은 그 안의 코드를 실행하는 것과 같습니다**. 파이썬 공식 문서도 믿을 수 없는 곳에서 받은 pickle 데이터는 절대 풀지 말라고 경고해요. 악의적으로 만든 pickle 파일은 여는 순간 내 컴퓨터에서 아무 명령이나 실행할 수 있습니다. 내가 만들고 내가 쓰는 파일에만 pickle을 쓰고, 남과 주고받는 데이터는 JSON으로 하세요.

### CSV로 한국어 데이터 처리

CSV는 쉼표로 칸을 나눈 텍스트 표입니다. `csv.DictWriter`는 딕셔너리 리스트를 CSV로 쓰는데, `fieldnames`로 열의 순서를 정해 주고 `writeheader()`로 머리줄을 먼저 씁니다. 읽을 때 쓰는 `csv.DictReader`는 머리줄을 키로 삼아 한 줄씩 딕셔너리로 돌려줘요.

파일을 열 때 `newline=""`을 꼭 넣으세요. `csv` 모듈이 줄바꿈을 직접 처리하는데, 이걸 빼면 윈도우에서 줄 사이에 빈 줄이 하나씩 끼어 저장됩니다. 그리고 CSV에서 읽은 값은 **모두 문자열**입니다. 연봉을 계산하거나 천 단위 쉼표를 찍으려면 `int(row['연봉'])`처럼 숫자로 바꿔야 해요.

```python
import csv

# 한국 직원 데이터
employees = [
    {"이름": "김철수", "부서": "개발팀", "연봉": 5000, "입사일": "2020-03-01"},
    {"이름": "이영희", "부서": "기획팀", "연봉": 4500, "입사일": "2021-06-15"},
    {"이름": "박민수", "부서": "영업팀", "연봉": 4800, "입사일": "2019-11-20"},
]

# CSV 파일 쓰기
with open("직원_명단.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["이름", "부서", "연봉", "입사일"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(employees)

# CSV 파일 읽기
with open("직원_명단.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    print("직원 목록:")
    for row in reader:
        print(f"- {row['이름']} ({row['부서']}) - {int(row['연봉']):,}만원")

# 고급 CSV 처리
import io

csv_data = """이름,나이,도시
김철수,25,서울
이영희,30,부산
박민수,28,대구"""

# StringIO를 사용한 메모리 CSV 처리
csv_stream = io.StringIO(csv_data)
reader = csv.DictReader(csv_stream)

for row in reader:
    print(f"{row['이름']}님은 {row['나이']}세, {row['도시']} 거주")
```

뒷부분의 `io.StringIO`는 문자열을 **파일인 척** 하게 만들어 줍니다. `csv.DictReader`는 파일을 받는 도구인데, 웹에서 받아 온 CSV 문자열처럼 파일로 저장하지 않은 데이터도 `StringIO`로 감싸면 그대로 읽을 수 있어요.

이렇게 `utf-8`로 저장한 한글 CSV를 윈도우용 엑셀에서 더블클릭해 열면 한글이 깨져 보이는 경우가 많습니다. 엑셀에서 열 파일이라면 `encoding="utf-8-sig"`로 저장하세요. 파일 맨 앞에 "UTF-8 파일입니다"라는 표식(BOM)이 붙어서 엑셀이 제대로 읽습니다. 20장의 분석 결과 저장에서도 이 방법을 씁니다.

## 네트워킹과 인터넷

날씨 앱은 날씨를 어떻게 알까요? 기상 정보를 가진 서버에 "서울 날씨 알려 줘"라고 인터넷으로 요청하고, 서버가 보내 준 JSON을 받아서 화면에 그립니다. 이렇게 프로그램끼리 정해진 형식으로 주고받는 창구를 **API**라고 해요. 이 절에서는 표준 라이브러리만으로 API에 요청을 보내고, 거꾸로 작은 웹 서버를 직접 띄워 봅니다.

### urllib로 한국 API 연동

인터넷 주소(URL)에는 영문, 숫자, 몇 가지 기호만 쓸 수 있습니다. 그래서 검색어 "파이썬 프로그래밍"을 주소에 넣으려면 한글과 공백을 `%ED%8C%8C…` 같은 **퍼센트 인코딩**으로 바꿔야 해요. `urllib.parse.urlencode()`가 딕셔너리를 받아서 이 변환과 `키=값&키=값` 조립을 한 번에 해 줍니다.

`get_korean_weather()`는 날씨 API(OpenWeatherMap)에 요청을 보내는 함수입니다. 이런 공개 API는 대부분 회원 가입을 하고 받은 **API 키**를 요청에 함께 보내야 해요. 예제의 `"YOUR_API_KEY"`는 자리만 잡아 둔 가짜 값이라 그대로 실행하면 서버가 거절하고, 함수는 `except`에서 `API 호출 오류: HTTP Error 401: Unauthorized`(인증 실패)를 출력한 뒤 `None`을 돌려줍니다. 진짜 키를 받았다면 코드에 직접 적지 말고 앞에서 본 환경변수로 넘기세요. 코드는 다른 사람과 공유되지만 키는 공유되면 안 되니까요.

`urllib.request.urlopen()`은 표준 라이브러리만으로 HTTP 요청을 보내는 방법입니다. 실무에서는 더 편한 외부 패키지 `requests`나 `httpx`를 많이 쓰지만, 설치 없이 쓸 수 있다는 것이 `urllib`의 장점이에요.

예제 뒷부분은 반대 방향, 즉 **요청을 받는 쪽**입니다. `http.server`의 `BaseHTTPRequestHandler`를 상속해 `do_GET()`을 만들면, 브라우저가 이 서버에 접속(GET 요청)할 때마다 그 메서드가 실행되어 HTML을 돌려줍니다. 주석 처리된 세 줄을 풀고 실행한 다음 브라우저에서 `http://localhost:8000`을 열면 인사말과 현재 시각이 보여요. 서버는 `Ctrl+C`로 멈춥니다. 이 서버는 공부용입니다. 실제 웹 서비스는 19장의 FastAPI 같은 프레임워크로 만듭니다.

```python
import datetime
import json
import urllib.parse
import urllib.request

# 한글 검색어를 포함한 URL 생성
base_url = "https://api.example.com/search"
params = {
    "q": "파이썬 프로그래밍",
    "lang": "ko",
    "limit": 10
}

# URL 인코딩
encoded_params = urllib.parse.urlencode(params)
full_url = f"{base_url}?{encoded_params}"
print(f"요청 URL: {full_url}")

# 한국 공공데이터 API 호출 예제 (모의)
def get_korean_weather(city="서울"):
    """한국 날씨 정보 조회"""
    try:
        # 실제로는 API 키가 필요
        api_url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{city},KR",
            "appid": "YOUR_API_KEY",
            "lang": "kr",
            "units": "metric"
        }
        
        encoded_params = urllib.parse.urlencode(params)
        url = f"{api_url}?{encoded_params}"
        
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return {
                    "도시": data.get("name", city),
                    "온도": data["main"]["temp"],
                    "날씨": data["weather"][0]["description"]
                }
    except Exception as e:
        print(f"API 호출 오류: {e}")
        return None

# HTTP 서버 만들기
from http.server import HTTPServer, BaseHTTPRequestHandler

class KoreanHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = """
        <html>
        <head><title>한국어 웹서버</title></head>
        <body>
            <h1>안녕하세요! 파이썬 웹서버입니다</h1>
            <p>현재 시간: {}</p>
        </body>
        </html>
        """.format(datetime.datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분'))
        
        self.wfile.write(html.encode('utf-8'))

# 서버 실행 예제 (주석 처리)
# server = HTTPServer(('localhost', 8000), KoreanHandler)
# print("서버 시작: http://localhost:8000")
# server.serve_forever()
```

## 수학과 통계

돈 계산과 통계는 "대충 맞으면 되는" 일이 아닙니다. 1원이 틀린 영수증은 틀린 영수증이죠. 3장에서 `0.1 + 0.1 + 0.1`이 `0.3`이 되지 않는 것을 봤던 것처럼, 실수(float) 계산에는 작은 오차가 끼어듭니다. 이 절에서는 정확한 십진 계산을 위한 `decimal`과, 평균·중앙값·표준편차를 계산해 주는 `statistics`를 봅니다. 무작위 수를 만드는 `random`은 14장에서 로또 번호 뽑기로 이미 만났어요.

### 한국 금융 계산

`Decimal`은 숫자를 우리가 종이에 쓰는 **십진수 그대로** 저장합니다. 그래서 `Decimal('0.00015')`는 정확히 0.00015예요. 이때 반드시 **문자열**로 만들어야 합니다. `Decimal(0.00015)`처럼 실수를 넘기면 실수에 이미 섞여 있는 오차까지 그대로 옮겨 오거든요. `getcontext().prec = 10`은 계산 결과를 유효숫자 10자리까지 유지하라는 설정입니다.

예제 뒷부분의 적금 계산은 `float`로 합니다. 매달 50만 원씩 36개월 넣는 적금에서, 첫 달에 넣은 돈은 36개월 동안, 마지막 달에 넣은 돈은 1개월 동안만 이자가 붙죠. `compound_interest(monthly_saving, annual_rate, (36 - month) / 12, 12)`가 바로 "이번 달에 넣은 돈이 만기까지 남은 기간 동안 얼마로 불어나는가"를 계산하고, `sum()`이 36번 넣은 돈을 모두 더합니다.

```python
import math
import decimal
from decimal import Decimal

# 한국 주식 계산 (소수점 정밀도 중요)
decimal.getcontext().prec = 10

stock_price = Decimal('45600')  # 삼성전자 주가
shares = 100
commission_rate = Decimal('0.00015')  # 0.015% 수수료

# 매수 총액 계산
total_cost = stock_price * shares
commission = total_cost * commission_rate
final_cost = total_cost + commission

print(f"주가: {stock_price:,}원")
print(f"주식 수: {shares}주")
print(f"매수 총액: {total_cost:,}원")
print(f"수수료: {commission:.0f}원")
print(f"최종 비용: {final_cost:,.0f}원")

# 복리 계산 (적금, 예금)
def compound_interest(principal, rate, years, compounds_per_year=12):
    """복리 이자 계산"""
    amount = principal * (1 + rate / compounds_per_year) ** (compounds_per_year * years)
    return amount

# 월 50만원 적금, 연 3% 이자, 3년
monthly_saving = 500000
annual_rate = 0.03
years = 3

total_principal = monthly_saving * 12 * years
final_amount = sum(
    compound_interest(monthly_saving, annual_rate, (36 - month) / 12, 12)
    for month in range(36)
)

print(f"\n적금 계산:")
print(f"월 납입액: {monthly_saving:,}원")
print(f"총 납입액: {total_principal:,}원")
print(f"만기 수령액: {final_amount:,.0f}원")
print(f"이자 수익: {final_amount - total_principal:,.0f}원")
```

주식은 매수 총액 4,560,000원에 수수료 684원(4,560,000 × 0.00015)이 붙어 최종 비용이 4,560,684원입니다. 적금은 총 1,800만 원을 넣어 만기에 18,857,306원, 이자 857,306원을 받는다고 나와요. 이 계산은 매달 이자에 이자가 붙는 **월복리**이고 세금도 빼지 않았습니다. 실제 은행 적금은 상품마다 이자 계산 방식이 다르고 이자에서 세금도 떼니, 이 숫자는 계산 방법을 익히는 예제로만 보세요.

### statistics로 데이터 분석

`statistics` 모듈은 기본 통계를 함수 하나씩으로 계산해 줍니다. `mean()`(평균), `median()`(중앙값), `stdev()`(표준편차), `variance()`(분산)이 대표적이에요. 표준편차와 분산은 값들이 평균에서 얼마나 흩어져 있는지를 나타내고, 표준편차를 제곱하면 분산이 됩니다. `quantiles(데이터, n=4)`는 데이터를 4등분하는 경계값 세 개를 돌려주는데, 첫 번째가 1사분위수(하위 25%), 세 번째가 3사분위수(하위 75%)입니다.

```python
import statistics

# 한국 주요 도시 인구 데이터 (만 명)
city_populations = [
    ("서울", 972.1),
    ("부산", 341.4),
    ("인천", 246.6),
    ("대구", 153.8),
    ("대전", 150.2),
    ("광주", 103.5),
    ("울산", 103.4),
    ("수원", 119.5),
    ("창원", 104.0)
]

populations = [pop for city, pop in city_populations]

# 기본 통계
print("한국 주요 도시 인구 통계 (단위: 만 명)")
print(f"평균: {statistics.mean(populations):.1f}")
print(f"중앙값: {statistics.median(populations):.1f}")
print(f"최빈값: 없음 (모든 값이 다름)")
print(f"표준편차: {statistics.stdev(populations):.1f}")
print(f"분산: {statistics.variance(populations):.1f}")

# 사분위수
sorted_pops = sorted(populations)
q1 = statistics.quantiles(sorted_pops, n=4)[0]
q3 = statistics.quantiles(sorted_pops, n=4)[2]
print(f"1사분위수: {q1:.1f}")
print(f"3사분위수: {q3:.1f}")
print(f"사분위수 범위: {q3 - q1:.1f}")

# 회사 직원 연봉 분석
salaries = [3200, 3500, 3800, 4200, 4500, 4800, 5200, 5500, 6000, 7500]  # 만원

print(f"\n직원 연봉 통계 (단위: 만원)")
print(f"평균 연봉: {statistics.mean(salaries):,.0f}")
print(f"중간 연봉: {statistics.median(salaries):,.0f}")
print(f"연봉 표준편차: {statistics.stdev(salaries):.0f}")
```

도시 인구의 평균은 254.9만 명인데 중앙값은 150.2만 명입니다. 서울 하나(972.1만 명)가 평균을 크게 끌어올렸기 때문이에요. 이렇게 한쪽으로 쏠린 데이터에서는 중앙값이 "보통 도시"를 더 잘 보여 줍니다. 표준편차(280.6)가 평균보다도 큰 것도 값들이 고르지 않다는 신호예요.

연봉은 평균 4,820만 원, 중간값 4,650만 원, 표준편차 1294만 원입니다. 표준편차와 분산은 이름이 비슷해서 헷갈리기 쉬운데, 분산은 표준편차의 제곱이라 단위도 '만 원'이 아니라 '만 원의 제곱'이 됩니다. 그래서 "평균에서 대략 얼마나 벗어나 있나"를 말할 때는 원래 단위 그대로인 표준편차를 씁니다. 분산이 필요하다면 `statistics.variance(salaries)`를 쓰면 됩니다.

`quantiles()` 앞에서 `sorted()`로 정렬했지만, `quantiles()`는 알아서 정렬해서 계산하므로 정렬하지 않은 리스트를 넘겨도 결과가 같습니다.

## 컬렉션과 반복

리스트, 딕셔너리, 튜플만으로도 대부분의 일을 할 수 있지만, 자주 하는 일에는 그 일에 딱 맞는 도구가 있으면 편하죠. `collections`는 그런 **특수 용도 자료구조**를, `itertools`는 반복을 조합하는 **부품**을 모아 둔 모듈입니다.

### collections 모듈 활용

6~8장에서 만난 도구들을 한 예제에서 다시 써 봅니다.

- `Counter`: 원소마다 몇 번 나왔는지 세는 딕셔너리. `most_common(5)`로 많이 나온 순서대로 5개를 꺼냅니다.
- `namedtuple`: 이름으로 꺼낼 수 있는 튜플. `student[1]` 대신 `student.국어`라고 쓸 수 있어요.
- `defaultdict(list)`: 없는 키를 꺼내면 빈 리스트를 자동으로 만들어 주는 딕셔너리. "키가 있는지 먼저 확인하고 없으면 만들기"를 생략할 수 있습니다.
- `deque(maxlen=5)`: 양쪽 끝에서 넣고 빼기가 빠른 자료구조. `maxlen`을 정하면 꽉 찼을 때 새 것이 들어오는 만큼 반대쪽 끝의 오래된 것이 밀려 나갑니다.

```python
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
```

단어 빈도 결과에서 '파이썬을'이 2번으로 1등이고, '파이썬은'과 '파이썬의'는 따로 1번씩 셌습니다. 사람 눈에는 모두 '파이썬'인데 왜 이렇게 됐을까요? 한국어는 낱말 뒤에 조사(은, 을, 의…)가 **붙어서** 쓰이기 때문에, 공백으로만 자르면 '파이썬을'과 '파이썬은'이 서로 다른 단어가 됩니다. '언어입니다.'처럼 마침표가 붙은 채로 세어진 것도 같은 이유고요. 한국어 단어를 제대로 세려면 낱말과 조사를 나눠 주는 **형태소 분석기**가 필요합니다. 표준 라이브러리에는 없고, KoNLPy 같은 외부 패키지를 씁니다.

과목별 평균은 국어 85.8점, 영어 85.8점, 수학 88.2점입니다. 최근 접속 기록은 6명이 들어왔지만 `maxlen=5` 때문에 가장 먼저 들어온 김철수의 기록이 밀려 나가고 5개만 남았어요. 이렇게 "최근 N개만 보관"할 때 `deque`가 딱 맞습니다.

### itertools로 효율적인 반복

`itertools`의 도구들은 대부분 결과를 한꺼번에 만들지 않고 **필요할 때 하나씩** 만들어 주는 이터레이터를 돌려줍니다(15장). 그래서 끝이 없는 반복도 다룰 수 있어요.

- `product(A, B)`: A와 B의 모든 짝(곱집합). 부서 3개 × 직급 3개 = 9가지 조합입니다.
- `cycle(목록)`: 목록을 끝없이 되풀이합니다. 끝이 없으니 `zip()`과 함께 써서, 짧은 쪽(요일 5개)이 끝나면 멈추게 하죠.
- `islice(이터레이터, 10)`: 이터레이터에서 처음 10개만 잘라 냅니다. 끝없이 숫자를 내놓는 `fibonacci()` 제너레이터도 이렇게 필요한 만큼만 꺼낼 수 있어요.
- `combinations(목록, 2)`: 순서를 따지지 않고 2개씩 고르는 모든 경우. ('안', '녕')과 ('녕', '안')은 같은 것으로 보고 한 번만 나옵니다.

```python
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
```

음절 다섯 개에서 2개를 고르는 조합은 모두 10가지(5 × 4 ÷ 2)이고, 예제는 그중 앞의 5개만 보여 줍니다. 순서까지 따지는 경우가 필요하면 `permutations()`를 쓰면 되는데, 그때는 20가지가 됩니다.

## 로깅과 디버깅

비행기에는 블랙박스가 있습니다. 평소에는 아무도 들여다보지 않지만, 사고가 나면 "그 순간 무슨 일이 있었는지"를 알려 주는 유일한 기록이죠. 서비스를 운영하는 프로그램에게 **로그(log)** 가 바로 블랙박스입니다. 새벽 3시에 오류가 났는데 로그가 없다면, 무슨 일이 있었는지 알아낼 방법이 없어요.

`print()`로도 기록은 남길 수 있지만 `logging` 모듈은 세 가지가 더 있습니다. 메시지마다 **중요도(레벨)** 를 붙일 수 있고, 같은 메시지를 화면과 파일 등 **여러 곳**에 동시에 보낼 수 있고, 시각·레벨·위치 같은 **정보를 자동으로** 붙여 줍니다.

### 한국어 로그 시스템

레벨은 낮은 것부터 `DEBUG`(개발할 때 보는 자세한 정보), `INFO`(정상적인 주요 사건), `WARNING`(이상하지만 계속 진행 가능), `ERROR`(작업 실패), `CRITICAL`(프로그램 전체가 위험) 순서입니다. `logger.setLevel(logging.DEBUG)`는 DEBUG 이상을 모두 기록하라는 뜻이고, 운영 서버에서는 보통 INFO나 WARNING으로 올려서 자잘한 기록을 줄입니다.

로거의 구조는 세 부품으로 이루어져요. **로거(logger)** 가 메시지를 받으면, 로거에 붙은 **핸들러(handler)** 들이 각자 목적지로 보내고, 핸들러마다 붙은 **포매터(formatter)** 가 한 줄의 모양을 정합니다. 예제는 파일 핸들러(한글이 깨지지 않게 `encoding='utf-8'`)와 콘솔 핸들러를 둘 다 붙여서, 같은 로그가 화면과 `서비스_로그.log` 파일에 함께 남습니다.

뒷부분의 `performance_log`는 10장에서 배운 데코레이터로, 함수 실행 전후에 시작·완료 로그와 걸린 시간을 남깁니다. 실패했을 때도 시간을 기록한 뒤 `raise`로 예외를 다시 던져서, 로그를 남긴다고 오류를 삼키지 않아요.

```python
import logging
import traceback
from datetime import datetime

# 한국어 로거 설정
def setup_korean_logger():
    logger = logging.getLogger('한국_서비스')
    logger.setLevel(logging.DEBUG)
    
    # 파일 핸들러 (한글 지원)
    file_handler = logging.FileHandler('서비스_로그.log', encoding='utf-8')
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    
    # 한국어 포맷터
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_korean_logger()

# 한국어 로그 메시지
def korean_login(username):
    try:
        logger.info(f"사용자 '{username}'님이 로그인을 시도합니다")
        
        # 실제 로그인 로직 (시뮬레이션)
        if username == "관리자":
            raise PermissionError("관리자 계정은 특별한 권한이 필요합니다")
        
        logger.info(f"사용자 '{username}'님 로그인 성공")
        return True
        
    except Exception as e:
        logger.error(f"로그인 오류 발생: {str(e)}")
        logger.debug(f"상세 오류 정보:\n{traceback.format_exc()}")
        return False

# 테스트
korean_login("김철수")
korean_login("관리자")

# 성능 로깅
import time
import functools

def performance_log(func):
    """함수 실행 시간을 로깅하는 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"'{func.__name__}' 함수 실행 시작")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"'{func.__name__}' 함수 실행 완료 (소요시간: {execution_time:.3f}초)")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"'{func.__name__}' 함수 실행 실패 (소요시간: {execution_time:.3f}초): {str(e)}")
            raise
    
    return wrapper

@performance_log
def process_korean_data(data_size):
    """한국어 데이터 처리 시뮬레이션"""
    time.sleep(data_size * 0.001)  # 데이터 크기에 비례한 처리 시간
    return f"{data_size}건의 한국어 데이터 처리 완료"

# 성능 테스트
result = process_korean_data(1000)
print(result)
```

실행하면 `[2024-03-15 10:20:31] INFO - 한국_서비스: 사용자 '김철수'님이 로그인을 시도합니다` 같은 줄이 찍힙니다. 포매터에 적은 대로 시각, 레벨, 로거 이름, 메시지 순서죠. '관리자' 로그인은 `ERROR` 줄과 함께, 레벨을 DEBUG로 열어 두었기 때문에 `traceback.format_exc()`가 만든 오류 추적 내용까지 `DEBUG` 줄로 남습니다. 마지막 데코레이터 예제는 `time.sleep(1.0)`을 기다렸으니 소요시간이 1초 남짓으로 기록돼요.

`logging.getLogger('한국_서비스')`는 같은 이름으로 몇 번을 불러도 **같은 로거 하나**를 돌려준다는 점을 기억하세요. 그래서 `setup_korean_logger()`를 실수로 두 번 부르면 같은 로거에 핸들러가 두 벌 붙어서, 메시지 하나가 화면에 두 번씩 찍힙니다. 로거 설정은 프로그램 시작할 때 한 번만 하세요.

## 동시성과 병렬성

라면 세 개를 끓인다고 해 봅시다. 냄비 하나로 하나씩 끓이면 물 끓기를 세 번 기다려야 하죠. 냄비 세 개를 가스레인지에 올려 두고 번갈아 보면, 기다리는 시간이 겹쳐서 훨씬 빨리 끝납니다. 이것이 **동시성(concurrency)** 이에요. 요리사는 한 명이지만 기다리는 시간을 놀리지 않는 거죠. 요리사를 세 명 두고 각자 하나씩 끓이면 **병렬성(parallelism)** 입니다. 진짜로 동시에 일하는 손이 여러 개인 거예요.

15장에서 본 것처럼, 파이썬(CPython)에는 한 번에 한 스레드만 파이썬 코드를 실행하게 하는 **GIL**이 있습니다. 그래서 고르는 기준이 생겨요.

- 네트워크 응답이나 파일을 **기다리는 일**이 대부분이라면(I/O 작업): 스레드(`threading`, `ThreadPoolExecutor`). 기다리는 동안에는 GIL을 내려놓으니 다른 스레드가 일할 수 있습니다.
- 계산을 **쉬지 않고 하는 일**이라면(CPU 작업): 프로세스(`ProcessPoolExecutor`). 프로세스마다 파이썬이 따로 떠서 GIL도 따로 가지니, CPU 코어 여러 개를 실제로 함께 씁니다.

### threading으로 동시 작업

채팅방 예제는 **생산자-소비자** 구조입니다. 손님 스레드 셋(생산자)이 메시지를 `queue.Queue`에 넣고, 방송 스레드 하나(소비자)가 큐에서 꺼내 전체에 알려요. 식당 주문서 꽂이를 떠올리면 됩니다. 홀 직원들은 주문서를 꽂기만 하고, 주방은 꽂힌 순서대로 하나씩 가져가죠. `queue.Queue`는 여러 스레드가 동시에 넣고 꺼내도 꼬이지 않게 만들어진(스레드 안전한) 자료구조라, 우리가 잠금(lock)을 따로 걸 필요가 없습니다.

`get(timeout=1)`은 1초 동안 기다려도 메시지가 없으면 `queue.Empty` 예외를 내고, 방송 스레드는 이것을 잡아서 `running`이 여전히 `True`인지 다시 확인합니다. 영원히 기다리지 않고 1초마다 "그만할까?"를 확인하는 거예요. `daemon = True`로 만든 스레드는 프로그램이 끝날 때 기다려 주지 않고 함께 종료되는 **보조 스레드**가 됩니다. `join()`은 그 스레드가 끝날 때까지 기다리라는 뜻이고요.

```python
import threading
import time
import queue

# 한국어 채팅 서버 시뮬레이션
class KoreanChatServer:
    def __init__(self):
        self.messages = queue.Queue()
        self.clients = []
        self.running = True
    
    def add_client(self, name):
        self.clients.append(name)
        print(f"{name}님이 채팅방에 입장했습니다")
    
    def send_message(self, sender, message):
        self.messages.put(f"{sender}: {message}")
    
    def broadcast_worker(self):
        """메시지 브로드캐스트 워커 스레드"""
        while self.running:
            try:
                message = self.messages.get(timeout=1)
                print(f"[전체 메시지] {message}")
                self.messages.task_done()
            except queue.Empty:
                continue

# 채팅 서버 테스트
chat_server = KoreanChatServer()

# 브로드캐스트 스레드 시작
broadcast_thread = threading.Thread(target=chat_server.broadcast_worker)
broadcast_thread.daemon = True
broadcast_thread.start()

# 클라이언트들 추가
chat_server.add_client("김철수")
chat_server.add_client("이영희")
chat_server.add_client("박민수")

# 메시지 전송 시뮬레이션
def client_worker(server, name, messages):
    for msg in messages:
        time.sleep(0.5)
        server.send_message(name, msg)

# 여러 클라이언트가 동시에 메시지 전송
clients_threads = [
    threading.Thread(target=client_worker, args=(
        chat_server, "김철수", ["안녕하세요!", "오늘 날씨가 좋네요"]
    )),
    threading.Thread(target=client_worker, args=(
        chat_server, "이영희", ["네, 안녕하세요!", "정말 그렇네요"]
    )),
    threading.Thread(target=client_worker, args=(
        chat_server, "박민수", ["반갑습니다", "좋은 하루 되세요"]
    ))
]

for thread in clients_threads:
    thread.start()

for thread in clients_threads:
    thread.join()

# 정리
time.sleep(2)
chat_server.running = False
```

세 사람이 0.5초 간격으로 두 번씩 말하니, 메시지는 세 개씩 두 차례에 걸쳐 방송됩니다. 같은 차례 안에서 김철수, 이영희, 박민수 중 누구의 메시지가 먼저 나올지는 **실행할 때마다 달라질 수 있어요**. 세 스레드가 거의 같은 순간에 큐에 넣으니, 누가 먼저 넣을지는 운영체제가 스레드를 언제 깨우느냐에 달렸거든요. 여러 스레드를 쓰는 프로그램에서는 "순서가 매번 같다"고 가정하면 안 됩니다.

### concurrent.futures로 병렬 처리

스레드를 하나하나 만들고 `start()`, `join()`하는 대신, `concurrent.futures`는 **일꾼 무리(pool)** 를 만들어 두고 일을 맡기는 방식을 씁니다. `executor.submit(함수, 인자)`로 일을 맡기면 바로 **Future**(나중에 결과를 받을 교환권)를 돌려주고, `future.result()`는 결과가 나올 때까지 기다렸다가 꺼내 줍니다. `ThreadPoolExecutor`와 `ProcessPoolExecutor`는 사용법이 똑같아서, 일의 성격에 따라 이름만 바꾸면 돼요.

예제는 함수와 데이터를 먼저 정의하고, 실제로 일을 맡기는 부분은 모두 `if __name__ == "__main__":` 아래에 넣었습니다. `ProcessPoolExecutor`를 쓸 때는 이 가드가 꼭 필요해요. macOS와 윈도우는 새 프로세스를 만들 때 파이썬을 새로 띄워서 **우리 스크립트 파일을 처음부터 다시 import** 합니다. 가드가 없으면 맨 바깥에 놓인 실행 코드까지 새 프로세스에서 다시 돌면서 프로세스가 끝없이 생기려 하고, 파이썬은 이걸 막으려고 `RuntimeError`를 낸 뒤 `BrokenProcessPool` 오류로 멈춥니다. 14장에서 본 `if __name__ == "__main__":`이 여기서 꼭 필요해지는 거예요. 가드 안의 코드는 이 파일을 직접 실행할 때만 돌고, 새 프로세스가 import할 때는 건너뜁니다.

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

# 한국 뉴스 사이트들에서 데이터 수집 (시뮬레이션)
korean_news_sites = [
    "https://news.naver.com",
    "https://news.daum.net", 
    "https://news.google.com/topstories?hl=ko",
    "https://www.yonhapnews.co.kr",
    "https://news.joins.com"
]

def fetch_news_data(url):
    """뉴스 데이터 수집 시뮬레이션"""
    try:
        # 실제로는 requests.get(url) 사용
        time.sleep(1)  # 네트워크 지연 시뮬레이션
        return f"{url}에서 뉴스 데이터 {len(url)}건 수집 완료"
    except Exception as e:
        return f"{url} 수집 실패: {str(e)}"

# CPU 집약적 작업: 한국어 텍스트 분석
def analyze_korean_text(text_data):
    """한국어 텍스트 분석 (CPU 집약적)"""
    # 복잡한 분석 작업 시뮬레이션
    word_count = 0
    for _ in range(1000000):
        word_count += len(text_data) % 100
    
    return f"텍스트 '{text_data[:20]}...' 분석 완료: {word_count}"

korean_texts = [
    "파이썬은 훌륭한 프로그래밍 언어입니다",
    "한국에서 파이썬 개발자가 늘어나고 있습니다", 
    "데이터 분석과 인공지능 분야에서 파이썬이 인기입니다",
    "웹 개발에서도 파이썬을 많이 사용합니다"
]

# 새 프로세스가 이 파일을 다시 import할 때 아래가 또 실행되지 않도록 막는다
if __name__ == "__main__":
    # 스레드풀로 동시 수집
    print("뉴스 데이터 수집 시작...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fetch_news_data, url) for url in korean_news_sites]

        for future in futures:
            result = future.result()
            print(result)

    end_time = time.time()
    print(f"총 소요시간: {end_time - start_time:.2f}초")

    # 프로세스풀로 CPU 집약적 작업 병렬 처리
    print("\n한국어 텍스트 분석 시작...")
    start_time = time.time()

    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(analyze_korean_text, text) for text in korean_texts]

        for future in futures:
            result = future.result()
            print(result)

    end_time = time.time()
    print(f"총 소요시간: {end_time - start_time:.2f}초")
```

뉴스 수집 부분의 소요시간을 계산해 봅시다. 1초씩 걸리는 일 5개를 일꾼 3명에게 맡겼으니, 첫 차례에 3개, 둘째 차례에 2개를 처리해서 약 2초가 걸립니다(실제로 재 보면 2.01초 정도). 하나씩 했다면 5초였겠죠. `time.sleep()`은 실제 네트워크 대기처럼 **기다리는** 동안 GIL을 내려놓기 때문에 스레드로 시간을 줄일 수 있었던 거예요.

뒷부분의 텍스트 분석은 프로세스 두 개가 나눠서 계산하고, 결과는 문장마다 `분석 완료: 20000000`처럼 나옵니다.

결과가 맡긴 순서대로 출력되는 것도 보세요. `futures` 리스트를 순서대로 돌며 `result()`를 기다리니, 먼저 끝난 일이 있어도 출력은 맡긴 순서를 따릅니다. 끝난 순서대로 받고 싶다면 `concurrent.futures.as_completed(futures)`로 돌면 됩니다.

> **Q. 스레드로는 계산이 왜 빨라지지 않나요?**
> 15장에서 본 GIL 때문입니다. 계산하는 동안에는 파이썬 코드를 쉬지 않고 실행해야 하는데, GIL은 한 번에 한 스레드만 파이썬 코드를 실행하게 하니 스레드를 늘려도 결국 줄을 서서 차례로 계산하게 돼요. `analyze_korean_text()` 같은 계산을 `ThreadPoolExecutor`로 바꿔 재 보면 하나씩 한 것과 별 차이가 없습니다. 프로세스는 각자 자기 파이썬과 자기 GIL을 갖기 때문에 이 줄 서기에서 벗어납니다. 대신 프로세스를 띄우는 비용과, 프로세스끼리 데이터를 주고받는 비용이 들어서 아주 짧은 계산에는 오히려 손해일 수 있어요.

## 시스템과 OS 인터페이스

프로그램이 자기 자신과 자기가 돌아가는 컴퓨터에 대해 알아야 할 때가 있습니다. "지금 파이썬 몇 버전이지?", "여기가 macOS인가 리눅스인가?", "디스크가 얼마나 남았지?" 같은 질문이요.

### sys와 os 모듈

`sys`는 파이썬 실행기 자신에 대한 정보(`sys.version`, `sys.executable`)를, `platform`은 운영체제와 하드웨어 정보를 알려 줍니다. `subprocess.run()`은 터미널 명령을 파이썬 안에서 실행하고, `capture_output=True`, `text=True`를 주면 그 출력을 문자열로 받아 와요. 결과의 `returncode`가 0이면 성공, 아니면 실패라는 것이 운영체제의 약속입니다.

예제는 `platform.system()`이 `"Darwin"`(macOS의 내부 이름)인지 `"Linux"`인지에 따라 다른 명령을 실행합니다. 윈도우에서는 두 조건에 모두 해당하지 않아서 명령 실행 부분을 건너뛰어요.

```python
import sys
import os
import platform
import subprocess

# 시스템 정보 출력
print("=== 한국어 시스템 정보 ===")
print(f"파이썬 버전: {sys.version}")
print(f"운영체제: {platform.system()} {platform.release()}")
print(f"프로세서: {platform.processor()}")
print(f"현재 작업 디렉토리: {os.getcwd()}")
print(f"파이썬 경로: {sys.executable}")

# 한국어 환경변수 설정
os.environ['한국_서비스_설정'] = 'production'
os.environ['LANG'] = 'ko_KR.UTF-8'

print(f"\n언어 설정: {os.environ.get('LANG', '설정되지 않음')}")
print(f"서비스 설정: {os.environ.get('한국_서비스_설정', '기본값')}")

# 시스템 명령 실행
def run_korean_command(command, description):
    """한국어 설명과 함께 시스템 명령 실행"""
    print(f"\n[{description}]")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"성공: {result.stdout.strip()}")
        else:
            print(f"실패: {result.stderr.strip()}")
    except Exception as e:
        print(f"오류: {str(e)}")

# 시스템 정보 수집
if platform.system() == "Darwin":  # macOS
    run_korean_command("sw_vers", "macOS 버전 확인")
    run_korean_command("uptime", "시스템 가동 시간")
elif platform.system() == "Linux":
    run_korean_command("lsb_release -a", "리눅스 배포판 확인")
    run_korean_command("df -h", "디스크 사용량 확인")

# 메모리 사용량 모니터링 (외부 패키지 psutil 필요)
def get_system_status():
    """시스템 상태 정보 수집"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "CPU 사용률": f"{cpu_percent}%",
        "메모리 사용률": f"{memory.percent}%",
        "메모리 사용량": f"{memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB",
        "디스크 사용률": f"{disk.percent}%",
        "디스크 여유공간": f"{disk.free / (1024**3):.1f}GB"
    }

try:
    import psutil
    print("\n=== 시스템 리소스 현황 ===")
    status = get_system_status()
    for key, value in status.items():
        print(f"{key}: {value}")
except ImportError:
    print("psutil 패키지가 설치되지 않음 (uv add psutil)")
```

`subprocess.run()`의 `shell=True`는 명령을 터미널(셸)에 문자열 그대로 넘깁니다. 예제처럼 코드에 직접 적은 명령이라면 괜찮지만, 사용자 입력이 명령 문자열에 섞이면 18장에서 볼 SQL 인젝션과 똑같은 문제가 생겨요. 입력을 다룰 때는 `subprocess.run(["ls", "-l", 폴더])`처럼 명령과 인자를 리스트로 나눠 넘기고 `shell=True`는 빼는 것이 안전합니다.

메모리 사용량 부분은 외부 패키지 `psutil`이 필요합니다(`uv add psutil`). 설치되어 있으면 CPU·메모리·디스크 사용률이 출력되고, 없으면 `psutil 패키지가 설치되지 않음 (uv add psutil)` 안내가 나와요. `import psutil`을 `try` 블록 **안**에 둔 것이 핵심입니다. psutil이 없을 때 오류(`ModuleNotFoundError`, `ImportError`의 하위 예외)가 나는 곳이 바로 그 줄이니까요. `import`를 `try` 바깥에 두면 `except ImportError`까지 가 보지도 못하고 그 줄에서 멈춥니다. 예외를 잡으려면 예외가 **나는 곳**이 `try` 안에 있어야 한다는 것, 12장의 예외 처리 규칙 그대로입니다.

## 고급 활용 패턴과 최적화

지금까지는 모듈 하나하나의 사용법을 봤습니다. 이 절은 그 모듈들을 엮어서 실무에서 자주 만나는 문제, 즉 **큰 파일, 느린 계산, 불안정한 네트워크, 환경마다 다른 설정**을 다루는 패턴을 모아 둔 곳이에요. 앞 절보다 코드가 길고 외부 패키지도 섞여 있으니, 처음 읽을 때는 각 예제가 **무슨 문제를 푸는지**부터 잡고 넘어가도 괜찮습니다.

### 메모리 효율적인 대용량 파일 처리

10GB짜리 CSV 파일을 `readlines()`로 한 번에 읽으면 어떻게 될까요? 메모리가 모자라서 컴퓨터가 멈출 수 있습니다. 큰 파일은 **조금씩 나눠서** 처리해야 해요. 수박을 통째로 입에 넣을 수 없으니 잘라 먹는 것과 같죠.

`process_large_korean_csv()`는 `islice(reader, size)`로 CSV를 1000줄씩 잘라 처리하고, 각 덩어리(chunk)를 `yield`로 하나씩 내보내는 제너레이터입니다. 메모리에는 한 번에 1000줄만 올라와요. 제너레이터라서 함수를 부르기만 해서는 아무 일도 일어나지 않고, `for chunk in process_large_korean_csv(...)`처럼 돌려야 실제로 읽기 시작합니다(15장).

`search_in_large_korean_file()`은 **메모리 매핑(mmap)** 을 씁니다. 파일 내용을 메모리로 복사하지 않고, 운영체제가 파일을 마치 메모리에 있는 큰 바이트 배열처럼 보이게 해 주는 기술이에요. 필요한 부분만 그때그때 디스크에서 읽어 옵니다. mmap은 **바이트** 세상이라, 한글 검색어도 `encode('utf-8')`로 바이트로 바꿔서 찾아야 합니다. 함수가 돌려주는 값은 검색어가 나온 횟수예요.

```python
from pathlib import Path
import mmap
import csv
from itertools import islice

def process_large_korean_csv(file_path, chunk_size=1000):
    """대용량 한글 CSV 파일을 청크 단위로 처리"""
    def csv_chunks(reader, size):
        while True:
            chunk = list(islice(reader, size))
            if not chunk:
                break
            yield chunk
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for chunk in csv_chunks(reader, chunk_size):
            # 각 청크별로 처리
            korean_names = [row['이름'] for row in chunk if row.get('이름')]
            print(f"처리된 한국어 이름 {len(korean_names)}개")
            
            # 메모리 사용량 최적화를 위한 지연 처리
            yield chunk

# 메모리 매핑을 이용한 대용량 텍스트 처리
def search_in_large_korean_file(file_path, search_term):
    """메모리 매핑으로 대용량 한글 파일 검색"""
    with open(file_path, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
            # 한글 검색어를 바이트로 변환
            search_bytes = search_term.encode('utf-8')
            
            position = 0
            matches = []
            
            while True:
                position = mmapped_file.find(search_bytes, position)
                if position == -1:
                    break
                
                matches.append(position)
                position += 1
            
            return len(matches)
```

### 캐싱과 성능 최적화

시험공부를 하다가 한 번 풀어 본 문제의 답을 노트에 적어 두면, 같은 문제가 또 나왔을 때 다시 풀 필요 없이 노트만 보면 되죠. 이것이 **캐싱(caching)** 입니다. 같은 입력에 늘 같은 결과를 내는 함수라면, 한 번 계산한 결과를 기억해 뒀다가 돌려주면 됩니다.

`functools.lru_cache`는 함수에 붙이기만 하면 이 노트를 대신 써 주는 데코레이터예요. LRU(Least Recently Used)는 노트가 꽉 차면(`maxsize=256`) **가장 오랫동안 안 본 답부터 지운다**는 뜻입니다. 아래 예제에는 데코레이터가 두 개 붙어 있습니다. 데코레이터는 아래에서부터 감싸므로, `measure_korean_performance`가 먼저 함수를 감싸고 그 바깥을 `lru_cache`가 감싸요. 그래서 캐시에 답이 있으면 시간 측정 함수까지 들어가지도 않고 바로 답을 돌려줍니다.

```python
from functools import lru_cache, wraps
import time
from typing import Dict, Any

class KoreanDataCache:
    """한국어 데이터 전용 캐시 시스템"""
    
    def __init__(self, maxsize=128):
        self._cache = {}
        self._maxsize = maxsize
        self._stats = {'hits': 0, 'misses': 0}
    
    def get(self, key: str) -> Any:
        """캐시에서 데이터 조회"""
        if key in self._cache:
            self._stats['hits'] += 1
            return self._cache[key]
        
        self._stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        """캐시에 데이터 저장"""
        if len(self._cache) >= self._maxsize:
            # 가장 먼저 넣은 항목을 지워 공간 확보
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[key] = value
    
    def stats(self) -> Dict[str, int]:
        """캐시 통계 반환"""
        return self._stats.copy()

# 성능 측정 데코레이터
def measure_korean_performance(func):
    """함수 실행 성능을 측정하는 한국어 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.perf_counter() - start_time
            
            print(f"[성능] {func.__name__}: {execution_time:.4f}초 소요")
            return result
            
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            print(f"[오류] {func.__name__}: {execution_time:.4f}초 후 실패 - {e}")
            raise
    
    return wrapper

@lru_cache(maxsize=256)
@measure_korean_performance
def expensive_korean_calculation(korean_text: str) -> int:
    """비용이 많이 드는 한국어 계산 (캐싱 적용)"""
    time.sleep(0.1)  # 무거운 계산 시뮬레이션
    
    # 한글 음절 수 계산
    korean_syllables = len([char for char in korean_text if '가' <= char <= '힣'])
    return korean_syllables * 1000

# 사용 예제
result1 = expensive_korean_calculation("안녕하세요 파이썬!")  # 첫 호출 (느림)
result2 = expensive_korean_calculation("안녕하세요 파이썬!")  # 캐시된 결과 (빠름)
```

실행하면 `[성능] expensive_korean_calculation: 0.1050초 소요` 같은 줄이 **딱 한 번만** 찍힙니다. 첫 호출은 0.1초를 기다렸고, 두 번째 호출은 `lru_cache`가 노트에 적힌 답을 바로 돌려줘서 측정 함수가 아예 실행되지 않았거든요. 캐시가 몇 번 맞았는지는 `expensive_korean_calculation.cache_info()`로 확인할 수 있습니다. 캐싱은 결과가 입력에만 달린 함수에만 써야 해요. 현재 시각이나 데이터베이스 내용처럼 바깥 상태에 따라 결과가 바뀌는 함수에 붙이면, 바뀐 뒤에도 옛날 답을 돌려줍니다.

예제 앞부분의 `KoreanDataCache` 클래스는 같은 생각을 직접 구현해 본 캐시입니다. 일반 딕셔너리에 결과를 저장하고, 찾으면 `hits`, 못 찾으면 `misses`를 세요. 꽉 차면 `next(iter(self._cache))`로 딕셔너리의 첫 키, 즉 **가장 먼저 넣은 항목**을 지웁니다. 파이썬 딕셔너리는 넣은 순서를 기억하기 때문에 가능한 방법이에요. 다만 이것은 "가장 오래 안 본 것"을 지우는 진짜 LRU가 아니라 "가장 먼저 넣은 것"을 지우는 방식입니다. 진짜 LRU가 필요하면 직접 만들기보다 `lru_cache`를 쓰세요.

### 비동기 한국어 데이터 처리

15장에서 배운 `async`/`await`를 실전 도구와 엮은 예제입니다. 여러 웹 페이지를 받아 오는 일은 대부분 응답을 **기다리는** 시간이라, 하나를 기다리는 동안 다른 요청을 보내 두면 전체 시간이 크게 줄어요. `asyncio.gather()`가 여러 작업을 한꺼번에 출발시키고 모두 끝나기를 기다립니다.

이 예제는 외부 패키지 두 개를 씁니다. `aiohttp`는 비동기 HTTP 요청을, `aiofiles`는 비동기 파일 읽기를 해 주는 패키지예요(`uv add aiohttp aiofiles`). 표준 라이브러리의 `urllib`나 `open()`은 기다리는 동안 이벤트 루프 전체를 멈춰 세우기 때문에 `async` 코드 안에서 쓰기에 알맞지 않거든요.

`cpu_intensive_korean_analysis()`는 반대 상황을 보여 줍니다. 계산 위주의 일을 `async` 함수 안에서 그냥 실행하면, 계산하는 동안 다른 작업이 모두 멈춥니다. 그래서 `loop.run_in_executor()`로 계산을 스레드 풀에 넘기고, 이벤트 루프는 그 결과를 `await`로 기다리기만 해요. `__aenter__`/`__aexit__`는 `async with`로 쓸 수 있게 해 주는 메서드로, 블록이 끝날 때 HTTP 세션과 스레드 풀을 정리합니다.

```python
import asyncio
import aiohttp
import aiofiles
from concurrent.futures import ThreadPoolExecutor
from typing import List

class AsyncKoreanDataProcessor:
    """비동기 한국어 데이터 처리 클래스"""
    
    def __init__(self, max_workers=5):
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        self.executor.shutdown(wait=True)
    
    async def fetch_korean_news(self, urls: List[str]) -> List[str]:
        """여러 한국 뉴스 사이트에서 동시에 데이터 수집"""
        async def fetch_single(url):
            try:
                async with self.session.get(url) as response:
                    content = await response.text(encoding='utf-8')
                    return f"{url}: {len(content)}바이트 수집"
            except Exception as e:
                return f"{url}: 오류 - {str(e)}"
        
        tasks = [fetch_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def process_korean_files(self, file_paths: List[str]) -> List[str]:
        """여러 한국어 파일을 비동기로 처리"""
        async def process_file(path):
            try:
                async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    korean_chars = len([c for c in content if '가' <= c <= '힣'])
                    return f"{path}: 한글 {korean_chars}자"
            except Exception as e:
                return f"{path}: 오류 - {str(e)}"
        
        tasks = [process_file(path) for path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def cpu_intensive_korean_analysis(self, texts: List[str]) -> List[dict]:
        """CPU 집약적인 한국어 분석을 비동기로 처리"""
        loop = asyncio.get_event_loop()
        
        def analyze_text(text):
            # CPU 집약적 작업은 스레드풀에서 실행
            korean_count = len([c for c in text if '가' <= c <= '힣'])
            word_count = len(text.split())
            complexity = korean_count * word_count
            
            return {
                'text_preview': text[:20] + '...' if len(text) > 20 else text,
                'korean_chars': korean_count,
                'words': word_count,
                'complexity': complexity
            }
        
        # CPU 작업을 스레드풀에서 병렬 실행
        tasks = [
            loop.run_in_executor(self.executor, analyze_text, text)
            for text in texts
        ]
        
        results = await asyncio.gather(*tasks)
        return results

# 사용 예제
async def main_async_example():
    korean_texts = [
        "파이썬은 훌륭한 프로그래밍 언어입니다.",
        "한국에서 파이썬 개발자가 늘어나고 있습니다.",
        "데이터 분석과 인공지능 분야에서 파이썬이 인기입니다."
    ]
    
    async with AsyncKoreanDataProcessor() as processor:
        # CPU 집약적 분석을 비동기로 실행
        analysis_results = await processor.cpu_intensive_korean_analysis(korean_texts)
        
        for result in analysis_results:
            print(f"텍스트: {result['text_preview']}")
            print(f"한글: {result['korean_chars']}자, 단어: {result['words']}개")
            print(f"복잡도: {result['complexity']}")
            print()

# asyncio.run(main_async_example())  # 주석 해제하여 실행
```

마지막 줄의 주석을 풀고 실행하면 세 문장마다 한글 글자 수, 단어 수, 그 둘을 곱한 '복잡도'가 출력됩니다. 예제가 실제로 실행하는 것은 계산 부분뿐이라 인터넷 연결은 필요 없지만, 파일 맨 위에서 `aiohttp`와 `aiofiles`를 불러오므로 두 패키지는 설치되어 있어야 해요.

함수 안의 `asyncio.get_event_loop()`는 실행 중인 루프를 얻으려고 쓴 것인데, `async` 함수 안에서는 `asyncio.get_running_loop()`가 정확한 표현입니다. 비슷한 일을 더 짧게 하고 싶다면 파이썬 3.9부터 생긴 `await asyncio.to_thread(함수, 인자)`도 있습니다.

### 에러 처리와 복원력

네트워크는 가끔 끊기고, 서버는 가끔 바쁘다며 요청을 거절합니다. 이런 **일시적인 실패**는 잠깐 기다렸다 다시 시도하면 대부분 성공해요. 전화가 안 받아지면 조금 있다 다시 거는 것처럼요. 이 예제는 실패에 대비하는 세 가지 도구를 한 클래스에 모았습니다.

- `handle_korean_error()`: 예외 종류에 맞는 한국어 설명을 붙여 로그로 남깁니다. `type(error)`로 딕셔너리에서 설명을 찾기 때문에, `ValueError`를 상속한 하위 예외는 정확히 같은 종류가 아니라서 "알 수 없는 오류"로 분류됩니다.
- `safe_korean_operation()`: 작업의 시작·성공·실패를 자동으로 기록하는 컨텍스트 매니저입니다. 실패하면 기록한 뒤 예외를 다시 던져요.
- `retry_korean_operation()`: 실패하면 `delay`초 쉬었다가 최대 `max_attempts`번까지 다시 시도하는 데코레이터입니다. 매개변수를 받는 데코레이터라서 함수가 세 겹으로 감싸여 있어요(10장).

```python
import logging
import time
from contextlib import contextmanager
from typing import Optional, Type, Callable
import traceback
from functools import wraps

class KoreanErrorHandler:
    """한국어 에러 처리 시스템"""
    
    def __init__(self, logger_name='한국_에러_처리'):
        self.logger = logging.getLogger(logger_name)
        self.setup_logger()
    
    def setup_logger(self):
        """한국어 로거 설정"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def handle_korean_error(self, operation: str, error: Exception):
        """한국어 에러 메시지 처리"""
        error_messages = {
            FileNotFoundError: "파일을 찾을 수 없습니다",
            PermissionError: "권한이 없습니다",
            ValueError: "잘못된 값입니다",
            TypeError: "타입 오류입니다",
            KeyError: "키를 찾을 수 없습니다",
            UnicodeDecodeError: "한글 인코딩 오류입니다"
        }
        
        error_type = type(error)
        korean_msg = error_messages.get(error_type, "알 수 없는 오류입니다")
        
        self.logger.error(f"{operation} 중 {korean_msg}: {str(error)}")
        self.logger.debug(f"상세 오류:\n{traceback.format_exc()}")
    
    @contextmanager
    def safe_korean_operation(self, operation_name: str):
        """안전한 한국어 작업 컨텍스트 매니저"""
        try:
            self.logger.info(f"{operation_name} 시작")
            yield
            self.logger.info(f"{operation_name} 성공적으로 완료")
        except Exception as e:
            self.handle_korean_error(operation_name, e)
            raise
    
    def retry_korean_operation(self, max_attempts=3, delay=1.0):
        """한국어 작업 재시도 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        if attempt > 0:
                            time.sleep(delay)
                            self.logger.info(f"{func.__name__} {attempt + 1}번째 재시도")
                        
                        return func(*args, **kwargs)
                        
                    except Exception as e:
                        last_exception = e
                        self.logger.warning(f"{func.__name__} {attempt + 1}번째 시도 실패: {str(e)}")
                
                self.handle_korean_error(f"{func.__name__} 최종", last_exception)
                raise last_exception
            
            return wrapper
        return decorator

# 사용 예제
error_handler = KoreanErrorHandler()

@error_handler.retry_korean_operation(max_attempts=3, delay=0.5)
def unreliable_korean_function():
    """불안정한 한국어 처리 함수"""
    import random
    if random.random() < 0.7:  # 70% 확률로 실패
        raise ValueError("임의의 한글 처리 오류")
    return "한글 처리 성공!"

# 안전한 파일 처리 예제
def safe_korean_file_processing():
    with error_handler.safe_korean_operation("한글 파일 처리"):
        korean_content = "안녕하세요 파이썬!"
        
        # 파일 쓰기
        with open("테스트_한글.txt", "w", encoding="utf-8") as f:
            f.write(korean_content)
        
        # 파일 읽기
        with open("테스트_한글.txt", "r", encoding="utf-8") as f:
            content = f.read()
            print(f"읽은 내용: {content}")
```

이 예제는 함수를 정의만 하고 부르지 않으니, 실행해도 아무것도 출력되지 않습니다. 직접 `unreliable_korean_function()`을 불러 보세요. 70% 확률로 실패하도록 만들었으니, 부를 때마다 결과가 달라집니다. 운이 좋으면 첫 시도에 "한글 처리 성공!"이 나오고, 실패하면 `WARNING` 로그를 남기며 0.5초 간격으로 다시 시도하다가, 세 번 모두 실패하면 `ERROR` 로그와 함께 `ValueError`가 올라와요.

`retry_korean_operation()`이 `except Exception`으로 **모든** 예외를 잡는다는 점은 조심해야 합니다. 예를 들어 맨 위의 `import time`을 빠뜨리면, 두 번째 시도의 `time.sleep()`에서 난 `NameError`까지 "시도 실패"로 잡혀서 로그에는 `2번째 시도 실패: name 'time' is not defined`가 찍히고, 함수는 한 번도 다시 실행되지 못한 채 마지막에 `NameError`가 올라옵니다. 첫 시도에 성공하면 `time.sleep()`까지 가지 않으니, 이런 실수는 실패할 때만 드러나서 찾기도 어려워요. 넓게 잡는 `except`가 오타 같은 버그까지 삼키는 전형적인 모습입니다(12장). 실패 경로도 꼭 실행해 봐야 하는 이유예요.

마지막으로, 모든 예외를 재시도하는 것은 위험합니다. 비밀번호가 틀린 것처럼 다시 해도 결과가 같은 오류까지 세 번씩 시도하면 시간만 버리고, 경우에 따라서는 계정이 잠기기도 해요. 실무에서는 재시도할 예외 종류를 정해 두고, 재시도 간격도 1초, 2초, 4초처럼 점점 늘리는 방식을 많이 씁니다.

### 설정 관리와 환경별 구성

같은 프로그램이라도 내 컴퓨터(개발), 테스트 서버, 실제 서비스(운영)에서는 데이터베이스 주소, 로그 수준, 디버그 모드가 달라야 합니다. 이 값들을 코드 곳곳에 흩어 적으면 환경을 옮길 때마다 코드를 고쳐야 하죠. 그래서 설정은 **한 곳에 모으고, 바깥에서 바꿀 수 있게** 만듭니다.

예제는 세 단계로 설정을 쌓아요. ① `KoreanAppConfig` 데이터클래스의 **기본값**에서 시작해서, ② `config/development.json` 같은 **환경별 파일**이 있으면 그 값으로 덮어쓰고, ③ `KOREAN_DEBUG` 같은 **환경변수**가 있으면 마지막으로 그 값으로 덮어씁니다. 나중 것이 이기는 구조라서, 운영 서버에서는 파일을 고치지 않고 환경변수만 바꿔서 설정을 조정할 수 있어요.

`api_keys`처럼 딕셔너리를 기본값으로 쓰는 필드에 `field(default_factory=dict)`를 쓴 것도 보세요. 데이터클래스에서 `api_keys: dict = {}`라고 쓰면 모든 객체가 **딕셔너리 하나를 함께 쓰게** 되는 문제가 있어서, 파이썬이 아예 `ValueError`로 막아 둡니다. `default_factory`는 객체를 만들 때마다 새 딕셔너리를 만들어 줍니다. 환경변수 값은 늘 문자열이라 `_override_with_env_vars()`가 `int`나 "true 비교" 함수로 알맞은 자료형으로 바꿔 넣는 것도 눈여겨보세요.

```python
import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from configparser import ConfigParser

@dataclass
class KoreanAppConfig:
    """한국어 앱 설정 클래스"""
    
    # 기본 설정
    app_name: str = "한국_파이썬_앱"
    version: str = "1.0.0"
    debug: bool = False
    
    # 데이터베이스 설정
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "korean_db"
    db_user: str = "postgres"
    db_password: str = ""
    
    # 로깅 설정
    log_level: str = "INFO"
    log_file: str = "한국_앱.log"
    
    # 한국어 설정
    locale: str = "ko_KR.UTF-8"
    timezone: str = "Asia/Seoul"
    date_format: str = "%Y년 %m월 %d일"
    
    # API 설정
    api_keys: Dict[str, str] = field(default_factory=dict)
    external_apis: Dict[str, str] = field(default_factory=lambda: {
        "weather": "https://api.openweathermap.org/data/2.5",
        "news": "https://newsapi.org/v2",
        "translate": "https://openapi.naver.com/v1/papago"
    })

class KoreanConfigManager:
    """한국어 설정 관리자"""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path("config")
        self.config_dir.mkdir(exist_ok=True)
        
        self.environments = ["development", "testing", "production"]
        self.current_env = os.environ.get("KOREAN_ENV", "development")
    
    def load_config(self, env: Optional[str] = None) -> KoreanAppConfig:
        """환경별 설정 로드"""
        env = env or self.current_env
        
        # 기본 설정으로 시작
        config = KoreanAppConfig()
        
        # 환경별 JSON 설정 파일 로드
        config_file = self.config_dir / f"{env}.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
        
        # 환경변수로 오버라이드
        self._override_with_env_vars(config)
        
        return config
    
    def save_config(self, config: KoreanAppConfig, env: str):
        """설정을 파일로 저장"""
        config_file = self.config_dir / f"{env}.json"
        config_dict = {
            key: getattr(config, key)
            for key in dir(config)
            if not key.startswith('_')
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
    
    def _override_with_env_vars(self, config: KoreanAppConfig):
        """환경변수로 설정 오버라이드"""
        env_mappings = {
            'KOREAN_DEBUG': ('debug', lambda x: x.lower() == 'true'),
            'KOREAN_DB_HOST': ('db_host', str),
            'KOREAN_DB_PORT': ('db_port', int),
            'KOREAN_LOG_LEVEL': ('log_level', str),
            'KOREAN_LOCALE': ('locale', str)
        }
        
        for env_var, (config_attr, converter) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                try:
                    setattr(config, config_attr, converter(value))
                except (ValueError, TypeError) as e:
                    print(f"환경변수 {env_var} 변환 실패: {e}")

# 사용 예제
config_manager = KoreanConfigManager()

# 개발 환경 설정 로드
dev_config = config_manager.load_config("development")
print(f"앱 이름: {dev_config.app_name}")
print(f"디버그 모드: {dev_config.debug}")
print(f"타임존: {dev_config.timezone}")
```

처음 실행하면 `config` 폴더만 생기고 `development.json`은 아직 없으니 기본값 그대로 `한국_파이썬_앱`, `False`, `Asia/Seoul`이 나옵니다. 터미널에서 `KOREAN_DEBUG=true uv run python 파일명.py`처럼 환경변수를 주고 실행하면 디버그 모드만 `True`로 바뀌어요. 데이터베이스 비밀번호(`db_password`) 같은 값은 설정 파일에도 적지 말고 환경변수로만 넘기는 것이 안전합니다. 설정 파일은 git에 함께 올라가기 쉬우니까요.

## 성능 모니터링과 프로파일링

"프로그램이 느려요"라는 말을 들으면 어디부터 고쳐야 할까요? 짐작으로 고치면 안 됩니다. 의사가 엑스레이부터 찍듯이, 먼저 **어느 함수가 시간을 얼마나 쓰는지** 재야 해요. 이것을 **프로파일링(profiling)** 이라고 합니다. 느린 원인은 대개 우리가 짐작한 곳이 아니라 엉뚱한 곳에 있거든요.

표준 라이브러리의 `cProfile`은 함수마다 몇 번 불렸고 시간이 얼마나 걸렸는지를 기록하고, `pstats`는 그 기록을 정렬해서 보여 줍니다. 예제의 `profile_function` 데코레이터는 여기에 메모리 사용량까지 함께 재는데, 메모리 측정에 쓴 `memory_profiler`는 외부 패키지라서 설치가 필요합니다(`uv add memory_profiler`).

예제에서 `stats.sort_stats('cumulative')`로 정렬만 하고 출력은 하지 않는 점도 알아 두세요. 함수별 기록을 직접 보려면 그 아래에 `stats.print_stats(10)`을 더하면 됩니다. 누적 시간이 큰 순서로 상위 10개 함수가 표로 나와요. 데코레이터를 쓰지 않고 스크립트 전체를 재고 싶다면, 코드를 고칠 필요 없이 터미널에서 `uv run python -m cProfile -s cumulative 파일명.py`로 실행하면 됩니다.

```python
import cProfile
import pstats
import memory_profiler
import time
from functools import wraps
from typing import Callable

class KoreanPerformanceMonitor:
    """한국어 성능 모니터링 시스템"""
    
    def __init__(self):
        self.metrics = {}
    
    def profile_function(self, func: Callable):
        """함수 프로파일링 데코레이터"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # CPU 프로파일링
            profiler = cProfile.Profile()
            profiler.enable()
            
            # 메모리 사용량 측정 시작
            start_memory = memory_profiler.memory_usage()[0]
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                
                # 측정 종료
                end_time = time.perf_counter()
                end_memory = memory_profiler.memory_usage()[0]
                profiler.disable()
                
                # 결과 저장
                function_name = func.__name__
                self.metrics[function_name] = {
                    'execution_time': end_time - start_time,
                    'memory_delta': end_memory - start_memory,
                    'memory_peak': max(memory_profiler.memory_usage()),
                    'call_count': self.metrics.get(function_name, {}).get('call_count', 0) + 1
                }
                
                # 프로파일 결과 저장
                stats = pstats.Stats(profiler)
                stats.sort_stats('cumulative')
                
                print(f"\n=== {function_name} 성능 리포트 ===")
                print(f"실행시간: {end_time - start_time:.4f}초")
                print(f"메모리 변화: {end_memory - start_memory:.2f}MB")
                print(f"호출 횟수: {self.metrics[function_name]['call_count']}")
                
                return result
                
            except Exception as e:
                profiler.disable()
                print(f"함수 {function_name} 실행 중 오류 발생: {e}")
                raise
        
        return wrapper
    
    def get_performance_summary(self) -> dict:
        """성능 요약 정보 반환"""
        if not self.metrics:
            return {"message": "수집된 성능 데이터가 없습니다"}
        
        summary = {}
        for func_name, metrics in self.metrics.items():
            summary[func_name] = {
                'average_time': metrics['execution_time'] / metrics['call_count'],
                'total_time': metrics['execution_time'],
                'call_count': metrics['call_count'],
                'memory_usage': metrics['memory_delta']
            }
        
        return summary

# 전역 성능 모니터
performance_monitor = KoreanPerformanceMonitor()

@performance_monitor.profile_function
def process_large_korean_dataset():
    """대용량 한국어 데이터 처리 시뮬레이션"""
    korean_words = ["안녕", "하세요", "파이썬", "프로그래밍"] * 100000
    
    # CPU 집약적 작업
    result = []
    for word in korean_words:
        processed = word.upper() + "_처리됨"
        result.append(processed)
    
    # 메모리 집약적 작업
    large_dict = {f"키_{i}": f"한글_값_{i}" for i in range(50000)}
    
    return len(result), len(large_dict)

# 성능 테스트 실행
# result = process_large_korean_dataset()
# summary = performance_monitor.get_performance_summary()
# print("\n전체 성능 요약:", summary)
```

이 장에서는 파이썬 표준 라이브러리의 핵심 모듈들을 한국 개발 환경에 맞춘 예제로 둘러봤습니다. 한글 텍스트와 유니코드, 한국 시간대와 공휴일, 파일 인코딩처럼 우리가 자주 마주치는 문제부터, 로깅과 동시성, 캐싱, 재시도, 설정 관리, 프로파일링 같은 실무 패턴까지요.

이 모든 모듈을 외울 필요는 없습니다. 기억할 것은 하나예요. **무언가를 직접 만들기 전에, 표준 라이브러리에 이미 있는지 먼저 찾아본다.** 그리고 공휴일 예제에서 봤듯이, 표준 라이브러리에 없는 것은 검증된 외부 패키지를 찾아보고, 어느 쪽이든 결과는 직접 실행해서 확인하세요.

다음 장에서는 표준 라이브러리에 들어 있는 또 하나의 모듈, `sqlite3`로 데이터베이스를 다룹니다. 이 장에서 JSON과 CSV 파일에 데이터를 저장했다면, 다음 장에서는 데이터를 찾고, 묶고, 안전하게 고치는 일을 전문으로 하는 데이터베이스에 저장하는 방법을 배웁니다.