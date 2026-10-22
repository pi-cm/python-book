# Chapter 11: 객체 지향 프로그래밍

> **학습 목표**  
> - 클래스와 객체의 기본 개념 이해
> - 속성과 메서드를 활용한 데이터 캡슐화
> - 상속과 다형성을 통한 코드 재사용
> - 특수 메서드(매직 메서드)로 객체 동작 커스터마이징
> - 추상 클래스와 인터페이스 설계 패턴
> - 한국 전자상거래 시스템 구현

---

## 들어가며: 객체가 뭘까요?

주변에 있는 자동차 한 대를 떠올려 보세요. 자동차에는 색상, 모델, 속도, 남은 연료 같은 **특징**이 있고, 가속, 감속, 방향 전환, 정지 같은 **기능**이 있죠. 빨간 세단도, 하얀 SUV도 특징의 값은 서로 다르지만 할 수 있는 일은 똑같습니다.

프로그래밍에서는 이렇게 특징과 기능을 한 덩어리로 묶은 것을 **객체(object)** 라고 부릅니다. 그리고 "자동차라면 이런 특징과 기능을 가진다"고 적어 둔 설계도가 **클래스(class)** 예요. 흔히 붕어빵 틀과 붕어빵에 비유합니다. 틀(클래스)은 하나지만 거기서 찍어 낸 붕어빵(객체)은 여러 개고, 팥이 들었는지 슈크림이 들었는지는 하나하나 다를 수 있죠.

그런데 왜 굳이 이렇게 묶어야 할까요? 이야기는 1966년 미국 유타 대학교로 거슬러 올라갑니다. 대학원생이던 앨런 케이(Alan Kay)는 고민이 있었어요. 프로그램은 기능을 더하고 고칠수록 필연적으로 복잡해지는데, 변수는 프로그램 어디서든 건드릴 수 있으니 언제 어디서 누가 값을 바꿨는지 알 수가 없었거든요. 생물학을 공부했던 그는 세포를 떠올렸습니다. 세포는 저마다 필요한 데이터와 역할을 안에 품고, 다른 세포의 속사정은 모른 채 신호만 주고받으며 하나의 생명을 이룹니다. 프로그램도 이렇게 **독립된 작은 객체들이 메시지를 주고받는 모임**으로 만들 수 있지 않을까? 이 생각이 객체 지향 프로그래밍(Object-Oriented Programming, OOP)이라는 이름의 출발점이 되었습니다.

> "OOP to me means only messaging, local retention and protection and hiding of state-process, and extreme late-binding of all things." — Alan Kay

어려워 보이지만 핵심은 세 가지예요. 객체끼리는 **메시지(메서드 호출)** 로만 대화하고, 자기 **상태는 안에 감춰서 스스로 지키고**, 누가 그 메시지를 처리할지는 **실행하는 순간에 정해진다**는 것. 이 장에서는 그중 앞의 두 가지, 즉 클래스를 만들고 데이터를 지키는 법을 배우고, 객체가 `+`나 `==` 같은 연산자에 반응하게 만드는 매직 메서드까지 다룹니다. 세 번째 이야기는 13장 상속과 다형성에서 이어집니다.

> **Q. 객체 지향이 있으면 다른 지향도 있나요? 함수 지향, 절차 지향 같은 거요?**
> 네, 있습니다. 명령을 위에서 아래로 차례차례 적어 나가는 방식을 **절차 지향(절차적 프로그래밍)**, 값을 받아 새 값을 돌려주는 함수를 조립해 프로그램을 만드는 방식을 **함수형 프로그래밍**이라고 해요(10장에서 맛봤죠). 어느 하나가 정답은 아닙니다. 파이썬은 세 방식을 모두 쓸 수 있는 언어라서, 짧은 스크립트는 절차적으로, 데이터 변환은 함수형으로, 등장인물이 많은 프로그램은 객체 지향으로 섞어 쓰는 경우가 많아요.

## 11.1 클래스와 객체 기본 개념

### 객체 지향 사고의 전환

클래스를 만드는 문법은 `class 이름:`으로 시작합니다. 가장 단순한 클래스는 값 몇 개에 이름을 붙여 묶어 두는 구조적인 자료형처럼 쓸 수도 있어요.

```python
class Structure:
    A = 1
    B = 2

print(Structure.A, Structure.B)  # 1 2
```

`Structure.A`처럼 **점(`.`)** 으로 안에 든 값을 꺼냅니다. 객체에 붙어 있는 이런 이름을 **속성(attribute)** 이라고 하고, 클래스 안에 정의한 함수는 **메서드(method)** 라고 불러요. 속성이 객체의 "명사"라면 메서드는 "동사"인 셈입니다.

이제 학생 정보를 다루는 두 가지 방법을 비교해 봅시다. 절차적인 방식에서는 이름, 나이, 전공이 각각 따로 노는 변수이고, 함수는 그 값들을 매번 인자로 받아야 합니다. 학생이 100명이 되면 변수가 300개로 늘고, 어떤 이름과 어떤 나이가 한 사람의 것인지 우리가 직접 맞춰 줘야 하죠. 객체 지향 방식은 한 학생의 정보와 그 학생이 할 수 있는 일을 `Student`라는 틀 하나에 담습니다.

```python
# 절차적 프로그래밍 방식 (기존)
student_name = "김철수"
student_age = 20
student_major = "컴퓨터과학과"

def print_student_info(name, age, major):
    print(f"학생: {name}, 나이: {age}, 전공: {major}")

def calculate_graduation_year(age, current_year=2024):
    # 22세에 졸업한다고 가정
    return current_year + (22 - age) if age < 22 else current_year

# 객체 지향 방식 (개선)
class Student:
    """한국 대학생 클래스"""
    
    def __init__(self, name: str, age: int, major: str):
        self.name = name
        self.age = age
        self.major = major
        self.current_year = 2024
    
    def introduce(self) -> str:
        """자기소개 메서드"""
        return f"안녕하세요! {self.name}입니다. {self.age}세이고 {self.major}를 전공하고 있습니다."
    
    def calculate_graduation_year(self) -> int:
        """졸업 예상 연도 계산"""
        return self.current_year + (22 - self.age) if self.age < 22 else self.current_year

# 객체 생성 및 사용
student1 = Student("김철수", 20, "컴퓨터과학과")
student2 = Student("이영희", 19, "경영학과")

print(student1.introduce())
print(f"졸업 예상: {student1.calculate_graduation_year()}년")
```

`Student("김철수", 20, "컴퓨터과학과")`처럼 클래스 이름을 함수처럼 부르면 새 객체가 하나 만들어지고, 곧바로 `__init__` 메서드가 실행되어 그 객체에 이름·나이·전공을 채워 넣습니다. 이렇게 어떤 클래스로 만든 객체를 그 클래스의 **인스턴스(instance)** 라고 해요. `student1`은 `Student`의 인스턴스입니다.

처음 보면 가장 헷갈리는 게 `self`죠. `self`는 **지금 다루고 있는 바로 그 객체 자신**을 가리킵니다. `student1.introduce()`라고 부르면 파이썬이 `student1`을 `self` 자리에 알아서 넣어 주기 때문에, 메서드 안에서는 `self.name`으로 "내 이름"을 꺼낼 수 있어요. 그래서 절차적 방식과 달리 `introduce()`를 부를 때 이름이나 나이를 인자로 넘길 필요가 없습니다. 데이터가 이미 객체 안에 있으니까요. `student2`로 `introduce()`를 부르면 같은 메서드가 이번에는 "이영희"를 꺼냅니다.

객체와 인스턴스가 다른 건지 궁금할 수 있는데, 거의 같은 말입니다. 클래스로 만든 실체 하나하나가 객체이고, 그 객체가 "어떤 클래스의" 것인지 함께 말할 때 인스턴스라고 불러요. "`student1`은 객체다"와 "`student1`은 `Student`의 인스턴스다"는 같은 대상을 가리킵니다.

### 클래스 설계 원칙

은행 계좌를 클래스로 만들어 보면 클래스에 무엇을 담아야 하는지 감이 옵니다. 여기서는 두 종류의 변수를 눈여겨보세요.

- **클래스 변수**: `class` 바로 아래에 적은 `bank_name`, `interest_rate`, `account_count`. 클래스에 딱 하나만 있고 모든 계좌가 함께 봅니다. 반 전체가 같이 쓰는 출석부 같은 거예요.
- **인스턴스 변수**: `__init__` 안에서 `self.`를 붙여 만든 `owner_name`, `balance`. 계좌마다 따로 갖는 개인 수첩입니다.

```python
from datetime import datetime
from typing import List, Optional

class KoreanBankAccount:
    """한국 은행 계좌 클래스"""
    
    # 클래스 변수 (모든 인스턴스가 공유)
    bank_name = "한국은행"
    interest_rate = 0.02
    account_count = 0
    
    def __init__(self, owner_name: str, initial_balance: int = 0):
        # 인스턴스 변수 (각 객체마다 고유)
        self.owner_name = owner_name
        self.balance = initial_balance
        self.created_at = datetime.now()
        self.transaction_history: List[str] = []
        
        # 계좌 번호 생성 (클래스 변수 활용)
        KoreanBankAccount.account_count += 1
        self.account_number = f"KB{KoreanBankAccount.account_count:06d}"
        
        # 첫 거래 기록
        self.transaction_history.append(
            f"{self.created_at.strftime('%Y-%m-%d %H:%M')} - 계좌 개설 (초기잔액: {initial_balance:,}원)"
        )
    
    def deposit(self, amount: int) -> bool:
        """입금"""
        if amount <= 0:
            print("[X] 입금액은 0원보다 커야 합니다.")
            return False
        
        self.balance += amount
        transaction = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - 입금: +{amount:,}원 (잔액: {self.balance:,}원)"
        self.transaction_history.append(transaction)
        print(f"[O] {amount:,}원 입금되었습니다. 현재 잔액: {self.balance:,}원")
        return True
    
    def withdraw(self, amount: int) -> bool:
        """출금"""
        if amount <= 0:
            print("[X] 출금액은 0원보다 커야 합니다.")
            return False
        
        if amount > self.balance:
            print(f"[X] 잔액이 부족합니다. 현재 잔액: {self.balance:,}원")
            return False
        
        self.balance -= amount
        transaction = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - 출금: -{amount:,}원 (잔액: {self.balance:,}원)"
        self.transaction_history.append(transaction)
        print(f"[O] {amount:,}원 출금되었습니다. 현재 잔액: {self.balance:,}원")
        return True
    
    def get_account_info(self) -> dict:
        """계좌 정보 조회"""
        return {
            "은행": self.bank_name,
            "계좌번호": self.account_number,
            "예금주": self.owner_name,
            "현재잔액": f"{self.balance:,}원",
            "개설일": self.created_at.strftime("%Y년 %m월 %d일"),
            "거래횟수": len(self.transaction_history)
        }
    
    def print_statement(self) -> None:
        """거래 내역 출력"""
        print(f"\n{self.owner_name}님의 거래내역 ({self.account_number})")
        print("=" * 60)
        for transaction in self.transaction_history[-10:]:  # 최근 10건만
            print(transaction)
        print("=" * 60)

# 사용 예제
account1 = KoreanBankAccount("김철수", 100000)
account2 = KoreanBankAccount("이영희", 50000)

print("계좌 정보:")
for key, value in account1.get_account_info().items():
    print(f"{key}: {value}")

account1.deposit(50000)
account1.withdraw(30000)
account1.print_statement()

print(f"\n총 개설된 계좌 수: {KoreanBankAccount.account_count}개")
```

계좌를 두 개 열었으니 마지막 줄은 "총 개설된 계좌 수: 2개"가 나옵니다. `account_count`가 클래스에 하나뿐인 출석부라서, 어느 계좌를 만들든 같은 숫자가 1씩 올라가거든요. 그 숫자로 `KB000001`, `KB000002` 같은 계좌번호도 만들어 냅니다.

여기서 `KoreanBankAccount.account_count += 1`처럼 **클래스 이름을 붙여** 올린 데는 이유가 있습니다. `self.account_count += 1`이라고 쓰면 파이썬은 클래스의 출석부를 고치는 대신 그 계좌 객체에 같은 이름의 개인 수첩을 새로 만들어 버려요. 클래스 쪽 숫자는 그대로 0에 머물죠. 공유하는 값을 바꿀 때는 클래스 이름으로 접근한다고 기억해 두세요.

`deposit()`과 `withdraw()`도 살펴보세요. 0원 이하는 받지 않고, 잔액보다 많이 빼려 하면 거절하고, 성공하면 거래 내역을 남깁니다. 잔액을 바꾸는 규칙이 전부 계좌 객체 안에 들어 있는 거예요. 그런데 누군가 `account1.balance = -1000000`이라고 직접 써 버리면 어떨까요? 파이썬은 막지 않습니다. 규칙을 다 건너뛰고 내역도 남지 않죠. 이렇게 내부 값을 밖에서 마음대로 고치면 객체로 묶은 의미가 사라집니다. 이걸 막는 도구가 다음 절의 프로퍼티입니다.

> **Q. 자동차가 객체라면 핸들이나 바퀴는요? 그것도 객체 같은데요?**
> 맞습니다. 핸들도, 바퀴도 그 자체로 객체예요. 그리고 그 작은 객체들이 모인 자동차도 하나의 객체입니다. 앨런 케이가 말한 "독립적인 작은 객체들의 모임"이 바로 이것이에요. 위의 계좌도 마찬가지입니다. `transaction_history`는 리스트 객체, `created_at`은 `datetime` 객체이고, 계좌는 이 객체들을 품고 있는 더 큰 객체죠. 이렇게 객체가 다른 객체를 **가지는** 관계를 조합(composition)이라고 하는데, 13장에서 상속과 나란히 놓고 다시 살펴봅니다.

## 11.2 속성과 메서드 고급 활용

### 프로퍼티 데코레이터

나이를 객체에 저장해 두면 해가 바뀔 때마다 틀린 값이 되어 버립니다. 생년월일만 저장하고 나이는 필요할 때마다 계산하는 게 맞죠. 그렇다고 `person.get_age()`처럼 괄호를 붙여 부르게 하면 쓰는 사람은 "나이는 값인데 왜 함수지?" 하고 헷갈립니다. 전화번호는 반대로 아무 문자열이나 들어오면 안 되니, 넣는 순간에 형식을 검사하고 싶고요.

`@property`가 이 두 가지를 해결합니다. 메서드 위에 `@property`를 붙이면 그 메서드는 괄호 없이 `person.age`처럼 **속성처럼 읽히고**, 읽을 때마다 메서드가 실행됩니다. 같은 이름에 `@이름.setter`를 붙인 메서드를 하나 더 만들면 `person.phone = "..."`처럼 **값을 넣을 때** 그 메서드가 대신 실행되어 검사를 할 수 있어요.

이름 앞의 밑줄 하나(`self._name`)는 파이썬 개발자들끼리의 약속입니다. "이건 안에서만 쓰는 값이니 밖에서 직접 건드리지 마세요"라는 표시죠. 자물쇠는 아니라서 `person._name`으로 접근하면 막히지는 않지만, 그렇게 쓰는 순간 약속을 어긴 겁니다.

```python
from datetime import datetime, date
from typing import Optional
import re

class KoreanPerson:
    """한국인 정보 클래스 (프로퍼티 활용)"""
    
    def __init__(self, name: str, birth_date: str, phone: str = None):
        self._name = name
        self._birth_date = self._validate_date(birth_date)
        self._phone = phone
        self._email = None
    
    @property
    def name(self) -> str:
        """이름 프로퍼티 (읽기 전용)"""
        return self._name
    
    @property
    def age(self) -> int:
        """나이 자동 계산 프로퍼티"""
        today = date.today()
        birth = datetime.strptime(self._birth_date, "%Y-%m-%d").date()
        age = today.year - birth.year
        
        # 생일이 지나지 않았으면 1살 빼기
        if today < birth.replace(year=today.year):
            age -= 1
        
        return age
    
    @property
    def korean_age(self) -> int:
        """세는 나이 계산 (올해 연도 - 출생연도 + 1)"""
        return date.today().year - self.birth_year + 1
    
    @property
    def birth_year(self) -> int:
        """출생연도"""
        return datetime.strptime(self._birth_date, "%Y-%m-%d").year
    
    @property
    def phone(self) -> Optional[str]:
        """전화번호"""
        return self._phone
    
    @phone.setter
    def phone(self, value: str) -> None:
        """전화번호 설정 (유효성 검사 포함)"""
        if value is None:
            self._phone = None
            return
        
        # 한국 휴대폰 번호 형식 검증
        phone_pattern = r'^010-\d{4}-\d{4}$'
        if not re.match(phone_pattern, value):
            raise ValueError("올바른 휴대폰 번호 형식이 아닙니다 (010-0000-0000)")
        
        self._phone = value
    
    @property
    def email(self) -> Optional[str]:
        """이메일"""
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        """이메일 설정 (유효성 검사 포함)"""
        if value is None:
            self._email = None
            return
        
        # 간단한 이메일 형식 검증
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValueError("올바른 이메일 형식이 아닙니다")
        
        self._email = value
    
    @staticmethod
    def _validate_date(date_str: str) -> str:
        """날짜 형식 검증"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            raise ValueError("날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
    
    def introduce(self) -> str:
        """자기소개"""
        intro = f"안녕하세요! {self.name}입니다."
        intro += f" {self.age}세 ({self.korean_age}세, 한국나이)이고"
        intro += f" {self.birth_year}년생입니다."
        
        if self.phone:
            intro += f" 연락처는 {self.phone}입니다."
        
        return intro

# 사용 예제
person = KoreanPerson("김철수", "1995-05-15")
print(person.introduce())

# 프로퍼티 활용
print(f"만 나이: {person.age}세")
print(f"한국 나이: {person.korean_age}세")

# setter를 통한 값 설정
person.phone = "010-1234-5678"
person.email = "kim@example.com"

print(f"전화번호: {person.phone}")
print(f"이메일: {person.email}")

# 잘못된 형식 입력 시 에러 발생
try:
    person.phone = "010-12345-6789"  # 잘못된 형식
except ValueError as e:
    print(f"오류: {e}")
```

실행해 보면 `person.age`에 괄호가 없는데도 오늘 날짜 기준으로 계산된 나이가 나옵니다. 마지막 `try` 부분에서는 `person.phone = "010-12345-6789"`라는 평범한 대입문이 setter를 거치면서 형식 검사에 걸려 `오류: 올바른 휴대폰 번호 형식이 아닙니다 (010-0000-0000)`가 출력되죠. 잘못된 값이 객체 안으로 들어가기 전에 문 앞에서 막힌 겁니다.

`name`에는 setter를 만들지 않았다는 점도 보세요. 그래서 `person.name = "이영희"`라고 쓰면 setter가 없다는 `AttributeError`가 납니다. setter를 빼는 것만으로 **읽기 전용** 속성이 되는 거예요.

메서드 위에 붙은 `@`가 궁금했을 텐데요, **데코레이터(decorator)** 라는 표시입니다. 바로 아래 함수를 받아서 기능을 덧붙인 것으로 바꿔 끼우라는 뜻이에요. `@property`는 "이 메서드를 속성처럼 읽히게 해 줘", `@classmethod`는 "이 메서드는 객체 말고 클래스를 받게 해 줘"라고 파이썬에게 알려 주는 거죠. 데코레이터를 직접 만드는 방법은 10장 10.4절에서 다뤘습니다.

### 클래스 메서드와 정적 메서드

지금까지 본 메서드는 모두 첫 번째 매개변수로 `self`를 받았습니다. 데코레이터 없이 정의한 이런 메서드를 **인스턴스 메서드**라고 해요. 클래스 안의 메서드에는 두 종류가 더 있습니다.

| 종류 | 표시 | 첫 매개변수 | 주로 쓰는 곳 |
|---|---|---|---|
| 인스턴스 메서드 | 없음 | `self` (객체 자신) | 객체 하나의 데이터를 읽고 바꿀 때 |
| 클래스 메서드 | `@classmethod` | `cls` (클래스 자신) | 다른 형태의 데이터로 객체를 만들 때, 클래스 전체 정보를 다룰 때 |
| 정적 메서드 | `@staticmethod` | 없음 | 클래스와 관련은 있지만 객체 데이터가 필요 없는 도우미 함수 |

클래스 메서드가 가장 빛나는 곳은 "또 다른 생성 방법"입니다. 회원 정보가 어떤 때는 튜플로, 어떤 때는 딕셔너리로, 어떤 때는 JSON 문자열로 들어온다고 해 볼게요. `__init__`은 하나뿐이니 형태마다 `fromTuple`, `fromDictionary`, `create_from_json` 같은 클래스 메서드를 만들어 두고, 각자 데이터를 풀어서 `cls(...)`로 객체를 만들어 돌려주면 됩니다. 아래 예제의 `create_from_dict`와 `create_from_json`이 그런 역할이에요.

```python
from typing import ClassVar, List
from datetime import datetime
import json

class KoreanUniversity:
    """한국 대학교 클래스"""
    
    # 클래스 변수 (타입 힌트 포함)
    total_universities: ClassVar[int] = 0
    university_list: ClassVar[List[str]] = []
    
    def __init__(self, name: str, location: str, founded_year: int):
        self.name = name
        self.location = location
        self.founded_year = founded_year
        self.student_count = 0
        self.departments: List[str] = []
        
        # 클래스 변수 업데이트
        KoreanUniversity.total_universities += 1
        KoreanUniversity.university_list.append(name)
    
    @classmethod
    def create_from_dict(cls, data: dict) -> 'KoreanUniversity':
        """딕셔너리로부터 대학교 객체 생성"""
        return cls(
            name=data['name'],
            location=data['location'],
            founded_year=data['founded_year']
        )
    
    @classmethod
    def create_from_json(cls, json_str: str) -> 'KoreanUniversity':
        """JSON 문자열로부터 대학교 객체 생성"""
        data = json.loads(json_str)
        return cls.create_from_dict(data)
    
    @classmethod
    def get_statistics(cls) -> dict:
        """대학교 통계 반환"""
        return {
            "총_대학수": cls.total_universities,
            "대학_목록": cls.university_list.copy(),
            "등록_시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @staticmethod
    def is_valid_year(year: int) -> bool:
        """설립 연도 유효성 검사 (정적 메서드)"""
        current_year = datetime.now().year
        return 1000 <= year <= current_year  # 천 년보다 이전 연도는 잘못 입력한 값으로 본다
    
    @staticmethod
    def calculate_history_length(founded_year: int) -> int:
        """대학 역사 계산"""
        return datetime.now().year - founded_year
    
    def add_department(self, department: str) -> None:
        """학과 추가"""
        if department not in self.departments:
            self.departments.append(department)
            print(f"[O] {self.name}에 {department} 추가됨")
        else:
            print(f"[X] {department}는 이미 존재합니다")
    
    def get_info(self) -> dict:
        """대학교 정보 반환"""
        return {
            "대학명": self.name,
            "소재지": self.location,
            "설립년도": self.founded_year,
            "역사": f"{self.calculate_history_length(self.founded_year)}년",
            "학생수": f"{self.student_count:,}명",
            "학과수": len(self.departments),
            "학과목록": self.departments
        }

# 사용 예제
# 일반적인 생성
snu = KoreanUniversity("서울대학교", "서울", 1946)
yonsei = KoreanUniversity("연세대학교", "서울", 1885)

# 클래스 메서드를 통한 생성
korea_data = {
    "name": "고려대학교",
    "location": "서울", 
    "founded_year": 1905
}
korea_univ = KoreanUniversity.create_from_dict(korea_data)

# JSON을 통한 생성
kaist_json = '{"name": "KAIST", "location": "대전", "founded_year": 1971}'
kaist = KoreanUniversity.create_from_json(kaist_json)

# 학과 추가
snu.add_department("컴퓨터공학과")
snu.add_department("경영학과")
snu.student_count = 28000

# 정적 메서드 사용
print(f"1885년이 유효한 설립연도인가? {KoreanUniversity.is_valid_year(1885)}")
print(f"연세대 역사: {KoreanUniversity.calculate_history_length(1885)}년")

# 클래스 메서드로 통계 확인
stats = KoreanUniversity.get_statistics()
print(f"\n대학교 통계:")
for key, value in stats.items():
    print(f"{key}: {value}")

# 개별 대학 정보
print(f"\n서울대 정보:")
for key, value in snu.get_info().items():
    print(f"{key}: {value}")
```

대학을 네 곳 만들었는데 두 곳은 `KoreanUniversity(...)`로, 두 곳은 클래스 메서드로 만들었습니다. 그런데 통계의 `총_대학수`는 4로 나와요. 클래스 메서드가 결국 `cls(...)`를 불러 객체를 만들기 때문에 `__init__`이 똑같이 실행되고, 거기서 클래스 변수의 숫자도 올라간 거죠. `cls`가 `KoreanUniversity`를 가리키니 `cls(...)`는 `KoreanUniversity(...)`와 같은 말입니다.

정적 메서드 `is_valid_year(1885)`는 `True`를 돌려줍니다. 이 메서드는 "1000년부터 올해까지"를 유효한 설립 연도로 보는데, 1885년은 그 안에 있으니까요. 계산에 필요한 건 연도 하나뿐이고 어떤 대학 객체의 정보도 쓰지 않죠. 정적 메서드는 `self`도 `cls`도 받지 않으니 객체를 만들지 않고 `KoreanUniversity.is_valid_year(...)`처럼 클래스 이름으로 바로 부를 수 있습니다.

> **Q. 정적 메서드는 객체도 클래스도 안 쓰는데, 이럴 거면 클래스 안에 왜 넣나요?**
> 좋은 질문이에요. 사실 정적 메서드는 클래스 밖의 평범한 함수로 빼도 똑같이 동작합니다. 그래도 안에 두는 이유는 **정리**예요. "설립 연도가 유효한가"는 대학교 이야기이니 `KoreanUniversity.is_valid_year`라는 이름으로 대학교 클래스 옆에 두면, 나중에 코드를 읽는 사람이 이 함수가 어디에 쓰이는지 바로 압니다. 관련 없는 곳에서도 두루 쓰는 함수라면 밖에 두는 편이 낫고요.

## 11.3 상속과 다형성

### 기본 상속

비슷한 클래스를 여러 개 만들다 보면 같은 코드가 반복됩니다. 자동차든 전기차든 브랜드, 모델, 연식, 주행거리가 있고 운전을 하죠. 이 공통 부분을 부모 클래스 `Vehicle`에 한 번만 적고, `KoreanCar`와 `ElectricCar`는 `class KoreanCar(Vehicle):`처럼 괄호 안에 부모를 적어 **물려받은 뒤 다른 부분만** 씁니다. 이것이 **상속(inheritance)** 이에요. 자식 클래스의 `__init__`에서 부르는 `super().__init__(...)`은 "부모가 하던 초기화를 먼저 해 줘"라는 뜻입니다.

`Vehicle(ABC)`와 `@abstractmethod`는 "자식이라면 이 메서드를 반드시 만들어야 한다"는 약속을 거는 장치입니다. 약속이 걸린 `Vehicle` 자체로는 객체를 만들 수 없어서 `Vehicle(...)`을 부르면 `TypeError`가 나요. 상속, `super()`, 추상 클래스는 13장에서 하나씩 깊게 다루니, 여기서는 흐름만 따라가 보세요.

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

class Vehicle(ABC):
    """차량 추상 기본 클래스"""
    
    def __init__(self, brand: str, model: str, year: int, price: int):
        self.brand = brand
        self.model = model
        self.year = year
        self.price = price
        self.mileage = 0
        self.is_running = False
    
    @abstractmethod
    def start_engine(self) -> str:
        """엔진 시작 (추상 메서드)"""
        pass
    
    @abstractmethod
    def stop_engine(self) -> str:
        """엔진 정지 (추상 메서드)"""
        pass
    
    @abstractmethod
    def get_fuel_efficiency(self) -> float:
        """연비 반환 (추상 메서드)"""
        pass
    
    def get_basic_info(self) -> str:
        """기본 정보 반환"""
        return f"{self.brand} {self.model} ({self.year}년식)"
    
    def drive(self, distance: int) -> str:
        """운전"""
        if not self.is_running:
            return "[X] 엔진을 먼저 시작하세요"
        
        self.mileage += distance
        return f"{distance}km 운전했습니다. 총 주행거리: {self.mileage:,}km"
    
    def get_age(self) -> int:
        """차량 연식 계산"""
        return datetime.now().year - self.year

class KoreanCar(Vehicle):
    """한국 자동차 클래스"""
    
    def __init__(self, brand: str, model: str, year: int, price: int, 
                 displacement: float, fuel_type: str = "gasoline"):
        super().__init__(brand, model, year, price)
        self.displacement = displacement  # 배기량 (리터)
        self.fuel_type = fuel_type
        self.warranty_years = 5  # 한국차 기본 보증 5년
    
    def start_engine(self) -> str:
        if self.is_running:
            return "[X] 이미 엔진이 가동 중입니다"
        
        self.is_running = True
        return f"[O] {self.get_basic_info()} 엔진 시동 완료!"
    
    def stop_engine(self) -> str:
        if not self.is_running:
            return "[X] 엔진이 이미 정지되어 있습니다"
        
        self.is_running = False
        return f"{self.get_basic_info()} 엔진 정지"
    
    def get_fuel_efficiency(self) -> float:
        """한국차 연비 계산 (km/L)"""
        base_efficiency = 12.0  # 기본 12km/L
        
        # 배기량에 따른 연비 조정
        if self.displacement <= 1.0:
            return base_efficiency + 3.0
        elif self.displacement <= 1.6:
            return base_efficiency + 1.0
        elif self.displacement <= 2.0:
            return base_efficiency
        else:
            return base_efficiency - 2.0
    
    def check_warranty(self) -> str:
        """보증 기간 확인"""
        age = self.get_age()
        remaining = self.warranty_years - age
        
        if remaining > 0:
            return f"[O] 보증 기간 {remaining}년 남음"
        else:
            return f"[X] 보증 기간 {abs(remaining)}년 경과"

class ElectricCar(Vehicle):
    """전기 자동차 클래스"""
    
    def __init__(self, brand: str, model: str, year: int, price: int,
                 battery_capacity: float, range_km: int):
        super().__init__(brand, model, year, price)
        self.battery_capacity = battery_capacity  # kWh
        self.range_km = range_km  # 1회 충전 주행거리
        self.battery_level = 100  # 배터리 잔량 (%)
        self.is_charging = False
    
    def start_engine(self) -> str:
        if self.battery_level <= 0:
            return "[X] 배터리가 방전되었습니다. 충전이 필요합니다."
        
        if self.is_running:
            return "[X] 이미 전원이 켜져 있습니다"
        
        self.is_running = True
        return f"{self.get_basic_info()} 전원 켜짐! (배터리: {self.battery_level}%)"
    
    def stop_engine(self) -> str:
        if not self.is_running:
            return "[X] 이미 전원이 꺼져 있습니다"
        
        self.is_running = False
        return f"{self.get_basic_info()} 전원 종료"
    
    def get_fuel_efficiency(self) -> float:
        """전기차 효율성 (km/kWh)"""
        return self.range_km / self.battery_capacity
    
    def drive(self, distance: int) -> str:
        """전기차 운전 (배터리 소모 포함)"""
        if not self.is_running:
            return "[X] 전원을 먼저 켜세요"
        
        # 배터리 소모 계산
        battery_consumption = (distance / self.range_km) * 100
        
        if self.battery_level < battery_consumption:
            return f"[X] 배터리 부족! 현재 {self.battery_level:.1f}%, 필요 {battery_consumption:.1f}%"
        
        self.battery_level -= battery_consumption
        self.mileage += distance
        
        return f"{distance}km 운전 완료. 배터리: {self.battery_level:.1f}%, 총 주행거리: {self.mileage:,}km"
    
    def charge(self, time_hours: float) -> str:
        """배터리 충전"""
        if self.is_running:
            return "[X] 충전하려면 전원을 먼저 끄세요"
        
        # 1시간에 20% 충전으로 가정
        charge_amount = min(time_hours * 20, 100 - self.battery_level)
        self.battery_level += charge_amount
        
        return f"{time_hours}시간 충전 완료! 배터리: {self.battery_level:.1f}%"

# 다형성 시연
def test_vehicle(vehicle: Vehicle) -> None:
    """차량 테스트 함수 (다형성 활용)"""
    print(f"\n{vehicle.get_basic_info()} 테스트")
    print(f"연식: {vehicle.get_age()}년")
    print(f"연비/효율성: {vehicle.get_fuel_efficiency():.1f}")
    
    print(vehicle.start_engine())
    print(vehicle.drive(50))
    print(vehicle.stop_engine())
    
    # 전기차인 경우 추가 기능 테스트
    if isinstance(vehicle, ElectricCar):
        print(vehicle.charge(2.0))
    
    # 한국차인 경우 보증 확인
    if isinstance(vehicle, KoreanCar):
        print(vehicle.check_warranty())

# 사용 예제
vehicles: List[Vehicle] = [
    KoreanCar("현대", "소나타", 2020, 25000000, 2.0),
    KoreanCar("기아", "K5", 2022, 28000000, 1.6),
    ElectricCar("테슬라", "Model 3", 2023, 50000000, 75.0, 400)
]

# 다형성을 활용한 모든 차량 테스트
for vehicle in vehicles:
    test_vehicle(vehicle)
```

`test_vehicle()`은 받은 차가 어떤 종류인지 묻지 않고 `start_engine()`, `drive()`, `stop_engine()`을 똑같이 부릅니다. 그런데 출력은 차마다 달라요. 현대·기아 차는 "엔진 시동 완료!"인데 테슬라는 "전원 켜짐! (배터리: 100%)"이고, 테슬라는 50km를 달리자 배터리가 87.5%로 줄었습니다. `ElectricCar`가 `drive()`를 자기 방식으로 다시 정의했기 때문이죠(400km를 달리는 배터리로 50km를 갔으니 12.5%를 쓴 거예요). 같은 메시지를 보냈는데 받는 객체에 따라 다르게 처리되는 것, 들어가며에서 말한 "누가 처리할지는 실행하는 순간에 정해진다"가 바로 이 모습입니다. 이 성질을 **다형성**이라고 하고, 13장의 주인공이에요.

보증 기간과 연식은 `datetime.now()`로 올해를 기준 삼아 계산하므로 실행하는 해에 따라 결과가 달라집니다.

## 11.4 특수 메서드 (매직 메서드)

### 기본 특수 메서드

3장 들어가며에서 연산은 사람이 정한 약속이고, 필요하면 우리가 직접 새 규칙을 만들 수도 있다고 했죠? 이제 그 약속을 만들 차례입니다.

다른 언어에서는 두 객체가 같은지 비교할 때 `if a.equals(b):`처럼 메서드 이름을 불러야 하는 경우가 많습니다. 라이브러리마다 `equals`, `isSame`, `compare`처럼 이름도 제각각이죠. 파이썬에서는 클래스에 `__eq__`라는 메서드를 만들어 두면 그냥 `if a == b:`라고 쓸 수 있어요. 비밀은 파이썬이 연산자를 만나면 정해진 이름의 메서드로 바꿔 부른다는 데 있습니다. `1 + 2`는 사실 `(1).__add__(2)`이고, `"a" + "b"`는 `"a".__add__("b")`예요. 둘 다 실제로 실행해 보면 `3`과 `'ab'`가 나옵니다. 숫자와 문자열의 `+`가 다르게 동작했던 것도 각자 `__add__`를 다르게 만들어 두었기 때문이었죠.

이렇게 앞뒤로 밑줄 두 개가 붙은 메서드를 **특수 메서드**, 흔히 **매직 메서드(magic method)** 라고 부릅니다(밑줄 두 개, double underscore를 줄여 "던더(dunder) 메서드"라고도 해요). 우리가 직접 부르는 일은 드물고, 파이썬이 알맞은 순간에 대신 불러 줍니다. 자주 쓰는 것들을 무리 지어 보면 이렇습니다.

| 무리 | 메서드 | 언제 불리나 |
|---|---|---|
| 생성과 소멸 | `__new__`, `__init__`, `__del__` | 객체를 만들 때, 채울 때, 없어질 때 |
| 비교 | `__eq__` `__ne__` `__lt__` `__le__` `__gt__` `__ge__` | `==` `!=` `<` `<=` `>` `>=` |
| 산술 | `__add__` `__sub__` `__mul__` `__truediv__` `__floordiv__` `__mod__` `__pow__` `__matmul__` | `+` `-` `*` `/` `//` `%` `**` `@` |
| 뒤집힌 산술 | `__radd__`, `__rsub__`, `__rmul__` … | 왼쪽 피연산자가 처리하지 못할 때 `3 + 객체` |
| 복합 할당 | `__iadd__`, `__isub__`, `__imul__` … | `+=` `-=` `*=` |
| 단항 | `__neg__`, `__pos__`, `__abs__` | `-객체`, `+객체`, `abs(객체)` |
| 타입 변환 | `__int__`, `__float__`, `__complex__`, `__bool__`, `__index__` | `int()`, `float()`, `complex()`, `bool()`, `hex()`·`bin()`·인덱스 |
| 표현 | `__str__`, `__repr__`, `__format__`, `__hash__` | `print()`·`str()`, `repr()`, f-문자열 서식, `hash()` |
| 컨테이너 | `__len__`, `__getitem__`, `__setitem__`, `__delitem__`, `__iter__`, `__contains__` | `len()`, `객체[키]`, `del 객체[키]`, `for`, `in` |
| 호출 | `__call__` | `객체(...)`처럼 함수로 부를 때 |
| 컨텍스트 | `__enter__`, `__exit__` | `with` 문 |

아래 `KoreanMoney`는 이 중 표현, 비교, 산술, 컨테이너 무리를 직접 만들어 본 예제입니다. 금액을 그냥 정수로 다루면 원화와 달러를 실수로 더해도 아무도 말려 주지 않지만, 클래스로 만들면 그런 연산을 거절할 수 있어요.

```python
from typing import Union
from datetime import datetime

class KoreanMoney:
    """한국 화폐 클래스 (특수 메서드 활용)"""
    
    def __init__(self, amount: int, currency: str = "KRW"):
        if not isinstance(amount, int):
            raise TypeError("금액은 정수여야 합니다")
        
        self.amount = amount
        self.currency = currency
    
    def __str__(self) -> str:
        """사용자 친화적 문자열 표현"""
        return f"{self.amount:,}{self._get_currency_symbol()}"
    
    def __repr__(self) -> str:
        """개발자용 문자열 표현"""
        return f"KoreanMoney({self.amount}, '{self.currency}')"
    
    def __eq__(self, other) -> bool:
        """동등성 비교"""
        if not isinstance(other, KoreanMoney):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other) -> bool:
        """작음 비교"""
        if not isinstance(other, KoreanMoney):
            return NotImplemented
        self._check_currency_compatibility(other)
        return self.amount < other.amount
    
    def __le__(self, other) -> bool:
        """작거나 같음 비교"""
        return self == other or self < other
    
    def __gt__(self, other) -> bool:
        """큼 비교"""
        if not isinstance(other, KoreanMoney):
            return NotImplemented
        return not (self <= other)
    
    def __ge__(self, other) -> bool:
        """크거나 같음 비교"""
        return self == other or self > other
    
    def __add__(self, other) -> 'KoreanMoney':
        """덧셈 연산"""
        if isinstance(other, KoreanMoney):
            self._check_currency_compatibility(other)
            return KoreanMoney(self.amount + other.amount, self.currency)
        elif isinstance(other, int):
            return KoreanMoney(self.amount + other, self.currency)
        else:
            return NotImplemented
    
    def __radd__(self, other) -> 'KoreanMoney':
        """역순 덧셈 연산 (숫자 + KoreanMoney)"""
        return self.__add__(other)
    
    def __sub__(self, other) -> 'KoreanMoney':
        """뺄셈 연산"""
        if isinstance(other, KoreanMoney):
            self._check_currency_compatibility(other)
            return KoreanMoney(self.amount - other.amount, self.currency)
        elif isinstance(other, int):
            return KoreanMoney(self.amount - other, self.currency)
        else:
            return NotImplemented
    
    def __mul__(self, other) -> 'KoreanMoney':
        """곱셈 연산"""
        if isinstance(other, (int, float)):
            return KoreanMoney(int(self.amount * other), self.currency)
        else:
            return NotImplemented
    
    def __rmul__(self, other) -> 'KoreanMoney':
        """역순 곱셈 연산"""
        return self.__mul__(other)
    
    def __truediv__(self, other) -> 'KoreanMoney':
        """나눗셈 연산"""
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("0으로 나눌 수 없습니다")
            return KoreanMoney(int(self.amount / other), self.currency)
        else:
            return NotImplemented
    
    def __hash__(self) -> int:
        """해시값 반환 (딕셔너리 키로 사용 가능)"""
        return hash((self.amount, self.currency))
    
    def __bool__(self) -> bool:
        """불린 변환 (금액이 0이 아니면 True)"""
        return self.amount != 0
    
    def __len__(self) -> int:
        """길이 반환 (자릿수)"""
        return len(str(abs(self.amount)))
    
    def __getitem__(self, index: int) -> str:
        """인덱싱 지원 (금액 문자열의 각 자릿수)"""
        amount_str = str(abs(self.amount))
        return amount_str[index]
    
    def __contains__(self, digit: str) -> bool:
        """멤버십 테스트 (특정 숫자 포함 여부)"""
        return str(digit) in str(abs(self.amount))
    
    def _get_currency_symbol(self) -> str:
        """통화 기호 반환"""
        symbols = {
            "KRW": "원",
            "USD": "달러", 
            "JPY": "엔",
            "EUR": "유로"
        }
        return symbols.get(self.currency, self.currency)
    
    def _check_currency_compatibility(self, other: 'KoreanMoney') -> None:
        """통화 호환성 검사"""
        if self.currency != other.currency:
            raise ValueError(f"다른 통화끼리 연산할 수 없습니다: {self.currency} vs {other.currency}")

# 사용 예제
money1 = KoreanMoney(50000)
money2 = KoreanMoney(30000)
money3 = KoreanMoney(50000)

print("기본 출력:")
print(f"money1: {money1}")
print(f"money2: {money2}")
print(f"repr: {repr(money1)}")

print("\n비교 연산:")
print(f"money1 == money3: {money1 == money3}")
print(f"money1 > money2: {money1 > money2}")
print(f"money2 < money1: {money2 < money1}")

print("\n산술 연산:")
total = money1 + money2
print(f"{money1} + {money2} = {total}")

difference = money1 - money2
print(f"{money1} - {money2} = {difference}")

doubled = money1 * 2
print(f"{money1} × 2 = {doubled}")

half = money1 / 2
print(f"{money1} ÷ 2 = {half}")

print("\n기타 특수 메서드:")
print(f"money1의 자릿수: {len(money1)}")
print(f"money1[0] (첫째 자리): {money1[0]}")
print(f"'5' in money1: {'5' in money1}")
print(f"bool(money1): {bool(money1)}")
print(f"bool(KoreanMoney(0)): {bool(KoreanMoney(0))}")

# 집합과 딕셔너리에서 사용 (해시 가능)
money_set = {money1, money2, money3}
print(f"\n집합 크기: {len(money_set)}")  # money1과 money3는 같으므로 2개

money_dict = {money1: "오만원", money2: "삼만원"}
print(f"딕셔너리: {money_dict}")
```

출력에서 몇 군데를 짚어 봅시다.

- **`__str__`과 `__repr__`**: `print(money1)`이나 f-문자열은 `__str__`을 불러 사람이 읽기 좋은 `50,000원`을 보여 줍니다. `repr(money1)`은 `__repr__`을 불러 `KoreanMoney(50000, 'KRW')`처럼 개발자가 "이 객체를 어떻게 만들었는지" 알 수 있는 모양을 보여 주고요. 마지막 줄의 딕셔너리 출력을 보면 키가 `KoreanMoney(50000, 'KRW')`로 찍혔죠? 리스트나 딕셔너리 안에 든 객체는 `__repr__`으로 표시되기 때문입니다. 둘 중 하나만 만든다면 `__repr__`을 만드세요. `__str__`이 없으면 `print()`도 `__repr__`을 대신 씁니다.
- **`NotImplemented`**: `__add__`는 모르는 타입이 들어오면 에러를 내지 않고 `NotImplemented`라는 특별한 값을 돌려줍니다. "나는 이 계산을 할 줄 몰라"라는 신호예요. 그러면 파이썬은 오른쪽 피연산자에게 뒤집힌 메서드(`__radd__`)로 다시 물어보고, 그쪽도 모르면 그때 `TypeError`를 냅니다. `money1 + "문자"`는 결국 `unsupported operand type(s) for +: 'KoreanMoney' and 'str'` 에러가 되죠.
- **`__radd__`**: `1000 + money1`에서 왼쪽의 `int`는 `KoreanMoney`를 더할 줄 모르니 `NotImplemented`를 돌려주고, 파이썬이 `money1.__radd__(1000)`을 불러 줍니다. 덕분에 `sum([KoreanMoney(1), KoreanMoney(2)])`도 동작해요. `sum()`은 0부터 더하기 시작하는데, 그 첫 `0 + KoreanMoney(1)`을 `__radd__`가 받아 주거든요.
- **`__eq__`와 `__hash__`**: 집합의 크기가 2인 이유는 `money1`과 `money3`이 `==`로 같고 해시값도 같아서 하나로 취급되었기 때문입니다. 파이썬은 `__eq__`만 만들고 `__hash__`를 만들지 않은 클래스를 **해시할 수 없는** 타입으로 바꿔 버려요. 그러면 집합에 넣거나 딕셔너리 키로 쓸 때 `unhashable type` 에러가 납니다. 같다고 판단한 두 객체는 해시값도 같아야 하니, 이 예제처럼 같은 값들로 해시를 만들어 주면 됩니다.
- **`__bool__`과 컨테이너 메서드**: `bool(KoreanMoney(0))`이 `False`라서 `if money:`처럼 "돈이 있으면"을 자연스럽게 쓸 수 있습니다. `len()`, `money1[0]`, `'5' in money1`은 각각 `__len__`, `__getitem__`, `__contains__`가 처리했어요.

`+=`는 어떨까요? `KoreanMoney`에는 `__iadd__`가 없지만 `money += 500`은 잘 동작합니다. 복합 할당 메서드가 없으면 파이썬이 `money = money + 500`으로 바꿔서 `__add__`를 쓰기 때문이에요. 이때 `money`에는 새로 만든 객체가 담깁니다.

표의 단항 연산자와 타입 변환 무리는 위 예제에 없으니 작은 클래스로 따로 확인해 보죠.

```python
class Won:
    """금액 하나를 담는 작은 클래스"""

    def __init__(self, amount: int):
        self.amount = amount

    def __neg__(self) -> "Won":      # -won
        return Won(-self.amount)

    def __abs__(self) -> "Won":      # abs(won)
        return Won(abs(self.amount))

    def __int__(self) -> int:        # int(won)
        return self.amount

    def __float__(self) -> float:    # float(won)
        return float(self.amount)

    def __repr__(self) -> str:
        return f"Won({self.amount})"

refund = Won(-3000)
print(-refund, abs(refund))        # Won(3000) Won(3000)
print(int(refund), float(refund))  # -3000 -3000.0
```

`-refund`라고 쓰면 `__neg__`가, `int(refund)`라고 쓰면 `__int__`가 불립니다. 예전 자료에서 `__div__`, `__long__`, `__oct__`, `__hex__` 같은 이름을 볼 수도 있는데, 모두 파이썬 2 시절 이름이라 파이썬 3에서는 동작하지 않아요. 나눗셈은 `__truediv__`(`/`)와 `__floordiv__`(`//`)로 나뉘었고, `hex()`·`oct()`·`bin()`은 `__index__`가 정수를 돌려주면 동작합니다.

> **Q. `__init__`이 객체를 만드는 생성자 아닌가요?**
> 엄밀히 말하면 객체를 실제로 만드는 건 `__new__`이고, `__init__`은 이미 만들어진 빈 객체에 값을 채우는 초기화 담당입니다. `Student(...)`를 부르면 `__new__`가 먼저 객체를 만들고, 그 객체가 `self`가 되어 `__init__`이 실행되죠. `__new__`는 튜플이나 문자열처럼 한번 만들면 바꿀 수 없는 타입을 상속할 때 말고는 거의 직접 만들 일이 없으니, 지금은 "`__init__`은 채우는 곳"이라고만 기억하세요. 반대편 끝의 `__del__`은 객체가 메모리에서 정리될 때 불리는데, **언제 불릴지 정확히 보장되지 않아서** 파일 닫기 같은 뒷정리를 맡기기엔 불안합니다. 그 일은 바로 다음에 볼 `with` 문이 확실하게 해 줍니다.

### 컨텍스트 매니저와 이터레이터

데이터베이스 연결이나 파일처럼 "열었으면 반드시 닫아야 하는" 자원이 있습니다. 중간에 에러가 나서 닫는 코드까지 못 가면 자원이 새어 나가죠. `with` 문은 들어갈 때 할 일과 나올 때 할 일을 객체에 맡겨서, 블록 안에서 무슨 일이 생겨도 나올 때 할 일은 꼭 실행되게 해 줍니다.

- `__enter__(self)`: `with` 블록에 들어갈 때 불립니다. 여기서 돌려준 값이 `as` 뒤의 이름에 담겨요.
- `__exit__(self, exc_type, exc_val, exc_tb)`: 블록을 빠져나올 때 **항상** 불립니다. 블록이 무사히 끝났으면 세 인자가 모두 `None`이고, 예외가 났으면 그 예외의 종류·값·추적 정보가 들어옵니다. 여기서 `True`를 돌려주면 예외를 삼켜 없던 일로 하고, `False`나 `None`을 돌려주면 예외가 그대로 바깥으로 퍼져 나가요.

반복도 매직 메서드로 이뤄집니다. `for student in classroom:`이라고 쓰면 파이썬은 먼저 `iter(classroom)`, 즉 `__iter__`를 불러 **이터레이터**를 받고, 그다음 `next()`, 즉 `__next__`를 계속 불러 하나씩 꺼내다가 `StopIteration` 예외가 나오면 반복을 끝냅니다.

```python
from typing import Iterator, List, Any
import time
import sqlite3

class KoreanDatabase:
    """한국어 데이터베이스 컨텍스트 매니저"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self.transaction_started = False
    
    def __enter__(self):
        """컨텍스트 진입"""
        print(f"데이터베이스 연결: {self.db_path}")
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                major TEXT
            )
        """)
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 종료"""
        if self.connection:
            if exc_type is not None:
                print(f"[X] 오류 발생으로 롤백: {exc_val}")
                self.connection.rollback()
            else:
                print("[O] 변경사항 저장")
                self.connection.commit()
            
            self.connection.close()
            print("데이터베이스 연결 해제")
        
        # True를 반환하면 예외를 억제, False나 None이면 예외 전파
        return False

class KoreanStudentIterator:
    """한국 학생 이터레이터"""
    
    def __init__(self, students: List[dict]):
        self.students = students
        self.index = 0
    
    def __iter__(self) -> Iterator[dict]:
        """이터레이터 반환"""
        self.index = 0
        return self
    
    def __next__(self) -> dict:
        """다음 항목 반환"""
        if self.index >= len(self.students):
            raise StopIteration
        
        student = self.students[self.index]
        self.index += 1
        
        # 학생 정보 처리 시뮬레이션
        processed_student = {
            **student,
            "processed_at": time.time(),
            "next_year_age": student["age"] + 1,  # 생년이 없어 내년 나이로 표시
            "status": "active"
        }
        
        return processed_student

class KoreanClassroom:
    """한국 학급 클래스 (이터레이터 지원)"""
    
    def __init__(self, class_name: str):
        self.class_name = class_name
        self.students: List[dict] = []
    
    def add_student(self, name: str, age: int, major: str) -> None:
        """학생 추가"""
        student = {
            "id": len(self.students) + 1,
            "name": name,
            "age": age,
            "major": major
        }
        self.students.append(student)
        print(f"[O] {name} 학생이 {self.class_name}에 추가되었습니다")
    
    def __iter__(self) -> Iterator[dict]:
        """이터레이터 반환"""
        return KoreanStudentIterator(self.students)
    
    def __len__(self) -> int:
        """학생 수 반환"""
        return len(self.students)
    
    def __getitem__(self, index: int) -> dict:
        """인덱싱 지원"""
        return self.students[index]
    
    def __contains__(self, student_name: str) -> bool:
        """학생 존재 여부 확인"""
        return any(student["name"] == student_name for student in self.students)

# 사용 예제
print("컨텍스트 매니저 테스트:")
with KoreanDatabase(":memory:") as db:
    cursor = db.cursor()
    cursor.execute("INSERT INTO students (name, age, major) VALUES (?, ?, ?)",
                   ("김철수", 20, "컴퓨터과학과"))
    cursor.execute("INSERT INTO students (name, age, major) VALUES (?, ?, ?)",
                   ("이영희", 21, "경영학과"))
    
    # 데이터 조회
    cursor.execute("SELECT * FROM students")
    results = cursor.fetchall()
    print(f"저장된 데이터: {results}")

print("\n이터레이터 테스트:")
classroom = KoreanClassroom("컴퓨터과학과 3학년")

# 학생 추가
classroom.add_student("박민수", 22, "컴퓨터과학과")
classroom.add_student("최지영", 21, "컴퓨터과학과")
classroom.add_student("정수진", 23, "컴퓨터과학과")

print(f"\n학급 정보: {classroom.class_name} ({len(classroom)}명)")

# 이터레이터를 통한 순회
print("\n학생 목록 (이터레이터 사용):")
for student in classroom:
    print(f"- {student['name']} ({student['age']}세, 내년이면 {student['next_year_age']}세)")

# 인덱싱 사용
print(f"\n첫 번째 학생: {classroom[0]['name']}")

# 멤버십 테스트
print(f"박민수가 있나요? {'박민수' in classroom}")
print(f"김철수가 있나요? {'김철수' in classroom}")
```

컨텍스트 매니저 쪽 출력은 "데이터베이스 연결 → 저장된 데이터 → [O] 변경사항 저장 → 데이터베이스 연결 해제" 순서입니다. 우리는 `with` 블록 안에 데이터를 넣고 조회하는 코드만 썼는데, 연결과 저장, 해제는 `__enter__`와 `__exit__`가 알아서 해 줬죠. 블록 안에서 예외가 났다면 `__exit__`가 저장 대신 롤백을 하고 연결을 닫은 뒤, `False`를 돌려줘서 예외를 바깥에 알렸을 겁니다. 12장에서 쓰는 `with open(...) as f:`도 파일 객체가 이 두 메서드를 갖고 있기 때문에 동작하는 거예요.

이터레이터 쪽에서는 `KoreanClassroom`이 `__iter__`를 부를 때마다 **새** `KoreanStudentIterator`를 만들어 돌려준다는 점이 중요합니다. 이터레이터는 "지금 몇 번째까지 꺼냈는지"를 기억하는 책갈피라서, 학급 객체와 책갈피를 따로 두면 같은 학급을 몇 번이고 처음부터 다시 돌 수 있어요. 학생마다 `korean_age`와 `status`가 붙어 나오는 것도 `__next__`가 꺼내 주는 순간에 정보를 덧붙였기 때문입니다. 이터레이터와 그것을 훨씬 짧게 쓰는 제너레이터는 15장에서 자세히 다룹니다.

## 11.5 실습 문제

### 기본 문제 (1-5번)

각 문제는 빈칸이 있는 클래스가 먼저 나오고, 그 아래 `# 답:` 다음에 풀이가 이어집니다. 답을 보기 전에 직접 채워 보세요. 같은 이름의 클래스를 다시 정의하면 나중 것이 앞의 것을 덮어쓰므로, 파일 하나에 통째로 붙여 실행해도 답 쪽 클래스로 동작합니다.

```python
# 1번: 기본 클래스 정의
class Book:
    def __init__(self, title: str, author: str, pages: int):
        # 문제: 책 클래스의 초기화 메서드를 완성하세요
        pass

# 답:
class Book:
    def __init__(self, title: str, author: str, pages: int):
        self.title = title
        self.author = author
        self.pages = pages
        self.is_borrowed = False
    
    def borrow(self):
        if not self.is_borrowed:
            self.is_borrowed = True
            return f"'{self.title}' 대출되었습니다"
        return "이미 대출된 책입니다"
    
    def return_book(self):
        if self.is_borrowed:
            self.is_borrowed = False
            return f"'{self.title}' 반납되었습니다"
        return "대출되지 않은 책입니다"

book = Book("파이썬 완전정복", "김개발", 500)
print(book.borrow())

# 2번: 프로퍼티 활용
class Temperature:
    def __init__(self, celsius: float = 0):
        self._celsius = celsius
    
    # 문제: 화씨온도 프로퍼티를 추가하세요
    pass

# 답:
class Temperature:
    def __init__(self, celsius: float = 0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("절대영도보다 낮을 수 없습니다")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5/9

temp = Temperature(25)
print(f"{temp.celsius}°C = {temp.fahrenheit}°F")

# 3번: 상속 구현
class Animal:
    def __init__(self, name: str):
        self.name = name
    
    def speak(self):
        pass

class Dog(Animal):
    # 문제: Dog 클래스에서 speak 메서드를 오버라이드하세요
    pass

# 답:
class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name)
        self.breed = breed
    
    def speak(self):
        return f"{self.name}: 멍멍!"

class Cat(Animal):
    def speak(self):
        return f"{self.name}: 야옹~"

dog = Dog("바둑이", "진돗개")
cat = Cat("나비")
print(dog.speak())
print(cat.speak())

# 4번: 클래스 메서드 활용
class Student:
    student_count = 0
    
    def __init__(self, name: str, grade: int):
        self.name = name
        self.grade = grade
        Student.student_count += 1
    
    # 문제: 총 학생 수를 반환하는 클래스 메서드를 만드세요
    pass

# 답:
class Student:
    student_count = 0
    
    def __init__(self, name: str, grade: int):
        self.name = name
        self.grade = grade
        Student.student_count += 1
    
    @classmethod
    def get_student_count(cls):
        return cls.student_count
    
    @classmethod
    def create_elementary_student(cls, name: str):
        return cls(name, 1)

s1 = Student("김철수", 3)
s2 = Student.create_elementary_student("이영희")
print(f"총 학생 수: {Student.get_student_count()}")

# 5번: 특수 메서드 구현
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    # 문제: 두 점 사이의 거리를 계산하는 특수 메서드들을 추가하세요
    pass

# 답:
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def distance_to(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5

p1 = Point(1, 2)
p2 = Point(3, 4)
print(f"p1: {p1}")
print(f"p1 + p2: {p1 + p2}")
print(f"거리: {p1.distance_to(p2):.2f}")
```

## 11.6 다음 장 미리보기

다음 Chapter 12에서는 **파일과 예외 처리**를 학습합니다:

### 주요 내용 미리보기
- **파일 입출력**: 텍스트 파일과 바이너리 파일 처리
- **pathlib**: 현대적 파일 경로 관리
- **예외 처리**: try-except-finally와 사용자 정의 예외
- **컨텍스트 매니저**: with문과 리소스 관리
- **파일 형식**: CSV, JSON, XML 데이터 처리
- **실무 프로젝트**: 한국 로그 분석 시스템

### 연결 포인트
- 클래스와 객체 → 예외 클래스와 파일 객체
- 컨텍스트 매니저 → 파일 리소스 안전 관리
- 특수 메서드 → `__enter__`, `__exit__` 구현

객체 지향 프로그래밍의 기초를 완전히 익혔다면, 이제 실무에서 자주 마주치는 파일 처리와 에러 상황을 우아하게 다루는 방법을 배울 준비가 되었습니다!

---

> **학습 팁**: 객체 지향 프로그래밍은 코드의 재사용성과 유지보수성을 크게 향상시킵니다. 상속보다는 컴포지션을, 복잡한 상속보다는 간단한 클래스 설계를 선호하세요.

**다음 장에서 만나요!** 