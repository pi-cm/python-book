"""1권 Chapter 13: 상속과 다형성 (Inheritance and Polymorphism) — 13.1 상속 기초 - TDD로 시작하기 ~ 13.4 다형성과 덕 타이핑 (앞 절의 정의를 이어 쓰므로 한 파일로 묶음)

원고: manuscript/chapters/13-inheritance-polymorphism.md (99줄부터)
"""

# ---- 원고 99줄 ----
# 한국 기업 구조를 모델링한 상속 계층
from typing import List, Optional
from datetime import datetime

class Employee:
    """한국 직장인 기본 클래스"""
    
    def __init__(self, name: str, department: str, salary: int):
        self.name = name
        self.department = department
        self.salary = salary  # 연봉(원)
        self.hire_date = datetime.now()
        self.employee_id = f"EMP{id(self):06d}"
    
    def introduce(self) -> str:
        """자기소개 메서드"""
        return f"안녕하세요, {self.department} {self.name}입니다."
    
    def calculate_bonus(self) -> int:
        """기본 보너스 계산 (급여의 10%)"""
        return int(self.salary * 0.1)
    
    def get_work_years(self) -> float:
        """근무 연수 계산"""
        delta = datetime.now() - self.hire_date
        return round(delta.days / 365.25, 1)

class Developer(Employee):
    """개발자 클래스"""
    
    def __init__(self, name: str, department: str, salary: int, programming_language: str):
        super().__init__(name, department, salary)
        self.programming_language = programming_language
        self.projects: List[str] = []
    
    def introduce(self) -> str:
        """개발자 자기소개 (오버라이딩)"""
        base_intro = super().introduce()
        return f"{base_intro} 주로 {self.programming_language} 언어를 사용합니다."
    
    def add_project(self, project_name: str) -> None:
        """프로젝트 추가"""
        self.projects.append(project_name)
        print(f"[O] '{project_name}' 프로젝트에 참여하게 되었습니다.")
    
    def calculate_bonus(self) -> int:
        """개발자 보너스 (프로젝트 수에 따라 추가)"""
        base_bonus = super().calculate_bonus()
        project_bonus = len(self.projects) * 50000  # 프로젝트당 5만원
        return base_bonus + project_bonus

class Manager(Employee):
    """관리자 클래스"""
    
    def __init__(self, name: str, department: str, salary: int, team_size: int):
        super().__init__(name, department, salary)
        self.team_size = team_size
        self.subordinates: List[Employee] = []
    
    def introduce(self) -> str:
        """관리자 자기소개 (오버라이딩)"""
        return f"안녕하세요, {self.department} {self.name} 부장입니다. {self.team_size}명의 팀을 관리하고 있습니다."
    
    def add_subordinate(self, employee: Employee) -> None:
        """부하직원 추가"""
        self.subordinates.append(employee)
        print(f"[O] {employee.name}님이 {self.name} 부장 팀에 배속되었습니다.")
    
    def calculate_bonus(self) -> int:
        """관리자 보너스 (팀 크기에 따라 추가)"""
        base_bonus = super().calculate_bonus()
        management_bonus = self.team_size * 30000  # 팀원 1명당 3만원
        return base_bonus + management_bonus

class SeniorDeveloper(Developer):
    """시니어 개발자 클래스"""
    
    def __init__(self, name: str, department: str, salary: int, 
                 programming_language: str, experience_years: int):
        super().__init__(name, department, salary, programming_language)
        self.experience_years = experience_years
        self.mentees: List[Developer] = []
    
    def introduce(self) -> str:
        """시니어 개발자 자기소개 (super 체이닝)"""
        base_intro = super().introduce()
        return f"{base_intro} {self.experience_years}년의 경력을 가지고 있습니다."
    
    def mentor_developer(self, junior: Developer) -> None:
        """후배 개발자 멘토링"""
        self.mentees.append(junior)
        print(f"{self.name}님이 {junior.name}님을 멘토링합니다.")
    
    def calculate_total_compensation(self) -> int:
        """총 보상 계산 (급여 + 보너스 + 멘토링 수당)"""
        bonus = self.calculate_bonus()
        mentoring_allowance = len(self.mentees) * 100000  # 멘티 1명당 10만원
        return self.salary + bonus + mentoring_allowance

# 테스트 실행
if __name__ == "__main__":
    print("=== 기본 상속 테스트 ===")
    
    # 기본 직원
    emp = Employee("김직원", "총무팀", 30_000_000)
    print(emp.introduce())
    print(f"보너스: {emp.calculate_bonus():,}원")
    
    # 개발자
    dev = Developer("이개발", "개발팀", 40_000_000, "Python")
    dev.add_project("쇼핑몰 개발")
    dev.add_project("API 서버 구축")
    print(f"\n{dev.introduce()}")
    print(f"보너스: {dev.calculate_bonus():,}원")
    
    # 관리자  
    mgr = Manager("박부장", "영업팀", 60_000_000, 8)
    mgr.add_subordinate(dev)
    print(f"\n{mgr.introduce()}")
    print(f"보너스: {mgr.calculate_bonus():,}원")
    
    # 시니어 개발자
    senior = SeniorDeveloper("최시니어", "개발팀", 55_000_000, "Java", 7)
    senior.add_project("레거시 시스템 개선")
    senior.mentor_developer(dev)
    print(f"\n{senior.introduce()}")
    print(f"총 보상: {senior.calculate_total_compensation():,}원")

# ---- 원고 244줄 ----
from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol, runtime_checkable

class EmployeeLevel(Enum):
    """직급 열거형"""
    INTERN = "인턴"
    JUNIOR = "주니어"
    SENIOR = "시니어" 
    LEAD = "리드"
    MANAGER = "관리자"
    DIRECTOR = "이사"

@runtime_checkable
class Manageable(Protocol):
    """관리 가능한 객체 프로토콜"""
    def get_performance_score(self) -> float: ...
    def set_performance_goal(self, goal: str) -> None: ...

class BaseEmployee(ABC):
    """직원 추상 기본 클래스 (리팩토링)"""
    
    def __init__(self, name: str, department: str, salary: int, level: EmployeeLevel):
        super().__init__()  # 믹스인과 함께 쓸 때 MRO 사슬을 끝까지 잇는다
        self.name = name
        self.department = department
        self.salary = salary
        self.level = level
        self.hire_date = datetime.now()
        self._performance_score = 3.0  # 기본 점수
        self._performance_goals: List[str] = []
    
    @abstractmethod
    def get_job_title(self) -> str:
        """직책 반환 (추상 메서드)"""
        pass
    
    @abstractmethod  
    def calculate_specific_bonus(self) -> int:
        """직종별 보너스 계산 (추상 메서드)"""
        pass
    
    def introduce(self) -> str:
        """템플릿 메서드 패턴"""
        title = self.get_job_title()
        return f"안녕하세요, {self.department} {title} {self.name}입니다."
    
    def calculate_total_bonus(self) -> int:
        """전체 보너스 계산 (템플릿 메서드)"""
        base_bonus = int(self.salary * 0.1)
        specific_bonus = self.calculate_specific_bonus()
        performance_bonus = int(self._performance_score * 20000)
        return base_bonus + specific_bonus + performance_bonus
    
    def get_performance_score(self) -> float:
        return self._performance_score
    
    def set_performance_goal(self, goal: str) -> None:
        self._performance_goals.append(goal)
        print(f"목표 설정: {goal}")

class TechEmployee(BaseEmployee):
    """기술직 직원 기본 클래스"""
    
    def __init__(self, name: str, department: str, salary: int, 
                 level: EmployeeLevel, tech_stack: List[str]):
        super().__init__(name, department, salary, level)
        self.tech_stack = tech_stack
        self.certifications: List[str] = []
    
    def add_certification(self, cert: str) -> None:
        """자격증 추가"""
        self.certifications.append(cert)
        print(f"{cert} 자격증을 취득했습니다!")
    
    def calculate_specific_bonus(self) -> int:
        """기술직 보너스 (자격증 개수에 따라)"""
        return len(self.certifications) * 100000

class BusinessEmployee(BaseEmployee):
    """비즈니스직 직원 기본 클래스"""
    
    def __init__(self, name: str, department: str, salary: int, 
                 level: EmployeeLevel, sales_target: int = 0):
        super().__init__(name, department, salary, level)
        self.sales_target = sales_target
        self.sales_achievement = 0
    
    def record_sales(self, amount: int) -> None:
        """매출 기록"""
        self.sales_achievement += amount
        print(f"매출 {amount:,}원 달성! 총 매출: {self.sales_achievement:,}원")
    
    def calculate_specific_bonus(self) -> int:
        """비즈니스직 보너스 (매출 달성률에 따라)"""
        if self.sales_target == 0:
            return 0
        achievement_rate = self.sales_achievement / self.sales_target
        return int(achievement_rate * 500000)

# ---- 원고 348줄 ----
class Parent:
    def __init__(self):
        self.__secret = "부모가 쓰는 값"

class Child(Parent):
    def __init__(self):
        super().__init__()
        self.__secret = "자식이 쓰는 값"   # 부모 값을 덮어쓰지 않는다

print(Child().__dict__)
# {'_Parent__secret': '부모가 쓰는 값', '_Child__secret': '자식이 쓰는 값'}

# ---- 원고 370줄 ----
def test_multiple_inheritance():
    """다중 상속 테스트"""
    
    # TeamLead는 Developer와 Manager 둘 다 상속해야 함
    team_lead = TeamLead("김팀리드", "개발팀", 70_000_000, "Python", 3)
    
    # 두 부모의 특성을 모두 가져야 함
    assert hasattr(team_lead, 'programming_language')  # Developer로부터
    assert hasattr(team_lead, 'team_size')  # Manager로부터
    
    # 메서드 해결 순서가 올바르게 작동해야 함
    intro = team_lead.introduce()
    assert "팀리드" in intro or "리더" in intro

def test_mro_diamond_problem():
    """다이아몬드 문제 해결 테스트"""
    
    # C3 선형화 알고리즘이 올바르게 작동해야 함
    lead = TeamLead("박리드", "개발팀", 75_000_000, "Java", 5)
    
    # MRO 순서 확인
    mro = TeamLead.__mro__
    assert BaseEmployee in mro
    assert Developer in mro
    assert Manager in mro
    
    # 메서드 호출 순서가 예측 가능해야 함
    bonus = lead.calculate_total_bonus()
    assert bonus > 0

# ---- 원고 412줄 ----
class A:
    def hello(self) -> str:
        return "A"

class B(A):
    def hello(self) -> str:
        return "B→" + super().hello()

class C(A):
    def hello(self) -> str:
        return "C→" + super().hello()

class D(B, C):
    def hello(self) -> str:
        return "D→" + super().hello()

print(D().hello())                          # D→B→C→A
print([cls.__name__ for cls in D.__mro__])  # ['D', 'B', 'C', 'A', 'object']

# ---- 원고 437줄 ----
class Developer(BaseEmployee):
    """개발자 클래스 (다중 상속용 개선)"""
    
    def __init__(self, name: str, department: str, salary: int, programming_language: str):
        super().__init__(name, department, salary, EmployeeLevel.SENIOR)
        self.programming_language = programming_language
        self.projects: List[str] = []
    
    def get_job_title(self) -> str:
        return f"{self.programming_language} 개발자"
    
    def calculate_specific_bonus(self) -> int:
        return len(self.projects) * 50000
    
    def add_project(self, project_name: str) -> None:
        """프로젝트 추가"""
        self.projects.append(project_name)
        print(f"[O] '{project_name}' 프로젝트에 참여하게 되었습니다.")
    
    def code_review(self, junior_name: str) -> None:
        """코드 리뷰"""
        print(f"{self.name}님이 {junior_name}님의 코드를 리뷰합니다.")

class Manager(BaseEmployee):
    """관리자 클래스 (다중 상속용 개선)"""
    
    def __init__(self, name: str, department: str, salary: int, team_size: int):
        super().__init__(name, department, salary, EmployeeLevel.MANAGER)
        self.team_size = team_size
        self.subordinates: List[BaseEmployee] = []
    
    def get_job_title(self) -> str:
        return "팀장"
    
    def calculate_specific_bonus(self) -> int:
        return self.team_size * 30000
    
    def conduct_meeting(self, topic: str) -> None:
        """회의 진행"""
        print(f"{self.name}님이 '{topic}' 주제로 회의를 진행합니다.")

class TeamLead(Developer, Manager):
    """팀 리드 클래스 (다중 상속)"""
    
    def __init__(self, name: str, department: str, salary: int, 
                 programming_language: str, team_size: int):
        # 다중 상속에서 super() 사용 시 주의점
        BaseEmployee.__init__(self, name, department, salary, EmployeeLevel.LEAD)
        self.programming_language = programming_language
        self.team_size = team_size
        self.projects: List[str] = []
        self.subordinates: List[BaseEmployee] = []
    
    def get_job_title(self) -> str:
        """메서드 오버라이딩으로 충돌 해결"""
        return f"{self.programming_language} 팀 리드"
    
    def calculate_specific_bonus(self) -> int:
        """두 부모의 보너스 계산법을 조합"""
        dev_bonus = len(self.projects) * 50000
        mgr_bonus = self.team_size * 30000
        lead_bonus = 200000  # 리더십 보너스
        return dev_bonus + mgr_bonus + lead_bonus
    
    def introduce(self) -> str:
        """메서드 해결 순서 활용"""
        base_intro = super().introduce()
        return f"{base_intro} {self.team_size}명의 개발팀을 이끌고 있습니다."
    
    def lead_technical_discussion(self, topic: str) -> None:
        """기술 토론 리딩"""
        print(f"팀 리드 {self.name}님이 '{topic}' 기술 토론을 이끕니다.")

# MRO 시연 및 테스트
print("=== 다중 상속과 MRO 테스트 ===")

team_lead = TeamLead("김팀리드", "백엔드팀", 80_000_000, "Python", 5)
print(f"MRO: {[cls.__name__ for cls in TeamLead.__mro__]}")

team_lead.add_project("마이크로서비스 개발")
team_lead.conduct_meeting("스프린트 계획")
team_lead.lead_technical_discussion("아키텍처 설계")

print(f"\n{team_lead.introduce()}")
print(f"보너스: {team_lead.calculate_total_bonus():,}원")

# ---- 원고 533줄 ----
class SkillMixin:
    """기술 관리 믹스인"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skills: List[str] = []
        self.skill_levels: dict[str, int] = {}  # 1-5 레벨
    
    def add_skill(self, skill: str, level: int = 1) -> None:
        """기술 추가"""
        if skill not in self.skills:
            self.skills.append(skill)
        self.skill_levels[skill] = level
        print(f"{skill} 기술 (레벨 {level}) 추가")
    
    def upgrade_skill(self, skill: str) -> None:
        """기술 레벨업"""
        if skill in self.skill_levels and self.skill_levels[skill] < 5:
            self.skill_levels[skill] += 1
            print(f"{skill} 레벨업! (레벨 {self.skill_levels[skill]})")

class LeadershipMixin:
    """리더십 관리 믹스인"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.leadership_score = 3.0
        self.team_satisfaction = 3.5
    
    def improve_leadership(self, points: float) -> None:
        """리더십 향상"""
        self.leadership_score = min(5.0, self.leadership_score + points)
        print(f"리더십 점수: {self.leadership_score:.1f}/5.0")
    
    def measure_team_satisfaction(self) -> float:
        """팀 만족도 조사"""
        # 실제로는 팀원들의 피드백을 종합
        return self.team_satisfaction

class MentorshipMixin:
    """멘토링 관리 믹스인"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mentees: List[str] = []
        self.mentoring_hours = 0
    
    def start_mentoring(self, mentee_name: str) -> None:
        """멘토링 시작"""
        if mentee_name not in self.mentees:
            self.mentees.append(mentee_name)
            print(f"{mentee_name}님의 멘토링을 시작합니다.")
    
    def log_mentoring_session(self, hours: float) -> None:
        """멘토링 시간 기록"""
        self.mentoring_hours += hours
        print(f"멘토링 {hours}시간 진행 (총 {self.mentoring_hours}시간)")

# 믹스인을 활용한 현대적 다중 상속
class ModernTeamLead(SkillMixin, LeadershipMixin, MentorshipMixin, BaseEmployee):
    """현대적 팀 리드 (믹스인 패턴)"""
    
    def __init__(self, name: str, department: str, salary: int, primary_skill: str):
        super().__init__(name, department, salary, EmployeeLevel.LEAD)
        self.primary_skill = primary_skill
    
    def get_job_title(self) -> str:
        return f"{self.primary_skill} 팀 리드"
    
    def calculate_specific_bonus(self) -> int:
        """다양한 요소를 고려한 보너스 계산"""
        skill_bonus = sum(self.skill_levels.values()) * 20000
        leadership_bonus = int(self.leadership_score * 50000)
        mentoring_bonus = len(self.mentees) * 30000
        return skill_bonus + leadership_bonus + mentoring_bonus

# 사용 예제
print("=== 믹스인 패턴 테스트 ===")

modern_lead = ModernTeamLead("이모던", "AI팀", 90_000_000, "Machine Learning")

# 믹스인 기능들 사용
modern_lead.add_skill("Python", 5)
modern_lead.add_skill("TensorFlow", 4)
modern_lead.add_skill("Kubernetes", 3)

modern_lead.improve_leadership(0.5)
modern_lead.start_mentoring("김주니어")
modern_lead.start_mentoring("박인턴")
modern_lead.log_mentoring_session(2.5)

print(f"\n{modern_lead.introduce()}")
print(f"총 보너스: {modern_lead.calculate_total_bonus():,}원")
print(f"리더십 점수: {modern_lead.leadership_score}/5.0")
print(f"멘토링 시간: {modern_lead.mentoring_hours}시간")

# ---- 원고 635줄 ----
class Engine:
    def start(self) -> str:
        return "부릉"

class Car:
    def __init__(self):
        self.engine = Engine()   # 차는 엔진을 '가지고' 있다 (has-a)

    def start(self) -> str:
        return f"시동: {self.engine.start()}"

print(Car().start())             # 시동: 부릉

# ---- 원고 663줄 ----
def test_abstract_classes():
    """추상 클래스 테스트"""
    
    # 추상 클래스는 직접 인스턴스화할 수 없어야 함
    with pytest.raises(TypeError):
        PaymentProcessor()
    
    # 구체 클래스는 모든 추상 메서드를 구현해야 함
    card_processor = CreditCardProcessor("신한카드")
    card_processor.set_card_info("1234-5678-9012-3456", "123", "12/30")
    # 승인 여부는 무작위로 정해지므로 결과가 bool인지만 확인
    assert isinstance(card_processor.process_payment(50000), bool)
    
    # 프로토콜 기반 다형성이 작동해야 함
    processors = [
        CreditCardProcessor("우리카드"),
        BankTransferProcessor("국민은행"),
        KakaoPayProcessor("카카오페이")
    ]
    
    for processor in processors:
        assert hasattr(processor, 'process_payment')
        assert hasattr(processor, 'validate_payment')

def test_protocol_based_polymorphism():
    """프로토콜 기반 다형성 테스트"""
    
    # 다양한 결제 수단이 같은 인터페이스로 작동해야 함
    payment_methods = [
        CreditCardProcessor("우리카드"),
        BankTransferProcessor("국민은행"),
        KakaoPayProcessor("카카오페이"),
    ]
    
    for method in payment_methods:
        assert isinstance(method, PaymentMethod)  # 프로토콜 체크
        result = method.process_payment(10000)
        assert isinstance(result, bool)

# ---- 원고 713줄 ----
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable
from enum import Enum
import hashlib
import time

class PaymentStatus(Enum):
    """결제 상태 열거형"""
    PENDING = "대기"
    SUCCESS = "성공" 
    FAILED = "실패"
    CANCELLED = "취소"

@runtime_checkable
class PaymentMethod(Protocol):
    """결제 수단 프로토콜 (인터페이스)"""
    
    def process_payment(self, amount: int) -> bool:
        """결제 처리"""
        ...
    
    def validate_payment(self, amount: int) -> bool:
        """결제 유효성 검사"""
        ...
    
    def get_payment_info(self) -> dict:
        """결제 정보 반환"""
        ...

class PaymentProcessor(ABC):
    """결제 처리기 추상 기본 클래스"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.transaction_history: List[dict] = []
        self._daily_limit = 1000000  # 일일 한도 100만원
        self._daily_used = 0
    
    @abstractmethod
    def process_payment(self, amount: int) -> bool:
        """결제 처리 (추상 메서드)"""
        pass
    
    @abstractmethod
    def validate_payment_details(self, **kwargs) -> bool:
        """결제 상세 정보 검증 (추상 메서드)"""
        pass
    
    def validate_payment(self, amount: int) -> bool:
        """공통 결제 유효성 검사 (템플릿 메서드)"""
        if amount <= 0:
            print("[X] 결제 금액은 0원보다 커야 합니다.")
            return False
        
        if self._daily_used + amount > self._daily_limit:
            print(f"[X] 일일 한도 초과: 현재 {self._daily_used:,}원, 한도 {self._daily_limit:,}원")
            return False
        
        return True
    
    def record_transaction(self, amount: int, status: PaymentStatus, **details) -> str:
        """거래 기록"""
        transaction_id = hashlib.md5(f"{time.time()}{amount}".encode()).hexdigest()[:8]
        
        transaction = {
            "id": transaction_id,
            "amount": amount,
            "status": status.value,
            "provider": self.provider_name,
            "timestamp": datetime.now(),
            "details": details
        }
        
        self.transaction_history.append(transaction)
        
        if status == PaymentStatus.SUCCESS:
            self._daily_used += amount
        
        return transaction_id
    
    def get_payment_info(self) -> dict:
        """결제 정보 반환"""
        return {
            "provider": self.provider_name,
            "daily_limit": self._daily_limit,
            "daily_used": self._daily_used,
            "daily_remaining": self._daily_limit - self._daily_used,
            "transaction_count": len(self.transaction_history)
        }

class CreditCardProcessor(PaymentProcessor):
    """신용카드 결제 처리기"""
    
    def __init__(self, provider_name: str):
        super().__init__(provider_name)
        self.card_number = None
        self.cvv = None
        self.expiry_date = None
    
    def set_card_info(self, card_number: str, cvv: str, expiry_date: str) -> None:
        """카드 정보 설정"""
        self.card_number = card_number[-4:]  # 마지막 4자리만 저장
        self.cvv = "***"  # 보안을 위해 숨김
        self.expiry_date = expiry_date
        print(f"카드 정보 설정 완료: ****-****-****-{self.card_number}")
    
    def validate_payment_details(self, **kwargs) -> bool:
        """카드 정보 검증"""
        if not all([self.card_number, self.cvv, self.expiry_date]):
            print("[X] 카드 정보가 완전하지 않습니다.")
            return False
        return True
    
    def process_payment(self, amount: int) -> bool:
        """신용카드 결제 처리"""
        if not self.validate_payment(amount):
            self.record_transaction(amount, PaymentStatus.FAILED, reason="유효성 검사 실패")
            return False
        
        if not self.validate_payment_details():
            self.record_transaction(amount, PaymentStatus.FAILED, reason="카드 정보 오류")
            return False
        
        # 결제 처리 시뮬레이션
        print(f"{self.provider_name} 카드로 {amount:,}원 결제 중...")
        time.sleep(0.1)  # 네트워크 지연 시뮬레이션
        
        # 90% 성공률
        import random
        success = random.random() > 0.1
        
        if success:
            transaction_id = self.record_transaction(
                amount, PaymentStatus.SUCCESS, 
                method="credit_card", card_last4=self.card_number
            )
            print(f"[O] 결제 성공! 거래번호: {transaction_id}")
            return True
        else:
            self.record_transaction(amount, PaymentStatus.FAILED, reason="카드사 승인 거부")
            print("[X] 결제 실패: 카드사에서 승인을 거부했습니다.")
            return False

class BankTransferProcessor(PaymentProcessor):
    """계좌이체 결제 처리기"""
    
    def __init__(self, bank_name: str):
        super().__init__(bank_name)
        self.account_number = None
        self.account_holder = None
    
    def set_account_info(self, account_number: str, account_holder: str) -> None:
        """계좌 정보 설정"""
        self.account_number = account_number[-4:]  # 마지막 4자리만 저장
        self.account_holder = account_holder
        print(f"계좌 정보 설정: {self.account_holder} (****{self.account_number})")
    
    def validate_payment_details(self, **kwargs) -> bool:
        """계좌 정보 검증"""
        if not all([self.account_number, self.account_holder]):
            print("[X] 계좌 정보가 완전하지 않습니다.")
            return False
        return True
    
    def process_payment(self, amount: int) -> bool:
        """계좌이체 결제 처리"""
        if not self.validate_payment(amount):
            self.record_transaction(amount, PaymentStatus.FAILED, reason="유효성 검사 실패")
            return False
        
        if not self.validate_payment_details():
            self.record_transaction(amount, PaymentStatus.FAILED, reason="계좌 정보 오류")
            return False
        
        print(f"{self.provider_name} 계좌이체로 {amount:,}원 결제 중...")
        time.sleep(0.2)  # 은행 시스템 처리 시간
        
        # 95% 성공률 (계좌이체가 더 안정적)
        import random
        success = random.random() > 0.05
        
        if success:
            transaction_id = self.record_transaction(
                amount, PaymentStatus.SUCCESS,
                method="bank_transfer", 
                account_last4=self.account_number,
                bank=self.provider_name
            )
            print(f"[O] 이체 성공! 거래번호: {transaction_id}")
            return True
        else:
            self.record_transaction(amount, PaymentStatus.FAILED, reason="잔액 부족")
            print("[X] 이체 실패: 계좌 잔액이 부족합니다.")
            return False

class KakaoPayProcessor(PaymentProcessor):
    """카카오페이 결제 처리기"""
    
    def __init__(self, service_name: str = "카카오페이"):
        super().__init__(service_name)
        self.user_id = None
        self.is_authenticated = False
    
    def authenticate_user(self, user_id: str, password: str = "1234") -> bool:
        """사용자 인증"""
        self.user_id = user_id
        # 간단한 인증 시뮬레이션
        self.is_authenticated = (password == "1234")
        
        if self.is_authenticated:
            print(f"카카오페이 인증 성공: {user_id}")
        else:
            print("[X] 카카오페이 인증 실패")
        
        return self.is_authenticated
    
    def validate_payment_details(self, **kwargs) -> bool:
        """카카오페이 인증 확인"""
        if not self.is_authenticated:
            print("[X] 카카오페이 인증이 필요합니다.")
            return False
        return True
    
    def process_payment(self, amount: int) -> bool:
        """카카오페이 결제 처리"""
        if not self.validate_payment(amount):
            self.record_transaction(amount, PaymentStatus.FAILED, reason="유효성 검사 실패")
            return False
        
        if not self.validate_payment_details():
            self.record_transaction(amount, PaymentStatus.FAILED, reason="인증 실패")
            return False
        
        print(f"카카오페이로 {amount:,}원 결제 중...")
        time.sleep(0.1)
        
        # 98% 성공률 (간편결제의 높은 성공률)
        import random
        success = random.random() > 0.02
        
        if success:
            transaction_id = self.record_transaction(
                amount, PaymentStatus.SUCCESS,
                method="kakaopay",
                user_id=self.user_id
            )
            print(f"[O] 카카오페이 결제 성공! 거래번호: {transaction_id}")
            return True
        else:
            self.record_transaction(amount, PaymentStatus.FAILED, reason="시스템 오류")
            print("[X] 카카오페이 결제 실패: 일시적 시스템 오류")
            return False

# ---- 원고 979줄 ----
from typing import TypeVar, Generic, Union
from dataclasses import dataclass
from contextlib import contextmanager

T = TypeVar('T', bound=PaymentProcessor)

@dataclass
class PaymentResult:
    """결제 결과 데이터 클래스"""
    success: bool
    transaction_id: Optional[str] = None
    amount: int = 0
    message: str = ""
    details: dict = None

class PaymentFactory:
    """팩토리 패턴으로 결제 처리기 생성"""
    
    _processors = {
        "신용카드": CreditCardProcessor,
        "계좌이체": BankTransferProcessor, 
        "카카오페이": KakaoPayProcessor
    }
    
    @classmethod
    def create_processor(cls, payment_type: str, provider: str) -> PaymentProcessor:
        """결제 처리기 생성"""
        if payment_type not in cls._processors:
            raise ValueError(f"지원하지 않는 결제 방식: {payment_type}")
        
        processor_class = cls._processors[payment_type]
        return processor_class(provider)
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """지원 가능한 결제 방식 목록"""
        return list(cls._processors.keys())

class PaymentOrchestrator:
    """전략 패턴으로 결제 처리 조율"""
    
    def __init__(self):
        self.processors: List[PaymentProcessor] = []
        self.fallback_enabled = True
    
    def add_processor(self, processor: PaymentProcessor) -> None:
        """결제 처리기 추가"""
        self.processors.append(processor)
        print(f"{processor.provider_name} 결제 수단 추가")
    
    def process_payment_with_fallback(self, amount: int) -> PaymentResult:
        """폴백 지원 결제 처리"""
        if not self.processors:
            return PaymentResult(False, message="사용 가능한 결제 수단이 없습니다.")
        
        for i, processor in enumerate(self.processors):
            try:
                print(f"\n결제 시도 {i+1}/{len(self.processors)}: {processor.provider_name}")
                
                success = processor.process_payment(amount)
                
                if success:
                    # 성공한 처리기를 맨 앞으로 이동 (최적화)
                    if i > 0:
                        self.processors[0], self.processors[i] = self.processors[i], self.processors[0]
                    
                    last_transaction = processor.transaction_history[-1]
                    return PaymentResult(
                        success=True,
                        transaction_id=last_transaction["id"],
                        amount=amount,
                        message=f"결제 완료 (결제 수단: {processor.provider_name})",
                        details=last_transaction
                    )
                
                elif not self.fallback_enabled:
                    break
                    
            except Exception as e:
                print(f"[X] {processor.provider_name} 결제 중 오류: {e}")
                if not self.fallback_enabled:
                    return PaymentResult(False, message=f"결제 오류: {e}")
        
        return PaymentResult(False, message="모든 결제 수단 실패")

@contextmanager
def payment_session(orchestrator: PaymentOrchestrator):
    """결제 세션 컨텍스트 매니저"""
    print("결제 세션 시작")
    try:
        yield orchestrator
    except Exception as e:
        print(f"[X] 결제 세션 오류: {e}")
        raise
    finally:
        print("결제 세션 종료")

# 종합 테스트
if __name__ == "__main__":
    print("=== 추상 클래스와 다형성 테스트 ===")
    
    # 팩토리 패턴으로 처리기 생성
    card_processor = PaymentFactory.create_processor("신용카드", "삼성카드")
    bank_processor = PaymentFactory.create_processor("계좌이체", "신한은행")
    kakao_processor = PaymentFactory.create_processor("카카오페이", "카카오페이")
    
    # 결제 정보 설정
    card_processor.set_card_info("1234-5678-9012-3456", "123", "12/25")
    bank_processor.set_account_info("110-123-456789", "김결제")
    kakao_processor.authenticate_user("user@example.com")
    
    # 오케스트레이터를 통한 통합 결제
    orchestrator = PaymentOrchestrator()
    orchestrator.add_processor(card_processor)
    orchestrator.add_processor(bank_processor) 
    orchestrator.add_processor(kakao_processor)
    
    # 컨텍스트 매니저로 안전한 결제 처리
    with payment_session(orchestrator) as session:
        result = session.process_payment_with_fallback(75000)
        
        if result.success:
            print(f"\n최종 결제 성공!")
            print(f"거래번호: {result.transaction_id}")
            print(f"금액: {result.amount:,}원")
            print(f"메시지: {result.message}")
        else:
            print(f"\n최종 결제 실패: {result.message}")
    
    # 결제 정보 출력
    print("\n결제 수단별 현황:")
    for processor in orchestrator.processors:
        info = processor.get_payment_info()
        print(f"- {info['provider']}: 거래 {info['transaction_count']}건, "
              f"일일사용 {info['daily_used']:,}원/{info['daily_limit']:,}원")

# ---- 원고 1129줄 ----
def test_polymorphism():
    """다형성 테스트"""
    
    # 서로 다른 클래스의 객체들이 같은 인터페이스로 작동해야 함
    animals = [Dog("바둑이"), Cat("나비"), Bird("짹짹이")]
    
    for animal in animals:
        # 모든 동물이 같은 메서드를 가져야 함
        sound = animal.make_sound()
        assert isinstance(sound, str)
        assert len(sound) > 0
    
    # 다형성 함수가 모든 타입에서 작동해야 함
    sounds = animal_chorus(animals)
    assert len(sounds) == 3

def test_duck_typing():
    """덕 타이핑 테스트"""
    
    # File-like 객체들이 모두 같은 방식으로 작동해야 함
    file_objects = [
        StringFile("테스트 내용"),
        DatabaseFile("users"),
        NetworkFile("http://example.com/data")
    ]
    
    for file_obj in file_objects:
        # 덕 타이핑으로 같은 인터페이스 보장
        content = file_obj.read()
        assert content is not None
        file_obj.write("새 내용")
        file_obj.close()

# ---- 원고 1170줄 ----
from typing import Protocol
from io import StringIO, BytesIO


def josa(word: str, with_final: str, without_final: str) -> str:
    """마지막 글자의 받침 유무에 맞춰 조사를 붙인다. 예: josa("나비", "이", "가")는 "나비가"를 돌려준다."""
    last = word[-1]
    # 한글 음절은 '가'부터 28개씩 받침 순서로 놓여 있어서, 나머지가 0이면 받침이 없다
    has_final = "가" <= last <= "힣" and (ord(last) - ord("가")) % 28 != 0
    return word + (with_final if has_final else without_final)

class SoundMaker(Protocol):
    """소리 내는 객체 프로토콜"""
    def make_sound(self) -> str: ...
    def get_species(self) -> str: ...

class Animal(ABC):
    """동물 추상 기본 클래스"""
    
    def __init__(self, name: str):
        self.name = name
        self.energy = 100
    
    @abstractmethod
    def make_sound(self) -> str:
        pass
    
    @abstractmethod
    def get_species(self) -> str:
        pass
    
    def sleep(self) -> None:
        """공통 행동"""
        self.energy = min(100, self.energy + 20)
        print(f"{josa(self.name, '이', '가')} 잠을 자고 있습니다. 에너지: {self.energy}")

class Dog(Animal):
    """개 클래스"""
    
    def __init__(self, name: str, breed: str = "믹스"):
        super().__init__(name)
        self.breed = breed
        self.loyalty = 100
    
    def make_sound(self) -> str:
        return f"{self.name}: 멍멍! "
    
    def get_species(self) -> str:
        return f"{self.breed} 개"
    
    def fetch(self, item: str) -> None:
        """개 고유 행동"""
        print(f"{josa(self.name, '이', '가')} {josa(item, '을', '를')} 가져옵니다!")
        self.energy -= 10

class Cat(Animal):
    """고양이 클래스"""
    
    def __init__(self, name: str, color: str = "회색"):
        super().__init__(name)
        self.color = color
        self.independence = 80
    
    def make_sound(self) -> str:
        return f"{self.name}: 야옹~ "
    
    def get_species(self) -> str:
        return f"{self.color} 고양이"
    
    def hunt(self, prey: str = "쥐") -> None:
        """고양이 고유 행동"""
        print(f"{josa(self.name, '이', '가')} {josa(prey, '을', '를')} 사냥합니다!")
        self.energy -= 15

class Bird(Animal):
    """새 클래스"""
    
    def __init__(self, name: str, wing_span: float = 20.0):
        super().__init__(name)
        self.wing_span = wing_span
        self.can_fly = wing_span > 15.0
    
    def make_sound(self) -> str:
        return f"{self.name}: 짹짹! "
    
    def get_species(self) -> str:
        return "새"
    
    def fly(self, distance: int) -> None:
        """새 고유 행동"""
        if self.can_fly:
            print(f"{josa(self.name, '이', '가')} {distance}m 날아갑니다!")
            self.energy -= distance // 10
        else:
            print(f"{josa(self.name, '은', '는')} 날 수 없습니다.")

# 다형성 활용 함수들
def animal_chorus(animals: List[SoundMaker]) -> List[str]:
    """동물 합창 (다형성)"""
    print("동물 합창단 공연 시작!")
    sounds = []
    
    for animal in animals:
        sound = animal.make_sound()
        species = animal.get_species()
        print(f"  {species}: {sound}")
        sounds.append(sound)
    
    print("합창 끝!")
    return sounds

def feed_animals(animals: List[Animal], food_amount: int = 20) -> None:
    """동물들 먹이주기 (다형성)"""
    print(f"{len(animals)}마리 동물에게 먹이를 줍니다...")
    
    for animal in animals:
        animal.energy = min(100, animal.energy + food_amount)
        print(f"  {animal.name} ({animal.get_species()}): 에너지 {animal.energy}")

def animal_exercise_session(animals: List[Animal]) -> None:
    """동물별 맞춤 운동 (다형성 + 타입 체크)"""
    print("동물 운동 시간!")
    
    for animal in animals:
        print(f"\n{animal.name}의 운동:")
        
        # 다형성과 타입별 특화 행동 조합
        if isinstance(animal, Dog):
            animal.fetch("공")
        elif isinstance(animal, Cat):
            animal.hunt("털실")
        elif isinstance(animal, Bird):
            animal.fly(50)
        
        # 공통 행동
        if animal.energy < 30:
            animal.sleep()

# 덕 타이핑 예제
class FileInterface(Protocol):
    """파일 인터페이스 프로토콜"""
    def read(self) -> str: ...
    def write(self, content: str) -> None: ...
    def close(self) -> None: ...

class StringFile:
    """메모리 문자열 파일 (덕 타이핑)"""
    
    def __init__(self, initial_content: str = ""):
        self._content = StringIO(initial_content)
        self._closed = False
    
    def read(self) -> str:
        if self._closed:
            raise ValueError("파일이 닫혔습니다")
        return self._content.getvalue()
    
    def write(self, content: str) -> None:
        if self._closed:
            raise ValueError("파일이 닫혔습니다")
        self._content.write(content)
        print(f"메모리에 '{content}' 작성")
    
    def close(self) -> None:
        self._content.close()
        self._closed = True
        print("StringFile 닫힘")

class NetworkFile:
    """네트워크 파일 (덕 타이핑)"""
    
    def __init__(self, url: str):
        self.url = url
        self._content = ""
        self._closed = False
    
    def read(self) -> str:
        if self._closed:
            raise ValueError("연결이 닫혔습니다")
        # 실제로는 HTTP 요청
        self._content = f"네트워크 데이터: {self.url}"
        return self._content
    
    def write(self, content: str) -> None:
        if self._closed:
            raise ValueError("연결이 닫혔습니다")
        # 실제로는 POST 요청
        print(f"{self.url}에 '{content}' 업로드")
    
    def close(self) -> None:
        self._closed = True
        print("네트워크 연결 닫힘")

class DatabaseFile:
    """데이터베이스 파일 (덕 타이핑)"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self._content = ""
        self._closed = False
    
    def read(self) -> str:
        if self._closed:
            raise ValueError("데이터베이스 연결이 닫혔습니다")
        self._content = f"SELECT * FROM {self.table_name}"
        return self._content
    
    def write(self, content: str) -> None:
        if self._closed:
            raise ValueError("데이터베이스 연결이 닫혔습니다")
        print(f"{self.table_name} 테이블에 '{content}' 저장")
    
    def close(self) -> None:
        self._closed = True
        print("데이터베이스 연결 닫힘")

def process_files(files: List[FileInterface]) -> None:
    """덕 타이핑으로 다양한 파일 처리"""
    print("파일 처리 시작...")
    
    for i, file_obj in enumerate(files, 1):
        print(f"\n파일 {i} 처리:")
        
        # 덕 타이핑으로 같은 인터페이스 사용
        content = file_obj.read()
        print(f"읽기 완료: {content[:50]}...")
        
        file_obj.write(f"처리 완료 시각: {datetime.now()}")
        file_obj.close()
    
    print("\n모든 파일 처리 완료!")

# 사용 예제
if __name__ == "__main__":
    print("=== 다형성과 덕 타이핑 테스트 ===")
    
    # 다형성 테스트
    animals = [
        Dog("바둑이", "진돗개"),
        Cat("나비", "러시안블루"),
        Bird("짹짹이", 25.0),
        Dog("멍멍이", "골든리트리버"),
        Cat("야옹이", "페르시안")
    ]
    
    # 다형성 함수 호출
    animal_chorus(animals)
    print()
    feed_animals(animals, 25)
    print()
    animal_exercise_session(animals)
    
    print("\n" + "="*50)
    
    # 덕 타이핑 테스트
    files = [
        StringFile("초기 내용입니다."),
        NetworkFile("https://api.example.com/data"),
        DatabaseFile("users")
    ]
    
    process_files(files)

# ---- 원고 1449줄 ----
from typing import TypeVar, Generic, Callable, Union
from functools import singledispatch, wraps
import inspect

# 제네릭 타입을 활용한 고급 다형성
T = TypeVar('T')
U = TypeVar('U')

class Container(Generic[T]):
    """제네릭 컨테이너"""
    
    def __init__(self):
        self._items: List[T] = []
    
    def add(self, item: T) -> None:
        self._items.append(item)
    
    def get_all(self) -> List[T]:
        return self._items.copy()
    
    def transform(self, func: Callable[[T], U]) -> 'Container[U]':
        """함수형 프로그래밍과 다형성 결합"""
        result = Container[U]()
        for item in self._items:
            result.add(func(item))
        return result
    
    def filter(self, predicate: Callable[[T], bool]) -> 'Container[T]':
        """필터링"""
        result = Container[T]()
        for item in self._items:
            if predicate(item):
                result.add(item)
        return result

# 싱글 디스패치를 활용한 다형성
@singledispatch
def process_korean_data(data):
    """한국 데이터 처리 (기본)"""
    return f"알 수 없는 데이터 타입: {type(data).__name__}"

@process_korean_data.register
def _(data: str):
    """문자열 데이터 처리"""
    return f"한국어 텍스트 처리: '{data}' ({len(data)}글자)"

@process_korean_data.register
def _(data: int):
    """숫자 데이터 처리"""
    return f"한국식 숫자 표기: {data:,}원"

@process_korean_data.register
def _(data: list):
    """리스트 데이터 처리"""
    return f"한국 목록 데이터: {len(data)}개 항목 - {', '.join(map(str, data[:3]))}..."

@process_korean_data.register
def _(data: dict):
    """딕셔너리 데이터 처리"""
    korean_keys = [k for k in data.keys() if isinstance(k, str) and any('가' <= c <= '힣' for c in k)]
    return f"한국어 키 {len(korean_keys)}개 포함한 딕셔너리: {list(data.keys())[:3]}..."

# 프로토콜 기반 고급 다형성
class Drawable(Protocol):
    """그리기 가능한 객체"""
    def draw(self, canvas: str) -> str: ...
    def get_bounds(self) -> tuple[int, int, int, int]: ...

class Movable(Protocol):
    """이동 가능한 객체"""
    def move(self, dx: int, dy: int) -> None: ...
    def get_position(self) -> tuple[int, int]: ...

class Interactive(Protocol):
    """상호작용 가능한 객체"""
    def on_click(self, x: int, y: int) -> None: ...
    def on_hover(self) -> str: ...

class KoreanButton:
    """한국형 버튼 (다중 프로토콜 구현)"""
    
    def __init__(self, text: str, x: int = 0, y: int = 0):
        self.text = text
        self.x = x
        self.y = y
        self.width = len(text) * 10 + 20
        self.height = 30
        self.clicked = False
    
    def draw(self, canvas: str) -> str:
        return f"[{self.text}] 버튼을 {canvas}에 그림 ({self.x}, {self.y})"
    
    def get_bounds(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)
    
    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
        print(f"'{self.text}' 버튼 이동 ({dx}, {dy}): 새 위치 ({self.x}, {self.y})")
    
    def get_position(self) -> tuple[int, int]:
        return (self.x, self.y)
    
    def on_click(self, x: int, y: int) -> None:
        bounds = self.get_bounds()
        if bounds[0] <= x <= bounds[2] and bounds[1] <= y <= bounds[3]:
            self.clicked = True
            print(f"[O] '{self.text}' 버튼이 클릭되었습니다!")
        else:
            print(f"[X] 버튼 영역 밖을 클릭했습니다.")
    
    def on_hover(self) -> str:
        return f"'{self.text}' 버튼에 마우스가 올라갔습니다."

class KoreanLabel:
    """한국형 라벨"""
    
    def __init__(self, text: str, x: int = 0, y: int = 0):
        self.text = text
        self.x = x
        self.y = y
        self.width = len(text) * 8
        self.height = 20
    
    def draw(self, canvas: str) -> str:
        return f"'{self.text}' 라벨을 {canvas}에 그림"
    
    def get_bounds(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)
    
    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
    
    def get_position(self) -> tuple[int, int]:
        return (self.x, self.y)

# 고급 다형성 활용 함수들
def render_ui_elements(elements: List[Drawable], canvas: str = "화면") -> None:
    """UI 요소 렌더링 (Drawable 프로토콜)"""
    print(f"{canvas} 렌더링 시작:")
    for element in elements:
        result = element.draw(canvas)
        bounds = element.get_bounds()
        print(f"  - {result} | 경계: {bounds}")

def move_all_elements(elements: List[Movable], dx: int, dy: int) -> None:
    """모든 요소 이동 (Movable 프로토콜)"""
    print(f"모든 요소를 ({dx}, {dy})만큼 이동:")
    for element in elements:
        old_pos = element.get_position()
        element.move(dx, dy)
        new_pos = element.get_position()
        print(f"  - {old_pos} → {new_pos}")

def handle_interactions(elements: List[Interactive], click_x: int, click_y: int) -> None:
    """상호작용 처리 (Interactive 프로토콜)"""
    print(f"({click_x}, {click_y}) 위치 클릭 처리:")
    for element in elements:
        hover_msg = element.on_hover()
        print(f"  - {hover_msg}")
        element.on_click(click_x, click_y)

# 종합 테스트
if __name__ == "__main__":
    print("=== 고급 다형성 패턴 테스트 ===")
    
    # 제네릭 컨테이너 테스트
    print("1. 제네릭 컨테이너:")
    animal_container = Container[Animal]()
    animal_container.add(Dog("바둑이"))
    animal_container.add(Cat("나비"))
    animal_container.add(Bird("짹짹이"))
    
    # 함수형 변환
    sound_container = animal_container.transform(lambda a: a.make_sound())
    sounds = sound_container.get_all()
    print(f"동물 소리: {sounds}")
    
    # 필터링
    dogs_only = animal_container.filter(lambda a: isinstance(a, Dog))
    print(f"개만 필터링: {len(dogs_only.get_all())}마리")
    
    print("\n2. 싱글 디스패치:")
    test_data = [
        "안녕하세요",
        1000000,
        ["사과", "바나나", "오렌지"],
        {"이름": "김철수", "나이": 30, "city": "Seoul"}
    ]
    
    for data in test_data:
        result = process_korean_data(data)
        print(f"  {result}")
    
    print("\n3. 다중 프로토콜:")
    ui_elements = [
        KoreanButton("확인", 10, 20),
        KoreanButton("취소", 100, 20),
        KoreanLabel("사용자 이름:", 10, 60)
    ]
    
    # Drawable 프로토콜로 렌더링
    render_ui_elements(ui_elements, "메인 화면")
    
    # Movable 프로토콜로 이동
    movable_elements = [e for e in ui_elements if isinstance(e, (KoreanButton, KoreanLabel))]
    move_all_elements(movable_elements, 5, 5)
    
    # Interactive 프로토콜로 상호작용
    interactive_elements = [e for e in ui_elements if hasattr(e, 'on_click')]
    handle_interactions(interactive_elements, 50, 25)
