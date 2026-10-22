"""1권 Chapter 11: 객체 지향 프로그래밍 — 11.4 특수 메서드 (매직 메서드)

원고: manuscript/chapters/11-object-oriented-programming.md (694줄부터)
"""

# ---- 원고 694줄 ----
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

# ---- 원고 878줄 ----
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

# ---- 원고 919줄 ----
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
