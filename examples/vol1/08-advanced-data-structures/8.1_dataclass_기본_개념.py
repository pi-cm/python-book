"""1권 Chapter 8: 고급 데이터 구조 — 8.1 dataclass 기본 개념

원고: manuscript/chapters/08-advanced-data-structures.md (39줄부터)
"""

# ---- 원고 39줄 ----
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

# ---- 원고 100줄 ----
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
