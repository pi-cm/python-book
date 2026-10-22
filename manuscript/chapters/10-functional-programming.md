# Chapter 10: 함수형 프로그래밍

> **학습 목표**  
> - 함수 정의와 매개변수 고급 활용법 습득
> - 람다 함수와 고차 함수의 함수형 패러다임 이해
> - map(), filter(), reduce() 등 내장 함수 활용
> - 데코레이터를 통한 함수 래핑과 메타프로그래밍
> - 클로저와 스코프 심화 이해
> - 한국어 자연어 처리 파이프라인 구현

---

## 들어가며: 함수도 값이에요

9장에서 함수를 만들고 부르는 법을 배웠죠. 이번 장은 질문 하나로 시작해 볼게요. `print`라는 이름 뒤에 괄호를 붙이지 않고 그냥 `print`라고만 쓰면 무엇이 나올까요?

```python
출력 = print
출력("함수도 변수에 담을 수 있어요")
```

`print` 함수가 `출력`이라는 새 이름표를 하나 더 달았을 뿐, 똑같이 동작합니다. 파이썬에서는 함수도 숫자나 문자열처럼 **값**이에요. 변수에 담을 수 있으니 다른 함수에 넘길 수도 있고, 함수가 함수를 만들어 돌려줄 수도 있습니다.

이 성질을 적극적으로 쓰는 방식이 **함수형 프로그래밍**입니다. 작은 함수를 레고 블록처럼 만들어 두고, 그것을 조립해서 큰 일을 해내는 거죠. 이 장에서는 매개변수를 더 깊이 다룬 다음(10.1절), 이름 없는 짧은 함수인 람다와 함수를 주고받는 고차 함수, `map`/`filter`/`reduce`, 함수에 기능을 덧입히는 데코레이터, 그리고 함수가 태어난 곳을 기억하는 클로저까지 차례로 만납니다.

## 10.1 함수 정의 심화: 매개변수 더 깊이

### 기본 함수 정의

이제 앞에서 다진 기초 위에 몇 가지를 더 얹어 봅시다. 아래 함수에는 두 가지가 새로 보입니다.

**첫째, 타입 힌트**입니다. `name: str`은 "이 매개변수에는 문자열이 오길 바란다", `-> str`은 "이 함수는 문자열을 돌려준다"는 표시예요. 파이썬은 입력과 출력의 타입을 **강제하지는 않습니다**. 다른 타입을 넣어도 실행은 돼요. 대신 읽는 사람과 편집기에게 "이렇게 써 주세요"라고 **제안**합니다. 함수에 적힌 타입 힌트는 `greet_korean.__annotations__`로 꺼내 볼 수 있습니다.

**둘째, 독스트링(docstring)** 입니다. 함수 첫 줄의 `"""한국식 인사 함수"""`처럼 따옴표 세 개로 감싼 설명문이에요. 주석과 달리 함수에 붙어 다녀서 `help(greet_korean)`으로 볼 수 있습니다. 코드는 쓰는 시간보다 읽히는 시간이 훨씬 길어요. 정해진 팀 규칙이 없다면 PEP 257(독스트링 작성 관례)을 따르는 것이 무난합니다. 핵심만 추리면 이렇습니다.

- 한 줄짜리여도 따옴표 세 개를 쓰고, 여는 따옴표와 닫는 따옴표를 같은 줄에 둡니다.
- 여러 줄이면 첫 줄에 한 줄 요약, 빈 줄 하나, 그다음 자세한 설명을 씁니다.
- 함수라면 무엇을 받아 무엇을 돌려주는지, 어떤 예외를 일으키는지 적습니다.

`calculate_korean_age()`의 `current_year: Optional[int] = None`도 보세요. 기본값을 `None`으로 두고 함수 안에서 "값이 안 들어왔으면 올해로" 채우는 방식입니다. 기본값 자리에 `datetime.now().year`를 바로 쓰면 함수를 **정의할 때 한 번만** 계산되어, 해가 바뀌어도 프로그램을 다시 시작하기 전까지는 옛 연도가 쓰이기 때문이에요. 타입 힌트를 `int`가 아니라 `Optional[int]`로 적은 것도 같은 이유입니다. "정수 또는 `None`"이 들어올 수 있다는 뜻이라, 기본값 `None`과 힌트가 서로 맞아요.

```python
from typing import Optional

def greet_korean(name: str, age: Optional[int] = None) -> str:
    """한국식 인사 함수"""
    if age is not None:
        return f"안녕하세요, {name}님! {age}세이시군요."
    return f"안녕하세요, {name}님!"

def calculate_korean_age(birth_year: int, current_year: Optional[int] = None) -> int:
    """세는 나이 계산 (올해 - 출생연도 + 1)"""
    if current_year is None:
        from datetime import datetime
        current_year = datetime.now().year
    
    international_age = current_year - birth_year
    korean_age = international_age + 1  # 한국 나이는 태어나면서 1세
    return korean_age

# 사용 예제
print(greet_korean("김철수"))
print(greet_korean("이영희", 25))

korean_age = calculate_korean_age(1995)
print(f"1995년생의 한국 나이: {korean_age}세")
```

`greet_korean("김철수")`처럼 나이를 빼고 부르면 기본값 `None`이 들어가서 이름만 넣은 인사가 나옵니다. 마지막 줄의 나이는 실행하는 해에 따라 달라져요. 참고로 이 함수가 계산하는 것은 태어나자마자 1살로 치는 "세는 나이"입니다. 우리나라는 2023년 6월부터 법령과 공문서에서 만 나이를 쓰도록 통일했으니, 실제 서비스에서 나이를 다룬다면 만 나이로 계산하세요.

### 고급 매개변수 활용

앞에서 본 `*`와 `**`를 실제 함수에 써 봅시다. `format_korean_address()`는 주소 조각을 몇 개든 `*address_parts`로 받고, 그 뒤의 `separator`와 `postal_code`는 기본값이 있는 매개변수입니다. `*` 뒤에 온 매개변수는 위치로는 값을 받을 수 없어서 **반드시 키워드 인자로** 넘겨야 해요. 그렇지 않으면 주소 조각인지 우편번호인지 구분할 방법이 없으니까요.

`create_student_profile()`은 이름만 꼭 받고 나머지는 `**kwargs`로 받습니다. `kwargs`는 평범한 딕셔너리라서 `kwargs.get("age", "미입력")`처럼 없는 키에 기본값을 주며 꺼낼 수 있어요. 미리 정해 둔 키가 아닌 것(`hobby`, `mbti`)은 따로 모아 "추가정보"에 넣습니다.

```python
def format_korean_address(*address_parts, separator=" ", postal_code=None):
    """한국 주소 포맷팅"""
    if not address_parts:
        return "주소가 입력되지 않았습니다."
    
    formatted_address = separator.join(address_parts)
    
    if postal_code:
        formatted_address = f"({postal_code}) {formatted_address}"
    
    return formatted_address

def create_student_profile(name: str, **kwargs) -> dict:
    """학생 프로필 생성 (키워드 인자 활용)"""
    profile = {
        "이름": name,
        "나이": kwargs.get("age", "미입력"),
        "전공": kwargs.get("major", "미정"),
        "학년": kwargs.get("grade", 1),
        "연락처": kwargs.get("phone", "미입력"),
        "이메일": kwargs.get("email", "미입력")
    }
    
    # 추가 정보가 있다면 포함
    extra_info = {k: v for k, v in kwargs.items() 
                  if k not in ["age", "major", "grade", "phone", "email"]}
    
    if extra_info:
        profile["추가정보"] = extra_info
    
    return profile

# 사용 예제
print("주소 포맷팅:")
print(format_korean_address("서울시", "강남구", "역삼동", "123-45"))
print(format_korean_address("부산시", "해운대구", "우동", postal_code="48094"))

print("\n학생 프로필:")
student = create_student_profile(
    "김철수",
    age=20,
    major="컴퓨터과학과",
    grade=2,
    phone="010-1234-5678",
    hobby="프로그래밍",
    mbti="ISTJ"
)

for key, value in student.items():
    print(f"{key}: {value}")
```

첫 번째 주소는 우편번호를 주지 않아 조각만 공백으로 이어졌고, 두 번째는 `postal_code="48094"`를 키워드로 넘겨 `(48094) 부산시 해운대구 우동`이 되었습니다. 학생 프로필에서는 넘기지 않은 `email`이 `미입력`으로, 정해 두지 않은 `hobby`와 `mbti`가 `추가정보: {'hobby': '프로그래밍', 'mbti': 'ISTJ'}`로 나와요.

### 키워드 전용 매개변수 (Python 3+)

대출 계산기를 떠올려 봅시다. 원금, 이율, 기간은 누구나 순서를 짐작할 수 있지만, 상환 방식이나 보험 포함 여부까지 위치로 넘기면 `calc(300000000, 0.035, 20, "equal_payment", True, 0.005)`처럼 무엇이 무엇인지 알 수 없는 호출이 됩니다.

매개변수 목록 중간에 별표 하나 `*`만 단독으로 쓰면, **그 뒤의 매개변수는 키워드로만 받겠다**는 뜻이 됩니다. 앞의 `*args`처럼 값을 모으지는 않고 경계선 역할만 해요. 위치로 넘기려 하면 `TypeError`가 나니, 부르는 쪽은 `payment_type="equal_payment"`처럼 이름을 적을 수밖에 없습니다. 읽기 쉬운 호출을 강제하는 장치예요.

```python
def calculate_loan_payment(
    principal: int,        # 원금
    rate: float,          # 연이율
    years: int,           # 대출 기간
    *,                    # 이후 매개변수는 키워드 전용
    payment_type: str = "equal_payment",  # 상환 방식
    include_insurance: bool = False,       # 보험 포함 여부
    insurance_rate: float = 0.005         # 보험료율
) -> dict:
    """한국 주택담보대출 계산기"""
    
    monthly_rate = rate / 12
    total_months = years * 12
    
    if payment_type == "equal_payment":  # 원리금균등상환
        if monthly_rate == 0:
            monthly_payment = principal / total_months
        else:
            monthly_payment = principal * (
                monthly_rate * (1 + monthly_rate) ** total_months
            ) / ((1 + monthly_rate) ** total_months - 1)
    
    elif payment_type == "equal_principal":  # 원금균등상환
        monthly_principal = principal / total_months
        # 첫 달 이자 (최대 이자)
        first_month_interest = principal * monthly_rate
        monthly_payment = monthly_principal + first_month_interest
    
    else:
        raise ValueError("payment_type은 'equal_payment' 또는 'equal_principal'이어야 합니다.")
    
    # 보험료 계산
    insurance_payment = 0
    if include_insurance:
        insurance_payment = principal * insurance_rate / 12
        monthly_payment += insurance_payment
    
    total_payment = monthly_payment * total_months
    total_interest = total_payment - principal
    
    return {
        "원금": f"{principal:,}원",
        "월상환액": f"{monthly_payment:,.0f}원",
        "총상환액": f"{total_payment:,.0f}원", 
        "총이자": f"{total_interest:,.0f}원",
        "상환방식": "원리금균등" if payment_type == "equal_payment" else "원금균등",
        "보험료": f"{insurance_payment:,.0f}원" if include_insurance else "없음"
    }

# 사용 예제 (키워드 전용 매개변수 활용)
loan1 = calculate_loan_payment(
    300000000,  # 3억원
    0.035,      # 3.5%
    20,         # 20년
    payment_type="equal_payment",
    include_insurance=True
)

print("주택담보대출 계산 결과:")
for key, value in loan1.items():
    print(f"{key}: {value}")
```

3억 원을 연 3.5%로 20년 동안 원리금균등 방식으로 갚으면 월 상환액이 약 186만 원(보험료 12만 5천 원 포함)으로 나옵니다. 앞의 세 값은 주석만 보고도 무엇인지 알 수 있게 위치로 넘겼고, 뒤의 두 값은 이름을 붙여 넘겼어요. 결과를 문자열이 든 딕셔너리로 돌려주는 것도 눈여겨보세요. 함수 하나가 여러 값을 돌려주고 싶을 때는 이렇게 딕셔너리나 튜플에 묶어서 `return`합니다.

## 10.2 람다 함수와 고차 함수

### 람다 함수 기본 활용

**람다(lambda)** 는 이름 없이 한 줄로 만드는 작은 함수입니다. `lambda x: x["점수"]`는 "`x`를 받아 `x["점수"]`를 돌려주는 함수"로, 아래 `def`와 같은 일을 해요.

```python
def get_score(x):
    return x["점수"]
```

람다가 가장 빛나는 자리는 `sorted()`, `max()`의 `key=`처럼 **함수를 잠깐 건네줘야 하는 곳**입니다. "점수를 기준으로 정렬해 줘"라고 말하려고 함수를 따로 만들고 이름까지 짓기는 번거로우니까요.

아래 예제의 `groupby()`는 이웃한 원소 중 기준값이 같은 것끼리 묶어 줍니다. **이웃한** 것끼리만 묶으므로, 먼저 같은 기준으로 정렬해 두어야 학과별로 제대로 모여요.

```python
# 한국어 정렬을 위한 람다 함수들
korean_students = [
    {"이름": "김철수", "점수": 85, "학과": "컴퓨터"},
    {"이름": "이영희", "점수": 92, "학과": "경영"}, 
    {"이름": "박민수", "점수": 78, "학과": "컴퓨터"},
    {"이름": "최지영", "점수": 88, "학과": "경영"},
    {"이름": "정수진", "점수": 95, "학과": "수학"}
]

# 점수순 정렬
by_score = sorted(korean_students, key=lambda x: x["점수"], reverse=True)
print("점수순 정렬:")
for student in by_score[:3]:
    print(f"{student['이름']}: {student['점수']}점")

# 이름순 정렬 (한글 가나다순)
by_name = sorted(korean_students, key=lambda x: x["이름"])
print(f"\n이름순 정렬: {[s['이름'] for s in by_name]}")

# 학과별 그룹핑 후 점수순 정렬
from itertools import groupby

grouped = groupby(
    sorted(korean_students, key=lambda x: x["학과"]), 
    key=lambda x: x["학과"]
)

print("\n학과별 최고점:")
for department, students in grouped:
    student_list = list(students)
    top_student = max(student_list, key=lambda x: x["점수"])
    print(f"{department}과: {top_student['이름']} ({top_student['점수']}점)")
```

이름순 정렬 결과는 `['김철수', '박민수', '이영희', '정수진', '최지영']`으로 가나다순입니다. 한글도 유니코드 번호가 가나다순으로 매겨져 있어서 문자열 비교만으로 정렬돼요. 학과별 최고점은 정렬된 학과 이름 순서대로 경영, 수학, 컴퓨터가 나옵니다.

> **Q. 람다는 쓰지 말라는 말을 들었는데, 왜인가요?**
> 정확히는 "람다를 **변수에 담아 이름을 붙여 쓰지 말라**"는 권고입니다. 파이썬 스타일 가이드 PEP 8은 `square = lambda x: x ** 2`처럼 람다를 이름에 바로 할당하지 말고 `def square(x):`로 쓰라고 합니다. 이름을 붙일 거라면 `def`가 더 읽기 쉽고, 오류가 났을 때 추적 메시지에 `<lambda>` 대신 진짜 함수 이름이 찍혀 어디서 문제가 생겼는지 찾기 쉽기 때문이에요. 위 예제처럼 `key=`에 잠깐 건네는 짧은 람다는 문제없습니다. 다만 람다 안에 조건이 여러 개 들어가 한눈에 읽히지 않는다면, 그때는 이름 있는 함수로 꺼내는 편이 유지보수와 재사용에 좋습니다.

### 고차 함수 구현

파이썬에서 함수는 **일급 객체(first-class object)** 입니다. 숫자나 문자열처럼 함수도 변수에 담고, 리스트에 넣고, 다른 함수의 인자로 넘기고, 반환값으로 돌려줄 수 있다는 뜻이에요. 괄호를 붙이면 함수를 **부르는** 것이고, 괄호 없이 이름만 쓰면 함수 **그 자체**를 가리킵니다.

```python
def add2(a, b): return a + b
def sub2(a, b): return a - b
def mul2(a, b): return a * b
def div2(a, b): return a / b

funcs = [add2, sub2, mul2, div2]   # 함수를 리스트에 담을 수 있어요
for func in funcs:
    print(func.__name__, ":", func(8, 2))

say = print                         # 함수에 다른 이름표를 붙일 수도 있고요
say("print를 say라는 이름으로 불렀어요")
```

`funcs` 리스트에는 계산 결과가 아니라 함수 네 개가 들어 있습니다. 반복문이 하나씩 꺼내 `func.__name__`으로 이름을 찍고 `func(8, 2)`로 불러서 `add2 : 10`, `sub2 : 6`, `mul2 : 16`, `div2 : 4.0`이 나와요. 계산 종류가 늘어도 리스트에 함수 하나만 추가하면 되니 확장하기 좋습니다. (함수 몸통이 짧으면 `def` 줄에 이어 한 줄로 쓸 수도 있지만, 보통은 줄을 바꿔 씁니다.)

이렇게 **함수를 인자로 받거나 함수를 돌려주는 함수**를 **고차 함수(higher-order function)** 라고 합니다. 앞의 `sorted(..., key=...)`가 함수를 받는 고차 함수였죠. 아래 예제의 `create_price_converter()`와 `create_tax_calculator()`는 반대로 **함수를 만들어 돌려주는** 고차 함수입니다. 환율 1300과 통화 이름 `"USD"`를 넣으면 "원화를 달러로 바꾸는 함수"가 만들어져 나와요. 공장에 설정값을 넣으면 그에 맞는 기계가 하나 나오는 셈입니다.

맨 위의 `korean_currency_formatter()`는 안에 `to_man`, `to_eok`, `to_jo` 세 함수를 품고 있습니다. 조 단위 함수는 나머지를 억 단위 함수에, 억 단위 함수는 나머지를 만 단위 함수에 맡기면서 같은 계산을 반복하지 않아요. 이 도우미 함수들은 바깥에서 쓸 일이 없으니 함수 안에 숨겨 둔 것입니다.

```python
def korean_currency_formatter(amount: int, unit: str = "원") -> str:
    """한국 화폐 단위 포맷터"""
    
    # 큰 단위 변환기들
    def to_man(amount):
        if amount < 10000:
            return str(amount)
        man, rest = divmod(amount, 10000)
        return f"{man}만{rest}" if rest > 0 else f"{man}만"  # 25만0원이 아니라 25만원
    
    def to_eok(amount):
        eok = amount // 100000000
        remaining = amount % 100000000
        
        if eok > 0:
            if remaining > 0:
                man_part = to_man(remaining)
                return f"{eok}억{man_part}"
            return f"{eok}억"
        return to_man(amount)
    
    # 조 단위까지 처리
    def to_jo(amount):
        jo = amount // 1000000000000
        remaining = amount % 1000000000000
        
        if jo > 0:
            if remaining > 0:
                eok_part = to_eok(remaining)
                return f"{jo}조{eok_part}"
            return f"{jo}조"
        return to_eok(amount)
    
    formatted = to_jo(amount)
    return f"{formatted}{unit}"

def create_price_converter(exchange_rate: float, currency_name: str):
    """가격 변환기 생성 함수 (고차 함수)"""
    def converter(krw_amount: int) -> str:
        converted = krw_amount / exchange_rate
        return f"{converted:,.2f} {currency_name}"
    
    return converter

def create_tax_calculator(tax_rate: float, tax_name: str):
    """세금 계산기 생성 함수"""
    def calculator(amount: int, include_tax: bool = True) -> dict:
        if include_tax:
            # 세금 포함 가격에서 세전 가격 계산
            pre_tax = amount / (1 + tax_rate)
            tax_amount = amount - pre_tax
        else:
            # 세전 가격에서 세금 계산
            pre_tax = amount
            tax_amount = amount * tax_rate
            amount = pre_tax + tax_amount
        
        return {
            "세전가격": f"{pre_tax:,.0f}원",
            "세금": f"{tax_amount:,.0f}원",
            "총가격": f"{amount:,.0f}원",
            "세금종류": tax_name,
            "세율": f"{tax_rate*100:.1f}%"
        }
    
    return calculator

# 사용 예제
print("화폐 단위 포맷팅:")
amounts = [15000, 250000, 3500000, 120000000, 1500000000000]
for amount in amounts:
    print(f"{amount:,}원 → {korean_currency_formatter(amount)}")

# 환율 변환기
usd_converter = create_price_converter(1300, "USD")
eur_converter = create_price_converter(1400, "EUR") 
jpy_converter = create_price_converter(9.5, "JPY")

print(f"\n환율 변환:")
krw_price = 130000
print(f"{krw_price:,}원 = {usd_converter(krw_price)}")
print(f"{krw_price:,}원 = {eur_converter(krw_price)}")
print(f"{krw_price:,}원 = {jpy_converter(krw_price)}")

# 세금 계산기
vat_calc = create_tax_calculator(0.10, "부가가치세")
income_tax_calc = create_tax_calculator(0.24, "소득세")

print(f"\n세금 계산:")
price = 100000
vat_result = vat_calc(price, include_tax=False)
print("부가세 계산:")
for key, value in vat_result.items():
    print(f"  {key}: {value}")
```

환율 변환기 셋은 같은 `create_price_converter()`에서 나왔지만 각자 자기 환율을 기억하고 있습니다. 그래서 같은 13만 원을 넣어도 `100.00 USD`, `92.86 EUR`, `13,684.21 JPY`로 다르게 나와요. 함수가 만들어질 때의 값을 기억하는 이 성질이 10.5절에서 배울 **클로저**입니다.

화폐 포맷 결과도 보세요. `15,000원`은 `1만5000원`, `250,000원`은 `25만원`, `120,000,000원`은 `1억2000만원`으로 나옵니다. `to_man()`이 만 단위 아래 나머지가 0인지 따로 확인하기 때문이에요. 이 확인이 없으면 `25만0원`처럼 어색한 `0`이 붙습니다. 이런 경계값(0, 딱 떨어지는 수)은 함수를 만든 뒤 꼭 따로 시험해 봐야 하는 곳입니다.

## 10.3 내장 함수: map, filter, reduce

파이썬에는 `import` 없이 바로 쓸 수 있는 **내장 함수(built-in function)** 가 수십 개 있습니다. 빌트인 옷장이 집에 처음부터 달려 있듯이요. 다 외울 필요는 없고, 필요할 때 공식 문서의 내장 함수 목록에서 찾아 쓰면 됩니다. 이 절에서는 그중 함수를 인자로 받는 세 친구를 봅니다.

- `map(함수, 반복 가능한 객체)`: 모든 원소에 함수를 적용한 결과를 내놓습니다.
- `filter(함수, 반복 가능한 객체)`: 함수가 참을 돌려주는 원소만 남깁니다.
- `reduce(함수, 반복 가능한 객체[, 초깃값])`: 원소를 왼쪽부터 차례로 합쳐 값 하나로 줄입니다. 내장 함수가 아니라 `functools` 모듈에 있어서 `import`가 필요해요.

### map() 함수 활용

공장의 컨베이어 벨트를 떠올려 보세요. 벨트 위로 지나가는 물건 하나하나에 같은 스티커를 붙이는 기계가 `map()`입니다. 아래 예제는 센티미터 값들에 "척으로 바꾸기" 함수를, 문장들에 "전처리" 함수를 하나씩 적용해요.

`map()`의 결과는 리스트가 아니라 **이터레이터(iterator)** 입니다. 값을 미리 다 계산해 두지 않고, 하나씩 꺼낼 때마다 계산해서 건네주는 객체예요. 그래서 그냥 `print()`하면 `<map object at 0x...>` 같은 주소만 보이고, 예제처럼 `list()`로 감싸야 결과가 한꺼번에 보입니다. `zip()`, `filter()`, `reversed()`도 마찬가지예요. 반복할 수 있는 객체(iterable)와 이터레이터의 차이는 15장에서 자세히 다룹니다.

```python
# 한국 전통 측정 단위 변환
def convert_traditional_units():
    """한국 전통 단위 변환"""
    
    # 길이 단위 변환 (척, 자, 치, 분)
    modern_lengths_cm = [30, 150, 180, 200, 25]  # cm
    
    # 1척 = 30.3cm
    to_cheok = lambda cm: round(cm / 30.3, 2)
    cheok_lengths = list(map(to_cheok, modern_lengths_cm))
    
    print("길이 단위 변환 (cm → 척):")
    for cm, cheok in zip(modern_lengths_cm, cheok_lengths):
        print(f"{cm}cm = {cheok}척")
    
    # 무게 단위 변환 (관, 근, 량)
    modern_weights_g = [600, 1500, 3750, 37500]  # g
    
    # 1관 = 3.75kg = 3750g, 1근 = 600g, 1량 = 37.5g
    def to_traditional_weight(grams):
        gwan = grams // 3750
        remaining = grams % 3750
        geun = remaining // 600
        remaining = remaining % 600
        ryang = remaining // 37.5
        
        parts = []
        if gwan > 0: parts.append(f"{int(gwan)}관")
        if geun > 0: parts.append(f"{int(geun)}근")
        if ryang > 0: parts.append(f"{ryang:.1f}량")
        
        return " ".join(parts) if parts else "0량"
    
    traditional_weights = list(map(to_traditional_weight, modern_weights_g))
    
    print(f"\n무게 단위 변환 (g → 관/근/량):")
    for g, trad in zip(modern_weights_g, traditional_weights):
        print(f"{g}g = {trad}")

# 한국어 텍스트 전처리
korean_texts = [
    "안녕하세요! 파이썬을 배워봅시다.",
    "데이터 분석이 정말 재미있어요~~~",
    "프로그래밍은 창의적인 활동입니다!!",
    "열심히 공부해서 개발자가 되고 싶습니다 ㅎㅎㅎ"
]

def preprocess_korean_text(text: str) -> dict:
    """한국어 텍스트 전처리"""
    import re
    
    # 특수문자 제거
    cleaned = re.sub(r'[^\w\s가-힣]', '', text)
    
    # 연속된 공백 정리
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # 단어 분리
    words = cleaned.split()
    
    # 글자 수 계산
    char_count = len(text.replace(' ', ''))
    korean_char_count = len(re.findall(r'[가-힣]', text))
    
    return {
        "원문": text,
        "정제문": cleaned,
        "단어수": len(words),
        "총글자수": char_count,
        "한글글자수": korean_char_count,
        "한글비율": f"{korean_char_count/char_count*100:.1f}%" if char_count > 0 else "0%"
    }

print("\n한국어 텍스트 전처리:")
processed_texts = list(map(preprocess_korean_text, korean_texts))

for i, result in enumerate(processed_texts, 1):
    print(f"\n텍스트 {i}:")
    for key, value in result.items():
        print(f"  {key}: {value}")

convert_traditional_units()
```

출력은 텍스트 전처리 결과가 먼저 나오고 단위 변환이 뒤에 나옵니다. 코드에서 전처리 부분은 바로 실행되고, `convert_traditional_units()`는 맨 마지막 줄에서야 불리기 때문이에요. 함수는 정의만 해서는 아무 일도 하지 않고, **불렀을 때** 실행됩니다.

단위 변환에서 `30cm = 0.99척`처럼 30cm가 1척에 조금 못 미치는 것은 1척을 30.3cm로 잡았기 때문입니다. 무게는 `1500g = 2근 8.0량`으로 나와요. 1500g에서 2근(1200g)을 빼고 남은 300g이 37.5g짜리 량으로 8개라는 뜻입니다. `map()`에는 `to_cheok`처럼 람다를 담은 변수를 넘겨도 되고, `to_traditional_weight`처럼 `def`로 만든 함수를 넘겨도 됩니다. 함수이기만 하면 돼요.

### filter() 함수 활용

`filter()`는 체 같은 함수입니다. 원소를 하나씩 함수에 넣어 보고 `True`가 나온 것만 통과시켜요. 함수 자리에 `None`을 주면 원소 자체가 참인 것만 남깁니다. `filter(None, [0, 1, "", 2])`의 결과는 `[1, 2]`예요(3장의 "비어 있으면 거짓" 규칙 그대로입니다).

조건이 짧으면 람다로, 여러 줄이면 `is_korean_word()`처럼 이름 있는 함수로 만들어 넘기는 것이 좋습니다. 이름이 곧 설명이 되어 `filter(is_korean_word, korean_words)`가 "한국어 단어만 거르기"라고 읽히거든요.

```python
# 한국 대학교 정보 필터링
universities = [
    {"이름": "서울대학교", "설립년": 1946, "소재지": "서울", "학생수": 28000, "유형": "국립"},
    {"이름": "연세대학교", "설립년": 1885, "소재지": "서울", "학생수": 38000, "유형": "사립"},
    {"이름": "고려대학교", "설립년": 1905, "소재지": "서울", "학생수": 36000, "유형": "사립"},
    {"이름": "KAIST", "설립년": 1971, "소재지": "대전", "학생수": 10000, "유형": "국립"},
    {"이름": "포항공대", "설립년": 1986, "소재지": "포항", "학생수": 3000, "유형": "사립"},
    {"이름": "부산대학교", "설립년": 1946, "소재지": "부산", "학생수": 30000, "유형": "국립"},
    {"이름": "경희대학교", "설립년": 1949, "소재지": "서울", "학생수": 35000, "유형": "사립"}
]

def demonstrate_university_filtering():
    """대학교 정보 필터링 시연"""
    
    # 서울 소재 대학교
    seoul_universities = list(filter(lambda x: x["소재지"] == "서울", universities))
    print(f"서울 소재 대학교 ({len(seoul_universities)}곳):")
    for uni in seoul_universities:
        print(f"  {uni['이름']} ({uni['설립년']})")
    
    # 100년 이상 된 대학교 (올해 기준)
    from datetime import datetime
    current_year = datetime.now().year
    old_universities = list(filter(
        lambda x: current_year - x["설립년"] >= 100, 
        universities
    ))
    print(f"\n100년 이상 된 대학교 ({len(old_universities)}곳):")
    for uni in old_universities:
        age = current_year - uni["설립년"]
        print(f"  {uni['이름']}: {age}년")
    
    # 학생 수 3만명 이상인 대학교
    large_universities = list(filter(
        lambda x: x["학생수"] >= 30000,
        universities
    ))
    print(f"\n대형 대학교 (3만명 이상, {len(large_universities)}곳):")
    for uni in sorted(large_universities, key=lambda x: x["학생수"], reverse=True):
        print(f"  {uni['이름']}: {uni['학생수']:,}명")
    
    # 복합 조건: 서울 소재 + 사립 + 3만명 이상
    premium_universities = list(filter(
        lambda x: (x["소재지"] == "서울" and 
                  x["유형"] == "사립" and 
                  x["학생수"] >= 30000),
        universities
    ))
    print(f"\n서울 소재 대형 사립대 ({len(premium_universities)}곳):")
    for uni in premium_universities:
        print(f"  {uni['이름']}")

# 한국어 단어 필터링
korean_words = [
    "사과", "apple", "바나나", "banana", "컴퓨터", "computer",
    "프로그래밍", "programming", "안녕하세요", "hello",
    "데이터분석", "data analysis", "머신러닝", "machine learning"
]

def is_korean_word(word: str) -> bool:
    """한국어 단어 판별"""
    import re
    return bool(re.search(r'[가-힣]', word)) and not re.search(r'[a-zA-Z]', word)

def is_mixed_word(word: str) -> bool:
    """한영 혼합 단어 판별"""
    import re
    return bool(re.search(r'[가-힣]', word)) and bool(re.search(r'[a-zA-Z]', word))

print("\n단어 분류:")
korean_only = list(filter(is_korean_word, korean_words))
english_only = list(filter(lambda w: not is_korean_word(w) and not is_mixed_word(w), korean_words))
mixed_words = list(filter(is_mixed_word, korean_words))

print(f"순한글 단어: {korean_only}")
print(f"영어 단어: {english_only}") 
print(f"한영혼합: {mixed_words}")

demonstrate_university_filtering()
```

여기서도 단어 분류가 먼저, 대학교 필터링이 나중에 출력됩니다. "100년 이상 된 대학교"는 앞의 `calculate_korean_age()`처럼 `datetime.now().year`로 올해를 구해 계산하므로, 실행하는 해에 따라 햇수가 달라져요. 기준 연도를 `2024`처럼 코드에 직접 적어 두면 해가 바뀔 때마다 결과가 틀려지니 피하는 것이 좋습니다. 단어 분류에서 "한영혼합"이 빈 리스트인 것은 예제 단어 목록에 한글과 영어가 섞인 단어가 하나도 없어서예요. `"AI모델"` 같은 단어를 추가해 보면 이 칸이 채워집니다.

### reduce() 함수 활용

`reduce()`는 눈덩이 굴리기입니다. 첫 원소와 두 번째 원소를 합쳐 작은 눈덩이를 만들고, 그 눈덩이에 세 번째 원소를 붙이고, 또 네 번째를 붙이고… 끝까지 굴려서 **값 하나**를 남겨요. `reduce(operator.mul, [1, 2, 3, 4])`는 `((1 × 2) × 3) × 4 = 24`를 계산합니다. `operator.mul`은 `*` 연산을 함수로 만들어 둔 것이에요.

세 번째 인자로 **초깃값**을 줄 수 있습니다. 기업 매출 합계에서 `0`을 준 이유는 원소가 딕셔너리라서예요. 초깃값이 없으면 첫 원소인 딕셔너리 자체가 눈덩이의 시작이 되어 `딕셔너리 + 숫자`를 계산하려다 오류가 납니다. 초깃값 `0`에서 시작하면 `0 + 매출`, `그 합 + 매출`… 로 숫자끼리만 더해져요.

```python
from functools import reduce
import operator

def korean_math_operations():
    """한국어 수학 연산 예제"""
    
    number_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # 곱셈으로 팩토리얼 계산
    factorial_10 = reduce(operator.mul, number_values)
    print(f"10! (팩토리얼): {factorial_10:,}")
    
    # 덧셈으로 합계 계산  
    total_sum = reduce(operator.add, number_values)
    print(f"1부터 10까지 합: {total_sum}")
    
    # 최대값 찾기
    scores = [85, 92, 78, 96, 88, 91, 87]
    max_score = reduce(max, scores)
    print(f"최고 점수: {max_score}")
    
    # 문자열 연결
    korean_regions = ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]
    all_regions = reduce(lambda x, y: f"{x}, {y}", korean_regions)
    print(f"특별시·광역시: {all_regions}")

def analyze_korean_company_data():
    """한국 기업 데이터 분석"""
    
    companies = [
        {"이름": "삼성전자", "매출": 2796890, "직원수": 267800, "업종": "전자"},
        {"이름": "SK하이닉스", "매출": 366020, "직원수": 33690, "업종": "반도체"},
        {"이름": "LG전자", "매출": 748632, "직원수": 75000, "업종": "전자"},
        {"이름": "현대자동차", "매출": 1055210, "직원수": 120000, "업종": "자동차"},
        {"이름": "기아", "매출": 894750, "직원수": 52000, "업종": "자동차"},
        {"이름": "POSCO", "매출": 713680, "직원수": 29000, "업종": "철강"},
        {"이름": "LG화학", "매출": 442010, "직원수": 45000, "업종": "화학"}
    ]
    
    # 총 매출 계산
    total_revenue = reduce(
        lambda acc, company: acc + company["매출"], 
        companies, 
        0
    )
    print(f"\n선정 기업 총 매출: {total_revenue:,} 억원")
    
    # 총 직원 수 계산
    total_employees = reduce(
        lambda acc, company: acc + company["직원수"],
        companies,
        0
    )
    print(f"선정 기업 총 직원 수: {total_employees:,} 명")
    
    # 업종별 집계
    from collections import defaultdict
    
    def group_by_industry(acc, company):
        industry = company["업종"]
        if industry not in acc:
            acc[industry] = {"매출": 0, "직원수": 0, "기업수": 0}
        
        acc[industry]["매출"] += company["매출"]
        acc[industry]["직원수"] += company["직원수"] 
        acc[industry]["기업수"] += 1
        return acc
    
    industry_stats = reduce(group_by_industry, companies, {})
    
    print(f"\n업종별 현황:")
    for industry, stats in industry_stats.items():
        avg_revenue = stats["매출"] / stats["기업수"]
        avg_employees = stats["직원수"] / stats["기업수"]
        print(f"{industry}업:")
        print(f"  총 매출: {stats['매출']:,} 억원")
        print(f"  총 직원: {stats['직원수']:,} 명")
        print(f"  기업당 평균 매출: {avg_revenue:,.0f} 억원")
        print(f"  기업당 평균 직원: {avg_employees:,.0f} 명")
        print()

korean_math_operations()
analyze_korean_company_data()
```

`10!`은 `3,628,800`, 1부터 10까지의 합은 `55`, 최고 점수는 `96`입니다. 솔직히 말하면 합계와 최댓값은 `sum()`, `max()`가 더 짧고 읽기 쉬워요. `reduce()`의 진짜 쓸모는 업종별 집계처럼 **딕셔너리 같은 꾸러미를 초깃값으로 두고 원소를 하나씩 반영해 나가는** 경우입니다. `group_by_industry()`가 꾸러미(`acc`)를 받아 기업 하나를 반영한 뒤 그 꾸러미를 다시 돌려주고, `reduce()`가 이것을 끝까지 이어 줍니다. 기업 매출과 직원 수는 예제를 위한 숫자이니 실제 통계로 쓰지는 마세요.

## 10.4 데코레이터 기초

### 기본 데코레이터

어떤 함수가 언제 시작해서 언제 끝났는지, 실행에 몇 초 걸렸는지 알고 싶다고 해 봅시다. 프로그램이 이상하게 동작할 때 함수들이 어떤 순서로 불렸는지 알면 문제의 원인을 찾기 쉽고, 웹 서버처럼 응답 속도가 중요한 곳에서는 처리 시간을 재는 일이 아주 흔하거든요. 그런데 함수마다 시작 시각과 끝 시각을 재는 코드를 일일이 넣으려니 번거롭고, 원래 함수의 코드도 지저분해집니다.

**데코레이터(decorator)** 는 함수를 **직접 고치지 않고** 앞뒤에 기능을 덧붙이는 방법입니다. 선물 상자를 포장지로 감싸는 것과 같아요. 상자 속 선물(원래 함수)은 그대로이고, 겉에 포장(추가 기능)이 둘러집니다. 구조는 앞에서 배운 것들의 조합이에요.

1. 데코레이터는 **함수를 받아서**(고차 함수)
2. 안에서 원래 함수를 감싸는 새 함수 `wrapper`를 만들고(함수 안의 함수)
3. 그 `wrapper`를 **돌려줍니다**.

`wrapper`는 `*args, **kwargs`로 무엇이든 받아서 원래 함수에 그대로 넘겨주니, 어떤 모양의 함수든 감쌀 수 있어요. 함수 정의 위에 `@korean_time_logger`라고 쓰는 것은 `create_korean_student_id = korean_time_logger(create_korean_student_id)`를 짧게 쓴 것입니다. 원래 이름에 포장된 함수를 다시 붙여 주는 거죠.

`@functools.wraps(func)`는 포장지에 원래 상자의 이름표를 옮겨 붙이는 장치입니다. 이게 없으면 감싼 뒤의 함수 이름(`__name__`)과 독스트링이 모두 `wrapper`의 것으로 바뀌어서, 오류 메시지나 `help()`에서 어떤 함수였는지 알기 어려워집니다.

```python
import time
import functools
from datetime import datetime

def korean_time_logger(func):
    """한국 시간으로 함수 실행 시간 기록"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_datetime = datetime.now()
        
        print(f"함수 '{func.__name__}' 실행 시작: {start_datetime.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}")
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"함수 '{func.__name__}' 실행 완료: {execution_time:.4f}초 소요")
        return result
    
    return wrapper

def korean_input_validator(*validators):
    """한국어 입력 검증 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 인자 검증
            for i, (arg, validator) in enumerate(zip(args, validators)):
                if not validator(arg):
                    validator_name = validator.__name__ if hasattr(validator, '__name__') else str(validator)
                    raise ValueError(f"인자 {i+1}번 '{arg}'이(가) 조건 '{validator_name}'을(를) 만족하지 않습니다.")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 검증 함수들
def is_korean_name(name: str) -> bool:
    """한글 이름 검증"""
    import re
    return bool(re.match(r'^[가-힣]{2,5}$', name))

def is_positive_int(value: int) -> bool:
    """양의 정수 검증"""
    return isinstance(value, int) and value > 0

def is_valid_age(age: int) -> bool:
    """유효한 나이 검증"""
    return isinstance(age, int) and 0 <= age <= 150

# 데코레이터 적용 예제
@korean_time_logger
@korean_input_validator(is_korean_name, is_positive_int, is_valid_age)
def create_korean_student_id(name: str, student_number: int, age: int) -> str:
    """한국 학생 ID 생성"""
    time.sleep(0.1)  # 처리 시간 시뮬레이션
    
    # 이름의 첫 글자로 성씨 추출
    surname = name[0]
    
    # 학번을 4자리로 포맷팅
    formatted_number = f"{student_number:04d}"
    
    # 연령대 코드
    age_group = f"{age // 10}0"
    
    student_id = f"KOR{surname}{formatted_number}{age_group}"
    
    print(f"학생 ID 생성: {name}님 → {student_id}")
    return student_id

# 사용 예제
print("학생 ID 생성 테스트:")
try:
    id1 = create_korean_student_id("김철수", 1234, 20)
    id2 = create_korean_student_id("이영희", 5678, 22)
    print(f"생성된 ID들: {id1}, {id2}")
except ValueError as e:
    print(f"[X] 오류: {e}")

# 잘못된 입력 테스트
print(f"\n잘못된 입력 테스트:")
try:
    create_korean_student_id("John", 1234, 20)  # 영문 이름
except ValueError as e:
    print(f"[X] 오류: {e}")
```

데코레이터는 이렇게 **여러 겹** 씌울 수 있습니다. 아래에 쓴 것이 먼저 감싸고 위에 쓴 것이 그 바깥을 감싸요. 그래서 `@korean_time_logger`가 가장 바깥 포장이고, 그 안에 `@korean_input_validator`, 맨 안에 원래 함수가 있습니다.

출력에서 이 순서가 그대로 보입니다. 정상 호출은 "실행 시작 → 학생 ID 생성 → 실행 완료" 순서이고, 실행 시간은 `time.sleep(0.1)` 때문에 0.1초 남짓이에요. `"John"`을 넣은 호출은 바깥 포장이 "실행 시작"을 찍은 뒤, 안쪽 포장인 검증기에서 `ValueError`가 나서 **"실행 완료"는 찍히지 않고** 바로 `except`로 넘어갑니다. 원래 함수는 아예 실행되지 않았어요. 검증기가 입구에서 막아 준 것입니다.

### 매개변수를 받는 데코레이터

`@korean_retry(max_attempts=3, delay=0.5)`처럼 데코레이터에 설정값을 넘기고 싶을 때가 있습니다. 이때는 포장이 한 겹 더 필요해요.

1. `korean_retry(max_attempts=3, ...)`가 먼저 불려서 설정값을 기억한 **데코레이터**를 돌려주고,
2. 그 데코레이터가 원래 함수를 받아 `wrapper`를 돌려줍니다.

함수가 세 겹(`korean_retry` → `decorator` → `wrapper`)인 이유가 이것입니다. 앞 예제의 `korean_input_validator(...)`도 같은 구조였어요. 안쪽 함수들이 바깥 함수의 `max_attempts`, `delay`, `cache` 같은 값을 계속 쓸 수 있는 것은 10.5절에서 볼 클로저 덕분입니다.

`korean_cache`는 같은 인자로 다시 부르면 계산하지 않고 저장해 둔 답을 돌려주는 데코레이터입니다. 표준 라이브러리에도 같은 일을 하는 `functools.lru_cache`가 있으니, 실무에서는 그쪽을 먼저 쓰세요. 여기서는 데코레이터가 어떻게 동작하는지 보려고 직접 만들었습니다. 클래스에 씌우는 데코레이터 등 더 깊은 내용은 16장에서 다룹니다.

```python
def korean_retry(max_attempts: int = 3, delay: float = 1.0, exceptions=(Exception,)):
    """한국어 재시도 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    print(f"시도 {attempt}/{max_attempts}: {func.__name__}")
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        print(f"[O] {attempt}번째 시도에서 성공!")
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    print(f"[X] {attempt}번째 시도 실패: {str(e)}")
                    
                    if attempt < max_attempts:
                        print(f"{delay}초 후 재시도...")
                        time.sleep(delay)
                    else:
                        print(f"모든 시도 실패. 포기합니다.")
            
            raise last_exception
        
        return wrapper
    return decorator

def korean_cache(maxsize: int = 128):
    """한국어 캐시 데코레이터"""
    def decorator(func):
        cache = {}
        cache_info = {"hits": 0, "misses": 0, "maxsize": maxsize}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 딕셔너리는 해시 불가능하므로 키워드 인자를 튜플로 변환
            key = (args, tuple(sorted(kwargs.items())))
            
            if key in cache:
                cache_info["hits"] += 1
                print(f"캐시 히트: {func.__name__}")
                return cache[key]
            
            # 캐시 크기 제한
            if len(cache) >= maxsize:
                # 가장 오래된 항목 제거 (FIFO)
                oldest_key = next(iter(cache))
                del cache[oldest_key]
                print(f"캐시 공간 확보: 항목 제거")
            
            cache_info["misses"] += 1
            print(f"캐시 미스: {func.__name__} 계산 중...")
            
            result = func(*args, **kwargs)
            cache[key] = result
            
            return result
        
        def cache_clear():
            cache.clear()
            cache_info["hits"] = cache_info["misses"] = 0
            print("캐시 초기화 완료")
        
        def cache_status():
            total = cache_info["hits"] + cache_info["misses"]
            hit_rate = cache_info["hits"] / total * 100 if total > 0 else 0
            return {
                "캐시_크기": len(cache),
                "최대_크기": cache_info["maxsize"],
                "히트_수": cache_info["hits"],
                "미스_수": cache_info["misses"],
                "히트율": f"{hit_rate:.1f}%"
            }
        
        wrapper.cache_clear = cache_clear
        wrapper.cache_status = cache_status
        
        return wrapper
    return decorator

# 데코레이터 적용 예제
import random

@korean_retry(max_attempts=3, delay=0.5, exceptions=(ValueError, ConnectionError))
def unstable_korean_api_call(city: str) -> dict:
    """불안정한 한국 도시 API 호출 시뮬레이션"""
    
    # 랜덤하게 실패
    if random.random() < 0.7:  # 70% 실패율
        raise ConnectionError(f"{city} 날씨 정보 조회 실패")
    
    # 성공 시 가짜 데이터 반환
    weather_conditions = ["맑음", "흐림", "비", "눈", "안개"]
    return {
        "도시": city,
        "날씨": random.choice(weather_conditions),
        "온도": random.randint(-10, 35),
        "습도": random.randint(30, 90)
    }

@korean_cache(maxsize=5)
def expensive_korean_calculation(base: int, exponent: int) -> int:
    """비용이 많이 드는 한국어 계산"""
    print(f"복잡한 계산 수행: {base}^{exponent}")
    time.sleep(1)  # 계산 시간 시뮬레이션
    result = base ** exponent
    print(f"[O] 계산 완료: {result:,}")
    return result

# 사용 예제
print("API 재시도 테스트:")
try:
    weather = unstable_korean_api_call("서울")
    print(f"날씨 정보: {weather}")
except Exception as e:
    print(f"최종 실패: {e}")

print(f"\n캐시 테스트:")
# 같은 계산을 여러 번 수행 (캐시 효과 확인)
for _ in range(2):
    expensive_korean_calculation(2, 10)

for _ in range(2):
    expensive_korean_calculation(3, 5)

print(f"캐시 상태: {expensive_korean_calculation.cache_status()}")
```

API 재시도 결과는 `random`으로 70% 확률의 실패를 흉내 내기 때문에 실행할 때마다 다릅니다. 첫 시도에 성공할 수도 있고, 세 번 모두 실패해서 "최종 실패"가 찍힐 수도 있어요. 캐시 쪽은 항상 같습니다. `2^10`과 `3^5`를 각각 두 번씩 불렀는데, 처음에만 1초짜리 계산을 하고(캐시 미스) 두 번째는 저장해 둔 답을 바로 돌려줍니다(캐시 히트). 그래서 마지막 상태가 히트 2, 미스 2, 히트율 50.0%예요.

## 10.5 클로저와 스코프

### 클로저 기본 개념

보통 함수 안의 지역 변수는 함수가 끝나면 사라진다고 했습니다. 그런데 앞에서 본 환율 변환기는 `create_price_converter()`가 끝난 뒤에도 환율을 기억하고 있었죠? 안쪽 함수가 바깥 함수의 변수를 쓰고 있으면, 파이썬은 바깥 함수가 끝나도 그 변수를 버리지 않고 **안쪽 함수에 붙여 둡니다**. 이렇게 자기가 만들어질 때의 주변 변수를 기억하는 함수를 **클로저(closure)** 라고 해요. 도시락을 싸 들고 집을 나선 아이처럼, 집(바깥 함수)을 떠나도 필요한 것을 챙겨 다니는 거죠.

아래 `korean_greeting_factory()`가 돌려주는 `greet`는 바깥의 `base_greeting`을 기억합니다. `"formal"`로 만든 것은 "안녕하십니까"를, `"morning"`으로 만든 것은 "좋은 아침입니다"를 계속 쓰죠.

`korean_counter_factory()`는 기억한 값을 **바꾸는** 클로저입니다. 안쪽 함수에서 바깥 변수 `count`를 바꾸려면 `nonlocal count`가 필요해요. 이게 없으면 앞에서 본 `UnboundLocalError`가 납니다. 이 팩토리는 다섯 개의 안쪽 함수를 딕셔너리에 담아 돌려주는데, 다섯 함수가 모두 **같은 `count` 하나**를 함께 기억하고 있어서 `증가`로 바꾼 값을 `현재값`이 그대로 읽을 수 있습니다.

```python
def korean_greeting_factory(greeting_type: str):
    """한국어 인사말 생성기"""
    
    greetings = {
        "formal": "안녕하십니까",
        "casual": "안녕하세요", 
        "friendly": "안녕",
        "morning": "좋은 아침입니다",
        "evening": "안녕히 주무세요"
    }
    
    base_greeting = greetings.get(greeting_type, "안녕하세요")
    
    def greet(name: str, title: str = "") -> str:
        # 클로저: 외부 함수의 변수에 접근
        if title:
            full_name = f"{name} {title}"
        else:
            full_name = name
            
        return f"{base_greeting}, {full_name}님!"
    
    # 클로저 정보를 추가하는 내부 함수
    def get_greeting_info():
        return {
            "인사_유형": greeting_type,
            "기본_인사말": base_greeting
        }
    
    # 함수에 속성 추가
    greet.get_info = get_greeting_info
    
    return greet

def korean_counter_factory(initial_value: int = 0, step: int = 1):
    """한국어 카운터 생성기"""
    
    count = initial_value
    
    def increment():
        nonlocal count
        count += step
        return count
    
    def decrement():
        nonlocal count
        count -= step
        return count
    
    def reset():
        nonlocal count
        count = initial_value
        return count
    
    def get_count():
        return count
    
    def get_korean_number():
        """숫자를 한국어로 변환"""
        korean_numbers = [
            "영", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구", "십"
        ]
        if 0 <= count <= 10:
            return korean_numbers[count]
        else:
            return str(count)
    
    # 여러 함수를 가진 객체 반환
    return {
        "증가": increment,
        "감소": decrement,
        "초기화": reset,
        "현재값": get_count,
        "한국어숫자": get_korean_number
    }

# 클로저 사용 예제
print("인사말 생성기:")
formal_greet = korean_greeting_factory("formal")
casual_greet = korean_greeting_factory("casual")
morning_greet = korean_greeting_factory("morning")

print(formal_greet("김철수", "부장"))
print(casual_greet("이영희"))
print(morning_greet("박민수", "교수"))

print(f"격식 인사 정보: {formal_greet.get_info()}")

print(f"\n카운터 생성기:")
counter1 = korean_counter_factory(0, 2)  # 0부터 시작, 2씩 증가
counter2 = korean_counter_factory(10, 1)  # 10부터 시작, 1씩 증가

print(f"카운터1 증가: {counter1['증가']()}, {counter1['증가']()}, {counter1['증가']()}")
print(f"카운터1 한국어: {counter1['한국어숫자']()}")

print(f"카운터2 감소: {counter2['감소']()}, {counter2['감소']()}")
print(f"카운터2 현재값: {counter2['현재값']()}")
```

카운터1은 0에서 시작해 2씩 늘어 `2, 4, 6`이 되고, 한국어로는 `육`입니다. 카운터2는 10에서 1씩 줄어 `9, 8`이에요. 두 카운터는 같은 팩토리에서 나왔지만 **각자 자기 `count`를 따로** 가지고 있어서 서로 영향을 주지 않습니다. 팩토리를 부를 때마다 새 지역 변수가 생기고, 그 변수를 새 클로저가 챙겨 가기 때문이에요.

> **Q. 이럴 거면 클래스를 쓰는 게 낫지 않나요?**
> 좋은 질문이에요. 값(`count`)과 그 값을 다루는 함수들(`증가`, `감소`…)을 함께 묶는 일은 11장에서 배울 클래스가 원래 하는 일입니다. 기억할 값이 한두 개이고 함수도 하나뿐이라면 클로저가 가볍고 간단하지만, 이 카운터처럼 다루는 함수가 여럿으로 늘어나면 클래스로 만드는 편이 읽기 쉽습니다. 둘 다 "상태를 기억하는 방법"이라는 점을 기억해 두면 11장이 훨씬 쉽게 읽힐 거예요.

### 실무 클로저 예제

클로저는 "설정은 한 번, 사용은 여러 번"인 상황에 잘 맞습니다. `korean_validator_factory()`는 정규 표현식 패턴들을 **한 번만** 컴파일해 두고, `create_validator("휴대폰")`처럼 부를 때마다 그 패턴을 기억하는 검증 함수를 만들어 줍니다. 오류 메시지도 기본값을 쓰거나 원하는 문구로 바꿔 만들 수 있어요.

`korean_data_processor_factory()`도 같은 생각입니다. 처리 규칙(공백 정리 → 소문자 변환 → 특수문자 제거)을 딕셔너리로 넘기면, 그 규칙들을 **순서대로** 적용하는 처리 함수를 만들어 줘요. 처리 중 오류가 나도 멈추지 않고 "오류" 목록에 적어 둔 뒤 다음 데이터로 넘어갑니다.

```python
def korean_validator_factory():
    """한국어 검증기 팩토리"""
    
    # 공통 검증 규칙들
    import re
    
    patterns = {
        "휴대폰": re.compile(r'^010-\d{4}-\d{4}$'),
        "이메일": re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
        "주민등록번호": re.compile(r'^\d{6}-\d{7}$'),
        "사업자등록번호": re.compile(r'^\d{3}-\d{2}-\d{5}$'),
        "한글이름": re.compile(r'^[가-힣]{2,5}$')
    }
    
    def create_validator(validation_type: str, custom_message: str = None):
        """특정 유형의 검증기 생성"""
        
        if validation_type not in patterns:
            raise ValueError(f"지원하지 않는 검증 유형: {validation_type}")
        
        pattern = patterns[validation_type]
        default_messages = {
            "휴대폰": "올바른 휴대폰 번호 형식이 아닙니다 (010-0000-0000)",
            "이메일": "올바른 이메일 형식이 아닙니다",
            "주민등록번호": "올바른 주민등록번호 형식이 아닙니다 (000000-0000000)",
            "사업자등록번호": "올바른 사업자등록번호 형식이 아닙니다 (000-00-00000)",
            "한글이름": "올바른 한글 이름이 아닙니다 (2-5글자)"
        }
        
        error_message = custom_message or default_messages[validation_type]
        
        def validate(value: str) -> tuple[bool, str]:
            """검증 수행"""
            if not isinstance(value, str):
                return False, "문자열이 아닙니다"
            
            if pattern.match(value):
                return True, "검증 성공"
            else:
                return False, error_message
        
        # 검증기 정보 추가
        validate.validation_type = validation_type
        validate.pattern = pattern.pattern
        
        return validate
    
    return create_validator

def korean_data_processor_factory(processing_rules: dict):
    """한국어 데이터 처리기 팩토리"""
    
    def create_processor(data_type: str):
        """특정 유형의 데이터 처리기 생성"""
        
        if data_type not in processing_rules:
            raise ValueError(f"지원하지 않는 데이터 유형: {data_type}")
        
        rules = processing_rules[data_type]
        
        def process(data_list: list) -> dict:
            """데이터 처리 수행"""
            results = {
                "원본_데이터": data_list.copy(),
                "처리_결과": [],
                "통계": {},
                "오류": []
            }
            
            for item in data_list:
                try:
                    processed_item = item
                    
                    # 규칙별로 처리
                    for rule_name, rule_func in rules.items():
                        processed_item = rule_func(processed_item)
                    
                    results["처리_결과"].append(processed_item)
                    
                except Exception as e:
                    results["오류"].append({
                        "원본": item,
                        "오류내용": str(e)
                    })
            
            # 통계 계산
            results["통계"] = {
                "총_건수": len(data_list),
                "성공_건수": len(results["처리_결과"]),
                "실패_건수": len(results["오류"]),
                "성공률": f"{len(results['처리_결과'])/len(data_list)*100:.1f}%" if data_list else "0%"
            }
            
            return results
        
        process.data_type = data_type
        process.rules = list(rules.keys())
        
        return process
    
    return create_processor

# 클로저 팩토리 사용 예제
print("검증기 팩토리 사용:")
validator_factory = korean_validator_factory()

phone_validator = validator_factory("휴대폰")
email_validator = validator_factory("이메일")
name_validator = validator_factory("한글이름", "이름은 한글 2-5글자여야 합니다")

test_data = [
    ("휴대폰", "010-1234-5678", phone_validator),
    ("휴대폰", "010-12345-6789", phone_validator),
    ("이메일", "test@example.com", email_validator),
    ("이메일", "잘못된이메일", email_validator),
    ("이름", "김철수", name_validator),
    ("이름", "김", name_validator)
]

for data_type, test_value, validator in test_data:
    is_valid, message = validator(test_value)
    status = "[O]" if is_valid else "[X]"
    print(f"{status} {data_type} '{test_value}': {message}")

# 데이터 처리기 팩토리 사용
print(f"\n데이터 처리기 팩토리 사용:")

# 처리 규칙 정의
text_processing_rules = {
    "한국어_텍스트": {
        "공백_정리": lambda x: ' '.join(x.split()),
        "소문자_변환": lambda x: x.lower(),
        "특수문자_제거": lambda x: ''.join(c for c in x if c.isalnum() or c.isspace() or ord(c) >= 0xAC00)
    }
}

processor_factory = korean_data_processor_factory(text_processing_rules)
text_processor = processor_factory("한국어_텍스트")

sample_texts = [
    "안녕하세요!!!   파이썬을 배워봅시다~~~",
    "DATA  분석이   정말 재미있어요!@#$",
    "프로그래밍은     창의적인 활동입니다.",
    None  # 오류 발생할 데이터
]

try:
    results = text_processor(sample_texts[:-1])  # None 제외
    
    print(f"처리 통계: {results['통계']}")
    print(f"처리 결과:")
    for original, processed in zip(results["원본_데이터"], results["처리_결과"]):
        print(f"  '{original}' → '{processed}'")
        
except Exception as e:
    print(f"처리 오류: {e}")
```

검증 결과는 `[O]` 셋, `[X]` 셋입니다. 이름 검증기는 만들 때 넘긴 문구 "이름은 한글 2-5글자여야 합니다"를 기억해서, 기본 메시지 대신 그 문구로 알려 줘요. 데이터 처리 결과에서는 `DATA`가 `data`로 바뀌고 `!@#$`, `~~~`, 마침표가 사라졌습니다. 예제는 `sample_texts[:-1]`로 마지막의 `None`을 빼고 넘기므로 성공률이 100.0%예요. `None`까지 넣어 보면 `None.split()`에서 오류가 나는데, 처리기가 멈추지 않고 그 건을 "오류"에 기록하고 성공률을 75.0%로 계산합니다.

## 10.6 실무 예제: 한국어 자연어 처리 파이프라인

### 텍스트 전처리 파이프라인

이제 이 장에서 배운 것을 모아 작은 자연어 처리 파이프라인을 만듭니다. **파이프라인(pipeline)** 은 공장의 조립 라인처럼, 원료(문장)가 정해진 순서의 작업대를 하나씩 지나며 다듬어지는 구조예요. 이 예제의 작업대는 네 개입니다.

1. **정규화**: `ㅋㅋㅋ`, `!!!`처럼 같은 자음·모음이나 문장부호가 세 번 이상 이어지면 하나로 줄이고, 공백을 정리합니다.
2. **토크나이징**: 띄어쓰기로 단어를 나누고, 끝에 붙은 조사(`은`, `는`, `을` 등)를 떼어 냅니다.
3. **불용어 제거**: "그", "및", "때문에"처럼 뜻을 거의 더하지 않는 흔한 말과 한 글자짜리를 지웁니다.
4. **길이 필터**: 너무 짧거나 긴 단어를 걸러 냅니다.

각 작업대는 `create_korean_normalizer()` 같은 메서드가 만들어 주는 **클로저**이고, `add_processor()`로 원하는 순서대로 라인에 올립니다. `add_processor()`가 `self`를 돌려주기 때문에 `pipeline.add_processor(...).add_processor(...)`처럼 이어서 쓸 수도 있어요. 감성 분석기 `create_korean_sentiment_analyzer()`도 긍정, 부정 단어 사전을 기억하는 클로저입니다.

조사 떼기나 감성 사전은 아주 단순한 규칙이라는 점을 미리 알고 보세요. 실제 서비스에서는 형태소 분석기나 학습된 모델을 씁니다. 여기서는 **작은 함수들을 조립해 큰 일을 하는 방법**을 보는 데 집중하면 됩니다.

```python
import re
from functools import reduce, partial
from collections import Counter, defaultdict
from typing import List, Dict, Callable, Any

class KoreanNLPPipeline:
    """한국어 자연어 처리 파이프라인"""
    
    def __init__(self):
        self.processors = []
        self.statistics = defaultdict(int)
        self.korean_stopwords = {
            "이", "그", "저", "것", "들", "수", "등", "및", "또는", 
            "하지만", "그러나", "따라서", "즉", "때문에", "통해",
            "에서", "에게", "에는", "으로", "로", "와", "과", "을", "를"
        }
    
    def add_processor(self, name: str, processor_func: Callable[[str], str]):
        """처리기 추가"""
        self.processors.append((name, processor_func))
        return self
    
    def create_korean_normalizer(self):
        """한국어 정규화 처리기 생성"""
        def normalize(text: str) -> str:
            # 같은 자음/모음이 세 번 이상 이어지면 하나로 (ㅋㅋㅋ → ㅋ, ㅠㅠ는 그대로)
            text = re.sub(r'([ㄱ-ㅎㅏ-ㅣ])\1{2,}', r'\1', text)
            
            # 연속된 특수문자 정리
            text = re.sub(r'([!?~.])\1{2,}', r'\1', text)
            
            # 연속된 공백 정리
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
        
        return normalize
    
    def create_korean_tokenizer(self, include_particles: bool = False):
        """한국어 토크나이저 생성"""
        def tokenize(text: str) -> str:
            # 간단한 공백 기반 토크나이징
            tokens = text.split()
            
            if not include_particles:
                # 조사/어미 제거 (매우 단순한 방식)
                cleaned_tokens = []
                for token in tokens:
                    # 일반적인 조사들 제거
                    for particle in ['은', '는', '이', '가', '을', '를', '의', '에', '로', '와', '과']:
                        if token.endswith(particle) and len(token) > len(particle):
                            token = token[:-len(particle)]
                            break
                    cleaned_tokens.append(token)
                tokens = cleaned_tokens
            
            return ' '.join(tokens)
        
        return tokenize
    
    def create_stopword_remover(self, custom_stopwords: set = None):
        """불용어 제거기 생성"""
        stopwords = self.korean_stopwords.copy()
        if custom_stopwords:
            stopwords.update(custom_stopwords)
        
        def remove_stopwords(text: str) -> str:
            tokens = text.split()
            filtered_tokens = [
                token for token in tokens 
                if token not in stopwords and len(token) > 1
            ]
            return ' '.join(filtered_tokens)
        
        return remove_stopwords
    
    def create_length_filter(self, min_length: int = 2, max_length: int = 50):
        """길이 기반 필터 생성"""
        def filter_by_length(text: str) -> str:
            tokens = text.split()
            filtered_tokens = [
                token for token in tokens 
                if min_length <= len(token) <= max_length
            ]
            return ' '.join(filtered_tokens)
        
        return filter_by_length
    
    def process_single(self, text: str) -> Dict[str, Any]:
        """단일 텍스트 처리"""
        if not isinstance(text, str):
            return {"error": "입력이 문자열이 아닙니다", "original": text}
        
        result = {
            "original": text,
            "processed": text,
            "steps": []
        }
        
        current_text = text
        
        for step_name, processor in self.processors:
            try:
                processed_text = processor(current_text)
                result["steps"].append({
                    "step": step_name,
                    "before": current_text,
                    "after": processed_text
                })
                current_text = processed_text
                self.statistics[f"{step_name}_success"] += 1
                
            except Exception as e:
                result["steps"].append({
                    "step": step_name,
                    "error": str(e)
                })
                self.statistics[f"{step_name}_error"] += 1
                break
        
        result["processed"] = current_text
        result["token_count"] = len(current_text.split()) if current_text else 0
        
        return result
    
    def process_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """배치 처리"""
        return [self.process_single(text) for text in texts]
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """결과 분석"""
        total_texts = len(results)
        successful_results = [r for r in results if "error" not in r]
        
        # 토큰 통계
        all_tokens = []
        for result in successful_results:
            tokens = result["processed"].split()
            all_tokens.extend(tokens)
        
        token_frequency = Counter(all_tokens)
        
        # 길이 통계
        original_lengths = [len(r["original"]) for r in results if "original" in r]
        processed_lengths = [len(r["processed"]) for r in successful_results]
        
        return {
            "총_텍스트_수": total_texts,
            "성공_처리_수": len(successful_results),
            "실패_처리_수": total_texts - len(successful_results),
            "평균_원문_길이": sum(original_lengths) / len(original_lengths) if original_lengths else 0,
            "평균_처리후_길이": sum(processed_lengths) / len(processed_lengths) if processed_lengths else 0,
            "총_토큰_수": len(all_tokens),
            "고유_토큰_수": len(set(all_tokens)),
            "빈출_토큰_TOP10": token_frequency.most_common(10),
            "처리_단계_통계": dict(self.statistics)
        }

# 감성 분석 파이프라인
def create_korean_sentiment_analyzer():
    """한국어 감성 분석기 생성"""
    
    # 간단한 감성 사전 (실제로는 더 복잡한 사전이 필요)
    positive_words = {
        "좋은", "훌륭한", "멋진", "최고", "완벽한", "만족", "기쁜", "행복한", 
        "사랑", "즐거운", "신나는", "놀라운", "감동", "고마운", "편안한", "재미있는"
    }
    
    negative_words = {
        "나쁜", "끔찍한", "최악", "불만", "화난", "슬픈", "아쉬운", "실망", 
        "짜증", "힘든", "어려운", "문제", "고민", "걱정", "스트레스", "지친"
    }
    
    def analyze_sentiment(text: str) -> Dict[str, Any]:
        tokens = text.split()
        
        positive_count = sum(1 for token in tokens if token in positive_words)
        negative_count = sum(1 for token in tokens if token in negative_words)
        
        # 감성 점수 계산 (-1 ~ 1)
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            sentiment_score = 0
            sentiment_label = "중립"
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
            if sentiment_score > 0.2:
                sentiment_label = "긍정"
            elif sentiment_score < -0.2:
                sentiment_label = "부정"
            else:
                sentiment_label = "중립"
        
        return {
            "감성_점수": round(sentiment_score, 3),
            "감성_라벨": sentiment_label,
            "긍정_단어_수": positive_count,
            "부정_단어_수": negative_count,
            "감성_단어_비율": round(total_sentiment_words / len(tokens) * 100, 1) if tokens else 0,
            "발견된_긍정_단어": [token for token in tokens if token in positive_words],
            "발견된_부정_단어": [token for token in tokens if token in negative_words]
        }
    
    return analyze_sentiment

# 파이프라인 사용 예제
def demonstrate_nlp_pipeline():
    """NLP 파이프라인 시연"""
    
    # 샘플 텍스트
    sample_texts = [
        "안녕하세요!!! 파이썬을 배우는 것이 정말 재미있어요~~~ ㅋㅋㅋ",
        "데이터 분석은 어렵지만 매우 흥미로운 분야입니다. 열심히 공부하고 있어요!",
        "오늘 프로그래밍 과제가 너무 힘들었어요... 스트레스 받네요 ㅠㅠ",
        "새로운 라이브러리를 배우니까 정말 놀랍고 신나는 경험이에요!",
        "버그 때문에 몇 시간을 고생했지만, 결국 해결해서 기뻐요!"
    ]
    
    # 파이프라인 구성
    pipeline = KoreanNLPPipeline()
    
    # 처리기들 추가
    pipeline.add_processor("정규화", pipeline.create_korean_normalizer())
    pipeline.add_processor("토크나이징", pipeline.create_korean_tokenizer(include_particles=False))
    pipeline.add_processor("불용어제거", pipeline.create_stopword_remover())
    pipeline.add_processor("길이필터", pipeline.create_length_filter(min_length=2, max_length=15))
    
    print("한국어 NLP 파이프라인 처리 중...")
    
    # 배치 처리
    results = pipeline.process_batch(sample_texts)
    
    # 결과 출력
    print(f"\n처리 결과:")
    for i, result in enumerate(results, 1):
        print(f"\n텍스트 {i}:")
        print(f"  원문: {result['original']}")
        print(f"  처리후: {result['processed']}")
        print(f"  토큰 수: {result['token_count']}")
    
    # 전체 분석
    analysis = pipeline.analyze_results(results)
    print(f"\n전체 분석 결과:")
    for key, value in analysis.items():
        if key == "빈출_토큰_TOP10":
            print(f"  {key}:")
            for token, count in value:
                print(f"    '{token}': {count}회")
        else:
            print(f"  {key}: {value}")
    
    # 감성 분석 추가
    sentiment_analyzer = create_korean_sentiment_analyzer()
    
    print(f"\n감성 분석 결과:")
    for i, result in enumerate(results, 1):
        sentiment = sentiment_analyzer(result['processed'])
        print(f"\n텍스트 {i}: {sentiment['감성_라벨']} ({sentiment['감성_점수']})")
        if sentiment['발견된_긍정_단어']:
            print(f"  긍정 단어: {sentiment['발견된_긍정_단어']}")
        if sentiment['발견된_부정_단어']:
            print(f"  부정 단어: {sentiment['발견된_부정_단어']}")

# 실행
demonstrate_nlp_pipeline()
```

처리 결과를 원문과 나란히 놓고 보면 단순한 규칙의 한계가 그대로 드러납니다. 그리고 이것이 이 예제에서 가장 배울 것이 많은 부분이에요.

- 텍스트 1의 `~~~`는 `~`로 줄었지만, 텍스트 3의 `ㅠㅠ`는 두 글자뿐이라 그대로 남았습니다. 정규화는 **세 번 이상** 반복될 때만 줄이거든요.
- 텍스트 4의 `신나는`은 토크나이저가 끝의 `는`을 조사로 보고 떼어 `신나`가 됐습니다. 그런데 감성 사전에는 `신나는`으로 적혀 있어서, 감성 분석에서 긍정 단어로 잡히지 않아요. 텍스트 5의 `때문에`도 `에`가 떨어져 `때문`이 되는 바람에 불용어 목록의 `때문에`와 맞지 않아 지워지지 않았습니다.
- `재미있어요~`, `안녕하세요!`처럼 문장부호가 붙은 단어는 사전의 단어와 글자가 달라서 역시 찾지 못합니다.

결국 감성 분석에서 긍정이나 부정으로 판정된 것은 `스트레스`를 찾은 텍스트 3 하나뿐이고, 나머지는 모두 중립으로 나옵니다. 작업대 하나하나는 제대로 일했는데, **앞 단계의 결과가 뒷 단계의 기대와 어긋난** 거예요. 파이프라인을 만들 때는 단계마다 입력과 출력이 어떤 모양인지 맞춰 두는 것이 중요합니다. 감성 사전에 `신나`를 넣거나, 감성 분석을 토크나이징 전에 하도록 순서를 바꿔 보면서 결과가 어떻게 달라지는지 직접 확인해 보세요.

## 10.7 실습 문제

이 장에서 배운 것을 직접 써 보는 문제입니다. 각 문제는 `# 문제:` 주석으로 요구 사항을 적고 바로 아래에 `# 답:`을 붙여 두었어요. 답을 읽기 전에 먼저 직접 짜 보세요. 함수는 짧게 만들어 바로 불러 보고, 결과를 눈으로 확인하는 습관이 가장 좋은 공부입니다.

### 기본 문제 (1-5번)

함수 정의와 기본값 매개변수, 람다를 `key=`에 넘기기, `map()`과 `filter()`, 그리고 첫 데코레이터를 연습합니다.

```python
# 1번: 기본 함수 정의
def korean_grade_calculator(scores: list, weights: list = None) -> dict:
    """한국 학점 계산기"""
    pass

# 문제: 점수 리스트와 가중치를 받아서 가중평균과 학점을 계산하세요
# 답:
def korean_grade_calculator(scores: list, weights: list = None) -> dict:
    if not scores:
        return {"오류": "점수가 없습니다"}
    
    if weights is None:
        weights = [1] * len(scores)
    
    if len(scores) != len(weights):
        return {"오류": "점수와 가중치 개수가 다릅니다"}
    
    weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
    total_weight = sum(weights)
    average = weighted_sum / total_weight
    
    if average >= 95: grade = "A+"
    elif average >= 90: grade = "A"
    elif average >= 85: grade = "B+"
    elif average >= 80: grade = "B"
    elif average >= 75: grade = "C+"
    elif average >= 70: grade = "C"
    else: grade = "F"
    
    return {"평균": round(average, 2), "학점": grade}

result = korean_grade_calculator([85, 92, 78], [3, 4, 3])
print(f"성적 계산 결과: {result}")

# 2번: 람다 함수 활용
korean_cities = ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]
# 문제: 도시명 길이로 정렬하고, 같으면 가나다순으로 정렬하세요
# 답:
sorted_cities = sorted(korean_cities, key=lambda x: (len(x), x))
print(f"정렬된 도시: {sorted_cities}")

# 3번: map() 활용
temperatures_celsius = [25, 30, 15, 35, 20]
# 문제: 섭씨온도를 화씨온도로 변환하고 한글 설명을 추가하세요
# 답:
to_fahrenheit = lambda c: f"{c}°C = {c * 9/5 + 32:.1f}°F"
fahrenheit_temps = list(map(to_fahrenheit, temperatures_celsius))
for temp in fahrenheit_temps:
    print(temp)

# 4번: filter() 활용
korean_words = ["사과", "apple", "바나나", "banana", "컴퓨터", "computer"]
# 문제: 한글이 포함된 단어만 필터링하세요
# 답:
import re
korean_only = list(filter(lambda word: bool(re.search(r'[가-힣]', word)), korean_words))
print(f"한글 포함 단어: {korean_only}")

# 5번: 기본 데코레이터
def korean_log(func):
    """함수 호출을 한글로 로그"""
    def wrapper(*args, **kwargs):
        print(f"함수 '{func.__name__}' 실행 시작")
        result = func(*args, **kwargs)
        print(f"[O] 함수 '{func.__name__}' 실행 완료")
        return result
    return wrapper

@korean_log
def add_numbers(a, b):
    return a + b

result = add_numbers(3, 5)
print(f"결과: {result}")
```

### 중급 문제 (6-10번)

함수를 만들어 돌려주는 고차 함수, 초깃값을 쓰는 `reduce()`, 설정값을 받는 데코레이터, 클로저, 그리고 여러 함수를 이어 붙이는 함수 조합을 다룹니다.

```python
# 6번: 고차 함수 구현
def create_korean_formatter(format_type: str):
    """한국어 포맷터 생성기"""
    pass

# 문제: 다양한 한국 포맷터를 생성하는 함수를 만드세요
# 답:
def create_korean_formatter(format_type: str):
    formatters = {
        "currency": lambda amount: f"{amount:,}원",
        "phone": lambda number: f"{number[:3]}-{number[3:7]}-{number[7:]}",
        "date": lambda date_str: f"{date_str[:4]}년 {date_str[4:6]}월 {date_str[6:8]}일"
    }
    
    if format_type not in formatters:
        raise ValueError(f"지원하지 않는 포맷: {format_type}")
    
    return formatters[format_type]

currency_fmt = create_korean_formatter("currency")
phone_fmt = create_korean_formatter("phone")
date_fmt = create_korean_formatter("date")

print(f"통화: {currency_fmt(1500000)}")
print(f"전화번호: {phone_fmt('01012345678')}")
print(f"날짜: {date_fmt('20231225')}")

# 7번: reduce() 고급 활용
from functools import reduce

sales_data = [
    {"지역": "서울", "매출": 1500000},
    {"지역": "부산", "매출": 1200000}, 
    {"지역": "서울", "매출": 800000},
    {"지역": "대구", "매출": 600000},
    {"지역": "부산", "매출": 900000}
]

# 문제: reduce를 사용해서 지역별 매출 합계를 계산하세요
# 답:
def aggregate_sales(acc, sale):
    region = sale["지역"]
    amount = sale["매출"]
    if region in acc:
        acc[region] += amount
    else:
        acc[region] = amount
    return acc

regional_sales = reduce(aggregate_sales, sales_data, {})
print(f"지역별 매출: {regional_sales}")

# 8번: 매개변수를 받는 데코레이터
def korean_retry_decorator(max_attempts=3):
    """재시도 데코레이터"""
    pass

# 문제: 지정된 횟수만큼 재시도하는 데코레이터를 만드세요
# 답:
def korean_retry_decorator(max_attempts=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    print(f"시도 {attempt}/{max_attempts}")
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        print(f"최종 실패: {e}")
                        raise
                    print(f"실패, 재시도: {e}")
        return wrapper
    return decorator

@korean_retry_decorator(max_attempts=3)
def unstable_function():
    import random
    if random.random() < 0.7:
        raise Exception("일시적 오류")
    return "성공!"

try:
    result = unstable_function()
    print(f"결과: {result}")
except Exception as e:
    print(f"최종 실패: {e}")

# 9번: 클로저 활용
def korean_accumulator_factory(initial_value=0):
    """누적기 팩토리"""
    pass

# 문제: 값을 누적하고 통계를 제공하는 클로저를 만드세요
# 답:
def korean_accumulator_factory(initial_value=0):
    values = [initial_value]
    
    def add(value):
        values.append(value)
        return sum(values)
    
    def get_stats():
        if not values:
            return {"개수": 0, "합계": 0, "평균": 0}
        
        return {
            "개수": len(values),
            "합계": sum(values),
            "평균": sum(values) / len(values),
            "최대값": max(values),
            "최소값": min(values)
        }
    
    add.get_stats = get_stats
    add.values = values
    
    return add

acc = korean_accumulator_factory(10)
print(f"누적: {acc(5)}, {acc(15)}, {acc(20)}")
print(f"통계: {acc.get_stats()}")

# 10번: 함수 조합
def compose(*functions):
    """함수 조합기"""
    pass

# 문제: 여러 함수를 조합하는 compose 함수를 만드세요
# 답:
def compose(*functions):
    return lambda x: reduce(lambda acc, f: f(acc), functions, x)

# 한국어 텍스트 처리 함수들
def remove_spaces(text):
    return text.replace(" ", "")

def add_prefix(text):
    return f"한국어: {text}"

def add_suffix(text):
    return f"{text} (처리완료)"

# 함수 조합
text_processor = compose(remove_spaces, add_prefix, add_suffix)
result = text_processor("안녕 하세요 파이썬")
print(f"조합 결과: {result}")
```

### 고급 문제 (11-15번)

10.6절처럼 작은 함수를 조립해 큰 일을 하는 문제들입니다. 파이프라인, 실행 중에 함수 만들기, 메모이제이션(계산 결과 저장) 데코레이터, 함수 체이닝, 함수형 유틸리티 모음을 만들어 봅니다.

```python
# 11번: 복잡한 파이프라인
class KoreanTextPipeline:
    def __init__(self):
        self.steps = []
    
    def add_step(self, name, func):
        self.steps.append((name, func))
        return self
    
    def process(self, text):
        # 문제: 각 단계를 거쳐 텍스트를 처리하는 파이프라인을 구현하세요
        pass

# 답:
class KoreanTextPipeline:
    def __init__(self):
        self.steps = []
    
    def add_step(self, name, func):
        self.steps.append((name, func))
        return self
    
    def process(self, text):
        result = {
            "original": text,
            "final": text,
            "steps": []
        }
        
        current_text = text
        for step_name, step_func in self.steps:
            try:
                new_text = step_func(current_text)
                result["steps"].append({
                    "name": step_name,
                    "input": current_text,
                    "output": new_text
                })
                current_text = new_text
            except Exception as e:
                result["steps"].append({
                    "name": step_name,
                    "error": str(e)
                })
                break
        
        result["final"] = current_text
        return result

pipeline = KoreanTextPipeline()
pipeline.add_step("대문자변환", str.upper)
pipeline.add_step("접두어추가", lambda x: f"처리: {x}")
pipeline.add_step("길이계산", lambda x: f"{x} (길이: {len(x)})")

result = pipeline.process("안녕하세요")
print(f"파이프라인 결과: {result}")

# 12번: 동적 함수 생성
def create_korean_validator_function(rules):
    """검증 규칙으로 함수 생성"""
    pass

# 문제: 규칙 딕셔너리를 받아서 검증 함수를 동적으로 생성하세요
# 답:
def create_korean_validator_function(rules):
    def validator(data):
        errors = []
        
        for field, field_rules in rules.items():
            if field not in data:
                errors.append(f"{field}: 필수 필드입니다")
                continue
            
            value = data[field]
            
            for rule_name, rule_func in field_rules.items():
                try:
                    if not rule_func(value):
                        errors.append(f"{field}: {rule_name} 규칙 위반")
                except Exception as e:
                    errors.append(f"{field}: {rule_name} 검증 오류 - {e}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    return validator

# 검증 규칙 정의
validation_rules = {
    "이름": {
        "비어있지않음": lambda x: len(x.strip()) > 0,
        "한글만": lambda x: all('가' <= c <= '힣' for c in x.strip()),
        "길이제한": lambda x: 2 <= len(x.strip()) <= 5
    },
    "나이": {
        "양수": lambda x: isinstance(x, int) and x > 0,
        "범위": lambda x: 0 <= x <= 150
    }
}

validator = create_korean_validator_function(validation_rules)

test_data = {"이름": "김철수", "나이": 25}
result = validator(test_data)
print(f"검증 결과: {result}")

# 13번: 메모이제이션 데코레이터
def korean_memoize(maxsize=128):
    """메모이제이션 데코레이터"""
    pass

# 문제: 결과를 캐시하는 메모이제이션 데코레이터를 만드세요
# 답:
def korean_memoize(maxsize=128):
    def decorator(func):
        cache = {}
        stats = {"hits": 0, "misses": 0}
        
        def wrapper(*args, **kwargs):
            # 키 생성 (해시 가능한 형태로)
            key = (args, tuple(sorted(kwargs.items())))
            
            if key in cache:
                stats["hits"] += 1
                print(f"캐시 히트: {func.__name__}")
                return cache[key]
            
            # 캐시 크기 제한
            if len(cache) >= maxsize:
                # 가장 오래된 항목 제거
                oldest_key = next(iter(cache))
                del cache[oldest_key]
            
            stats["misses"] += 1
            result = func(*args, **kwargs)
            cache[key] = result
            
            return result
        
        wrapper.cache_info = lambda: stats
        wrapper.cache_clear = lambda: cache.clear()
        
        return wrapper
    return decorator

@korean_memoize(maxsize=10)
def fibonacci_korean(n):
    print(f"피보나치 {n} 계산 중...")
    if n <= 1:
        return n
    return fibonacci_korean(n-1) + fibonacci_korean(n-2)

result = fibonacci_korean(10)
print(f"피보나치(10): {result}")
print(f"캐시 정보: {fibonacci_korean.cache_info()}")

# 14번: 함수 체이닝
class KoreanDataProcessor:
    def __init__(self, data):
        self.data = data
    
    def filter_korean(self):
        # 문제: 메서드 체이닝이 가능한 데이터 처리기를 만드세요
        pass

# 답:
class KoreanDataProcessor:
    def __init__(self, data):
        self.data = data
    
    def filter_korean(self):
        import re
        self.data = [item for item in self.data if re.search(r'[가-힣]', str(item))]
        return self
    
    def filter_length(self, min_len=2, max_len=10):
        self.data = [item for item in self.data if min_len <= len(str(item)) <= max_len]
        return self
    
    def sort_by_length(self):
        self.data = sorted(self.data, key=lambda x: len(str(x)))
        return self
    
    def take(self, n):
        self.data = self.data[:n]
        return self
    
    def get_result(self):
        return self.data

words = ["안녕", "hello", "세상", "world", "프로그래밍", "programming", "파이썬"]
result = (KoreanDataProcessor(words)
          .filter_korean()
          .filter_length(min_len=2, max_len=5)
          .sort_by_length()
          .take(3)
          .get_result())

print(f"체이닝 결과: {result}")

# 15번: 고급 함수형 유틸리티
def korean_functional_utils():
    """한국어 함수형 유틸리티 모음"""
    
    def curry(func):
        """커링 함수"""
        pass
    
    def partial_korean(func, *partial_args, **partial_kwargs):
        """한국어 부분 적용"""
        pass

# 문제: 커링과 부분적용을 구현하세요
# 답:
def korean_functional_utils():
    
    def curry(func, arity=None):
        if arity is None:
            arity = func.__code__.co_argcount
        
        def curried(*args, **kwargs):
            if len(args) + len(kwargs) >= arity:
                return func(*args, **kwargs)
            else:
                def partial(*more_args, **more_kwargs):
                    return curried(*(args + more_args), **{**kwargs, **more_kwargs})
                return partial
        
        return curried
    
    def partial_korean(func, *partial_args, **partial_kwargs):
        def wrapper(*args, **kwargs):
            all_args = partial_args + args
            all_kwargs = {**partial_kwargs, **kwargs}
            return func(*all_args, **all_kwargs)
        
        return wrapper
    
    return curry, partial_korean

curry, partial_korean = korean_functional_utils()

# 한국어 인사 함수
def korean_greeting(greeting, name, title=""):
    return f"{greeting}, {name}{title}님!"

# 커링 적용
curried_greeting = curry(korean_greeting)
formal_greeting = curried_greeting("안녕하십니까")
casual_greeting = curried_greeting("안녕하세요")

print(f"정중한 인사: {formal_greeting('김철수', ' 부장')}")
print(f"일반 인사: {casual_greeting('이영희')}")

# 부분 적용
morning_greet = partial_korean(korean_greeting, "좋은 아침입니다")
print(f"아침 인사: {morning_greet('박민수', ' 교수')}")
```

## 10.8 다음 장 미리보기

다음 Chapter 11에서는 **객체 지향 프로그래밍**을 학습합니다:

### 주요 내용 미리보기
- **클래스와 객체**: 기본 개념과 인스턴스 생성
- **상속과 다형성**: 클래스 계층 구조와 메서드 오버라이딩
- **캡슐화**: private 속성과 프로퍼티 활용
- **특수 메서드**: `__init__`, `__str__`, `__eq__` 등 매직 메서드
- **추상 클래스**: ABC와 추상 메서드 구현
- **실무 프로젝트**: 한국 전자상거래 시스템 설계

### 연결 포인트
- 함수형 프로그래밍 → 객체 지향 프로그래밍 패러다임
- 고차 함수와 클로저 → 메서드와 인스턴스 변수
- 데코레이터 → 클래스 데코레이터와 프로퍼티

함수형 프로그래밍의 핵심을 완전히 이해했다면, 이제 데이터와 기능을 하나로 묶어서 관리하는 객체 지향 프로그래밍으로 더욱 구조화된 코드를 작성할 준비가 되었습니다!

---

> **학습 팁**: 함수형 프로그래밍은 불변성과 순수 함수를 중시합니다. map, filter, reduce와 같은 고차 함수들을 적극 활용하고, 데코레이터를 통해 횡단 관심사를 분리하세요.

**다음 장에서 만나요!** 