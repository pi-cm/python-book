# Chapter 13: 상속과 다형성 (Inheritance and Polymorphism)

> **학습 목표**  
> - 상속의 기본 원리와 올바른 활용법 이해
> - 메서드 오버라이딩과 super() 함수 완벽 활용
> - 다중 상속과 MRO(Method Resolution Order) 마스터
> - 추상 클래스와 인터페이스 설계 패턴 습득
> - 다형성을 통한 유연한 코드 작성
> - 한국 기업 계층 구조를 모델링한 종합 프로젝트 구현

---

## 들어가며: 객체 지향의 네 기둥

11장에서 클래스를 만들고 객체를 찍어 내는 법을 배웠습니다. 그럼 "객체 지향스럽게" 코드를 짠다는 건 정확히 뭘까요? 내 프로젝트에 등장하는 인물들을 정하고, 각자의 속성과 기능을 정의하고, 서로 메시지를 주고받게 하는 것. 이걸 잘하기 위해 흔히 네 가지를 신경 쓰라고 말합니다.

- **캡슐화**: 함께 쓰이는 데이터와 기능을 한 객체에 묶고, 내부 상태는 객체가 정한 방법(메서드)으로만 바꾸게 합니다. 11장에서 계좌 잔액을 밖에서 직접 바꾸면 규칙이 다 무너진다고 했고, 프로퍼티로 그 문을 지켰죠. 어디서나 건드릴 수 있던 공유 데이터가 줄어드니 코드가 읽기 쉬워지고 실수할 여지도 줄어듭니다.
- **상속**: 부모 클래스의 속성과 기능을 그대로 물려받고, **다른 부분만** 새로 적습니다. 같은 코드를 반복하지 않게 해 줘요.
- **추상화**: 쓰는 사람이 몰라도 되는 내부 사정은 감추고, 알아야 할 것(이름, 사용법)만 겉으로 드러냅니다.
- **다형성**: 같은 이름의 메시지를 보내도 받는 객체에 따라 알맞게 다르게 동작합니다.

이 장은 이 중 상속, 추상화, 다형성을 차례로 다룹니다. 캡슐화는 상속과 만나는 지점(이름 맹글링)에서 한 번 더 짚어요.

이 장의 코드는 **TDD(Test-Driven Development, 테스트 주도 개발)** 순서로 짜여 있습니다. 각 절이 세 단계로 나뉘어요.

1. **RED**: 만들고 싶은 기능을 먼저 **테스트 코드로** 적습니다. 아직 클래스가 없으니 실행하면 당연히 실패(빨간불)하죠.
2. **GREEN**: 테스트가 통과(초록불)할 만큼만 최소한으로 구현합니다.
3. **REFACTOR**: 테스트가 지켜 주는 상태에서 구조를 더 낫게 다듬습니다.

테스트 코드는 `pytest`라는 외부 도구로 실행합니다. `test_`로 시작하는 함수를 찾아 실행하고, 안의 `assert`가 하나라도 거짓이면 실패로 보고해 줘요. 또 이 장의 GREEN·REFACTOR 코드는 앞 코드에서 만든 클래스와 `import`를 이어서 쓰는 경우가 많습니다. 13.1절부터 13.4절까지는 GREEN·REFACTOR 코드를 한 파일에 차례로 이어 붙여 실행하세요(13.2절은 13.1절 REFACTOR의 `BaseEmployee`를 씁니다). 13.5절의 HR 시스템은 그 절 안의 코드만으로 실행됩니다.

## 13.1 상속 기초 - TDD로 시작하기

### RED Phase: 상속 요구사항 테스트

한국 회사의 직원 구조를 모델로 삼습니다. 모든 직원(`Employee`)에게는 이름, 부서, 급여가 있고, 개발자(`Developer`)와 관리자(`Manager`)는 직원이면서 저마다 특별한 정보를 더 가집니다. 아래 테스트는 "이렇게 동작해야 한다"는 요구사항을 코드로 적은 거예요.

```python
# test_inheritance_basics.py
import pytest
from abc import ABC, abstractmethod

def test_basic_inheritance():
    """기본 상속 관계 테스트"""
    # 이 테스트들은 처음엔 실패해야 함
    
    # 1. 부모 클래스 Employee가 존재해야 함
    employee = Employee("김철수", "개발팀", 35_000_000)
    assert employee.name == "김철수"
    assert employee.department == "개발팀" 
    assert employee.salary == 35_000_000
    
    # 2. 자식 클래스 Developer가 Employee를 상속해야 함
    dev = Developer("이영희", "개발팀", 40_000_000, "Python")
    assert isinstance(dev, Employee)  # is-a 관계
    assert dev.programming_language == "Python"
    
    # 3. 메서드 상속이 작동해야 함
    assert "김철수" in employee.introduce()
    assert "이영희" in dev.introduce()

def test_method_overriding():
    """메서드 오버라이딩 테스트"""
    
    # Manager는 introduce 메서드를 오버라이드해야 함
    manager = Manager("박부장", "영업팀", 60_000_000, 5)
    intro = manager.introduce()
    
    assert "부장" in intro or "관리자" in intro
    assert "5명" in intro
    assert manager.calculate_bonus() > 0

def test_super_usage():
    """super() 함수 사용 테스트"""
    
    # 자식 클래스에서 부모의 메서드를 확장해야 함
    senior_dev = SeniorDeveloper("최시니어", "개발팀", 55_000_000, "Java", 7)
    
    # 부모의 소개에 경력이 추가되어야 함
    intro = senior_dev.introduce()
    assert "최시니어" in intro
    assert "7년" in intro
    
    # 급여 계산이 확장되어야 함
    assert senior_dev.calculate_total_compensation() > senior_dev.salary

# 이 시점에서 이 테스트들은 모두 실패해야 함 (RED)
```

`isinstance(dev, Employee)`가 `True`여야 한다는 줄이 상속의 핵심입니다. 개발자는 **직원이다(is-a)**. 그러니 직원이 할 수 있는 일은 개발자도 할 수 있어야 하죠. 지금 이 파일을 `pytest`로 실행하면 `Employee`라는 이름이 없어서 `NameError`로 모두 실패합니다. 이게 RED예요.

### GREEN Phase: 최소 구현으로 테스트 통과

`class Developer(Employee):`처럼 클래스 이름 뒤 괄호에 부모를 적으면 상속이 됩니다. 부모 쪽을 **부모 클래스**(상위 클래스, 기반 클래스), 물려받는 쪽을 **자식 클래스**(하위 클래스, 파생 클래스)라고 불러요. 아래 코드에서 볼 도구는 두 가지입니다.

- **메서드 오버라이딩(overriding)**: 부모에게 있는 메서드를 자식이 같은 이름으로 다시 정의하면, 자식 객체에서는 자식 것이 쓰입니다. `Manager.introduce()`는 부모의 소개말을 통째로 자기 것으로 바꿨어요.
- **`super()`**: "부모 쪽의 그 메서드"를 부릅니다. `Developer.__init__`은 이름·부서·급여 저장을 부모의 `__init__`에 맡기고 자기만의 `programming_language`만 더 저장해요. `Developer.introduce()`는 부모의 소개말을 받아 뒤에 한 문장을 **덧붙입니다**. 통째로 바꾸는 대신 확장하는 거죠.

```python
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
```

시니어 개발자의 소개말이 재미있습니다. `안녕하세요, 개발팀 최시니어입니다. 주로 Java 언어를 사용합니다. 7년의 경력을 가지고 있습니다.` 세 문장이 각각 `Employee`, `Developer`, `SeniorDeveloper`에서 왔어요. `SeniorDeveloper.introduce()`가 `super().introduce()`로 `Developer`의 것을 부르고, 그 안에서 다시 `super().introduce()`로 `Employee`의 것을 불렀기 때문입니다. 할아버지 → 아버지 → 나 순서로 한 문장씩 이어 붙인 셈이죠. 보너스도 같은 방식으로 기본 보너스 위에 프로젝트 수당(개발자), 팀원 수당(관리자)을 얹습니다.

`SeniorDeveloper`에는 `add_project()`를 만들지 않았는데 `senior.add_project(...)`가 잘 동작하는 것도 보세요. 메서드를 찾을 때 파이썬은 먼저 객체의 클래스(`SeniorDeveloper`)를 보고, 없으면 부모(`Developer`), 그다음 그 부모(`Employee`)로 올라가며 찾습니다. 맨 처음 찾은 것을 쓰고요. 오버라이딩이 동작하는 원리도 바로 이 "가까운 쪽부터 찾기"입니다.

> **Q. 오버라이딩 말고 오버로딩이라는 말도 들었는데, 같은 건가요?**
> 다릅니다. **오버로딩(overloading)** 은 같은 이름의 메서드를 매개변수의 개수나 타입만 다르게 여러 개 정의하는 거예요. 자바나 C++은 이걸 지원하지만 파이썬은 지원하지 않습니다. 같은 이름으로 함수를 두 번 정의하면 앞의 것은 사라지고 **나중 것만** 남아요. `def f(a)` 다음에 `def f(a, b)`를 정의하고 `f(1)`을 부르면 `b`가 없다는 `TypeError`가 납니다. 파이썬에서는 대신 기본값 매개변수(`def f(a, b=None)`)를 쓰거나, 타입에 따라 다른 함수를 골라 주는 `functools.singledispatch`를 씁니다. 13.4절 REFACTOR에서 `singledispatch`를 직접 써 봅니다.

### REFACTOR Phase: 상속 관계 개선

GREEN 단계의 코드는 잘 동작하지만 아쉬운 점이 있습니다. `Employee`로 객체를 바로 만들 수 있으니 "직책이 없는 그냥 직원"이 생길 수 있고, 자식 클래스가 꼭 만들어야 할 메서드가 무엇인지 어디에도 적혀 있지 않아요. 리팩터링 버전은 세 가지를 바꿉니다.

- `BaseEmployee(ABC)`에 `@abstractmethod`를 붙여 `get_job_title()`과 `calculate_specific_bonus()`를 **자식이 반드시 구현해야 하는 약속**으로 만듭니다. 이 약속을 지키지 않은 클래스로는 객체를 만들 수 없어요(13.3절에서 자세히 봅니다).
- `introduce()`와 `calculate_total_bonus()`는 부모가 전체 흐름을 쥐고, 달라지는 한 조각만 자식의 메서드를 불러 채웁니다. 이런 구조를 **템플릿 메서드 패턴**이라고 해요. 소개말의 틀은 모든 직원이 같고 직책만 다르니, 직책 부분만 자식에게 맡기는 거죠.
- 직급은 문자열 대신 `Enum`으로 정해진 값만 쓰게 하고, `Protocol`로 "평가할 수 있는 객체"가 갖춰야 할 메서드를 적어 둡니다.

```python
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
```

`self._performance_score`처럼 밑줄 하나로 시작하는 이름은 11장에서 본 대로 "안에서만 쓰는 값"이라는 약속입니다. 상속이 끼면 밑줄 **두 개**도 의미가 생깁니다. 부모와 자식이 우연히 같은 이름의 내부 변수를 쓰면, 자식이 부모의 값을 덮어써서 부모의 메서드가 엉뚱하게 동작할 수 있거든요. 이름을 `__`로 시작하게 지으면 파이썬이 그 이름 앞에 클래스 이름을 몰래 붙여 바꿔 줍니다. 이걸 **이름 맹글링(name mangling)** 이라고 해요.

```python
class Parent:
    def __init__(self):
        self.__secret = "부모가 쓰는 값"

class Child(Parent):
    def __init__(self):
        super().__init__()
        self.__secret = "자식이 쓰는 값"   # 부모 값을 덮어쓰지 않는다

print(Child().__dict__)
# {'_Parent__secret': '부모가 쓰는 값', '_Child__secret': '자식이 쓰는 값'}
```

두 클래스 모두 `self.__secret`이라고 썼지만 객체 안에는 `_Parent__secret`과 `_Child__secret`이 따로 저장됐습니다. 클래스 안에서는 `self.__secret`으로 부르면 자기 것이 찾아지고, 밖에서 `obj.__secret`으로 부르면 그런 이름이 없다는 `AttributeError`가 나요. 그렇다고 완전히 숨겨지는 건 아닙니다. `obj._Parent__secret`처럼 바뀐 이름을 알면 꺼낼 수 있으니, 맹글링은 자물쇠라기보다 **상속 계층에서 이름이 부딪히지 않게 하는 장치**로 이해하세요. 평소에는 밑줄 하나로 충분합니다.

## 13.2 다중 상속과 MRO (Method Resolution Order)

### RED Phase: 다중 상속 테스트 시나리오

팀 리드는 코드도 짜고 팀도 이끕니다. 개발자이면서 관리자인 거죠. 파이썬은 `class TeamLead(Developer, Manager):`처럼 부모를 **여러 개** 둘 수 있습니다. 이걸 다중 상속이라고 해요. 그런데 `Developer`와 `Manager`가 둘 다 `get_job_title()`을 갖고 있다면 팀 리드는 누구의 것을 써야 할까요? 게다가 두 부모가 같은 조상 `BaseEmployee`를 두고 있으니, 족보를 그리면 마름모 모양이 됩니다. 이 모양에서 생기는 "누구 것을 쓰나" 문제를 **다이아몬드 문제**라고 해요. 테스트는 이 순서가 예측 가능해야 한다고 요구합니다.

```python
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
```

### GREEN Phase: 다중 상속 구현

파이썬은 다이아몬드 문제를 **MRO(Method Resolution Order, 메서드 탐색 순서)** 로 풉니다. 클래스마다 "메서드를 찾을 때 어떤 순서로 클래스들을 뒤질지"를 한 줄로 정해 둔 목록이에요. C3 선형화라는 규칙으로 만드는데, 지켜지는 원칙은 세 가지입니다.

1. 자식은 항상 부모보다 먼저 나온다.
2. 부모들은 `class TeamLead(Developer, Manager)`에 **적은 순서대로**(왼쪽부터) 나온다.
3. 어떤 클래스도 두 번 나오지 않는다. 공통 조상은 자식들이 다 나온 뒤 한 번만 나온다.

여기서 꼭 알아야 할 사실이 하나 있습니다. `super()`는 "내 부모"가 아니라 **"MRO에서 내 다음 차례"** 를 부른다는 거예요. 작은 예제로 확인해 보죠.

```python
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
```

`B`의 부모는 `A`인데, `D` 객체에서 `B`의 `super().hello()`는 `A`가 아니라 `C`로 갔습니다. `D`의 MRO에서 `B` 다음 차례가 `C`이기 때문이에요. 덕분에 `A`의 `hello()`는 딱 한 번만 실행됩니다. 마지막 줄의 `object`는 파이썬의 모든 클래스가 최종적으로 물려받는 조상이고요.

이제 `TeamLead`를 봅시다. 아래 코드는 `__init__`에서 `super()` 대신 `BaseEmployee.__init__(self, ...)`를 직접 불렀습니다. `Developer.__init__`과 `Manager.__init__`이 받는 인자가 서로 달라서 `super()` 사슬을 따라가기 곤란하니, 공통 조상의 초기화만 직접 하고 나머지 속성은 손으로 채운 거예요. 반면 `introduce()`의 `super()`는 MRO를 따라갑니다.

```python
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
```

출력되는 MRO는 `['TeamLead', 'Developer', 'Manager', 'BaseEmployee', 'ABC', 'object']`입니다. 세 원칙 그대로죠. 자식 `TeamLead`가 맨 앞, 적은 순서대로 `Developer`, `Manager`, 공통 조상 `BaseEmployee`는 그 둘이 다 나온 뒤 한 번만 나옵니다. 그래서 `TeamLead`가 `get_job_title()`을 직접 정의하지 않았다면 `Developer`의 것이 쓰였을 거예요. 두 부모의 방식이 모두 필요한 보너스 계산은 `TeamLead`가 직접 오버라이딩해서 둘을 합쳤습니다. 부모들이 부딪히는 곳은 자식이 직접 정리해 주는 게 가장 확실한 해결책입니다.

### REFACTOR Phase: 믹스인 패턴으로 개선

다중 상속이 이렇게 헷갈린다면 아예 안 쓰는 게 나을까요? 실무에서는 다중 상속을 **믹스인(mixin)** 이라는 제한된 모양으로 많이 씁니다. 믹스인은 혼자서는 의미가 없고, 다른 클래스에 기능 하나를 섞어 넣기 위해 만든 작은 클래스예요. "기술 관리 기능", "리더십 관리 기능"처럼 이름 그대로 한 가지 능력만 담습니다. 아이스크림에 토핑을 얹듯 필요한 믹스인만 골라 붙이는 거죠.

믹스인이 제대로 동작하려면 MRO의 모든 클래스가 **협력**해야 합니다. 아래 믹스인들의 `__init__`이 모두 `*args, **kwargs`를 받아 `super().__init__(*args, **kwargs)`로 넘기는 이유예요. 각자 자기 몫의 속성만 만들고 나머지 인자는 MRO의 다음 차례에게 그대로 넘겨서, 사슬의 끝까지 모든 `__init__`이 한 번씩 실행되게 하는 겁니다. 사슬 중간의 어느 한 클래스라도 `super().__init__()`을 부르지 않으면 그 뒤 차례의 초기화는 실행되지 않아요. 그래서 믹스인은 보통 클래스 정의에서 기반 클래스보다 **왼쪽에** 적고, 기반 클래스의 `__init__`도 사슬을 이어 주도록 만듭니다. 아래 `ModernTeamLead`가 믹스인 셋을 앞에, `BaseEmployee`를 맨 뒤에 적은 이유이고, 13.1절 REFACTOR의 `BaseEmployee.__init__` 첫 줄이 `super().__init__()`인 이유이기도 해요.

```python
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
```

`ModernTeamLead`는 직원이라는 뼈대(`BaseEmployee`)에 기술, 리더십, 멘토링 세 토핑을 얹었습니다. 나중에 "멘토링은 하지만 리더는 아닌" 시니어 개발자가 필요하면 `MentorshipMixin`만 골라 붙이면 되죠. 기능을 작은 단위로 나눠 두면 이렇게 조합이 자유로워집니다.

상속만이 코드를 재사용하는 방법은 아닙니다. 11장에서 "자동차는 객체인데 바퀴도 객체 아니냐"는 질문이 있었죠. 자동차는 엔진의 한 종류가 아니라 엔진을 **가지고** 있습니다. 이렇게 다른 객체를 속성으로 품어서 그 기능을 빌려 쓰는 것을 **조합(composition)** 이라고 해요.

```python
class Engine:
    def start(self) -> str:
        return "부릉"

class Car:
    def __init__(self):
        self.engine = Engine()   # 차는 엔진을 '가지고' 있다 (has-a)

    def start(self) -> str:
        return f"시동: {self.engine.start()}"

print(Car().start())             # 시동: 부릉
```

둘을 고르는 기준은 간단합니다. "A는 B다(is-a)"가 자연스러우면 상속, "A는 B를 가진다(has-a)"가 자연스러우면 조합이에요. 개발자는 직원이니 상속, 자동차는 엔진을 가지니 조합입니다. 헷갈릴 때는 조합 쪽이 대체로 안전합니다. 상속은 부모가 바뀌면 모든 자식이 영향을 받지만, 조합은 부품만 갈아 끼우면 되거든요. 11장 끝의 학습 팁이 "상속보다는 컴포지션"이라고 한 이유입니다.

## 13.3 추상 클래스와 인터페이스

### RED Phase: 추상 클래스 테스트

스마트폰을 떠올려 보세요. 전원 버튼을 누르면 화면이 켜지고, 볼륨 버튼을 누르면 소리가 커집니다. 우리는 그 뒤에서 반도체가 무슨 일을 하는지, 저항과 콘덴서가 어떻게 연결됐는지 몰라도 스마트폰을 잘 씁니다. 겉으로 드러난 버튼, 즉 **인터페이스**만 알면 되니까요. 노트북 키보드도, 자동차의 가속 페달과 브레이크도 마찬가지예요. 페달을 밟으면 빨라지고 브레이크를 밟으면 멈춘다는 것만 알면 됩니다.

> **Q. 그런데 그 뒤의 원리를 굳이 몰라도 되나요?**
> 네, 그게 핵심이에요. 기술이 발전할수록 알아야 할 정보가 너무 많아졌습니다. 모든 부품의 원리를 알아야 쓸 수 있다면 아무도 스마트폰을 못 쓰겠죠. 쓰는 사람에게 필요한 건 "이 기계가 안전하고, 내가 원하는 기능을 해 준다"는 믿음뿐입니다. 내부를 손대지 않고도 대부분의 사람이 원하는 걸 얻어 갈 수 있다면 **추상화**가 잘된 거예요. 코드에서는 동작을 잘 이해하고 구조를 설계한 다음, 이름을 잘 짓고 docstring으로 적당한 설명과 예제를 붙이는 것이 추상화의 시작입니다.

결제를 예로 들어 봅시다. 쇼핑몰 입장에서는 신용카드든 계좌이체든 카카오페이든 "이 금액을 결제해 줘(`process_payment`)"라고 부를 수만 있으면 됩니다. 각 결제 수단 안에서 무슨 일이 벌어지는지는 몰라도 되죠. 아래 테스트는 이 공통 인터페이스를 요구합니다. 첫 번째 요구가 눈에 띄는데, 공통 틀인 `PaymentProcessor`로는 객체를 **만들 수 없어야** 한다는 거예요. "그냥 결제 수단"이라는 건 실제로 존재하지 않으니까요.

```python
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
```

### GREEN Phase: 추상 클래스 구현

파이썬에서 인터페이스를 적는 방법은 두 가지입니다.

- **추상 베이스 클래스(ABC)**: `abc` 모듈의 `ABC`를 상속하고, 자식이 꼭 만들어야 할 메서드에 `@abstractmethod`를 붙입니다. 추상 메서드가 하나라도 남아 있는 클래스로 객체를 만들려 하면 `TypeError: Can't instantiate abstract class ...`가 나요. 자식 클래스가 **명시적으로 상속**해야 하니 "이 가문의 일원"임을 선언하는 방식입니다. 추상 메서드가 아닌 일반 메서드에는 공통 코드를 넣어 물려줄 수도 있어요.
- **프로토콜(Protocol)**: `typing.Protocol`을 상속해 "이런 메서드들이 있어야 한다"는 **모양**만 적습니다. 실제 클래스는 프로토콜을 상속하지 않아도, 그 메서드들을 갖추기만 하면 같은 종류로 인정돼요. `@runtime_checkable`을 붙이면 `isinstance(obj, PaymentMethod)`로 확인할 수 있는데, 이때는 **메서드 이름이 있는지만** 봅니다. 매개변수 개수나 타입까지 맞는지는 검사하지 않으니, 그건 mypy 같은 타입 검사 도구의 몫이에요.

아래 코드는 둘을 함께 씁니다. `PaymentProcessor`는 ABC로 일일 한도 검사(`validate_payment`)와 거래 기록(`record_transaction`) 같은 공통 코드를 물려주고, 결제 방식마다 다른 `process_payment`와 `validate_payment_details`는 추상 메서드로 남겨 자식에게 맡깁니다. `PaymentMethod`는 프로토콜로 바깥에서 기대하는 모양을 적어 두었고요.

```python
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
```

세 처리기의 `process_payment()`는 모양이 거의 같습니다. 공통 유효성 검사 → 결제 수단별 정보 검사 → 실제 결제 → 거래 기록. 다른 건 "결제 수단별 정보 검사"와 성공 확률뿐이에요. 카드는 카드 정보가, 계좌이체는 계좌 정보가, 카카오페이는 로그인이 필요하죠. 공통 부분은 부모가 한 번만 갖고 있고, 달라지는 부분만 자식이 채웠습니다. 카드 번호를 `card_number[-4:]`로 마지막 네 자리만 저장하고 CVV를 `"***"`로 바꿔 두는 부분도 눈여겨보세요. 객체가 민감한 정보를 아예 품지 않는 것도 캡슐화의 좋은 습관입니다.

### REFACTOR Phase: 고급 패턴 적용

이제 이 결제 처리기들을 실제 서비스처럼 묶어 봅니다. 여기 등장하는 이름들은 많은 개발자가 반복해서 써 온 설계 방법, 즉 **디자인 패턴**의 이름이에요.

- **팩토리 패턴** (`PaymentFactory`): `"신용카드"` 같은 문자열을 받아 알맞은 클래스의 객체를 만들어 줍니다. 딕셔너리 `_processors`의 값이 클래스 자체라는 점이 재미있죠. 파이썬에서는 클래스도 객체라서 딕셔너리에 담았다가 `processor_class(provider)`처럼 꺼내 부를 수 있습니다.
- **전략 패턴과 폴백** (`PaymentOrchestrator`): 여러 결제 수단을 목록으로 들고 있다가 첫 번째부터 시도하고, 실패하면 다음 수단으로 넘어갑니다. 오케스트레이터는 각 처리기가 카드인지 카카오페이인지 몰라도 `process_payment()`만 부르면 돼요. 앞 절에서 만든 공통 인터페이스 덕분입니다.
- **결과 객체** (`PaymentResult`): 성공 여부, 거래번호, 메시지를 `@dataclass`로 한데 묶어 돌려줍니다. `True`/`False` 하나보다 훨씬 많은 정보를 전할 수 있어요.
- **컨텍스트 매니저** (`payment_session`): `@contextmanager`를 붙인 함수에서 `yield` 앞은 `__enter__`, 뒤의 `finally`는 `__exit__` 역할을 합니다. 11장처럼 클래스를 만들지 않고도 `with` 문을 쓸 수 있는 지름길이에요.

```python
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
```

결제 성공 여부는 `random`으로 정하기 때문에 실행할 때마다 결과가 다를 수 있습니다. 대부분은 첫 번째 수단(카드)에서 바로 성공해서 "결제 시도 1/3"만 보이고, 카드 쪽 거래만 1건 기록됩니다. 가끔 카드가 실패하면 "결제 시도 2/3"으로 넘어가 계좌이체가 결제를 이어받는 폴백을 볼 수 있어요. 여러 번 실행해 보세요. 거래번호도 시각을 바탕으로 만드니 매번 바뀝니다.

## 13.4 다형성과 덕 타이핑

### RED Phase: 다형성 테스트

**다형성(polymorphism)** 은 "여러(poly) 모양(morph)"이라는 뜻입니다. 같은 이름의 메서드나 연산자를 클래스마다 다르게 구현해서, 같은 메시지를 보내도 받는 객체에 따라 결과가 달라지는 성질이에요. 동물 클래스에 `sound()`가 있고 고양이 클래스가 그걸 오버라이딩해 "야옹~"을 출력하게 하면, `animal.sound()`와 `cat.sound()`는 같은 호출인데 다른 소리를 냅니다. 11장에서 `+`가 숫자와 문자열, `KoreanMoney`에서 각각 다르게 동작했던 것도 다형성이죠.

다형성의 진짜 힘은 **부르는 쪽 코드**에서 나옵니다. 동물이 몇 종류든 `for animal in animals: animal.make_sound()` 한 줄로 끝나요. 나중에 오리 클래스가 추가돼도 이 반복문은 한 글자도 고칠 필요가 없습니다.

파이썬은 여기서 한 걸음 더 나갑니다. "오리처럼 걷고 오리처럼 꽥꽥거리면 그건 오리다"라는 말에서 따온 **덕 타이핑(duck typing)** 이에요. 파이썬은 객체가 어떤 클래스를 상속했는지 묻지 않고, 필요한 메서드가 **있기만 하면** 그냥 부릅니다. 두 번째 테스트의 파일 같은 객체들은 공통 부모가 없어도 `read()`, `write()`, `close()`만 있으면 같은 방식으로 쓸 수 있어야 한다는 요구예요.

```python
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
```

### GREEN Phase: 다형성 구현

코드는 두 부분입니다. 앞부분의 `Dog`, `Cat`, `Bird`는 같은 부모 `Animal`을 상속하고 `make_sound()`와 `get_species()`를 각자 오버라이딩한 **상속 기반 다형성**이에요. 뒷부분의 `StringFile`, `NetworkFile`, `DatabaseFile`은 서로 아무 관계가 없는 클래스인데 메서드 이름만 맞춘 **덕 타이핑**입니다. `FileInterface` 프로토콜은 그 모양을 문서처럼 적어 두었을 뿐, 세 클래스 중 누구도 상속하지 않아요.

맨 위의 `josa()`는 출력 문장을 자연스럽게 만드는 작은 도우미입니다. "바둑이가"와 "나비가"처럼 이름마다 이/가, 을/를이 달라지는데, 한글 음절은 유니코드에서 '가'부터 받침 순서대로 28개씩 놓여 있어서 `(ord(글자) - ord('가')) % 28`이 0이면 받침이 없는 글자예요.

```python
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
```

`animal_chorus()`의 출력을 보면 같은 `animal.make_sound()` 호출에서 "멍멍!", "야옹~", "짹짹!"이 차례로 나오고, `get_species()`도 "진돗개 개", "러시안블루 고양이", "새"처럼 각자 다르게 답합니다. 함수 안에는 `if`로 종류를 가르는 코드가 하나도 없는데 말이죠. `feed_animals()`도 모든 동물을 똑같이 다룹니다.

반면 `animal_exercise_session()`은 `isinstance()`로 종류를 확인해서 개에게는 `fetch()`, 고양이에게는 `hunt()`를 시킵니다. 각 동물에게만 있는 고유 행동을 부르려면 어쩔 수 없는 부분이에요. 다만 이런 `isinstance()` 분기가 늘어날수록 새 동물이 생길 때마다 함수를 고쳐야 하니, 공통으로 부를 수 있는 일이라면 `exercise()` 같은 메서드를 부모에 두고 각자 오버라이딩하게 하는 편이 다형성을 더 잘 살리는 설계입니다.

`process_files()`는 메모리, 네트워크, 데이터베이스라는 전혀 다른 대상을 똑같이 `read() → write() → close()` 순서로 처리했습니다. 파이썬 표준 라이브러리도 이 방식을 많이 씁니다. `json.dump()`가 실제 파일뿐 아니라 메모리 속 `io.StringIO`에도 쓸 수 있는 건, `write()` 메서드가 있는 객체면 무엇이든 받기 때문이에요.

### REFACTOR Phase: 고급 다형성 패턴

다형성을 넓히는 도구 세 가지를 더 봅니다.

- **제네릭(`Generic[T]`)**: `Container[Animal]`처럼 "무엇을 담는 상자인지"를 타입으로 적을 수 있게 합니다. 실행 동작은 그대로이고, 타입 검사 도구와 코드를 읽는 사람에게 정보를 주는 장치예요.
- **싱글 디스패치(`@singledispatch`)**: 첫 번째 인자의 **타입에 따라** 다른 함수가 실행되게 합니다. `@process_korean_data.register` 아래 함수의 타입 힌트(`data: str`, `data: int` …)를 보고 알맞은 것을 골라 줘요. 13.1절의 Q&A에서 말한, 파이썬에 없는 오버로딩을 대신하는 방법입니다.
- **여러 프로토콜**: `KoreanButton`은 `Drawable`, `Movable`, `Interactive` 세 프로토콜의 메서드를 모두 갖췄고, `KoreanLabel`은 그중 일부만 갖췄습니다. 함수마다 자기가 필요한 프로토콜만 요구하니, 객체는 갖춘 능력만큼 여러 곳에서 쓰일 수 있어요.

```python
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
```

싱글 디스패치 출력을 보면 같은 `process_korean_data()` 호출인데 문자열은 "한국어 텍스트 처리: '안녕하세요' (5글자)", 정수는 "한국식 숫자 표기: 1,000,000원", 리스트와 딕셔너리는 또 각자의 방식으로 처리됩니다. 등록되지 않은 타입이 들어오면 맨 위의 기본 함수가 "알 수 없는 데이터 타입"이라고 답하고요. 마지막 부분의 `hasattr(e, 'on_click')`은 덕 타이핑을 그대로 코드로 옮긴 겁니다. "클릭을 받을 수 있는가?"를 클래스 이름이 아니라 메서드가 있는지로 판단하죠.

## 13.5 실전 프로젝트: 한국 기업 HR 관리 시스템

### 프로젝트 개요
TDD 방법론을 활용하여 한국 기업의 복잡한 인사관리 시스템을 구축합니다. 상속, 다형성, 추상 클래스의 모든 개념을 종합적으로 활용합니다.

### RED Phase: 시스템 요구사항 테스트

테스트는 세 가지를 요구합니다. 대표 → CTO → 개발 매니저 → 개발자로 이어지는 **보고 체계**가 만들어져야 하고, 직원 종류가 무엇이든 같은 `PayrollProcessor`로 **급여를 계산**할 수 있어야 하며, 가중치를 둔 항목들로 **성과를 평가**해 S~D 등급을 매길 수 있어야 해요. 두 번째 요구가 이 장 전체의 요약입니다. 급여 처리기는 상대가 CEO인지 신입인지 묻지 않고 같은 메서드를 부를 뿐인데, 결과는 직급마다 달라야 하죠. 상속과 다형성이 함께 일하는 장면입니다.

```python
# test_hr_system.py
import pytest
from datetime import datetime, date

def test_employee_hierarchy():
    """직원 계층 구조 테스트"""
    # 다양한 직급의 직원들이 올바른 계층을 형성해야 함
    ceo = CEO("김대표", 120000000)
    cto = CTO("박기술", 80000000, "Engineering")
    dev_manager = DevelopmentManager("이개발", 60000000, "Backend", 10)
    senior_dev = SeniorDeveloper("최시니어", 50000000, ["Python", "Go"], 8)
    junior_dev = JuniorDeveloper("신입김", 35000000, ["Python"], 0)
    
    # 보고 관계 설정
    cto.add_subordinate(dev_manager)
    dev_manager.add_subordinate(senior_dev)
    dev_manager.add_subordinate(junior_dev)
    senior_dev.add_mentee(junior_dev)
    
    # 계층 관계 검증
    assert junior_dev.get_direct_manager() == dev_manager
    assert senior_dev.get_department_head() == cto
    assert len(dev_manager.get_all_subordinates()) == 2

def test_payroll_calculation():
    """급여 계산 시스템 테스트"""
    employees = [
        CEO("김대표", 120000000),
        SeniorDeveloper("최시니어", 50000000, ["Python", "Go"], 8),
        JuniorDeveloper("신입김", 35000000, ["Python"], 0),
    ]
    payroll = PayrollProcessor()
    
    for employee in employees:
        salary_info = payroll.calculate_monthly_salary(employee)
        assert salary_info.base_salary > 0
        assert salary_info.total_before_tax >= salary_info.base_salary
        assert salary_info.total_deductions > 0  # 세금과 4대 보험 공제
        assert salary_info.net_salary < salary_info.total_before_tax

def test_performance_evaluation():
    """성과 평가 시스템 테스트"""
    employee = SeniorDeveloper("테스트", 50000000, ["Python"], 5)
    evaluator = PerformanceEvaluator()
    
    # 평가 항목 추가
    evaluator.add_evaluation_criteria("기술 역량", 0.4)
    evaluator.add_evaluation_criteria("협업 능력", 0.3) 
    evaluator.add_evaluation_criteria("리더십", 0.3)
    
    # 평가 진행
    evaluation = evaluator.evaluate(employee, {
        "기술 역량": 4.5,
        "협업 능력": 4.0,
        "리더십": 3.8
    })
    
    assert evaluation.overall_score > 0
    assert evaluation.grade in ['S', 'A', 'B', 'C', 'D']
    assert len(evaluation.feedback) > 0
```

### GREEN Phase: 최소 HR 시스템 구현

코드가 길지만 클래스의 족보를 먼저 그려 두면 길을 잃지 않습니다.

```
BaseEmployee (추상)
├── Developer
│   ├── JuniorDeveloper
│   └── SeniorDeveloper
├── Manager (추상)
│   ├── DevelopmentManager
│   └── CTO ─────────── + ExecutiveRole (추상)
└── CEO ─────────────── + ExecutiveRole (추상)
```

`BaseEmployee`는 모든 직원의 공통 속성(사번, 연봉, 부서, 직급, 상사와 부하 목록)과 공통 기능(월 기본급, 근속 연수)을 갖고, 직책 이름(`get_job_title`)과 성과급 계산(`calculate_performance_bonus`)은 추상 메서드로 남겨 둡니다. 직급마다 성과급 규칙이 다르니까요. 임원만 하는 일(전략 결정, 예산 승인)은 `ExecutiveRole`이라는 별도의 추상 클래스로 떼어 내서, `CTO`와 `CEO`만 다중 상속으로 이 역할을 더했습니다. 13.2절의 믹스인처럼 "직원이라는 뼈대 + 임원이라는 역할"을 조합한 모양이에요.

그 뒤의 `PayrollProcessor`와 `PerformanceEvaluator`는 직원을 상속하지 않는 별개의 클래스입니다. `calculate_monthly_salary(employee)`는 `employee.get_monthly_base_salary()`와 `employee.calculate_performance_bonus()`를 부를 뿐이라, 새 직급 클래스가 생겨도 급여 처리기는 고칠 필요가 없어요.

```python
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
```

실행하면 조직도가 들여쓰기로 그려지고, 직원마다 기본급·성과급·직급수당과 세전·세후 금액이 계산됩니다. 같은 `calculate_monthly_salary()` 호출인데 CEO의 성과급은 연봉의 1/6, 개발자는 프로젝트 수에 따라 달라지는 식으로 각자의 규칙이 적용돼요. 조직도를 그리는 쪽도 상대가 누구든 `get_job_title()`만 부르면 "최고경영자 (CEO)", "Backend 개발팀 매니저"처럼 알맞은 직책이 나옵니다.

### REFACTOR Phase: 시스템 확장 및 최적화

마지막 리팩터링은 이 시스템을 실무 규모로 키울 때 쓰는 도구들을 보여 줍니다. 모두 이 장의 범위를 넘어서는 주제라 자세한 설명은 해당 장으로 미루고, 여기서는 무엇을 하려는 코드인지만 짚어 볼게요.

- **Pydantic `BaseModel`** (`EmployeeData`): 필드에 길이·범위·형식 조건을 적어 두면 객체를 만들 때 자동으로 검증해 주는 외부 라이브러리입니다. 19장 FastAPI에서 본격적으로 씁니다.
- **`async`/`await`** (`add_employee_async`): 데이터베이스 저장처럼 기다리는 시간이 긴 작업을 동시에 처리하기 위한 비동기 문법이에요. 15장에서 다룹니다.
- **커맨드 패턴** (`Command`, `HireEmployeeCommand`, `PromoteEmployeeCommand`): "채용한다", "승진시킨다" 같은 동작을 `execute()`와 `undo()`를 가진 객체로 만듭니다. 실행한 커맨드를 목록에 쌓아 두면 마지막 작업을 되돌리기(`undo_last_command`)가 쉬워져요. `Command`가 추상 클래스이고 각 커맨드가 그것을 구현하니, 처리기 입장에서는 어떤 커맨드든 똑같이 `execute()`만 부르면 됩니다. 여기서도 다형성이 일하고 있죠.

```python
# hr_system_advanced.py
from abc import ABC, abstractmethod
from typing import Dict, List, TypeAlias, NewType, Literal
from pydantic import BaseModel, field_validator, Field
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

# 앞의 GREEN 단계에서 만든 클래스를 그대로 가져와 확장합니다 (같은 폴더의 hr_management_system.py)
from hr_management_system import (
    BaseEmployee, CEO, CTO, Department, EmployeeLevel, JuniorDeveloper, SeniorDeveloper,
)

# 타입 별칭과 NewType
EmployeeID: TypeAlias = str
Salary: TypeAlias = int
Score = NewType('Score', float)

class EmployeeData(BaseModel):
    """Pydantic를 활용한 데이터 검증"""
    name: str = Field(..., min_length=2, max_length=30)
    annual_salary: int = Field(..., gt=0, le=500000000)
    department: str
    hire_date: datetime = Field(default_factory=datetime.now)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    
    @field_validator('name')
    @classmethod
    def validate_korean_name(cls, v):
        if not any('가' <= c <= '힣' for c in v):
            raise ValueError('한국어 이름을 입력해주세요')
        return v

class HRSystemOptimized:
    """최적화된 HR 시스템"""
    
    def __init__(self):
        self._employees: Dict[EmployeeID, BaseEmployee] = {}
        self._department_index: Dict[Department, List[EmployeeID]] = {}
        self._level_index: Dict[EmployeeLevel, List[EmployeeID]] = {}
    
    async def add_employee_async(self, employee: BaseEmployee) -> None:
        """비동기 직원 추가"""
        await asyncio.sleep(0.1)  # DB 저장 시뮬레이션
        self._employees[employee.employee_id] = employee
        self._update_indices(employee)
        print(f"[O] {employee.name} 등록 완료 (비동기)")
    
    def _update_indices(self, employee: BaseEmployee) -> None:
        """인덱스 업데이트"""
        # 부서별 인덱스
        if employee.department not in self._department_index:
            self._department_index[employee.department] = []
        self._department_index[employee.department].append(employee.employee_id)
        
        # 직급별 인덱스
        if employee.level not in self._level_index:
            self._level_index[employee.level] = []
        self._level_index[employee.level].append(employee.employee_id)
    
    def get_employees_by_department(self, department: Department) -> List[BaseEmployee]:
        """부서별 직원 조회 (O(1) 인덱스 활용)"""
        employee_ids = self._department_index.get(department, [])
        return [self._employees[eid] for eid in employee_ids]
    
    def get_employees_by_level(self, level: EmployeeLevel) -> List[BaseEmployee]:
        """직급별 직원 조회"""
        employee_ids = self._level_index.get(level, [])
        return [self._employees[eid] for eid in employee_ids]
    
    @asynccontextmanager
    async def bulk_operation(self):
        """대량 작업용 컨텍스트 매니저"""
        print("대량 작업 시작...")
        start_time = datetime.now()
        try:
            yield self
        finally:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            print(f"[O] 대량 작업 완료 (소요 시간: {duration:.2f}초)")

# 고급 디자인 패턴 적용
class Command(ABC):
    """커맨드 패턴"""
    
    @abstractmethod
    async def execute(self) -> None:
        pass
    
    @abstractmethod
    async def undo(self) -> None:
        pass

class HireEmployeeCommand(Command):
    """직원 채용 커맨드"""
    
    def __init__(self, hr_system: HRSystemOptimized, employee: BaseEmployee):
        self.hr_system = hr_system
        self.employee = employee
        self.executed = False
    
    async def execute(self) -> None:
        await self.hr_system.add_employee_async(self.employee)
        self.executed = True
        print(f"[O] 채용 완료: {self.employee.name}")
    
    async def undo(self) -> None:
        if self.executed:
            # 실제로는 직원 제거 로직
            print(f"[!] 채용 취소: {self.employee.name}")
            self.executed = False

class PromoteEmployeeCommand(Command):
    """직원 승진 커맨드"""
    
    def __init__(self, employee: BaseEmployee, new_level: EmployeeLevel, 
                 new_salary: int):
        self.employee = employee
        self.new_level = new_level
        self.new_salary = new_salary
        self.old_level = employee.level
        self.old_salary = employee.annual_salary
        self.executed = False
    
    async def execute(self) -> None:
        self.employee.level = self.new_level
        self.employee.annual_salary = self.new_salary
        self.executed = True
        print(f"승진 완료: {self.employee.name} → {self.new_level.korean_name}")
    
    async def undo(self) -> None:
        if self.executed:
            self.employee.level = self.old_level
            self.employee.annual_salary = self.old_salary
            self.executed = False
            print(f"[!] 승진 취소: {self.employee.name}")

class HRCommandProcessor:
    """커맨드 프로세서"""
    
    def __init__(self):
        self._history: List[Command] = []
    
    async def execute_command(self, command: Command) -> None:
        """커맨드 실행"""
        await command.execute()
        self._history.append(command)
    
    async def undo_last_command(self) -> None:
        """마지막 커맨드 취소"""
        if self._history:
            last_command = self._history.pop()
            await last_command.undo()
        else:
            print("취소할 커맨드가 없습니다.")

# 종합 테스트 및 시연
async def main():
    """메인 실행 함수"""
    print("=== 고급 HR 시스템 시연 ===")
    
    hr_system = HRSystemOptimized()
    command_processor = HRCommandProcessor()
    
    # 직원들 생성
    employees = [
        CEO("김대표", 150000000),
        CTO("박기술", 100000000, "AI 혁신"),
        SeniorDeveloper("최개발", 60000000, ["Python", "Go"], 7),
        JuniorDeveloper("신입김", 40000000, ["Python"], 0.5)
    ]
    
    # 비동기 대량 채용
    async with hr_system.bulk_operation():
        for employee in employees:
            hire_command = HireEmployeeCommand(hr_system, employee)
            await command_processor.execute_command(hire_command)
    
    # 부서별 조회
    dev_employees = hr_system.get_employees_by_department(Department.ENGINEERING)
    print(f"\n개발팀 직원 수: {len(dev_employees)}명")
    
    # 승진 처리
    junior = next(emp for emp in employees if isinstance(emp, JuniorDeveloper))
    promote_command = PromoteEmployeeCommand(junior, EmployeeLevel.SENIOR, 50000000)
    await command_processor.execute_command(promote_command)
    
    # 승진 취소 시연
    print("\n승진 취소 시연:")
    await command_processor.undo_last_command()
    
    print("\n=== 시연 완료 ===")

if __name__ == "__main__":
    asyncio.run(main())
```

> **Q. 네 기둥은 알겠는데, 실제로 클래스를 설계할 때는 뭘 기준으로 삼아야 하나요?**
> 사실 캡슐화·상속·추상화·다형성만 가지고 좋은 클래스를 설계하기는 꽤 어렵습니다. 그래서 많은 개발자가 다섯 가지 원칙의 앞 글자를 딴 **SOLID**를 점검표로 씁니다. 이 장의 코드에서 각 원칙이 어디에 있었는지 함께 보세요.
>
> - **S, 단일 책임 원칙**: 클래스는 한 가지 이유로만 바뀌어야 한다. 직원 클래스와 급여 처리기(`PayrollProcessor`)를 나눈 것.
> - **O, 개방·폐쇄 원칙**: 확장에는 열려 있고 수정에는 닫혀 있어야 한다. 새 결제 수단은 클래스를 추가하면 되고 오케스트레이터는 고치지 않는 것.
> - **L, 리스코프 치환 원칙**: 부모 자리에 자식을 넣어도 프로그램이 올바르게 동작해야 한다. 어떤 직원 객체를 넣어도 급여 계산이 되는 것.
> - **I, 인터페이스 분리 원칙**: 쓰지 않는 메서드까지 억지로 갖추게 하지 말고 인터페이스를 작게 나눈다. `Drawable`, `Movable`, `Interactive`를 따로 둔 것.
> - **D, 의존성 역전 원칙**: 구체적인 클래스가 아니라 추상(인터페이스)에 기대어 코드를 짠다. 오케스트레이터가 `PaymentProcessor`라는 추상만 알고 카드·카카오페이는 모르는 것.

## 13.6 실습 문제

### 기본 문제 (1-5번)

기본 문제는 이 장의 순서 그대로 상속 → 오버라이딩 → `super()` → 추상 클래스 → 다중 상속과 MRO를 하나씩 연습합니다. 각 문제의 `# 답안:` 아래 코드를 보기 전에 직접 채워 보세요. 5번에서는 `Duck.__mro__`를 출력하기 전에 순서를 먼저 예상해 보면 13.2절의 세 원칙을 확인할 수 있습니다.

```python
# 1번: 기본 상속 구현
class Vehicle:
    def __init__(self, brand: str, model: str):
        self.brand = brand
        self.model = model
        self.speed = 0
    
    def accelerate(self, increment: int) -> None:
        # 문제: 속도 증가 메서드 구현
        pass
    
    def brake(self, decrement: int) -> None:
        # 문제: 속도 감소 메서드 구현 (0 이하로 내려가지 않게)
        pass

class Car(Vehicle):
    def __init__(self, brand: str, model: str, doors: int):
        # 문제: 부모 클래스 초기화 호출
        pass
        self.doors = doors
    
    def honk(self) -> str:
        # 문제: 클랙션 메서드 구현
        pass

# 답안:
class Vehicle:
    def __init__(self, brand: str, model: str):
        self.brand = brand
        self.model = model
        self.speed = 0
    
    def accelerate(self, increment: int) -> None:
        self.speed += increment
        print(f"속도 증가: {self.speed}km/h")
    
    def brake(self, decrement: int) -> None:
        self.speed = max(0, self.speed - decrement)
        print(f"속도 감소: {self.speed}km/h")

class Car(Vehicle):
    def __init__(self, brand: str, model: str, doors: int):
        super().__init__(brand, model)
        self.doors = doors
    
    def honk(self) -> str:
        return f"{self.brand} {self.model}: 빵빵!"

# 테스트
car = Car("현대", "소나타", 4)
car.accelerate(60)
car.brake(20)
print(car.honk())

# 2번: 메서드 오버라이딩
class Animal:
    def __init__(self, name: str):
        self.name = name
    
    def make_sound(self) -> str:
        return "동물이 소리를 냅니다"
    
    def move(self) -> str:
        return f"{self.name}: 이동합니다"

class Dog(Animal):
    # 문제: make_sound 메서드를 오버라이드하여 "멍멍!"을 반환
    pass

class Fish(Animal):
    # 문제: move 메서드를 오버라이드하여 "수영"을 포함한 문자열 반환
    pass

# 답안:
class Dog(Animal):
    def make_sound(self) -> str:
        return f"{self.name}: 멍멍!"

class Fish(Animal):
    def move(self) -> str:
        return f"{self.name}: 물속에서 수영합니다"

# 테스트
dog = Dog("바둑이")
fish = Fish("금붕어")
print(dog.make_sound())
print(dog.move())
print(fish.move())

# 3번: super() 활용
class Employee:
    def __init__(self, name: str, salary: int):
        self.name = name
        self.salary = salary
    
    def get_annual_bonus(self) -> int:
        return self.salary // 12  # 월급의 1개월분

class Manager(Employee):
    def __init__(self, name: str, salary: int, team_size: int):
        # 문제: super()를 사용하여 부모 클래스 초기화
        pass
        self.team_size = team_size
    
    def get_annual_bonus(self) -> int:
        # 문제: 부모의 보너스 + 팀원 수 * 50000 추가
        pass

# 답안:
class Manager(Employee):
    def __init__(self, name: str, salary: int, team_size: int):
        super().__init__(name, salary)
        self.team_size = team_size
    
    def get_annual_bonus(self) -> int:
        base_bonus = super().get_annual_bonus()
        return base_bonus + (self.team_size * 50000)

# 테스트
manager = Manager("김팀장", 5000000, 5)
print(f"연간 보너스: {manager.get_annual_bonus():,}원")

# 4번: 추상 클래스 구현
from abc import ABC, abstractmethod

class Shape(ABC):
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def calculate_area(self) -> float:
        pass
    
    @abstractmethod
    def calculate_perimeter(self) -> float:
        pass
    
    def describe(self) -> str:
        return f"{self.name}: 넓이 {self.calculate_area():.2f}, 둘레 {self.calculate_perimeter():.2f}"

# 문제: Rectangle 클래스 구현
class Rectangle(Shape):
    pass

# 문제: Circle 클래스 구현
class Circle(Shape):
    pass

# 답안:
import math

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        super().__init__("직사각형")
        self.width = width
        self.height = height
    
    def calculate_area(self) -> float:
        return self.width * self.height
    
    def calculate_perimeter(self) -> float:
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius: float):
        super().__init__("원")
        self.radius = radius
    
    def calculate_area(self) -> float:
        return math.pi * self.radius ** 2
    
    def calculate_perimeter(self) -> float:
        return 2 * math.pi * self.radius

# 테스트
shapes = [
    Rectangle(5, 3),
    Circle(4)
]

for shape in shapes:
    print(shape.describe())

# 5번: 다중 상속과 MRO
class Flyable:
    def fly(self) -> str:
        return "날고 있습니다"

class Swimmable:
    def swim(self) -> str:
        return "수영하고 있습니다"

class Bird:
    def __init__(self, name: str):
        self.name = name
    
    def chirp(self) -> str:
        return f"{self.name}: 짹짹!"

# 문제: Duck 클래스가 Bird, Flyable, Swimmable을 모두 상속받도록 구현
class Duck(Bird, Flyable, Swimmable):
    def __init__(self, name: str):
        # 문제: super()를 올바르게 사용
        pass
    
    def quack(self) -> str:
        # 문제: 오리 특유의 소리 구현
        pass

# 답안:
class Duck(Bird, Flyable, Swimmable):
    def __init__(self, name: str):
        super().__init__(name)
    
    def quack(self) -> str:
        return f"{self.name}: 꽥꽥!"
    
    def show_abilities(self) -> None:
        print(self.chirp())
        print(self.quack()) 
        print(self.fly())
        print(self.swim())

# MRO 확인
print("Duck MRO:", [cls.__name__ for cls in Duck.__mro__])

# 테스트
duck = Duck("도널드")
duck.show_abilities()
```

### 중급 문제 (6-10번)

중급 문제는 상속을 프로퍼티, 팩토리, 믹스인, 덕 타이핑, 컨텍스트 매니저와 엮습니다. 6번처럼 부모의 메서드를 오버라이딩할 때는 부모가 하던 일을 통째로 다시 쓸지, `super()`로 부르고 조건만 더할지부터 정해 보세요.

```python
# 6번: 프로퍼티와 상속
class BankAccount:
    def __init__(self, owner: str, balance: int = 0):
        self.owner = owner
        self._balance = balance
        self._transaction_fee = 1000
    
    @property
    def balance(self) -> int:
        return self._balance
    
    def withdraw(self, amount: int) -> bool:
        if amount + self._transaction_fee <= self._balance:
            self._balance -= (amount + self._transaction_fee)
            return True
        return False

class PremiumAccount(BankAccount):
    def __init__(self, owner: str, balance: int = 0):
        super().__init__(owner, balance)
        self._transaction_fee = 0  # 프리미엄은 수수료 무료
        self._monthly_limit = 10000000
    
    # 문제: withdraw 메서드를 오버라이드하여 월 한도 체크 추가
    def withdraw(self, amount: int) -> bool:
        # 월 한도 체크 로직 추가 필요
        pass

# 답안:
class PremiumAccount(BankAccount):
    def __init__(self, owner: str, balance: int = 0):
        super().__init__(owner, balance)
        self._transaction_fee = 0
        self._monthly_limit = 10000000
        self._monthly_withdrawn = 0
    
    def withdraw(self, amount: int) -> bool:
        if self._monthly_withdrawn + amount > self._monthly_limit:
            print(f"월 한도 초과: {self._monthly_limit:,}원")
            return False
        
        success = super().withdraw(amount)
        if success:
            self._monthly_withdrawn += amount
        return success
    
    def reset_monthly_limit(self):
        """월 한도 리셋"""
        self._monthly_withdrawn = 0

# 7번: 팩토리 패턴과 상속
from abc import ABC, abstractmethod

class Vehicle(ABC):
    @abstractmethod
    def start(self) -> str:
        pass
    
    @abstractmethod
    def stop(self) -> str:
        pass

class Car(Vehicle):
    def start(self) -> str:
        return "자동차 시동 켜짐"
    
    def stop(self) -> str:
        return "자동차 시동 꺼짐"

class Motorcycle(Vehicle):
    def start(self) -> str:
        return "오토바이 시동 켜짐"
    
    def stop(self) -> str:
        return "오토바이 시동 꺼짐"

# 문제: VehicleFactory 클래스 구현
class VehicleFactory:
    @staticmethod
    def create_vehicle(vehicle_type: str) -> Vehicle:
        # 문제: 타입에 따라 적절한 Vehicle 반환
        pass

# 답안:
class VehicleFactory:
    @staticmethod
    def create_vehicle(vehicle_type: str) -> Vehicle:
        if vehicle_type.lower() == "car":
            return Car()
        elif vehicle_type.lower() == "motorcycle":
            return Motorcycle()
        else:
            raise ValueError(f"알 수 없는 차량 타입: {vehicle_type}")

# 테스트
vehicles = [
    VehicleFactory.create_vehicle("car"),
    VehicleFactory.create_vehicle("motorcycle")
]

for vehicle in vehicles:
    print(vehicle.start())
    print(vehicle.stop())

# 8번: 믹스인 패턴
from datetime import datetime

class TimestampMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def touch(self):
        """수정 시간 업데이트"""
        self.updated_at = datetime.now()

class ValidationMixin:
    def validate(self) -> bool:
        """기본 검증"""
        return True

# 문제: User 클래스가 두 믹스인을 사용하도록 구현
class User:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

# 답안:
class User(TimestampMixin, ValidationMixin):
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
        super().__init__()  # 믹스인 초기화
    
    def validate(self) -> bool:
        """사용자 정보 검증"""
        if len(self.username) < 3:
            return False
        if "@" not in self.email:
            return False
        return super().validate()
    
    def update_profile(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.touch()  # 수정 시간 업데이트

# 테스트
user = User("김사용자", "user@example.com")
print(f"유효성 검사: {user.validate()}")
print(f"생성 시간: {user.created_at}")

user.update_profile(email="new@example.com")
print(f"수정 시간: {user.updated_at}")

# 9번: 다형성과 덕 타이핑
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str: ...

class Button:
    def __init__(self, text: str):
        self.text = text
    
    def draw(self) -> str:
        return f"[{self.text}] 버튼"

class Icon:
    def __init__(self, name: str):
        self.name = name
    
    def draw(self) -> str:
        return f"{self.name} 아이콘"

# 문제: render_ui 함수가 Drawable 프로토콜을 활용하도록 구현
def render_ui(components: list[Drawable]) -> None:
    # 문제: 모든 컴포넌트의 draw 메서드 호출
    pass

# 답안:
def render_ui(components: list[Drawable]) -> None:
    print("UI 렌더링 시작:")
    for component in components:
        print(f"  {component.draw()}")
    print("UI 렌더링 완료")

# 테스트
ui_components = [
    Button("확인"),
    Button("취소"),
    Icon("홈"),
    Icon("설정")
]

render_ui(ui_components)

# 10번: 컨텍스트 매니저와 상속
from contextlib import contextmanager

class DatabaseConnection:
    def __init__(self, host: str, db_name: str):
        self.host = host
        self.db_name = db_name
        self.connected = False
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
    
    def connect(self):
        self.connected = True
        print(f"{self.host}의 {self.db_name}에 연결")
    
    def disconnect(self):
        self.connected = False
        print(f"{self.db_name} 연결 해제")

class PostgreSQLConnection(DatabaseConnection):
    def __init__(self, host: str, db_name: str, port: int = 5432):
        super().__init__(host, db_name)
        self.port = port
    
    # 문제: PostgreSQL 전용 기능 추가
    def execute_query(self, query: str) -> str:
        if not self.connected:
            return "연결되지 않음"
        return f"PostgreSQL에서 쿼리 실행: {query}"

# 답안은 이미 구현됨

# 테스트
with PostgreSQLConnection("localhost", "myapp", 5432) as db:
    result = db.execute_query("SELECT * FROM users")
    print(result)
```

### 고급 문제 (11-15번)

고급 문제에는 아직 배우지 않은 도구가 섞여 있습니다. 11번의 메타클래스는 16장, 13번의 `async`/`await`는 15장에서 자세히 다루니, 지금은 상속과 어떻게 맞물리는지만 보고 넘어가도 괜찮아요. 15번 게임 캐릭터 시스템은 이 장의 모든 내용을 한데 모은 종합 문제입니다. 공격 결과에 무작위 값이 섞여 있어서 실행할 때마다 전투 결과가 달라집니다.

```python
# 11번: 메타클래스와 상속
class SingletonMeta(type):
    """싱글톤 메타클래스"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DatabaseManager(metaclass=SingletonMeta):
    def __init__(self):
        self.connections = []
    
    def add_connection(self, conn_string: str):
        self.connections.append(conn_string)

# 테스트
db1 = DatabaseManager()
db2 = DatabaseManager()
print(f"동일한 객체인가? {db1 is db2}")

# 12번: 제네릭과 상속
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Repository(Generic[T]):
    """제네릭 저장소"""
    def __init__(self):
        self._items: List[T] = []
    
    def add(self, item: T) -> None:
        self._items.append(item)
    
    def get_all(self) -> List[T]:
        return self._items.copy()
    
    def find_by_id(self, item_id: str) -> T | None:
        # 문제: ID로 항목 찾기 구현 (hasattr 활용)
        pass

# 답안:
class Repository(Generic[T]):
    def __init__(self):
        self._items: List[T] = []
    
    def add(self, item: T) -> None:
        self._items.append(item)
    
    def get_all(self) -> List[T]:
        return self._items.copy()
    
    def find_by_id(self, item_id: str) -> T | None:
        for item in self._items:
            if hasattr(item, 'id') and item.id == item_id:
                return item
        return None

class User:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

# 테스트
user_repo = Repository[User]()
user_repo.add(User("1", "김사용자"))
user_repo.add(User("2", "이사용자"))

found_user = user_repo.find_by_id("1")
print(f"찾은 사용자: {found_user.name if found_user else 'None'}")

# 13번: 비동기와 상속
import asyncio
from abc import ABC, abstractmethod

class AsyncProcessor(ABC):
    @abstractmethod
    async def process(self, data: str) -> str:
        pass

class FileProcessor(AsyncProcessor):
    async def process(self, data: str) -> str:
        # 파일 처리 시뮬레이션
        await asyncio.sleep(0.1)
        return f"파일 처리 완료: {data}"

class NetworkProcessor(AsyncProcessor):
    async def process(self, data: str) -> str:
        # 네트워크 처리 시뮬레이션
        await asyncio.sleep(0.2)
        return f"네트워크 전송 완료: {data}"

# 문제: 다양한 프로세서를 비동기로 실행하는 함수 구현
async def process_all(processors: List[AsyncProcessor], data: str) -> List[str]:
    # 문제: 모든 프로세서를 동시에 실행
    pass

# 답안:
async def process_all(processors: List[AsyncProcessor], data: str) -> List[str]:
    tasks = [processor.process(data) for processor in processors]
    results = await asyncio.gather(*tasks)
    return results

# 테스트
async def main():
    processors = [
        FileProcessor(),
        NetworkProcessor()
    ]
    
    results = await process_all(processors, "테스트 데이터")
    for result in results:
        print(result)

# asyncio.run(main())

# 14번: 데코레이터와 상속
from functools import wraps

def log_method_calls(cls):
    """클래스의 모든 메서드 호출을 로깅하는 데코레이터"""
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            setattr(cls, attr_name, _log_wrapper(attr, attr_name))
    return cls

def _log_wrapper(method, method_name):
    @wraps(method)
    def wrapper(*args, **kwargs):
        print(f"{method_name} 메서드 호출")
        result = method(*args, **kwargs)
        print(f"[O] {method_name} 메서드 완료")
        return result
    return wrapper

@log_method_calls
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b
    
    def multiply(self, a: int, b: int) -> int:
        return a * b

# 테스트
calc = Calculator()
print(calc.add(5, 3))
print(calc.multiply(4, 7))

# 15번: 종합 프로젝트 - 게임 캐릭터 시스템
from typing import Dict, List
from enum import Enum
import random

class CharacterClass(Enum):
    WARRIOR = "전사"
    MAGE = "마법사" 
    ARCHER = "궁수"
    HEALER = "힐러"

class Skill(ABC):
    def __init__(self, name: str, damage: int, mana_cost: int):
        self.name = name
        self.damage = damage
        self.mana_cost = mana_cost
    
    @abstractmethod
    def use(self, caster: 'Character', target: 'Character') -> str:
        pass

class AttackSkill(Skill):
    def use(self, caster: 'Character', target: 'Character') -> str:
        if caster.mana < self.mana_cost:
            return f"{caster.name}의 마나가 부족합니다!"
        
        caster.mana -= self.mana_cost
        damage = self.damage + random.randint(-5, 5)
        target.take_damage(damage)
        return f"{caster.name}의 {self.name}! {target.name}에게 {damage} 피해!"

class HealSkill(Skill):
    def use(self, caster: 'Character', target: 'Character') -> str:
        if caster.mana < self.mana_cost:
            return f"{caster.name}의 마나가 부족합니다!"
        
        caster.mana -= self.mana_cost
        heal_amount = self.damage  # damage 대신 힐량으로 사용
        target.heal(heal_amount)
        return f"{caster.name}의 {self.name}! {target.name}의 체력 {heal_amount} 회복!"

class Character(ABC):
    def __init__(self, name: str, character_class: CharacterClass):
        self.name = name
        self.character_class = character_class
        self.max_hp = 100
        self.hp = 100
        self.max_mana = 50
        self.mana = 50
        self.skills: List[Skill] = []
        self.level = 1
        self.exp = 0
    
    def add_skill(self, skill: Skill):
        self.skills.append(skill)
    
    def take_damage(self, damage: int):
        self.hp = max(0, self.hp - damage)
        if self.hp == 0:
            print(f"[X] {self.name} 쓰러짐!")
    
    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)
    
    def is_alive(self) -> bool:
        return self.hp > 0
    
    @abstractmethod
    def get_base_stats(self) -> Dict[str, int]:
        pass
    
    def get_status(self) -> str:
        return f"{self.name} ({self.character_class.value}) Lv.{self.level} - HP: {self.hp}/{self.max_hp}, MP: {self.mana}/{self.max_mana}"

class Warrior(Character):
    def __init__(self, name: str):
        super().__init__(name, CharacterClass.WARRIOR)
        self.max_hp = 150  # 전사는 체력이 높음
        self.hp = 150
        self.max_mana = 30  # 마나는 낮음
        self.mana = 30
        
        # 전사 스킬
        self.add_skill(AttackSkill("검 베기", 25, 5))
        self.add_skill(AttackSkill("파워 어택", 40, 15))
    
    def get_base_stats(self) -> Dict[str, int]:
        return {"attack": 20, "defense": 15, "magic": 5}

class Mage(Character):
    def __init__(self, name: str):
        super().__init__(name, CharacterClass.MAGE)
        self.max_hp = 80  # 마법사는 체력이 낮음
        self.hp = 80
        self.max_mana = 100  # 마나는 높음
        self.mana = 100
        
        # 마법사 스킬
        self.add_skill(AttackSkill("파이어볼", 35, 20))
        self.add_skill(AttackSkill("라이트닝", 45, 30))
    
    def get_base_stats(self) -> Dict[str, int]:
        return {"attack": 10, "defense": 5, "magic": 25}

class Healer(Character):
    def __init__(self, name: str):
        super().__init__(name, CharacterClass.HEALER)
        self.max_mana = 80
        self.mana = 80
        
        # 힐러 스킬
        self.add_skill(HealSkill("힐", 30, 15))
        self.add_skill(AttackSkill("홀리 라이트", 20, 10))
    
    def get_base_stats(self) -> Dict[str, int]:
        return {"attack": 12, "defense": 10, "magic": 18}

# 게임 시스템
class BattleSystem:
    MAX_TURNS = 30   # 서로 회복만 하며 끝나지 않는 전투를 막기 위한 턴 제한
    MANA_REGEN = 10  # 턴마다 회복하는 마나

    def __init__(self):
        self.turn_count = 0
    
    def start_battle(self, team1: List[Character], team2: List[Character]):
        print("전투 시작!")
        self.turn_count = 0
        
        while self._has_alive_members(team1) and self._has_alive_members(team2):
            if self.turn_count >= self.MAX_TURNS:
                print(f"\n{self.MAX_TURNS}턴이 지나 무승부!")
                return
            self.turn_count += 1
            print(f"\n--- 턴 {self.turn_count} ---")
            
            # 팀1 턴
            self._execute_team_turn(team1, team2, "팀1")
            if not self._has_alive_members(team2):
                break
            
            # 팀2 턴
            self._execute_team_turn(team2, team1, "팀2")
        
        # 승부 결과
        if self._has_alive_members(team1):
            print("팀1 승리!")
        else:
            print("팀2 승리!")
    
    def _has_alive_members(self, team: List[Character]) -> bool:
        return any(char.is_alive() for char in team)
    
    def _execute_team_turn(self, attacking_team: List[Character], 
                          defending_team: List[Character], team_name: str):
        print(f"\n{team_name}의 턴:")
        
        for attacker in attacking_team:
            if not attacker.is_alive():
                continue
            
            # 매 턴 마나를 조금씩 회복 (회복이 없으면 마나가 바닥난 뒤 아무도 공격하지 못한다)
            attacker.mana = min(attacker.max_mana, attacker.mana + self.MANA_REGEN)
            
            # 살아있는 적 중 랜덤 선택
            alive_enemies = [char for char in defending_team if char.is_alive()]
            if not alive_enemies:
                break
            
            target = random.choice(alive_enemies)
            
            # 스킬 중 랜덤 선택
            if attacker.skills:
                skill = random.choice(attacker.skills)
                if isinstance(skill, HealSkill):
                    # 회복 스킬은 적이 아니라 체력이 가장 낮은 아군에게 쓴다
                    alive_allies = [char for char in attacking_team if char.is_alive()]
                    target = min(alive_allies, key=lambda char: char.hp)
                result = skill.use(attacker, target)
                print(f"  {result}")
            
            # 상태 출력
            print(f"  → {target.get_status()}")

# 테스트 실행
if __name__ == "__main__":
    # 팀 구성
    team1 = [
        Warrior("아서"),
        Mage("멀린")
    ]
    
    team2 = [
        Warrior("골리앗"),
        Healer("엘리사")
    ]
    
    # 전투 시작
    battle = BattleSystem()
    battle.start_battle(team1, team2)
```

## 13.7 다음 장 미리보기

다음 Chapter 14에서는 **모듈과 패키지**를 학습합니다:

### 주요 내용 미리보기
- **모듈 시스템**: import 구문과 모듈 검색 경로
- **패키지 구조**: `__init__.py`와 네임스페이스
- **uv 패키지 매니저**: 현대적 의존성 관리
- **pyproject.toml**: 프로젝트 설정과 메타데이터
- **표준 라이브러리**: 주요 내장 모듈 활용
- **실무 프로젝트**: 한국어 처리 라이브러리 개발

### 연결 포인트
- 클래스 계층 → 모듈 단위로 분리한 패키지 구조
- 추상 클래스와 인터페이스 → 패키지 공개 API 설계
- 다형성 → 플러그인 방식의 모듈 확장

상속과 다형성의 강력함을 완전히 익혔다면, 이제 코드를 모듈과 패키지로 구조화하여 재사용 가능하고 유지보수가 쉬운 프로그램을 만들 준비가 되었습니다!

---

> **학습 팁**: 상속은 "is-a" 관계일 때만 사용하고, 코드 재사용이 목적이라면 컴포지션을 고려하세요. 다형성은 인터페이스(프로토콜)를 통해 구현하는 것이 더 유연합니다.

**다음 장에서 만나요!** 
