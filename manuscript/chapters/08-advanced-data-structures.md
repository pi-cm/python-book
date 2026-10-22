# Chapter 8: 고급 데이터 구조

> **학습 목표**  
> - dataclass를 활용한 구조화된 클래스 정의
> - NamedTuple과 타입 힌팅의 실무 활용
> - Enum을 통한 상수와 열거형 관리
> - typing 모듈의 고급 타입 힌팅 기법
> - collections 모듈의 특수 자료구조 활용
> - Pydantic을 활용한 현대적 데이터 검증과 API 통합
> - 한국 부동산 데이터 분석 시스템 구현

---

## 들어가며: 데이터에 모양을 주자

학생 한 명의 정보를 저장한다고 해 봅시다. 지금까지 배운 것으로는 두 가지 방법이 떠오르죠?

- 튜플 `("김철수", 20, [85, 92])`: 짧지만, 0번이 이름이고 1번이 나이라는 걸 **순서로 외워야** 합니다.
- 딕셔너리 `{"name": "김철수", "age": 20}`: 이름표가 붙어 읽기 좋지만, 누가 `student["nmae"] = "이영희"`처럼 오타를 내도 파이썬은 아무 말 없이 새 키를 하나 더 만들어 버립니다.

관공서에서 쓰는 **서류 양식**을 떠올려 보세요. 칸마다 "성명", "생년월일" 같은 제목이 인쇄되어 있어서 무엇을 어디에 써야 하는지 헷갈리지 않고, 없는 칸에는 쓸 수도 없습니다. 이 장에서 배우는 도구들은 데이터에 이런 양식을 만들어 주는 것들이에요.

- **dataclass**: 칸 이름과 종류를 적어 두면 양식을 찍어 주는 도장
- **NamedTuple**: 한 번 쓰면 고칠 수 없게 코팅한 카드
- **Enum**: "주문대기, 배송중, 배송완료"처럼 고를 수 있는 답이 정해진 체크박스
- **collections 모듈**: 줄 서기, 개수 세기처럼 특정한 일에 맞춘 전문 공구
- **Pydantic**: 양식을 받을 때 빈칸과 형식을 꼼꼼히 검사하는 접수 창구

코드에 `class`와 `@` 기호가 자주 나옵니다. 클래스는 11장, `@`로 시작하는 데코레이터는 10장에서 자세히 배우니, 이 장에서는 "데이터의 틀을 만드는 문법" 정도로만 받아들이고 읽어 나가도 충분합니다.

## 8.1 dataclass 기본 개념

### dataclass란 무엇인가?

dataclass는 Python 3.7에서 도입된 데코레이터로, 데이터 저장 클래스를 간단하게 정의할 수 있게 해줍니다.

아래 예제에서 위쪽 `StudentTraditional`은 클래스를 손으로 직접 만든 모습입니다. 이름, 나이, 성적을 저장하려고 `__init__`(만들 때 값 넣기), `__repr__`(보기 좋게 출력하기), `__eq__`(같은지 비교하기)를 일일이 써야 하고, `name`, `age`, `grades`라는 이름도 몇 번씩 반복해서 적어야 하죠. 아래쪽 `Student`는 같은 일을 dataclass로 한 것입니다. 칸 이름과 타입만 나열하면 나머지 세 가지를 파이썬이 대신 만들어 줍니다.

```python
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

# 전통적인 클래스 정의 방식
class StudentTraditional:
    def __init__(self, name: str, age: int, grades: List[int]):
        self.name = name
        self.age = age
        self.grades = grades
    
    def __repr__(self):
        return f"Student(name='{self.name}', age={self.age}, grades={self.grades})"
    
    def __eq__(self, other):
        if not isinstance(other, StudentTraditional):
            return NotImplemented
        return (self.name, self.age, self.grades) == (other.name, other.age, other.grades)

# dataclass를 사용한 간단한 정의
@dataclass
class Student:
    name: str
    age: int
    grades: List[int]
    gpa: Optional[float] = None
    
    def calculate_gpa(self) -> float:
        """GPA 계산"""
        if not self.grades:
            return 0.0
        return sum(self.grades) / len(self.grades) / 25  # 4.0 스케일로 변환

# 사용 예제
student1 = Student("김철수", 20, [85, 92, 78, 88])
student2 = Student("이영희", 21, [95, 87, 91, 89])

print(student1)
print(f"김철수 GPA: {student1.calculate_gpa():.2f}")
print(f"같은 학생인가? {student1 == student2}")
```

`print(student1)`의 결과가 `Student(name='김철수', age=20, grades=[85, 92, 78, 88], gpa=None)`처럼 칸 이름과 값이 모두 보이게 나옵니다. 우리가 쓰지 않은 `__repr__`가 자동으로 생겼다는 증거예요. `==`도 마찬가지로, 두 학생의 칸 값을 순서대로 비교해서 하나라도 다르면 `False`를 돌려줍니다.

`gpa: Optional[float] = None`처럼 기본값이 있는 칸은 기본값이 없는 칸보다 **뒤에** 와야 합니다. 순서를 바꿔 기본값 있는 칸을 앞에 두면 클래스를 만드는 순간 `TypeError`가 납니다. 함수를 정의할 때 기본값 있는 매개변수를 뒤에 두는 것과 같은 규칙이에요(9장에서 다시 만납니다).

> **Q. 타입을 `int`라고 적었는데 문자열을 넣으면 막아 주나요?**
> 아니요, 막아 주지 않습니다. `Student("김철수", "스무 살", [])`도 아무 오류 없이 만들어져요. dataclass의 타입 표시는 사람과 도구(편집기, 타입 검사기)를 위한 **안내문**일 뿐, 실행 중에 검사하지는 않습니다. 들어오는 값을 실제로 검사하고 싶다면 8.5절의 Pydantic을 씁니다.

### dataclass 고급 옵션

`@dataclass` 뒤 괄호에 옵션을 넣으면 양식의 성격을 바꿀 수 있습니다. 아래 예제에서 눈여겨볼 것은 네 가지예요.

- `frozen=True`: 한 번 만든 뒤에는 값을 바꿀 수 없습니다. 주소처럼 중간에 바뀌면 곤란한 데이터에 씁니다. `address.city = "부산"`처럼 고치려 하면 `FrozenInstanceError`가 납니다.
- `order=True`: `<`, `>`로 비교할 수 있게 되어 `sorted()`로 정렬할 수 있습니다. 칸을 **위에서부터 순서대로** 비교하니, 여기서는 첫 칸인 `city`가 정렬 기준이 됩니다.
- `__post_init__`: 자동으로 만든 `__init__`이 값을 다 넣은 **직후**에 불리는 메서드입니다. 우편번호가 5자리인지 같은 검사를 여기에 둡니다.
- `field(default_factory=list)`: 칸의 기본값을 빈 리스트로 두고 싶을 때 씁니다. `employees: List[str] = []`라고 쓰면 dataclass가 `ValueError`를 내며 거절하는데, 모든 회사가 **빈 리스트 하나를 같이 쓰게** 되는 사고를 막으려는 것입니다. `default_factory`에 `list`를 주면 회사를 만들 때마다 새 빈 리스트를 하나씩 만들어 줍니다.

`field(repr=False)`는 출력할 때 그 칸을 감추라는 뜻이고, `asdict()`는 dataclass를 딕셔너리로 바꿔 줍니다. 안에 든 `KoreanAddress`까지 통째로 딕셔너리가 되기 때문에 바로 `json.dumps()`에 넘길 수 있어요.

```python
from dataclasses import dataclass, field, asdict, astuple
from typing import Dict, Any
import json

@dataclass(frozen=True, order=True)
class KoreanAddress:
    """한국 주소 데이터 클래스 (불변, 정렬 가능)"""
    city: str
    district: str
    dong: str
    postal_code: str
    
    def __post_init__(self):
        """초기화 후 검증"""
        if len(self.postal_code) != 5:
            raise ValueError("우편번호는 5자리여야 합니다")

@dataclass
class Company:
    """회사 정보 클래스"""
    name: str
    address: KoreanAddress
    employees: List[str] = field(default_factory=list)
    founded_year: int = 2000
    metadata: Dict[str, Any] = field(default_factory=dict, repr=False)
    
    def add_employee(self, employee_name: str):
        """직원 추가"""
        self.employees.append(employee_name)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)
    
    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

# 사용 예제
address = KoreanAddress("서울", "강남구", "역삼동", "06234")
company = Company(
    name="파이썬 테크놀로지",
    address=address,
    employees=["김철수", "이영희"],
    founded_year=2020
)

company.add_employee("박민수")
print("회사 정보:")
print(company.to_json())

# 주소 정렬 테스트
addresses = [
    KoreanAddress("부산", "해운대구", "우동", "48094"),
    KoreanAddress("서울", "강남구", "역삼동", "06234"),
    KoreanAddress("대구", "중구", "동성로", "41953")
]

sorted_addresses = sorted(addresses)
print(f"\n정렬된 주소: {[addr.city for addr in sorted_addresses]}")
```

출력된 JSON을 보면 `metadata`는 `repr=False`인데도 들어 있습니다. `repr=False`는 `print()`로 보여 줄 때만 숨길 뿐, `asdict()`로 바꾸는 데이터에서는 빠지지 않거든요. 정렬 결과는 `['대구', '부산', '서울']`로 도시 이름의 가나다순입니다. `order=True`가 첫 칸인 `city`부터 비교했기 때문이에요.

## 8.2 NamedTuple과 타입 힌팅

### typing.NamedTuple 활용

6.5절에서 `collections.namedtuple`로 "이름표 붙은 튜플"을 만들어 봤죠. `typing.NamedTuple`은 같은 것을 dataclass처럼 클래스 모양으로 쓰는 방법입니다. 칸마다 타입을 적을 수 있고, `format_balance()` 같은 메서드도 넣을 수 있어요.

dataclass와의 가장 큰 차이는 **튜플이라는 점**입니다. 튜플이니 한 번 만들면 값을 바꿀 수 없어요. 은행 거래 내역처럼 "이미 일어난 일"을 기록하는 데 잘 맞습니다. 이미 찍힌 영수증을 고쳐 쓰면 안 되니까요. 값을 바꾸고 싶으면 `account._replace(balance=0)`처럼 바뀐 값을 가진 **새 튜플**을 만들어야 합니다. 원래 튜플은 그대로 남아요.

```python
from typing import NamedTuple, Optional, Union
from datetime import date, datetime
from enum import Enum

class TransactionType(Enum):
    """거래 유형"""
    DEPOSIT = "입금"
    WITHDRAWAL = "출금"
    TRANSFER = "이체"

class BankAccount(NamedTuple):
    """은행 계좌 정보"""
    account_number: str
    holder_name: str
    balance: int
    bank_name: str
    created_date: date
    
    def format_balance(self) -> str:
        """잔액 포맷팅"""
        return f"{self.balance:,}원"
    
    def is_active(self) -> bool:
        """계좌 활성 상태 확인"""
        return self.balance >= 0

class Transaction(NamedTuple):
    """거래 내역"""
    transaction_id: str
    account_number: str
    transaction_type: TransactionType
    amount: int
    description: str
    timestamp: datetime
    balance_after: int
    
    def format_transaction(self) -> str:
        """거래 내역 포맷팅"""
        type_symbol = {
            TransactionType.DEPOSIT: "+",
            TransactionType.WITHDRAWAL: "-",
            TransactionType.TRANSFER: "→"
        }
        
        symbol = type_symbol[self.transaction_type]
        return (f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                f"{symbol}{self.amount:,}원 | "
                f"{self.description} | "
                f"잔액: {self.balance_after:,}원")

# 사용 예제
account = BankAccount(
    account_number="110-123-456789",
    holder_name="김철수",
    balance=1500000,
    bank_name="국민은행",
    created_date=date(2023, 1, 15)
)

transaction = Transaction(
    transaction_id="TXN20231201001",
    account_number=account.account_number,
    transaction_type=TransactionType.WITHDRAWAL,
    amount=50000,
    description="ATM 출금",
    timestamp=datetime(2023, 12, 1, 14, 30),
    balance_after=account.balance - 50000
)

print(f"계좌: {account.holder_name} ({account.format_balance()})")
print(f"거래: {transaction.format_transaction()}")
```

거래 내역이 `2023-12-01 14:30 | -50,000원 | ATM 출금 | 잔액: 1,450,000원`으로 나옵니다. 출금이라 금액 앞에 `-`가 붙었죠? `format_transaction()` 안의 `type_symbol` 딕셔너리가 거래 유형(8.3절에서 볼 Enum)을 기호로 바꿔 준 결과입니다. 이렇게 NamedTuple 안에 다른 데이터 구조를 칸으로 넣어 조립할 수 있어요.

### 고급 타입 힌팅

타입 힌트는 "이 칸에는 이런 값이 들어와요"라고 적어 두는 메모입니다. 앞에서 본 것처럼 파이썬은 실행 중에 이 메모를 검사하지 않아요. 대신 편집기의 자동 완성과 경고, 그리고 mypy 같은 타입 검사기가 이 메모를 읽고 실행 전에 실수를 찾아 줍니다. 메모를 더 정확하게 쓰는 도구 두 가지가 이 예제에 나옵니다.

**Protocol**은 "이런 메서드를 가진 것이면 누구든 좋다"는 약속입니다. 흔히 "오리처럼 걷고 오리처럼 꽥꽥거리면 오리로 친다"고 하죠. `Rectangle`과 `Circle`은 `Drawable`을 물려받지 않았는데도 `draw()`와 `get_area()`를 갖고 있으니 `Drawable` 자리에 들어갈 수 있습니다.

**TypeVar와 Generic**은 상자에 붙이는 내용물 라벨입니다. `Container[T]`의 `T`는 "아직 정하지 않은 어떤 타입"이고, `Container[Drawable]`이라고 쓰는 순간 "도형만 담는 상자"가 됩니다. 그러면 타입 검사기가 `add()`에 도형이 아닌 것을 넣는 실수를 잡아 줄 수 있어요.

```python
from typing import (
    List, Dict, Set, Tuple, Optional, Union, Any, Callable,
    TypeVar, Generic, Protocol, Literal, Final
)
from dataclasses import dataclass
from abc import abstractmethod

# 타입 변수 정의
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Protocol을 사용한 구조적 타이핑
class Drawable(Protocol):
    """그리기 가능한 객체 프로토콜"""
    
    def draw(self) -> str:
        ...
    
    def get_area(self) -> float:
        ...

@dataclass
class Rectangle:
    """직사각형 클래스"""
    width: float
    height: float
    
    def draw(self) -> str:
        return f"사각형 ({self.width}x{self.height})"
    
    def get_area(self) -> float:
        return self.width * self.height

@dataclass
class Circle:
    """원 클래스"""
    radius: float
    
    def draw(self) -> str:
        return f"원 (반지름: {self.radius})"
    
    def get_area(self) -> float:
        return 3.14159 * self.radius ** 2

# Generic 클래스
@dataclass
class Container(Generic[T]):
    """제네릭 컨테이너"""
    items: List[T]
    
    def add(self, item: T) -> None:
        self.items.append(item)
    
    def get_all(self) -> List[T]:
        return self.items.copy()
    
    def find_by_predicate(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """조건에 맞는 첫 번째 아이템 찾기"""
        for item in self.items:
            if predicate(item):
                return item
        return None

# 조건 검사 함수 (predicate): 도형을 받아 True/False를 돌려줌
def is_large_shape(shape: Drawable) -> bool:
    """큰 도형인지 확인"""
    return shape.get_area() > 100

# 사용 예제
def render_shapes(shapes: List[Drawable]) -> List[str]:
    """도형들을 렌더링"""
    results = []
    for shape in shapes:
        area_info = f"(면적: {shape.get_area():.2f})"
        size_info = "큰 도형" if is_large_shape(shape) else "작은 도형"
        results.append(f"{shape.draw()} {area_info} - {size_info}")
    return results

# 컨테이너 사용
shape_container = Container[Drawable]([
    Rectangle(10, 5),
    Circle(8),
    Rectangle(3, 4)
])

large_shape = shape_container.find_by_predicate(is_large_shape)
if large_shape:
    print(f"발견된 큰 도형: {large_shape.draw()}")

# 도형 렌더링
all_shapes = shape_container.get_all()
rendered = render_shapes(all_shapes)
for result in rendered:
    print(result)
```

`find_by_predicate()`에 함수 `is_large_shape`를 그대로 넘긴 부분을 보세요. 함수를 값처럼 넘기는 이 방법은 10장의 주인공입니다. 결과는 면적이 100을 넘는 첫 도형인 `원 (반지름: 8)`(면적 201.06)이고, 나머지 둘은 "작은 도형"으로 분류됩니다.

## 8.3 Enum과 상수 관리

### 기본 Enum 활용

주문 상태를 문자열로 관리한다고 해 봅시다. 어떤 곳에는 `"배송중"`, 다른 곳에는 `"배송 중"`이라고 쓰면 둘은 다른 값이라 비교가 어긋나고, 파이썬은 이 오타를 알려 주지 않습니다. 고를 수 있는 답이 정해져 있다면 그 답들에 **이름을 붙여 한곳에 모아 두는 것**이 안전해요. 그게 **Enum(열거형)** 입니다. `KoreanGrade.A_PLUS`처럼 쓰면 오타가 났을 때 바로 `AttributeError`가 나니 실수를 일찍 잡을 수 있습니다.

Enum 멤버는 이름(`.name`, 예: `'A_PLUS'`)과 값(`.value`, 예: `'A+'`)을 함께 갖습니다. 예제에는 세 종류가 나와요.

- `Enum`: 기본형입니다. 멤버끼리 같은지(`==`)는 물을 수 있지만 크기 비교(`<`)는 `TypeError`가 납니다. 학점 등급의 "A+"와 "B"는 글자일 뿐이니까요.
- `IntEnum`: 정수처럼 동작합니다. 우선순위처럼 **크기 비교가 의미 있는** 상수에 씁니다. 그래서 `task_priority >= Priority.HIGH`가 됩니다.
- `Flag`: 여러 개를 동시에 켤 수 있는 체크박스입니다. `auto()`가 값을 1, 2, 4로 매겨서, 3장에서 배운 비트 연산 `|`로 "읽기 + 쓰기"를 한 값에 담고 `&`로 켜져 있는지 확인합니다.

```python
from enum import Enum, IntEnum, Flag, auto
from typing import Dict, Any

class KoreanGrade(Enum):
    """한국 학점 시스템"""
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C_PLUS = "C+"
    C = "C"
    D_PLUS = "D+"
    D = "D"
    F = "F"
    
    @property
    def gpa_value(self) -> float:
        """GPA 값 반환"""
        gpa_mapping = {
            self.A_PLUS: 4.5, self.A: 4.0,
            self.B_PLUS: 3.5, self.B: 3.0,
            self.C_PLUS: 2.5, self.C: 2.0,
            self.D_PLUS: 1.5, self.D: 1.0,
            self.F: 0.0
        }
        return gpa_mapping[self]
    
    @property
    def korean_name(self) -> str:
        """한글 등급명"""
        korean_mapping = {
            self.A_PLUS: "매우우수", self.A: "우수",
            self.B_PLUS: "양호", self.B: "보통",
            self.C_PLUS: "미흡", self.C: "부족",
            self.D_PLUS: "매우부족", self.D: "불량",
            self.F: "낙제"
        }
        return korean_mapping[self]

class Priority(IntEnum):
    """우선순위 (정수 기반)"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    
    def __str__(self):
        korean_names = {
            self.LOW: "낮음",
            self.MEDIUM: "보통", 
            self.HIGH: "높음",
            self.CRITICAL: "긴급"
        }
        return korean_names[self]

class FilePermission(Flag):
    """파일 권한 (비트 플래그)"""
    READ = auto()
    WRITE = auto() 
    EXECUTE = auto()
    
    def to_korean(self) -> str:
        """한글 권한 설명"""
        permissions = []
        if self & FilePermission.READ:
            permissions.append("읽기")
        if self & FilePermission.WRITE:
            permissions.append("쓰기")
        if self & FilePermission.EXECUTE:
            permissions.append("실행")
        return ", ".join(permissions) if permissions else "권한 없음"

# 사용 예제
def demonstrate_enums():
    """Enum 시연"""
    print("한국 학점 시스템:")
    grades = [KoreanGrade.A_PLUS, KoreanGrade.B, KoreanGrade.C_PLUS, KoreanGrade.F]
    
    for grade in grades:
        print(f"{grade.value}: {grade.korean_name} (GPA: {grade.gpa_value})")
    
    print(f"\n평균 GPA: {sum(g.gpa_value for g in grades) / len(grades):.2f}")
    
    print("\n우선순위 비교:")
    task_priority = Priority.HIGH
    if task_priority >= Priority.HIGH:
        print(f"{task_priority} 우선순위 작업은 즉시 처리해야 합니다.")
    
    print("\n파일 권한:")
    file_perm = FilePermission.READ | FilePermission.WRITE
    print(f"현재 권한: {file_perm.to_korean()}")
    
    # 실행 권한 추가
    file_perm |= FilePermission.EXECUTE
    print(f"실행 권한 추가 후: {file_perm.to_korean()}")

demonstrate_enums()
```

출력에서 `Priority.HIGH`가 `HIGH`나 `3`이 아니라 `높음`으로 찍힌 것은 `Priority` 안에 `__str__`을 직접 정의했기 때문입니다. 권한은 처음에 `읽기, 쓰기`였다가 `|=`로 실행 권한을 더하자 `읽기, 쓰기, 실행`이 되었죠. 체크박스에 하나를 더 체크한 셈이에요.

### Enum을 활용한 상태 기계

택배 배송 조회를 떠올려 보세요. "주문확인 → 상품준비 → 배송중 → 배송완료"로 차례차례 넘어가고, 이미 배송 중인 물건이 갑자기 "주문대기"로 돌아가는 일은 없죠. 이렇게 **정해진 상태들 사이를 정해진 길로만 오가는 구조**를 상태 기계(state machine)라고 합니다.

아래 예제는 Enum으로 상태를 정하고, `can_transition_to()` 안의 딕셔너리에 "이 상태에서 갈 수 있는 다음 상태들"을 집합으로 적어 둡니다. 길이 표에 없으면 상태를 바꾸지 않아요. 규칙이 한곳에 모여 있으니, 나중에 "배송중에도 취소 가능"으로 정책이 바뀌어도 표 한 줄만 고치면 됩니다.

```python
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set
from datetime import datetime

class OrderStatus(Enum):
    """주문 상태"""
    PENDING = "주문대기"
    CONFIRMED = "주문확인" 
    PREPARING = "준비중"
    SHIPPING = "배송중"
    DELIVERED = "배송완료"
    CANCELLED = "주문취소"
    RETURNED = "반품"
    
    def can_transition_to(self, new_status: 'OrderStatus') -> bool:
        """상태 전환 가능 여부 확인"""
        valid_transitions = {
            self.PENDING: {self.CONFIRMED, self.CANCELLED},
            self.CONFIRMED: {self.PREPARING, self.CANCELLED},
            self.PREPARING: {self.SHIPPING, self.CANCELLED},
            self.SHIPPING: {self.DELIVERED, self.RETURNED},
            self.DELIVERED: {self.RETURNED},
            self.CANCELLED: set(),  # 취소된 주문은 다른 상태로 변경 불가
            self.RETURNED: set()    # 반품된 주문은 다른 상태로 변경 불가
        }
        
        return new_status in valid_transitions.get(self, set())

@dataclass
class Order:
    """주문 클래스"""
    order_id: str
    customer_name: str
    product_name: str
    quantity: int
    price: int
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = None
    status_history: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.status_history is None:
            self.status_history = []
            self.status_history.append({
                "status": self.status,
                "timestamp": self.created_at,
                "note": "주문 생성"
            })
    
    def change_status(self, new_status: OrderStatus, note: str = "") -> bool:
        """주문 상태 변경"""
        if not self.status.can_transition_to(new_status):
            print(f"[X] {self.status.value}에서 {new_status.value}로 변경할 수 없습니다.")
            return False
        
        old_status = self.status
        self.status = new_status
        self.status_history.append({
            "status": new_status,
            "timestamp": datetime.now(),
            "note": note or f"{old_status.value} → {new_status.value}"
        })
        
        print(f"[O] 주문 {self.order_id}: {old_status.value} → {new_status.value}")
        return True
    
    def get_total_price(self) -> int:
        """총 가격 계산"""
        return self.price * self.quantity
    
    def print_status_history(self):
        """상태 변경 이력 출력"""
        print(f"\n주문 {self.order_id} 상태 이력:")
        for entry in self.status_history:
            timestamp = entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            print(f"  {timestamp} | {entry['status'].value} | {entry['note']}")

# 주문 처리 시뮬레이션
def simulate_order_processing():
    """주문 처리 시뮬레이션"""
    order = Order(
        order_id="ORD-2023-1201-001",
        customer_name="김철수",
        product_name="파이썬 프로그래밍 책",
        quantity=2,
        price=25000
    )
    
    print(f"새 주문 생성: {order.customer_name} - {order.product_name}")
    print(f"총 금액: {order.get_total_price():,}원")
    
    # 정상적인 주문 처리 과정
    order.change_status(OrderStatus.CONFIRMED, "결제 완료")
    order.change_status(OrderStatus.PREPARING, "상품 포장 시작")
    order.change_status(OrderStatus.SHIPPING, "택배 발송")
    
    # 잘못된 상태 변경 시도
    order.change_status(OrderStatus.PENDING, "되돌리기 시도")  # 실패해야 함
    
    # 정상 완료
    order.change_status(OrderStatus.DELIVERED, "고객 수령 확인")
    
    order.print_status_history()

simulate_order_processing()
```

결과에서 `[X] 배송중에서 주문대기로 변경할 수 없습니다.` 한 줄만 실패하고 나머지는 모두 `[O]`입니다. 실패한 변경은 이력에도 남지 않아서, 마지막에 출력되는 상태 이력은 "주문대기 → 주문확인 → 준비중 → 배송중 → 배송완료"의 다섯 줄이에요.

`Order`의 `created_at`과 `status_history`는 기본값을 `None`으로 두고 `__post_init__`에서 실제 값을 채웁니다. 앞에서 본 `field(default_factory=...)`와 같은 목적의 다른 방법이에요. 기본값 자리에 빈 리스트를 쓰면 dataclass가 거절하고, `datetime.now()`를 바로 쓰면 클래스를 정의할 때 딱 한 번 계산되어 모든 주문이 같은 시각을 갖게 됩니다. 그래서 주문을 만들 때마다 새로 계산하도록 미뤄 두는 것입니다.

## 8.4 collections 모듈의 특수 자료구조

리스트, 딕셔너리만으로도 웬만한 일은 할 수 있습니다. 하지만 "줄 세우기", "개수 세기"처럼 자주 하는 일에는 그 일에 맞춘 전문 공구가 더 편하고 빠르죠. 표준 라이브러리의 `collections` 모듈이 그런 공구 상자입니다. 따로 설치하지 않고 `import`만 하면 됩니다.

### deque (양방향 큐)

은행 번호표 줄을 생각해 보세요. 새 손님은 뒤에 서고, 창구는 맨 앞 손님부터 부릅니다. 리스트로 이 줄을 만들면 `append()`로 뒤에 넣고 `pop(0)`으로 앞에서 빼게 되는데, 리스트는 맨 앞을 빼면 **나머지 모든 원소를 한 칸씩 앞으로 당겨야** 합니다. 줄이 길수록 느려지죠. 파이썬 공식 문서도 리스트의 `pop(0)`과 `insert(0, v)`는 길이에 비례하는 비용(O(n))이 든다고 적고 있어요.

**deque**(덱, double-ended queue)는 양쪽 끝 모두에서 넣고 빼는 일이 길이와 상관없이 빠릅니다(O(1)). 앞쪽 전용 메서드는 이름에 `left`가 붙어요. `appendleft()`로 맨 앞에 끼워 넣고, `popleft()`로 맨 앞을 꺼냅니다.

`maxlen`을 주면 크기가 정해진 줄이 됩니다. 꽉 찬 상태에서 한쪽에 새로 넣으면 **반대쪽 끝이 저절로 밀려나요**. "최근 본 상품 10개"처럼 최근 것만 남기고 싶을 때 딱 맞습니다. 아래 예제의 `completed`가 완료된 작업을 최대 100개까지만 보관하는 방법이 이것입니다.

```python
from collections import deque, defaultdict, Counter, ChainMap
from typing import Any, Optional
import time

class TaskQueue:
    """작업 큐 (deque 활용)"""
    
    def __init__(self, maxsize: Optional[int] = None):
        self.queue = deque(maxlen=maxsize)
        self.completed = deque(maxlen=100)  # 완료된 작업 최대 100개 보관
    
    def add_task(self, task: str, priority: bool = False):
        """작업 추가 (우선순위 작업은 앞에 추가)"""
        if priority:
            self.queue.appendleft(f"{task}")
            print(f"긴급 작업 추가: {task}")
        else:
            self.queue.append(task)
            print(f"일반 작업 추가: {task}")
    
    def process_task(self) -> Optional[str]:
        """다음 작업 처리"""
        if not self.queue:
            return None
        
        task = self.queue.popleft()
        self.completed.append(f"{task} (완료시간: {time.strftime('%H:%M:%S')})")
        print(f"작업 처리: {task}")
        return task
    
    def get_status(self) -> dict:
        """큐 상태 반환"""
        return {
            "대기중": list(self.queue),
            "완료됨": list(self.completed),
            "대기_작업_수": len(self.queue)
        }

# 작업 큐 시연
def demonstrate_task_queue():
    """작업 큐 시연"""
    queue = TaskQueue(maxsize=5)
    
    # 일반 작업들 추가
    queue.add_task("데이터베이스 백업")
    queue.add_task("보고서 작성")
    queue.add_task("코드 리뷰")
    
    # 긴급 작업 추가
    queue.add_task("서버 장애 처리", priority=True)
    queue.add_task("고객 문의 응답", priority=True)
    
    print(f"\n큐 상태: {queue.get_status()['대기_작업_수']}개 대기중")
    
    # 작업 처리
    for _ in range(3):
        queue.process_task()
    
    status = queue.get_status()
    print(f"\n남은 대기 작업: {status['대기중']}")
    print(f"완료된 작업: {status['완료됨']}")

demonstrate_task_queue()
```

처리 순서를 보세요. 일반 작업 셋을 먼저 넣고 긴급 작업 둘을 `appendleft()`로 앞에 끼웠더니, 가장 **나중에** 끼운 "고객 문의 응답"이 맨 앞에 서서 제일 먼저 처리됐습니다. 그다음이 "서버 장애 처리", 그리고 일반 작업 중 첫 번째인 "데이터베이스 백업"이에요.

`get_status()`의 `list(self.queue)`도 눈여겨볼 만합니다. `list()`, `dict()`, `tuple()`, `set()`처럼 자료형 이름과 같은 함수들은 **다른 자료형의 데이터를 그 자료형으로 바꾼 새 객체**를 만들어 줍니다. 형 변환(type casting)이라고 불러 온 것이 사실은 모두 함수였던 거죠. deque를 리스트로 바꿔 두면 받는 쪽은 deque를 몰라도 평범한 리스트처럼 다룰 수 있습니다.

### defaultdict과 Counter 고급 활용

7장에서 딕셔너리를 배웠죠. `collections` 모듈에는 딕셔너리를 바탕으로 한 특수한 딕셔너리들이 있습니다. 모두 딕셔너리의 연산자와 메서드를 그대로 쓸 수 있고, 한 가지씩 재주가 더 붙어 있어요.

- **defaultdict**: 없는 키를 찾으면 `KeyError` 대신 **미리 정해 둔 기본값을 만들어 넣습니다**. `defaultdict(list)`면 빈 리스트, `defaultdict(int)`면 0이 기본값이에요. "이 키가 처음인가?"를 매번 확인할 필요가 없어집니다.
- **Counter**: 해시 가능한(hashable) 값의 개수를 세는 데 특화된 딕셔너리입니다. 리스트를 넣으면 값마다 몇 번 나왔는지 세어 주고, `most_common(n)`으로 많이 나온 순서대로 n개를 꺼낼 수 있어요. 없는 값을 물으면 0을 돌려줍니다.
- **OrderedDict**: 넣은 순서를 기억하는 딕셔너리입니다. 다만 파이썬 3.7부터는 보통 딕셔너리도 넣은 순서를 지키도록 언어 규칙이 정해져서, 요즘은 쓸 일이 많이 줄었습니다.

먼저 짧은 예제로 감을 잡아 봅시다.

```python
from collections import defaultdict, Counter

a = [1, 1, 1, 2, 2, 3, 3, 3, 3, 3]
counts = Counter(a)
print(counts)                 # Counter({3: 5, 1: 3, 2: 2})
print(counts.most_common(1))  # [(3, 5)]
print(counts[7])              # 0 (없는 값은 0개)

groups = defaultdict(list)    # 없는 키는 빈 리스트로 시작
for word in ["사과", "바나나", "수박", "배"]:
    groups[len(word)].append(word)
print(dict(groups))           # {2: ['사과', '수박'], 3: ['바나나'], 1: ['배']}
```

`groups[len(word)].append(word)` 한 줄이 핵심입니다. 보통 딕셔너리였다면 키 `2`가 처음 나왔을 때 `KeyError`가 났을 텐데, defaultdict는 빈 리스트를 먼저 만들어 넣고 거기에 `append()`합니다.

아래 예제는 이 둘을 텍스트 통계에 씁니다. 단어 빈도는 `Counter`, 문장 길이 분포와 품사 패턴은 `defaultdict`가 맡아요. 뒤쪽의 **ChainMap**은 여러 딕셔너리를 겹쳐 놓고 **앞에 있는 것부터** 찾는 도구입니다. 투명 필름 여러 장을 겹쳐 놓고 위에서 내려다보는 것과 같아요. 위 필름에 글씨가 있으면 그게 보이고, 비어 있으면 아래 필름의 글씨가 보입니다. 기본 설정 위에 환경별 설정을 덮어쓰는 데 잘 맞죠.

```python
from collections import defaultdict, Counter, namedtuple
from typing import Dict, List
import re

class KoreanTextStats:
    """한국어 텍스트 통계 분석기"""
    
    def __init__(self):
        self.word_frequency = Counter()
        self.sentence_lengths = defaultdict(int)
        self.pos_patterns = defaultdict(list)  # 품사별 패턴
        
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """텍스트 종합 분석"""
        # 문장 분리
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        
        # 단어 분리 및 빈도 계산
        words = []
        for sentence in sentences:
            sentence_words = sentence.split()
            words.extend(sentence_words)
            
            # 문장 길이별 분포
            length_category = self._categorize_sentence_length(len(sentence))
            self.sentence_lengths[length_category] += 1
        
        # 단어 빈도 업데이트
        self.word_frequency.update(words)
        
        # 품사 패턴 분석 (간단한 규칙 기반)
        self._analyze_pos_patterns(words)
        
        return {
            "총_문장_수": len(sentences),
            "총_단어_수": len(words),
            "고유_단어_수": len(set(words)),
            "평균_문장_길이": sum(len(s) for s in sentences) / len(sentences) if sentences else 0,
            "문장_길이_분포": dict(self.sentence_lengths),
            "빈출_단어": self.word_frequency.most_common(10),
            "품사_패턴": {k: len(v) for k, v in self.pos_patterns.items()}
        }
    
    def _categorize_sentence_length(self, length: int) -> str:
        """문장 길이 범주화"""
        if length < 30:
            return "짧은문장"
        elif length < 60:
            return "보통문장"
        else:
            return "긴문장"
    
    def _analyze_pos_patterns(self, words: List[str]):
        """간단한 품사 패턴 분석"""
        # 한국어 조사/어미 패턴 (매우 간단한 규칙)
        for word in words:
            if word.endswith(('은', '는', '이', '가', '을', '를')):
                self.pos_patterns['조사'].append(word)
            elif word.endswith(('다', '요', '니다', '습니다')):
                self.pos_patterns['어미'].append(word)
            elif any(word.startswith(prefix) for prefix in ['안', '못', '불', '비']):
                self.pos_patterns['부정어'].append(word)
            else:
                self.pos_patterns['기타'].append(word)

# ChainMap 활용한 설정 관리
def demonstrate_chainmap():
    """ChainMap을 활용한 설정 관리"""
    # 기본 설정
    default_config = {
        "host": "localhost",
        "port": 8000,
        "debug": False,
        "database": "sqlite:///default.db"
    }
    
    # 개발 환경 설정
    dev_config = {
        "debug": True,
        "database": "sqlite:///dev.db",
        "log_level": "DEBUG"
    }
    
    # 운영 환경 설정
    prod_config = {
        "host": "production.server.com",
        "port": 80,
        "database": "postgresql://prod_db",
        "log_level": "WARNING"
    }
    
    # ChainMap으로 설정 계층 구성
    # 우선순위: 운영 > 개발 > 기본
    config = ChainMap(prod_config, dev_config, default_config)
    
    print("설정 관리 (ChainMap):")
    print(f"현재 호스트: {config['host']}")
    print(f"현재 포트: {config['port']}")  
    print(f"현재 데이터베이스: {config['database']}")
    print(f"로그 레벨: {config['log_level']}")
    print(f"디버그 모드: {config['debug']}")
    
    # 런타임에 설정 변경
    runtime_config = {"cache_timeout": 3600}
    config = config.new_child(runtime_config)  # 기존 계층 위에 한 층을 더 얹음
    
    print(f"캐시 타임아웃: {config['cache_timeout']}")
    
    # 설정 계층 확인
    print(f"\n설정 계층 수: {len(config.maps)}")
    for i, layer in enumerate(config.maps):
        print(f"  레이어 {i}: {list(layer.keys())}")

# 텍스트 분석 시연
def demonstrate_text_analysis():
    """텍스트 분석 시연"""
    sample_texts = [
        "파이썬은 프로그래밍 언어입니다. 배우기 쉽고 강력한 기능을 제공합니다.",
        "데이터 분석과 웹 개발에 널리 사용됩니다. 많은 개발자들이 선호하는 언어입니다.",
        "라이브러리가 풍부하고 커뮤니티가 활발합니다. 지속적으로 발전하고 있습니다."
    ]
    
    print("\n한국어 텍스트 분석:")
    for i, text in enumerate(sample_texts, 1):
        print(f"\n--- 텍스트 {i} 분석 ---")
        analyzer = KoreanTextStats()  # 텍스트마다 새 분석기 (통계가 섞이지 않도록)
        result = analyzer.analyze_text(text)
        
        for key, value in result.items():
            if isinstance(value, list):
                print(f"{key}: {value[:3]}...")  # 처음 3개만 표시
            else:
                print(f"{key}: {value}")

demonstrate_chainmap()
demonstrate_text_analysis()
```

ChainMap 결과에서 호스트, 포트, 데이터베이스는 맨 위 필름인 운영 설정의 값이 나옵니다. 그런데 디버그 모드는 `True`예요. 운영 설정에 `debug` 칸이 없어서 그 아래 개발 설정의 값이 비쳐 보인 것입니다. 겹쳐 놓기는 이렇게 편하지만, 위층에 빠진 칸이 있으면 아래층 값이 조용히 쓰인다는 점은 꼭 기억하세요.

실행 중에 설정을 한 층 더 얹을 때는 `config.new_child(runtime_config)`를 썼습니다. 기존 세 층을 그대로 둔 채 맨 위에 새 필름 한 장을 더하는 메서드라서 "설정 계층 수"가 4로 나오고, 레이어 0부터 차례로 실행 중 설정, 운영, 개발, 기본 설정의 키가 찍힙니다. 만약 `ChainMap(runtime_config, config)`처럼 ChainMap을 다시 ChainMap으로 감싸면, 기존 ChainMap 전체가 **필름 한 장**으로 취급되어 계층 수가 2로 나와요. 값을 찾는 결과는 같지만 층의 구조가 감춰집니다.

텍스트 분석에서는 반복문 안에서 텍스트마다 `KoreanTextStats()`를 새로 만든다는 점을 눈여겨보세요. 분석기는 `Counter`와 `defaultdict`에 결과를 **쌓아 두는** 구조라서, 분석기 하나로 세 텍스트를 연달아 분석하면 텍스트 2의 "빈출 단어"에 텍스트 1의 단어가 섞이고 "문장 길이 분포"의 합이 그 텍스트의 문장 수보다 커집니다. 텍스트마다 새 분석기를 쓰니 각 결과의 문장 수와 길이 분포가 딱 맞아요. 반대로 여러 텍스트를 합친 전체 통계가 필요하다면 분석기 하나를 계속 쓰면 됩니다.

## 8.5 Pydantic을 활용한 현대적 데이터 검증

### Pydantic 기초 (Pydantic Basics)

8.1절의 Q&A에서 dataclass는 나이 칸에 문자열이 들어와도 막지 않는다고 했죠. 프로그램 안에서 우리가 직접 만드는 값이라면 그래도 괜찮습니다. 하지만 사용자가 입력한 회원가입 정보나 다른 서버가 보낸 데이터는 무엇이 들어올지 모릅니다. 이런 바깥 데이터는 **입구에서 검사**해야 해요. 관공서 접수 창구 직원이 서류를 받자마자 빈칸과 형식을 확인하고, 틀린 곳이 있으면 그 자리에서 돌려주는 것처럼요.

Pydantic은 Python 타입 힌트를 활용한 현대적인 데이터 검증 라이브러리입니다. dataclass보다 강력한 검증과 자동 타입 변환을 제공합니다. 표준 라이브러리가 아니라서 먼저 설치해야 합니다(`uv add pydantic`). 이 장의 예제는 Pydantic 2 문법(`field_validator`, `model_validator`, `model_dump()`)을 기준으로 합니다.

예제에서 검사 규칙은 세 군데에 적습니다.

- `Field(...)`: 칸 하나에 대한 간단한 규칙입니다. `...`은 "꼭 채워야 함", `ge=0, le=120`은 0 이상 120 이하, `pattern=`은 정규 표현식 형식 검사예요.
- `@field_validator('name')`: 칸 하나를 직접 만든 함수로 검사합니다. 틀리면 `ValueError`를 일으키고, 맞으면 값을 그대로 돌려줍니다.
- `@model_validator(mode='after')`: 모든 칸이 채워진 뒤 **칸들 사이의 관계**를 검사합니다. "나이와 생년월일이 맞는가"처럼 칸 하나만 봐서는 알 수 없는 규칙이 여기에 들어가요.

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import List, Optional, Union
from datetime import date, datetime
import re
import json

# 기본 Pydantic 모델
class KoreanPerson(BaseModel):
    """한국인 개인정보 모델"""
    name: str = Field(..., min_length=2, max_length=10, description="한글 이름")
    age: int = Field(..., ge=0, le=120, description="나이")
    phone: str = Field(..., pattern=r'^010-\d{4}-\d{4}$', description="휴대폰 번호")
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    birth_date: Optional[date] = None
    
    @field_validator('name')
    @classmethod
    def validate_korean_name(cls, v):
        """한글 이름 검증"""
        korean_pattern = re.compile(r'^[가-힣]{2,5}$')
        if not korean_pattern.match(v):
            raise ValueError('한글 2-5자로 입력해주세요')
        return v
    
    @model_validator(mode='after')
    def validate_birth_date(self):
        """생년월일과 나이의 일관성 검증"""
        if self.birth_date and self.age:
            calculated_age = datetime.now().year - self.birth_date.year
            if abs(calculated_age - self.age) > 1:
                raise ValueError('나이와 생년월일이 일치하지 않습니다')
        return self
    
    # JSON 스키마 생성 시 예시 데이터 포함
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "김철수",
                "age": 26,
                "phone": "010-1234-5678", 
                "email": "kim@example.com",
                "birth_date": "1998-03-15"
            }
        }
    )

# 자동 타입 변환 시연
def demonstrate_pydantic_basics():
    """Pydantic 기본 기능 시연"""
    print("Pydantic 기본 검증:")
    
    # 올바른 데이터
    try:
        person = KoreanPerson(
            name="김철수",
            age=26,
            phone="010-1234-5678",
            email="kim@example.com"
        )
        print(f"[O] 유효한 데이터: {person.name}, {person.age}세")
    except Exception as e:
        print(f"[X] 검증 실패: {e}")
    
    # 자동 타입 변환
    try:
        person = KoreanPerson(
            name="이영희",
            age="30",  # 문자열 -> 정수 자동 변환
            phone="010-9876-5432"
        )
        print(f"[O] 타입 변환: 나이 {person.age} (타입: {type(person.age)})")
    except Exception as e:
        print(f"[X] 변환 실패: {e}")
    
    # 검증 실패 사례
    try:
        invalid_person = KoreanPerson(
            name="Kim",  # 영문 이름
            age=26,
            phone="010-1234-567"  # 잘못된 번호 형식
        )
    except Exception as e:
        print(f"[X] 예상된 검증 실패: {e}")

demonstrate_pydantic_basics()
```

결과에서 볼 점이 세 가지 있습니다.

1. 두 번째 사람은 나이를 문자열 `"30"`으로 넣었는데 `30 (타입: <class 'int'>)`으로 나옵니다. Pydantic이 숫자로 바꿀 수 있는 문자열을 알아서 정수로 바꿔 준 거예요. `"서른"`처럼 바꿀 수 없는 값이면 오류가 납니다.
2. 세 번째 사람은 이름(`Kim`)과 전화번호(`010-1234-567`)가 둘 다 틀렸는데, 오류 메시지 하나에 `2 validation errors`로 **두 문제를 한꺼번에** 알려 줍니다. 하나 고치고 다시 넣고, 또 하나 고치고 다시 넣는 수고를 덜어 주죠.
3. 모델 전체에 대한 설정은 `model_config = ConfigDict(...)`에 적습니다. 여기서는 `json_schema_extra`로 JSON 스키마에 예시 데이터를 넣었어요. 인터넷의 옛 예제에서 보이는 `class Config:`와 `schema_extra`는 Pydantic 1의 방식이라, Pydantic 2에서 그대로 쓰면 경고(`UserWarning`)가 납니다.

### 한국 특화 데이터 검증 (Korean-specific Validation)

Pydantic 모델은 다른 모델을 칸으로 가질 수 있습니다. 아래 예제에서 `KoreanBusiness`는 `address` 칸에 `KoreanAddress`를, `KoreanEmployee`는 `personal_info` 칸에 앞에서 만든 `KoreanPerson`을 품고 있어요. 바깥 모델을 만들 때 안쪽 모델의 검사도 함께 이루어집니다. 서류 안에 첨부 서류가 있으면 첨부 서류도 같이 확인하는 셈이죠.

`validate_business_number()`의 체크섬 계산은 주석에 적힌 대로 **간소화한 예시**입니다. 실제 사업자등록번호 검증 규칙과는 다르니 그대로 가져다 쓰지 마세요. 예제의 번호 `123-45-67890`은 이 간이 계산을 통과하지 못해 `[!]` 경고가 찍히지만, 경고만 하고 값은 받아들이도록 짜여 있어서 사업자 정보는 정상으로 만들어집니다.

```python
class KoreanAddress(BaseModel):
    """한국 주소 검증 모델"""
    postal_code: str = Field(..., pattern=r'^\d{5}$', description="우편번호")
    city: str = Field(..., min_length=2, description="시/도")
    district: str = Field(..., min_length=2, description="구/군")
    street: str = Field(..., min_length=3, description="상세주소")
    
    @field_validator('city')
    @classmethod
    def validate_korean_city(cls, v):
        """한국 시/도명 검증"""
        valid_cities = [
            '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', 
            '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원도',
            '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도'
        ]
        
        # 간단한 형태도 허용 (서울, 부산 등)
        simple_names = [city.replace('특별시', '').replace('광역시', '').replace('도', '') 
                       for city in valid_cities]
        
        if v not in valid_cities and v not in simple_names:
            raise ValueError(f'올바른 시/도명을 입력해주세요. 입력값: {v}')
        return v

class KoreanBusiness(BaseModel):
    """한국 사업자 정보 모델"""
    business_name: str = Field(..., min_length=2, max_length=50)
    business_number: str = Field(..., pattern=r'^\d{3}-\d{2}-\d{5}$', 
                                description="사업자등록번호 (123-45-67890)")
    address: KoreanAddress
    phone: str = Field(..., pattern=r'^0\d{1,2}-\d{3,4}-\d{4}$', 
                      description="사업장 전화번호")
    ceo_name: str = Field(..., description="대표자명")
    employees: int = Field(default=1, ge=1, le=10000, description="직원 수")
    
    @field_validator('business_number')
    @classmethod
    def validate_business_number(cls, v):
        """사업자등록번호 체크섬 검증"""
        # 간단한 체크섬 검증 (실제로는 더 복잡한 알고리즘 사용)
        digits = ''.join(c for c in v if c.isdigit())
        if len(digits) != 10:
            raise ValueError('사업자등록번호는 10자리 숫자여야 합니다')
        
        # 체크섬 계산 (간소화된 버전)
        multipliers = [1, 3, 7, 1, 3, 7, 1, 3, 5, 1]
        total = sum(int(digit) * mult for digit, mult in zip(digits, multipliers))
        
        if total % 10 != 0:
            # 실제 구현에서는 더 정확한 체크섬 사용
            print(f"[!] 사업자등록번호 체크섬 확인 필요: {v}")
        
        return v
    
    @model_validator(mode='after')
    def validate_business_logic(self):
        """사업자 정보 전체 검증"""
        if self.ceo_name and self.business_name:
            # CEO 이름이 사업자명과 동일한 경우 개인사업자로 간주
            if self.ceo_name in self.business_name:
                if self.employees > 50:
                    raise ValueError('개인사업자는 직원 수 제한이 있습니다')
        
        return self

class KoreanEmployee(BaseModel):
    """한국 직원 정보 모델"""
    personal_info: KoreanPerson
    employee_id: str = Field(..., pattern=r'^EMP\d{4}$')
    department: str = Field(..., min_length=2)
    position: str = Field(..., min_length=2)
    salary: int = Field(..., ge=2000000, le=200000000, description="연봉 (원)")
    hire_date: date = Field(default_factory=date.today)
    
    @field_validator('hire_date')
    @classmethod
    def validate_hire_date(cls, v):
        """입사일 검증"""
        if v > date.today():
            raise ValueError('입사일은 미래일 수 없습니다')
        if v.year < 1980:
            raise ValueError('입사일이 너무 과거입니다')
        return v
    
    def calculate_years_of_service(self) -> int:
        """근속년수 계산"""
        today = date.today()
        years = today.year - self.hire_date.year
        if today.month < self.hire_date.month or \
           (today.month == self.hire_date.month and today.day < self.hire_date.day):
            years -= 1
        return max(0, years)

# 한국 특화 검증 시연
def demonstrate_korean_validation():
    """한국 특화 데이터 검증 시연"""
    print("\n한국 특화 데이터 검증:")
    
    # 주소 검증
    address = KoreanAddress(
        postal_code="06234",
        city="서울",
        district="강남구",
        street="테헤란로 123"
    )
    print(f"[O] 주소: {address.city} {address.district} {address.street}")
    
    # 사업자 정보 검증
    try:
        business = KoreanBusiness(
            business_name="파이썬 테크놀로지",
            business_number="123-45-67890",
            address=address,
            phone="02-1234-5678",
            ceo_name="김대표",
            employees=15
        )
        print(f"[O] 사업자: {business.business_name} ({business.business_number})")
    except Exception as e:
        print(f"[X] 사업자 검증 실패: {e}")
    
    # 직원 정보 검증
    person = KoreanPerson(
        name="박개발",
        age=28,
        phone="010-1111-2222",
        email="park@company.com"
    )
    
    employee = KoreanEmployee(
        personal_info=person,
        employee_id="EMP0001",
        department="개발팀",
        position="시니어 개발자",
        salary=60000000,
        hire_date=date(2021, 3, 15)
    )
    
    years_service = employee.calculate_years_of_service()
    print(f"[O] 직원: {person.name}, 근속 {years_service}년")

demonstrate_korean_validation()
```

주소의 `city`에 `"서울"`이라고 짧게 넣었는데도 통과했습니다. `validate_korean_city()`가 `'서울특별시'`에서 `'특별시'`를 떼어 낸 짧은 이름 목록도 함께 허용하기 때문이에요. 마지막 줄의 근속 연수는 오늘 날짜를 기준으로 계산하므로 실행하는 날에 따라 달라집니다.

### 고급 Pydantic 기능 (Advanced Pydantic Features)

이번 예제에는 새 도구가 셋 나옵니다.

- `class PaymentMethod(str, Enum)`: `str`과 `Enum`을 함께 물려받은 Enum입니다. 멤버가 문자열처럼도 동작해서 JSON으로 내보내거나 문자열과 비교하기 편해요.
- `Literal["KRW"]`: "이 칸에는 딱 이 값만 올 수 있다"는 표시입니다. 통화 칸에 `"USD"`를 넣으면 검증에서 걸립니다.
- `create_model()`: 모델을 **실행 중에** 만들어 냅니다. 설문 문항이 그때그때 바뀌는 경우처럼, 코드를 쓸 때는 칸 목록을 모르는 상황에 씁니다.

`validate_order_logic()`은 결제 수단별 한도나 할인 최소 금액처럼 여러 칸을 함께 봐야 하는 업무 규칙을 모아 둔 곳입니다. 값이 틀리면 오류를 내기도 하지만, 서울 지역 소액 주문에 메모를 덧붙이는 것처럼 값을 보정할 수도 있어요.

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, create_model
from typing import Dict, Any, Union, Literal
from enum import Enum

class PaymentMethod(str, Enum):
    """결제 수단"""
    CARD = "카드"
    CASH = "현금" 
    TRANSFER = "계좌이체"
    MOBILE = "모바일결제"

class OrderStatus(str, Enum):
    """주문 상태"""
    PENDING = "대기"
    CONFIRMED = "확인"
    SHIPPED = "배송중"
    DELIVERED = "배송완료"
    CANCELLED = "취소"

class KoreanOrder(BaseModel):
    """한국 전자상거래 주문 모델"""
    order_id: str = Field(..., pattern=r'^ORD\d{8}$')
    customer_name: str = Field(..., min_length=2, max_length=10)
    customer_phone: str = Field(..., pattern=r'^010-\d{4}-\d{4}$')
    
    # Union 타입으로 여러 결제 수단 지원
    payment_method: PaymentMethod
    payment_amount: int = Field(..., gt=0, description="결제금액")
    
    # Literal 타입으로 정확한 값 제한
    currency: Literal["KRW"] = "KRW"
    
    shipping_address: KoreanAddress
    status: OrderStatus = OrderStatus.PENDING
    
    # 선택적 필드들
    discount_rate: Optional[float] = Field(None, ge=0.0, le=0.5, description="할인율")
    notes: Optional[str] = Field(None, max_length=500)
    
    @model_validator(mode='after')
    def validate_order_logic(self):
        """주문 전체 로직 검증"""
        # 결제 방법별 한도 확인
        if self.payment_method == PaymentMethod.MOBILE and self.payment_amount > 1000000:
            raise ValueError('모바일결제는 일일 100만원 한도입니다')
        
        if self.payment_method == PaymentMethod.CASH and self.payment_amount > 5000000:
            raise ValueError('현금결제는 500만원 한도입니다')
        
        # 할인이 적용된 경우 최소 금액 확인
        if self.discount_rate and self.payment_amount:
            if self.payment_amount < 10000:
                raise ValueError('할인 적용 시 최소 주문금액은 1만원입니다')
        
        # 배송지와 고객 정보 일관성 확인
        if self.shipping_address and self.customer_name:
            # 서울 지역 당일배송 최소 금액
            if (self.shipping_address.city in ['서울', '서울특별시'] and 
                self.payment_amount < 30000):
                current_notes = self.notes or ''
                self.notes = (current_notes + ' [당일배송 최소금액 미달]').strip()
        
        return self
    
    def calculate_final_amount(self) -> int:
        """최종 결제 금액 계산"""
        if self.discount_rate:
            return int(self.payment_amount * (1 - self.discount_rate))
        return self.payment_amount
    
    def can_cancel(self) -> bool:
        """취소 가능 여부"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]

# 동적 모델 생성 (런타임 모델)
def create_survey_model(questions: Dict[str, str]) -> type[BaseModel]:
    """설문조사 동적 모델 생성"""
    fields = {}
    
    for field_name, question in questions.items():
        if '점수' in question:
            fields[field_name] = (int, Field(..., ge=1, le=10, description=question))
        elif '이메일' in question:
            fields[field_name] = (str, Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$', description=question))
        else:
            fields[field_name] = (str, Field(..., min_length=1, max_length=200, description=question))
    
    return create_model('DynamicSurvey', **fields)

# model_config 고급 설정
class KoreanProduct(BaseModel):
    """한국 상품 정보"""
    name: str = Field(..., min_length=2, max_length=100)
    price: int = Field(..., gt=0)
    category: str
    made_in_korea: bool = True
    
    model_config = ConfigDict(
        # 추가 속성 허용 안함
        extra="forbid",
        
        # 검증 전에 문자열 앞뒤 공백 제거
        str_strip_whitespace=True,
        
        # 스키마 예제
        json_schema_extra={
            "example": {
                "name": "한국산 김치",
                "price": 15000,
                "category": "식품",
                "made_in_korea": True
            }
        }
    )

# 고급 기능 시연
def demonstrate_advanced_pydantic():
    """고급 Pydantic 기능 시연"""
    print("\n고급 Pydantic 기능:")
    
    # 복잡한 주문 검증
    address = KoreanAddress(
        postal_code="12345",
        city="서울",
        district="강남구", 
        street="테헤란로 456"
    )
    
    order = KoreanOrder(
        order_id="ORD20231201",
        customer_name="최고객",
        customer_phone="010-9999-8888",
        payment_method=PaymentMethod.CARD,
        payment_amount=50000,
        shipping_address=address,
        discount_rate=0.1
    )
    
    final_amount = order.calculate_final_amount()
    print(f"[O] 주문: {order.order_id}, 최종금액: {final_amount:,}원")
    print(f"   취소가능: {order.can_cancel()}")
    
    # 동적 모델 생성
    survey_questions = {
        "satisfaction_score": "서비스 만족도 점수는?",
        "email": "이메일 주소를 입력하세요",
        "feedback": "추가 의견이 있으시면 작성해주세요"
    }
    
    SurveyModel = create_survey_model(survey_questions)
    
    survey = SurveyModel(
        satisfaction_score=9,
        email="customer@example.com",
        feedback="서비스가 매우 좋습니다"
    )
    
    print(f"[O] 설문조사: 만족도 {survey.satisfaction_score}점")
    
    # 상품 정보
    product = KoreanProduct(
        name="  한국산 고추장  ",  # 공백 자동 제거
        price=8000,
        category="조미료"
    )
    
    print(f"[O] 상품: {product.name} ({product.price:,}원)")

demonstrate_advanced_pydantic()
```

주문의 최종 금액은 결제 금액 50,000원에 할인율 0.1을 적용한 45,000원입니다. 상태가 기본값인 `PENDING`(대기)이니 `can_cancel()`은 `True`를 돌려주죠. 이처럼 검증을 마친 모델에는 계산 메서드를 마음 놓고 붙일 수 있습니다. 이미 입구에서 값이 올바르다는 것을 확인했으니, 메서드 안에서 값을 또 의심할 필요가 없거든요.

동적으로 만든 설문 모델도 평범한 모델처럼 검증하며 값을 받아 `만족도 9점`이 출력됩니다. 마지막 상품은 이름을 `"  한국산 고추장  "`처럼 앞뒤 공백을 붙여 넣었는데 `한국산 고추장`으로 깔끔하게 나와요. `model_config`의 `str_strip_whitespace=True`가 검증 전에 문자열 앞뒤 공백을 지웠기 때문입니다. `extra="forbid"`는 정해 두지 않은 칸(예: `color="red"`)이 들어오면 오류를 내라는 설정이에요.

### JSON/API 통합 (JSON/API Integration)

웹 서비스끼리는 데이터를 주로 JSON 문자열로 주고받습니다. Pydantic 모델은 이 변환을 메서드 하나로 해 줘요.

- `model_dump()`: 모델을 딕셔너리로 바꿉니다.
- `model_dump_json()`: 모델을 JSON 문자열로 바꿉니다.
- `model_json_schema()`: "이 모델은 이런 칸들로 되어 있다"는 설명서(JSON 스키마)를 만듭니다.

반대 방향은 예제의 `from_json()`처럼 JSON을 딕셔너리로 읽은 뒤 모델에 넣으면 됩니다. 이때 검증도 다시 이루어지니, 밖에서 들어온 JSON도 안심하고 쓸 수 있어요.

예제 중간의 `FastAPI` 부분은 이 모델을 웹 API의 입력과 출력 형식으로 그대로 쓰는 모습을 미리 보여 줍니다. FastAPI는 19장에서 본격적으로 다루니 지금은 "Pydantic 모델이 API의 양식이 된다"는 것만 보면 됩니다. 실행하려면 `uv add "fastapi[standard]"`로 설치가 필요합니다(19장과 같은 설치 방법).

```python
from pydantic import BaseModel
from typing import List, Dict
import json
from fastapi import FastAPI
from datetime import datetime

class APIResponse(BaseModel):
    """표준 API 응답 형식"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)  # JSON에서는 ISO 형식 문자열로 바뀜

class KoreanUserAPI(BaseModel):
    """API용 한국 사용자 모델"""
    user_id: str = Field(..., pattern=r'^USER\d{6}$')
    name: str = Field(..., min_length=2, max_length=10)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: str = Field(..., pattern=r'^010-\d{4}-\d{4}$')
    address: KoreanAddress
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    def to_api_response(self, message: str = "성공") -> APIResponse:
        """API 응답 형식으로 변환"""
        return APIResponse(
            success=True,
            message=message,
            data=self.model_dump()
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'KoreanUserAPI':
        """JSON 문자열에서 객체 생성"""
        data = json.loads(json_str)
        return cls(**data)
    
    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return self.model_dump_json(indent=2)

# OpenAPI 스키마 생성을 위한 FastAPI 통합 예제
app = FastAPI(title="Korean User API", version="1.0.0")

@app.post("/users/", response_model=APIResponse)
async def create_user(user: KoreanUserAPI):
    """새 사용자 생성"""
    # 실제로는 데이터베이스에 저장
    response = user.to_api_response("사용자가 성공적으로 생성되었습니다")
    return response

@app.get("/users/{user_id}", response_model=APIResponse) 
async def get_user(user_id: str):
    """사용자 조회"""
    # 실제로는 데이터베이스에서 조회
    sample_address = KoreanAddress(
        postal_code="12345",
        city="서울",
        district="강남구",
        street="테헤란로 789"
    )
    
    user = KoreanUserAPI(
        user_id=user_id,
        name="김사용자",
        email="user@example.com", 
        phone="010-1234-5678",
        address=sample_address,
        preferences={"theme": "dark", "language": "ko"}
    )
    
    return user.to_api_response("사용자 조회 성공")

# 배치 데이터 처리용 모델
class KoreanUserBatch(BaseModel):
    """배치 처리용 사용자 모델"""
    users: List[KoreanUserAPI] = Field(..., min_length=1, max_length=100)
    
    def validate_all(self) -> Dict[str, List[str]]:
        """모든 사용자 검증 결과"""
        results = {"valid": [], "invalid": []}
        
        for user in self.users:
            try:
                # 추가 비즈니스 로직 검증
                if user.name and user.email and user.phone:
                    results["valid"].append(user.user_id)
                else:
                    results["invalid"].append(f"{user.user_id}: 필수 정보 누락")
            except Exception as e:
                results["invalid"].append(f"{user.user_id}: {str(e)}")
        
        return results
    
    def to_csv_headers(self) -> List[str]:
        """CSV 헤더 생성"""
        return ["user_id", "name", "email", "phone", "city", "district"]
    
    def to_csv_rows(self) -> List[List[str]]:
        """CSV 행 데이터 생성"""
        rows = []
        for user in self.users:
            rows.append([
                user.user_id,
                user.name,
                user.email,
                user.phone,
                user.address.city,
                user.address.district
            ])
        return rows

# JSON/API 통합 시연
def demonstrate_json_api_integration():
    """JSON/API 통합 시연"""
    print("\nJSON/API 통합:")
    
    # JSON 직렬화/역직렬화
    address = KoreanAddress(
        postal_code="54321",
        city="부산",
        district="해운대구",
        street="해운대해변로 100"
    )
    
    user = KoreanUserAPI(
        user_id="USER123456",
        name="이부산",
        email="busan@example.com",
        phone="010-2222-3333",
        address=address,
        preferences={"newsletter": True, "sms": False}
    )
    
    # JSON 문자열로 변환
    json_str = user.to_json()
    print("[O] JSON 직렬화:")
    print(json_str[:200] + "...")
    
    # JSON에서 객체 복원
    restored_user = KoreanUserAPI.from_json(json_str)
    print(f"[O] JSON 역직렬화: {restored_user.name} ({restored_user.address.city})")
    
    # API 응답 형식
    api_response = user.to_api_response("사용자 정보 조회 성공")
    print(f"[O] API 응답: {api_response.success}, {api_response.message}")
    
    # OpenAPI 스키마 정보
    schema = KoreanUserAPI.model_json_schema()
    print(f"[O] OpenAPI 스키마 생성됨: {len(schema['properties'])}개 필드")
    
    # 배치 처리
    users_data = [user, user]  # 예시로 같은 사용자 2명
    batch = KoreanUserBatch(users=users_data)
    validation_results = batch.validate_all()
    print(f"[O] 배치 검증: 유효 {len(validation_results['valid'])}명, "
          f"무효 {len(validation_results['invalid'])}명")

demonstrate_json_api_integration()
```

JSON으로 바꿨다가 다시 모델로 되살린 `restored_user`의 이름과 도시가 원래 값 그대로 나옵니다. 안쪽의 주소 모델까지 빠짐없이 오간 거예요. 스키마에는 `user_id`, `name`, `email`, `phone`, `address`, `preferences`의 6개 칸이 잡힙니다.

## 8.6 실무 예제: 한국 부동산 데이터 분석 시스템

### 부동산 데이터 모델 정의

이제 이 장의 도구들을 한데 모아 봅시다. 부동산 거래 데이터를 담고 분석하는 작은 시스템인데, 각 도구가 맡은 역할은 이렇습니다.

| 도구 | 맡은 일 |
|---|---|
| Enum | 부동산 유형(아파트, 빌라 등)과 거래 유형(매매, 전세, 월세) |
| dataclass | 부동산 정보 `PropertyInfo`와 거래 내역 `Transaction` |
| `@property`(11장) | 평 단위 면적, 건물 연식, 평당 가격처럼 **저장하지 않고 그때그때 계산하는 값** |
| defaultdict(list) | 지역별, 유형별로 거래를 모아 두는 바구니 |
| Counter | 지역에서 가장 많이 거래된 유형 찾기 |

면적은 제곱미터로 저장하고 평은 계산해서 씁니다(1평 ≈ 3.3058㎡). 값을 한 가지 단위로만 저장해 두면 두 값이 서로 어긋날 일이 없어요. 평균, 중간값, 표준편차는 표준 라이브러리의 `statistics` 모듈이 계산합니다(17장에서 다시 만납니다).

```python
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Set
from enum import Enum
from datetime import date, datetime
from collections import defaultdict, Counter
import statistics

class PropertyType(Enum):
    """부동산 유형"""
    APARTMENT = "아파트"
    VILLA = "빌라"
    ONEROOM = "원룸"
    OFFICETEL = "오피스텔"
    HOUSE = "단독주택"
    COMMERCIAL = "상가"

class TransactionType(Enum):
    """거래 유형"""
    SALE = "매매"
    RENT = "전세"
    MONTHLY_RENT = "월세"

@dataclass
class PropertyInfo:
    """부동산 기본 정보"""
    property_id: str
    address: str
    property_type: PropertyType
    area_sqm: float  # 평방미터
    floor: Optional[int] = None
    total_floors: Optional[int] = None
    built_year: Optional[int] = None
    
    @property
    def area_pyeong(self) -> float:
        """평 단위 면적"""
        return self.area_sqm / 3.3058
    
    @property
    def age(self) -> Optional[int]:
        """건물 연식"""
        if self.built_year:
            return datetime.now().year - self.built_year
        return None

@dataclass
class Transaction:
    """거래 내역"""
    transaction_id: str
    property_info: PropertyInfo
    transaction_type: TransactionType
    price: int  # 만원 단위
    deposit: Optional[int] = None  # 보증금 (월세의 경우)
    monthly_rent: Optional[int] = None  # 월세
    transaction_date: date = field(default_factory=date.today)
    
    @property
    def price_per_pyeong(self) -> float:
        """평당 가격"""
        return self.price / self.property_info.area_pyeong
    
    def format_price(self) -> str:
        """가격 포맷팅"""
        if self.transaction_type == TransactionType.MONTHLY_RENT:
            return f"보증금 {self.deposit:,}만원, 월세 {self.monthly_rent:,}만원"
        else:
            return f"{self.price:,}만원"

class RealEstateAnalyzer:
    """부동산 데이터 분석기"""
    
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.region_stats = defaultdict(list)
        self.property_type_stats = defaultdict(list)
        
    def add_transaction(self, transaction: Transaction):
        """거래 데이터 추가"""
        self.transactions.append(transaction)
        
        # 지역별 통계 업데이트
        region = self._extract_region(transaction.property_info.address)
        self.region_stats[region].append(transaction)
        
        # 부동산 유형별 통계 업데이트  
        self.property_type_stats[transaction.property_info.property_type].append(transaction)
    
    def _extract_region(self, address: str) -> str:
        """주소에서 지역 추출"""
        # 간단한 지역 추출 로직
        parts = address.split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}"  # 예: "서울시 강남구"
        return parts[0] if parts else "알 수 없음"
    
    def analyze_by_region(self) -> Dict[str, Dict[str, Any]]:
        """지역별 분석"""
        results = {}
        
        for region, transactions in self.region_stats.items():
            if not transactions:
                continue
                
            prices = [t.price for t in transactions if t.transaction_type != TransactionType.MONTHLY_RENT]
            
            if prices:
                results[region] = {
                    "거래수": len(transactions),
                    "평균가격": statistics.mean(prices),
                    "중간가격": statistics.median(prices),
                    "최고가격": max(prices),
                    "최저가격": min(prices),
                    "가격표준편차": statistics.stdev(prices) if len(prices) > 1 else 0,
                    "주요부동산유형": Counter(t.property_info.property_type for t in transactions).most_common(1)[0]
                }
        
        return results
    
    def analyze_by_property_type(self) -> Dict[PropertyType, Dict[str, Any]]:
        """부동산 유형별 분석"""
        results = {}
        
        for prop_type, transactions in self.property_type_stats.items():
            if not transactions:
                continue
                
            prices = [t.price for t in transactions if t.transaction_type != TransactionType.MONTHLY_RENT]
            areas = [t.property_info.area_pyeong for t in transactions]
            
            if prices and areas:
                # 가격과 면적을 같은 거래에서 짝지어야 하므로 월세를 뺀 거래에서 직접 계산
                price_per_pyeong = [t.price_per_pyeong for t in transactions
                                    if t.transaction_type != TransactionType.MONTHLY_RENT]
                
                results[prop_type] = {
                    "거래수": len(transactions),
                    "평균가격": statistics.mean(prices),
                    "평균면적": statistics.mean(areas),
                    "평당평균가격": statistics.mean(price_per_pyeong),
                    "거래유형분포": Counter(t.transaction_type for t in transactions),
                    "주요지역": Counter(self._extract_region(t.property_info.address) for t in transactions).most_common(3)
                }
        
        return results
    
    def find_best_value_properties(self, max_price: int, min_area: float) -> List[Transaction]:
        """가성비 좋은 매물 찾기"""
        candidates = []
        
        for transaction in self.transactions:
            if (transaction.transaction_type == TransactionType.SALE and
                transaction.price <= max_price and
                transaction.property_info.area_pyeong >= min_area):
                candidates.append(transaction)
        
        # 평당 가격 기준으로 정렬
        candidates.sort(key=lambda t: t.price_per_pyeong)
        
        return candidates[:10]  # 상위 10개 반환
    
    def generate_report(self) -> str:
        """종합 분석 보고서 생성"""
        report = ["부동산 시장 분석 보고서", "=" * 40]
        
        # 기본 통계
        total_transactions = len(self.transactions)
        report.append(f"\n기본 통계:")
        report.append(f"  총 거래 수: {total_transactions:,}건")
        report.append(f"  분석 지역 수: {len(self.region_stats)}개 지역")
        report.append(f"  부동산 유형 수: {len(self.property_type_stats)}개 유형")
        
        # 지역별 분석
        region_analysis = self.analyze_by_region()
        report.append(f"\n지역별 분석 (상위 5개 지역):")
        
        sorted_regions = sorted(region_analysis.items(), 
                               key=lambda x: x[1]["평균가격"], reverse=True)[:5]
        
        for region, stats in sorted_regions:
            report.append(f"  {region}:")
            report.append(f"    평균 가격: {stats['평균가격']:,.0f}만원")
            report.append(f"    거래 수: {stats['거래수']}건")
            report.append(f"    주요 유형: {stats['주요부동산유형'][0].value}")
        
        # 부동산 유형별 분석
        type_analysis = self.analyze_by_property_type()
        report.append(f"\n부동산 유형별 분석:")
        
        for prop_type, stats in type_analysis.items():
            report.append(f"  {prop_type.value}:")
            report.append(f"    평균 가격: {stats['평균가격']:,.0f}만원")
            report.append(f"    평당 가격: {stats['평당평균가격']:,.0f}만원/평")
            report.append(f"    평균 면적: {stats['평균면적']:.1f}평")
        
        return "\n".join(report)
```

`RealEstateAnalyzer`는 거래가 들어올 때마다(`add_transaction`) 지역별, 유형별 바구니에 미리 나눠 담아 둡니다. 분석할 때 전체 거래를 처음부터 다시 훑지 않아도 되도록요. 분석 메서드들은 월세 거래를 가격 계산에서 뺍니다. 월세는 `price`가 0이라 평균에 섞이면 값이 엉뚱하게 낮아지기 때문이에요. 이 블록은 클래스만 정의하므로 실행해도 아무것도 출력되지 않습니다.

### 샘플 데이터 생성 및 분석

실제 거래 데이터 대신 `random`으로 그럴듯한 가짜 거래 200건을 만들어 분석기에 넣어 봅니다. 기본 가격 5억(50,000만원)에서 시작해 강남구, 서초구는 2배, 그 밖의 서울은 1.5배, 아파트는 1.2배, 원룸은 0.3배처럼 지역과 유형에 따라 가격을 조정하고, 마지막에 0.7~1.3배 사이로 흔들어 줍니다.

```python
def create_sample_data() -> List[Transaction]:
    """샘플 부동산 거래 데이터 생성"""
    import random
    from datetime import timedelta
    
    # 서울 주요 지역
    seoul_regions = [
        "서울시 강남구", "서울시 서초구", "서울시 송파구", "서울시 강동구",
        "서울시 마포구", "서울시 용산구", "서울시 성동구", "서울시 광진구",
        "서울시 강북구", "서울시 노원구"
    ]
    
    # 경기도 주요 지역
    gyeonggi_regions = [
        "경기도 성남시", "경기도 고양시", "경기도 수원시", "경기도 안양시",
        "경기도 부천시", "경기도 의정부시"
    ]
    
    all_regions = seoul_regions + gyeonggi_regions
    
    transactions = []
    base_date = date(2023, 1, 1)
    
    for i in range(200):  # 200개 샘플 거래 생성
        region = random.choice(all_regions)
        property_type = random.choice(list(PropertyType))
        transaction_type = random.choice(list(TransactionType))
        
        # 지역과 부동산 유형에 따른 가격 조정
        base_price = 50000  # 기본 5억
        if "강남구" in region or "서초구" in region:
            base_price *= 2
        elif "서울시" in region:
            base_price *= 1.5
        
        if property_type == PropertyType.APARTMENT:
            base_price *= 1.2
        elif property_type == PropertyType.ONEROOM:
            base_price *= 0.3
        elif property_type == PropertyType.VILLA:
            base_price *= 0.7
        
        # 면적 생성
        area_sqm = random.uniform(20, 150)
        if property_type == PropertyType.ONEROOM:
            area_sqm = random.uniform(15, 30)
        elif property_type == PropertyType.APARTMENT:
            area_sqm = random.uniform(60, 120)
        
        # 거래 생성
        property_info = PropertyInfo(
            property_id=f"PROP_{i+1:04d}",
            address=f"{region} {random.choice(['역삼동', '논현동', '도곡동', '청담동'])}",
            property_type=property_type,
            area_sqm=area_sqm,
            floor=random.randint(1, 20) if random.random() > 0.2 else None,
            total_floors=random.randint(5, 25) if random.random() > 0.3 else None,
            built_year=random.randint(1990, 2023) if random.random() > 0.1 else None
        )
        
        # 가격 계산
        price_variation = random.uniform(0.7, 1.3)
        final_price = int(base_price * price_variation)
        
        transaction_date = base_date + timedelta(days=random.randint(0, 365))
        
        if transaction_type == TransactionType.MONTHLY_RENT:
            deposit = int(final_price * random.uniform(0.1, 0.3))
            monthly_rent = int(final_price * random.uniform(0.01, 0.03))
            transaction = Transaction(
                transaction_id=f"TXN_{i+1:04d}",
                property_info=property_info,
                transaction_type=transaction_type,
                price=0,  # 월세는 price가 0
                deposit=deposit,
                monthly_rent=monthly_rent,
                transaction_date=transaction_date
            )
        else:
            transaction = Transaction(
                transaction_id=f"TXN_{i+1:04d}",
                property_info=property_info,
                transaction_type=transaction_type,
                price=final_price,
                transaction_date=transaction_date
            )
        
        transactions.append(transaction)
    
    return transactions

def demonstrate_real_estate_analysis():
    """부동산 분석 시연"""
    print("한국 부동산 데이터 분석 시스템")
    print("=" * 50)
    
    # 샘플 데이터 생성
    print("샘플 데이터 생성 중...")
    transactions = create_sample_data()
    
    # 분석기 생성 및 데이터 추가
    analyzer = RealEstateAnalyzer()
    for transaction in transactions:
        analyzer.add_transaction(transaction)
    
    # 종합 보고서 출력
    report = analyzer.generate_report()
    print(report)
    
    # 가성비 좋은 매물 찾기
    print(f"\n가성비 매물 (5억 이하, 25평 이상):")
    print("-" * 40)
    
    value_properties = analyzer.find_best_value_properties(
        max_price=50000,  # 5억
        min_area=25       # 25평
    )
    
    for i, transaction in enumerate(value_properties[:5], 1):
        prop = transaction.property_info
        print(f"{i}. {prop.property_type.value} | {prop.address}")
        print(f"   {prop.area_pyeong:.1f}평 | {transaction.format_price()}")
        print(f"   평당 {transaction.price_per_pyeong:,.0f}만원")
        if prop.age:
            print(f"   건물 연식: {prop.age}년")
        print()

# 분석 실행
demonstrate_real_estate_analysis()
```

데이터를 무작위로 만들기 때문에 **실행할 때마다 숫자가 달라집니다**. 책에 결과를 싣지 않은 이유예요. 그래도 몇 가지는 늘 같습니다. 총 거래는 200건이고, 지역은 서울 10곳과 경기 6곳을 합친 16개 이내, 유형은 6개 이내로 잡힙니다. 지역별 평균 가격 상위에는 가격을 2배로 잡은 강남구, 서초구가 자주 올라오고, "가성비 매물"은 5억 이하이면서 25평 이상인 매매 거래만 골라 평당 가격이 싼 순서로 보여 줍니다.

> **Q. 매번 같은 결과가 나오게 할 수는 없나요?**
> 무작위 값을 만들기 전에 `random.seed(42)`처럼 씨앗 값을 하나 정해 두면 됩니다. 씨앗이 같으면 같은 순서의 "무작위" 값이 나와서, 실행할 때마다 같은 결과를 얻을 수 있어요. 결과를 다른 사람과 비교하거나 버그를 재현할 때 쓰는 방법입니다.

## 8.7 실습 문제

이 장에서 배운 도구를 직접 써 보는 문제입니다. 각 문제는 `# 문제:` 주석으로 요구 사항을 적고 바로 아래에 `# 답:`을 붙여 두었어요. 답을 보기 전에 먼저 직접 짜 보고, 그다음 자기 코드와 비교해 보세요.

### 기본 문제 (1-5번)

dataclass, Enum, NamedTuple, defaultdict, Counter의 기본 사용법을 하나씩 확인하는 문제입니다.

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

# 1번: dataclass 기본 활용
@dataclass
class Book:
    title: str
    author: str
    pages: int
    price: int = 0
    isbn: Optional[str] = None
    
# 문제: 책 정보를 생성하고 할인 가격을 계산하는 메서드를 추가하세요
# 답:
@dataclass
class Book:
    title: str
    author: str  
    pages: int
    price: int = 0
    isbn: Optional[str] = None
    
    def discounted_price(self, discount_rate: float) -> int:
        return int(self.price * (1 - discount_rate))

book = Book("파이썬 완전정복", "김개발", 500, 35000)
print(f"할인가: {book.discounted_price(0.2):,}원")

# 2번: Enum 활용
class WeekDay(Enum):
    MONDAY = "월요일"
    TUESDAY = "화요일"
    WEDNESDAY = "수요일"
    THURSDAY = "목요일"
    FRIDAY = "금요일"

# 문제: 주말 여부를 확인하는 메서드를 추가하세요
# 답:
class WeekDay(Enum):
    MONDAY = "월요일"
    TUESDAY = "화요일"
    WEDNESDAY = "수요일" 
    THURSDAY = "목요일"
    FRIDAY = "금요일"
    SATURDAY = "토요일"
    SUNDAY = "일요일"
    
    def is_weekend(self) -> bool:
        return self in (WeekDay.SATURDAY, WeekDay.SUNDAY)

print(f"금요일은 주말인가? {WeekDay.FRIDAY.is_weekend()}")

# 3번: NamedTuple 활용
from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float

# 문제: 두 점 사이의 거리를 계산하는 메서드를 추가하세요
# 답:
class Point(NamedTuple):
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5

p1 = Point(0, 0)
p2 = Point(3, 4)
print(f"거리: {p1.distance_to(p2)}")

# 4번: defaultdict 활용
from collections import defaultdict

student_scores = [
    ("김철수", "국어", 85),
    ("김철수", "영어", 92),
    ("이영희", "국어", 95),
    ("이영희", "수학", 87)
]

# 문제: 학생별 과목별 점수를 defaultdict로 구성하세요
# 답:
grades = defaultdict(dict)
for name, subject, score in student_scores:
    grades[name][subject] = score

print(f"김철수 성적: {dict(grades['김철수'])}")

# 5번: Counter 활용
from collections import Counter

text = "파이썬은 정말 좋은 언어입니다 파이썬을 배워봅시다"
# 문제: 가장 자주 나타나는 단어 3개를 찾으세요
# 답:
words = text.split()
word_counter = Counter(words)
most_common = word_counter.most_common(3)
print(f"빈출 단어: {most_common}")
```

### 중급 문제 (6-10번)

도구를 서로 엮어 봅니다. dataclass 안에 dataclass 넣기, Enum으로 신호등 상태 기계 만들기, deque로 실행 취소/다시 실행 구현하기, Generic으로 스택 만들기, ChainMap으로 환경별 설정 관리하기가 나옵니다.

```python
# 6번: 복합 dataclass
@dataclass
class Address:
    city: str
    district: str
    street: str

@dataclass  
class Person:
    name: str
    age: int
    address: Address
    hobbies: List[str] = field(default_factory=list)

# 문제: 같은 지역에 사는지 확인하는 메서드를 추가하세요
# 답:
@dataclass
class Person:
    name: str
    age: int
    address: Address
    hobbies: List[str] = field(default_factory=list)
    
    def lives_in_same_city(self, other: 'Person') -> bool:
        return self.address.city == other.address.city

addr1 = Address("서울", "강남구", "테헤란로")
addr2 = Address("서울", "서초구", "강남대로")
person1 = Person("김철수", 25, addr1)
person2 = Person("이영희", 23, addr2)
print(f"같은 도시: {person1.lives_in_same_city(person2)}")

# 7번: 상태 기계 Enum
class LightState(Enum):
    RED = "빨간불"
    YELLOW = "노란불"  
    GREEN = "초록불"
    
    def next_state(self) -> 'LightState':
        transitions = {
            LightState.RED: LightState.GREEN,
            LightState.GREEN: LightState.YELLOW,
            LightState.YELLOW: LightState.RED
        }
        return transitions[self]

# 문제: 신호등 시뮬레이션을 구현하세요
# 답:
@dataclass
class TrafficLight:
    current_state: LightState = LightState.RED
    
    def change_light(self):
        self.current_state = self.current_state.next_state()
        print(f"신호등: {self.current_state.value}")

light = TrafficLight()
for _ in range(5):
    light.change_light()

# 8번: deque를 활용한 히스토리 관리
from collections import deque

class CommandHistory:
    def __init__(self, max_history: int = 10):
        self.history = deque(maxlen=max_history)
        self.current_index = -1
    
# 문제: 실행 취소/다시 실행 기능을 구현하세요
# 답:
class CommandHistory:
    def __init__(self, max_history: int = 10):
        self.history = deque(maxlen=max_history)
        self.current_index = -1
    
    def execute(self, command: str):
        # 현재 위치 이후의 히스토리 제거
        while len(self.history) > self.current_index + 1:
            self.history.pop()
        
        self.history.append(command)
        self.current_index += 1
        print(f"실행: {command}")
    
    def undo(self) -> Optional[str]:
        if self.current_index >= 0:
            command = self.history[self.current_index]
            self.current_index -= 1
            print(f"실행 취소: {command}")
            return command
        return None
    
    def redo(self) -> Optional[str]:
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            command = self.history[self.current_index]
            print(f"다시 실행: {command}")
            return command
        return None

history = CommandHistory()
history.execute("파일 열기")
history.execute("텍스트 입력")
history.undo()
history.redo()

# 9번: Generic dataclass
from typing import TypeVar, Generic

T = TypeVar('T')

@dataclass
class Stack(Generic[T]):
    items: List[T] = field(default_factory=list)
    
# 문제: push, pop, peek 메서드를 구현하세요
# 답:
@dataclass
class Stack(Generic[T]):
    items: List[T] = field(default_factory=list)
    
    def push(self, item: T):
        self.items.append(item)
    
    def pop(self) -> Optional[T]:
        return self.items.pop() if self.items else None
    
    def peek(self) -> Optional[T]:
        return self.items[-1] if self.items else None
    
    def is_empty(self) -> bool:
        return len(self.items) == 0

int_stack = Stack[int]()
int_stack.push(1)
int_stack.push(2)
print(f"peek: {int_stack.peek()}")
print(f"pop: {int_stack.pop()}")

# 10번: ChainMap 설정 관리
from collections import ChainMap

# 문제: 환경별 설정을 ChainMap으로 관리하는 클래스를 만드세요
# 답:
class ConfigManager:
    def __init__(self):
        self.default_config = {
            "timeout": 30,
            "retry_count": 3,
            "log_level": "INFO"
        }
        self.user_config = {}
        self.runtime_config = {}
        self.config = ChainMap(
            self.runtime_config,
            self.user_config, 
            self.default_config
        )
    
    def set_user_config(self, **kwargs):
        self.user_config.update(kwargs)
    
    def set_runtime_config(self, **kwargs):
        self.runtime_config.update(kwargs)
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)
    
    def get_all_configs(self) -> Dict[str, Any]:
        return dict(self.config)

config_mgr = ConfigManager()
config_mgr.set_user_config(timeout=60, log_level="DEBUG")
config_mgr.set_runtime_config(retry_count=5)

print(f"최종 설정: {config_mgr.get_all_configs()}")
```

### 고급 문제 (11-15번)

작은 시스템 하나를 설계하는 수준의 문제입니다. dataclass 상속, 메서드를 가진 Enum, 의존성이 있는 작업 관리, 여러 층의 캐시, JSON 직렬화 관리자를 만들어 봅니다. 답이 길어도 겁먹지 말고, 어떤 데이터를 어떤 도구에 담았는지부터 읽어 보세요.

```python
# 11번: 복잡한 dataclass 상속
@dataclass
class Vehicle:
    brand: str
    model: str
    year: int
    
    def get_age(self) -> int:
        return datetime.now().year - self.year

@dataclass
class Car(Vehicle):
    doors: int = 4
    fuel_type: str = "gasoline"

@dataclass  
class ElectricCar(Car):
    battery_capacity: float = 0.0
    range_km: int = 0
    fuel_type: str = field(default="electric", init=False)

# 문제: 전기차의 효율성을 계산하는 메서드를 추가하세요
# 답:
@dataclass
class ElectricCar(Car):
    battery_capacity: float = 0.0
    range_km: int = 0
    fuel_type: str = field(default="electric", init=False)
    
    def efficiency_km_per_kwh(self) -> float:
        if self.battery_capacity <= 0:
            return 0.0
        return self.range_km / self.battery_capacity
    
    def charging_cost(self, electricity_price_per_kwh: float) -> float:
        return self.battery_capacity * electricity_price_per_kwh

tesla = ElectricCar("Tesla", "Model 3", 2023, battery_capacity=75.0, range_km=500)
print(f"효율성: {tesla.efficiency_km_per_kwh():.2f} km/kWh")
print(f"충전 비용: {tesla.charging_cost(300):.0f}원")

# 12번: 고급 Enum with 메서드
class HTTPStatus(Enum):
    OK = 200
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
    
    def is_success(self) -> bool:
        return 200 <= self.value < 300
    
    def is_client_error(self) -> bool:
        return 400 <= self.value < 500
    
    def is_server_error(self) -> bool:
        return 500 <= self.value < 600

# 문제: HTTP 응답을 관리하는 클래스를 만드세요
# 답:
@dataclass
class HTTPResponse:
    status: HTTPStatus
    body: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    
    def is_successful(self) -> bool:
        return self.status.is_success()
    
    def add_header(self, key: str, value: str):
        self.headers[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status_code": self.status.value,
            "status_name": self.status.name,
            "body": self.body,
            "headers": self.headers,
            "is_successful": self.is_successful()
        }

response = HTTPResponse(HTTPStatus.OK, "Success", {"Content-Type": "application/json"})
print(f"응답 정보: {response.to_dict()}")

# 13번: 복잡한 데이터 구조 관리
@dataclass
class Task:
    id: str
    title: str
    priority: int
    completed: bool = False
    dependencies: Set[str] = field(default_factory=set)
    
class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.completion_order: deque = deque(maxlen=50)
    
# 문제: 의존성을 고려한 작업 완료 시스템을 구현하세요
# 답:
class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.completion_order: deque = deque(maxlen=50)
    
    def add_task(self, task: Task):
        self.tasks[task.id] = task
    
    def can_complete_task(self, task_id: str) -> bool:
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.completed:
            return False
        
        # 모든 의존성 작업이 완료되었는지 확인
        for dep_id in task.dependencies:
            if dep_id in self.tasks and not self.tasks[dep_id].completed:
                return False
        
        return True
    
    def complete_task(self, task_id: str) -> bool:
        if not self.can_complete_task(task_id):
            return False
        
        self.tasks[task_id].completed = True
        self.completion_order.append(task_id)
        print(f"[O] 작업 완료: {self.tasks[task_id].title}")
        return True
    
    def get_available_tasks(self) -> List[Task]:
        return [task for task in self.tasks.values() 
                if self.can_complete_task(task.id)]

# 테스트
manager = TaskManager()
manager.add_task(Task("1", "기초 설계", 3))
manager.add_task(Task("2", "상세 설계", 2, dependencies={"1"}))
manager.add_task(Task("3", "개발", 1, dependencies={"2"}))
manager.add_task(Task("4", "테스트", 1, dependencies={"3"}))

manager.complete_task("1")
manager.complete_task("2")
available = manager.get_available_tasks()
print(f"수행 가능한 작업: {[t.title for t in available]}")

# 14번: 멀티레벨 캐시 시스템
from collections import OrderedDict

class MultiLevelCache:
    def __init__(self, l1_size: int = 10, l2_size: int = 50):
        self.l1_cache: OrderedDict = OrderedDict()  # LRU 캐시
        self.l2_cache: Dict[str, Any] = {}  # 단순 딕셔너리
        self.l1_size = l1_size
        self.l2_size = l2_size
        self.stats = defaultdict(int)
    
# 문제: 계층적 캐시 시스템의 get/put을 구현하세요
# 답:
class MultiLevelCache:
    def __init__(self, l1_size: int = 10, l2_size: int = 50):
        self.l1_cache: OrderedDict = OrderedDict()
        self.l2_cache: Dict[str, Any] = {}
        self.l1_size = l1_size
        self.l2_size = l2_size
        self.stats = defaultdict(int)
    
    def get(self, key: str) -> Optional[Any]:
        # L1 캐시 확인
        if key in self.l1_cache:
            # LRU 업데이트
            value = self.l1_cache.pop(key)
            self.l1_cache[key] = value
            self.stats["l1_hits"] += 1
            return value
        
        # L2 캐시 확인
        if key in self.l2_cache:
            value = self.l2_cache[key]
            # L1으로 승격
            self._put_l1(key, value)
            self.stats["l2_hits"] += 1
            return value
        
        self.stats["misses"] += 1
        return None
    
    def put(self, key: str, value: Any):
        # L1에 저장
        self._put_l1(key, value)
        # L2에도 저장
        self._put_l2(key, value)
    
    def _put_l1(self, key: str, value: Any):
        if key in self.l1_cache:
            self.l1_cache.pop(key)
        elif len(self.l1_cache) >= self.l1_size:
            # LRU 제거
            evicted_key, evicted_value = self.l1_cache.popitem(last=False)
            # L2로 이동
            self._put_l2(evicted_key, evicted_value)
        
        self.l1_cache[key] = value
    
    def _put_l2(self, key: str, value: Any):
        if len(self.l2_cache) >= self.l2_size and key not in self.l2_cache:
            # 임의의 항목 제거 (단순화)
            oldest_key = next(iter(self.l2_cache))
            del self.l2_cache[oldest_key]
        
        self.l2_cache[key] = value
    
    def get_stats(self) -> Dict[str, Any]:
        total_requests = sum(self.stats.values())
        if total_requests == 0:
            return self.stats
        
        return {
            **dict(self.stats),
            "hit_rate": (self.stats["l1_hits"] + self.stats["l2_hits"]) / total_requests,
            "l1_hit_rate": self.stats["l1_hits"] / total_requests,
            "l2_hit_rate": self.stats["l2_hits"] / total_requests
        }

# 캐시 테스트
cache = MultiLevelCache(l1_size=3, l2_size=5)
for i in range(10):
    cache.put(f"key_{i}", f"value_{i}")

# 액세스 패턴 시뮬레이션
for key in ["key_1", "key_2", "key_1", "key_5", "key_9", "key_1"]:
    value = cache.get(key)
    print(f"GET {key}: {value}")

print(f"캐시 통계: {cache.get_stats()}")

# 15번: 고급 타입 힌팅과 데이터 검증
from typing import Protocol, runtime_checkable
from dataclasses import dataclass, field, asdict
import json

@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Serializable':
        ...

@dataclass
class Address:
    street: str
    city: str
    postal_code: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Address':
        return cls(**data)

@dataclass
class Person:
    name: str
    age: int
    address: Address
    emails: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.age < 0:
            raise ValueError("나이는 0 이상이어야 합니다")
        if not self.name.strip():
            raise ValueError("이름은 비어있을 수 없습니다")
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Person':
        address_data = data.pop('address')
        address = Address.from_dict(address_data)
        return cls(address=address, **data)

# 문제: JSON 직렬화/역직렬화 관리자를 만드세요
# 답:
class SerializationManager:
    @staticmethod
    def to_json(obj: Serializable) -> str:
        if not isinstance(obj, Serializable):
            raise TypeError(f"{type(obj)}는 Serializable 프로토콜을 구현해야 합니다")
        return json.dumps(obj.to_dict(), ensure_ascii=False, indent=2)
    
    @staticmethod
    def from_json(json_str: str, cls: type) -> Serializable:
        if not hasattr(cls, 'from_dict'):
            raise TypeError(f"{cls}는 from_dict 메서드가 필요합니다")
        data = json.loads(json_str)
        return cls.from_dict(data)

# 테스트
address = Address("테헤란로 123", "서울", "06234")
person = Person("김철수", 30, address, ["kim@example.com"])

# 직렬화
json_str = SerializationManager.to_json(person)
print("JSON 직렬화:")
print(json_str)

# 역직렬화
restored_person = SerializationManager.from_json(json_str, Person)
print(f"\n복원된 객체: {restored_person.name}, {restored_person.address.city}")
```

## 8.8 다음 장 미리보기

다음 Chapter 9에서는 **함수형 프로그래밍**을 학습합니다:

### 주요 내용 미리보기
- **함수 정의**: def 키워드와 매개변수 활용
- **고급 매개변수**: *args, **kwargs, 키워드 전용 매개변수
- **람다 함수**: 익명 함수와 함수형 패러다임
- **내장 함수**: map(), filter(), reduce(), zip() 활용
- **데코레이터**: 함수 래핑과 메타프로그래밍
- **실무 프로젝트**: 한국어 자연어 처리 파이프라인

### 연결 포인트
- dataclass와 NamedTuple → 함수의 매개변수와 반환값
- Enum과 타입 힌팅 → 함수 시그니처 최적화
- 고급 자료구조 → 함수형 프로그래밍 패턴

고급 데이터 구조를 완전히 습득했다면, 이제 함수를 통해 데이터를 효율적으로 처리하고 변환하는 함수형 프로그래밍 기법을 배울 준비가 되었습니다!

---

> **학습 팁**: dataclass는 데이터 클래스에, Enum은 상수 관리에, NamedTuple은 불변 구조체에 사용하세요. typing 모듈을 활용하면 코드의 가독성과 안정성을 크게 향상시킬 수 있습니다.

**다음 장에서 만나요!** 