"""1권 부록 B. 한눈에 보는 파이썬 — B.12 클래스 (11장, 13장)

원고: manuscript/appendix/B-cheatsheet.md (530줄부터)
"""

# ---- 원고 530줄 ----
class Account:
    bank = "파이썬은행"                     # 클래스 속성 (모든 객체가 공유)

    def __init__(self, owner, balance=0):
        self.owner = owner                 # 인스턴스 속성
        self._balance = balance            # 밑줄 하나: "내부용" 약속

    @property
    def balance(self):                     # 읽기 전용 속성처럼
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("입금액은 양수여야 합니다")
        self._balance += amount
        return self

    @classmethod
    def empty(cls, owner):                 # 다른 생성 방법
        return cls(owner)

    @staticmethod
    def fee(amount):                       # self도 cls도 필요 없는 도우미
        return amount // 100

    def __repr__(self):
        return f"{type(self).__name__}({self.owner!r}, {self._balance})"

acc = Account.empty("민수").deposit(5000).deposit(300)
print(acc, acc.balance, Account.fee(5000))  # Account('민수', 5300) 5300 50

# ---- 원고 565줄 ----
class Savings(Account):
    def __init__(self, owner, balance=0, rate=0.03):
        super().__init__(owner, balance)   # 부모의 초기화 먼저
        self.rate = rate

    def deposit(self, amount):             # 오버라이딩
        return super().deposit(amount + 100)

s = Savings("지아").deposit(1000)
print(s, isinstance(s, Account))           # Savings('지아', 1100) True
print([c.__name__ for c in Savings.__mro__])  # ['Savings', 'Account', 'object']

# ---- 원고 597줄 ----
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self): ...

class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self):
        return self.side ** 2

print(Square(3).area())   # 9
