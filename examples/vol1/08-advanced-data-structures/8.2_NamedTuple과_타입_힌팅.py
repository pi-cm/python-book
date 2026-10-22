"""1권 Chapter 8: 고급 데이터 구조 — 8.2 NamedTuple과 타입 힌팅

원고: manuscript/chapters/08-advanced-data-structures.md (173줄부터)
"""

# ---- 원고 173줄 ----
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

# ---- 원고 257줄 ----
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
