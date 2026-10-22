"""1권 Chapter 11: 객체 지향 프로그래밍 — 11.1 클래스와 객체 기본 개념

원고: manuscript/chapters/11-object-oriented-programming.md (34줄부터)
"""

# ---- 원고 34줄 ----
class Structure:
    A = 1
    B = 2

print(Structure.A, Structure.B)  # 1 2

# ---- 원고 46줄 ----
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

# ---- 원고 98줄 ----
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
