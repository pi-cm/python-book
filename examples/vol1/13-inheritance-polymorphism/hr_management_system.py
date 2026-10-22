# [1권 Chapter 13: 상속과 다형성 (Inheritance and Polymorphism) · 13.5 실전 프로젝트: 한국 기업 HR 관리 시스템 · manuscript/chapters/13-inheritance-polymorphism.md:1757]
# hr_management_system.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Protocol
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
import json

class EmployeeLevel(Enum):
    """직급 체계"""
    INTERN = ("인턴", 1)
    JUNIOR = ("주니어", 2) 
    SENIOR = ("시니어", 3)
    LEAD = ("리드", 4)
    MANAGER = ("매니저", 5)
    DIRECTOR = ("이사", 6)
    VP = ("부사장", 7)
    CEO = ("대표", 8)
    
    def __init__(self, korean_name: str, level: int):
        self.korean_name = korean_name
        self.level = level

class Department(Enum):
    """부서"""
    ENGINEERING = "개발팀"
    PRODUCT = "기획팀"
    DESIGN = "디자인팀"
    MARKETING = "마케팅팀"
    SALES = "영업팀"
    HR = "인사팀"
    FINANCE = "재무팀"
    LEGAL = "법무팀"

@dataclass
class PerformanceReview:
    """성과 평가 결과"""
    employee_id: str
    reviewer_id: str
    period: str
    scores: Dict[str, float]
    overall_score: float
    grade: str
    feedback: str
    improvement_areas: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass 
class SalaryInfo:
    """급여 정보"""
    employee_id: str
    base_salary: int
    performance_bonus: int
    position_allowance: int
    meal_allowance: int = 100000
    transport_allowance: int = 100000
    total_before_tax: int = 0
    income_tax: int = 0
    national_pension: int = 0
    health_insurance: int = 0
    employment_insurance: int = 0
    total_deductions: int = 0
    net_salary: int = 0
    
    def __post_init__(self):
        self.total_before_tax = (self.base_salary + self.performance_bonus + 
                               self.position_allowance + self.meal_allowance + 
                               self.transport_allowance)
        self._calculate_deductions()
        self.net_salary = self.total_before_tax - self.total_deductions
    
    def _calculate_deductions(self):
        """세금 및 공제 계산"""
        # 간소화된 한국 세금 계산
        self.income_tax = int(self.total_before_tax * 0.08)  # 간이세액표 기준
        self.national_pension = int(self.total_before_tax * 0.045)  # 국민연금 4.5%
        self.health_insurance = int(self.total_before_tax * 0.0335)  # 건강보험 3.35%
        self.employment_insurance = int(self.total_before_tax * 0.008)  # 고용보험 0.8%
        
        self.total_deductions = (self.income_tax + self.national_pension + 
                               self.health_insurance + self.employment_insurance)

class BaseEmployee(ABC):
    """직원 기본 추상 클래스"""
    
    _employee_counter = 0
    
    def __init__(self, name: str, annual_salary: int, department: Department, 
                 level: EmployeeLevel, hire_date: Optional[date] = None):
        BaseEmployee._employee_counter += 1
        self.employee_id = f"EMP{BaseEmployee._employee_counter:06d}"
        self.name = name
        self.annual_salary = annual_salary
        self.department = department
        self.level = level
        self.hire_date = hire_date or date.today()
        self.direct_manager: Optional['BaseEmployee'] = None
        self.subordinates: List['BaseEmployee'] = []
        self.performance_reviews: List[PerformanceReview] = []
        self.is_active = True
    
    @abstractmethod
    def get_job_title(self) -> str:
        """직책 반환"""
        pass
    
    @abstractmethod
    def calculate_performance_bonus(self) -> int:
        """성과급 계산"""
        pass
    
    def get_monthly_base_salary(self) -> int:
        """월 기본급"""
        return self.annual_salary // 12
    
    def get_years_of_service(self) -> float:
        """근속 년수"""
        delta = date.today() - self.hire_date
        return round(delta.days / 365.25, 1)
    
    def add_subordinate(self, employee: 'BaseEmployee') -> None:
        """부하 직원 추가"""
        if employee not in self.subordinates:
            self.subordinates.append(employee)
            employee.direct_manager = self
            print(f"[O] {employee.name}님이 {self.name}님의 팀에 합류했습니다.")
    
    def remove_subordinate(self, employee: 'BaseEmployee') -> None:
        """부하 직원 제거"""
        if employee in self.subordinates:
            self.subordinates.remove(employee)
            employee.direct_manager = None
            print(f"{employee.name}님이 {self.name}님의 팀에서 떠났습니다.")
    
    def get_all_subordinates(self) -> List['BaseEmployee']:
        """모든 하위 직원 (재귀적)"""
        all_subs = self.subordinates.copy()
        for subordinate in self.subordinates:
            all_subs.extend(subordinate.get_all_subordinates())
        return all_subs
    
    def get_direct_manager(self) -> Optional['BaseEmployee']:
        """직속 상관"""
        return self.direct_manager
    
    def get_department_head(self) -> Optional['BaseEmployee']:
        """부서장 찾기"""
        current = self
        while current.direct_manager:
            current = current.direct_manager
            if current.level in [EmployeeLevel.DIRECTOR, EmployeeLevel.VP, EmployeeLevel.CEO]:
                return current
        return current
    
    def introduce(self) -> str:
        """자기소개"""
        title = self.get_job_title()
        years = self.get_years_of_service()
        return f"안녕하세요, {self.department.value} {title} {self.name}입니다. (근속 {years}년)"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.get_job_title()}) - {self.employee_id}"

class Developer(BaseEmployee):
    """개발자 기본 클래스"""
    
    def __init__(self, name: str, annual_salary: int, tech_stack: List[str],
                 experience_years: int, specialization: str = "Full Stack"):
        super().__init__(name, annual_salary, Department.ENGINEERING, self._determine_level(experience_years))
        self.tech_stack = tech_stack
        self.experience_years = experience_years
        self.specialization = specialization
        self.projects: List[str] = []
        self.code_reviews_completed = 0
        self.bugs_fixed = 0
        self.features_delivered = 0
    
    @staticmethod
    def _determine_level(years: int) -> EmployeeLevel:
        """경력에 따른 레벨 결정"""
        if years < 1:
            return EmployeeLevel.JUNIOR
        elif years < 5:
            return EmployeeLevel.SENIOR
        else:
            return EmployeeLevel.LEAD
    
    def get_job_title(self) -> str:
        return f"{self.specialization} {self.level.korean_name} 개발자"
    
    def calculate_performance_bonus(self) -> int:
        """개발자 성과급 계산"""
        base_bonus = self.annual_salary // 12  # 월급 1개월분
        
        # 프로젝트 완료 보너스
        project_bonus = len(self.projects) * 200000
        
        # 코드 리뷰 보너스
        review_bonus = self.code_reviews_completed * 10000
        
        # 버그 수정 보너스
        bug_bonus = self.bugs_fixed * 20000
        
        # 기능 개발 보너스
        feature_bonus = self.features_delivered * 100000
        
        total_bonus = base_bonus + project_bonus + review_bonus + bug_bonus + feature_bonus
        
        # 최대 연봉의 50%까지
        max_bonus = self.annual_salary // 2
        return min(total_bonus, max_bonus)
    
    def add_project(self, project_name: str) -> None:
        """프로젝트 추가"""
        self.projects.append(project_name)
        print(f"{self.name}님이 '{project_name}' 프로젝트에 참여합니다.")
    
    def complete_code_review(self, reviewer: str) -> None:
        """코드 리뷰 완료"""
        self.code_reviews_completed += 1
        print(f"{self.name}님이 {reviewer}님의 코드 리뷰를 완료했습니다.")
    
    def fix_bug(self, bug_description: str) -> None:
        """버그 수정"""
        self.bugs_fixed += 1
        print(f"{self.name}님이 버그를 수정했습니다: {bug_description}")
    
    def deliver_feature(self, feature_name: str) -> None:
        """기능 개발 완료"""
        self.features_delivered += 1
        print(f"{self.name}님이 '{feature_name}' 기능을 완료했습니다.")

class JuniorDeveloper(Developer):
    """주니어 개발자"""
    
    def __init__(self, name: str, annual_salary: int, tech_stack: List[str], 
                 experience_years: int = 0):
        super().__init__(name, annual_salary, tech_stack, experience_years)
        self.level = EmployeeLevel.JUNIOR
        self.mentor: Optional['SeniorDeveloper'] = None
        self.training_completed = 0
    
    def assign_mentor(self, mentor: 'SeniorDeveloper') -> None:
        """멘토 배정"""
        self.mentor = mentor
        mentor.add_mentee(self)
        print(f"{mentor.name}님이 {self.name}님의 멘토가 되었습니다.")
    
    def complete_training(self, training_name: str) -> None:
        """교육 이수"""
        self.training_completed += 1
        print(f"{self.name}님이 '{training_name}' 교육을 이수했습니다.")
    
    def calculate_performance_bonus(self) -> int:
        """주니어 개발자 성과급 (교육 이수 추가)"""
        base_bonus = super().calculate_performance_bonus()
        training_bonus = self.training_completed * 50000
        return base_bonus + training_bonus

class SeniorDeveloper(Developer):
    """시니어 개발자"""
    
    def __init__(self, name: str, annual_salary: int, tech_stack: List[str], 
                 experience_years: int):
        super().__init__(name, annual_salary, tech_stack, experience_years)
        self.level = EmployeeLevel.SENIOR
        self.mentees: List[JuniorDeveloper] = []
        self.architecture_designs = 0
        self.tech_talks_given = 0
    
    def add_mentee(self, mentee: JuniorDeveloper) -> None:
        """멘티 추가"""
        if mentee not in self.mentees:
            self.mentees.append(mentee)
            print(f"{self.name}님이 {mentee.name}님을 멘토링합니다.")
    
    def conduct_tech_talk(self, topic: str) -> None:
        """기술 발표"""
        self.tech_talks_given += 1
        print(f"{self.name}님이 '{topic}' 주제로 기술 발표를 했습니다.")
    
    def design_architecture(self, system_name: str) -> None:
        """아키텍처 설계"""
        self.architecture_designs += 1
        print(f"{self.name}님이 '{system_name}' 아키텍처를 설계했습니다.")
    
    def calculate_performance_bonus(self) -> int:
        """시니어 개발자 성과급 (멘토링, 설계 추가)"""
        base_bonus = super().calculate_performance_bonus()
        mentoring_bonus = len(self.mentees) * 100000
        architecture_bonus = self.architecture_designs * 300000
        talk_bonus = self.tech_talks_given * 50000
        return base_bonus + mentoring_bonus + architecture_bonus + talk_bonus

class Manager(BaseEmployee, ABC):
    """관리자 추상 클래스"""
    
    def __init__(self, name: str, annual_salary: int, department: Department, 
                 team_size: int, level: EmployeeLevel = EmployeeLevel.MANAGER):
        super().__init__(name, annual_salary, department, level)
        self.team_size = team_size
        self.meetings_conducted = 0
        self.team_projects: List[str] = []
        self.budget_managed = 0
    
    def conduct_team_meeting(self, agenda: str) -> None:
        """팀 미팅 진행"""
        self.meetings_conducted += 1
        print(f"{self.name}님이 '{agenda}' 안건으로 팀 미팅을 진행합니다.")
    
    def start_team_project(self, project_name: str, budget: int = 0) -> None:
        """팀 프로젝트 시작"""
        self.team_projects.append(project_name)
        self.budget_managed += budget
        print(f"{self.name}님의 팀이 '{project_name}' 프로젝트를 시작합니다. (예산: {budget:,}원)")
    
    def calculate_performance_bonus(self) -> int:
        """관리자 성과급 계산"""
        base_bonus = self.annual_salary // 12
        
        # 팀 규모에 따른 보너스
        team_bonus = self.team_size * 100000
        
        # 프로젝트 관리 보너스
        project_bonus = len(self.team_projects) * 500000
        
        # 미팅 진행 보너스
        meeting_bonus = self.meetings_conducted * 20000
        
        # 예산 관리 보너스 (관리 예산의 1%)
        budget_bonus = int(self.budget_managed * 0.01)
        
        return base_bonus + team_bonus + project_bonus + meeting_bonus + budget_bonus

class DevelopmentManager(Manager):
    """개발팀 매니저"""
    
    def __init__(self, name: str, annual_salary: int, tech_focus: str, team_size: int):
        super().__init__(name, annual_salary, Department.ENGINEERING, team_size)
        self.tech_focus = tech_focus  # Backend, Frontend, Mobile, DevOps 등
        self.code_quality_score = 85.0
        self.deployment_success_rate = 95.0
    
    def get_job_title(self) -> str:
        return f"{self.tech_focus} 개발팀 매니저"
    
    def improve_code_quality(self, improvement: float) -> None:
        """코드 품질 개선"""
        self.code_quality_score = min(100.0, self.code_quality_score + improvement)
        print(f"코드 품질 점수가 {self.code_quality_score:.1f}점으로 향상되었습니다.")
    
    def track_deployment(self, success: bool) -> None:
        """배포 추적"""
        # 간단한 성공률 계산 (실제로는 더 복잡한 로직 필요)
        if success:
            self.deployment_success_rate = min(100.0, self.deployment_success_rate + 0.1)
            print("배포 성공!")
        else:
            self.deployment_success_rate = max(80.0, self.deployment_success_rate - 1.0)
            print("[X] 배포 실패")

class ExecutiveRole(ABC):
    """임원 역할 추상 클래스"""
    
    @abstractmethod
    def make_strategic_decision(self, decision: str, impact_areas: List[str]) -> None:
        pass
    
    @abstractmethod
    def approve_budget(self, department: str, amount: int) -> bool:
        pass

class CTO(Manager, ExecutiveRole):
    """최고 기술 책임자"""
    
    def __init__(self, name: str, annual_salary: int, tech_vision: str):
        super().__init__(name, annual_salary, Department.ENGINEERING, 50, EmployeeLevel.VP)
        self.tech_vision = tech_vision
        self.strategic_initiatives: List[str] = []
        self.approved_budgets: Dict[str, int] = {}
    
    def get_job_title(self) -> str:
        return "최고 기술 책임자 (CTO)"
    
    def make_strategic_decision(self, decision: str, impact_areas: List[str]) -> None:
        """전략적 의사결정"""
        self.strategic_initiatives.append(decision)
        areas_str = ", ".join(impact_areas)
        print(f"CTO 전략 결정: '{decision}' (영향 영역: {areas_str})")
    
    def approve_budget(self, department: str, amount: int) -> bool:
        """예산 승인"""
        # 간단한 승인 로직 (실제로는 더 복잡)
        if amount <= 100000000:  # 1억원 이하
            self.approved_budgets[department] = amount
            print(f"{department} 예산 {amount:,}원 승인")
            return True
        else:
            print(f"[X] {department} 예산 {amount:,}원 승인 거부 (한도 초과)")
            return False
    
    def set_technology_direction(self, direction: str) -> None:
        """기술 방향성 설정"""
        self.tech_vision = direction
        print(f"새로운 기술 비전: {direction}")

class CEO(BaseEmployee, ExecutiveRole):
    """최고경영자"""
    
    def __init__(self, name: str, annual_salary: int):
        super().__init__(name, annual_salary, Department.FINANCE, EmployeeLevel.CEO)
        self.company_vision = ""
        self.board_meetings = 0
        self.major_decisions: List[str] = []
    
    def get_job_title(self) -> str:
        return "최고경영자 (CEO)"
    
    def calculate_performance_bonus(self) -> int:
        """CEO 성과급 (회사 전체 성과 기반)"""
        # 실제로는 회사 매출, 수익성 등을 고려
        return self.annual_salary // 6  # 연봉의 1/6
    
    def make_strategic_decision(self, decision: str, impact_areas: List[str]) -> None:
        """최고 경영 의사결정"""
        self.major_decisions.append(decision)
        areas_str = ", ".join(impact_areas)
        print(f"CEO 전략 결정: '{decision}' (영향 영역: {areas_str})")
    
    def approve_budget(self, department: str, amount: int) -> bool:
        """최종 예산 승인"""
        # CEO는 모든 예산을 승인할 수 있음
        print(f"CEO가 {department} 예산 {amount:,}원을 최종 승인했습니다.")
        return True
    
    def set_company_vision(self, vision: str) -> None:
        """회사 비전 설정"""
        self.company_vision = vision
        print(f"새로운 회사 비전: {vision}")
    
    def attend_board_meeting(self, agenda: str) -> None:
        """이사회 참석"""
        self.board_meetings += 1
        print(f"CEO가 이사회에 참석합니다. 안건: {agenda}")

class PayrollProcessor:
    """급여 처리 시스템"""
    
    def calculate_monthly_salary(self, employee: BaseEmployee) -> SalaryInfo:
        """월급 계산"""
        base_salary = employee.get_monthly_base_salary()
        performance_bonus = employee.calculate_performance_bonus()
        
        # 직급 수당
        position_allowance = self._calculate_position_allowance(employee.level)
        
        return SalaryInfo(
            employee_id=employee.employee_id,
            base_salary=base_salary,
            performance_bonus=performance_bonus,
            position_allowance=position_allowance
        )
    
    def _calculate_position_allowance(self, level: EmployeeLevel) -> int:
        """직급 수당 계산"""
        allowances = {
            EmployeeLevel.INTERN: 0,
            EmployeeLevel.JUNIOR: 100000,
            EmployeeLevel.SENIOR: 300000,
            EmployeeLevel.LEAD: 500000,
            EmployeeLevel.MANAGER: 800000,
            EmployeeLevel.DIRECTOR: 1200000,
            EmployeeLevel.VP: 1800000,
            EmployeeLevel.CEO: 2500000
        }
        return allowances.get(level, 0)

class PerformanceEvaluator:
    """성과 평가 시스템"""
    
    def __init__(self):
        self.criteria: Dict[str, float] = {}  # 평가 항목과 가중치
    
    def add_evaluation_criteria(self, criterion: str, weight: float) -> None:
        """평가 항목 추가"""
        self.criteria[criterion] = weight
        print(f"평가 항목 추가: {criterion} (가중치: {weight})")
    
    def evaluate(self, employee: BaseEmployee, scores: Dict[str, float]) -> PerformanceReview:
        """성과 평가 실시"""
        if not self.criteria:
            raise ValueError("평가 항목이 설정되지 않았습니다.")
        
        # 가중 평균 계산
        weighted_sum = sum(scores.get(criterion, 0) * weight 
                          for criterion, weight in self.criteria.items())
        total_weight = sum(self.criteria.values())
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        # 등급 결정
        grade = self._determine_grade(overall_score)
        
        # 피드백 생성
        feedback = self._generate_feedback(scores, overall_score)
        
        return PerformanceReview(
            employee_id=employee.employee_id,
            reviewer_id="SYSTEM",  # 실제로는 평가자 ID
            period=f"{datetime.now().year}년 상반기",
            scores=scores,
            overall_score=overall_score,
            grade=grade,
            feedback=feedback
        )
    
    def _determine_grade(self, score: float) -> str:
        """점수에 따른 등급 결정"""
        if score >= 4.5:
            return 'S'
        elif score >= 4.0:
            return 'A'
        elif score >= 3.5:
            return 'B'
        elif score >= 3.0:
            return 'C'
        else:
            return 'D'
    
    def _generate_feedback(self, scores: Dict[str, float], overall: float) -> str:
        """피드백 생성"""
        strong_areas = [k for k, v in scores.items() if v >= 4.0]
        weak_areas = [k for k, v in scores.items() if v < 3.5]
        
        feedback = f"전체 평가: {overall:.1f}점\n"
        
        if strong_areas:
            feedback += f"우수 영역: {', '.join(strong_areas)}\n"
        
        if weak_areas:
            feedback += f"개선 필요 영역: {', '.join(weak_areas)}\n"
        
        return feedback

# 사용 예제와 테스트
if __name__ == "__main__":
    print("=== 한국 기업 HR 관리 시스템 ===")
    
    # 1. 조직 구성
    print("1. 조직 구성:")
    ceo = CEO("김대표", 150000000)
    cto = CTO("박기술", 100000000, "AI 중심 디지털 전환")
    
    # 개발팀 구성
    backend_manager = DevelopmentManager("이백엔드", 70000000, "Backend", 8)
    frontend_manager = DevelopmentManager("김프론트", 65000000, "Frontend", 6)
    
    # 개발자들
    senior_dev1 = SeniorDeveloper("최시니어", 60000000, ["Python", "Go", "Docker"], 7)
    senior_dev2 = SeniorDeveloper("박베테랑", 55000000, ["React", "TypeScript", "AWS"], 6)
    junior_dev1 = JuniorDeveloper("신입김", 40000000, ["Python", "JavaScript"], 0.5)
    junior_dev2 = JuniorDeveloper("새내기이", 38000000, ["React", "Node.js"], 0.3)
    
    # 조직 구조 설정
    ceo.add_subordinate(cto)
    cto.add_subordinate(backend_manager)
    cto.add_subordinate(frontend_manager)
    
    backend_manager.add_subordinate(senior_dev1)
    backend_manager.add_subordinate(junior_dev1)
    frontend_manager.add_subordinate(senior_dev2)
    frontend_manager.add_subordinate(junior_dev2)
    
    # 멘토링 관계 설정
    junior_dev1.assign_mentor(senior_dev1)
    junior_dev2.assign_mentor(senior_dev2)
    
    print("\n2. 조직도:")
    def print_org_chart(employee: BaseEmployee, level: int = 0):
        indent = "  " * level
        print(f"{indent}- {employee}")
        for subordinate in employee.subordinates:
            print_org_chart(subordinate, level + 1)
    
    print_org_chart(ceo)
    
    # 3. 활동 시뮬레이션
    print("\n3. 업무 활동:")
    
    # CEO 활동
    ceo.set_company_vision("AI 기반 혁신 기업")
    ceo.make_strategic_decision("글로벌 시장 진출", ["마케팅", "개발", "인사"])
    ceo.attend_board_meeting("Q3 실적 보고")
    
    # CTO 활동
    cto.set_technology_direction("마이크로서비스 아키텍처로 전환")
    cto.make_strategic_decision("클라우드 네이티브 전환", ["개발", "인프라"])
    cto.approve_budget("Backend팀", 50000000)
    
    # 개발자 활동
    senior_dev1.add_project("사용자 인증 시스템 개선")
    senior_dev1.design_architecture("마이크로서비스 아키텍처")
    senior_dev1.conduct_tech_talk("Go 언어를 활용한 고성능 API 개발")
    
    junior_dev1.complete_training("Docker 기초")
    junior_dev1.complete_training("Kubernetes 입문")
    junior_dev1.add_project("로그 수집 시스템")
    junior_dev1.fix_bug("메모리 누수 문제 해결")
    
    # 4. 급여 계산
    print("\n4. 급여 계산:")
    payroll = PayrollProcessor()
    
    employees = [ceo, cto, backend_manager, senior_dev1, junior_dev1]
    for emp in employees:
        salary_info = payroll.calculate_monthly_salary(emp)
        print(f"\n{emp.name} ({emp.get_job_title()}):")
        print(f"  기본급: {salary_info.base_salary:,}원")
        print(f"  성과급: {salary_info.performance_bonus:,}원") 
        print(f"  직급수당: {salary_info.position_allowance:,}원")
        print(f"  세전총액: {salary_info.total_before_tax:,}원")
        print(f"  세후실수령: {salary_info.net_salary:,}원")
    
    # 5. 성과 평가
    print("\n5. 성과 평가:")
    evaluator = PerformanceEvaluator()
    evaluator.add_evaluation_criteria("기술 역량", 0.4)
    evaluator.add_evaluation_criteria("협업 능력", 0.3)
    evaluator.add_evaluation_criteria("문제 해결", 0.2)
    evaluator.add_evaluation_criteria("리더십", 0.1)
    
    # 시니어 개발자 평가
    evaluation = evaluator.evaluate(senior_dev1, {
        "기술 역량": 4.5,
        "협업 능력": 4.2,
        "문제 해결": 4.3,
        "리더십": 4.0
    })
    
    print(f"\n{senior_dev1.name} 성과 평가:")
    print(f"전체 점수: {evaluation.overall_score:.2f}")
    print(f"등급: {evaluation.grade}")
    print(f"피드백:\n{evaluation.feedback}")
